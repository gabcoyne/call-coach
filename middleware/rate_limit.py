"""
Rate limiting middleware using token bucket algorithm.

Implements per-user and per-endpoint rate limits with configurable
burst capacity and refill rate.
"""
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock
from typing import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """
    Token bucket for rate limiting.

    Algorithm:
    - Bucket has capacity C tokens
    - Refills at rate R tokens per second
    - Each request consumes 1 token
    - If bucket is empty, request is rejected
    """
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.

        Returns:
            True if tokens were available, False if rate limited
        """
        now = time.time()
        elapsed = now - self.last_refill

        # Refill bucket based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now

        # Try to consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def remaining_tokens(self) -> int:
        """Get number of remaining tokens (rounded down)."""
        return int(self.tokens)

    def reset_time(self) -> float:
        """Estimate seconds until bucket is full again."""
        tokens_needed = self.capacity - self.tokens
        return tokens_needed / self.refill_rate if self.refill_rate > 0 else 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with per-user and per-endpoint limits.

    Default limits (can be overridden per endpoint):
    - 100 requests per minute per user (general)
    - 20 requests per minute for expensive operations
    - 1000 requests per minute per user (total burst)
    """

    def __init__(
        self,
        app,
        default_rate_limit: int = 100,  # requests per minute
        default_burst: int = 150,
        expensive_rate_limit: int = 20,
        expensive_burst: int = 30,
    ):
        super().__init__(app)
        self.default_rate_limit = default_rate_limit
        self.default_burst = default_burst
        self.expensive_rate_limit = expensive_rate_limit
        self.expensive_burst = expensive_burst

        # Per-user rate limit buckets (key: user_identifier)
        self.user_buckets: dict[str, TokenBucket] = {}
        self.lock = Lock()

        # Expensive endpoints (require more rate limiting)
        self.expensive_endpoints = {
            "/tools/analyze_call",
            "/tools/analyze_opportunity",
            "/tools/get_learning_insights",
        }

    def _get_user_identifier(self, request: Request) -> str:
        """
        Extract user identifier from request.

        Priority:
        1. User email from auth header
        2. API key from header
        3. IP address as fallback
        """
        # Check for user email in headers (from auth middleware)
        user_email = request.headers.get("X-User-Email")
        if user_email:
            return f"user:{user_email}"

        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key[:16]}"  # Use prefix to avoid logging full key

        # Fallback to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    def _get_rate_limit_bucket(self, user_id: str, path: str) -> TokenBucket:
        """Get or create token bucket for user."""
        # Determine if this is an expensive endpoint
        is_expensive = any(path.startswith(ep) for ep in self.expensive_endpoints)

        rate_limit = self.expensive_rate_limit if is_expensive else self.default_rate_limit
        burst = self.expensive_burst if is_expensive else self.default_burst

        # Use per-endpoint buckets for better isolation
        bucket_key = f"{user_id}:{path}"

        with self.lock:
            if bucket_key not in self.user_buckets:
                self.user_buckets[bucket_key] = TokenBucket(
                    capacity=burst,
                    refill_rate=rate_limit / 60.0,  # Convert per minute to per second
                    tokens=float(burst),  # Start with full bucket
                    last_refill=time.time(),
                )

            return self.user_buckets[bucket_key]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get user identifier and rate limit bucket
        user_id = self._get_user_identifier(request)
        bucket = self._get_rate_limit_bucket(user_id, request.url.path)

        # Try to consume token
        if not bucket.consume():
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {user_id} on {request.url.path}"
            )

            # Add rate limit headers
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": int(bucket.reset_time()),
                },
                headers={
                    "X-RateLimit-Limit": str(bucket.capacity),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + bucket.reset_time())),
                    "Retry-After": str(int(bucket.reset_time())),
                },
            )
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(bucket.capacity)
        response.headers["X-RateLimit-Remaining"] = str(bucket.remaining_tokens())
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + bucket.reset_time()))

        return response

    def cleanup_old_buckets(self, max_age_seconds: float = 3600):
        """
        Clean up inactive buckets (call periodically).

        Removes buckets that haven't been used in max_age_seconds.
        """
        now = time.time()
        with self.lock:
            expired_keys = [
                key for key, bucket in self.user_buckets.items()
                if now - bucket.last_refill > max_age_seconds
            ]
            for key in expired_keys:
                del self.user_buckets[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired rate limit buckets")


def get_rate_limit_stats() -> dict:
    """
    Get current rate limit statistics.

    Returns:
        Dict with active buckets, total requests, rate limit hits
    """
    # This would need to be integrated with the middleware instance
    # For now, return placeholder
    return {
        "active_buckets": 0,
        "total_requests": 0,
        "rate_limit_hits": 0,
    }
