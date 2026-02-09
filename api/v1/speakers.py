"""
Speaker role management API endpoints.

Provides endpoints for managers to view and update speaker roles:
- GET /speakers/{speaker_id}: Get speaker details including role
- PUT /speakers/{speaker_id}/role: Update speaker role
- GET /speakers/{speaker_id}/history: Get role change history
- POST /speakers/bulk-update-roles: Update multiple speaker roles
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.middleware.rbac import get_current_user
from db import queries

router = APIRouter(prefix="/speakers", tags=["speakers"])


# Request/Response Models
class UpdateRoleRequest(BaseModel):
    """Request body for updating a speaker's role."""

    role: str | None = Field(
        description="New role for speaker: 'ae', 'se', 'csm', 'support', or null to remove role"
    )


class BulkUpdateRequest(BaseModel):
    """Request body for bulk updating speaker roles."""

    updates: list[dict[str, Any]] = Field(
        description="List of updates with speaker_id and role"
    )


# Endpoints
@router.get("/")
async def list_speakers(
    company_side_only: bool = True,
    role: str | None = None,
    include_unassigned: bool = True,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    List all speakers with optional filtering.

    Only accessible to managers and admins.

    Headers:
        X-User-Email: User email for authentication

    Query Parameters:
        company_side_only: If true, only return Prefect staff (default: true)
        role: Optional role filter ('ae', 'se', 'csm', 'support')
        include_unassigned: If false, exclude speakers with no role (default: true)

    Returns:
        List of unique speakers (one per email) with aggregated call stats

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    speakers = queries.get_all_speakers(
        company_side_only=company_side_only,
        role_filter=role,
        include_unassigned=include_unassigned,
    )

    # Convert UUIDs and timestamps to strings
    return [
        {
            **speaker,
            "id": str(speaker["id"]),
            "first_seen": (
                speaker["first_seen"].isoformat() if speaker.get("first_seen") else None
            ),
            "last_call_date": (
                speaker["last_call_date"].isoformat()
                if speaker.get("last_call_date")
                else None
            ),
        }
        for speaker in speakers
    ]


@router.get("/{speaker_id}")
async def get_speaker(
    speaker_id: UUID,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get speaker details including role.

    Only accessible to managers and admins.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        speaker_id: UUID of the speaker

    Returns:
        Speaker object with id, email, name, role, company_side, etc.

    Raises:
        HTTPException: 403 if user is not a manager or admin
        HTTPException: 404 if speaker not found
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    speaker = queries.get_speaker_role(speaker_id)

    if not speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")

    # Convert UUIDs to strings for JSON serialization
    return {
        **speaker,
        "id": str(speaker["id"]),
        "call_id": str(speaker["call_id"]) if speaker.get("call_id") else None,
        "manager_id": str(speaker["manager_id"]) if speaker.get("manager_id") else None,
    }


@router.put("/{speaker_id}/role")
async def update_speaker_role(
    speaker_id: UUID,
    request: UpdateRoleRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Update speaker role.

    Only accessible to managers and admins. The change is logged to
    speaker_role_history with the user's email.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        speaker_id: UUID of the speaker

    Request Body:
        {
            "role": "ae" | "se" | "csm" | "support" | null
        }

    Returns:
        Updated speaker object

    Raises:
        HTTPException: 403 if user is not a manager or admin
        HTTPException: 404 if speaker not found
        HTTPException: 400 if role is invalid
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    try:
        updated_speaker = queries.update_speaker_role(
            speaker_id=speaker_id,
            role=request.role,
            changed_by=user["email"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated_speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")

    # Convert UUIDs to strings
    return {
        **updated_speaker,
        "id": str(updated_speaker["id"]),
        "call_id": str(updated_speaker["call_id"]) if updated_speaker.get("call_id") else None,
        "manager_id": str(updated_speaker["manager_id"]) if updated_speaker.get("manager_id") else None,
    }


@router.get("/{speaker_id}/history")
async def get_speaker_history(
    speaker_id: UUID,
    limit: int = 50,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Get role change history for a speaker.

    Only accessible to managers and admins.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        speaker_id: UUID of the speaker

    Query Parameters:
        limit: Maximum number of history entries to return (default: 50)

    Returns:
        List of history entries with old_role, new_role, changed_by, changed_at, etc.

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    history = queries.get_speaker_role_history(speaker_id, limit=limit)

    # Convert UUIDs and timestamps to strings
    return [
        {
            **entry,
            "id": str(entry["id"]),
            "speaker_id": str(entry["speaker_id"]),
            "changed_at": entry["changed_at"].isoformat() if entry.get("changed_at") else None,
        }
        for entry in history
    ]


@router.post("/bulk-update-roles")
async def bulk_update_roles(
    request: BulkUpdateRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Update multiple speaker roles in a single transaction.

    Only accessible to managers and admins. All updates are performed
    in a transaction - if any update fails, all changes are rolled back.

    Headers:
        X-User-Email: User email for authentication

    Request Body:
        {
            "updates": [
                {"speaker_id": "uuid-string", "role": "ae"},
                {"speaker_id": "uuid-string", "role": "se"},
                ...
            ]
        }

    Returns:
        {
            "updated": int,              # Number successfully updated
            "failed": list[str],         # Speaker IDs that failed
            "speakers": list[dict]       # Updated speaker records
        }

    Raises:
        HTTPException: 403 if user is not a manager or admin
        HTTPException: 400 if any role is invalid or request malformed
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    # Parse and validate updates
    try:
        updates = [
            (UUID(update["speaker_id"]), update["role"])
            for update in request.updates
        ]
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request format: {e}. Expected list of {{speaker_id, role}}"
        )

    try:
        result = queries.bulk_update_speaker_roles(
            updates=updates,
            changed_by=user["email"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Convert UUIDs to strings in speakers
    result["speakers"] = [
        {
            **speaker,
            "id": str(speaker["id"]),
            "call_id": str(speaker["call_id"]) if speaker.get("call_id") else None,
            "manager_id": str(speaker["manager_id"]) if speaker.get("manager_id") else None,
        }
        for speaker in result["speakers"]
    ]

    return result
