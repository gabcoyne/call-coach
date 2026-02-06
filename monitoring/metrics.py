"""
Prometheus metrics for monitoring application performance and usage.

Tracks: API response times, Claude API token usage, cache hit rates,
database query times, and other key performance indicators.
"""

import logging
import time
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
except ImportError:
    # Fallback for environments without prometheus_client
    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def time(self, *args, **kwargs):
            from contextlib import contextmanager

            @contextmanager
            def noop():
                yield

            return noop()

        def labels(self, *args, **kwargs):
            return self

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def dec(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    CollectorRegistry = object

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Prometheus metrics collector for the Call Coach application."""

    def __init__(self, registry: CollectorRegistry | None = None):
        """
        Initialize metrics collector.

        Args:
            registry: Prometheus registry (uses default if None)
        """
        self.registry = registry

        # API metrics
        self.api_request_count = Counter(
            "api_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"],
            registry=registry,
        )
        self.api_request_duration = Histogram(
            "api_request_duration_seconds",
            "API request duration in seconds",
            ["method", "endpoint"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=registry,
        )

        # Claude API metrics
        self.claude_api_calls = Counter(
            "claude_api_calls_total",
            "Total Claude API calls",
            ["model", "status"],
            registry=registry,
        )
        self.claude_input_tokens = Counter(
            "claude_input_tokens_total",
            "Total input tokens sent to Claude API",
            ["model"],
            registry=registry,
        )
        self.claude_output_tokens = Counter(
            "claude_output_tokens_total",
            "Total output tokens received from Claude API",
            ["model"],
            registry=registry,
        )
        self.claude_api_duration = Histogram(
            "claude_api_duration_seconds",
            "Claude API call duration in seconds",
            ["model"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
            registry=registry,
        )

        # Cache metrics
        self.cache_hits = Counter(
            "cache_hits_total",
            "Total cache hits",
            ["cache_type"],
            registry=registry,
        )
        self.cache_misses = Counter(
            "cache_misses_total",
            "Total cache misses",
            ["cache_type"],
            registry=registry,
        )
        self.cache_size = Gauge(
            "cache_size_bytes",
            "Current cache size in bytes",
            ["cache_type"],
            registry=registry,
        )

        # Database metrics
        self.db_query_count = Counter(
            "db_queries_total",
            "Total database queries",
            ["operation", "table"],
            registry=registry,
        )
        self.db_query_duration = Histogram(
            "db_query_duration_seconds",
            "Database query duration in seconds",
            ["operation", "table"],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
            registry=registry,
        )
        self.db_connections = Gauge(
            "db_connections_active",
            "Active database connections",
            registry=registry,
        )

        # Business metrics
        self.calls_analyzed = Counter(
            "calls_analyzed_total",
            "Total calls analyzed",
            ["status"],
            registry=registry,
        )
        self.coaching_sessions_created = Counter(
            "coaching_sessions_created_total",
            "Total coaching sessions created",
            registry=registry,
        )
        self.coaching_session_duration = Histogram(
            "coaching_session_duration_seconds",
            "Coaching session duration in seconds",
            buckets=(10, 30, 60, 300, 600, 1800, 3600),
            registry=registry,
        )

        # Error metrics
        self.errors_total = Counter(
            "errors_total",
            "Total errors",
            ["error_type", "source"],
            registry=registry,
        )
        self.gong_api_errors = Counter(
            "gong_api_errors_total",
            "Total Gong API errors",
            ["error_type"],
            registry=registry,
        )

        # System metrics
        self.background_tasks_running = Gauge(
            "background_tasks_running",
            "Number of background tasks running",
            registry=registry,
        )

    # API metrics methods
    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
    ) -> None:
        """Record an API request."""
        self.api_request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    @contextmanager
    def track_api_request(self, method: str, endpoint: str, status: int = 200):
        """Context manager to track API request timing."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_api_request(method, endpoint, status, duration)

    # Claude API metrics methods
    def record_claude_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration: float,
        status: str = "success",
    ) -> None:
        """Record a Claude API call."""
        self.claude_api_calls.labels(model=model, status=status).inc()
        self.claude_input_tokens.labels(model=model).inc(input_tokens)
        self.claude_output_tokens.labels(model=model).inc(output_tokens)
        self.claude_api_duration.labels(model=model).observe(duration)

    @contextmanager
    def track_claude_call(self, model: str = "claude-opus-4-5"):
        """Context manager to track Claude API call."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            # Update metrics with actual token usage from context if available
            self.claude_api_duration.labels(model=model).observe(duration)

    # Cache metrics methods
    def record_cache_hit(self, cache_type: str) -> None:
        """Record a cache hit."""
        self.cache_hits.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str) -> None:
        """Record a cache miss."""
        self.cache_misses.labels(cache_type=cache_type).inc()

    def set_cache_size(self, cache_type: str, size_bytes: int) -> None:
        """Update cache size."""
        self.cache_size.labels(cache_type=cache_type).set(size_bytes)

    def get_cache_hit_rate(self, cache_type: str) -> float:
        """Calculate cache hit rate for a given cache type."""
        hits = (
            self.cache_hits.labels(cache_type=cache_type)._value.get()
            if hasattr(self.cache_hits.labels(cache_type=cache_type), "_value")
            else 0
        )
        misses = (
            self.cache_misses.labels(cache_type=cache_type)._value.get()
            if hasattr(self.cache_misses.labels(cache_type=cache_type), "_value")
            else 0
        )
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0

    # Database metrics methods
    def record_db_query(
        self,
        operation: str,
        table: str,
        duration: float,
        success: bool = True,
    ) -> None:
        """Record a database query."""
        status = "success" if success else "error"
        self.db_query_count.labels(operation=operation, table=table).inc()
        self.db_query_duration.labels(operation=operation, table=table).observe(duration)

    @contextmanager
    def track_db_query(self, operation: str, table: str):
        """Context manager to track database query."""
        start_time = time.time()
        success = True
        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            self.record_db_query(operation, table, duration, success)

    def set_db_connection_count(self, count: int) -> None:
        """Update active database connection count."""
        self.db_connections.set(count)

    # Business metrics methods
    def record_call_analyzed(self, status: str = "success") -> None:
        """Record a call analysis."""
        self.calls_analyzed.labels(status=status).inc()

    def record_coaching_session_created(self) -> None:
        """Record a coaching session creation."""
        self.coaching_sessions_created.inc()

    def record_coaching_session_duration(self, duration: float) -> None:
        """Record coaching session duration."""
        self.coaching_session_duration.observe(duration)

    # Error metrics methods
    def record_error(self, error_type: str, source: str) -> None:
        """Record an error."""
        self.errors_total.labels(error_type=error_type, source=source).inc()

    def record_gong_api_error(self, error_type: str) -> None:
        """Record a Gong API error."""
        self.gong_api_errors.labels(error_type=error_type).inc()

    # System metrics methods
    def set_background_tasks_count(self, count: int) -> None:
        """Update background task count."""
        self.background_tasks_running.set(count)


# Global metrics instance
_metrics: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


def initialize_metrics() -> MetricsCollector:
    """Initialize global metrics collector."""
    global _metrics
    _metrics = MetricsCollector()
    logger.info("Metrics collector initialized")
    return _metrics


def track_api_call(method: str, endpoint: str):
    """Decorator to track API calls."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            metrics = get_metrics()
            start_time = time.time()
            status = 200
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                status = 500
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_api_request(method, endpoint, status, duration)

        return wrapper

    return decorator
