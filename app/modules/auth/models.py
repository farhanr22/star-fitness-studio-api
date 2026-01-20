"""User database model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.core.utils import now_in_ist
from app.db.session import Base

class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    refresh_token_jti_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_in_ist, nullable=False)
