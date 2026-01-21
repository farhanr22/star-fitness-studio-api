"""API endpoints for managing class bookings."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth import get_current_user, User
from app.modules.bookings import service
from app.modules.bookings.schemas import (
    BookingCreate,
    BookingResponse,
    UserBookingResponse,
)
from app.core.exceptions import AppException


router = APIRouter()


@router.post("/book", response_model=BookingResponse, status_code=201)
def book_class(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Book a slot in a class. Requires authentication."""
    try:
        booking = service.create_booking(db, current_user, booking_in)
        return booking
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/bookings", response_model=List[UserBookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all bookings made by the authenticated user."""
    results = service.get_user_bookings(db, current_user.id)
    
    # Map the tuple fields to the response schema
    response = []
    for booking, fitness_class in results:
        response.append({
            "class_id": fitness_class.id,
            "name": fitness_class.name,
            "instructor": fitness_class.instructor,
            "date_time": fitness_class.dateTime,
            "booking_id": booking.id,
            "booked_at": booking.created_at,
            "booked_as_name": booking.client_name,
            "booked_as_email": booking.client_email,
        })
        
    return response