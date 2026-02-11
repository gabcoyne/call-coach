"""
FastMCP Server for Gong Call Coaching Agent.
Provides on-demand coaching tools accessible via Claude Desktop.
"""

import argparse
import logging
import os
import sys
from typing import Any

from fastmcp import FastMCP

from coaching_mcp.shared import settings
from coaching_mcp.tools.analyze_call import analyze_call_tool
from coaching_mcp.tools.get_coaching_feed import get_coaching_feed_tool
from coaching_mcp.tools.get_rep_insights import get_rep_insights_tool
from coaching_mcp.tools.search_calls import search_calls_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _validate_environment() -> None:
    """
    Validate that all required environment variables are present.
    Uses the settings object which automatically loads from .env file.

    Raises:
        SystemExit: If any required variable is missing
    """
    try:
        # Access settings attributes to trigger validation
        # If any required field is missing, pydantic will raise ValidationError
        _ = settings.gong_api_key
        _ = settings.gong_api_secret
        _ = settings.gong_api_base_url
        _ = settings.anthropic_api_key
        _ = settings.database_url
        logger.info("✓ All required environment variables present")
    except Exception as e:
        logger.error(f"✗ Missing required environment variables: {e}")
        logger.error("Set these in .env file before starting the server")
        sys.exit(1)


def _validate_database_connection() -> None:
    """
    Test database connectivity and verify schema.

    Raises:
        SystemExit: If database connection fails or required tables are missing
    """
    from db import fetch_all, fetch_one

    try:
        # Verify sslmode is present for Neon
        if "sslmode=require" not in settings.database_url:
            logger.error("✗ DATABASE_URL must include sslmode=require for Neon")
            logger.error("Example: postgresql://user:pass@host/db?sslmode=require")
            sys.exit(1)

        # Test connection with simple query
        result = fetch_one("SELECT 1 as test")
        if result and result.get("test") == 1:
            logger.info("✓ Database connection successful")
        else:
            logger.error("✗ Database query returned unexpected result")
            sys.exit(1)

        # Verify required tables exist
        required_tables = ["calls", "speakers", "transcripts", "coaching_sessions"]
        existing_tables = fetch_all(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """
        )
        existing_table_names = {row["table_name"] for row in existing_tables}

        missing_tables = [t for t in required_tables if t not in existing_table_names]
        if missing_tables:
            logger.error(f"✗ Missing required database tables: {', '.join(missing_tables)}")
            logger.error("Run database migrations to create required schema")
            sys.exit(1)

        logger.info(f"✓ Database schema validated ({len(required_tables)} tables)")

    except SystemExit:
        # Re-raise SystemExit to preserve validation failure behavior
        raise
    except Exception as e:
        logger.error(f"✗ Database validation failed: {e}")
        logger.error("Verify DATABASE_URL and Neon database is accessible")
        sys.exit(1)


def _validate_database_connection_only() -> None:
    """
    Test basic database connectivity without schema validation.
    Used in development mode for faster startup.

    Raises:
        SystemExit: If database connection fails
    """
    from db import fetch_one

    try:
        # Verify sslmode is present for Neon
        if "sslmode=require" not in settings.database_url:
            logger.error("✗ DATABASE_URL must include sslmode=require for Neon")
            logger.error("Example: postgresql://user:pass@host/db?sslmode=require")
            sys.exit(1)

        # Test connection with simple query
        result = fetch_one("SELECT 1 as test")
        if result and result.get("test") == 1:
            logger.info("✓ Database connection successful (dev mode - schema not validated)")
        else:
            logger.error("✗ Database query returned unexpected result")
            sys.exit(1)

    except SystemExit:
        # Re-raise SystemExit to preserve validation failure behavior
        raise
    except Exception as e:
        logger.error(f"✗ Database validation failed: {e}")
        logger.error("Verify DATABASE_URL and Neon database is accessible")
        sys.exit(1)


def _validate_gong_api(dev_mode: bool = False) -> None:
    """
    Test Gong API authentication with minimal request.

    Non-fatal for timeouts (logs warning), fatal for auth failures.
    Skipped entirely in development mode.

    Args:
        dev_mode: If True, skips Gong API validation entirely

    Raises:
        SystemExit: If Gong API authentication definitively fails (401/403)
    """
    if dev_mode:
        logger.info("✓ Gong API validation skipped (dev mode)")
        return

    from datetime import datetime, timedelta

    import httpx

    from gong.client import GongAPIError, GongClient

    try:
        # Create client with short timeout for validation
        client_kwargs = {
            "api_key": settings.gong_api_key,
            "api_secret": settings.gong_api_secret,
            "base_url": settings.gong_api_base_url,
        }

        # Temporarily patch the client to use 1-second timeout for validation
        original_init = GongClient.__init__

        def patched_init(self, **kwargs):
            original_init(self, **kwargs)
            # Replace the client with a shorter timeout
            self.client.close()
            self.client = httpx.Client(
                base_url=self.base_url,
                auth=(self.api_key, self.api_secret),
                timeout=1.0,  # 1 second timeout for validation
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

        GongClient.__init__ = patched_init

        try:
            with GongClient(**client_kwargs) as client:
                # Test with minimal date range (last 1 day instead of 7)
                to_date = datetime.now()
                from_date = to_date - timedelta(days=1)

                # Attempt to list calls (will fail auth if credentials invalid)
                calls, _ = client.list_calls(
                    from_date=from_date.isoformat() + "Z",
                    to_date=to_date.isoformat() + "Z",
                )

                logger.info("✓ Gong API authentication successful")
        finally:
            # Restore original __init__
            GongClient.__init__ = original_init

    except httpx.TimeoutException:
        # Non-fatal: log warning but allow server to start
        logger.warning("⚠️  Gong API validation timed out (server will still start)")
        logger.warning("This may indicate slow network or Gong API issues")
        return

    except GongAPIError as e:
        # Check for definitive auth failures (401, 403)
        error_str = str(e)
        if (
            "401" in error_str
            or "403" in error_str
            or "authentication" in error_str.lower()
            or "unauthorized" in error_str.lower()
        ):
            logger.error("✗ Gong API authentication failed")
            logger.error("Verify GONG_API_KEY and GONG_API_SECRET are correct")
            sys.exit(1)
        else:
            # Other errors - log warning but don't fail startup
            logger.warning(f"⚠️  Gong API validation error (non-fatal): {e}")
            logger.warning("Server will start, but Gong API may not be accessible")
            return

    except Exception as e:
        # Check if it's a timeout-related error
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            logger.warning("⚠️  Gong API validation timed out (server will still start)")
            logger.warning("This may indicate slow network or Gong API issues")
            return

        # Other unexpected errors - log warning but don't fail startup
        logger.warning(f"⚠️  Gong API validation failed (non-fatal): {e}")
        logger.warning("Server will start, but Gong API may not be accessible")
        return


def _validate_anthropic_api() -> None:
    """
    Validate Anthropic API key format.

    Raises:
        SystemExit: If API key format is invalid
    """
    api_key = settings.anthropic_api_key

    # Check key is long enough and not a placeholder
    if len(api_key) < 20:
        logger.error("✗ ANTHROPIC_API_KEY is too short (minimum 20 characters)")
        logger.error("Verify you have a valid API key from Anthropic Console")
        sys.exit(1)

    # Check for obvious placeholders
    placeholder_patterns = ["your_key", "replace", "placeholder", "xxx", "example"]
    if any(pattern in api_key.lower() for pattern in placeholder_patterns):
        logger.error("✗ ANTHROPIC_API_KEY appears to be a placeholder")
        logger.error("Replace with actual API key from Anthropic Console")
        sys.exit(1)

    logger.info("✓ Anthropic API key validated")


# Initialize FastMCP server
mcp = FastMCP("Gong Call Coaching Agent")

# Server status tracking
_server_ready = False


# Add health check endpoint
async def health_check(request):
    """Health check endpoint for monitoring server status."""
    from starlette.responses import JSONResponse

    if _server_ready:
        return JSONResponse({"status": "ok", "tools": 5})
    else:
        return JSONResponse({"status": "starting"}, status_code=503)


# Add health endpoint to the SSE app
mcp.sse_app().add_route("/health", health_check, methods=["GET"])


# Register tools
@mcp.tool()
def analyze_opportunity(opportunity_id: str) -> dict[str, Any]:
    """
    Analyze an opportunity with holistic coaching insights across all calls and emails.

    Provides:
    - Coaching score patterns across all touchpoints
    - Recurring themes and evolution
    - Objection handling patterns (resolved vs recurring)
    - Relationship strength trends
    - Specific coaching recommendations for next steps

    Args:
        opportunity_id: UUID of the opportunity to analyze

    Returns:
        Comprehensive opportunity analysis with coaching insights
    """
    from analysis.opportunity_coaching import (
        analyze_objection_progression,
        analyze_opportunity_patterns,
        assess_relationship_strength,
        generate_coaching_recommendations,
        identify_recurring_themes,
    )
    from db import queries

    # Verify opportunity exists
    opp = queries.get_opportunity(opportunity_id)
    if not opp:
        return {"error": f"Opportunity not found: {opportunity_id}"}

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


@mcp.tool()
def get_learning_insights(rep_email: str, focus_area: str = "discovery") -> dict[str, Any]:
    """
    Compare rep's performance to top performers on closed-won deals.

    ROLE-AWARE COMPARISON: Automatically detects the rep's role and compares them
    ONLY to top performers in the same role (AE to AE, SE to SE, CSM to CSM).
    This ensures apples-to-apples comparison on role-appropriate behaviors.

    Shows specific behavioral differences with concrete examples from successful calls.
    Focus areas: discovery, objections, product_knowledge, rapport, next_steps.

    Args:
        rep_email: Email of the rep to analyze
        focus_area: Area to focus on (discovery, objections, product_knowledge, rapport, next_steps)

    Returns:
        Behavioral differences and exemplar moments from top performers in the same role.
        Includes 'rep_role' and 'comparison_note' fields showing role-based filtering.
    """
    from analysis.learning_insights import get_learning_insights as _get_learning_insights

    return _get_learning_insights(rep_email, focus_area)


@mcp.tool()
def get_coaching_feed(
    type_filter: str | None = None,
    time_filter: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    offset: int = 0,
    include_dismissed: bool = False,
    include_team_insights: bool = False,
    rep_email: str | None = None,
) -> dict[str, Any]:
    """
    Get personalized coaching feed with recent insights and recommendations.

    Generates feed items from:
    - Recent coaching sessions (last 7 days by default)
    - High-impact moments (significant score improvements/declines)
    - Team-wide patterns (for managers)
    - Milestone achievements

    Args:
        type_filter: Filter by type (call_analysis, team_insight, highlight, milestone)
        time_filter: Time range (today, this_week, this_month, custom)
        start_date: Custom start date (ISO format)
        end_date: Custom end date (ISO format)
        limit: Maximum number of items to return
        offset: Pagination offset
        include_dismissed: Include dismissed items
        include_team_insights: Include team-wide insights (managers only)
        rep_email: Filter to specific rep (None = current user)

    Returns:
        dict with:
            - items: List of feed items
            - team_insights: Team-wide insights (managers only)
            - highlights: Notable moments
            - total_count: Total available items
            - has_more: Whether more items available
            - new_items_count: Count of unread items
    """
    return get_coaching_feed_tool(
        type_filter=type_filter,
        time_filter=time_filter,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        include_dismissed=include_dismissed,
        include_team_insights=include_team_insights,
        rep_email=rep_email,
    )


@mcp.tool()
def analyze_call(
    call_id: str,
    dimensions: list[str] | None = None,
    use_cache: bool = True,
    include_transcript_snippets: bool = True,
    force_reanalysis: bool = False,
    role: str | None = None,
) -> dict[str, Any]:
    """
    Deep-dive analysis of a specific call with role-aware coaching insights.

    ROLE-AWARE EVALUATION: Automatically detects speaker role (AE, SE, CSM) and evaluates
    against role-specific rubrics. AEs are judged on selling skills, SEs on technical
    communication, CSMs on relationship management. You can override auto-detection
    with the 'role' parameter.

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
        role: Override role detection (ae, se, csm). If not provided, auto-detects
              from primary speaker's assigned role in staff_roles table.

    Returns:
        Comprehensive coaching analysis with scores, strengths, areas for improvement,
        specific examples from the call, and actionable recommendations. Includes
        'evaluated_as_role' field showing which role rubric was used.

    Example:
        >>> result = analyze_call("1464927526043145564", dimensions=["discovery"])
        >>> print(f"Discovery score: {result['scores']['discovery']}/100")
        >>> print(f"Evaluated as: {result['rep_analyzed']['evaluated_as_role']}")
        >>> for strength in result['strengths']:
        >>>     print(f"✓ {strength}")
    """
    return analyze_call_tool(
        call_id=call_id,
        dimensions=dimensions,
        use_cache=use_cache,
        include_transcript_snippets=include_transcript_snippets,
        force_reanalysis=force_reanalysis,
        role=role,
    )


@mcp.tool()
def get_rep_insights(
    rep_email: str,
    time_period: str = "last_30_days",
    product_filter: str | None = None,
) -> dict[str, Any]:
    """
    Performance trends and coaching history for a specific sales rep.

    ROLE-AWARE BENCHMARKING: Compares rep's performance against team members in
    the same role only. AEs are benchmarked against other AEs, SEs against SEs,
    and CSMs against CSMs, ensuring fair and relevant comparisons.

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
        - Skill gaps with priority rankings (compared to same role only)
        - Improvement areas and recent wins
        - Personalized coaching plan
        - Rep role field showing which role cohort they're compared against

    Example:
        >>> insights = get_rep_insights("sarah.jones@prefect.io", time_period="last_quarter")
        >>> print(f"Role: {insights['rep_info']['role']}")
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
    role: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Find calls matching specific criteria with role-aware filtering.

    ROLE-AWARE SEARCH: Filter calls by speaker role (ae, se, csm) to find
    examples relevant to specific roles. Useful for finding role-appropriate
    training examples or comparing performance within role cohorts.

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
        role: Filter by speaker role (ae, se, csm) - only returns calls evaluated
              with this role's rubric
        limit: Maximum number of results (default: 20, max: 100)

    Returns:
        List of matching calls with metadata and summary scores.

    Example:
        >>> # Find SE discovery calls with high technical scores
        >>> calls = search_calls(
        >>>     role="se",
        >>>     call_type="discovery",
        >>>     min_score=80,
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
        role=role,
        limit=limit,
    )


def main(dev: bool = False) -> None:
    """
    Start the MCP server with optional development mode.

    Args:
        dev: Enable development mode with relaxed validation
    """
    global _server_ready

    logger.info("=" * 60)
    logger.info("Starting Gong Call Coaching MCP Server")
    if dev:
        logger.info("🏗️  Dev mode: skipping expensive validations")
    logger.info("=" * 60)

    # Run startup validation checks (optional - controlled by env var)
    skip_validation = os.getenv("SKIP_VALIDATION", "false").lower() == "true"

    if not skip_validation:
        try:
            logger.info("\n🔍 Running pre-flight validation checks...")

            _validate_environment()

            # Use relaxed validation in dev mode
            if dev:
                _validate_database_connection_only()
                _validate_gong_api(dev_mode=True)
            else:
                _validate_database_connection()
                _validate_gong_api(dev_mode=False)

            _validate_anthropic_api()

            logger.info("\n✅ All validation checks passed!")
            logger.info("=" * 60)
            logger.info("🚀 MCP server ready - 5 tools registered")
            logger.info("=" * 60)

            # Mark server as ready
            _server_ready = True

        except SystemExit:
            # Validation failed - error already logged
            logger.error("\n❌ Startup validation failed - server cannot start")
            logger.error("=" * 60)
            sys.exit(1)

        except Exception as e:
            logger.error(f"\n❌ Unexpected error during validation: {e}")
            logger.error("=" * 60)
            sys.exit(1)
    else:
        logger.info("\n⚠️  Validation skipped (SKIP_VALIDATION=true)")
        logger.info("=" * 60)
        logger.info("🚀 MCP server starting - 5 tools registered")
        logger.info("=" * 60)
        _server_ready = True

    # Run the server
    mcp.run()


def main_dev() -> None:
    """
    Start the MCP server in development mode.
    Wrapper for `main(dev=True)` to be used with uv script entry.
    """
    main(dev=True)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Gong Call Coaching MCP Server")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode with relaxed validation (skips Gong API check, basic DB check only)",
    )
    args = parser.parse_args()

    main(dev=args.dev)
