"""
Rubric management API endpoints.

Provides endpoints for managers to view and edit rubric criteria:
- GET /rubrics/{role}/{dimension}: Get criteria for role-dimension
- GET /rubrics/{role}: Get all criteria for role
- PUT /rubrics/criteria/{criterion_id}: Update a criterion
- POST /rubrics/criteria: Create new criterion
- DELETE /rubrics/criteria/{criterion_id}: Delete a criterion
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.middleware.rbac import get_current_user
from db import queries

router = APIRouter(prefix="/rubrics", tags=["rubrics"])


# Request/Response Models
class UpdateCriterionRequest(BaseModel):
    """Request body for updating a criterion."""

    description: str | None = Field(
        None, description="New description (10-500 chars)"
    )
    weight: int | None = Field(None, ge=0, le=100, description="New weight (0-100%)")
    max_score: int | None = Field(
        None, ge=1, le=100, description="New max score (1-100)"
    )
    display_order: int | None = Field(None, description="New display order")


class CreateCriterionRequest(BaseModel):
    """Request body for creating a criterion."""

    role: str = Field(description="Speaker role: ae, se, csm, support")
    dimension: str = Field(
        description="Dimension: discovery, engagement, product_knowledge, objection_handling, five_wins"
    )
    criterion_name: str = Field(description="Short name (max 100 chars)")
    description: str = Field(description="Detailed description (10-500 chars)")
    weight: int = Field(ge=0, le=100, description="Weight percentage (0-100)")
    max_score: int = Field(ge=1, le=100, description="Max score (1-100)")
    display_order: int = Field(default=0, description="Display order")


# Endpoints
@router.get("/{role}/{dimension}")
async def get_criteria_for_dimension(
    role: str,
    dimension: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Get rubric criteria for a specific role-dimension combination.

    Only accessible to managers and admins.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        role: Speaker role (ae, se, csm, support)
        dimension: Coaching dimension (discovery, engagement, product_knowledge,
                   objection_handling, five_wins)

    Returns:
        List of criteria ordered by display_order

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    try:
        criteria = queries.get_rubric_criteria(role, dimension)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid role or dimension: {e}")

    # Convert UUIDs and timestamps to strings
    return [
        {
            **criterion,
            "id": str(criterion["id"]),
            "created_at": (
                criterion["created_at"].isoformat() if criterion.get("created_at") else None
            ),
            "updated_at": (
                criterion["updated_at"].isoformat() if criterion.get("updated_at") else None
            ),
        }
        for criterion in criteria
    ]


@router.get("/{role}")
async def get_criteria_for_role(
    role: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """
    Get all rubric criteria for a specific role across all dimensions.

    Only accessible to managers and admins.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        role: Speaker role (ae, se, csm, support)

    Returns:
        List of criteria ordered by dimension and display_order

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    try:
        criteria = queries.get_rubric_criteria(role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid role: {e}")

    # Convert UUIDs and timestamps to strings
    return [
        {
            **criterion,
            "id": str(criterion["id"]),
            "created_at": (
                criterion["created_at"].isoformat() if criterion.get("created_at") else None
            ),
            "updated_at": (
                criterion["updated_at"].isoformat() if criterion.get("updated_at") else None
            ),
        }
        for criterion in criteria
    ]


@router.put("/criteria/{criterion_id}")
async def update_criterion(
    criterion_id: UUID,
    request: UpdateCriterionRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Update a rubric criterion.

    Only accessible to managers and admins. Changes are logged to
    rubric_change_log with the user's email.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        criterion_id: UUID of the criterion

    Request Body:
        {
            "description"?: "new description",
            "weight"?: 20,
            "max_score"?: 15,
            "display_order"?: 5
        }

    Returns:
        Updated criterion object

    Raises:
        HTTPException: 403 if user is not a manager or admin
        HTTPException: 404 if criterion not found
        HTTPException: 400 if validation fails
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    try:
        updated_criterion = queries.update_rubric_criterion(
            criterion_id=criterion_id,
            description=request.description,
            weight=request.weight,
            max_score=request.max_score,
            display_order=request.display_order,
            changed_by=user["email"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated_criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")

    # Convert UUIDs and timestamps to strings
    return {
        **updated_criterion,
        "id": str(updated_criterion["id"]),
        "created_at": (
            updated_criterion["created_at"].isoformat()
            if updated_criterion.get("created_at")
            else None
        ),
        "updated_at": (
            updated_criterion["updated_at"].isoformat()
            if updated_criterion.get("updated_at")
            else None
        ),
    }


@router.post("/criteria")
async def create_criterion(
    request: CreateCriterionRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Create a new rubric criterion.

    Only accessible to managers and admins. Creation is logged to
    rubric_change_log with the user's email.

    Headers:
        X-User-Email: User email for authentication

    Request Body:
        {
            "role": "ae",
            "dimension": "discovery",
            "criterion_name": "New Criterion",
            "description": "Description...",
            "weight": 10,
            "max_score": 10,
            "display_order": 0
        }

    Returns:
        Newly created criterion object

    Raises:
        HTTPException: 403 if user is not a manager or admin
        HTTPException: 400 if validation fails or criterion name already exists
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    try:
        new_criterion = queries.create_rubric_criterion(
            role=request.role,
            dimension=request.dimension,
            criterion_name=request.criterion_name,
            description=request.description,
            weight=request.weight,
            max_score=request.max_score,
            display_order=request.display_order,
            changed_by=user["email"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle duplicate criterion name constraint
        if "unique_criterion_per_role_dimension" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Criterion '{request.criterion_name}' already exists for {request.role}/{request.dimension}",
            )
        raise HTTPException(status_code=400, detail=str(e))

    # Convert UUIDs and timestamps to strings
    return {
        **new_criterion,
        "id": str(new_criterion["id"]),
        "created_at": (
            new_criterion["created_at"].isoformat()
            if new_criterion.get("created_at")
            else None
        ),
        "updated_at": (
            new_criterion["updated_at"].isoformat()
            if new_criterion.get("updated_at")
            else None
        ),
    }


@router.delete("/criteria/{criterion_id}")
async def delete_criterion(
    criterion_id: UUID,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Delete a rubric criterion.

    Only accessible to managers and admins. Deletion is logged to
    rubric_change_log with the user's email.

    Headers:
        X-User-Email: User email for authentication

    Path Parameters:
        criterion_id: UUID of the criterion

    Returns:
        {"deleted": true} or {"deleted": false}

    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if user["role"] not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Managers and admins only")

    deleted = queries.delete_rubric_criterion(
        criterion_id=criterion_id,
        changed_by=user["email"],
    )

    return {"deleted": deleted}
