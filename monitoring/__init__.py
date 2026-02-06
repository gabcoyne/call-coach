"""
Monitoring and observability infrastructure for Call Coach.

Provides:
- Sentry integration for error tracking
- Prometheus metrics collection
- Structured JSON logging
- Performance profiling
- Alerting rules and configurations
"""

from monitoring.metrics import get_metrics, initialize_metrics, track_api_call
from monitoring.sentry import (
    add_breadcrumb,
    capture_exception,
    capture_message,
    initialize_sentry,
    set_tags,
    set_user_context,
)

__all__ = [
    "initialize_sentry",
    "capture_exception",
    "capture_message",
    "add_breadcrumb",
    "set_user_context",
    "set_tags",
    "get_metrics",
    "initialize_metrics",
    "track_api_call",
]
