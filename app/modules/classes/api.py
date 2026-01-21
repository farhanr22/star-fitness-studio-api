"""API endpoints for managing fitness classes."""

from typing import List
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth import get_current_user, User
from app.modules.classes import service
from app.modules.classes.schemas import ClassCreate, ClassResponse
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/classes", response_model=ClassResponse, status_code=201)
def create_new_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new fitness class. Requires authentication."""
    logger.info(
        f"Request to create new class received from user '{current_user.email}'"
    )
    new_class = service.create_class(
        db=db, class_data=class_in, creator_id=current_user.id
    )
    return new_class


@router.get("/classes", response_model=List[ClassResponse])
def get_all_upcoming_classes(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    """Fetch all upcoming fitness classes. Requires authentication."""
    logger.info("Request to fetch all upcoming classes received.")
    classes = service.get_upcoming_classes(db=db)
    return classes
