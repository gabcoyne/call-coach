"""
Learning insights from top performers.

Compares rep patterns to top performers on similar closed-won opportunities.
Provides concrete behavioral examples from successful deals.

COACHING PHILOSOPHY:
- Show exactly what top performers do differently
- Use specific call examples with timestamps
- Compare behavioral patterns, not just scores
- Focus on actionable differences the rep can learn from
"""

import json
import logging
from typing import Any

import anthropic

from coaching_mcp.shared import settings
from db import queries
from db.models import CoachingDimension

logger = logging.getLogger(__name__)


def find_similar_won_opportunities(
    rep_email: str, product: str | None = None, rep_role: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """
    Find closed-won opportunities by top performers in similar product/size and same role.

    Args:
        rep_email: Email of rep to compare against
        product: Product category to filter by (optional)
        rep_role: Role to filter by (ae, se, csm) for apples-to-apples comparison (optional)
        limit: Max opportunities to return

    Returns:
        List of closed-won opportunities from similar role performers
    """
    from db import fetch_all

    filters = {
        "stage": "Closed Won",
    }

    # Add product filter if specified
    # Note: This would need product field in opportunities table
    # For now, we'll filter all closed-won deals

    won_opps, _ = queries.search_opportunities(filters=filters, limit=limit, offset=0)

    # Exclude opportunities owned by the rep being analyzed
    won_opps = [opp for opp in won_opps if opp["owner_email"] != rep_email]

    # Filter by role if specified - only compare within same role
    if rep_role:
        # Get roles for all opportunity owners
        owner_emails = [opp["owner_email"] for opp in won_opps if opp.get("owner_email")]

        if owner_emails:
            # Query staff_roles for these emails
            placeholders = ",".join(["%s"] * len(owner_emails))
            roles_query = f"SELECT email, role FROM staff_roles WHERE email IN ({placeholders})"
            role_results = fetch_all(roles_query, tuple(owner_emails))

            # Create email -> role mapping
            email_to_role = {r["email"]: r["role"] for r in role_results}

            # Filter opportunities to only those owned by same role
            won_opps = [
                opp
                for opp in won_opps
                if opp.get("owner_email") and email_to_role.get(opp["owner_email"]) == rep_role
            ]

            logger.info(
                f"Filtered to {len(won_opps)} closed-won opportunities from {rep_role.upper()} role performers"
            )

    return won_opps


def aggregate_coaching_patterns(
    opportunities: list[dict[str, Any]], focus_area: str, role_filter: str | None = None
) -> dict[str, Any]:
    """
    Aggregate coaching scores and patterns across opportunities, optionally filtered by role.

    Args:
        opportunities: List of opportunity dicts
        focus_area: Coaching dimension to focus on (discovery, objections, product_knowledge, etc.)
        role_filter: Optional role filter (ae, se, csm) to ensure comparisons are within same role

    Returns:
        Dict with aggregated patterns and scores
    """
    # Map focus area to CoachingDimension
    dimension_map = {
        "discovery": CoachingDimension.DISCOVERY,
        "objections": CoachingDimension.OBJECTION_HANDLING,
        "product_knowledge": CoachingDimension.PRODUCT_KNOWLEDGE,
        "engagement": CoachingDimension.ENGAGEMENT,
    }

    dimension = dimension_map.get(focus_area, CoachingDimension.DISCOVERY)

    patterns = {
        "opportunity_count": len(opportunities),
        "total_calls_analyzed": 0,
        "average_score": 0,
        "high_scoring_examples": [],
    }

    all_scores = []
    high_score_examples = []

    for opp in opportunities:
        # Get timeline to find calls
        timeline_items = queries.get_opportunity_timeline(opp["id"], limit=1000, offset=0)
        call_ids = [item["id"] for item in timeline_items if item["item_type"] == "call"]

        for call_id in call_ids:
            sessions = queries.get_coaching_sessions_for_call(call_id, dimension)
            if sessions:
                session = sessions[0]  # Most recent
                score = session["score"]
                all_scores.append(score)

                # Collect high-scoring examples (>80)
                if score >= 80:
                    call = queries.get_call_by_id(call_id)
                    transcript = queries.get_full_transcript(call_id)

                    high_score_examples.append(
                        {
                            "call_id": call_id,
                            "opportunity_name": opp["name"],
                            "score": score,
                            "feedback": session.get("feedback"),
                            "transcript_excerpt": transcript[:1000] if transcript else "",
                            "call_date": (
                                call["scheduled_at"].isoformat()
                                if call.get("scheduled_at")
                                else None
                            ),
                        }
                    )

    patterns["total_calls_analyzed"] = len(all_scores)
    patterns["average_score"] = sum(all_scores) / len(all_scores) if all_scores else 0
    patterns["high_scoring_examples"] = sorted(
        high_score_examples, key=lambda x: x["score"], reverse=True
    )[:5]

    return patterns


def extract_exemplar_moments(
    top_performer_patterns: dict[str, Any], focus_area: str
) -> list[dict[str, Any]]:
    """
    Identify specific high-scoring call segments from top performers.

    Args:
        top_performer_patterns: Aggregated patterns from top performers
        focus_area: Coaching dimension

    Returns:
        List of exemplar moments with timestamps and explanations
    """
    exemplars = []

    for example in top_performer_patterns.get("high_scoring_examples", [])[:3]:
        # Parse coaching feedback to extract specific moments
        exemplars.append(
            {
                "call_id": example["call_id"],
                "opportunity_name": example["opportunity_name"],
                "score": example["score"],
                "what_they_did": example["feedback"],
                "transcript_excerpt": example["transcript_excerpt"],
                "call_date": example["call_date"],
            }
        )

    return exemplars


def get_learning_insights(
    rep_email: str, focus_area: str, rep_role: str | None = None
) -> dict[str, Any]:
    """
    Compare rep's patterns to top performers in the same role and generate learning insights.

    Args:
        rep_email: Email of rep to coach
        focus_area: Area to focus on (discovery, objections, product_knowledge, etc.)
        rep_role: Optional role override. If not provided, will detect from staff_roles table.

    Returns:
        Dict with behavioral differences and concrete examples from top performers in same role
    """
    from db import fetch_one

    # Detect rep's role if not provided
    if not rep_role:
        role_result = fetch_one("SELECT role FROM staff_roles WHERE email = %s", (rep_email,))
        rep_role = role_result["role"] if role_result else "ae"  # Default to AE
        logger.info(f"Detected role for {rep_email}: {rep_role}")

    # Get rep's recent opportunities
    rep_opps, _ = queries.search_opportunities(
        filters={"owner": rep_email}, sort="updated_at", sort_dir="DESC", limit=20, offset=0
    )

    if not rep_opps:
        return {
            "error": f"No opportunities found for {rep_email}",
        }

    # Get rep's patterns
    rep_patterns = aggregate_coaching_patterns(rep_opps, focus_area, role_filter=rep_role)

    # Find similar won opportunities by top performers in SAME ROLE
    won_opps = find_similar_won_opportunities(rep_email, rep_role=rep_role, limit=50)

    if not won_opps:
        return {
            "error": f"No closed-won opportunities found from other {rep_role.upper()}s for comparison",
        }

    # Get top performer patterns (same role)
    top_performer_patterns = aggregate_coaching_patterns(won_opps, focus_area, role_filter=rep_role)

    # Extract exemplar moments
    exemplars = extract_exemplar_moments(top_performer_patterns, focus_area)

    # Use Claude to generate comparative analysis with role context
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Map role to friendly name
    role_names = {
        "ae": "Account Executive",
        "se": "Sales Engineer",
        "csm": "Customer Success Manager",
    }
    role_display = role_names.get(rep_role, rep_role.upper())

    prompt = f"""Compare this rep's patterns to top-performing {role_display}s who closed deals successfully.

REP: {rep_email}
ROLE: {role_display}
FOCUS AREA: {focus_area}

IMPORTANT: This comparison is between {role_display}s only. All examples and patterns are from other {role_display}s,
ensuring apples-to-apples comparison on role-appropriate behaviors and responsibilities.

Rep's Performance:
- Opportunities analyzed: {rep_patterns['opportunity_count']}
- Calls analyzed: {rep_patterns['total_calls_analyzed']}
- Average score: {rep_patterns['average_score']:.1f}

Top-Performing {role_display}s (Closed Won):
- Opportunities analyzed: {top_performer_patterns['opportunity_count']}
- Calls analyzed: {top_performer_patterns['total_calls_analyzed']}
- Average score: {top_performer_patterns['average_score']:.1f}

Examples from Top-Performing {role_display}s:
{json.dumps(exemplars, indent=2)}

Identify 3 CONCRETE BEHAVIORAL DIFFERENCES:
1. What top-performing {role_display}s do that this rep doesn't
2. Specific examples with timestamps/quotes from top performer calls
3. Why each behavior is effective for closing deals in the {role_display} role

BE DIRECT. Point out exactly what the rep is missing compared to other successful {role_display}s.
Use specific examples from the top performer calls. No encouragement - just show the gap and what good looks like."""

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "rep_email": rep_email,
        "rep_role": rep_role,
        "role_display": role_names.get(rep_role, rep_role.upper()),
        "focus_area": focus_area,
        "comparison_note": f"Comparing to top-performing {role_names.get(rep_role, rep_role.upper())}s only",
        "rep_performance": {
            "opportunities": rep_patterns["opportunity_count"],
            "calls": rep_patterns["total_calls_analyzed"],
            "average_score": round(rep_patterns["average_score"], 1),
        },
        "top_performer_benchmark": {
            "opportunities": top_performer_patterns["opportunity_count"],
            "calls": top_performer_patterns["total_calls_analyzed"],
            "average_score": round(top_performer_patterns["average_score"], 1),
            "note": f"All examples from {role_names.get(rep_role, rep_role.upper())}s with closed-won deals",
        },
        "behavioral_differences": response.content[0].text,
        "exemplar_moments": exemplars,
    }
