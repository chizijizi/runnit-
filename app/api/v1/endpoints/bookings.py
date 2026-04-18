from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.models import Booking, TimeSlot, Activity, BookingStatus
from app.schemas.schemas import BookingCreate, BookingOut, BookingStatusUpdate
from app.core.security import get_current_user_id

router = APIRouter()


def booking_query(db: Session):
    return db.query(Booking).options(
        joinedload(Booking.activity).joinedload(Activity.provider),
        joinedload(Booking.activity).joinedload(Activity.category),
        joinedload(Booking.time_slot),
    )


@router.post("/", response_model=BookingOut, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Naruči termin — kao naručivanje hrane ali za avanturu! 🏔️"""
    activity = db.query(Activity).filter(Activity.id == data.activity_id).first()
    if not activity or not activity.active:
        raise HTTPException(status_code=404, detail="Aktivnost nije pronađena")

    slot = db.query(TimeSlot).filter(TimeSlot.id == data.time_slot_id).first()
    if not slot or slot.activity_id != data.activity_id:
        raise HTTPException(status_code=404, detail="Termin nije pronađen")

    if slot.available < data.participants:
        raise HTTPException(
            status_code=409,
            detail=f"Nema dovoljno mjesta. Slobodno: {slot.available}"
        )

    # Provjeri duplikat — isti korisnik, isti termin
    existing = db.query(Booking).filter(
        Booking.user_id == user_id,
        Booking.time_slot_id == slot.id,
        Booking.status != BookingStatus.cancelled,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Već imate rezervaciju za ovaj termin")

    total_price = activity.price * data.participants

    booking = Booking(
        user_id=user_id,
        activity_id=data.activity_id,
        time_slot_id=data.time_slot_id,
        participants=data.participants,
        total_price=total_price,
        status=BookingStatus.confirmed,
    )
    slot.booked += data.participants

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking_query(db).filter(Booking.id == booking.id).first()


@router.get("/my", response_model=list[BookingOut])
def my_bookings(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Sve narudžbe prijavljenog korisnika."""
    return (
        booking_query(db)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.booked_at.desc())
        .all()
    )


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    booking = booking_query(db).filter(Booking.id == booking_id).first()
    if not booking or booking.user_id != user_id:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")
    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Otkazivanje rezervacije — oslobađa mjesta u terminu."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking or booking.user_id != user_id:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Rezervacija je već otkazana")

    booking.status = BookingStatus.cancelled
    slot = db.query(TimeSlot).filter(TimeSlot.id == booking.time_slot_id).first()
    if slot:
        slot.booked = max(0, slot.booked - booking.participants)

    db.commit()
    db.refresh(booking)
    return booking_query(db).filter(Booking.id == booking.id).first()
