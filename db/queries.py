"""
Helper functions for common database queries.
Provides high-level abstractions over raw SQL.
"""
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from .connection import fetch_one, fetch_all, execute_query
from .models import (
    Call,
    Speaker,
    CoachingSession,
    RepPerformanceSummary,
    CallAnalysisStatus,
    CoachingDimension,
)

logger = logging.getLogger(__name__)


# ============================================================================
# CALL QUERIES
# ============================================================================

def get_call_by_id(call_id: UUID) -> dict[str, Any] | None:
    """Get call by database UUID."""
    return fetch_one("SELECT * FROM calls WHERE id = %s", (str(call_id),))


def get_call_by_gong_id(gong_call_id: str) -> dict[str, Any] | None:
    """Get call by Gong call ID."""
    return fetch_one("SELECT * FROM calls WHERE gong_call_id = %s", (gong_call_id,))


def get_recent_calls(limit: int = 50) -> list[dict[str, Any]]:
    """Get most recent calls."""
    return fetch_all(
        "SELECT * FROM calls ORDER BY scheduled_at DESC NULLS LAST LIMIT %s",
        (limit,),
    )


def get_calls_by_date_range(
    start_date: datetime,
    end_date: datetime,
    product: str | None = None,
) -> list[dict[str, Any]]:
    """Get calls within date range, optionally filtered by product."""
    if product:
        return fetch_all(
            """
            SELECT * FROM calls
            WHERE scheduled_at BETWEEN %s AND %s
            AND product = %s
            ORDER BY scheduled_at DESC
            """,
            (start_date, end_date, product),
        )
    else:
        return fetch_all(
            """
            SELECT * FROM calls
            WHERE scheduled_at BETWEEN %s AND %s
            ORDER BY scheduled_at DESC
            """,
            (start_date, end_date),
        )


# ============================================================================
# SPEAKER QUERIES
# ============================================================================

def get_speakers_for_call(call_id: UUID) -> list[dict[str, Any]]:
    """Get all speakers for a call."""
    return fetch_all(
        "SELECT * FROM speakers WHERE call_id = %s ORDER BY talk_time_seconds DESC NULLS LAST",
        (str(call_id),),
    )


def get_rep_by_email(email: str) -> dict[str, Any] | None:
    """Get rep by email address."""
    return fetch_one(
        """
        SELECT DISTINCT ON (email) *
        FROM speakers
        WHERE email = %s
        AND company_side = true
        ORDER BY email, created_at DESC
        """,
        (email,),
    )


def get_reps_list() -> list[dict[str, Any]]:
    """Get list of all company reps (distinct by email)."""
    return fetch_all(
        """
        SELECT DISTINCT ON (email)
            id, name, email, role
        FROM speakers
        WHERE company_side = true
        AND email IS NOT NULL
        ORDER BY email, created_at DESC
        """
    )


# ============================================================================
# TRANSCRIPT QUERIES
# ============================================================================

def get_full_transcript(call_id: UUID) -> str:
    """Get full transcript for a call as single string."""
    result = fetch_one(
        """
        SELECT STRING_AGG(text, ' ' ORDER BY sequence_number) as full_transcript
        FROM transcripts
        WHERE call_id = %s
        """,
        (str(call_id),),
    )
    return result["full_transcript"] if result else ""


def get_transcript_segments(call_id: UUID) -> list[dict[str, Any]]:
    """Get transcript segments with speaker info."""
    return fetch_all(
        """
        SELECT
            t.*,
            s.name as speaker_name,
            s.email as speaker_email,
            s.role as speaker_role
        FROM transcripts t
        LEFT JOIN speakers s ON t.speaker_id = s.id
        WHERE t.call_id = %s
        ORDER BY t.sequence_number
        """,
        (str(call_id),),
    )


def search_transcripts(
    query: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Full-text search across transcripts."""
    return fetch_all(
        """
        SELECT
            t.call_id,
            t.text,
            t.timestamp_seconds,
            c.title as call_title,
            c.scheduled_at,
            s.name as speaker_name
        FROM transcripts t
        JOIN calls c ON t.call_id = c.id
        LEFT JOIN speakers s ON t.speaker_id = s.id
        WHERE t.full_text_search @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank(t.full_text_search, plainto_tsquery('english', %s)) DESC
        LIMIT %s
        """,
        (query, query, limit),
    )


# ============================================================================
# COACHING SESSION QUERIES
# ============================================================================

def get_coaching_sessions_for_call(
    call_id: UUID,
    dimension: CoachingDimension | None = None,
) -> list[dict[str, Any]]:
    """Get coaching sessions for a call, optionally filtered by dimension."""
    if dimension:
        return fetch_all(
            """
            SELECT * FROM coaching_sessions
            WHERE call_id = %s
            AND coaching_dimension = %s
            ORDER BY created_at DESC
            """,
            (str(call_id), dimension.value),
        )
    else:
        return fetch_all(
            """
            SELECT * FROM coaching_sessions
            WHERE call_id = %s
            ORDER BY coaching_dimension, created_at DESC
            """,
            (str(call_id),),
        )


def get_coaching_sessions_for_rep(
    rep_email: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    dimension: CoachingDimension | None = None,
) -> list[dict[str, Any]]:
    """Get coaching sessions for a rep with optional filters."""
    # Build query based on filters
    where_clauses = ["s.email = %s", "s.company_side = true"]
    params: list[Any] = [rep_email]

    if start_date:
        where_clauses.append("cs.created_at >= %s")
        params.append(start_date)

    if end_date:
        where_clauses.append("cs.created_at <= %s")
        params.append(end_date)

    if dimension:
        where_clauses.append("cs.coaching_dimension = %s")
        params.append(dimension.value)

    query = f"""
        SELECT
            cs.*,
            c.title as call_title,
            c.scheduled_at as call_date
        FROM coaching_sessions cs
        JOIN speakers s ON cs.rep_id = s.id
        JOIN calls c ON cs.call_id = c.id
        WHERE {' AND '.join(where_clauses)}
        ORDER BY cs.created_at DESC
    """

    return fetch_all(query, tuple(params))


def get_rep_performance_summary(rep_email: str) -> dict[str, Any] | None:
    """Get performance summary for a rep."""
    return fetch_one(
        """
        SELECT * FROM rep_performance_summary
        WHERE rep_email = %s
        """,
        (rep_email,),
    )


def get_call_analysis_status(call_id: UUID) -> dict[str, Any] | None:
    """Get analysis status for a call."""
    return fetch_one(
        """
        SELECT * FROM call_analysis_status
        WHERE call_id = %s
        """,
        (str(call_id),),
    )


# ============================================================================
# ANALYTICS QUERIES
# ============================================================================

def get_score_trends_for_rep(
    rep_email: str,
    dimension: CoachingDimension,
    days: int = 90,
) -> list[dict[str, Any]]:
    """Get score trends over time for a rep and dimension."""
    return fetch_all(
        """
        SELECT
            DATE(cs.created_at) as date,
            AVG(cs.score) as avg_score,
            COUNT(*) as session_count
        FROM coaching_sessions cs
        JOIN speakers s ON cs.rep_id = s.id
        WHERE s.email = %s
        AND cs.coaching_dimension = %s
        AND cs.created_at >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(cs.created_at)
        ORDER BY date ASC
        """,
        (rep_email, dimension.value, days),
    )


def get_team_average_scores(
    dimension: CoachingDimension,
    days: int = 30,
) -> dict[str, Any] | None:
    """Get team average score for a dimension."""
    return fetch_one(
        """
        SELECT
            AVG(score) as avg_score,
            MIN(score) as min_score,
            MAX(score) as max_score,
            COUNT(*) as session_count
        FROM coaching_sessions
        WHERE coaching_dimension = %s
        AND created_at >= NOW() - INTERVAL '%s days'
        """,
        (dimension.value, days),
    )


def get_top_performers(
    dimension: CoachingDimension,
    days: int = 30,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Get top performing reps for a dimension."""
    return fetch_all(
        """
        SELECT
            s.name,
            s.email,
            s.role,
            AVG(cs.score) as avg_score,
            COUNT(DISTINCT cs.call_id) as call_count
        FROM coaching_sessions cs
        JOIN speakers s ON cs.rep_id = s.id
        WHERE cs.coaching_dimension = %s
        AND cs.created_at >= NOW() - INTERVAL '%s days'
        AND s.company_side = true
        GROUP BY s.id, s.name, s.email, s.role
        HAVING COUNT(DISTINCT cs.call_id) >= 3  -- Min 3 calls
        ORDER BY avg_score DESC
        LIMIT %s
        """,
        (dimension.value, days, limit),
    )
