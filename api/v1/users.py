"""
Users API endpoints.

Provides user authentication and profile endpoints:
- GET /me: Get current authenticated user
"""

from typing import Any

from fastapi import APIRouter, Depends

from api.middleware.rbac import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user_endpoint(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """
    Get current authenticated user with role.

    Returns user profile including:
    - id: User UUID
    - email: User email address
    - name: User full name
    - role: User role (admin, manager, rep)

    Headers:
        X-User-Email: User email for authentication (testing only)

    Returns:
        User profile dict
    """
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }
