from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.models import Wishlist, Activity
from app.schemas.schemas import WishlistOut
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/", response_model=list[WishlistOut])
def my_wishlist(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return (
        db.query(Wishlist)
        .options(
            joinedload(Wishlist.activity).joinedload(Activity.provider),
            joinedload(Wishlist.activity).joinedload(Activity.category),
        )
        .filter(Wishlist.user_id == user_id)
        .order_by(Wishlist.added_at.desc())
        .all()
    )


@router.post("/{activity_id}", response_model=WishlistOut, status_code=201)
def add_to_wishlist(
    activity_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if not db.query(Activity).filter(Activity.id == activity_id).first():
        raise HTTPException(status_code=404, detail="Aktivnost nije pronađena")

    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id, Wishlist.activity_id == activity_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Već u listi željenog")

    item = Wishlist(user_id=user_id, activity_id=activity_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return (
        db.query(Wishlist)
        .options(
            joinedload(Wishlist.activity).joinedload(Activity.provider),
            joinedload(Wishlist.activity).joinedload(Activity.category),
        )
        .filter(Wishlist.id == item.id)
        .first()
    )


@router.delete("/{activity_id}", status_code=204)
def remove_from_wishlist(
    activity_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    item = db.query(Wishlist).filter(
        Wishlist.user_id == user_id, Wishlist.activity_id == activity_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Nije u listi željenog")
    db.delete(item)
    db.commit()
