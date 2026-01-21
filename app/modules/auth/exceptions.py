"""Auth-specific exceptions."""

from app.core.exceptions import AppException


class InvalidCredentials(AppException):
    """Raised when login credentials are invalid."""
    
    def __init__(self):
        super().__init__("Invalid email or password", status_code=401)


class UserAlreadyExists(AppException):
    """Raised when trying to create a user with existing email."""
    
    def __init__(self):
        super().__init__("User with this email already exists", status_code=400)


class TokenExpired(AppException):
    """Raised when token has expired."""
    
    def __init__(self):
        super().__init__("Token has expired", status_code=401)


class InvalidToken(AppException):
    """Raised when token is invalid."""
    
    def __init__(self):
        super().__init__("Invalid token", status_code=401)


class AuthenticationError(AppException):
    """Raised when authentication fails on a protected endpoint."""
    
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message, status_code=401)