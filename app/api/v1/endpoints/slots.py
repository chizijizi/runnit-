from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import TimeSlot, Activity
from app.schemas.schemas import TimeSlotCreate, TimeSlotOut
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/activity/{activity_id}", response_model=list[TimeSlotOut])
def get_slots_for_activity(activity_id: str, db: Session = Depends(get_db)):
    """Slobodni termini za određenu aktivnost."""
    if not db.query(Activity).filter(Activity.id == activity_id).first():
        raise HTTPException(status_code=404, detail="Aktivnost nije pronađena")

    slots = (
        db.query(TimeSlot)
        .filter(TimeSlot.activity_id == activity_id)
        .order_by(TimeSlot.starts_at)
        .all()
    )
    return slots


@router.post("/", response_model=TimeSlotOut, status_code=201)
def create_slot(
    data: TimeSlotCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    """Dodavanje novog termina za aktivnost."""
    if not db.query(Activity).filter(Activity.id == data.activity_id).first():
        raise HTTPException(status_code=404, detail="Aktivnost nije pronađena")

    slot = TimeSlot(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/{slot_id}", status_code=204)
def delete_slot(
    slot_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Termin nije pronađen")
    db.delete(slot)
    db.commit()
