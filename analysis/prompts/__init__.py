"""Prompt templates for coaching analysis."""
from .discovery import analyze_discovery_prompt
from .engagement import analyze_engagement_prompt
from .objection_handling import analyze_objection_handling_prompt
from .product_knowledge import analyze_product_knowledge_prompt

__all__ = [
    "analyze_discovery_prompt",
    "analyze_engagement_prompt",
    "analyze_objection_handling_prompt",
    "analyze_product_knowledge_prompt",
]
