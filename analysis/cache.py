"""
Intelligent caching for coaching analyses.
Critical for cost optimization (60-80% reduction).
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any

from coaching_mcp.shared import settings
from db import execute_query, fetch_one
from db.models import CoachingDimension

logger = logging.getLogger(__name__)


def generate_transcript_hash(transcript: str) -> str:
    """
    Generate SHA256 hash of transcript content.
    Used as cache key component.

    Args:
        transcript: Full transcript text

    Returns:
        Hex-encoded SHA256 hash
    """
    return hashlib.sha256(transcript.encode("utf-8")).hexdigest()


def generate_cache_key(
    call_id: str,
    dimension: CoachingDimension,
    transcript_hash: str,
    rubric_version: str,
) -> str:
    """
    Generate unique cache key for a coaching analysis.

    Cache key components:
    - dimension: What aspect we're analyzing
    - transcript_hash: Content fingerprint
    - rubric_version: Rubric version used for evaluation

    Args:
        call_id: Call UUID
        dimension: Coaching dimension
        transcript_hash: SHA256 of transcript
        rubric_version: Rubric version string

    Returns:
        Unique cache key
    """
    components = f"{dimension.value}:{transcript_hash}:{rubric_version}"
    cache_key = hashlib.sha256(components.encode("utf-8")).hexdigest()

    logger.debug(
        f"Generated cache key for call {call_id}, "
        f"dimension={dimension.value}, "
        f"rubric_version={rubric_version}"
    )

    return cache_key


def get_cached_analysis(
    call_id: str,
    dimension: CoachingDimension,
    transcript_hash: str,
    rubric_version: str,
) -> dict[str, Any] | None:
    """
    Check if cached analysis exists for this call + dimension + rubric version.

    Args:
        call_id: Call UUID
        dimension: Coaching dimension
        transcript_hash: SHA256 of transcript
        rubric_version: Rubric version

    Returns:
        Cached coaching session data or None if cache miss
    """
    cache_key = generate_cache_key(call_id, dimension, transcript_hash, rubric_version)

    # Check cache with TTL
    cache_cutoff = datetime.now() - timedelta(days=settings.cache_ttl_days)

    cached = fetch_one(
        """
        SELECT * FROM coaching_sessions
        WHERE cache_key = %s
        AND transcript_hash = %s
        AND rubric_version = %s
        AND coaching_dimension = %s
        AND created_at > %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (cache_key, transcript_hash, rubric_version, dimension.value, cache_cutoff),
        as_dict=True,
    )

    if cached and isinstance(cached, dict):
        logger.info(
            f"Cache HIT for call {call_id}, dimension={dimension.value}, "
            f"rubric_version={rubric_version}"
        )
        return cached

    logger.info(
        f"Cache MISS for call {call_id}, dimension={dimension.value}, "
        f"rubric_version={rubric_version}"
    )
    return None


def invalidate_cache_for_rubric(dimension: CoachingDimension, old_version: str) -> int:
    """
    Invalidate cache entries when a rubric is updated.
    This forces re-analysis with new rubric version.

    Args:
        dimension: Coaching dimension
        old_version: Old rubric version being deprecated

    Returns:
        Number of cache entries invalidated
    """
    logger.info(
        f"Invalidating cache for dimension={dimension.value}, " f"rubric_version={old_version}"
    )

    # We don't delete cache entries, just mark the rubric as deprecated
    # This allows us to see historical analyses
    # New analyses will use the new rubric version and create new cache entries

    result = fetch_one(
        """
        SELECT COUNT(*) as count FROM coaching_sessions
        WHERE coaching_dimension = %s
        AND rubric_version = %s
        """,
        (dimension.value, old_version),
        as_dict=True,
    )

    count = int(result["count"]) if result and isinstance(result, dict) else 0

    logger.info(f"Found {count} cached analyses that will be bypassed due to rubric update")

    return count


def get_cache_statistics(days: int = 30) -> dict[str, Any]:
    """
    Get cache hit rate statistics for cost analysis.

    Args:
        days: Number of days to analyze

    Returns:
        Dict with cache statistics
    """
    cutoff = datetime.now() - timedelta(days=days)

    stats = fetch_one(
        """
        SELECT
            COUNT(*) as total_analyses,
            COUNT(DISTINCT transcript_hash) as unique_transcripts,
            COUNT(DISTINCT cache_key) as unique_cache_keys,
            -- Estimate cache hits (sessions with same transcript_hash)
            COUNT(*) - COUNT(DISTINCT transcript_hash) as estimated_cache_hits
        FROM coaching_sessions
        WHERE created_at > %s
        """,
        (cutoff,),
        as_dict=True,
    )

    if not stats or not isinstance(stats, dict) or stats["total_analyses"] == 0:
        return {
            "days_analyzed": days,
            "total_analyses": 0,
            "cache_hit_rate": 0.0,
            "estimated_cost_savings": 0.0,
        }

    total = stats["total_analyses"]
    cache_hits = stats["estimated_cache_hits"]
    cache_hit_rate = (cache_hits / total) * 100 if total > 0 else 0

    # Estimate cost savings (assuming $0.003/K input tokens, 30K tokens per analysis)
    tokens_saved = cache_hits * 30000
    cost_savings = (tokens_saved / 1000) * 0.003

    return {
        "days_analyzed": days,
        "total_analyses": total,
        "unique_transcripts": stats["unique_transcripts"],
        "unique_cache_keys": stats["unique_cache_keys"],
        "estimated_cache_hits": cache_hits,
        "cache_hit_rate": round(cache_hit_rate, 2),
        "tokens_saved": tokens_saved,
        "estimated_cost_savings": round(cost_savings, 2),
    }


def get_active_rubric_version(dimension: CoachingDimension) -> str:
    """
    Get the active rubric version for a dimension.

    Args:
        dimension: Coaching dimension

    Returns:
        Active rubric version string

    Raises:
        ValueError: If no active rubric found
    """
    rubric = fetch_one(
        """
        SELECT version FROM coaching_rubrics
        WHERE category = %s
        AND active = true
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (dimension.value,),
        as_dict=True,
    )

    if not rubric or not isinstance(rubric, dict):
        raise ValueError(f"No active rubric found for dimension {dimension.value}")

    return str(rubric["version"])


def store_analysis_with_cache(
    call_id: str,
    rep_id: str,
    dimension: CoachingDimension,
    transcript_hash: str,
    rubric_version: str,
    analysis_result: dict[str, Any],
    session_type: str = "on_demand",
    analyst: str = "claude-sonnet-4.5",
) -> str:
    """
    Store analysis result with cache metadata.

    Args:
        call_id: Call UUID
        rep_id: Rep UUID
        dimension: Coaching dimension
        transcript_hash: SHA256 of transcript
        rubric_version: Rubric version used
        analysis_result: Analysis results from Claude
        session_type: Type of coaching session
        analyst: Model/analyst identifier

    Returns:
        Coaching session ID
    """
    cache_key = generate_cache_key(call_id, dimension, transcript_hash, rubric_version)

    import json

    # Serialize JSONB fields
    specific_examples = analysis_result.get("specific_examples")
    metadata = analysis_result.get("metadata")

    execute_query(
        """
        INSERT INTO coaching_sessions (
            call_id, rep_id, coaching_dimension, session_type, analyst,
            cache_key, transcript_hash, rubric_version,
            score, strengths, areas_for_improvement, specific_examples,
            action_items, full_analysis, metadata
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s::jsonb,
            %s, %s, %s::jsonb
        )
        """,
        (
            call_id,
            rep_id,
            dimension.value,
            session_type,
            analyst,
            cache_key,
            transcript_hash,
            rubric_version,
            analysis_result.get("score"),
            analysis_result.get("strengths"),
            analysis_result.get("areas_for_improvement"),
            json.dumps(specific_examples) if specific_examples else None,
            analysis_result.get("action_items"),
            analysis_result.get("full_analysis"),
            json.dumps(metadata) if metadata else None,
        ),
    )

    # Get inserted session ID
    session = fetch_one(
        """
        SELECT id FROM coaching_sessions
        WHERE cache_key = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (cache_key,),
        as_dict=True,
    )

    logger.info(
        f"Stored analysis with cache metadata: "
        f"call={call_id}, dimension={dimension.value}, "
        f"cache_key={cache_key[:16]}..."
    )

    return str(session["id"]) if session and isinstance(session, dict) else None
