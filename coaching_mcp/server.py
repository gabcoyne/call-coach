"""
FastMCP Server for Gong Call Coaching Agent.
Provides on-demand coaching tools accessible via Claude Desktop.
"""
import logging
import os
import sys
from typing import Any

from fastmcp import FastMCP

from config import settings
from coaching_mcp.tools.analyze_call import analyze_call_tool
from coaching_mcp.tools.get_rep_insights import get_rep_insights_tool
from coaching_mcp.tools.search_calls import search_calls_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _validate_environment() -> None:
    """
    Validate that all required environment variables are present.

    Raises:
        SystemExit: If any required variable is missing
    """
    required_vars = [
        "GONG_API_KEY",
        "GONG_API_SECRET",
        "GONG_API_BASE_URL",
        "ANTHROPIC_API_KEY",
        "DATABASE_URL",
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        logger.error(f"✗ Missing required environment variables: {', '.join(missing)}")
        logger.error("Set these in Horizon UI or .env file before deployment")
        sys.exit(1)

    logger.info("✓ All required environment variables present")


def _validate_database_connection() -> None:
    """
    Test database connectivity with a simple query.

    Raises:
        SystemExit: If database connection fails
    """
    from db import fetch_one

    try:
        # Verify sslmode is present for Neon
        if "sslmode=require" not in settings.database_url:
            logger.error("✗ DATABASE_URL must include sslmode=require for Neon")
            logger.error(f"Example: postgresql://user:pass@host/db?sslmode=require")
            sys.exit(1)

        # Test connection with simple query
        result = fetch_one("SELECT 1 as test")
        if result and result.get("test") == 1:
            logger.info("✓ Database connection successful")
        else:
            logger.error("✗ Database query returned unexpected result")
            sys.exit(1)

    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        logger.error("Verify DATABASE_URL and Neon database is accessible")
        sys.exit(1)


def _validate_gong_api() -> None:
    """
    Test Gong API authentication with minimal request.

    Raises:
        SystemExit: If Gong API authentication fails
    """
    from datetime import datetime, timedelta
    from gong.client import GongClient, GongAPIError

    try:
        with GongClient() as client:
            # Test with minimal date range (last 7 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)

            # Attempt to list calls (will fail auth if credentials invalid)
            calls, _ = client.list_calls(
                from_date=from_date.isoformat() + "Z",
                to_date=to_date.isoformat() + "Z",
            )

            logger.info("✓ Gong API authentication successful")

    except GongAPIError as e:
        if "401" in str(e) or "authentication" in str(e).lower():
            logger.error("✗ Gong API authentication failed")
            logger.error("Verify GONG_API_KEY and GONG_API_SECRET are correct")
        else:
            logger.error(f"✗ Gong API error: {e}")
            logger.error("Verify GONG_API_BASE_URL is correct tenant URL")
        sys.exit(1)

    except Exception as e:
        logger.error(f"✗ Gong API unreachable: {e}")
        logger.error("Verify GONG_API_BASE_URL and network connectivity")
        sys.exit(1)


def _validate_anthropic_api() -> None:
    """
    Validate Anthropic API key format.

    Raises:
        SystemExit: If API key format is invalid
    """
    api_key = settings.anthropic_api_key

    # Check format (should start with sk-ant-)
    if not api_key.startswith("sk-ant-"):
        logger.error("✗ ANTHROPIC_API_KEY has invalid format")
        logger.error("Expected format: sk-ant-...")
        sys.exit(1)

    logger.info("✓ Anthropic API key validated")

# Initialize FastMCP server
mcp = FastMCP("Gong Call Coaching Agent")


# Register tools
@mcp.tool()
def analyze_call(
    call_id: str,
    dimensions: list[str] | None = None,
    use_cache: bool = True,
    include_transcript_snippets: bool = True,
    force_reanalysis: bool = False,
) -> dict[str, Any]:
    """
    Deep-dive analysis of a specific call with coaching insights.

    Analyzes a Gong call across multiple coaching dimensions (product knowledge,
    discovery, objection handling, engagement) and provides detailed feedback
    with specific examples and action items.

    Args:
        call_id: Gong call ID to analyze
        dimensions: List of dimensions to analyze. Options:
                   - "product_knowledge": Technical accuracy and positioning
                   - "discovery": Question quality, active listening, needs discovery
                   - "objection_handling": Identification and response quality
                   - "engagement": Rapport, energy, talk-listen ratio
                   Default: all dimensions
        use_cache: Use cached analyses if available (default: True)
        include_transcript_snippets: Include actual quotes from call (default: True)
        force_reanalysis: Bypass cache and regenerate analysis (default: False)

    Returns:
        Comprehensive coaching analysis with scores, strengths, areas for improvement,
        specific examples from the call, and actionable recommendations.

    Example:
        >>> result = analyze_call("1464927526043145564", dimensions=["discovery"])
        >>> print(f"Discovery score: {result['scores']['discovery']}/100")
        >>> for strength in result['strengths']:
        >>>     print(f"✓ {strength}")
    """
    return analyze_call_tool(
        call_id=call_id,
        dimensions=dimensions,
        use_cache=use_cache,
        include_transcript_snippets=include_transcript_snippets,
        force_reanalysis=force_reanalysis,
    )


@mcp.tool()
def get_rep_insights(
    rep_email: str,
    time_period: str = "last_30_days",
    product_filter: str | None = None,
) -> dict[str, Any]:
    """
    Performance trends and coaching history for a specific sales rep.

    Aggregates coaching data across multiple calls to identify patterns,
    track improvement over time, and generate personalized coaching plans.

    Args:
        rep_email: Email address of the sales rep (e.g., "john.doe@prefect.io")
        time_period: Time range for analysis. Options:
                    - "last_7_days"
                    - "last_30_days" (default)
                    - "last_quarter"
                    - "last_year"
                    - "all_time"
        product_filter: Filter by product. Options: "prefect", "horizon", "both", or None for all

    Returns:
        Comprehensive rep performance data including:
        - Score trends over time for each dimension
        - Skill gaps with priority rankings
        - Improvement areas and recent wins
        - Personalized coaching plan

    Example:
        >>> insights = get_rep_insights("sarah.jones@prefect.io", time_period="last_quarter")
        >>> print(f"Calls analyzed: {insights['rep_info']['calls_analyzed']}")
        >>> for gap in insights['skill_gaps']:
        >>>     print(f"Gap: {gap['area']} - Current: {gap['current_score']}, Target: {gap['target_score']}")
    """
    return get_rep_insights_tool(
        rep_email=rep_email,
        time_period=time_period,
        product_filter=product_filter,
    )


@mcp.tool()
def search_calls(
    rep_email: str | None = None,
    product: str | None = None,
    call_type: str | None = None,
    date_range: dict[str, str] | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    has_objection_type: str | None = None,
    topics: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Find calls matching specific criteria.

    Powerful search across all analyzed calls with support for multiple filters.
    Useful for finding similar situations, identifying patterns, or pulling
    examples for training.

    Args:
        rep_email: Filter by sales rep email
        product: Filter by product ("prefect", "horizon", "both")
        call_type: Filter by call type ("discovery", "demo", "technical_deep_dive", "negotiation")
        date_range: Date range filter, e.g., {"start": "2025-01-01", "end": "2025-01-31"}
        min_score: Minimum overall score (0-100)
        max_score: Maximum overall score (0-100)
        has_objection_type: Filter for calls with specific objection types:
                           "pricing", "timing", "technical", "competitor"
        topics: Filter by topics discussed (e.g., ["Objections", "Product Demo"])
        limit: Maximum number of results (default: 20, max: 100)

    Returns:
        List of matching calls with metadata and summary scores.

    Example:
        >>> # Find all discovery calls with pricing objections
        >>> calls = search_calls(
        >>>     call_type="discovery",
        >>>     has_objection_type="pricing",
        >>>     min_score=70,
        >>>     limit=10
        >>> )
        >>> for call in calls:
        >>>     print(f"{call['title']}: {call['overall_score']}/100")
    """
    return search_calls_tool(
        rep_email=rep_email,
        product=product,
        call_type=call_type,
        date_range=date_range,
        min_score=min_score,
        max_score=max_score,
        has_objection_type=has_objection_type,
        topics=topics,
        limit=limit,
    )


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Gong Call Coaching MCP Server")
    logger.info("=" * 60)

    # Run startup validation checks
    try:
        logger.info("\n🔍 Running pre-flight validation checks...")

        _validate_environment()
        _validate_database_connection()
        _validate_gong_api()
        _validate_anthropic_api()

        logger.info("\n✅ All validation checks passed!")
        logger.info("=" * 60)
        logger.info("🚀 MCP server ready - 3 tools registered")
        logger.info("=" * 60)

    except SystemExit:
        # Validation failed - error already logged
        logger.error("\n❌ Startup validation failed - server cannot start")
        logger.error("=" * 60)
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Unexpected error during validation: {e}")
        logger.error("=" * 60)
        sys.exit(1)

    # Run the server
    mcp.run()
