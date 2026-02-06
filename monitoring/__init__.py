"""
Monitoring and observability infrastructure for Call Coach.

Provides:
- Sentry integration for error tracking
- Prometheus metrics collection
- Structured JSON logging
- Performance profiling
- Alerting rules and configurations
"""

from monitoring.sentry import (
    initialize_sentry,
    capture_exception,
    capture_message,
    add_breadcrumb,
    set_user_context,
    set_tags,
)
from monitoring.metrics import (
    get_metrics,
    initialize_metrics,
    track_api_call,
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
