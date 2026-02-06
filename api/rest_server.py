"""
REST API Bridge for FastMCP Tools

Exposes FastMCP coaching tools as REST HTTP endpoints for the Next.js frontend.
This bridge allows the React app to call MCP tools via standard HTTP POST requests.
"""
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Call Coaching API",
    description="REST API bridge for FastMCP coaching tools",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",  # Alternative port
        "https://*.vercel.app",   # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models for type safety
class AnalyzeCallRequest(BaseModel):
    call_id: str = Field(..., description="Gong call ID to analyze")
    dimensions: list[str] | None = Field(None, description="Dimensions to analyze")
    use_cache: bool = Field(True, description="Use cached results if available")
    include_transcript_snippets: bool = Field(True, description="Include transcript quotes")
    force_reanalysis: bool = Field(False, description="Force regeneration of analysis")


class RepInsightsRequest(BaseModel):
    rep_email: str = Field(..., description="Email of the sales rep")
    time_period: str = Field("last_30_days", description="Time period for analysis")
    product_filter: str | None = Field(None, description="Filter by product")


class SearchCallsRequest(BaseModel):
    rep_email: str | None = None
    product: str | None = None
    call_type: str | None = None
    date_range: dict[str, str] | None = None
    min_score: int | None = None
    max_score: int | None = None
    has_objection_type: str | None = None
    topics: list[str] | None = None
    limit: int = 20


class AnalyzeOpportunityRequest(BaseModel):
    opportunity_id: str = Field(..., description="UUID of the opportunity")


class LearningInsightsRequest(BaseModel):
    rep_email: str = Field(..., description="Email of the sales rep")
    focus_area: str = Field("discovery", description="Area to focus on")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "call-coaching-api", "tools": 5}


# Tool endpoints
@app.post("/tools/analyze_call")
async def analyze_call_endpoint(request: AnalyzeCallRequest) -> dict[str, Any]:
    """
    Analyze a specific call with coaching insights.

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
        return result
    except Exception as e:
        logger.error(f"Error analyzing call {request.call_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/get_rep_insights")
async def get_rep_insights_endpoint(request: RepInsightsRequest) -> dict[str, Any]:
    """
    Get performance insights and trends for a sales rep.

    Returns score trends, skill gaps, improvement areas, and coaching plan.
    """
    try:
        result = get_rep_insights_tool(
            rep_email=request.rep_email,
            time_period=request.time_period,
            product_filter=request.product_filter,
        )
        return result
    except Exception as e:
        logger.error(f"Error getting insights for {request.rep_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/search_calls")
async def search_calls_endpoint(request: SearchCallsRequest) -> list[dict[str, Any]]:
    """
    Search for calls matching specific criteria.

    Returns list of calls with metadata and scores.
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
        return result
    except Exception as e:
        logger.error(f"Error searching calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/analyze_opportunity")
async def analyze_opportunity_endpoint(request: AnalyzeOpportunityRequest) -> dict[str, Any]:
    """
    Analyze an opportunity with holistic coaching insights.

    Returns patterns, themes, objections, relationship strength, and recommendations.
    """
    try:
        opportunity_id = request.opportunity_id

        # Verify opportunity exists
        opp = queries.get_opportunity(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail=f"Opportunity not found: {opportunity_id}")

        # Run all analyses
        patterns = analyze_opportunity_patterns(opportunity_id)
        themes = identify_recurring_themes(opportunity_id)
        objections = analyze_objection_progression(opportunity_id)
        relationship = assess_relationship_strength(opportunity_id)
        recommendations = generate_coaching_recommendations(opportunity_id)

        return {
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing opportunity {request.opportunity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/get_learning_insights")
async def get_learning_insights_endpoint(request: LearningInsightsRequest) -> dict[str, Any]:
    """
    Compare rep's performance to top performers on closed-won deals.

    Returns behavioral differences with concrete examples from successful calls.
    """
    try:
        result = get_learning_insights(
            rep_email=request.rep_email,
            focus_area=request.focus_area,
        )
        return result
    except Exception as e:
        logger.error(f"Error getting learning insights for {request.rep_email}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    # Run the REST API server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
