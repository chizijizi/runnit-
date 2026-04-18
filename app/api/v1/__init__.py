from fastapi import APIRouter
from app.api.v1.endpoints import auth, activities, slots, bookings, reviews, wishlist

router = APIRouter()

router.include_router(auth.router,       prefix="/auth",       tags=["Auth"])
router.include_router(activities.router, prefix="/activities", tags=["Aktivnosti"])
router.include_router(slots.router,      prefix="/slots",      tags=["Termini"])
router.include_router(bookings.router,   prefix="/bookings",   tags=["Rezervacije"])
router.include_router(reviews.router,    prefix="/reviews",    tags=["Recenzije"])
router.include_router(wishlist.router,   prefix="/wishlist",   tags=["Lista željenog"])
