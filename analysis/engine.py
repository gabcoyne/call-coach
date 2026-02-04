"""
Core analysis engine for coaching insights.
Integrates Claude API with caching and chunking.
"""
import logging
from typing import Any
from uuid import UUID

from anthropic import Anthropic

from config import settings
from db import fetch_one
from db.models import CoachingDimension
from .cache import (
    generate_transcript_hash,
    get_cached_analysis,
    get_active_rubric_version,
    store_analysis_with_cache,
)

logger = logging.getLogger(__name__)

# Initialize Claude API client
anthropic_client = Anthropic(api_key=settings.anthropic_api_key)


def get_or_create_coaching_session(
    call_id: UUID,
    rep_id: UUID,
    dimension: CoachingDimension,
    transcript: str,
    force_reanalysis: bool = False,
    session_type: str = "on_demand",
) -> dict[str, Any]:
    """
    Get coaching session from cache or create new analysis.
    This is the main entry point for getting coaching insights.

    Args:
        call_id: Call UUID
        rep_id: Rep UUID
        dimension: Coaching dimension to analyze
        transcript: Full call transcript
        force_reanalysis: Bypass cache and regenerate
        session_type: Type of session (on_demand, weekly_review, etc.)

    Returns:
        Coaching session data with analysis
    """
    logger.info(
        f"Getting coaching session: call={call_id}, "
        f"dimension={dimension.value}, force={force_reanalysis}"
    )

    # Generate transcript hash for caching
    transcript_hash = generate_transcript_hash(transcript)

    # Get active rubric version
    try:
        rubric_version = get_active_rubric_version(dimension)
    except ValueError as e:
        logger.error(f"Failed to get rubric version: {e}")
        raise

    # Check cache if not forcing reanalysis
    if not force_reanalysis and settings.enable_caching:
        cached = get_cached_analysis(
            call_id=str(call_id),
            dimension=dimension,
            transcript_hash=transcript_hash,
            rubric_version=rubric_version,
        )

        if cached:
            logger.info(f"Returning cached analysis for call {call_id}")
            return cached

    # Cache miss or forced reanalysis - run new analysis
    logger.info(f"Running new analysis for call {call_id}, dimension={dimension.value}")

    # TODO: Phase 3 - Implement actual Claude API analysis
    # For now, return placeholder
    analysis_result = _run_placeholder_analysis(dimension)

    # Store analysis with cache metadata
    session_id = store_analysis_with_cache(
        call_id=str(call_id),
        rep_id=str(rep_id),
        dimension=dimension,
        transcript_hash=transcript_hash,
        rubric_version=rubric_version,
        analysis_result=analysis_result,
        session_type=session_type,
    )

    # Fetch and return stored session
    session = fetch_one(
        "SELECT * FROM coaching_sessions WHERE id = %s",
        (session_id,),
    )

    return session


def analyze_call(
    call_id: UUID,
    dimensions: list[CoachingDimension] | None = None,
    force_reanalysis: bool = False,
) -> dict[str, Any]:
    """
    Analyze a call across multiple dimensions.
    This is a higher-level function that analyzes all requested dimensions.

    Args:
        call_id: Call UUID
        dimensions: List of dimensions to analyze (default: all)
        force_reanalysis: Bypass cache

    Returns:
        Dict mapping dimension to analysis results
    """
    # Default to all dimensions
    if dimensions is None:
        dimensions = list(CoachingDimension)

    logger.info(
        f"Analyzing call {call_id} across {len(dimensions)} dimensions: "
        f"{[d.value for d in dimensions]}"
    )

    # Get call and transcript
    call = fetch_one("SELECT * FROM calls WHERE id = %s", (str(call_id),))
    if not call:
        raise ValueError(f"Call {call_id} not found")

    # Get transcript segments
    segments = fetch_one(
        """
        SELECT STRING_AGG(text, ' ' ORDER BY sequence_number) as full_transcript
        FROM transcripts
        WHERE call_id = %s
        """,
        (str(call_id),),
    )

    if not segments or not segments.get("full_transcript"):
        raise ValueError(f"No transcript found for call {call_id}")

    transcript = segments["full_transcript"]

    # Get primary rep (company_side = true speaker with most talk time)
    rep = fetch_one(
        """
        SELECT * FROM speakers
        WHERE call_id = %s
        AND company_side = true
        ORDER BY talk_time_seconds DESC NULLS LAST
        LIMIT 1
        """,
        (str(call_id),),
    )

    if not rep:
        raise ValueError(f"No company rep found for call {call_id}")

    rep_id = rep["id"]

    # Analyze each dimension
    # TODO: Phase 4 - Implement parallel execution with Prefect tasks
    results = {}
    for dimension in dimensions:
        session = get_or_create_coaching_session(
            call_id=call_id,
            rep_id=UUID(rep_id),
            dimension=dimension,
            transcript=transcript,
            force_reanalysis=force_reanalysis,
        )
        results[dimension.value] = session

    logger.info(f"Completed analysis for call {call_id}")

    return {
        "call_id": str(call_id),
        "call_title": call.get("title"),
        "rep_name": rep.get("name"),
        "dimensions_analyzed": [d.value for d in dimensions],
        "results": results,
    }


def _run_placeholder_analysis(dimension: CoachingDimension) -> dict[str, Any]:
    """
    Placeholder for actual Claude API analysis.
    TODO: Phase 3 - Replace with real analysis implementation.

    Args:
        dimension: Coaching dimension

    Returns:
        Placeholder analysis result
    """
    return {
        "score": 75,
        "strengths": [
            "Good engagement with prospect",
            "Clear explanation of key concepts",
        ],
        "areas_for_improvement": [
            "Could ask more discovery questions",
            "Missed opportunity to discuss competitive advantages",
        ],
        "specific_examples": {
            "good": [
                {
                    "quote": "Example good quote...",
                    "timestamp": 300,
                    "analysis": "This was effective because...",
                }
            ],
            "needs_work": [
                {
                    "quote": "Example improvement quote...",
                    "timestamp": 600,
                    "analysis": "Could be improved by...",
                }
            ],
        },
        "action_items": [
            "Practice discovery question framework",
            "Review competitive positioning guide",
        ],
        "full_analysis": f"Full analysis for {dimension.value} dimension...",
        "metadata": {
            "model": "claude-sonnet-4.5-placeholder",
            "tokens_used": 2500,
        },
    }
