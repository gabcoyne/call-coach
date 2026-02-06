"""
Versioned tool endpoints for API v1.

These endpoints provide stable interfaces to MCP tools with:
- Versioned request/response schemas
- Backward compatibility guarantees
- Deprecation warnings when needed
"""
import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import MCP tool implementations
from coaching_mcp.tools.analyze_call import analyze_call_tool
from coaching_mcp.tools.get_rep_insights import get_rep_insights_tool
from coaching_mcp.tools.search_calls import search_calls_tool
from analysis.opportunity_coaching import (
    analyze_opportunity_patterns,
    identify_recurring_themes,
    analyze_objection_progression,
    assess_relationship_strength,
    generate_coaching_recommendations,
)
from analysis.learning_insights import get_learning_insights
from db import queries

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS (v1)
# ============================================================================

class AnalyzeCallRequestV1(BaseModel):
    """Request schema for call analysis (v1)."""
    call_id: str = Field(..., description="Gong call ID to analyze")
    dimensions: list[str] | None = Field(None, description="Dimensions to analyze")
    use_cache: bool = Field(True, description="Use cached results if available")
    include_transcript_snippets: bool = Field(True, description="Include transcript quotes")
    force_reanalysis: bool = Field(False, description="Force regeneration of analysis")


class RepInsightsRequestV1(BaseModel):
    """Request schema for rep insights (v1)."""
    rep_email: str = Field(..., description="Email of the sales rep")
    time_period: str = Field("last_30_days", description="Time period for analysis")
    product_filter: str | None = Field(None, description="Filter by product")


class SearchCallsRequestV1(BaseModel):
    """Request schema for call search (v1)."""
    rep_email: str | None = None
    product: str | None = None
    call_type: str | None = None
    date_range: dict[str, str] | None = None
    min_score: int | None = None
    max_score: int | None = None
    has_objection_type: str | None = None
    topics: list[str] | None = None
    limit: int = 20
    offset: int = 0  # Added for pagination


class AnalyzeOpportunityRequestV1(BaseModel):
    """Request schema for opportunity analysis (v1)."""
    opportunity_id: str = Field(..., description="UUID of the opportunity")


class LearningInsightsRequestV1(BaseModel):
    """Request schema for learning insights (v1)."""
    rep_email: str = Field(..., description="Email of the sales rep")
    focus_area: str = Field("discovery", description="Area to focus on")


class PaginatedResponse(BaseModel):
    """Generic paginated response (v1)."""
    items: list[Any]
    total: int
    page: int
    page_size: int
    has_next: bool


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/analyze_call", response_model=dict[str, Any])
async def analyze_call_v1(request: AnalyzeCallRequestV1) -> dict[str, Any]:
    """
    Analyze a specific call with coaching insights (v1).

    Returns comprehensive coaching analysis with scores, strengths,
    areas for improvement, and actionable recommendations.
    """
    try:
        result = analyze_call_tool(
            call_id=request.call_id,
            dimensions=request.dimensions,
            use_cache=request.use_cache,
            include_transcript_snippets=request.include_transcript_snippets,
            force_reanalysis=request.force_reanalysis,
        )
        return {
            "api_version": "v1",
            "data": result,
        }
    except Exception as e:
        logger.error(f"Error analyzing call {request.call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_rep_insights", response_model=dict[str, Any])
async def get_rep_insights_v1(request: RepInsightsRequestV1) -> dict[str, Any]:
    """
    Get performance insights and trends for a sales rep (v1).

    Returns score trends, skill gaps, improvement areas, and coaching plan.
    """
    try:
        result = get_rep_insights_tool(
            rep_email=request.rep_email,
            time_period=request.time_period,
            product_filter=request.product_filter,
        )
        return {
            "api_version": "v1",
            "data": result,
        }
    except Exception as e:
        logger.error(f"Error getting insights for {request.rep_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search_calls", response_model=dict[str, Any])
async def search_calls_v1(request: SearchCallsRequestV1) -> dict[str, Any]:
    """
    Search for calls matching specific criteria (v1).

    Returns paginated list of calls with metadata and scores.
    """
    try:
        result = search_calls_tool(
            rep_email=request.rep_email,
            product=request.product,
            call_type=request.call_type,
            date_range=request.date_range,
            min_score=request.min_score,
            max_score=request.max_score,
            has_objection_type=request.has_objection_type,
            topics=request.topics,
            limit=request.limit,
        )

        # Add pagination metadata
        return {
            "api_version": "v1",
            "data": {
                "items": result,
                "total": len(result),
                "page": request.offset // request.limit if request.limit > 0 else 0,
                "page_size": request.limit,
                "has_next": len(result) == request.limit,
            }
        }
    except Exception as e:
        logger.error(f"Error searching calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze_opportunity", response_model=dict[str, Any])
async def analyze_opportunity_v1(request: AnalyzeOpportunityRequestV1) -> dict[str, Any]:
    """
    Analyze an opportunity with holistic coaching insights (v1).

    Returns patterns, themes, objections, relationship strength, and recommendations.
    """
    try:
        opportunity_id = request.opportunity_id

        # Verify opportunity exists
        opp = queries.get_opportunity(opportunity_id)
        if not opp:
            raise HTTPException(
                status_code=404,
                detail=f"Opportunity not found: {opportunity_id}"
            )

        # Run all analyses
        patterns = analyze_opportunity_patterns(opportunity_id)
        themes = identify_recurring_themes(opportunity_id)
        objections = analyze_objection_progression(opportunity_id)
        relationship = assess_relationship_strength(opportunity_id)
        recommendations = generate_coaching_recommendations(opportunity_id)

        return {
            "api_version": "v1",
            "data": {
                "opportunity": {
                    "id": opportunity_id,
                    "name": opp["name"],
                    "account": opp["account_name"],
                    "owner": opp["owner_email"],
                    "stage": opp["stage"],
                    "health_score": opp.get("health_score"),
                },
                "patterns": patterns,
                "themes": themes,
                "objections": objections,
                "relationship": relationship,
                "recommendations": recommendations,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing opportunity {request.opportunity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_learning_insights", response_model=dict[str, Any])
async def get_learning_insights_v1(request: LearningInsightsRequestV1) -> dict[str, Any]:
    """
    Compare rep's performance to top performers on closed-won deals (v1).

    Returns behavioral differences with concrete examples from successful calls.
    """
    try:
        result = get_learning_insights(
            rep_email=request.rep_email,
            focus_area=request.focus_area,
        )
        return {
            "api_version": "v1",
            "data": result,
        }
    except Exception as e:
        logger.error(f"Error getting learning insights for {request.rep_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
