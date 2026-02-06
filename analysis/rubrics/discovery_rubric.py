"""
Discovery Rubric - Structured Criteria for Transparent Scoring

Defines the evaluation criteria for discovery skills with point allocations.
Used to generate "show your work" breakdowns in the UI.
"""

from typing import TypedDict


class RubricCriterion(TypedDict):
    """Definition of a single rubric criterion"""

    name: str  # Display name
    description: str  # What this evaluates
    max_score: int  # Maximum points
    criteria: list[str]  # Specific things to look for


# Discovery Rubric - Total: 100 points
# Based on SPICED framework + sales best practices

DISCOVERY_RUBRIC: dict[str, RubricCriterion] = {
    "opening_questions": {
        "name": "Opening Questions",
        "description": "Asks open-ended questions to understand the customer's situation",
        "max_score": 10,
        "criteria": [
            "Asks 'What brings you here today?' or similar open-ended opener",
            "Avoids leading or assumptive questions",
            "Lets customer talk first before pitching",
        ],
    },
    "situation_exploration": {
        "name": "Situation Exploration",
        "description": "Understands current state, challenges, and context",
        "max_score": 15,
        "criteria": [
            "Explores current workflow or process",
            "Asks about team size, structure, and roles",
            "Understands current tools and stack",
            "Identifies who is involved in the process",
        ],
    },
    "pain_identification": {
        "name": "Pain Identification",
        "description": "Uncovers specific pain points and challenges",
        "max_score": 15,
        "criteria": [
            "Asks about problems or frustrations with current approach",
            "Uses follow-up questions to dig deeper into pain",
            "Identifies root causes, not just symptoms",
            "Explores impact of pain on team or business",
        ],
    },
    "impact_quantification": {
        "name": "Impact Quantification",
        "description": "Quantifies the business impact and cost of problems",
        "max_score": 15,
        "criteria": [
            "Asks 'How much time does this cost you?' or similar",
            "Explores financial impact or opportunity cost",
            "Quantifies frequency or scale of problem",
            "Connects pain to business metrics (revenue, efficiency, etc.)",
        ],
    },
    "critical_event": {
        "name": "Critical Event",
        "description": "Identifies the trigger or urgency driving this conversation",
        "max_score": 10,
        "criteria": [
            "Asks 'Why now?' or 'What changed?'",
            "Explores timing and urgency",
            "Identifies forcing function or deadline",
        ],
    },
    "decision_process": {
        "name": "Decision Process",
        "description": "Understands authority, stakeholders, and approval process",
        "max_score": 15,
        "criteria": [
            "Asks who else needs to be involved in the decision",
            "Explores approval process and chain",
            "Identifies economic buyer vs technical buyer",
            "Understands decision timeline and steps",
        ],
    },
    "budget_exploration": {
        "name": "Budget & Resources",
        "description": "Explores budget, constraints, and resource allocation",
        "max_score": 10,
        "criteria": [
            "Asks about budget range or allocation",
            "Explores budget flexibility and constraints",
            "Discusses how budget decisions are made",
        ],
    },
    "success_criteria": {
        "name": "Success Criteria",
        "description": "Defines what success looks like for the customer",
        "max_score": 10,
        "criteria": [
            "Asks 'What does success look like?' or similar",
            "Explores specific outcomes or metrics",
            "Understands customer's desired end state",
            "Identifies how they'll measure ROI or value",
        ],
    },
}

# Verification: Ensure rubric adds up to 100 points
_total_points = sum(criterion["max_score"] for criterion in DISCOVERY_RUBRIC.values())
assert _total_points == 100, f"Discovery rubric must total 100 points, got {_total_points}"


def get_rubric() -> dict[str, RubricCriterion]:
    """Get the discovery rubric definition"""
    return DISCOVERY_RUBRIC


def get_total_points() -> int:
    """Get total possible points for discovery"""
    return sum(criterion["max_score"] for criterion in DISCOVERY_RUBRIC.values())


def get_criterion_names() -> list[str]:
    """Get list of criterion keys"""
    return list(DISCOVERY_RUBRIC.keys())
