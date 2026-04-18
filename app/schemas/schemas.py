from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.models import BookingStatus


# ─── USER ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── PROVIDER ────────────────────────────────────────────────────────────────

class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    address: Optional[str] = None
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    contact_email: Optional[EmailStr] = None

class ProviderOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    address: Optional[str]
    lat: float
    lng: float
    contact_email: Optional[str]
    verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── CATEGORY ────────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id: str
    name: str
    icon: Optional[str]

    model_config = {"from_attributes": True}


# ─── ACTIVITY ────────────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    provider_id: str
    category_id: str
    title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    duration_min: int = Field(..., gt=0)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class ActivityOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    price: float
    duration_min: int
    lat: float
    lng: float
    avg_rating: float
    active: bool
    provider: ProviderOut
    category: CategoryOut
    distance_km: Optional[float] = None  # popunjava se pri pretraživanju

    model_config = {"from_attributes": True}


# ─── TIME SLOT ────────────────────────────────────────────────────────────────

class TimeSlotCreate(BaseModel):
    activity_id: str
    starts_at: datetime
    capacity: int = Field(..., gt=0)

class TimeSlotOut(BaseModel):
    id: str
    activity_id: str
    starts_at: datetime
    capacity: int
    booked: int
    available: int

    model_config = {"from_attributes": True}


# ─── BOOKING ─────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    activity_id: str
    time_slot_id: str
    participants: int = Field(1, ge=1, le=20)

class BookingOut(BaseModel):
    id: str
    activity_id: str
    time_slot_id: str
    participants: int
    total_price: float
    status: BookingStatus
    booked_at: datetime
    activity: ActivityOut
    time_slot: TimeSlotOut

    model_config = {"from_attributes": True}

class BookingStatusUpdate(BaseModel):
    status: BookingStatus


# ─── REVIEW ──────────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    activity_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    id: str
    activity_id: str
    rating: int
    comment: Optional[str]
    created_at: datetime
    user: UserOut

    model_config = {"from_attributes": True}


# ─── WISHLIST ─────────────────────────────────────────────────────────────────

class WishlistOut(BaseModel):
    id: str
    activity_id: str
    added_at: datetime
    activity: ActivityOut

    model_config = {"from_attributes": True}


# ─── SEARCH ──────────────────────────────────────────────────────────────────

class NearbySearch(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(25.0, gt=0, le=200)
    category_id: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
