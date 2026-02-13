"""
Action Selector for Five Wins Coaching

Selects the single most important action item from the Five Wins evaluation.

Priority order:
1. Unblock a blocked win (if something is stuck, fix it first)
2. Advance the primary win for this call type
3. Prevent a win from becoming at-risk

The action must:
- Reference a specific win
- Be tied to a specific call moment
- Be concrete enough to execute (not "do better discovery")
"""

from typing import Any

from analysis.models.five_wins import CallMoment, PrimaryAction
from analysis.rubrics.five_wins_unified import FIVE_WINS_UNIFIED, get_primary_win_for_call_type


def select_primary_action(
    evaluation: dict[str, Any],
    call_type: str = "discovery",
    moments: list[CallMoment] | list[dict[str, Any]] | None = None,
) -> PrimaryAction:
    """
    Select the single most important action from Five Wins evaluation.

    Priority order:
    1. Unblock blocked wins (highest priority - deals stall on blockers)
    2. Advance the primary win for this call type
    3. Prevent an at-risk win from degrading

    Args:
        evaluation: Five Wins evaluation dict from LLM
        call_type: Type of call (discovery, demo, etc.)
        moments: List of key moments from the call

    Returns:
        PrimaryAction with specific, actionable instruction
    """
    moments = moments or []

    # Convert moments to list of dicts if needed
    moment_dicts = [m if isinstance(m, dict) else m.model_dump() for m in moments]

    # Step 1: Check for blocked wins (highest priority)
    blocked_wins = _find_blocked_wins(evaluation)
    if blocked_wins:
        win_name, blocker = blocked_wins[0]
        return _create_unblock_action(win_name, blocker, moment_dicts)

    # Step 2: Advance the primary win for this call type
    primary_win = get_primary_win_for_call_type(call_type)  # type: ignore
    primary_data = _get_win_data(evaluation, primary_win)

    if primary_data and primary_data.get("score", 0) < 80:
        return _create_advance_action(primary_win, primary_data, moment_dicts, call_type)

    # Step 3: Prevent at-risk wins
    at_risk_wins = _find_at_risk_wins(evaluation)
    if at_risk_wins:
        win_name, score = at_risk_wins[0]
        win_data = _get_win_data(evaluation, win_name)
        return _create_prevent_risk_action(win_name, win_data, moment_dicts)

    # Step 4: Fallback - maintain momentum on highest-scoring win
    return _create_maintenance_action(evaluation, moment_dicts)


def _find_blocked_wins(evaluation: dict[str, Any]) -> list[tuple[str, str]]:
    """Find wins that have explicit blockers."""
    blocked = []

    for win_key in ["business", "technical", "security", "commercial", "legal"]:
        data = _get_win_data(evaluation, win_key)
        if data:
            blockers = data.get("blockers", [])
            if blockers:
                blocked.append((win_key, blockers[0]))

    # Sort by win weight (more important wins first)
    weight_order = {"business": 0, "commercial": 1, "technical": 2, "security": 3, "legal": 4}
    blocked.sort(key=lambda x: weight_order.get(x[0], 5))

    return blocked


def _find_at_risk_wins(evaluation: dict[str, Any]) -> list[tuple[str, int]]:
    """Find wins that are at risk (score < 40)."""
    at_risk = []

    for win_key in ["business", "technical", "security", "commercial", "legal"]:
        data = _get_win_data(evaluation, win_key)
        if data:
            score = data.get("score", 0)
            if score < 40:
                at_risk.append((win_key, score))

    # Sort by score (lowest first)
    at_risk.sort(key=lambda x: x[1])

    return at_risk


def _get_win_data(evaluation: dict[str, Any], win_key: str) -> dict[str, Any] | None:
    """Get win data, handling both new and old key formats."""
    # Try direct key first
    data = evaluation.get(win_key)
    if data and isinstance(data, dict):
        return dict(data)

    # Try with _win suffix
    data = evaluation.get(f"{win_key}_win")
    if data and isinstance(data, dict):
        return dict(data)

    # Try nested in five_wins_evaluation
    nested = evaluation.get("five_wins_evaluation", {})
    if isinstance(nested, dict):
        result = nested.get(win_key) or nested.get(f"{win_key}_win")
        if result and isinstance(result, dict):
            return dict(result)
    return None


def _create_unblock_action(
    win_name: str,
    blocker: str,
    moments: list[dict[str, Any]],
) -> PrimaryAction:
    """Create action to unblock a stuck win."""
    win_display = FIVE_WINS_UNIFIED[win_name]["name"]

    # Find relevant moment (one that shows the blocker)
    relevant_moment = _find_relevant_moment(moments, win_name, blocker)

    action_templates = {
        "business": f"Before your next call, prepare questions to address: {blocker}. "
        "Specifically, ask who needs to approve this, what budget is allocated, "
        "and what timeline they're working toward.",
        "technical": f"Address the technical blocker: {blocker}. "
        "Prepare a specific response or demo that resolves this concern.",
        "security": f"Proactively address security concern: {blocker}. "
        "Share our trust portal and offer to schedule an architecture review.",
        "commercial": f"Clarify commercial alignment: {blocker}. "
        "Prepare to discuss scope, pricing, and executive approval path.",
        "legal": f"Get ahead of legal concern: {blocker}. "
        "Discuss timeline expectations and any terms that might impact pricing.",
    }

    return PrimaryAction(
        win=win_name,  # type: ignore
        action=action_templates.get(win_name, f"Address blocker: {blocker}"),
        context=f"This is blocking progress on {win_display}. "
        f"Resolving it should be the priority before advancing other wins.",
        related_moment=CallMoment(**relevant_moment) if relevant_moment else None,
    )


def _create_advance_action(
    win_name: str,
    win_data: dict[str, Any],
    moments: list[dict[str, Any]],
    call_type: str,
) -> PrimaryAction:
    """Create action to advance a primary win."""
    win_display = FIVE_WINS_UNIFIED[win_name]["name"]
    discovery_topics = FIVE_WINS_UNIFIED[win_name]["discovery_topics"]

    # Find what's missing from discovery
    missing_discovery: list[str] = []
    topics_list = list(discovery_topics)[:3]  # Focus on first 3
    for topic in topics_list:
        if not win_data.get(f"{topic}_covered", False):
            missing_discovery.append(str(topic).replace("_", " "))

    relevant_moment = _find_relevant_moment(moments, win_name)

    if missing_discovery:
        action = (
            f"Before your next call, prepare questions to discover: {', '.join(missing_discovery)}."
        )
    else:
        # Win-specific advancement actions
        action_templates = {
            "business": "Prepare questions to validate your champion: "
            "What's their personal incentive? Can they move the deal? "
            "Are they sharing real org intel?",
            "technical": "Prepare to close the technical evaluation. "
            "Ask: 'Based on what you've seen, is Prefect your vendor of choice?'",
            "security": "Ask for the security review timeline and offer to share our trust portal.",
            "commercial": "Prepare to discuss scope and pricing with the executive sponsor.",
            "legal": "Ask about their standard contract process and any terms that impact pricing.",
        }
        action = action_templates.get(win_name, f"Continue advancing {win_display}.")

    return PrimaryAction(
        win=win_name,  # type: ignore
        action=action,
        context=f"This {call_type.replace('_', ' ')} should primarily advance {win_display}. "
        f"Current score: {win_data.get('score', 0)}/100.",
        related_moment=CallMoment(**relevant_moment) if relevant_moment else None,
    )


def _create_prevent_risk_action(
    win_name: str,
    win_data: dict[str, Any] | None,
    moments: list[dict[str, Any]],
) -> PrimaryAction:
    """Create action to prevent an at-risk win from degrading."""
    win_display = FIVE_WINS_UNIFIED[win_name]["name"]
    score = win_data.get("score", 0) if win_data else 0

    relevant_moment = _find_relevant_moment(moments, win_name)

    risk_actions = {
        "business": "Your business case is weak. Before the next call, "
        "quantify the impact: What's this problem costing them? "
        "What opportunities are they missing?",
        "technical": "Technical validation is at risk. "
        "Schedule a focused technical deep-dive to validate requirements.",
        "security": "Security could become a late-stage blocker. "
        "Ask about their InfoSec review process now, before it delays the deal.",
        "commercial": "Commercial alignment is unclear. "
        "Confirm there's an executive sponsor with budget authority.",
        "legal": "Legal timing is unknown. "
        "Ask about their typical contract review process and timeline.",
    }

    return PrimaryAction(
        win=win_name,  # type: ignore
        action=risk_actions.get(
            win_name, f"Focus on improving {win_display} before it becomes a blocker."
        ),
        context=f"{win_display} is at risk (score: {score}). "
        f"Address this before it delays the deal.",
        related_moment=CallMoment(**relevant_moment) if relevant_moment else None,
    )


def _create_maintenance_action(
    evaluation: dict[str, Any],
    moments: list[dict[str, Any]],
) -> PrimaryAction:
    """Fallback action when all wins are progressing well."""
    # Find the highest-scoring win
    best_win = "business"
    best_score = 0

    for win_key in ["business", "technical", "security", "commercial", "legal"]:
        data = _get_win_data(evaluation, win_key)
        if data:
            score = data.get("score", 0)
            if score > best_score:
                best_score = score
                best_win = win_key

    relevant_moment = _find_relevant_moment(moments, best_win)

    return PrimaryAction(
        win=best_win,  # type: ignore
        action=f"Great progress! To close {FIVE_WINS_UNIFIED[best_win]['name']}, "
        f"confirm exit criteria: {FIVE_WINS_UNIFIED[best_win]['exit_criteria']}",
        context="All wins are progressing well. Focus on securing the strongest win first.",
        related_moment=CallMoment(**relevant_moment) if relevant_moment else None,
    )


def _find_relevant_moment(
    moments: list[dict[str, Any]],
    win_name: str,
    keyword: str | None = None,
) -> dict[str, Any] | None:
    """Find the most relevant moment for a given win."""
    if not moments:
        return None

    # Score each moment for relevance
    best_moment = None
    best_score = -1

    for moment in moments:
        score = 0
        summary = moment.get("summary", "").lower()

        # Check for win name relevance
        if win_name in summary:
            score += 2

        # Check for keyword match
        if keyword and keyword.lower() in summary:
            score += 3

        # Prefer moments with issues/missed opportunities
        negative_indicators = ["missed", "didn't", "failed", "no ", "lack", "without"]
        if any(ind in summary for ind in negative_indicators):
            score += 1

        if score > best_score:
            best_score = score
            best_moment = moment

    return best_moment if best_score > 0 else (moments[0] if moments else None)
