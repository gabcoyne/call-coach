"""
Opportunity API Endpoints

Provides REST API access to opportunity data including:
- Listing opportunities with filters and pagination
- Fetching opportunity details
- Accessing opportunity timeline (calls and emails)
"""

import logging
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from db import queries

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class OpportunityListResponse(BaseModel):
    """Response model for opportunity list endpoint."""

    opportunities: list[dict[str, Any]] = Field(description="List of opportunities")
    total: int = Field(description="Total count of opportunities matching filters")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    has_more: bool = Field(description="Whether there are more pages available")


class OpportunityDetailResponse(BaseModel):
    """Response model for opportunity detail endpoint."""

    opportunity: dict[str, Any] = Field(description="Opportunity details")
    timeline: list[dict[str, Any]] = Field(description="Timeline of calls and emails", default=[])


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("", response_model=OpportunityListResponse)
async def list_opportunities(
    owner_email: str | None = Query(None, description="Filter by opportunity owner email"),
    stage: str | None = Query(None, description="Filter by stage (e.g., 'Prospecting')"),
    health_score_min: float | None = Query(
        None, description="Minimum health score (0.0-10.0)", ge=0.0, le=10.0
    ),
    health_score_max: float | None = Query(
        None, description="Maximum health score (0.0-10.0)", ge=0.0, le=10.0
    ),
    search: str | None = Query(None, description="Search in opportunity name and account name"),
    sort: Literal["updated_desc", "close_date_asc", "amount_desc", "name_asc"] = Query(
        "updated_desc", description="Sort order"
    ),
    page: int = Query(1, description="Page number (1-indexed)", ge=1),
    page_size: int = Query(20, description="Items per page", ge=1, le=100),
) -> OpportunityListResponse:
    """
    List opportunities with optional filters and pagination.

    Supports filtering by:
    - Owner email
    - Stage (e.g., Prospecting, Qualification, Proposal, Negotiation, Closed Won)
    - Health score range
    - Search text (name, account)

    Supports sorting by:
    - updated_desc: Most recently updated first (default)
    - close_date_asc: Soonest closing date first
    - amount_desc: Highest value first
    - name_asc: Alphabetical by name

    Returns paginated results with total count and pagination metadata.
    """
    try:
        # Build filters dict
        filters: dict[str, Any] = {}
        if owner_email:
            filters["owner_email"] = owner_email
        if stage:
            filters["stage"] = stage
        if health_score_min is not None:
            filters["health_score_min"] = health_score_min
        if health_score_max is not None:
            filters["health_score_max"] = health_score_max
        if search:
            filters["search"] = search

        # Calculate offset from page number
        offset = (page - 1) * page_size

        # Query database
        result = queries.search_opportunities(
            filters=filters, sort=sort, limit=page_size, offset=offset
        )

        # Calculate pagination metadata
        total = result["total"]  # type: ignore[call-overload,index]
        has_more = offset + page_size < total

        return OpportunityListResponse(
            opportunities=result["opportunities"],  # type: ignore[call-overload,index]
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more,
        )

    except Exception as e:
        logger.error(f"Error listing opportunities: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list opportunities: {str(e)}",
        ) from e


@router.get("/{opportunity_id}", response_model=OpportunityDetailResponse)
async def get_opportunity_detail(
    opportunity_id: str,
    timeline_limit: int = Query(50, description="Number of timeline items to return", ge=1, le=200),
    timeline_offset: int = Query(0, description="Timeline pagination offset", ge=0),
) -> OpportunityDetailResponse:
    """
    Get detailed information about a specific opportunity.

    Returns:
    - Opportunity metadata (name, account, owner, stage, close date, amount, health score)
    - Counts of associated calls and emails
    - Timeline of calls and emails (paginated)

    Timeline items are sorted chronologically (newest first) and include:
    - Calls: title, date, participants, coaching scores
    - Emails: subject, sender, recipients, sent date, body snippet
    """
    try:
        # Get opportunity details
        opportunity = queries.get_opportunity(opportunity_id)

        if not opportunity:
            raise HTTPException(
                status_code=404,
                detail=f"Opportunity not found: {opportunity_id}",
            )

        # Get timeline items
        timeline_result = queries.get_opportunity_timeline(
            opp_id=opportunity_id, limit=timeline_limit, offset=timeline_offset
        )

        return OpportunityDetailResponse(
            opportunity=opportunity, timeline=timeline_result["items"]  # type: ignore[call-overload,index]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching opportunity {opportunity_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch opportunity: {str(e)}",
        ) from e
