"""Pydantic schemas for auth endpoints."""

from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    """Request schema for user signup."""
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class SignUpResponse(BaseModel):
    """Response schema for a successful user registration."""
    message: str


class TokenResponse(BaseModel):
    """Response schema for token endpoints."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True
