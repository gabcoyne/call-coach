"""
API monitoring and metrics endpoints.

Provides real-time metrics for:
- Rate limiting statistics
- Response time percentiles
- Error rates
- Database performance
- API usage patterns
"""
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ============================================================================
# METRICS COLLECTION
# ============================================================================

@dataclass
class MetricsCollector:
    """
    Thread-safe metrics collector for API monitoring.

    Tracks request counts, response times, errors, and rate limiting.
    """
    # Request counts by endpoint
    request_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Response times (store last N for percentiles)
    response_times: dict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    max_response_time_samples: int = 1000

    # Error counts by status code
    error_counts: dict[int, int] = field(default_factory=lambda: defaultdict(int))

    # Rate limit hits
    rate_limit_hits: int = 0
    rate_limit_hits_by_endpoint: dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    # Start time for uptime calculation
    start_time: float = field(default_factory=time.time)

    # Thread lock
    lock: Lock = field(default_factory=Lock)

    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record request metrics."""
        with self.lock:
            self.request_counts[endpoint] += 1

            # Store response time (keep last N samples)
            times = self.response_times[endpoint]
            times.append(response_time)
            if len(times) > self.max_response_time_samples:
                times.pop(0)

            # Record errors
            if status_code >= 400:
                self.error_counts[status_code] += 1

            # Record rate limit hits
            if status_code == 429:
                self.rate_limit_hits += 1
                self.rate_limit_hits_by_endpoint[endpoint] += 1

    def get_percentile(self, endpoint: str, percentile: float) -> float | None:
        """Calculate response time percentile for endpoint."""
        with self.lock:
            times = self.response_times.get(endpoint, [])
            if not times:
                return None

            sorted_times = sorted(times)
            index = int(len(sorted_times) * (percentile / 100))
            return sorted_times[min(index, len(sorted_times) - 1)]

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all metrics."""
        with self.lock:
            total_requests = sum(self.request_counts.values())
            total_errors = sum(self.error_counts.values())

            # Calculate global percentiles
            all_times = []
            for times in self.response_times.values():
                all_times.extend(times)

            global_p50 = None
            global_p95 = None
            global_p99 = None

            if all_times:
                sorted_times = sorted(all_times)
                global_p50 = sorted_times[int(len(sorted_times) * 0.5)]
                global_p95 = sorted_times[int(len(sorted_times) * 0.95)]
                global_p99 = sorted_times[int(len(sorted_times) * 0.99)]

            return {
                "uptime_seconds": time.time() - self.start_time,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": total_errors / total_requests if total_requests > 0 else 0,
                "rate_limit_hits": self.rate_limit_hits,
                "response_time_ms": {
                    "p50": global_p50,
                    "p95": global_p95,
                    "p99": global_p99,
                },
                "requests_by_endpoint": dict(self.request_counts),
                "errors_by_status": dict(self.error_counts),
                "rate_limit_hits_by_endpoint": dict(self.rate_limit_hits_by_endpoint),
            }

    def get_endpoint_metrics(self, endpoint: str) -> dict[str, Any]:
        """Get detailed metrics for specific endpoint."""
        with self.lock:
            request_count = self.request_counts.get(endpoint, 0)

            return {
                "endpoint": endpoint,
                "total_requests": request_count,
                "rate_limit_hits": self.rate_limit_hits_by_endpoint.get(endpoint, 0),
                "response_time_ms": {
                    "p50": self.get_percentile(endpoint, 50),
                    "p90": self.get_percentile(endpoint, 90),
                    "p95": self.get_percentile(endpoint, 95),
                    "p99": self.get_percentile(endpoint, 99),
                },
            }

    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self.lock:
            self.request_counts.clear()
            self.response_times.clear()
            self.error_counts.clear()
            self.rate_limit_hits = 0
            self.rate_limit_hits_by_endpoint.clear()
            self.start_time = time.time()


# Global metrics collector instance
metrics = MetricsCollector()


# ============================================================================
# MONITORING ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for load balancers.

    Returns:
        Health status with basic metrics
    """
    from db.connection import get_db_pool

    # Check database connectivity
    db_healthy = True
    try:
        pool = get_db_pool()
        # Basic check - pool exists
        db_healthy = pool is not None
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - metrics.start_time,
        "database": "connected" if db_healthy else "error",
    }


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """
    Get comprehensive API metrics.

    Returns:
        Detailed metrics including request counts, response times, errors
    """
    return metrics.get_metrics_summary()


@router.get("/metrics/endpoint/{endpoint:path}")
async def get_endpoint_metrics(endpoint: str) -> dict[str, Any]:
    """
    Get detailed metrics for specific endpoint.

    Args:
        endpoint: Endpoint path (e.g., "/tools/analyze_call")

    Returns:
        Endpoint-specific metrics
    """
    return metrics.get_endpoint_metrics(f"/{endpoint}")


@router.get("/metrics/database")
async def get_database_metrics() -> dict[str, Any]:
    """
    Get database performance metrics.

    Returns:
        Database connection pool stats and query performance
    """
    from db.connection import fetch_one

    try:
        # Get connection pool stats
        pool_stats = fetch_one("""
            SELECT
                count(*) as total_connections,
                sum(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active,
                sum(CASE WHEN state = 'idle' THEN 1 ELSE 0 END) as idle,
                sum(CASE WHEN state = 'idle in transaction' THEN 1 ELSE 0 END) as idle_in_transaction
            FROM pg_stat_activity
            WHERE datname = current_database()
        """)

        # Get slow query count (queries > 1 second)
        slow_queries = fetch_one("""
            SELECT count(*) as slow_query_count
            FROM pg_stat_activity
            WHERE state != 'idle'
            AND now() - query_start > interval '1 second'
        """)

        return {
            "connection_pool": pool_stats,
            "slow_queries": slow_queries["slow_query_count"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching database metrics: {e}")
        return {
            "error": "Failed to fetch database metrics",
            "detail": str(e),
        }


@router.get("/metrics/rate-limits")
async def get_rate_limit_metrics() -> dict[str, Any]:
    """
    Get rate limiting statistics.

    Returns:
        Rate limit hits and patterns
    """
    return {
        "total_rate_limit_hits": metrics.rate_limit_hits,
        "rate_limit_hits_by_endpoint": dict(metrics.rate_limit_hits_by_endpoint),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/metrics/reset")
async def reset_metrics() -> dict[str, str]:
    """
    Reset metrics (admin only - should add auth).

    Returns:
        Success confirmation
    """
    # TODO: Add authentication
    metrics.reset_metrics()
    return {"status": "metrics_reset", "timestamp": datetime.utcnow().isoformat()}


# ============================================================================
# MIDDLEWARE INTEGRATION
# ============================================================================

async def record_request_metrics(request: Request, response_time: float, status_code: int):
    """
    Record request metrics from middleware.

    This should be called by the request timing middleware.

    Args:
        request: FastAPI request
        response_time: Response time in milliseconds
        status_code: HTTP status code
    """
    endpoint = request.url.path
    metrics.record_request(endpoint, response_time, status_code)
