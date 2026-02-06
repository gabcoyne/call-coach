"""
Product Knowledge Rubric - Supplementary Framework

This rubric evaluates how well the rep demonstrates product mastery
during technical discussions and demonstrations.

Total: 100 points distributed across product expertise dimensions.
"""

from typing import TypedDict


class RubricCriterion(TypedDict):
    """Definition of a single rubric criterion"""

    name: str
    description: str
    max_score: int
    criteria: list[str]


# Product Knowledge Rubric - Total: 100 points
# Used when calls involve product demonstrations or technical discussions

PRODUCT_KNOWLEDGE_RUBRIC: dict[str, RubricCriterion] = {
    "solution_positioning": {
        "name": "Solution Positioning",
        "description": "Rep positions Prefect as the right solution for customer's use case",
        "max_score": 20,
        "criteria": [
            "Clear articulation of Prefect's core value proposition",
            "Positioning against customer's current tools/approach",
            "Use case fit explanation (why Prefect for their scenario)",
            "Differentiation from alternatives discussed",
        ],
    },
    "feature_knowledge": {
        "name": "Feature Knowledge",
        "description": "Rep demonstrates deep knowledge of Prefect features and capabilities",
        "max_score": 20,
        "criteria": [
            "Accurate description of relevant features",
            "Explanation of how features work together",
            "Feature benefits tied to customer needs",
            "Upcoming/roadmap features discussed appropriately",
        ],
    },
    "technical_depth": {
        "name": "Technical Depth",
        "description": "Rep shows technical understanding and can go deep when needed",
        "max_score": 15,
        "criteria": [
            "Architecture and design patterns explained clearly",
            "Integration points and API usage discussed",
            "Performance and scale considerations addressed",
            "Technical trade-offs explained honestly",
        ],
    },
    "demo_execution": {
        "name": "Demo Execution",
        "description": "Rep delivers effective product demonstrations",
        "max_score": 15,
        "criteria": [
            "Demo aligned to customer's use case (not generic)",
            "Smooth execution with minimal technical issues",
            "Explains what's happening and why it matters",
            "Responds effectively to demo questions",
        ],
    },
    "competitive_awareness": {
        "name": "Competitive Awareness",
        "description": "Rep handles competitive comparisons with knowledge and confidence",
        "max_score": 10,
        "criteria": [
            "Knows competitor strengths and weaknesses",
            "Positions Prefect's advantages clearly",
            "Avoids disparaging competitors",
            "Acknowledges trade-offs honestly",
        ],
    },
    "use_case_examples": {
        "name": "Use Case Examples",
        "description": "Rep uses relevant customer stories and examples",
        "max_score": 10,
        "criteria": [
            "Shares similar customer success stories",
            "Examples relevant to prospect's industry/use case",
            "Quantified outcomes from examples when possible",
            "Builds credibility through proof points",
        ],
    },
    "limits_and_gaps": {
        "name": "Limits and Gaps",
        "description": "Rep honestly addresses Prefect's limitations or gaps",
        "max_score": 10,
        "criteria": [
            "Acknowledges gaps when they exist",
            "Explains workarounds or roadmap plans",
            "Sets realistic expectations",
            "Doesn't oversell or overpromise",
        ],
    },
}

# Verification
_total_points = sum(criterion["max_score"] for criterion in PRODUCT_KNOWLEDGE_RUBRIC.values())
assert _total_points == 100, f"Product Knowledge rubric must total 100 points, got {_total_points}"


def get_rubric() -> dict[str, RubricCriterion]:
    """Get the Product Knowledge rubric definition"""
    return PRODUCT_KNOWLEDGE_RUBRIC


def get_total_points() -> int:
    """Get total possible points for Product Knowledge"""
    return sum(criterion["max_score"] for criterion in PRODUCT_KNOWLEDGE_RUBRIC.values())


def get_criterion_names() -> list[str]:
    """Get list of criterion keys"""
    return list(PRODUCT_KNOWLEDGE_RUBRIC.keys())


def get_criteria_by_importance() -> list[tuple[str, int]]:
    """Get criteria sorted by point value (importance)"""
    return sorted(
        [
            (criterion, details["max_score"])
            for criterion, details in PRODUCT_KNOWLEDGE_RUBRIC.items()
        ],
        key=lambda x: x[1],
        reverse=True,
    )
