"""
Team management API endpoints.

Provides endpoints for managers to view team members and their calls:
- GET /reps: Get all reps managed by current user (managers only)
- GET /calls: Get all calls from managed reps (managers only)
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from api.middleware.rbac import get_current_user
from db import queries

router = APIRouter(prefix="/team", tags=["team"])


@router.get("/reps")
async def get_team_reps(
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Get all reps managed by current user.

    Only accessible to managers and admins.

    Headers:
        X-User-Email: Manager email for authentication

    Returns:
        List of rep profiles with id, email, name, role

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    # Get managed reps
    reps = queries.get_managed_reps(user["email"])

    return [
        {
            "id": str(rep["id"]),
            "email": rep["email"],
            "name": rep["name"],
            "role": rep["role"],
        }
        for rep in reps
    ]


@router.get("/calls")
async def get_team_calls(
    limit: int = 50,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Get all calls from managed reps.

    Only accessible to managers and admins. Managers see calls from
    their team members, admins see all calls.

    Headers:
        X-User-Email: Manager email for authentication

    Query Parameters:
        limit: Maximum number of calls to return (default: 50)

    Returns:
        List of call objects

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    # Get calls filtered by role
    calls = queries.get_calls_for_user(user["email"], user["role"], limit)

    # Convert UUIDs to strings for JSON serialization
    return [
        {
            **call,
            "id": str(call["id"]),
        }
        for call in calls
    ]
