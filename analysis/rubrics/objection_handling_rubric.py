"""
Objection Handling Rubric - Supplementary Framework

This rubric evaluates how well the rep addresses customer concerns,
objections, and potential blockers.

Total: 100 points distributed across objection management dimensions.
"""

from typing import TypedDict


class RubricCriterion(TypedDict):
    """Definition of a single rubric criterion"""

    name: str
    description: str
    max_score: int
    criteria: list[str]


# Objection Handling Rubric - Total: 100 points
# Used when calls include customer objections or concerns

OBJECTION_HANDLING_RUBRIC: dict[str, RubricCriterion] = {
    "objection_identification": {
        "name": "Objection Identification",
        "description": "Rep recognizes and surfaces objections early",
        "max_score": 15,
        "criteria": [
            "Proactively asks about concerns",
            "Picks up on hesitation or uncertainty signals",
            "Creates safe space for customer to voice concerns",
            "Doesn't brush past or ignore objections",
        ],
    },
    "understanding_root_cause": {
        "name": "Understanding Root Cause",
        "description": "Rep digs into the underlying concern behind the objection",
        "max_score": 20,
        "criteria": [
            "Asks clarifying questions to understand the real issue",
            "Doesn't assume what the objection means",
            "Validates understanding with customer",
            "Identifies if objection is a blocker or preference",
        ],
    },
    "empathy_and_validation": {
        "name": "Empathy and Validation",
        "description": "Rep shows understanding and validates customer's concerns",
        "max_score": 15,
        "criteria": [
            "Acknowledges the concern without being defensive",
            "Shows empathy and understanding",
            "Shares how other customers had similar concerns",
            "Validates that concern is reasonable",
        ],
    },
    "reframing_response": {
        "name": "Reframing Response",
        "description": "Rep addresses objection with data, examples, or alternative perspective",
        "max_score": 25,
        "criteria": [
            "Provides evidence (data, examples, case studies)",
            "Reframes concern in a new light when appropriate",
            "Offers concrete solutions or workarounds",
            "Ties response back to customer's goals",
        ],
    },
    "confirmation_and_resolution": {
        "name": "Confirmation and Resolution",
        "description": "Rep confirms the objection is resolved or has a clear path forward",
        "max_score": 15,
        "criteria": [
            "Checks if the response addressed the concern",
            "Doesn't assume objection is resolved without confirmation",
            "Agrees on next steps if concern remains",
            "Documents unresolved concerns for follow-up",
        ],
    },
    "handling_difficult_objections": {
        "name": "Handling Difficult Objections",
        "description": "Rep manages pricing, timing, or competitive objections effectively",
        "max_score": 10,
        "criteria": [
            "Pricing objections: focuses on value, not just cost",
            "Timing objections: uncovers urgency or creates it",
            "Competitive objections: differentiates without disparaging",
            "Authority objections: navigates to decision-maker",
        ],
    },
}

# Verification
_total_points = sum(criterion["max_score"] for criterion in OBJECTION_HANDLING_RUBRIC.values())
assert _total_points == 100, f"Objection Handling rubric must total 100 points, got {_total_points}"


def get_rubric() -> dict[str, RubricCriterion]:
    """Get the Objection Handling rubric definition"""
    return OBJECTION_HANDLING_RUBRIC


def get_total_points() -> int:
    """Get total possible points for Objection Handling"""
    return sum(criterion["max_score"] for criterion in OBJECTION_HANDLING_RUBRIC.values())


def get_criterion_names() -> list[str]:
    """Get list of criterion keys"""
    return list(OBJECTION_HANDLING_RUBRIC.keys())


def get_criteria_by_importance() -> list[tuple[str, int]]:
    """Get criteria sorted by point value (importance)"""
    return sorted(
        [
            (criterion, details["max_score"])
            for criterion, details in OBJECTION_HANDLING_RUBRIC.items()
        ],
        key=lambda x: x[1],
        reverse=True,
    )
