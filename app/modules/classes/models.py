"""Database model for fitness classes."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.core.utils import now_in_ist


class FitnessClass(Base):
    """Represents a single fitness class session."""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    instructor = Column(String, nullable=False)
    dateTime = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Total capacity of the class, set at creation
    capacity = Column(Integer, nullable=False)
    # Current available slots, decremented on booking
    available_slots = Column(Integer, nullable=False)
    
    # Foreign key to the user who created the class
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User")
    
    created_at = Column(DateTime(timezone=True), default=now_in_ist, nullable=False)
    
    __table_args__ = (
        # An instructor cannot be booked for two classes at the same time
        UniqueConstraint('instructor', 'dateTime', name='_instructor_datetime_uc'),
    )