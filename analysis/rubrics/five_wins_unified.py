"""
Five Wins Unified Rubric - Single Source of Truth

This module defines the Five Wins framework used for all sales coaching at Prefect.
It replaces fragmented methodology-specific rubrics (SPICED, Challenger, Sandler, MEDDIC)
with a unified evaluation framework focused on what it takes to close a deal.

The Five Wins:
1. Business Win (35%) - Budget and resources allocated to evaluate/implement
2. Technical Win (25%) - Vendor of choice from technical evaluators
3. Security Win (15%) - InfoSec/Architecture approval
4. Commercial Win (15%) - Exec sponsor approval on scope and commercials
5. Legal Win (10%) - Contract signed

Key principles:
- No methodology jargon in coaching output
- Focus on exit criteria, not process
- One actionable recommendation per call
- Feedback tied to specific call moments
"""

from typing import Any, Literal

# Type aliases for clarity
WinName = Literal["business", "technical", "security", "commercial", "legal"]
CallType = Literal[
    "discovery",
    "technical_deep_dive",
    "demo",
    "poc_kickoff",
    "architecture_review",
    "executive_presentation",
    "negotiation",
]


FIVE_WINS_UNIFIED: dict[str, dict[str, Any]] = {
    "business": {
        "name": "Business Win",
        "weight": 35,
        "exit_criteria": "Budget and resources allocated to evaluate and implement a solution",
        "discovery_topics": [
            "current_state",
            "pain_points",
            "future_state",
            "success_metrics",
            "executive_priorities",
            "evaluation_process",
            "decision_process",
        ],
        "what_good_looks_like": [
            "Discovery covers: current state, pain, future state, success metrics, executive priorities",
            "Business case answers: Why change? Why Prefect? Why now?",
            "Champion identified and tested (incentive, influence, information)",
            "Executive sponsor engaged",
            "Budget confirmed",
        ],
        "champion_criteria": {
            "incentive": "What's in it for them personally?",
            "influence": "Can they actually move the deal forward?",
            "information": "Are they giving you real intel about the org?",
        },
        "business_case_questions": {
            "why_change": "What happens if they don't solve this problem?",
            "why_prefect": "Why is Prefect the right solution vs alternatives?",
            "why_now": "What's driving the timeline? What's the cost of delay?",
        },
        "coaching_focus": "Did the rep advance toward exit criteria? What's blocking?",
    },
    "technical": {
        "name": "Technical Win",
        "weight": 25,
        "exit_criteria": "Received 'vendor of choice' from technical evaluators",
        "discovery_topics": [
            "technical_requirements",
            "use_case_alignment",
            "infrastructure",
            "ci_cd_integration",
            "current_tooling",
        ],
        "what_good_looks_like": [
            "Technical discovery complete: requirements, use case alignment, infrastructure, CI/CD",
            "Demo tailored to business AND technical discovery findings",
            "POC scoped with defined timeline and success criteria",
            "Explicit confirmation received (not passive approval)",
        ],
        "coaching_focus": "Is the technical evaluation progressing? Is the POC scoped or open-ended?",
    },
    "security": {
        "name": "Security Win",
        "weight": 15,
        "exit_criteria": "InfoSec/Architecture gives formal approval",
        "discovery_topics": [
            "infosec_requirements",
            "compliance_needs",
            "review_process",
            "timeline",
            "questionnaire_needs",
        ],
        "what_good_looks_like": [
            "Discovery covers: InfoSec requirements, review process, timeline, questionnaire needs",
            "Trust portal shared proactively",
            "Architecture review scheduled/completed",
            "Formal sign-off received",
        ],
        "coaching_focus": "Is security review on track? Will it become a late-stage blocker?",
    },
    "commercial": {
        "name": "Commercial Win",
        "weight": 15,
        "exit_criteria": "Executive sponsor gives final approval on scope and commercials",
        "discovery_topics": [
            "deployment_scope",
            "usage_requirements",
            "support_level",
            "pricing_preferences",
        ],
        "what_good_looks_like": [
            "Discovery covers: required scope, usage, support level",
            "EB alignment on: scope, implementation plan, adoption plan, pricing",
            "Agreement confirmed by exec sponsor (not just mid-level manager)",
        ],
        "coaching_focus": "Is there real executive sponsorship? Are commercial terms aligned?",
    },
    "legal": {
        "name": "Legal Win",
        "weight": 10,
        "exit_criteria": "Contract signed",
        "discovery_topics": [
            "required_terms",
            "legal_lead_time",
            "review_intensity",
            "procurement_process",
        ],
        "what_good_looks_like": [
            "Discovery covers: required terms, legal lead time, review intensity",
            "Upfront expectation set on terms that impact price",
            "Redlines managed efficiently",
            "Mutual language reached, contract signed",
        ],
        "coaching_focus": "Is legal on track? Were price-impacting terms discussed early?",
    },
}


# Map call types to primary win (what this call should advance)
CALL_TYPE_TO_PRIMARY_WIN: dict[CallType, WinName] = {
    "discovery": "business",
    "technical_deep_dive": "technical",
    "demo": "technical",
    "poc_kickoff": "technical",
    "architecture_review": "security",
    "executive_presentation": "business",
    "negotiation": "commercial",
}

# Map call types to secondary wins (can be seeded during this call)
CALL_TYPE_TO_SECONDARY_WINS: dict[CallType, list[WinName]] = {
    "discovery": ["technical", "security", "legal"],  # Seed questions for later
    "technical_deep_dive": ["business"],  # Keep business context
    "demo": ["business"],  # Reinforce business value
    "poc_kickoff": ["security"],  # Often surfaces security needs
    "architecture_review": ["technical"],  # Tech implications
    "executive_presentation": ["commercial"],  # Budget/pricing alignment
    "negotiation": ["legal"],  # Contract terms
}


def get_rubric() -> dict[str, dict[str, Any]]:
    """Get the unified Five Wins rubric."""
    return FIVE_WINS_UNIFIED


def get_win(win_name: WinName) -> dict[str, Any]:
    """Get a specific win definition."""
    return FIVE_WINS_UNIFIED[win_name]


def get_weights() -> dict[str, int]:
    """Get the weight for each win."""
    return {name: int(win["weight"]) for name, win in FIVE_WINS_UNIFIED.items()}


def get_primary_win_for_call_type(call_type: CallType) -> str:
    """Get the primary win to advance for a given call type."""
    return CALL_TYPE_TO_PRIMARY_WIN.get(call_type, "business")


def get_secondary_wins_for_call_type(call_type: CallType) -> list[str]:
    """Get secondary wins to seed for a given call type."""
    return list(CALL_TYPE_TO_SECONDARY_WINS.get(call_type, []))


def get_exit_criteria(win_name: WinName) -> str:
    """Get the exit criteria for a specific win."""
    return str(FIVE_WINS_UNIFIED[win_name]["exit_criteria"])


def get_discovery_topics(win_name: WinName) -> list[str]:
    """Get the discovery topics for a specific win."""
    return list(FIVE_WINS_UNIFIED[win_name]["discovery_topics"])


def get_coaching_focus(win_name: WinName) -> str:
    """Get the coaching focus question for a specific win."""
    return str(FIVE_WINS_UNIFIED[win_name]["coaching_focus"])


# Verification: weights must sum to 100
_total_weight = sum(int(win["weight"]) for win in FIVE_WINS_UNIFIED.values())
assert _total_weight == 100, f"Five Wins weights must total 100, got {_total_weight}"
