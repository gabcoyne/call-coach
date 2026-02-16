"""
Opportunity-level coaching analysis.

Analyzes patterns across all calls and emails for an opportunity to provide
holistic coaching insights. Focuses on deal progression, recurring themes,
objection handling, and relationship strength.

COACHING PHILOSOPHY:
- Be DIRECT about specific problems with timestamps
- Compare to top performers on closed-won deals
- NO encouragement language - focus on gaps and fixes
- Provide actionable behavioral changes only
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any

import anthropic

from coaching_mcp.shared import settings
from db import queries
from db.models import CoachingDimension

logger = logging.getLogger(__name__)

# Cache TTL for opportunity analysis (7 days - refreshes after new calls)
OPPORTUNITY_CACHE_TTL_DAYS = 7


def _get_opportunity_cache_key(opportunity_id: str, analysis_type: str) -> str:
    """
    Generate cache key for opportunity-level analysis.

    The key includes all call IDs associated with the opportunity, so the cache
    automatically invalidates when new calls are added.

    Args:
        opportunity_id: Opportunity UUID
        analysis_type: Type of analysis (patterns, themes, objections, relationship, recommendations)

    Returns:
        SHA256 hash-based cache key
    """
    # Get all call IDs for this opportunity to include in cache key
    timeline_items = queries.get_opportunity_timeline(opportunity_id, limit=1000, offset=0)
    call_ids = sorted([item["id"] for item in timeline_items if item["item_type"] == "call"])

    # Include call IDs in the key so cache invalidates when calls change
    key_components = f"{opportunity_id}:{analysis_type}:{','.join(str(cid) for cid in call_ids)}"
    return hashlib.sha256(key_components.encode("utf-8")).hexdigest()


def _get_cached_analysis(cache_key: str) -> dict[str, Any] | None:
    """
    Retrieve cached opportunity analysis if valid.

    Args:
        cache_key: Cache key from _get_opportunity_cache_key

    Returns:
        Cached analysis result or None if not found/expired
    """
    try:
        cached = queries.get_opportunity_analysis_cache(cache_key)
        if cached:
            # Check TTL
            cached_at = cached.get("cached_at")
            if cached_at:
                expiry = cached_at + timedelta(days=OPPORTUNITY_CACHE_TTL_DAYS)
                if datetime.utcnow() < expiry:
                    logger.info(f"Cache HIT for opportunity analysis: {cache_key[:16]}...")
                    result = cached.get("analysis_result")
                    if isinstance(result, dict):
                        return result
                    return None
                else:
                    logger.info(f"Cache EXPIRED for opportunity analysis: {cache_key[:16]}...")
        return None
    except Exception as e:
        logger.warning(f"Failed to retrieve opportunity cache: {e}")
        return None


def _set_cached_analysis(
    cache_key: str,
    opportunity_id: str,
    analysis_type: str,
    result: dict[str, Any] | list[str],
) -> None:
    """
    Store opportunity analysis in cache.

    Args:
        cache_key: Cache key from _get_opportunity_cache_key
        opportunity_id: Opportunity UUID
        analysis_type: Type of analysis
        result: Analysis result to cache
    """
    try:
        queries.set_opportunity_analysis_cache(
            cache_key=cache_key,
            opportunity_id=opportunity_id,
            analysis_type=analysis_type,
            analysis_result=result,
        )
        logger.info(f"Cached opportunity analysis: {cache_key[:16]}... type={analysis_type}")
    except Exception as e:
        logger.warning(f"Failed to cache opportunity analysis: {e}")


def detect_speaker_role(call_id: str) -> str:
    """
    Detect the role of the primary Prefect speaker on a call.

    Identifies Prefect staff by @prefect.io email domain, selects primary speaker
    by talk time, and looks up their assigned role.

    Args:
        call_id: Call UUID

    Returns:
        Role identifier ('ae', 'se', 'csm'). Defaults to 'ae' if no role assigned.
    """
    # Get all speakers for the call
    speakers = queries.get_speakers_for_call(call_id)  # type: ignore[arg-type]

    # Filter to Prefect speakers (company_side=true and @prefect.io email)
    prefect_speakers = [
        s
        for s in speakers
        if s.get("company_side") and s.get("email") and s["email"].endswith("@prefect.io")
    ]

    if not prefect_speakers:
        logger.info(f"No Prefect speakers found for call {call_id}, defaulting to AE rubric")
        return "ae"

    # Select primary speaker (highest talk time)
    primary_speaker = max(prefect_speakers, key=lambda s: s.get("talk_time_percentage", 0) or 0)

    speaker_email = primary_speaker["email"]
    logger.info(
        f"Primary Prefect speaker on call {call_id}: {speaker_email} "
        f"({primary_speaker.get('talk_time_percentage', 0)}% talk time)"
    )

    # Look up role assignment
    role = queries.get_staff_role(speaker_email)

    if role:
        logger.info(f"Speaker {speaker_email} has assigned role: {role}")
    else:
        logger.info(f"No role assigned for {speaker_email}, defaulting to 'ae'")
        role = "ae"

    return role


def analyze_opportunity_patterns(opportunity_id: str, use_cache: bool = True) -> dict[str, Any]:
    """
    Aggregate coaching scores across all calls for an opportunity.

    Args:
        opportunity_id: Opportunity UUID
        use_cache: Whether to use cached results (default True)

    Returns:
        Dict with average scores per dimension and trend lines
    """
    # Check cache first
    if use_cache:
        cache_key = _get_opportunity_cache_key(opportunity_id, "patterns")
        cached = _get_cached_analysis(cache_key)
        if cached:
            return cached

    # Get opportunity and all associated calls
    opp = queries.get_opportunity(opportunity_id)
    if not opp:
        raise ValueError(f"Opportunity not found: {opportunity_id}")

    # Get timeline to find all calls
    timeline_items, _ = queries.search_opportunities(limit=1000, offset=0)
    call_ids = [
        item["id"]
        for item in queries.get_opportunity_timeline(opportunity_id, limit=1000, offset=0)
        if item["item_type"] == "call"
    ]

    if not call_ids:
        return {
            "average_scores": {},
            "trends": {},
            "call_count": 0,
            "message": "No calls found for this opportunity",
        }

    # Aggregate coaching scores by dimension
    dimension_scores = {}
    for dimension in CoachingDimension:
        scores_over_time = []

        for call_id in call_ids:
            sessions = queries.get_coaching_sessions_for_call(call_id, dimension)
            if sessions:
                # Get most recent session for this call/dimension
                latest_session = sessions[0]
                scores_over_time.append(
                    {
                        "call_id": call_id,
                        "score": latest_session["score"],
                        "timestamp": latest_session["created_at"],
                    }
                )

        if scores_over_time:
            # Calculate average and trend
            scores = [s["score"] for s in scores_over_time]
            avg_score = sum(scores) / len(scores)

            # Determine trend (improving/declining/stable)
            if len(scores) >= 2:
                first_half_avg = sum(scores[: len(scores) // 2]) / (len(scores) // 2)
                second_half_avg = sum(scores[len(scores) // 2 :]) / (len(scores) - len(scores) // 2)
                score_delta = second_half_avg - first_half_avg

                if score_delta > 5:
                    trend = "improving"
                elif score_delta < -5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"

            dimension_scores[dimension.value] = {
                "average": avg_score,
                "trend": trend,
                "data_points": len(scores),
                "scores_over_time": scores_over_time,
            }

    result = {
        "opportunity_id": opportunity_id,
        "opportunity_name": opp["name"],
        "call_count": len(call_ids),
        "average_scores": dimension_scores,
    }

    # Cache the result
    if use_cache:
        _set_cached_analysis(cache_key, opportunity_id, "patterns", result)

    return result


def identify_recurring_themes(opportunity_id: str, use_cache: bool = True) -> dict[str, Any]:
    """
    Use Claude to find patterns in transcripts across all calls.

    Args:
        opportunity_id: Opportunity UUID
        use_cache: Whether to use cached results (default True)

    Returns:
        Dict with recurring themes and their evolution over time
    """
    # Check cache first (expensive Claude call)
    if use_cache:
        cache_key = _get_opportunity_cache_key(opportunity_id, "themes")
        cached = _get_cached_analysis(cache_key)
        if cached:
            return cached

    # Get all call transcripts for opportunity
    timeline_items = queries.get_opportunity_timeline(opportunity_id, limit=1000, offset=0)
    call_ids = [item["id"] for item in timeline_items if item["item_type"] == "call"]

    if not call_ids:
        return {"themes": [], "message": "No calls found"}

    # Gather transcripts
    transcripts_data = []
    for call_id in call_ids:
        transcript = queries.get_full_transcript(call_id)
        call = queries.get_call_by_id(call_id)
        if transcript and call:
            transcripts_data.append(
                {
                    "call_id": call_id,
                    "date": (
                        call["scheduled_at"].isoformat() if call.get("scheduled_at") else "unknown"
                    ),
                    "transcript": transcript[:5000],  # Limit length
                }
            )

    # Use Claude to analyze themes
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = f"""Analyze these sales call transcripts for an opportunity. Identify recurring themes, topics, and concerns that appear across multiple calls.

Calls (in chronological order):
{json.dumps(transcripts_data, indent=2)}

Identify:
1. Recurring discussion topics across calls
2. Customer concerns or objections that appear multiple times
3. How topics evolve over time (new topics vs resolved topics)

BE DIRECT. State exactly what was discussed and how it changed over time. No encouragement or positive spin."""

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    result = {
        "themes": response.content[0].text,
        "call_count": len(call_ids),
    }

    # Cache the result
    if use_cache:
        _set_cached_analysis(cache_key, opportunity_id, "themes", result)

    return result


def analyze_objection_progression(opportunity_id: str, use_cache: bool = True) -> dict[str, Any]:
    """
    Track objections across the opportunity timeline.

    Args:
        opportunity_id: Opportunity UUID
        use_cache: Whether to use cached results (default True)

    Returns:
        Dict with objections, resolution status, and persistence
    """
    # Check cache first
    if use_cache:
        cache_key = _get_opportunity_cache_key(opportunity_id, "objections")
        cached = _get_cached_analysis(cache_key)
        if cached:
            return cached

    # Get coaching sessions focused on objections
    timeline_items = queries.get_opportunity_timeline(opportunity_id, limit=1000, offset=0)
    call_ids = [item["id"] for item in timeline_items if item["item_type"] == "call"]

    objections_by_call = []
    for call_id in call_ids:
        sessions = queries.get_coaching_sessions_for_call(
            call_id, CoachingDimension.OBJECTION_HANDLING
        )
        call_data = queries.get_call_by_id(call_id)

        if sessions:
            session = sessions[0]  # Most recent
            objections_by_call.append(
                {
                    "call_id": call_id,
                    "call_date": (
                        call_data["scheduled_at"].isoformat()
                        if call_data.get("scheduled_at")
                        else None
                    ),
                    "score": session["score"],
                    "feedback": session.get("feedback"),
                }
            )

    # Use Claude to identify patterns
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = f"""Analyze objection handling patterns across these sales calls:

{json.dumps(objections_by_call, indent=2)}

Identify:
1. Which objections keep recurring (not being resolved)
2. Which objections were successfully addressed and don't reappear
3. Specific coaching feedback that points to persistent problems

BE DIRECT. Point out exactly which objections the rep is failing to resolve and how many times they reappear. No sugarcoating."""

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    result = {
        "objection_analysis": response.content[0].text,
        "calls_analyzed": len(objections_by_call),
    }

    # Cache the result
    if use_cache:
        _set_cached_analysis(cache_key, opportunity_id, "objections", result)

    return result


def assess_relationship_strength(opportunity_id: str, use_cache: bool = True) -> dict[str, Any]:
    """
    Evaluate rapport and engagement trends over time.

    Args:
        opportunity_id: Opportunity UUID
        use_cache: Whether to use cached results (default True)

    Returns:
        Dict with relationship strength assessment and trends
    """
    # Check cache first
    if use_cache:
        cache_key = _get_opportunity_cache_key(opportunity_id, "relationship")
        cached = _get_cached_analysis(cache_key)
        if cached:
            return cached

    timeline_items = queries.get_opportunity_timeline(opportunity_id, limit=1000, offset=0)

    # Collect engagement metrics
    calls = [item for item in timeline_items if item["item_type"] == "call"]
    emails = [item for item in timeline_items if item["item_type"] == "email"]

    # Analyze call duration trends
    call_durations = []
    for call_item in calls:
        call = queries.get_call_by_id(call_item["id"])
        if call and call.get("duration"):
            call_durations.append(
                {
                    "date": call["scheduled_at"].isoformat() if call.get("scheduled_at") else None,
                    "duration": call["duration"],
                }
            )

    # Analyze email frequency
    email_frequency = len(emails) / max(len(calls), 1) if calls else 0

    # Determine trend
    if len(call_durations) >= 2:
        early_avg = sum([c["duration"] for c in call_durations[: len(call_durations) // 2]]) / (
            len(call_durations) // 2
        )
        recent_avg = sum([c["duration"] for c in call_durations[len(call_durations) // 2 :]]) / (
            len(call_durations) - len(call_durations) // 2
        )

        if recent_avg > early_avg * 1.2:
            trend = "strengthening"
        elif recent_avg < early_avg * 0.8:
            trend = "weakening"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    result = {
        "call_count": len(calls),
        "email_count": len(emails),
        "email_to_call_ratio": round(email_frequency, 2),
        "call_duration_trend": trend,
        "call_durations": call_durations,
    }

    # Cache the result
    if use_cache:
        _set_cached_analysis(cache_key, opportunity_id, "relationship", result)

    return result


def generate_coaching_recommendations(opportunity_id: str, use_cache: bool = True) -> list[str]:
    """
    Generate specific coaching recommendations for next steps.

    Args:
        opportunity_id: Opportunity UUID
        use_cache: Whether to use cached results (default True)

    Returns:
        List of 3-5 actionable coaching recommendations
    """
    # Check cache first
    if use_cache:
        cache_key = _get_opportunity_cache_key(opportunity_id, "recommendations")
        cached = _get_cached_analysis(cache_key)
        if cached and isinstance(cached, list):
            return cached  # type: ignore[return-value]

    # Gather all analysis data (use cache for sub-analyses)
    patterns = analyze_opportunity_patterns(opportunity_id, use_cache=use_cache)
    themes = identify_recurring_themes(opportunity_id, use_cache=use_cache)
    objections = analyze_objection_progression(opportunity_id, use_cache=use_cache)
    relationship = assess_relationship_strength(opportunity_id, use_cache=use_cache)

    # Use Claude to synthesize recommendations
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = f"""Based on this opportunity analysis, generate 3-5 specific coaching recommendations for the next customer interaction.

Coaching Score Patterns:
{json.dumps(patterns, indent=2, default=str)}

Recurring Themes:
{themes['themes']}

Objection Patterns:
{objections['objection_analysis']}

Relationship Strength:
{json.dumps(relationship, indent=2)}

Provide DIRECT, ACTIONABLE recommendations:
- Focus on specific gaps and problems
- Reference exact patterns from the data
- Tell the rep exactly what behavior to change
- No encouragement, just fixes

Format as a numbered list of 3-5 recommendations."""

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    recommendations_text = response.content[0].text

    # Parse into list
    recommendations = [
        line.strip()
        for line in recommendations_text.split("\n")
        if line.strip() and line[0].isdigit()
    ]

    # Cache the result
    if use_cache:
        _set_cached_analysis(cache_key, opportunity_id, "recommendations", recommendations)

    return recommendations
