"""
Centralized error handling for FastAPI applications.

Provides:
- Standardized error response format
- Error tracking integration hooks
- Retry logic for transient errors
- Detailed logging with context
"""

import logging
import traceback
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from psycopg2 import InterfaceError, OperationalError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


# ============================================================================
# ERROR RESPONSE SCHEMA
# ============================================================================


class ErrorResponse:
    """Standardized error response format."""

    @staticmethod
    def format_error(
        error: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Format error response consistently.

        Args:
            error: Error code or type
            message: Human-readable error message
            details: Additional error details
            request_id: Request ID for tracking

        Returns:
            Formatted error dict
        """
        response = {
            "error": error,
            "message": message or "An error occurred",
        }

        if details:
            response["details"] = details

        if request_id:
            response["request_id"] = request_id

        return response


# ============================================================================
# ERROR CATEGORIES
# ============================================================================


class TransientError(Exception):
    """Error that may succeed on retry (network, timeout, etc.)."""

    pass


class ValidationErrorException(Exception):
    """Error in request validation."""

    pass


class DatabaseError(Exception):
    """Database operation error."""

    pass


# ============================================================================
# ERROR HANDLERS
# ============================================================================


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPException with standardized format.

    Args:
        request: FastAPI request
        exc: HTTPException instance

    Returns:
        JSONResponse with error details
    """
    request_id = request.headers.get("X-Request-ID")

    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.format_error(
            error=f"http_{exc.status_code}",
            message=exc.detail,
            request_id=request_id,
        ),
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: ValidationError from Pydantic

    Returns:
        JSONResponse with validation error details
    """
    request_id = request.headers.get("X-Request-ID")

    # Extract validation errors
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        f"Validation error: {len(errors)} fields",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "errors": errors,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.format_error(
            error="validation_error",
            message="Request validation failed",
            details={"validation_errors": errors},
            request_id=request_id,
        ),
    )


async def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle database-related errors.

    Args:
        request: FastAPI request
        exc: Database exception

    Returns:
        JSONResponse with appropriate error
    """
    request_id = request.headers.get("X-Request-ID")

    # Determine if error is transient
    is_transient = isinstance(exc, (OperationalError, InterfaceError))

    if is_transient:
        logger.warning(
            f"Transient database error: {exc}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "error_type": type(exc).__name__,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse.format_error(
                error="database_unavailable",
                message="Database temporarily unavailable. Please retry.",
                details={"retry_after": 5},
                request_id=request_id,
            ),
            headers={"Retry-After": "5"},
        )

    # Non-transient database error
    logger.error(
        f"Database error: {exc}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "error_type": type(exc).__name__,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.format_error(
            error="database_error",
            message="Database operation failed",
            request_id=request_id,
        ),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected errors.

    Args:
        request: FastAPI request
        exc: Exception instance

    Returns:
        JSONResponse with error details
    """
    request_id = request.headers.get("X-Request-ID")

    # Log full traceback for unexpected errors
    logger.error(
        f"Unexpected error: {exc}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        },
        exc_info=True,
    )

    # TODO: Send to error tracking service (Sentry, etc.)
    # send_to_error_tracking(exc, request)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.format_error(
            error="internal_error",
            message="An unexpected error occurred",
            request_id=request_id,
        ),
    )


# ============================================================================
# RETRY LOGIC
# ============================================================================


async def retry_on_transient_error(
    func, max_retries: int = 3, backoff_factor: float = 1.0, *args, **kwargs
) -> Any:
    """
    Retry function on transient errors with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for backoff delay
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result of successful function call

    Raises:
        Exception from last failed attempt
    """
    import asyncio

    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except (OperationalError, InterfaceError, TransientError) as e:
            last_exception = e

            if attempt < max_retries - 1:
                delay = backoff_factor * (2**attempt)
                logger.warning(
                    f"Transient error on attempt {attempt + 1}/{max_retries}. "
                    f"Retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Failed after {max_retries} attempts: {e}",
                    exc_info=True,
                )

    # All retries failed
    raise last_exception


# ============================================================================
# ERROR TRACKING INTEGRATION
# ============================================================================


def send_to_error_tracking(exc: Exception, request: Request) -> None:
    """
    Send error to external tracking service (Sentry, etc.).

    This is a placeholder for actual error tracking integration.

    Args:
        exc: Exception that occurred
        request: FastAPI request
    """
    # TODO: Implement error tracking integration
    # Example with Sentry:
    # import sentry_sdk
    # with sentry_sdk.push_scope() as scope:
    #     scope.set_context("request", {
    #         "url": str(request.url),
    #         "method": request.method,
    #         "headers": dict(request.headers),
    #     })
    #     sentry_sdk.capture_exception(exc)

    pass


def setup_error_handlers(app) -> None:
    """
    Register all error handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler((OperationalError, InterfaceError), database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers registered")
