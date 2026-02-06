"""
Instrumentation for structured logging, profiling, and observability.

Provides:
- Structured JSON logging with correlation IDs
- Performance profiling and bottleneck detection
- Request tracing capabilities
"""

from instrumentation.logger import (
    get_correlation_id,
    get_logger,
    set_correlation_id,
    setup_structured_logging,
)
from instrumentation.profiler import (
    get_cpu_profiler,
    get_performance_profiler,
    get_slow_request_detector,
    initialize_profiling,
    profile_request,
)

__all__ = [
    "setup_structured_logging",
    "get_logger",
    "get_correlation_id",
    "set_correlation_id",
    "get_performance_profiler",
    "get_cpu_profiler",
    "get_slow_request_detector",
    "initialize_profiling",
    "profile_request",
]
