"""
Moment Linker for Five Wins Coaching

Links coaching actions to specific moments in the call transcript.
This creates the connection between "what to do" and "what happened
in the call that makes this important."

Key principles:
1. Prefer moments showing missed opportunities
2. Include accurate timestamp and speaker
3. Keep summaries concise and relevant
"""

from typing import Any

from analysis.models.five_wins import CallMoment


def link_action_to_moment(
    action: str,
    win: str,
    moments: list[CallMoment] | list[dict[str, Any]],
) -> CallMoment | None:
    """
    Find the call moment most relevant to a coaching action.

    This creates the connection between "what to do" and
    "what happened in the call that makes this important."

    Args:
        action: The action text to link
        win: The win this action relates to
        moments: List of key moments from the call

    Returns:
        Most relevant CallMoment or None if no good match
    """
    if not moments:
        return None

    # Convert to list of dicts for processing
    moment_dicts = [m if isinstance(m, dict) else m.model_dump() for m in moments]

    # Score each moment for relevance
    scored_moments = []
    for moment in moment_dicts:
        score = _score_moment_relevance(moment, action, win)
        scored_moments.append((moment, score))

    # Sort by score descending
    scored_moments.sort(key=lambda x: x[1], reverse=True)

    # Return best match if score > 0
    if scored_moments and scored_moments[0][1] > 0:
        best = scored_moments[0][0]
        return CallMoment(
            timestamp_seconds=best.get("timestamp_seconds", 0),
            speaker=best.get("speaker", "Unknown"),
            summary=best.get("summary", ""),
        )

    # Fallback to first moment if nothing matches
    if moment_dicts:
        first = moment_dicts[0]
        return CallMoment(
            timestamp_seconds=first.get("timestamp_seconds", 0),
            speaker=first.get("speaker", "Unknown"),
            summary=first.get("summary", ""),
        )

    return None


def extract_moments_from_transcript(
    transcript_segments: list[dict[str, Any]],
    five_wins_evaluation: dict[str, Any],
    limit: int = 5,
) -> list[CallMoment]:
    """
    Extract key moments from transcript based on Five Wins evaluation.

    Looks for moments that:
    1. Correspond to evidence cited in the evaluation
    2. Show missed opportunities
    3. Represent turning points in the conversation

    Args:
        transcript_segments: List of transcript segments with timestamp, speaker, text
        five_wins_evaluation: Five Wins evaluation results
        limit: Maximum moments to return

    Returns:
        List of key CallMoments
    """
    moments = []

    # Collect all evidence and blockers from evaluation
    evidence_snippets = []
    for win_key in ["business", "technical", "security", "commercial", "legal"]:
        win_data = five_wins_evaluation.get(win_key, {})
        if not win_data:
            win_data = five_wins_evaluation.get(f"{win_key}_win", {})

        # Collect evidence
        evidence = win_data.get("evidence", [])
        if isinstance(evidence, list):
            evidence_snippets.extend(evidence)

        # Collect blockers (these indicate problem moments)
        blockers = win_data.get("blockers", [])
        if isinstance(blockers, list):
            evidence_snippets.extend(blockers)

    # Find transcript segments that match evidence
    for segment in transcript_segments:
        text = segment.get("text", "")
        timestamp_ms = segment.get("start_time_ms", 0)
        speaker = segment.get("speaker", "Unknown")

        # Check if this segment is mentioned in evidence
        relevance_score = 0
        matched_evidence = None

        for evidence in evidence_snippets:
            if not isinstance(evidence, str):
                continue

            # Check for partial match (evidence might be summarized)
            evidence_lower = evidence.lower()
            text_lower = text.lower()

            # Check key phrases overlap
            evidence_words = set(evidence_lower.split())
            text_words = set(text_lower.split())
            overlap = len(evidence_words & text_words)

            if overlap > 3:  # At least 3 words match
                relevance_score = overlap
                matched_evidence = evidence
                break

        if relevance_score > 0:
            moments.append(
                CallMoment(
                    timestamp_seconds=timestamp_ms // 1000,
                    speaker=speaker,
                    summary=_summarize_segment(text, matched_evidence),
                )
            )

    # Deduplicate by timestamp proximity (within 30 seconds)
    deduplicated = _deduplicate_moments(moments)

    # Return top N by relevance (earlier moments with good content)
    return deduplicated[:limit]


def _score_moment_relevance(
    moment: dict[str, Any],
    action: str,
    win: str,
) -> int:
    """Score how relevant a moment is to an action."""
    score = 0
    summary = moment.get("summary", "").lower()
    action_lower = action.lower()

    # Win name in summary
    if win.lower() in summary:
        score += 3

    # Win-related keywords
    win_keywords = {
        "business": ["budget", "roi", "champion", "sponsor", "executive", "decision"],
        "technical": ["technical", "requirements", "poc", "demo", "architecture", "infrastructure"],
        "security": ["security", "infosec", "compliance", "soc2", "review", "approval"],
        "commercial": ["pricing", "scope", "commercial", "terms", "contract"],
        "legal": ["legal", "contract", "redlines", "procurement", "terms"],
    }

    for keyword in win_keywords.get(win, []):
        if keyword in summary:
            score += 1

    # Action keywords in summary
    action_words = set(action_lower.split())
    summary_words = set(summary.split())
    word_overlap = len(action_words & summary_words)
    score += word_overlap

    # Prefer moments showing problems (more teachable)
    negative_keywords = ["missed", "didn't", "failed", "no ", "without", "skipped", "forgot"]
    if any(neg in summary for neg in negative_keywords):
        score += 2

    return score


def _summarize_segment(text: str, evidence: str | None) -> str:
    """Create a brief summary of a transcript segment."""
    # Use evidence if available, otherwise truncate text
    if evidence and len(evidence) < 150:
        return evidence

    # Truncate long text
    if len(text) > 150:
        return text[:147] + "..."

    return text


def _deduplicate_moments(moments: list[CallMoment]) -> list[CallMoment]:
    """Remove moments that are too close together in time."""
    if not moments:
        return []

    # Sort by timestamp
    sorted_moments = sorted(moments, key=lambda m: m.timestamp_seconds)

    deduplicated = [sorted_moments[0]]
    for moment in sorted_moments[1:]:
        # Only add if at least 30 seconds from previous
        if moment.timestamp_seconds - deduplicated[-1].timestamp_seconds >= 30:
            deduplicated.append(moment)

    return deduplicated
