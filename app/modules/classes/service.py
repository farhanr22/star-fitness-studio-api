"""Service layer for class-related business logic."""

from typing import List
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.utils import now_in_ist
from app.modules.classes.models import FitnessClass
from app.modules.classes.schemas import ClassCreate
from app.modules.classes.exceptions import (
    InvalidClassTimeError,
    InstructorBookingConflictError,
)

logger = logging.getLogger(__name__)

def create_class(db: Session, class_data: ClassCreate, creator_id: int) -> FitnessClass:
    """Creates a new fitness class."""
    logger.info(f"Creating class '{class_data.name}' for creator ID {creator_id}")

    if class_data.dateTime < now_in_ist():
        raise InvalidClassTimeError()

    new_class = FitnessClass(
        name=class_data.name,
        instructor=class_data.instructor,
        dateTime=class_data.dateTime,
        capacity=class_data.available_slots,  # Store the capacity information separately
        available_slots=class_data.available_slots,
        creator_id=creator_id,
    )

    db.add(new_class)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Instructor booking conflict for instructor '{class_data.instructor}' at '{class_data.dateTime}'"
        )
        raise InstructorBookingConflictError()

    db.refresh(new_class)
    logger.info(
        f"Successfully created class '{new_class.name}' with ID {new_class.id}"
    )
    return new_class


def get_upcoming_classes(db: Session) -> List[FitnessClass]:
    """Retrieves all classes scheduled for the future."""
    return (
        db.query(FitnessClass)
        .filter(FitnessClass.dateTime > now_in_ist())
        .order_by(FitnessClass.dateTime)
        .all()
    )


def get_class_by_id(db: Session, class_id: int) -> FitnessClass | None:
    """Retrieves a single class by its ID."""
    return db.query(FitnessClass).filter(FitnessClass.id == class_id).first()
