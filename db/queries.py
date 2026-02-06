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


# ============================================================================
# OPPORTUNITY QUERIES
# ============================================================================

def upsert_opportunity(opp_data: dict[str, Any]) -> str:
    """
    Upsert opportunity from Gong API data.

    Args:
        opp_data: Opportunity dict from Gong API

    Returns:
        Opportunity UUID (str)
    """
    execute_query(
        """
        INSERT INTO opportunities (
            gong_opportunity_id, name, account_name, owner_email,
            stage, close_date, amount, health_score, metadata, updated_at
        ) VALUES (
            %(gong_opportunity_id)s, %(name)s, %(account_name)s, %(owner_email)s,
            %(stage)s, %(close_date)s, %(amount)s, %(health_score)s, %(metadata)s, NOW()
        )
        ON CONFLICT (gong_opportunity_id) DO UPDATE SET
            name = EXCLUDED.name,
            account_name = EXCLUDED.account_name,
            owner_email = EXCLUDED.owner_email,
            stage = EXCLUDED.stage,
            close_date = EXCLUDED.close_date,
            amount = EXCLUDED.amount,
            health_score = EXCLUDED.health_score,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        """,
        opp_data,
    )

    result = fetch_one(
        "SELECT id FROM opportunities WHERE gong_opportunity_id = %s",
        (opp_data["gong_opportunity_id"],),
    )
    return result["id"] if result else None


def upsert_email(email_data: dict[str, Any]) -> str:
    """
    Upsert email from Gong API data.

    Args:
        email_data: Email dict from Gong API with opportunity_id already set

    Returns:
        Email UUID (str)
    """
    execute_query(
        """
        INSERT INTO emails (
            gong_email_id, opportunity_id, subject, sender_email,
            recipients, sent_at, body_snippet, metadata
        ) VALUES (
            %(gong_email_id)s, %(opportunity_id)s, %(subject)s, %(sender_email)s,
            %(recipients)s, %(sent_at)s, %(body_snippet)s, %(metadata)s
        )
        ON CONFLICT (gong_email_id) DO UPDATE SET
            opportunity_id = EXCLUDED.opportunity_id,
            subject = EXCLUDED.subject,
            sender_email = EXCLUDED.sender_email,
            recipients = EXCLUDED.recipients,
            sent_at = EXCLUDED.sent_at,
            body_snippet = EXCLUDED.body_snippet,
            metadata = EXCLUDED.metadata
        """,
        email_data,
    )

    result = fetch_one(
        "SELECT id FROM emails WHERE gong_email_id = %s",
        (email_data["gong_email_id"],),
    )
    return result["id"] if result else None


def link_call_to_opportunity(call_id: str, opp_id: str) -> None:
    """
    Create junction record linking call to opportunity.

    Args:
        call_id: Call UUID
        opp_id: Opportunity UUID
    """
    execute_query(
        """
        INSERT INTO call_opportunities (call_id, opportunity_id)
        VALUES (%s, %s)
        ON CONFLICT (call_id, opportunity_id) DO NOTHING
        """,
        (call_id, opp_id),
    )


def get_opportunity(opp_id: str) -> dict[str, Any] | None:
    """
    Get opportunity with aggregated call/email counts.

    Args:
        opp_id: Opportunity UUID

    Returns:
        Opportunity dict with call_count and email_count
    """
    return fetch_one(
        """
        SELECT
            o.*,
            COUNT(DISTINCT co.call_id) as call_count,
            COUNT(DISTINCT e.id) as email_count
        FROM opportunities o
        LEFT JOIN call_opportunities co ON o.id = co.opportunity_id
        LEFT JOIN emails e ON o.id = e.opportunity_id
        WHERE o.id = %s
        GROUP BY o.id
        """,
        (opp_id,),
    )


def get_opportunity_timeline(
    opp_id: str,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """
    Get chronological timeline of calls and emails for an opportunity.

    Args:
        opp_id: Opportunity UUID
        limit: Max items to return
        offset: Number of items to skip

    Returns:
        List of timeline items with type field ('call' or 'email')
    """
    return fetch_all(
        """
        -- Calls timeline
        SELECT
            'call' as item_type,
            c.id,
            c.gong_call_id,
            c.title,
            c.scheduled_at as timestamp,
            c.duration,
            NULL as subject,
            NULL as sender_email
        FROM calls c
        JOIN call_opportunities co ON c.id = co.call_id
        WHERE co.opportunity_id = %s

        UNION ALL

        -- Emails timeline
        SELECT
            'email' as item_type,
            e.id,
            e.gong_email_id,
            NULL as title,
            e.sent_at as timestamp,
            NULL as duration,
            e.subject,
            e.sender_email
        FROM emails e
        WHERE e.opportunity_id = %s

        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s
        """,
        (opp_id, opp_id, limit, offset),
    )


def search_opportunities(
    filters: dict[str, Any] | None = None,
    sort: str = "updated_at",
    sort_dir: str = "DESC",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """
    Search opportunities with filters, sorting, and pagination.

    Args:
        filters: Dict with optional keys: owner, stage, health_score_min, health_score_max, search
        sort: Field to sort by (updated_at, close_date, health_score, amount)
        sort_dir: Sort direction (ASC or DESC)
        limit: Max results to return
        offset: Number of results to skip

    Returns:
        Tuple of (opportunities list, total count)
    """
    filters = filters or {}

    # Build WHERE clauses
    where_clauses = []
    params = {}

    if "owner" in filters:
        where_clauses.append("o.owner_email = %(owner)s")
        params["owner"] = filters["owner"]

    if "stage" in filters:
        if isinstance(filters["stage"], list):
            where_clauses.append("o.stage = ANY(%(stage)s)")
            params["stage"] = filters["stage"]
        else:
            where_clauses.append("o.stage = %(stage)s")
            params["stage"] = filters["stage"]

    if "health_score_min" in filters:
        where_clauses.append("o.health_score >= %(health_score_min)s")
        params["health_score_min"] = filters["health_score_min"]

    if "health_score_max" in filters:
        where_clauses.append("o.health_score <= %(health_score_max)s")
        params["health_score_max"] = filters["health_score_max"]

    if "search" in filters:
        where_clauses.append("(o.name ILIKE %(search)s OR o.account_name ILIKE %(search)s)")
        params["search"] = f"%{filters['search']}%"

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Validate sort field
    valid_sorts = {"updated_at", "close_date", "health_score", "amount"}
    if sort not in valid_sorts:
        sort = "updated_at"

    # Validate sort direction
    sort_dir = "DESC" if sort_dir.upper() == "DESC" else "ASC"

    params["limit"] = limit
    params["offset"] = offset

    # Get total count
    count_result = fetch_one(
        f"""
        SELECT COUNT(*) as total
        FROM opportunities o
        {where_sql}
        """,
        params,
    )
    total = count_result["total"] if count_result else 0

    # Get paginated results with counts
    opportunities = fetch_all(
        f"""
        SELECT
            o.*,
            COUNT(DISTINCT co.call_id) as call_count,
            COUNT(DISTINCT e.id) as email_count
        FROM opportunities o
        LEFT JOIN call_opportunities co ON o.id = co.opportunity_id
        LEFT JOIN emails e ON o.id = e.opportunity_id
        {where_sql}
        GROUP BY o.id
        ORDER BY o.{sort} {sort_dir} NULLS LAST
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        params,
    )

    return opportunities, total


def get_sync_status(entity_type: str) -> dict[str, Any] | None:
    """
    Get last sync timestamp for entity type.

    Args:
        entity_type: Type of entity (opportunities, calls, emails)

    Returns:
        Sync status dict or None
    """
    return fetch_one(
        "SELECT * FROM sync_status WHERE entity_type = %s",
        (entity_type,),
    )


def update_sync_status(
    entity_type: str,
    status: str = "success",
    items_synced: int = 0,
    errors_count: int = 0,
    error_details: dict[str, Any] | None = None,
) -> None:
    """
    Update sync status after successful sync.

    Args:
        entity_type: Type of entity (opportunities, calls, emails)
        status: Sync status (success, partial, failed)
        items_synced: Number of items successfully synced
        errors_count: Number of errors encountered
        error_details: JSONB dict with error details
    """
    execute_query(
        """
        INSERT INTO sync_status (
            entity_type, last_sync_timestamp, last_sync_status,
            items_synced, errors_count, error_details, updated_at
        ) VALUES (
            %s, NOW(), %s, %s, %s, %s, NOW()
        )
        ON CONFLICT (entity_type) DO UPDATE SET
            last_sync_timestamp = NOW(),
            last_sync_status = EXCLUDED.last_sync_status,
            items_synced = EXCLUDED.items_synced,
            errors_count = EXCLUDED.errors_count,
            error_details = EXCLUDED.error_details,
            updated_at = NOW()
        """,
        (entity_type, status, items_synced, errors_count, error_details),
    )


# ============================================================================
# STAFF ROLE QUERIES
# ============================================================================

def get_staff_role(email: str) -> str | None:
    """
    Get role assignment for staff member by email.

    Args:
        email: Staff member email address

    Returns:
        Role identifier ('ae', 'se', 'csm') or None if not assigned
    """
    result = fetch_one(
        "SELECT role FROM staff_roles WHERE email = %s",
        (email,),
    )
    return result["role"] if result else None


def upsert_staff_role(email: str, role: str, assigned_by: str) -> None:
    """
    Create or update role assignment for staff member.

    Args:
        email: Staff member email address
        role: Role identifier ('ae', 'se', 'csm')
        assigned_by: Email of manager assigning the role
    """
    execute_query(
        """
        INSERT INTO staff_roles (email, role, assigned_by, assigned_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        ON CONFLICT (email) DO UPDATE SET
            role = EXCLUDED.role,
            assigned_by = EXCLUDED.assigned_by,
            updated_at = NOW()
        """,
        (email, role, assigned_by),
    )
    logger.info(f"Updated role for {email}: {role} (assigned by {assigned_by})")


def delete_staff_role(email: str) -> None:
    """
    Remove role assignment for staff member.

    Args:
        email: Staff member email address
    """
    execute_query(
        "DELETE FROM staff_roles WHERE email = %s",
        (email,),
    )
    logger.info(f"Deleted role assignment for {email}")


def list_all_staff_roles() -> list[dict[str, Any]]:
    """
    Get all staff role assignments with metadata.

    Returns:
        List of role assignments with email, role, assigned_by, assigned_at, updated_at
    """
    return fetch_all(
        """
        SELECT email, role, assigned_by, assigned_at, updated_at
        FROM staff_roles
        ORDER BY updated_at DESC
        """
    )


def get_prefect_staff() -> list[dict[str, Any]]:
    """
    Get all unique Prefect staff from speakers table.

    Identifies staff by @prefect.io email domain.

    Returns:
        List of dicts with email, name (from most recent call)
    """
    return fetch_all(
        """
        SELECT DISTINCT ON (email)
            email,
            name
        FROM speakers
        WHERE email LIKE '%@prefect.io'
        AND company_side = true
        ORDER BY email
        """
    )


# ============================================================================
# COACHING FEEDBACK QUERIES
# ============================================================================

def get_feedback_for_session(coaching_session_id: str) -> list[dict[str, Any]]:
    """Get all feedback for a coaching session."""
    return fetch_all(
        """
        SELECT * FROM coaching_feedback
        WHERE coaching_session_id = %s
        ORDER BY created_at DESC
        """,
        (coaching_session_id,),
    )


def submit_feedback(
    coaching_session_id: str,
    rep_id: str,
    feedback_type: str,
    feedback_text: str | None = None,
) -> str | None:
    """
    Submit feedback on a coaching session.

    Args:
        coaching_session_id: UUID of the coaching session
        rep_id: UUID of the rep being coached
        feedback_type: Type of feedback (accurate, inaccurate, missing_context, helpful, not_helpful)
        feedback_text: Optional feedback text

    Returns:
        Feedback record ID (str) or None if failed
    """
    result = fetch_one(
        """
        INSERT INTO coaching_feedback (
            coaching_session_id, rep_id, feedback_type, feedback_text, created_at
        )
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id
        """,
        (coaching_session_id, rep_id, feedback_type, feedback_text),
    )
    return result["id"] if result else None


def get_feedback_stats(
    dimension: str | None = None,
    days: int = 30,
) -> dict[str, Any] | None:
    """
    Get aggregated feedback statistics for coaching quality.

    Args:
        dimension: Optional coaching dimension to filter by
        days: Number of days to look back

    Returns:
        Stats dict with accuracy rate, helpfulness rate, etc.
    """
    where_clause = "cf.created_at >= NOW() - INTERVAL '%s days'" % days

    if dimension:
        where_clause += " AND cs.coaching_dimension = '%s'" % dimension

    return fetch_one(
        f"""
        SELECT
            COUNT(*) as total_feedback,
            SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) as accurate_count,
            SUM(CASE WHEN cf.feedback_type = 'inaccurate' THEN 1 ELSE 0 END) as inaccurate_count,
            SUM(CASE WHEN cf.feedback_type = 'missing_context' THEN 1 ELSE 0 END) as missing_context_count,
            SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) as helpful_count,
            SUM(CASE WHEN cf.feedback_type = 'not_helpful' THEN 1 ELSE 0 END) as not_helpful_count,
            ROUND(
                100.0 * SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0),
                2
            ) as accuracy_rate,
            ROUND(
                100.0 * SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0),
                2
            ) as helpfulness_rate
        FROM coaching_feedback cf
        JOIN coaching_sessions cs ON cf.coaching_session_id = cs.id
        WHERE {where_clause}
        """
    )


def get_feedback_stats_by_dimension(
    days: int = 30,
) -> list[dict[str, Any]]:
    """
    Get feedback statistics grouped by coaching dimension.

    Args:
        days: Number of days to look back

    Returns:
        List of stats dicts per dimension
    """
    return fetch_all(
        """
        SELECT
            cs.coaching_dimension as dimension,
            COUNT(*) as total_feedback,
            SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) as accurate_count,
            SUM(CASE WHEN cf.feedback_type = 'inaccurate' THEN 1 ELSE 0 END) as inaccurate_count,
            SUM(CASE WHEN cf.feedback_type = 'missing_context' THEN 1 ELSE 0 END) as missing_context_count,
            SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) as helpful_count,
            SUM(CASE WHEN cf.feedback_type = 'not_helpful' THEN 1 ELSE 0 END) as not_helpful_count,
            ROUND(
                100.0 * SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0),
                2
            ) as accuracy_rate,
            ROUND(
                100.0 * SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0),
                2
            ) as helpfulness_rate
        FROM coaching_feedback cf
        JOIN coaching_sessions cs ON cf.coaching_session_id = cs.id
        WHERE cf.created_at >= NOW() - INTERVAL '%s days'
        GROUP BY cs.coaching_dimension
        ORDER BY total_feedback DESC
        """,
        (days,),
    )


def get_coaching_quality_issues(
    days: int = 30,
) -> list[dict[str, Any]]:
    """
    Identify coaching quality issues from feedback data.

    Args:
        days: Number of days to analyze

    Returns:
        List of quality issues sorted by severity
    """
    stats = get_feedback_stats(days=days)

    if not stats or stats["total_feedback"] == 0:
        return []

    issues = []

    # Issue 1: Low accuracy
    if (stats["accuracy_rate"] or 0) < 80:
        issues.append({
            "type": "low_accuracy",
            "severity": "high",
            "message": f"Coaching accuracy is {stats['accuracy_rate']}% (target: 90%+)",
            "metric_value": stats["accuracy_rate"],
            "affected_count": stats["inaccurate_count"],
        })

    # Issue 2: Low helpfulness
    if (stats["helpfulness_rate"] or 0) < 70:
        issues.append({
            "type": "low_helpfulness",
            "severity": "medium",
            "message": f"Coaching helpfulness is {stats['helpfulness_rate']}% (target: 80%+)",
            "metric_value": stats["helpfulness_rate"],
            "affected_count": stats["not_helpful_count"],
        })

    # Issue 3: High missing context
    missing_context_rate = (
        (100 * stats["missing_context_count"]) / stats["total_feedback"]
        if stats["total_feedback"] > 0
        else 0
    )

    if missing_context_rate > 20:
        issues.append({
            "type": "missing_context",
            "severity": "medium",
            "message": f"{missing_context_rate:.0f}% of feedback indicates missing context in coaching",
            "metric_value": missing_context_rate,
            "affected_count": stats["missing_context_count"],
        })

    return sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])


def get_feedback_by_rep(
    rep_email: str,
    days: int = 30,
) -> dict[str, Any] | None:
    """
    Get feedback statistics for a specific rep.

    Args:
        rep_email: Email of the rep
        days: Number of days to look back

    Returns:
        Stats dict with accuracy and helpfulness rates
    """
    return fetch_one(
        """
        SELECT
            COUNT(*) as total_feedback,
            SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) as accurate_count,
            SUM(CASE WHEN cf.feedback_type = 'inaccurate' THEN 1 ELSE 0 END) as inaccurate_count,
            SUM(CASE WHEN cf.feedback_type = 'missing_context' THEN 1 ELSE 0 END) as missing_context_count,
            SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) as helpful_count,
            SUM(CASE WHEN cf.feedback_type = 'not_helpful' THEN 1 ELSE 0 END) as not_helpful_count,
            ROUND(
                100.0 * SUM(CASE WHEN cf.feedback_type = 'accurate' THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0),
                2
            ) as accuracy_rate,
            ROUND(
                100.0 * SUM(CASE WHEN cf.feedback_type = 'helpful' THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0),
                2
            ) as helpfulness_rate
        FROM coaching_feedback cf
        JOIN coaching_sessions cs ON cf.coaching_session_id = cs.id
        JOIN speakers s ON cf.rep_id = s.id
        WHERE s.email = %s
        AND cf.created_at >= NOW() - INTERVAL '%s days'
        """,
        (rep_email, days),
    )
