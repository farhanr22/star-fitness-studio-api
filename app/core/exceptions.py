"""Base exception classes and custom application-wide exception handlers."""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.schemas import ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception class for application-specific exceptions."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def http_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles exceptions raised by application logic (subclasses of AppException)."""

    logger.error(f"AppException: {exc.__class__.__name__} - {exc.message}")
    error = ErrorDetail(loc=["server"], msg=exc.message, type="application_error")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(errors=[error]).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles Pydantic validation errors."""

    errors = [
        ErrorDetail(loc=list(err["loc"]), msg=err["msg"], type=err["type"])
        for err in exc.errors()
    ]

    # Human friendly formatting for ErrorDetail
    error_summary = "; ".join(
        f"field='{'.'.join(map(str, err.loc))}', reason='{err.msg}'" for err in errors
    )
    logger.warning(f"Validation error on request {request.method} {request.url.path}: {error_summary}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(errors=errors).model_dump(),
    )


async def unhandled_exception_middleware(request: Request, call_next):
    """Catches any unhandled exceptions and returns a generic 500 error."""
    
    try:
        return await call_next(request)
    except Exception as e:
        logger.error("Unhandled exception caught", exc_info=True)
        error = ErrorDetail(
            loc=["server"], msg="Internal Server Error", type="unhandled_exception"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(errors=[error]).model_dump(),
        )
