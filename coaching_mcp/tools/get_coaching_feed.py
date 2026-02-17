"""
Get Coaching Feed Tool

Generates a personalized coaching feed with recent insights, team trends,
and high-impact moments for sales reps and managers.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from db import queries
from db.connection import get_db_connection

logger = logging.getLogger(__name__)


def get_coaching_feed_tool(
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
    try:
        # Calculate date range based on time_filter
        end_dt = datetime.now()
        if time_filter == "today":
            start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "this_week":
            start_dt = end_dt - timedelta(days=7)
        elif time_filter == "this_month":
            start_dt = end_dt - timedelta(days=30)
        elif time_filter == "custom" and start_date and end_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        else:
            # Default: last 7 days
            start_dt = end_dt - timedelta(days=7)

        # Fetch recent coaching sessions
        if rep_email:
            # Get sessions for specific rep
            sessions = queries.get_coaching_sessions_for_rep(
                rep_email=rep_email, start_date=start_dt, end_date=end_dt
            )
        else:
            # Get all recent sessions (for managers/feed view)
            sessions = _get_recent_sessions(start_dt, end_dt, limit * 2)

        # Generate feed items from sessions
        feed_items = []
        for session in sessions:
            # Skip dismissed items unless requested
            if not include_dismissed and session.get("is_dismissed"):
                continue

            # Apply type filter
            if type_filter and type_filter != "all" and type_filter != "call_analysis":
                continue

            # Get call details
            call = queries.get_call_by_id(session["call_id"])
            if not call:
                continue

            # Calculate overall score (average of dimensions)
            scores = session.get("scores", {})
            avg_score = sum(scores.values()) / len(scores) if scores else 0.0

            # Determine if this is a highlight (exceptional or concerning score)
            is_highlight = avg_score >= 8.5 or avg_score <= 4.0

            # Create feed item
            item = {
                "id": f"session_{session['id']}",
                "type": "call_analysis",
                "timestamp": (
                    session["created_at"].isoformat()
                    if isinstance(session["created_at"], datetime)
                    else session["created_at"]
                ),
                "title": f"Call Analysis: {call.get('title', 'Untitled Call')}",
                "description": _generate_description(session, avg_score),
                "metadata": {
                    "call_id": session["call_id"],
                    "call_title": call.get("title"),
                    "rep_email": session.get("rep_email"),
                    "score": round(avg_score, 1),
                    "dimension": _get_top_dimension(scores),
                    "action_items": session.get("action_items", [])[:3],
                },
                "is_bookmarked": session.get("is_bookmarked", False),
                "is_dismissed": session.get("is_dismissed", False),
                "is_new": _is_new(session),
            }

            feed_items.append(item)

            # If this is a highlight, add to highlights section
            if is_highlight:
                # Highlights will be extracted separately

                pass

        # Apply pagination
        total_count = len(feed_items)
        feed_items = feed_items[offset : offset + limit]
        has_more = offset + limit < total_count

        # Extract highlights (top/bottom performers)
        highlights = []
        if not type_filter or type_filter in ["all", "highlight"]:
            for item in feed_items:
                if item["metadata"]["score"] >= 8.5:
                    highlights.append(
                        {
                            "id": f"highlight_{item['id']}",
                            "type": "achievement",
                            "title": f"Excellent Call: {item['metadata']['call_title']}",
                            "description": f"Scored {item['metadata']['score']}/10 - Outstanding {item['metadata']['dimension']}",
                            "timestamp": item["timestamp"],
                            "call_id": item["metadata"]["call_id"],
                        }
                    )
                elif item["metadata"]["score"] <= 4.0:
                    highlights.append(
                        {
                            "id": f"concern_{item['id']}",
                            "type": "needs_attention",
                            "title": f"Needs Coaching: {item['metadata']['call_title']}",
                            "description": f"Scored {item['metadata']['score']}/10 - Focus on {item['metadata']['dimension']}",
                            "timestamp": item["timestamp"],
                            "call_id": item["metadata"]["call_id"],
                        }
                    )

        # Generate team insights (managers only)
        team_insights = []
        if include_team_insights:
            # Calculate team-wide metrics
            all_sessions = _get_recent_sessions(start_dt, end_dt, 1000)

            if all_sessions:
                # Team average score
                team_scores = []
                for s in all_sessions:
                    scores = s.get("scores", {})
                    if scores:
                        team_scores.append(sum(scores.values()) / len(scores))

                if team_scores:
                    team_avg = sum(team_scores) / len(team_scores)
                    team_insights.append(
                        {
                            "id": "team_avg",
                            "type": "trend",
                            "title": "Team Performance Overview",
                            "description": f"Team average score: {team_avg:.1f}/10 across {len(all_sessions)} calls",
                            "metric": "average_score",
                            "value": round(team_avg, 1),
                            "trend": "stable",  # Could calculate trend from previous period
                        }
                    )

        # Count new items (created in last 24 hours)
        new_items_count = sum(1 for item in feed_items if item.get("is_new"))

        return {
            "items": feed_items,
            "team_insights": team_insights,
            "highlights": highlights[:5],  # Limit to 5 highlights
            "total_count": total_count,
            "has_more": has_more,
            "new_items_count": new_items_count,
        }

    except Exception as e:
        logger.error(f"Error generating coaching feed: {e}", exc_info=True)
        # Return empty feed on error
        return {
            "items": [],
            "team_insights": [],
            "highlights": [],
            "total_count": 0,
            "has_more": False,
            "new_items_count": 0,
            "error": str(e),
        }


def _generate_description(session: dict[str, Any], avg_score: float) -> str:
    """Generate a description for a feed item based on the session."""
    scores = session.get("scores", {})

    if avg_score >= 8.0:
        return f"Excellent performance across {len(scores)} dimensions. Review strengths to replicate success."
    elif avg_score >= 6.0:
        return "Solid performance with room for improvement. Check action items for next steps."
    else:
        return "Coaching opportunity identified. Focus on key areas for development."


def _get_top_dimension(scores: dict[str, float]) -> str:
    """Get the dimension with the highest (or lowest if concerning) score."""
    if not scores:
        return "overall"

    # Return the dimension with highest score
    top_dim = max(scores.items(), key=lambda x: x[1])
    return top_dim[0]


def _is_new(session: dict[str, Any]) -> bool:
    """Check if a session was created in the last 24 hours."""
    created_at = session.get("created_at")
    if not created_at:
        return False

    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

    age = datetime.now() - created_at.replace(tzinfo=None)
    return bool(age.total_seconds() < 86400)  # 24 hours


def _get_recent_sessions(
    start_date: datetime, end_date: datetime, limit: int = 100
) -> list[dict[str, Any]]:
    """Get all recent coaching sessions within a date range."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT
                cs.id,
                cs.call_id,
                cs.created_at,
                cs.scores,
                cs.action_items,
                cs.strengths,
                cs.weaknesses,
                s.email as rep_email,
                s.name as rep_name
            FROM coaching_sessions cs
            JOIN speakers s ON cs.rep_id = s.id
            WHERE cs.created_at >= %s
              AND cs.created_at <= %s
              AND s.company_side = true
            ORDER BY cs.created_at DESC
            LIMIT %s
        """
        cursor.execute(query, (start_date, end_date, limit))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
