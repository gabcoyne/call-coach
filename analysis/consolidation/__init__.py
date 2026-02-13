"""
Consolidation Layer for Five Wins Coaching

Post-processing module that transforms raw Five Wins evaluation into
actionable coaching output:

1. narrative_generator - Synthesize wins into 2-3 sentence narrative
2. action_selector - Pick the single most important action
3. moment_linker - Connect actions to specific call moments
"""

from .action_selector import select_primary_action
from .moment_linker import link_action_to_moment
from .narrative_generator import generate_narrative

__all__ = [
    "generate_narrative",
    "select_primary_action",
    "link_action_to_moment",
]
