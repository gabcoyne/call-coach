"""
A/B Testing Infrastructure for Five Wins Pipeline

Provides controlled rollout of the Five Wins Unified pipeline:
1. Route percentage of calls to new pipeline
2. Log which pipeline was used
3. Collect comparison metrics

Usage:
    from analysis.ab_testing import should_use_unified_pipeline, log_pipeline_usage

    if should_use_unified_pipeline(call_id):
        result = run_five_wins_unified_analysis(...)
        log_pipeline_usage(call_id, "unified", result)
    else:
        result = run_legacy_analysis(...)
        log_pipeline_usage(call_id, "legacy", result)
"""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# A/B test configuration
FIVE_WINS_UNIFIED_ROLLOUT_PERCENTAGE = int(os.getenv("FIVE_WINS_UNIFIED_ROLLOUT_PCT", "0"))

# Feature flags
FIVE_WINS_UNIFIED_ENABLED = os.getenv("FIVE_WINS_UNIFIED_ENABLED", "false").lower() == "true"
FIVE_WINS_AB_TESTING_ENABLED = os.getenv("FIVE_WINS_AB_TESTING_ENABLED", "false").lower() == "true"


def should_use_unified_pipeline(
    call_id: str,
    override: bool | None = None,
) -> bool:
    """
    Determine whether to use the Five Wins Unified pipeline for a call.

    Decision logic (in priority order):
    1. If override is specified, use that
    2. If FIVE_WINS_UNIFIED_ENABLED=true, always use unified
    3. If FIVE_WINS_AB_TESTING_ENABLED=true, hash call_id for deterministic routing
    4. Otherwise, use legacy pipeline

    Args:
        call_id: Call identifier for consistent hashing
        override: Optional override to force unified (True) or legacy (False)

    Returns:
        True if unified pipeline should be used
    """
    # Priority 1: Explicit override
    if override is not None:
        logger.debug(f"Pipeline override for {call_id}: {'unified' if override else 'legacy'}")
        return override

    # Priority 2: Global enable flag
    if FIVE_WINS_UNIFIED_ENABLED:
        logger.debug(f"Unified pipeline enabled globally for {call_id}")
        return True

    # Priority 3: A/B testing with percentage rollout
    if FIVE_WINS_AB_TESTING_ENABLED and FIVE_WINS_UNIFIED_ROLLOUT_PERCENTAGE > 0:
        # Use consistent hashing so same call always gets same pipeline
        hash_value = _hash_call_id(call_id)
        use_unified = hash_value < FIVE_WINS_UNIFIED_ROLLOUT_PERCENTAGE

        logger.debug(
            f"A/B test for {call_id}: hash={hash_value}, "
            f"threshold={FIVE_WINS_UNIFIED_ROLLOUT_PERCENTAGE}, "
            f"result={'unified' if use_unified else 'legacy'}"
        )
        return use_unified

    # Default: legacy pipeline
    logger.debug(f"Using legacy pipeline for {call_id} (default)")
    return False


def _hash_call_id(call_id: str) -> int:
    """
    Hash call_id to a value 0-99 for percentage-based routing.

    Uses SHA-256 for uniform distribution.
    """
    hash_bytes = hashlib.sha256(call_id.encode()).digest()
    # Use first 4 bytes as integer, mod 100 for percentage
    hash_int = int.from_bytes(hash_bytes[:4], "big")
    return hash_int % 100


def log_pipeline_usage(
    call_id: str,
    pipeline: str,
    result: dict[str, Any],
    duration_ms: float | None = None,
) -> None:
    """
    Log which pipeline was used for a call and key metrics.

    This creates an audit trail for A/B test analysis.

    Args:
        call_id: Call identifier
        pipeline: "unified" or "legacy"
        result: Analysis result (for extracting metrics)
        duration_ms: Optional execution time in milliseconds
    """
    # Extract key metrics for comparison
    metrics = _extract_comparison_metrics(result, pipeline)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "call_id": call_id,
        "pipeline": pipeline,
        "duration_ms": duration_ms,
        "metrics": metrics,
    }

    # Log at INFO level for easy filtering
    logger.info(
        f"PIPELINE_USAGE: call_id={call_id} pipeline={pipeline} "
        f"overall_score={metrics.get('overall_score')} "
        f"wins_secured={metrics.get('wins_secured')} "
        f"has_narrative={metrics.get('has_narrative')} "
        f"has_primary_action={metrics.get('has_primary_action')} "
        f"duration_ms={duration_ms}"
    )

    # Also store in database for analysis
    _store_ab_test_result(log_entry)


def _extract_comparison_metrics(result: dict[str, Any], pipeline: str) -> dict[str, Any]:
    """
    Extract key metrics for A/B comparison.
    """
    metrics = {
        "pipeline": pipeline,
        "overall_score": None,
        "wins_secured": None,
        "has_narrative": False,
        "has_primary_action": False,
        "action_item_count": 0,
        "tokens_used": None,
    }

    # Five Wins scores
    five_wins = result.get("five_wins_evaluation", {})
    metrics["overall_score"] = five_wins.get("overall_score")
    metrics["wins_secured"] = five_wins.get("wins_secured")

    # Unified pipeline specific
    metrics["has_narrative"] = bool(result.get("narrative"))
    metrics["has_primary_action"] = bool(result.get("primary_action"))

    # Action items
    action_items = result.get("action_items_filtered") or result.get("action_items", [])
    metrics["action_item_count"] = len(action_items) if action_items else 0

    # Token usage from metadata
    for dim_result in result.get("dimension_details", {}).values():
        if isinstance(dim_result, dict) and "metadata" in dim_result:
            metadata = dim_result["metadata"]
            if "tokens_used" in metadata:
                metrics["tokens_used"] = (metrics["tokens_used"] or 0) + metadata["tokens_used"]

    return metrics


def _store_ab_test_result(log_entry: dict[str, Any]) -> None:
    """
    Store A/B test result in database for analysis.

    Creates ab_test_results table if needed.
    """
    try:
        from db import execute_query

        # Ensure table exists (idempotent)
        execute_query(
            """
            CREATE TABLE IF NOT EXISTS ab_test_results (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                call_id TEXT NOT NULL,
                pipeline TEXT NOT NULL,
                duration_ms FLOAT,
                overall_score INT,
                wins_secured INT,
                has_narrative BOOLEAN,
                has_primary_action BOOLEAN,
                action_item_count INT,
                tokens_used INT,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            commit=True,
        )

        # Insert result
        metrics = log_entry.get("metrics", {})
        execute_query(
            """
            INSERT INTO ab_test_results (
                timestamp, call_id, pipeline, duration_ms,
                overall_score, wins_secured, has_narrative,
                has_primary_action, action_item_count, tokens_used
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                log_entry["timestamp"],
                log_entry["call_id"],
                log_entry["pipeline"],
                log_entry.get("duration_ms"),
                metrics.get("overall_score"),
                metrics.get("wins_secured"),
                metrics.get("has_narrative"),
                metrics.get("has_primary_action"),
                metrics.get("action_item_count"),
                metrics.get("tokens_used"),
            ),
            commit=True,
        )

    except Exception as e:
        # Don't fail the main operation if logging fails
        logger.warning(f"Failed to store A/B test result: {e}")


def get_ab_test_summary(days: int = 7) -> dict[str, Any]:
    """
    Get summary statistics from A/B test results.

    Args:
        days: Number of days to look back

    Returns:
        Summary with counts, scores, and comparisons
    """
    try:
        from db import fetch_all

        results = fetch_all(
            """
            SELECT
                pipeline,
                COUNT(*) as call_count,
                AVG(overall_score) as avg_score,
                AVG(wins_secured) as avg_wins_secured,
                AVG(action_item_count) as avg_action_items,
                AVG(tokens_used) as avg_tokens,
                AVG(duration_ms) as avg_duration_ms,
                SUM(CASE WHEN has_narrative THEN 1 ELSE 0 END)::float / COUNT(*) as narrative_rate,
                SUM(CASE WHEN has_primary_action THEN 1 ELSE 0 END)::float / COUNT(*) as primary_action_rate
            FROM ab_test_results
            WHERE timestamp > NOW() - INTERVAL '%s days'
            GROUP BY pipeline
            """,
            (days,),
            as_dict=True,
        )

        summary: dict[str, Any] = {"days": days, "pipelines": {}}

        if isinstance(results, list):
            for row in results:
                if isinstance(row, dict) and row.get("pipeline"):
                    summary["pipelines"][row["pipeline"]] = {
                        "call_count": row.get("call_count", 0),
                        "avg_score": round(row["avg_score"], 1) if row.get("avg_score") else None,
                        "avg_wins_secured": (
                            round(row["avg_wins_secured"], 2)
                            if row.get("avg_wins_secured")
                            else None
                        ),
                        "avg_action_items": (
                            round(row["avg_action_items"], 1)
                            if row.get("avg_action_items")
                            else None
                        ),
                        "avg_tokens": round(row["avg_tokens"]) if row.get("avg_tokens") else None,
                        "avg_duration_ms": (
                            round(row["avg_duration_ms"], 1) if row.get("avg_duration_ms") else None
                        ),
                        "narrative_rate": (
                            round(row["narrative_rate"] * 100, 1)
                            if row.get("narrative_rate")
                            else 0
                        ),
                        "primary_action_rate": (
                            round(row["primary_action_rate"] * 100, 1)
                            if row.get("primary_action_rate")
                            else 0
                        ),
                    }

        return summary

    except Exception as e:
        logger.error(f"Failed to get A/B test summary: {e}")
        return {"error": str(e), "days": days, "pipelines": {}}
