"""
Engagement Rubric - Structured Criteria for Transparent Scoring

Defines evaluation criteria for engagement and rapport-building with point allocations.
"""

from typing import TypedDict


class RubricCriterion(TypedDict):
    """Definition of a single rubric criterion"""

    name: str
    description: str
    max_score: int
    criteria: list[str]


# Engagement Rubric - Total: 100 points
# Evaluates rapport, listening, energy, and customer-centricity

ENGAGEMENT_RUBRIC: dict[str, RubricCriterion] = {
    "talk_listen_ratio": {
        "name": "Talk-Listen Ratio",
        "description": "Balances talking vs listening appropriately for call type",
        "max_score": 20,
        "criteria": [
            "Discovery: Rep talks 20-30%, customer talks 70-80%",
            "Demo: Rep talks 40-50%, customer talks 50-60%",
            "Avoids monologuing or over-explaining",
            "Leaves space for customer to think and respond",
        ],
    },
    "active_listening": {
        "name": "Active Listening",
        "description": "Demonstrates genuine listening through responses and follow-ups",
        "max_score": 20,
        "criteria": [
            "Paraphrases or summarizes customer statements",
            "Asks follow-up questions based on what customer said",
            "References earlier points customer made",
            "Doesn't interrupt or talk over customer",
        ],
    },
    "rapport_building": {
        "name": "Rapport Building",
        "description": "Creates personal connection and trust with customer",
        "max_score": 15,
        "criteria": [
            "Uses customer's name naturally",
            "Finds common ground or shared experiences",
            "Shows genuine curiosity about customer's work",
            "Maintains friendly, conversational tone",
        ],
    },
    "energy_enthusiasm": {
        "name": "Energy & Enthusiasm",
        "description": "Maintains positive energy that engages without overwhelming",
        "max_score": 15,
        "criteria": [
            "Vocal energy matches customer's energy level",
            "Sounds genuinely interested and engaged",
            "Avoids monotone or low-energy delivery",
            "Enthusiasm feels authentic, not forced",
        ],
    },
    "empathy_validation": {
        "name": "Empathy & Validation",
        "description": "Acknowledges customer's challenges and feelings",
        "max_score": 15,
        "criteria": [
            "Validates customer frustrations or concerns",
            "Shows understanding of their situation",
            "Uses empathetic language ('I can see how that would be frustrating')",
            "Doesn't dismiss or minimize customer concerns",
        ],
    },
    "customer_centricity": {
        "name": "Customer-Centric Language",
        "description": "Focuses conversation on customer, not product or company",
        "max_score": 10,
        "criteria": [
            "Uses 'you' more than 'we' or 'I'",
            "Frames features as benefits to customer",
            "Asks about customer needs before presenting solutions",
            "Avoids company jargon or internal terminology",
        ],
    },
    "engagement_checks": {
        "name": "Engagement Checks",
        "description": "Regularly checks for understanding and engagement",
        "max_score": 5,
        "criteria": [
            "Asks 'Does that make sense?' or similar",
            "Pauses to let customer process information",
            "Invites questions throughout, not just at end",
        ],
    },
}

# Verification
_total_points = sum(criterion["max_score"] for criterion in ENGAGEMENT_RUBRIC.values())
assert _total_points == 100, f"Engagement rubric must total 100 points, got {_total_points}"


def get_rubric() -> dict[str, RubricCriterion]:
    """Get the engagement rubric definition"""
    return ENGAGEMENT_RUBRIC


def get_total_points() -> int:
    """Get total possible points for engagement"""
    return sum(criterion["max_score"] for criterion in ENGAGEMENT_RUBRIC.values())


def get_criterion_names() -> list[str]:
    """Get list of criterion keys"""
    return list(ENGAGEMENT_RUBRIC.keys())
