"""
Knowledge Base Management System

Provides APIs and utilities for managing:
- Product documentation (Prefect, Horizon features)
- Coaching rubrics with versioning
- Competitive intelligence
- Version control for knowledge entries
"""

from .loader import KnowledgeBaseManager

__all__ = ["KnowledgeBaseManager"]
