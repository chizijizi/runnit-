from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import UserRegister, UserLogin, UserOut, TokenOut, UserLocationUpdate
from app.core.security import hash_password, verify_password, create_access_token, get_current_user_id

router = APIRouter()


def get_user_or_404(user_id: str, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen")
    return user


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email već postoji")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Pogrešan email ili lozinka")

    token = create_access_token(subject=user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return get_user_or_404(user_id, db)


@router.patch("/me/location", response_model=UserOut)
def update_location(
    data: UserLocationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Ažurira GPS lokaciju korisnika (poziva se pri otvaranju aplikacije)."""
    user = get_user_or_404(user_id, db)
    user.lat = data.lat
    user.lng = data.lng
    db.commit()
    db.refresh(user)
    return user
