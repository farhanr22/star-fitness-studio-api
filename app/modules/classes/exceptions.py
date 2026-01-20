"""Custom exceptions for the classes module."""

from app.core.exceptions import AppException


class InvalidClassTimeError(AppException):
    """Raised when trying to create a class in the past."""

    def __init__(self):
        super().__init__("Cannot create a class in the past", status_code=400)


class InstructorBookingConflictError(AppException):
    """Raised when an instructor is already booked at a specific time."""

    def __init__(self):
        super().__init__(
            "This instructor is already booked for a class at this time",
            status_code=409,
        )
