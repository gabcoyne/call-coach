"""
Narrative Generator for Five Wins Coaching

Synthesizes Five Wins evaluation into a 2-3 sentence narrative that:
1. Highlights what went well (wins addressed)
2. Identifies what's at risk (wins missed or blocked)
3. Provides a net assessment

The narrative avoids:
- Generic platitudes
- Methodology jargon
- More than 3 sentences
"""

from typing import Any

from analysis.models.five_wins import FiveWinsEvaluation
from analysis.rubrics.five_wins_unified import FIVE_WINS_UNIFIED


def generate_narrative(
    evaluation: FiveWinsEvaluation | dict[str, Any],
    call_type: str = "discovery",
) -> str:
    """
    Synthesize Five Wins evaluation into 2-3 sentence narrative.

    The narrative pattern:
    1. What went well (wins addressed/progressed)
    2. What's at risk (wins missed/blocked)
    3. Net assessment (overall trajectory)

    Args:
        evaluation: FiveWinsEvaluation model or dict with same structure
        call_type: Type of call for context

    Returns:
        2-3 sentence narrative string
    """
    # Handle both Pydantic model and dict
    if isinstance(evaluation, dict):
        wins = _extract_wins_from_dict(evaluation)
    else:
        wins = _extract_wins_from_model(evaluation)

    # Categorize wins
    addressed = []  # score >= 60
    at_risk = []  # score < 40 and has blockers
    partial = []  # 40 <= score < 60

    for name, data in wins.items():
        score = data["score"]
        blockers = data.get("blockers", [])

        if score >= 60:
            addressed.append((name, score, data.get("evidence", [])))
        elif score < 40 or blockers:
            at_risk.append((name, score, blockers))
        else:
            partial.append((name, score))

    # Build narrative
    sentences = []

    # Sentence 1: What went well
    if addressed:
        win_names = [str(FIVE_WINS_UNIFIED[name]["name"]) for name, _, _ in addressed[:2]]
        if len(addressed) == 1:
            sentences.append(f"This call made good progress on {win_names[0]}.")
        else:
            sentences.append(f"This call advanced {' and '.join(win_names)}.")
    else:
        sentences.append(
            f"This {call_type.replace('_', ' ')} call didn't clearly advance any wins."
        )

    # Sentence 2: What's at risk
    if at_risk:
        risk_details: list[str] = []
        for name, score, blockers in at_risk[:2]:
            win_name = str(FIVE_WINS_UNIFIED[name]["name"])
            if blockers:
                risk_details.append(f"{win_name} is blocked ({blockers[0]})")
            else:
                risk_details.append(f"{win_name} needs attention (score: {score})")

        if len(risk_details) == 1:
            sentences.append(f"However, {risk_details[0]}.")
        else:
            sentences.append(f"However, {risk_details[0]} and {risk_details[1]}.")

    # Sentence 3: Net assessment (only if there's something meaningful to say)
    overall_score = sum(data["score"] for data in wins.values())

    if len(at_risk) > len(addressed):
        sentences.append("The deal needs focused attention on blocked wins before progressing.")
    elif overall_score >= 70 and not at_risk:
        sentences.append("The deal is progressing well toward close.")
    elif at_risk and any(b for _, _, b in at_risk):
        # There are explicit blockers - emphasize unblocking
        pass  # The blocker message in sentence 2 is enough

    return " ".join(sentences)


def _extract_wins_from_model(evaluation: FiveWinsEvaluation) -> dict[str, dict[str, Any]]:
    """Extract win data from Pydantic model."""
    return {
        "business": {
            "score": evaluation.business.score,
            "blockers": evaluation.business.blockers,
            "evidence": evaluation.business.evidence,
        },
        "technical": {
            "score": evaluation.technical.score,
            "blockers": evaluation.technical.blockers,
            "evidence": evaluation.technical.evidence,
        },
        "security": {
            "score": evaluation.security.score,
            "blockers": evaluation.security.blockers,
            "evidence": evaluation.security.evidence,
        },
        "commercial": {
            "score": evaluation.commercial.score,
            "blockers": evaluation.commercial.blockers,
            "evidence": evaluation.commercial.evidence,
        },
        "legal": {
            "score": evaluation.legal.score,
            "blockers": evaluation.legal.blockers,
            "evidence": evaluation.legal.evidence,
        },
    }


def _extract_wins_from_dict(evaluation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract win data from raw dict (API response format)."""
    result = {}

    # Handle both new format (business, technical, etc.) and old format (business_win, etc.)
    for win_key in ["business", "technical", "security", "commercial", "legal"]:
        # Try new format first
        data = evaluation.get(win_key, {})
        if not data:
            # Try old format
            data = evaluation.get(f"{win_key}_win", {})

        result[win_key] = {
            "score": data.get("score", 0),
            "blockers": data.get("blockers", []),
            "evidence": data.get("evidence", []),
        }

    return result
