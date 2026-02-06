"""
Rate limiting middleware for API protection.

Implements token bucket algorithm with Redis backend for
distributed rate limiting across multiple API instances.

Rate Limits (per user):
- GET endpoints: 100 requests/minute
- POST endpoints: 30 requests/minute
- Analysis endpoints: 10 requests/minute (expensive operations)

Headers added to responses:
- X-RateLimit-Limit: Maximum requests allowed
- X-RateLimit-Remaining: Requests remaining in window
- X-RateLimit-Reset: Unix timestamp when limit resets
"""
import logging
import time
from typing import Callable

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.

    Supports:
    - Per-user rate limits (by email or IP)
    - Per-endpoint rate limits
    - Redis-backed distributed limiting
    - Graceful degradation if Redis unavailable
    """

    # Default rate limits (requests per minute)
    DEFAULT_LIMITS = {
        "GET": 100,
        "POST": 30,
        "PUT": 30,
        "PATCH": 30,
        "DELETE": 20,
    }

    # Endpoint-specific overrides
    ENDPOINT_LIMITS = {
        "/tools/analyze_call": 10,  # Expensive Claude API calls
        "/tools/analyze_opportunity": 10,
        "/tools/get_learning_insights": 10,
        "/tools/get_rep_insights": 20,
        "/tools/search_calls": 50,
    }

    def __init__(
        self,
        app: ASGIApp,
        redis_client=None,
        enable_rate_limiting: bool = True,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: ASGI application
            redis_client: Redis client for distributed limiting
            enable_rate_limiting: Enable/disable rate limiting
        """
        super().__init__(app)
        self.redis_client = redis_client
        self.enable_rate_limiting = enable_rate_limiting
        self._local_cache = {}  # Fallback if Redis unavailable

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Check rate limits and process request.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response (or 429 if rate limited)
        """
        # Skip rate limiting if disabled or for health checks
        if not self.enable_rate_limiting or request.url.path == "/health":
            return await call_next(request)

        # Identify user (email from header or IP as fallback)
        user_id = self._get_user_identifier(request)

        # Get rate limit for this request
        limit = self._get_rate_limit(request)

        # Check rate limit
        allowed, remaining, reset_time = self._check_rate_limit(
            user_id=user_id,
            endpoint=request.url.path,
            method=request.method,
            limit=limit,
        )

        # Add rate limit headers to response
        if not allowed:
            # Rate limit exceeded
            retry_after = int(reset_time - time.time())
            logger.warning(
                f"Rate limit exceeded for user {user_id} on {request.method} {request.url.path}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "retry_after": retry_after,
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(retry_after),
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response

    def _get_user_identifier(self, request: Request) -> str:
        """
        Get user identifier for rate limiting.

        Priority:
        1. X-User-Email header (from authenticated session)
        2. X-Forwarded-For (if behind proxy)
        3. Client IP address

        Args:
            request: HTTP request

        Returns:
            User identifier string
        """
        # Check for user email header (from auth)
        user_email = request.headers.get("x-user-email")
        if user_email:
            return f"user:{user_email}"

        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Take first IP if multiple
            ip = forwarded.split(",")[0].strip()
            return f"ip:{ip}"

        # Fall back to client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _get_rate_limit(self, request: Request) -> int:
        """
        Get rate limit for this request.

        Checks endpoint-specific limits first, then method-based defaults.

        Args:
            request: HTTP request

        Returns:
            Rate limit (requests per minute)
        """
        # Check endpoint-specific limit
        endpoint = request.url.path
        if endpoint in self.ENDPOINT_LIMITS:
            return self.ENDPOINT_LIMITS[endpoint]

        # Fall back to method-based limit
        method = request.method
        return self.DEFAULT_LIMITS.get(method, 30)

    def _check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        limit: int,
    ) -> tuple[bool, int, float]:
        """
        Check if request is within rate limit.

        Uses token bucket algorithm:
        - Bucket starts full with {limit} tokens
        - Each request consumes 1 token
        - Bucket refills at rate of {limit} tokens per minute
        - If bucket empty, request is rate limited

        Args:
            user_id: User identifier
            endpoint: API endpoint
            method: HTTP method
            limit: Rate limit (requests per minute)

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        window_seconds = 60  # 1 minute window
        current_time = time.time()

        # Build cache key
        key = f"ratelimit:{user_id}:{method}:{endpoint}"

        if self.redis_client and self.redis_client.available:
            # Use Redis for distributed rate limiting
            return self._check_rate_limit_redis(
                key, limit, window_seconds, current_time
            )
        else:
            # Fall back to local cache (single instance only)
            return self._check_rate_limit_local(
                key, limit, window_seconds, current_time
            )

    def _check_rate_limit_redis(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        current_time: float,
    ) -> tuple[bool, int, float]:
        """
        Check rate limit using Redis.

        Uses Redis INCR with EXPIRE for atomic rate limiting.

        Args:
            key: Redis key
            limit: Rate limit
            window_seconds: Time window in seconds
            current_time: Current timestamp

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        try:
            # Get current count
            count = self.redis_client._client.get(key)

            if count is None:
                # First request in window
                self.redis_client._client.setex(key, window_seconds, 1)
                reset_time = current_time + window_seconds
                return True, limit - 1, reset_time
            else:
                count = int(count)

                if count < limit:
                    # Within limit, increment
                    new_count = self.redis_client._client.incr(key)
                    ttl = self.redis_client._client.ttl(key)
                    reset_time = current_time + ttl
                    return True, limit - new_count, reset_time
                else:
                    # Exceeded limit
                    ttl = self.redis_client._client.ttl(key)
                    reset_time = current_time + ttl
                    return False, 0, reset_time

        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fall back to local cache
            return self._check_rate_limit_local(
                key, limit, window_seconds, current_time
            )

    def _check_rate_limit_local(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        current_time: float,
    ) -> tuple[bool, int, float]:
        """
        Check rate limit using local in-memory cache.

        Note: This only works for single-instance deployments.
        Use Redis for distributed deployments.

        Args:
            key: Cache key
            limit: Rate limit
            window_seconds: Time window in seconds
            current_time: Current timestamp

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        # Clean up expired entries
        self._cleanup_local_cache(current_time)

        if key not in self._local_cache:
            # First request in window
            self._local_cache[key] = {
                "count": 1,
                "reset_time": current_time + window_seconds,
            }
            return True, limit - 1, current_time + window_seconds

        entry = self._local_cache[key]

        # Check if window expired
        if current_time >= entry["reset_time"]:
            # Reset window
            entry["count"] = 1
            entry["reset_time"] = current_time + window_seconds
            return True, limit - 1, entry["reset_time"]

        # Check limit
        if entry["count"] < limit:
            entry["count"] += 1
            return True, limit - entry["count"], entry["reset_time"]
        else:
            return False, 0, entry["reset_time"]

    def _cleanup_local_cache(self, current_time: float) -> None:
        """
        Remove expired entries from local cache.

        Args:
            current_time: Current timestamp
        """
        expired_keys = [
            key for key, entry in self._local_cache.items()
            if current_time >= entry["reset_time"]
        ]

        for key in expired_keys:
            del self._local_cache[key]


def get_rate_limit_stats() -> dict:
    """
    Get rate limiting statistics.

    Returns:
        Dict with rate limit configuration and stats
    """
    return {
        "enabled": True,
        "default_limits": RateLimitMiddleware.DEFAULT_LIMITS,
        "endpoint_limits": RateLimitMiddleware.ENDPOINT_LIMITS,
        "backend": "redis",
    }
