"""
Helper functions for common database queries.
Provides high-level abstractions over raw SQL.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from .connection import execute_query, fetch_all, fetch_one
from .models import CoachingDimension

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


def get_all_speakers(
    company_side_only: bool = True,
    role_filter: str | None = None,
    include_unassigned: bool = True,
) -> list[dict[str, Any]]:
    """
    Get all speakers, optionally filtered by company_side and role.

    Args:
        company_side_only: If True, only return Prefect staff (company_side=true)
        role_filter: Optional role to filter by ('ae', 'se', 'csm', 'support')
        include_unassigned: If False, exclude speakers with role=NULL

    Returns:
        List of speaker dictionaries with unique speakers (distinct by email)
        Fields: id, email, name, role, company_side, last_call_date, total_calls
    """
    where_clauses = []
    params: list[Any] = []

    if company_side_only:
        where_clauses.append("company_side = true")

    if role_filter:
        where_clauses.append("role = %s")
        params.append(role_filter)

    if not include_unassigned:
        where_clauses.append("role IS NOT NULL")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Get unique speakers with aggregated stats
    query = f"""
        SELECT DISTINCT ON (email)
            id,
            email,
            name,
            role,
            company_side,
            (SELECT MIN(c.scheduled_at)
             FROM calls c
             JOIN speakers s2 ON s2.call_id = c.id
             WHERE s2.email = speakers.email) as first_seen,
            (SELECT MAX(c.scheduled_at)
             FROM calls c
             JOIN speakers s2 ON s2.call_id = c.id
             WHERE s2.email = speakers.email) as last_call_date,
            (SELECT COUNT(DISTINCT s3.call_id)
             FROM speakers s3
             WHERE s3.email = speakers.email) as total_calls
        FROM speakers
        {where_sql}
        ORDER BY email, id DESC
    """

    return fetch_all(query, tuple(params))


def get_speaker_role(speaker_id: UUID) -> dict[str, Any] | None:
    """
    Get speaker with role information by speaker_id.

    Args:
        speaker_id: UUID of the speaker

    Returns:
        Dictionary with speaker details including role, or None if not found
        Fields: id, email, name, role, company_side, call_id, talk_time_seconds, etc.
    """
    return fetch_one(
        """
        SELECT
            id,
            email,
            name,
            role,
            company_side,
            call_id,
            talk_time_seconds,
            talk_time_percentage,
            speaker_id as gong_speaker_id,
            manager_id
        FROM speakers
        WHERE id = %s
        """,
        (str(speaker_id),),
    )


def update_speaker_role(
    speaker_id: UUID, role: str | None, changed_by: str
) -> dict[str, Any] | None:
    """
    Update speaker role and log the change to speaker_role_history.

    Args:
        speaker_id: UUID of the speaker to update
        role: New role ('ae', 'se', 'csm', 'support', or None to remove role)
        changed_by: Email of user making the change (for audit trail)

    Returns:
        Updated speaker record with new role, or None if speaker not found

    Raises:
        ValueError: If role is not a valid speaker_role value

    Note:
        The change is automatically logged to speaker_role_history via database trigger.
        The trigger uses app.current_user session variable to track changed_by.
    """
    # Validate role value
    valid_roles = ["ae", "se", "csm", "support", None]
    if role not in valid_roles:
        raise ValueError(f"Invalid role '{role}'. Must be one of: ae, se, csm, support, or None")

    # Use a transaction to set session variable and update role
    # The session variable is used by the trigger to track changed_by
    from psycopg2.extras import RealDictCursor

    from .connection import get_db_connection

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # Set session variable for audit trail
                cur.execute("SELECT set_config('app.current_user', %s, false)", (changed_by,))

                # Update speaker role
                cur.execute(
                    """
                    UPDATE speakers
                    SET role = %s::speaker_role
                    WHERE id = %s
                    RETURNING
                        id,
                        email,
                        name,
                        role,
                        company_side,
                        call_id,
                        talk_time_seconds,
                        talk_time_percentage,
                        speaker_id as gong_speaker_id,
                        manager_id
                    """,
                    (role, str(speaker_id)),
                )

                result = cur.fetchone()
                conn.commit()

                return dict(result) if result else None

            except Exception as e:
                conn.rollback()
                logger.error(
                    f"Failed to update speaker role: {e}\n"
                    f"speaker_id={speaker_id}, role={role}, changed_by={changed_by}"
                )
                raise


def bulk_update_speaker_roles(
    updates: list[tuple[UUID, str | None]], changed_by: str
) -> dict[str, Any]:
    """
    Update multiple speaker roles in a single transaction.

    Args:
        updates: List of (speaker_id, role) tuples to update
        changed_by: Email of user making the changes (for audit trail)

    Returns:
        Dictionary with results:
        {
            "updated": int,  # Number of speakers successfully updated
            "failed": list[str],  # List of speaker_ids that failed (if any)
            "speakers": list[dict]  # Updated speaker records
        }

    Raises:
        ValueError: If any role is not a valid speaker_role value

    Example:
        >>> updates = [
        ...     (UUID('...'), 'ae'),
        ...     (UUID('...'), 'se'),
        ...     (UUID('...'), None)
        ... ]
        >>> result = bulk_update_speaker_roles(updates, 'manager@prefect.io')
        >>> print(f"Updated {result['updated']} speakers")

    Note:
        All updates are performed in a single transaction. If any update fails,
        all changes are rolled back. Each change is logged to speaker_role_history.
    """
    # Validate all role values before starting
    valid_roles = ["ae", "se", "csm", "support", None]
    for speaker_id, role in updates:
        if role not in valid_roles:
            raise ValueError(
                f"Invalid role '{role}' for speaker {speaker_id}. "
                f"Must be one of: ae, se, csm, support, or None"
            )

    from psycopg2.extras import RealDictCursor

    from .connection import get_db_connection

    updated_speakers = []
    failed_ids = []

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # Set session variable for audit trail
                cur.execute("SELECT set_config('app.current_user', %s, false)", (changed_by,))

                # Update each speaker
                for speaker_id, role in updates:
                    try:
                        cur.execute(
                            """
                            UPDATE speakers
                            SET role = %s::speaker_role
                            WHERE id = %s
                            RETURNING
                                id,
                                email,
                                name,
                                role,
                                company_side,
                                call_id,
                                talk_time_seconds,
                                talk_time_percentage,
                                speaker_id as gong_speaker_id,
                                manager_id
                            """,
                            (role, str(speaker_id)),
                        )

                        result = cur.fetchone()
                        if result:
                            updated_speakers.append(dict(result))
                        else:
                            # Speaker not found
                            failed_ids.append(str(speaker_id))
                            logger.warning(f"Speaker not found: {speaker_id}")

                    except Exception as e:
                        failed_ids.append(str(speaker_id))
                        logger.error(f"Failed to update speaker {speaker_id}: {e}")

                # Commit all changes if no failures, otherwise rollback
                if failed_ids:
                    conn.rollback()
                    logger.warning(f"Bulk update rolled back due to {len(failed_ids)} failures")
                else:
                    conn.commit()
                    logger.info(f"Successfully updated {len(updated_speakers)} speaker roles")

                return {
                    "updated": len(updated_speakers),
                    "failed": failed_ids,
                    "speakers": updated_speakers,
                }

            except Exception as e:
                conn.rollback()
                logger.error(f"Bulk update failed: {e}")
                raise


def get_speaker_role_history(speaker_id: UUID, limit: int = 50) -> list[dict[str, Any]]:
    """
    Get role change history for a speaker.

    Args:
        speaker_id: UUID of the speaker
        limit: Maximum number of history entries to return (default: 50)

    Returns:
        List of history entries, ordered by most recent first.
        Each entry contains:
        - id: UUID of the history entry
        - speaker_id: UUID of the speaker
        - old_role: Previous role (None if first assignment)
        - new_role: New role after change (None if role removed)
        - changed_by: Email of user who made the change
        - changed_at: Timestamp of the change
        - change_reason: Description of the change (e.g., "Role changed", "Initial role assignment")
        - metadata: Additional context as JSONB

    Example:
        >>> history = get_speaker_role_history(UUID('...'))
        >>> for entry in history:
        ...     print(f"{entry['changed_at']}: {entry['old_role']} → {entry['new_role']} by {entry['changed_by']}")
    """
    return fetch_all(
        """
        SELECT
            id,
            speaker_id,
            old_role,
            new_role,
            changed_by,
            changed_at,
            change_reason,
            metadata
        FROM speaker_role_history
        WHERE speaker_id = %s
        ORDER BY changed_at DESC
        LIMIT %s
        """,
        (str(speaker_id), limit),
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
# RUBRIC QUERIES
# ============================================================================


def get_rubric_criteria(role: str, dimension: str | None = None) -> list[dict[str, Any]]:
    """
    Get rubric criteria filtered by role and optionally by dimension.

    Args:
        role: Speaker role ('ae', 'se', 'csm', 'support')
        dimension: Optional dimension filter ('discovery', 'engagement', 'product_knowledge',
                   'objection_handling', 'five_wins'). If None, returns all dimensions for role.

    Returns:
        List of rubric criteria ordered by display_order.
        Each criterion contains:
        - id: UUID of the criterion
        - role: Speaker role
        - dimension: Coaching dimension
        - criterion_name: Short name
        - description: Detailed description
        - weight: Percentage weight within dimension
        - max_score: Maximum score
        - display_order: Display order
        - created_at, updated_at: Timestamps

    Example:
        >>> criteria = get_rubric_criteria('ae', 'discovery')
        >>> for criterion in criteria:
        ...     print(f"{criterion['criterion_name']}: {criterion['weight']}%")
    """
    if dimension:
        return fetch_all(
            """
            SELECT
                id,
                role,
                dimension,
                criterion_name,
                description,
                weight,
                max_score,
                display_order,
                created_at,
                updated_at
            FROM rubric_criteria
            WHERE role = %s AND dimension = %s
            ORDER BY display_order ASC
            """,
            (role, dimension),
        )
    else:
        return fetch_all(
            """
            SELECT
                id,
                role,
                dimension,
                criterion_name,
                description,
                weight,
                max_score,
                display_order,
                created_at,
                updated_at
            FROM rubric_criteria
            WHERE role = %s
            ORDER BY dimension ASC, display_order ASC
            """,
            (role,),
        )


def update_rubric_criterion(
    criterion_id: UUID,
    description: str | None = None,
    weight: int | None = None,
    max_score: int | None = None,
    display_order: int | None = None,
    changed_by: str | None = None,
) -> dict[str, Any] | None:
    """
    Update a rubric criterion with field-level change tracking.

    Args:
        criterion_id: UUID of the criterion to update
        description: New description (10-500 chars, optional)
        weight: New weight percentage (0-100, optional)
        max_score: New max score (1-100, optional)
        display_order: New display order (optional)
        changed_by: Email of user making the change (for audit trail, optional)

    Returns:
        Updated criterion record, or None if not found

    Raises:
        ValueError: If validation constraints are violated

    Note:
        Changes are automatically logged to rubric_change_log via database trigger.
        The trigger uses app.current_user session variable for changed_by tracking.
        Only provided fields are updated (partial update support).
    """
    # Validate inputs
    if description is not None and not (10 <= len(description) <= 500):
        raise ValueError("Description must be between 10 and 500 characters")

    if weight is not None and not (0 <= weight <= 100):
        raise ValueError("Weight must be between 0 and 100")

    if max_score is not None and not (1 <= max_score <= 100):
        raise ValueError("Max score must be between 1 and 100")

    # Build dynamic UPDATE query based on provided fields
    updates = []
    params = []

    if description is not None:
        updates.append("description = %s")
        params.append(description)

    if weight is not None:
        updates.append("weight = %s")
        params.append(weight)

    if max_score is not None:
        updates.append("max_score = %s")
        params.append(max_score)

    if display_order is not None:
        updates.append("display_order = %s")
        params.append(display_order)

    # If no updates provided, return current record
    if not updates:
        return fetch_one(
            "SELECT * FROM rubric_criteria WHERE id = %s",
            (str(criterion_id),),
        )

    # Add criterion_id to params
    params.append(str(criterion_id))

    from psycopg2.extras import RealDictCursor

    from .connection import get_db_connection

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # Set session variable for audit trail if changed_by provided
                if changed_by:
                    cur.execute(
                        "SELECT set_config('app.current_user', %s, false)",
                        (changed_by,),
                    )

                # Build and execute UPDATE query
                update_clause = ", ".join(updates)
                query = f"""
                    UPDATE rubric_criteria
                    SET {update_clause}
                    WHERE id = %s
                    RETURNING
                        id,
                        role,
                        dimension,
                        criterion_name,
                        description,
                        weight,
                        max_score,
                        display_order,
                        created_at,
                        updated_at
                """

                cur.execute(query, params)
                result = cur.fetchone()
                conn.commit()

                return dict(result) if result else None

            except Exception as e:
                conn.rollback()
                logger.error(
                    f"Failed to update rubric criterion: {e}\n"
                    f"criterion_id={criterion_id}, updates={updates}"
                )
                raise


def create_rubric_criterion(
    role: str,
    dimension: str,
    criterion_name: str,
    description: str,
    weight: int,
    max_score: int,
    display_order: int = 0,
    changed_by: str | None = None,
) -> dict[str, Any]:
    """
    Create a new rubric criterion.

    Args:
        role: Speaker role ('ae', 'se', 'csm', 'support')
        dimension: Coaching dimension ('discovery', 'engagement', 'product_knowledge',
                   'objection_handling', 'five_wins')
        criterion_name: Short name for the criterion (max 100 chars)
        description: Detailed description (10-500 chars)
        weight: Percentage weight within dimension (0-100)
        max_score: Maximum score for criterion (1-100)
        display_order: Display order (default: 0)
        changed_by: Email of user creating the criterion (for audit trail, optional)

    Returns:
        Newly created criterion record

    Raises:
        ValueError: If validation constraints are violated
        psycopg2.IntegrityError: If criterion_name already exists for this role-dimension

    Note:
        Creation is automatically logged to rubric_change_log via database trigger.
        The unique constraint ensures no duplicate criterion names per role-dimension.
    """
    # Validate inputs
    if not criterion_name or len(criterion_name) > 100:
        raise ValueError("Criterion name must be 1-100 characters")

    if not (10 <= len(description) <= 500):
        raise ValueError("Description must be between 10 and 500 characters")

    if not (0 <= weight <= 100):
        raise ValueError("Weight must be between 0 and 100")

    if not (1 <= max_score <= 100):
        raise ValueError("Max score must be between 1 and 100")

    from psycopg2.extras import RealDictCursor

    from .connection import get_db_connection

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # Set session variable for audit trail if changed_by provided
                if changed_by:
                    cur.execute(
                        "SELECT set_config('app.current_user', %s, false)",
                        (changed_by,),
                    )

                # Insert new criterion
                cur.execute(
                    """
                    INSERT INTO rubric_criteria (
                        role,
                        dimension,
                        criterion_name,
                        description,
                        weight,
                        max_score,
                        display_order
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING
                        id,
                        role,
                        dimension,
                        criterion_name,
                        description,
                        weight,
                        max_score,
                        display_order,
                        created_at,
                        updated_at
                    """,
                    (
                        role,
                        dimension,
                        criterion_name,
                        description,
                        weight,
                        max_score,
                        display_order,
                    ),
                )

                result = cur.fetchone()
                conn.commit()

                logger.info(f"Created rubric criterion: {criterion_name} for {role}/{dimension}")

                return dict(result)

            except Exception as e:
                conn.rollback()
                logger.error(
                    f"Failed to create rubric criterion: {e}\n"
                    f"role={role}, dimension={dimension}, criterion_name={criterion_name}"
                )
                raise


def delete_rubric_criterion(
    criterion_id: UUID,
    changed_by: str | None = None,
) -> bool:
    """
    Delete a rubric criterion.

    Args:
        criterion_id: UUID of the criterion to delete
        changed_by: Email of user deleting the criterion (for audit trail, optional)

    Returns:
        True if criterion was deleted, False if not found

    Note:
        Deletion is automatically logged to rubric_change_log via database trigger.
        The trigger uses app.current_user session variable for changed_by tracking.
        After deletion, the change log entry will have criterion_id set to NULL
        (due to ON DELETE SET NULL constraint) but the snapshot is preserved.
    """
    from .connection import get_db_connection

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                # Set session variable for audit trail if changed_by provided
                if changed_by:
                    cur.execute(
                        "SELECT set_config('app.current_user', %s, false)",
                        (changed_by,),
                    )

                # Delete the criterion
                cur.execute(
                    """
                    DELETE FROM rubric_criteria
                    WHERE id = %s
                    """,
                    (str(criterion_id),),
                )

                deleted = cur.rowcount > 0
                conn.commit()

                if deleted:
                    logger.info(f"Deleted rubric criterion: {criterion_id}")
                else:
                    logger.warning(f"Criterion not found for deletion: {criterion_id}")

                return deleted

            except Exception as e:
                conn.rollback()
                logger.error(
                    f"Failed to delete rubric criterion: {e}\n" f"criterion_id={criterion_id}"
                )
                raise


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
        issues.append(
            {
                "type": "low_accuracy",
                "severity": "high",
                "message": f"Coaching accuracy is {stats['accuracy_rate']}% (target: 90%+)",
                "metric_value": stats["accuracy_rate"],
                "affected_count": stats["inaccurate_count"],
            }
        )

    # Issue 2: Low helpfulness
    if (stats["helpfulness_rate"] or 0) < 70:
        issues.append(
            {
                "type": "low_helpfulness",
                "severity": "medium",
                "message": f"Coaching helpfulness is {stats['helpfulness_rate']}% (target: 80%+)",
                "metric_value": stats["helpfulness_rate"],
                "affected_count": stats["not_helpful_count"],
            }
        )

    # Issue 3: High missing context
    missing_context_rate = (
        (100 * stats["missing_context_count"]) / stats["total_feedback"]
        if stats["total_feedback"] > 0
        else 0
    )

    if missing_context_rate > 20:
        issues.append(
            {
                "type": "missing_context",
                "severity": "medium",
                "message": f"{missing_context_rate:.0f}% of feedback indicates missing context in coaching",
                "metric_value": missing_context_rate,
                "affected_count": stats["missing_context_count"],
            }
        )

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


# ============================================================================
# USER QUERIES (RBAC)
# ============================================================================


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """
    Get user by email address.

    Args:
        email: User email address

    Returns:
        User dict with id, email, name, role, or None if not found
    """
    return fetch_one(
        "SELECT id, email, name, role, created_at, updated_at FROM users WHERE email = %s",
        (email,),
    )


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    """
    Get user by ID.

    Args:
        user_id: User UUID

    Returns:
        User dict with id, email, name, role, or None if not found
    """
    return fetch_one(
        "SELECT id, email, name, role, created_at, updated_at FROM users WHERE id = %s",
        (user_id,),
    )


def get_managed_reps(manager_email: str) -> list[dict[str, Any]]:
    """
    Get all reps managed by a specific manager.

    Args:
        manager_email: Manager's email address

    Returns:
        List of user dicts for reps reporting to this manager
    """
    return fetch_all(
        """
        SELECT DISTINCT u.id, u.email, u.name, u.role
        FROM users u
        JOIN speakers s ON u.email = s.email
        JOIN users m ON s.manager_id = m.id
        WHERE m.email = %s
        AND u.role = 'rep'
        ORDER BY u.name
        """,
        (manager_email,),
    )


def get_calls_for_user(user_email: str, role: str, limit: int = 50) -> list[dict[str, Any]]:
    """
    Get calls filtered by user role.
    - Reps see only their own calls
    - Managers see their team's calls
    - Admins see all calls

    Args:
        user_email: User's email address
        role: User's role ('admin', 'manager', 'rep')
        limit: Maximum number of calls to return

    Returns:
        List of call dicts
    """
    if role == "admin":
        # Admins see all calls
        return fetch_all(
            "SELECT * FROM calls ORDER BY scheduled_at DESC NULLS LAST LIMIT %s",
            (limit,),
        )
    elif role == "manager":
        # Managers see their team's calls
        return fetch_all(
            """
            SELECT DISTINCT c.*
            FROM calls c
            JOIN speakers s ON c.id = s.call_id
            JOIN users u ON s.email = u.email
            JOIN speakers s2 ON u.email = s2.email
            JOIN users manager ON s2.manager_id = manager.id
            WHERE manager.email = %s
            ORDER BY c.scheduled_at DESC NULLS LAST
            LIMIT %s
            """,
            (user_email, limit),
        )
    else:  # rep
        # Reps see only their own calls
        return fetch_all(
            """
            SELECT DISTINCT c.*
            FROM calls c
            JOIN speakers s ON c.id = s.call_id
            WHERE s.email = %s
            AND s.company_side = true
            ORDER BY c.scheduled_at DESC NULLS LAST
            LIMIT %s
            """,
            (user_email, limit),
        )
