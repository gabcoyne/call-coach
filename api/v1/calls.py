"""
Calls API endpoints with role-based access control.

Provides endpoints to retrieve calls filtered by user role:
- Reps see only their own calls
- Managers see their team's calls
- Admins see all calls
"""

from typing import Any

from fastapi import APIRouter, Depends

from api.middleware.rbac import get_current_user
from db import queries

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("")
async def get_calls(
    limit: int = 50,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Get calls filtered by user role.

    Access control:
    - Reps: See only their own calls
    - Managers: See calls from their team members
    - Admins: See all calls

    Headers:
        X-User-Email: User email for authentication

    Query Parameters:
        limit: Maximum number of calls to return (default: 50, max: 200)

    Returns:
        List of call objects with metadata
    """
    # Enforce max limit
    limit = min(limit, 200)

    # Get calls filtered by role
    calls = queries.get_calls_for_user(user["email"], user["role"], limit)

    # Convert UUIDs to strings and timestamps to ISO format
    return [
        {
            **call,
            "id": str(call["id"]),
            "scheduled_at": call["scheduled_at"].isoformat() if call.get("scheduled_at") else None,
            "created_at": call["created_at"].isoformat() if call.get("created_at") else None,
            "updated_at": call["updated_at"].isoformat() if call.get("updated_at") else None,
        }
        for call in calls
    ]
