from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.db.session import get_db
from app.models.models import Activity, Category, Provider
from app.schemas.schemas import ActivityCreate, ActivityOut, CategoryOut, NearbySearch
from app.core.security import get_current_user_id
from app.services.geo import filter_by_radius

router = APIRouter()


def activity_query(db: Session):
    return db.query(Activity).options(
        joinedload(Activity.provider),
        joinedload(Activity.category),
    )


@router.get("/", response_model=list[ActivityOut])
def list_activities(
    category_id: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    """Sve aktivnosti s opcionalnim filtrima."""
    q = activity_query(db).filter(Activity.active == True)
    if category_id:
        q = q.filter(Activity.category_id == category_id)
    if max_price:
        q = q.filter(Activity.price <= max_price)
    if min_rating:
        q = q.filter(Activity.avg_rating >= min_rating)
    return q.all()


@router.post("/nearby", response_model=list[ActivityOut])
def nearby_activities(search: NearbySearch, db: Session = Depends(get_db)):
    """
    Aktivnosti u zadanom radijusu od GPS koordinata.
    Rezultati su sortirani po udaljenosti (najbliže prvo).
    """
    q = activity_query(db).filter(Activity.active == True)
    if search.category_id:
        q = q.filter(Activity.category_id == search.category_id)
    if search.max_price:
        q = q.filter(Activity.price <= search.max_price)
    if search.min_rating:
        q = q.filter(Activity.avg_rating >= search.min_rating)

    activities = q.all()
    return filter_by_radius(activities, search.lat, search.lng, search.radius_km)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: str, db: Session = Depends(get_db)):
    activity = activity_query(db).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Aktivnost nije pronađena")
    return activity


@router.post("/", response_model=ActivityOut, status_code=201)
def create_activity(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user_id),  # mora biti prijavljen
):
    """Kreiranje nove aktivnosti (provider registrira svoju ponudu)."""
    if not db.query(Provider).filter(Provider.id == data.provider_id).first():
        raise HTTPException(status_code=404, detail="Provider nije pronađen")
    if not db.query(Category).filter(Category.id == data.category_id).first():
        raise HTTPException(status_code=404, detail="Kategorija nije pronađena")

    activity = Activity(**data.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity_query(db).filter(Activity.id == activity.id).first()
