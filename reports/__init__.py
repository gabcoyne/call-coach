"""
Reports module for generating and delivering coaching reports.

Provides utilities for:
- Rendering email templates
- Sending emails via various providers
- Posting to Slack webhooks
- Generating markdown and HTML reports
"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
