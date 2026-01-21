"""Custom exceptions for the bookings module."""

from app.core.exceptions import AppException


class ClassNotFoundError(AppException):
    """Raised when a class with the given ID does not exist."""
    def __init__(self):
        super().__init__("Class not found", status_code=404)


class ClassIsFullError(AppException):
    """Raised when trying to book a class that has no available slots."""
    def __init__(self):
        super().__init__("Class is full, no available slots", status_code=409)


class AlreadyBookedError(AppException):
    """Raised when a user tries to book a class they have already booked."""
    def __init__(self):
        super().__init__("You have already booked this class", status_code=409)


class ClassInPastError(AppException):
    """Raised when trying to book a class that is scheduled in the past."""
    def __init__(self):
        super().__init__("Cannot book a class that is in the past", status_code=400)