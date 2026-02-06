"""
REST API Bridge for FastMCP Tools

Exposes FastMCP coaching tools as REST HTTP endpoints for the Next.js frontend.
This bridge allows the React app to call MCP tools via standard HTTP POST requests.

Production Features:
- Rate limiting per-user and per-endpoint
- Response compression (gzip)
- API versioning (/api/v1/)
- Standardized error handling
- Request/response logging
- Performance monitoring
"""

import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from analysis.learning_insights import get_learning_insights
from analysis.opportunity_coaching import (
    analyze_objection_progression,
    analyze_opportunity_patterns,
    assess_relationship_strength,
    generate_coaching_recommendations,
    identify_recurring_themes,
)

# Import error handlers
from api.error_handlers import setup_error_handlers
from api.monitoring import router as monitoring_router

# Import versioned API routers
from api.v1 import router as v1_router

# Import MCP tool implementations
from coaching_mcp.tools.analyze_call import analyze_call_tool
from coaching_mcp.tools.get_rep_insights import get_rep_insights_tool
from coaching_mcp.tools.search_calls import search_calls_tool
from db import queries
from db.models import CoachingDimension, KnowledgeBaseCategory, Product
from knowledge_base.loader import KnowledgeBaseManager
from middleware.compression import CompressionMiddleware

# Import middleware
from middleware.rate_limit import RateLimitMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Call Coaching API",
    description="REST API bridge for FastMCP coaching tools with production features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# MIDDLEWARE SETUP
# ============================================================================

# CORS middleware (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",  # Alternative port
        "https://*.vercel.app",  # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-Request-ID",
        "X-Response-Time",
    ],
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    default_rate_limit=100,  # 100 requests per minute
    default_burst=150,
    expensive_rate_limit=20,  # 20 requests per minute for expensive ops
    expensive_burst=30,
)

# Compression middleware
app.add_middleware(
    CompressionMiddleware,
    minimum_size=500,  # Only compress responses > 500 bytes
    compression_level=6,
)


# Request ID and timing middleware
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """Add request ID and timing to all requests."""
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Time request
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - "
        f"{response.headers['X-Response-Time']}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": float(response.headers["X-Response-Time"].rstrip("ms")),
        },
    )

    return response


# ============================================================================
# ERROR HANDLERS
# ============================================================================

setup_error_handlers(app)

# ============================================================================
# API ROUTERS
# ============================================================================

# Include versioned API routes
app.include_router(v1_router)

# Include monitoring routes
app.include_router(monitoring_router)


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


class KnowledgeEntryRequest(BaseModel):
    product: str = Field(..., description="Product: prefect or horizon")
    category: str = Field(..., description="Category: feature, use_case, competitor, etc.")
    content: str = Field(..., description="Markdown content")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")


class RubricRequest(BaseModel):
    name: str = Field(..., description="Rubric name")
    version: str = Field(..., description="Semantic version (e.g., 1.0.0)")
    category: str = Field(..., description="Coaching dimension category")
    criteria: dict[str, Any] = Field(..., description="Evaluation criteria")
    scoring_guide: dict[str, Any] = Field(..., description="Scoring guidelines")
    examples: dict[str, Any] | None = Field(None, description="Example analyses")


# Initialize knowledge base manager
kb_manager = KnowledgeBaseManager()


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


# ============================================================================
# KNOWLEDGE BASE ENDPOINTS
# ============================================================================


@app.get("/knowledge")
async def list_knowledge_entries(
    product: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """List knowledge base entries with optional filters."""
    try:
        product_enum = Product(product) if product else None
        category_enum = KnowledgeBaseCategory(category) if category else None

        entries = kb_manager.list_entries(product=product_enum, category=category_enum)

        return [
            {
                "id": str(entry.id),
                "product": entry.product.value,
                "category": entry.category.value,
                "content": entry.content,
                "metadata": entry.metadata,
                "last_updated": entry.last_updated.isoformat() if entry.last_updated else None,
            }
            for entry in entries
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing knowledge entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge")
async def create_or_update_knowledge_entry(request: KnowledgeEntryRequest) -> dict[str, Any]:
    """Create or update a knowledge base entry."""
    try:
        product = Product(request.product)
        category = KnowledgeBaseCategory(request.category)

        entry = kb_manager.create_or_update_entry(
            product=product,
            category=category,
            content=request.content,
            metadata=request.metadata,
        )

        return {
            "id": str(entry.id),
            "product": entry.product.value,
            "category": entry.category.value,
            "content": entry.content,
            "metadata": entry.metadata,
            "last_updated": entry.last_updated.isoformat() if entry.last_updated else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating/updating knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/knowledge")
async def delete_knowledge_entry(product: str, category: str) -> dict[str, bool]:
    """Delete a knowledge base entry."""
    try:
        product_enum = Product(product)
        category_enum = KnowledgeBaseCategory(category)

        success = kb_manager.delete_entry(product=product_enum, category=category_enum)

        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")

        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/history")
async def get_knowledge_history(product: str, category: str) -> list[dict[str, Any]]:
    """Get version history for a knowledge base entry."""
    try:
        product_enum = Product(product)
        category_enum = KnowledgeBaseCategory(category)

        history = kb_manager.get_entry_history(product=product_enum, category=category_enum)

        return history
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching knowledge history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/stats")
async def get_knowledge_stats() -> dict[str, Any]:
    """Get knowledge base statistics."""
    try:
        stats = kb_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching knowledge stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COACHING RUBRICS ENDPOINTS
# ============================================================================


@app.get("/knowledge/rubrics")
async def list_rubrics(
    category: str | None = None,
    active_only: bool = True,
    all_versions: bool = False,
) -> list[dict[str, Any]]:
    """List coaching rubrics with optional filters."""
    try:
        category_enum = CoachingDimension(category) if category else None

        if all_versions and category_enum:
            rubrics = kb_manager.get_rubric_versions(category_enum)
        else:
            rubrics = kb_manager.list_rubrics(active_only=active_only, category=category_enum)

        return [
            {
                "id": str(rubric.id),
                "name": rubric.name,
                "version": rubric.version,
                "category": rubric.category.value,
                "criteria": rubric.criteria,
                "scoring_guide": rubric.scoring_guide,
                "examples": rubric.examples,
                "active": rubric.active,
                "created_at": rubric.created_at.isoformat() if rubric.created_at else None,
                "deprecated_at": rubric.deprecated_at.isoformat() if rubric.deprecated_at else None,
            }
            for rubric in rubrics
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing rubrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/rubrics")
async def create_rubric(request: RubricRequest) -> dict[str, Any]:
    """Create a new coaching rubric version."""
    try:
        rubric_data = {
            "name": request.name,
            "version": request.version,
            "category": request.category,
            "criteria": request.criteria,
            "scoring_guide": request.scoring_guide,
            "examples": request.examples or {},
        }

        rubric = kb_manager.create_rubric(rubric_data)

        return {
            "id": str(rubric.id),
            "name": rubric.name,
            "version": rubric.version,
            "category": rubric.category.value,
            "criteria": rubric.criteria,
            "scoring_guide": rubric.scoring_guide,
            "examples": rubric.examples,
            "active": rubric.active,
            "created_at": rubric.created_at.isoformat() if rubric.created_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating rubric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/knowledge/rubrics/{rubric_id}")
async def update_rubric(rubric_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Update rubric metadata (active status, examples)."""
    try:
        rubric = kb_manager.update_rubric(rubric_id, updates)

        if not rubric:
            raise HTTPException(status_code=404, detail="Rubric not found")

        return {
            "id": str(rubric.id),
            "name": rubric.name,
            "version": rubric.version,
            "category": rubric.category.value,
            "criteria": rubric.criteria,
            "scoring_guide": rubric.scoring_guide,
            "examples": rubric.examples,
            "active": rubric.active,
            "created_at": rubric.created_at.isoformat() if rubric.created_at else None,
            "deprecated_at": rubric.deprecated_at.isoformat() if rubric.deprecated_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rubric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"error": "Internal server error", "detail": str(exc)}
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
