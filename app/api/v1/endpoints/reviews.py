from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.models import Review, Activity, Booking, BookingStatus
from app.schemas.schemas import ReviewCreate, ReviewOut
from app.core.security import get_current_user_id

router = APIRouter()


def recalculate_rating(activity: Activity, db: Session):
    """Ažurira avg_rating na aktivnosti nakon svake nove recenzije."""
    reviews = db.query(Review).filter(Review.activity_id == activity.id).all()
    if reviews:
        activity.avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 2)
    db.commit()


@router.get("/activity/{activity_id}", response_model=list[ReviewOut])
def get_reviews(activity_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.activity_id == activity_id)
        .order_by(Review.created_at.desc())
        .all()
    )


@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Korisnik može ostaviti recenziju samo za aktivnost
    koju je stvarno rezervirao i dovršio.
    """
    activity = db.query(Activity).filter(Activity.id == data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Aktivnost nije pronađena")

    # Provjeri da korisnik ima completed booking za ovu aktivnost
    has_booking = db.query(Booking).filter(
        Booking.user_id == user_id,
        Booking.activity_id == data.activity_id,
        Booking.status == BookingStatus.completed,
    ).first()
    if not has_booking:
        raise HTTPException(
            status_code=403,
            detail="Možete recenzirati samo aktivnosti koje ste dovršili"
        )

    # Provjeri duplikat recenzije
    existing = db.query(Review).filter(
        Review.user_id == user_id,
        Review.activity_id == data.activity_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Već ste ostavili recenziju za ovu aktivnost")

    review = Review(user_id=user_id, **data.model_dump())
    db.add(review)
    db.flush()

    recalculate_rating(activity, db)
    db.refresh(review)

    return db.query(Review).options(joinedload(Review.user)).filter(Review.id == review.id).first()


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review or review.user_id != user_id:
        raise HTTPException(status_code=404, detail="Recenzija nije pronađena")

    activity = db.query(Activity).filter(Activity.id == review.activity_id).first()
    db.delete(review)
    db.flush()
    if activity:
        recalculate_rating(activity, db)
