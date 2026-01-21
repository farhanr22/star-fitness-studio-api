"""Database model for class bookings."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.core.utils import now_in_ist


class Booking(Base):
    """Represents a user's booking for a fitness class."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    
    # The authenticated user who made the booking
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    # The class that was booked
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    fitness_class = relationship("FitnessClass")
    
    # Client details provided at the time of booking
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=now_in_ist, nullable=False)
    
    __table_args__ = (
        # A user cannot book the same class more than once.
        UniqueConstraint('user_id', 'class_id', name='_user_class_uc'),
    )