"""Core Pydantic schemas for the application, such as error responses."""

from typing import List, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Schema for a single structured error detail."""
    loc: List[str | int] | None = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Schema for a unified error response body."""
    errors: List[ErrorDetail]