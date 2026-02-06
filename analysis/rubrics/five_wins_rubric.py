"""
Five Wins Rubric - Primary Evaluation Framework

This is the PRIMARY rubric used for sales coaching at Prefect.
The Five Wins represent what it takes to successfully close a deal.

Total: 100 points distributed across the 5 wins based on typical deal importance.
"""

from typing import TypedDict


class RubricCriterion(TypedDict):
    """Definition of a single rubric criterion"""

    name: str
    description: str
    max_score: int
    criteria: list[str]


# Five Wins Rubric - Total: 100 points
# Based on Prefect's internal sales methodology

FIVE_WINS_RUBRIC: dict[str, RubricCriterion] = {
    "business_win": {
        "name": "Business Win",
        "description": "Economic buyer sees clear business value and ROI",
        "max_score": 35,
        "criteria": [
            "Current state and problems clearly identified",
            "Future state and desired outcomes articulated",
            "Success metrics defined (how they'll measure value)",
            "Executive priorities and strategic alignment discussed",
            "Evaluation and decision criteria understood",
            "Business case strength: quantified impact and ROI",
        ],
    },
    "technical_win": {
        "name": "Technical Win",
        "description": "Technical champion/architect validates solution fits their requirements",
        "max_score": 25,
        "criteria": [
            "Technical requirements and constraints identified",
            "Use case alignment validated (Prefect solves their specific problem)",
            "Infrastructure and deployment requirements understood",
            "CI/CD and integration requirements discussed",
            "Demo/solution presentation planned or executed",
            "POC scoping discussed if needed",
        ],
    },
    "security_win": {
        "name": "Security Win",
        "description": "InfoSec/Security team approves or has clear path to approval",
        "max_score": 15,
        "criteria": [
            "InfoSec requirements identified (SOC2, HIPAA, data residency, etc.)",
            "Security review process and timeline understood",
            "Security questionnaire discussed or submitted",
            "Potential security blockers surfaced early",
        ],
    },
    "commercial_win": {
        "name": "Commercial Win",
        "description": "Pricing, packaging, and commercial terms are acceptable",
        "max_score": 15,
        "criteria": [
            "Scope of deployment discussed (users, use cases, scale)",
            "Budget range and flexibility explored",
            "Commercial terms and contract requirements understood",
            "Pricing model aligned with customer's procurement preferences",
        ],
    },
    "legal_win": {
        "name": "Legal Win",
        "description": "Legal/procurement process understood and on track",
        "max_score": 10,
        "criteria": [
            "Legal review process and timeline identified",
            "Contract requirements and redlines discussed",
            "Procurement process and stakeholders mapped",
            "Potential legal blockers surfaced",
        ],
    },
}

# Verification
_total_points = sum(criterion["max_score"] for criterion in FIVE_WINS_RUBRIC.values())
assert _total_points == 100, f"Five Wins rubric must total 100 points, got {_total_points}"


def get_rubric() -> dict[str, RubricCriterion]:
    """Get the Five Wins rubric definition"""
    return FIVE_WINS_RUBRIC


def get_total_points() -> int:
    """Get total possible points for Five Wins"""
    return sum(criterion["max_score"] for criterion in FIVE_WINS_RUBRIC.values())


def get_criterion_names() -> list[str]:
    """Get list of win keys"""
    return list(FIVE_WINS_RUBRIC.keys())


def get_wins_by_importance() -> list[tuple[str, int]]:
    """Get wins sorted by point value (importance)"""
    return sorted(
        [(win, details["max_score"]) for win, details in FIVE_WINS_RUBRIC.items()],
        key=lambda x: x[1],
        reverse=True,
    )
