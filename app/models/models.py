import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, Text,
    ForeignKey, DateTime, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


def now_utc():
    return datetime.now(timezone.utc)


def new_uuid():
    return str(uuid.uuid4())


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(String(), primary_key=True, default=new_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(30))
    lat = Column(Float)
    lng = Column(Float)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user")


class Provider(Base):
    __tablename__ = "providers"

    id = Column(String(), primary_key=True, default=new_uuid)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    address = Column(String(255))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    contact_email = Column(String(255))
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    activities = relationship("Activity", back_populates="provider")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(), primary_key=True, default=new_uuid)
    name = Column(String(80), unique=True, nullable=False)
    icon = Column(String(50))

    activities = relationship("Activity", back_populates="category")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(), primary_key=True, default=new_uuid)
    provider_id = Column(String(), ForeignKey("providers.id"), nullable=False)
    category_id = Column(String(), ForeignKey("categories.id"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    duration_min = Column(Integer, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    avg_rating = Column(Float, default=0.0)
    active = Column(Boolean, default=True)

    provider = relationship("Provider", back_populates="activities")
    category = relationship("Category", back_populates="activities")
    time_slots = relationship("TimeSlot", back_populates="activity")
    bookings = relationship("Booking", back_populates="activity")
    reviews = relationship("Review", back_populates="activity")
    wishlist = relationship("Wishlist", back_populates="activity")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(String(), primary_key=True, default=new_uuid)
    activity_id = Column(String(), ForeignKey("activities.id"), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    capacity = Column(Integer, nullable=False)
    booked = Column(Integer, default=0)

    activity = relationship("Activity", back_populates="time_slots")
    bookings = relationship("Booking", back_populates="time_slot")

    @property
    def available(self):
        return self.capacity - self.booked


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(), primary_key=True, default=new_uuid)
    user_id = Column(String(), ForeignKey("users.id"), nullable=False)
    activity_id = Column(String(), ForeignKey("activities.id"), nullable=False)
    time_slot_id = Column(String(), ForeignKey("time_slots.id"), nullable=False)
    participants = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.pending)
    booked_at = Column(DateTime(timezone=True), default=now_utc)

    user = relationship("User", back_populates="bookings")
    activity = relationship("Activity", back_populates="bookings")
    time_slot = relationship("TimeSlot", back_populates="bookings")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(), primary_key=True, default=new_uuid)
    user_id = Column(String(), ForeignKey("users.id"), nullable=False)
    activity_id = Column(String(), ForeignKey("activities.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    user = relationship("User", back_populates="reviews")
    activity = relationship("Activity", back_populates="reviews")


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(String(), primary_key=True, default=new_uuid)
    user_id = Column(String(), ForeignKey("users.id"), nullable=False)
    activity_id = Column(String(), ForeignKey("activities.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), default=now_utc)

    user = relationship("User", back_populates="wishlist")
    activity = relationship("Activity", back_populates="wishlist")
