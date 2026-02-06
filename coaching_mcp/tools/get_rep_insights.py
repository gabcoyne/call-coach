"""
Get Rep Insights Tool - Performance trends and coaching history for a sales rep.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from db import fetch_all, fetch_one

logger = logging.getLogger(__name__)


def get_rep_insights_tool(
    rep_email: str,
    time_period: str = "last_30_days",
    product_filter: str | None = None,
) -> dict[str, Any]:
    """
    Generate comprehensive performance insights for a sales rep.

    Args:
        rep_email: Email address of the sales rep
        time_period: Time range for analysis
        product_filter: Optional product filter

    Returns:
        Rep performance data with trends, gaps, and coaching plan
    """
    logger.info(f"Getting insights for {rep_email} over {time_period}")

    # Step 1: Parse time period
    date_filter = parse_time_period(time_period)

    # Step 2: Get rep info
    rep_info = fetch_one(
        """
        SELECT
            s.id,
            s.name,
            s.email,
            s.role,
            COUNT(DISTINCT c.id) as calls_analyzed
        FROM speakers s
        JOIN calls c ON s.call_id = c.id
        WHERE s.email = %s
            AND s.company_side = true
            AND c.processed_at IS NOT NULL
            AND c.scheduled_at >= %s
            AND (%s IS NULL OR c.product = %s)
        GROUP BY s.id, s.name, s.email, s.role
        LIMIT 1
        """,
        (rep_email, date_filter, product_filter, product_filter),
        as_dict=True,
    )

    if not rep_info or not isinstance(rep_info, dict):
        return {
            "error": f"No calls found for {rep_email} in {time_period}",
            "suggestion": "Check email address and ensure calls have been processed.",
        }

    logger.info(f"Found {rep_info['calls_analyzed']} calls for {rep_info['name']}")

    # Step 3: Get score trends over time
    score_trends = fetch_all(
        """
        SELECT
            cs.coaching_dimension,
            DATE_TRUNC('week', cs.created_at) as week,
            AVG(cs.score) as avg_score,
            COUNT(*) as call_count
        FROM coaching_sessions cs
        JOIN calls c ON cs.call_id = c.id
        WHERE cs.rep_id = %s
            AND cs.score IS NOT NULL
            AND cs.created_at >= %s
            AND (%s IS NULL OR c.product = %s)
        GROUP BY cs.coaching_dimension, DATE_TRUNC('week', cs.created_at)
        ORDER BY cs.coaching_dimension, week
        """,
        (rep_info["id"], date_filter, product_filter, product_filter),
        as_dict=True,
    )

    # Format trends by dimension
    trends_by_dimension: dict[str, dict[str, list[Any]]] = {}
    if isinstance(score_trends, list):
        for row in score_trends:
            if not isinstance(row, dict):
                continue
            dim = row["coaching_dimension"]
            if dim not in trends_by_dimension:
                trends_by_dimension[dim] = {"dates": [], "scores": [], "call_counts": []}

            trends_by_dimension[dim]["dates"].append(str(row["week"].date()))
            trends_by_dimension[dim]["scores"].append(round(float(row["avg_score"]), 1))
            trends_by_dimension[dim]["call_counts"].append(row["call_count"])

    # Step 4: Identify skill gaps (role-aware comparison)
    # Get rep's role for fair comparison
    rep_role = rep_info.get("role") or "ae"

    skill_gaps = fetch_all(
        """
        WITH rep_avg AS (
            SELECT
                coaching_dimension,
                AVG(score) as rep_score,
                COUNT(*) as sample_size
            FROM coaching_sessions
            WHERE rep_id = %s
                AND score IS NOT NULL
                AND created_at >= %s
            GROUP BY coaching_dimension
        ),
        team_avg AS (
            -- Compare to team members with same role only
            SELECT
                cs.coaching_dimension,
                AVG(cs.score) as team_score
            FROM coaching_sessions cs
            WHERE cs.score IS NOT NULL
                AND cs.created_at >= %s
                -- Filter by rubric_role in metadata to ensure apples-to-apples comparison
                AND cs.metadata->>'rubric_role' = %s
            GROUP BY cs.coaching_dimension
        )
        SELECT
            r.coaching_dimension as area,
            ROUND(r.rep_score, 1) as current_score,
            ROUND(t.team_score, 1) as target_score,
            ROUND(t.team_score - r.rep_score, 1) as gap,
            r.sample_size,
            CASE
                WHEN t.team_score - r.rep_score > 15 THEN 'high'
                WHEN t.team_score - r.rep_score > 5 THEN 'medium'
                ELSE 'low'
            END as priority
        FROM rep_avg r
        JOIN team_avg t ON r.coaching_dimension = t.coaching_dimension
        WHERE t.team_score > r.rep_score
        ORDER BY (t.team_score - r.rep_score) DESC
        """,
        (rep_info["id"], date_filter, date_filter, rep_role),
        as_dict=True,
    )

    # Step 5: Identify improvement areas (trending up/down/stable)
    improvement_areas = fetch_all(
        """
        WITH recent AS (
            SELECT
                coaching_dimension,
                AVG(score) as recent_score
            FROM coaching_sessions
            WHERE rep_id = %s
                AND score IS NOT NULL
                AND created_at >= NOW() - INTERVAL '14 days'
            GROUP BY coaching_dimension
        ),
        older AS (
            SELECT
                coaching_dimension,
                AVG(score) as older_score
            FROM coaching_sessions
            WHERE rep_id = %s
                AND score IS NOT NULL
                AND created_at >= NOW() - INTERVAL '60 days'
                AND created_at < NOW() - INTERVAL '14 days'
            GROUP BY coaching_dimension
        )
        SELECT
            r.coaching_dimension as area,
            ROUND(r.recent_score, 1) as recent_score,
            ROUND(o.older_score, 1) as older_score,
            ROUND(r.recent_score - o.older_score, 1) as change,
            CASE
                WHEN r.recent_score > o.older_score + 5 THEN 'improving'
                WHEN r.recent_score < o.older_score - 5 THEN 'declining'
                ELSE 'stable'
            END as trend
        FROM recent r
        LEFT JOIN older o ON r.coaching_dimension = o.coaching_dimension
        WHERE o.older_score IS NOT NULL
        """,
        (rep_info["id"], rep_info["id"]),
        as_dict=True,
    )

    # Step 6: Get recent wins (high-scoring moments)
    recent_wins = fetch_all(
        """
        SELECT DISTINCT
            c.title,
            c.scheduled_at,
            cs.coaching_dimension,
            cs.score,
            (cs.strengths)[1:3] as top_strengths
        FROM coaching_sessions cs
        JOIN calls c ON cs.call_id = c.id
        WHERE cs.rep_id = %s
            AND cs.score >= 85
            AND cs.created_at >= %s
        ORDER BY cs.score DESC, c.scheduled_at DESC
        LIMIT 5
        """,
        (rep_info["id"], date_filter),
        as_dict=True,
    )

    wins_formatted: list[str] = []
    if isinstance(recent_wins, list):
        for w in recent_wins:
            if not isinstance(w, dict):
                continue
            wins_formatted.append(
                f"{w['coaching_dimension']}: {w['score']}/100 on '{w['title']}' - "
                + ", ".join(w["top_strengths"] or [])
            )

    # Step 7: Generate coaching plan
    coaching_plan = generate_coaching_plan(skill_gaps, improvement_areas)

    # Step 8: Build response
    return {
        "rep_info": {
            "name": rep_info["name"],
            "email": rep_info["email"],
            "role": rep_info["role"],
            "calls_analyzed": rep_info["calls_analyzed"],
            "date_range": {
                "start": str(date_filter.date()),
                "end": str(datetime.now().date()),
                "period": time_period,
            },
            "product_filter": product_filter,
        },
        "score_trends": trends_by_dimension,
        "skill_gaps": skill_gaps,
        "improvement_areas": improvement_areas,
        "recent_wins": wins_formatted,
        "coaching_plan": coaching_plan,
    }


def parse_time_period(time_period: str) -> datetime:
    """Convert time period string to datetime filter."""
    now = datetime.now()

    if time_period == "last_7_days":
        return now - timedelta(days=7)
    elif time_period == "last_30_days":
        return now - timedelta(days=30)
    elif time_period == "last_quarter":
        return now - timedelta(days=90)
    elif time_period == "last_year":
        return now - timedelta(days=365)
    elif time_period == "all_time":
        return datetime(2020, 1, 1)  # Arbitrary old date
    else:
        logger.warning(f"Unknown time period '{time_period}', defaulting to last_30_days")
        return now - timedelta(days=30)


def generate_coaching_plan(skill_gaps: list[Any], improvement_areas: list[Any]) -> str:
    """
    Generate a personalized coaching plan based on gaps and trends.

    Args:
        skill_gaps: List of skills below team average
        improvement_areas: List of areas trending up/down

    Returns:
        Coaching plan as formatted markdown
    """
    plan_parts = ["# Personalized Coaching Plan\n"]

    # Section 1: Priority Focus Areas
    high_priority_gaps = [
        g for g in skill_gaps if isinstance(g, dict) and g.get("priority") == "high"
    ]
    if high_priority_gaps:
        plan_parts.append("## 🎯 Priority Focus Areas (High Impact)\n")
        for gap in high_priority_gaps[:3]:  # Top 3
            plan_parts.append(
                f"- **{gap['area'].replace('_', ' ').title()}**: "
                f"Current {gap['current_score']}/100, Target {gap['target_score']}/100 "
                f"(Gap: {abs(gap['gap'])} points)\n"
            )
        plan_parts.append("\n")

    # Section 2: Quick Wins
    medium_priority_gaps = [
        g for g in skill_gaps if isinstance(g, dict) and g.get("priority") == "medium"
    ]
    if medium_priority_gaps:
        plan_parts.append("## ⚡ Quick Wins (Medium Impact)\n")
        for gap in medium_priority_gaps[:2]:
            plan_parts.append(f"- {gap['area'].replace('_', ' ').title()}\n")
        plan_parts.append("\n")

    # Section 3: Celebrate Improvements
    improving = [
        a for a in improvement_areas if isinstance(a, dict) and a.get("trend") == "improving"
    ]
    if improving:
        plan_parts.append("## 🚀 Improving Areas (Keep It Up!)\n")
        for area in improving:
            plan_parts.append(
                f"- {area['area'].replace('_', ' ').title()}: "
                f"+{area['change']} points recently\n"
            )
        plan_parts.append("\n")

    # Section 4: Watch List
    declining = [
        a for a in improvement_areas if isinstance(a, dict) and a.get("trend") == "declining"
    ]
    if declining:
        plan_parts.append("## ⚠️  Watch List (Needs Attention)\n")
        for area in declining:
            plan_parts.append(
                f"- {area['area'].replace('_', ' ').title()}: "
                f"{area['change']} points (declining)\n"
            )
        plan_parts.append("\n")

    return "".join(plan_parts)
