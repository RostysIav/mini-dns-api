"""Custom exceptions and error handlers for the Mini DNS API."""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class DNSBaseError(Exception):
    """Base exception for all DNS API errors."""
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred"
    
    def __init__(
        self,
        detail: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
        **extra: Any,
    ) -> None:
        self.detail = detail or self.default_detail
        self.status_code = status_code or self.default_status_code
        self.headers = headers
        self.error_code = error_code or self.__class__.__name__
        self.extra = extra
        super().__init__(self.detail)


class ValidationError(DNSBaseError):
    """Raised when input validation fails."""
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation error"


class NotFoundError(DNSBaseError):
    """Raised when a requested resource is not found."""
    default_status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The requested resource was not found"


class ConflictError(DNSBaseError):
    """Raised when a resource conflict occurs."""
    default_status_code = status.HTTP_409_CONFLICT
    default_detail = "A conflict occurred with the current state of the resource"


class RateLimitExceededError(DNSBaseError):
    """Raised when rate limit is exceeded."""
    default_status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded"


class DNSError(DNSBaseError):
    """Base exception for DNS-related errors."""
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "DNS error occurred"


class RecordValidationError(ValidationError):
    """Raised when DNS record validation fails."""
    default_detail = "Invalid DNS record data"


class HostnameValidationError(ValidationError):
    """Raised when hostname validation fails."""
    default_detail = "Invalid hostname format"


class CNAMELoopError(DNSError):
    """Raised when a CNAME loop is detected."""
    default_detail = "CNAME loop detected"


class RecordConflictError(ConflictError):
    """Raised when a record conflict is detected."""
    default_detail = "Record conflict detected"


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
        headers=getattr(exc, "headers", None),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "ValidationError",
                "message": "Invalid request data",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "details": exc.errors(),
            }
        },
    )


def dns_base_error_handler(request: Request, exc: DNSBaseError) -> JSONResponse:
    """Handle custom DNS exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": str(exc.detail),
                "status_code": exc.status_code,
                **exc.extra,
            }
        },
        headers=exc.headers,
    )


def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    # In production, you might want to log this error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "InternalServerError",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        },
    )


def setup_exception_handlers(app):
    """Register exception handlers with the FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(DNSBaseError, dns_base_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
