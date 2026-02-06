"""
Search Calls Tool - Find calls matching specific criteria.
"""

import logging
from datetime import datetime
from typing import Any

from db import fetch_all

logger = logging.getLogger(__name__)


def search_calls_tool(
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
    Search for calls matching specified criteria with role-aware filtering.

    Args:
        rep_email: Filter by sales rep email
        product: Filter by product
        call_type: Filter by call type
        date_range: Date range filter
        min_score: Minimum overall score
        max_score: Maximum overall score
        has_objection_type: Filter for calls with specific objections
        topics: Filter by topics discussed
        role: Filter by speaker role (ae, se, csm) - searches metadata rubric_role field
        limit: Maximum results

    Returns:
        List of matching calls with metadata and scores, filtered by role if specified
    """
    logger.info(
        f"Searching calls with filters: rep={rep_email}, product={product}, type={call_type}, role={role}"
    )

    # Build dynamic query
    where_clauses = ["c.processed_at IS NOT NULL"]
    params = []

    # Filter by rep email
    if rep_email:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1 FROM speakers s
                WHERE s.call_id = c.id
                AND s.email = %s
                AND s.company_side = true
            )
        """
        )
        params.append(rep_email)

    # Filter by product
    if product:
        where_clauses.append("c.product = %s")
        params.append(product)

    # Filter by call type
    if call_type:
        where_clauses.append("c.call_type = %s")
        params.append(call_type)

    # Filter by date range
    if date_range:
        if "start" in date_range:
            where_clauses.append("c.scheduled_at >= %s")
            params.append(datetime.fromisoformat(date_range["start"]))
        if "end" in date_range:
            where_clauses.append("c.scheduled_at <= %s")
            params.append(datetime.fromisoformat(date_range["end"]))

    # Filter by score range (requires aggregating coaching sessions)
    score_filter = ""
    if min_score is not None or max_score is not None:
        score_conditions = []
        if min_score is not None:
            score_conditions.append("avg_score >= %s")
            params.append(min_score)
        if max_score is not None:
            score_conditions.append("avg_score <= %s")
            params.append(max_score)
        score_filter = "AND " + " AND ".join(score_conditions)

    # Filter by objection type (search in coaching session analysis)
    if has_objection_type:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1 FROM coaching_sessions cs
                WHERE cs.call_id = c.id
                AND cs.coaching_dimension = 'objection_handling'
                AND cs.full_analysis ILIKE %s
            )
        """
        )
        params.append(f"%{has_objection_type}%")

    # Filter by topics (search in transcript topics array)
    if topics:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1 FROM transcripts t
                WHERE t.call_id = c.id
                AND t.topics && %s::text[]
            )
        """
        )
        params.append(topics)

    # Filter by role (search in coaching_sessions metadata)
    if role:
        where_clauses.append(
            """
            EXISTS (
                SELECT 1 FROM coaching_sessions cs
                WHERE cs.call_id = c.id
                AND cs.metadata->>'rubric_role' = %s
            )
        """
        )
        params.append(role)

    # Limit
    params.append(min(limit, 100))  # Cap at 100

    # Build final query
    query = f"""
        WITH call_scores AS (
            SELECT
                cs.call_id,
                AVG(cs.score) as avg_score
            FROM coaching_sessions cs
            WHERE cs.score IS NOT NULL
            GROUP BY cs.call_id
        )
        SELECT
            c.id,
            c.gong_call_id,
            c.title,
            c.scheduled_at,
            c.duration_seconds,
            c.call_type,
            c.product,
            COALESCE(csc.avg_score, 0) as overall_score,
            ARRAY_AGG(DISTINCT s.name) FILTER (WHERE s.company_side = false) as customer_names,
            ARRAY_AGG(DISTINCT s.name) FILTER (WHERE s.company_side = true) as prefect_reps
        FROM calls c
        LEFT JOIN call_scores csc ON c.id = csc.call_id
        LEFT JOIN speakers s ON c.id = s.call_id
        WHERE {' AND '.join(where_clauses)}
            {score_filter}
        GROUP BY c.id, c.gong_call_id, c.title, c.scheduled_at,
                 c.duration_seconds, c.call_type, c.product, csc.avg_score
        ORDER BY c.scheduled_at DESC
        LIMIT %s
    """

    logger.debug(f"Search query: {query}")
    logger.debug(f"Parameters: {params}")

    # Execute search
    results = fetch_all(query, tuple(params))

    # Format results
    formatted_results = []
    for row in results:
        formatted_results.append(
            {
                "call_id": row["gong_call_id"],
                "title": row["title"],
                "date": str(row["scheduled_at"]) if row["scheduled_at"] else None,
                "duration_seconds": row["duration_seconds"],
                "call_type": row["call_type"],
                "product": row["product"],
                "overall_score": (
                    round(float(row["overall_score"]), 1) if row["overall_score"] else None
                ),
                "customer_names": row["customer_names"] or [],
                "prefect_reps": row["prefect_reps"] or [],
            }
        )

    logger.info(f"Found {len(formatted_results)} matching calls")
    return formatted_results
