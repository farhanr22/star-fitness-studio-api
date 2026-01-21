"""Pydantic schemas for the bookings module."""

from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.core.utils import serialize_datetime_to_utc_z_format


class BookingCreate(BaseModel):
    """Schema for creating a new booking."""
    class_id: int
    client_name: str = Field(..., min_length=1)
    client_email: EmailStr


class BookingResponse(BaseModel):
    """Schema for the response after creating a booking."""
    id: int
    class_id: int
    user_id: int
    client_name: str
    client_email: EmailStr
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return serialize_datetime_to_utc_z_format(dt)

    class Config:
        from_attributes = True


class UserBookingResponse(BaseModel):
    """
    Schema for the 'list of booked classes' response.
    Combines class and booking details.
    """
    # Class specific fields
    class_id: int = Field(..., alias="classId")
    name: str
    instructor: str
    date_time: datetime = Field(..., alias="dateTime")
    
    # Booking specific fields
    booking_id: int = Field(..., alias="bookingId")
    booked_at: datetime = Field(..., alias="bookedAt")
    booked_as_name: str = Field(..., alias="bookedAsName")
    booked_as_email: EmailStr = Field(..., alias="bookedAsEmail")

    @field_serializer('date_time', 'booked_at')
    def serialize_time_string(self, dt: datetime, _info) -> str:
        return serialize_datetime_to_utc_z_format(dt)

    class Config:
        from_attributes = True
        populate_by_name = True