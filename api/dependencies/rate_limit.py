"""
Rate limiting dependency using FastAPI dependency injection.

Refactored from middleware to use dependency injection for better:
- Testability (can inject mocks easily)
- Type safety (documented in OpenAPI schema)
- Error handling (proper FastAPI exceptions)
- Maintainability (no Starlette version issues)

Usage:
    @app.get("/endpoint")
    async def endpoint(
        rate_limit: RateLimitInfo = Depends(check_rate_limit)
    ):
        # rate_limit contains: allowed, remaining, reset_time
        ...
"""

import logging
import time
from dataclasses import dataclass
from threading import Lock
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

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
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
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


@dataclass
class RateLimitInfo:
    """Information about rate limit status."""

    allowed: bool
    limit: int
    remaining: int
    reset_time: float


class RateLimitService:
    """
    Rate limiting service with per-user and per-endpoint limits.

    Default limits (can be overridden per endpoint):
    - 100 requests per minute per user (general)
    - 20 requests per minute for expensive operations
    - 1000 requests per minute per user (total burst)
    """

    def __init__(
        self,
        default_rate_limit: int = 100,  # requests per minute
        default_burst: int = 150,
        expensive_rate_limit: int = 20,
        expensive_burst: int = 30,
    ):
        self.default_rate_limit = default_rate_limit
        self.default_burst = default_burst
        self.expensive_rate_limit = expensive_rate_limit
        self.expensive_burst = expensive_burst

        # Per-user rate limit buckets (key: user_identifier:path)
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

    def check_rate_limit(self, request: Request) -> RateLimitInfo:
        """
        Check if request is within rate limit.

        Returns:
            RateLimitInfo with allowed status and limit details
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return RateLimitInfo(allowed=True, limit=0, remaining=0, reset_time=0)

        # Get user identifier and rate limit bucket
        user_id = self._get_user_identifier(request)
        bucket = self._get_rate_limit_bucket(user_id, request.url.path)

        # Try to consume token
        if not bucket.consume():
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for {user_id} on {request.url.path}")
            return RateLimitInfo(
                allowed=False,
                limit=bucket.capacity,
                remaining=0,
                reset_time=time.time() + bucket.reset_time(),
            )

        # Within rate limit
        return RateLimitInfo(
            allowed=True,
            limit=bucket.capacity,
            remaining=bucket.remaining_tokens(),
            reset_time=time.time() + bucket.reset_time(),
        )

    def cleanup_old_buckets(self, max_age_seconds: float = 3600):
        """
        Clean up inactive buckets (call periodically).

        Removes buckets that haven't been used in max_age_seconds.
        """
        now = time.time()
        with self.lock:
            expired_keys = [
                key
                for key, bucket in self.user_buckets.items()
                if now - bucket.last_refill > max_age_seconds
            ]
            for key in expired_keys:
                del self.user_buckets[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired rate limit buckets")


# Global rate limit service instance
_rate_limit_service = RateLimitService()


def get_rate_limit_service() -> RateLimitService:
    """Get the global rate limit service instance."""
    return _rate_limit_service


async def check_rate_limit(
    request: Request,
    service: RateLimitService = Depends(get_rate_limit_service),
) -> RateLimitInfo:
    """
    FastAPI dependency for rate limiting.

    Usage:
        @app.get("/endpoint")
        async def endpoint(
            rate_limit: RateLimitInfo = Depends(check_rate_limit)
        ):
            # rate_limit.allowed, rate_limit.remaining, etc.
            ...

    Raises:
        HTTPException: 429 Too Many Requests if rate limit exceeded
    """
    rate_limit_info = service.check_rate_limit(request)

    if not rate_limit_info.allowed:
        # Rate limit exceeded - return 429 with headers
        retry_after = int(rate_limit_info.reset_time - time.time())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": retry_after,
            },
            headers={
                "X-RateLimit-Limit": str(rate_limit_info.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(rate_limit_info.reset_time)),
                "Retry-After": str(retry_after),
            },
        )

    return rate_limit_info


# Type alias for dependency injection
RateLimitDep = Annotated[RateLimitInfo, Depends(check_rate_limit)]
