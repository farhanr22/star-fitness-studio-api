"""Pydantic schemas for the classes module."""

from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator, field_serializer, Field


class ClassBase(BaseModel):
    """Base schema for class data."""
    name: str = Field(..., min_length=1)
    instructor: str = Field(..., min_length=1)
    
    # Map this field to 'availableSlots' key in API requests/responses
    available_slots: int = Field(..., gt=0, alias="availableSlots")

    class Config:
        # Use field alias for serialization in both ways
        populate_by_name = True
        from_attributes = True


class ClassCreate(ClassBase):
    """Schema for creating a new class."""
    dateTime: datetime

    @field_validator("dateTime")
    @classmethod
    def validate_datetime_is_utc(cls, v: datetime) -> datetime:
        """Ensure incoming datetime is UTC and convert to IST for storage."""
        if v.tzinfo is None:
            raise ValueError("dateTime must be timezone-aware")
        return v.astimezone(ZoneInfo("Asia/Kolkata"))


class ClassResponse(ClassBase):
    """Schema for returning class data."""
    id: int
    dateTime: datetime

    @field_serializer('dateTime')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize the IST datetime to a UTC datetime string with 'Z'."""
        utc_time = dt.astimezone(ZoneInfo("UTC"))
        return utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')