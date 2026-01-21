"""Service layer for booking-related business logic."""

from typing import List
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.utils import now_in_ist, ensure_ist_aware
from app.modules.auth.models import User
from app.modules.classes.models import FitnessClass
from app.modules.classes.service import get_class_by_id as get_class
from app.modules.bookings.models import Booking
from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.exceptions import (
    ClassNotFoundError,
    ClassIsFullError,
    AlreadyBookedError,
    ClassInPastError,
)


def create_booking(db: Session, user: User, booking_data: BookingCreate) -> Booking:
    """Creates a booking for a user for a specific class."""

    # Validate the class
    fitness_class = get_class(db, booking_data.class_id)
    if not fitness_class:
        raise ClassNotFoundError()
 
    class_time_ist = ensure_ist_aware(fitness_class.dateTime)

    if class_time_ist < now_in_ist():
        raise ClassInPastError()

    # Pre-check for duplicate booking to provide abetter error
    existing_booking = (
        db.query(Booking).filter_by(user_id=user.id, class_id=fitness_class.id).first()
    )
    if existing_booking:
        raise AlreadyBookedError()

    # Atomically update slot count and create booking
    try:
        # Nested transaction
        with db.begin_nested():
            # Lock the row and check slots
            locked_class = (
                db.query(FitnessClass)
                .filter_by(id=fitness_class.id)
                .with_for_update()
                .one()
            )

            if locked_class.available_slots <= 0:
                raise ClassIsFullError()

            locked_class.available_slots -= 1

            new_booking = Booking(
                user_id=user.id,
                class_id=fitness_class.id,
                client_name=booking_data.client_name,
                client_email=booking_data.client_email,
            )
            db.add(new_booking)
            db.flush()  # Flush to generate booking ID and check constraints
            db.refresh(new_booking) # Reload the booking object

        db.commit()
        return new_booking

    except IntegrityError:
        db.rollback()
        # Class was already booked
        raise AlreadyBookedError()
    except Exception:
        db.rollback()
        raise


def get_user_bookings(db: Session, user_id: int) -> List[tuple[Booking, FitnessClass]]:
    """
    Retrieves a list of all classes booked by a user.
    Returns a list of tuples containing (Booking, FitnessClass) for easy serialization.
    """
    return (
        db.query(Booking, FitnessClass)
        .join(FitnessClass, Booking.class_id == FitnessClass.id)
        .filter(Booking.user_id == user_id)
        .order_by(FitnessClass.dateTime)
        .all()
    )
