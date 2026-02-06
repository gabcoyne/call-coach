"""
Rubrics Module

Provides structured rubric definitions for all coaching dimensions.
Each rubric defines criteria, point allocations, and evaluation guidelines.

PRIMARY RUBRIC: Five Wins - this is how Prefect internally thinks about and coaches sales.
SUPPLEMENTARY RUBRICS: Discovery, Engagement, etc. - used to inform coaching within each win.
"""

from .discovery_rubric import DISCOVERY_RUBRIC
from .engagement_rubric import ENGAGEMENT_RUBRIC
from .five_wins_rubric import FIVE_WINS_RUBRIC
from .objection_handling_rubric import OBJECTION_HANDLING_RUBRIC
from .product_knowledge_rubric import PRODUCT_KNOWLEDGE_RUBRIC

__all__ = [
    "FIVE_WINS_RUBRIC",
    "DISCOVERY_RUBRIC",
    "ENGAGEMENT_RUBRIC",
    "PRODUCT_KNOWLEDGE_RUBRIC",
    "OBJECTION_HANDLING_RUBRIC",
    "get_rubric_for_dimension",
]


def get_rubric_for_dimension(dimension: str) -> dict:
    """
    Get the rubric definition for a coaching dimension.

    Args:
        dimension: Coaching dimension (five_wins, discovery, engagement, etc.)

    Returns:
        Rubric dictionary with criteria definitions

    Raises:
        ValueError: If dimension not found
    """
    rubrics = {
        "five_wins": FIVE_WINS_RUBRIC,
        "discovery": DISCOVERY_RUBRIC,
        "engagement": ENGAGEMENT_RUBRIC,
        "product_knowledge": PRODUCT_KNOWLEDGE_RUBRIC,
        "objection_handling": OBJECTION_HANDLING_RUBRIC,
    }

    if dimension not in rubrics:
        raise ValueError(
            f"No rubric defined for dimension '{dimension}'. " f"Available: {list(rubrics.keys())}"
        )

    return rubrics[dimension]
