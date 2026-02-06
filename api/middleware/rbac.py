"""
RBAC (Role-Based Access Control) middleware.

Provides authentication and authorization utilities for the API:
- get_current_user: Extract and validate user from request
- require_role: Decorator to enforce role requirements on endpoints
"""

import logging
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request

from db import queries

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> dict[str, Any]:
    """
    Get current user from request headers.

    For now, uses X-User-Email header for testing.
    In production, this will extract the user from Clerk JWT.

    Args:
        request: FastAPI request object

    Returns:
        User dict with id, email, name, role

    Raises:
        HTTPException: 401 if not authenticated, 404 if user not found
    """
    # For testing: get email from X-User-Email header
    email = request.headers.get("X-User-Email")

    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Fetch user from database
    user = queries.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {email}")

    logger.debug(f"Authenticated user: {user['email']} (role: {user['role']})")

    return user


def require_role(allowed_roles: list[str]):
    """
    Decorator to require specific roles for an endpoint.

    Usage:
        @require_role(["manager", "admin"])
        async def manager_only_endpoint(user = Depends(get_current_user)):
            ...

    Args:
        allowed_roles: List of role strings that are allowed

    Returns:
        Decorator function

    Raises:
        HTTPException: 403 if user doesn't have required role
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (passed by Depends(get_current_user))
            user = kwargs.get("user")

            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            if user["role"] not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
