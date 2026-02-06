"""
Unit tests for rate limiting dependency.

Tests cover:
- Rate limit enforcement (task 6.2)
- Rate limit headers (task 6.3)
- Per-endpoint rate limits (task 6.4)
- Per-user rate limiting (task 6.5)
- Rate limit reset (task 6.6)
"""

import time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request

from api.dependencies.rate_limit import RateLimitService, TokenBucket, check_rate_limit

# ============================================================================
# TokenBucket Tests
# ============================================================================


def test_token_bucket_consume_success():
    """Test successful token consumption from bucket."""
    bucket = TokenBucket(
        capacity=10,
        refill_rate=1.0,  # 1 token per second
        tokens=10.0,
        last_refill=time.time(),
    )

    assert bucket.consume(1) is True
    assert bucket.remaining_tokens() == 9


def test_token_bucket_consume_failure():
    """Test token consumption failure when bucket is empty."""
    bucket = TokenBucket(
        capacity=10,
        refill_rate=1.0,
        tokens=0.0,
        last_refill=time.time(),
    )

    assert bucket.consume(1) is False
    assert bucket.remaining_tokens() == 0


def test_token_bucket_refill():
    """Test bucket refills over time."""
    now = time.time()
    bucket = TokenBucket(
        capacity=10,
        refill_rate=1.0,  # 1 token per second
        tokens=5.0,
        last_refill=now - 2.0,  # 2 seconds ago
    )

    # Consume should trigger refill (5 + 2 = 7 tokens)
    assert bucket.consume(1) is True
    assert bucket.remaining_tokens() == 6


def test_token_bucket_max_capacity():
    """Test bucket doesn't exceed capacity during refill."""
    now = time.time()
    bucket = TokenBucket(
        capacity=10,
        refill_rate=1.0,
        tokens=8.0,
        last_refill=now - 5.0,  # 5 seconds ago - should only refill to 10
    )

    # Should refill to capacity (10), not 13
    assert bucket.consume(1) is True
    assert bucket.remaining_tokens() == 9


def test_token_bucket_reset_time():
    """Test reset time calculation."""
    bucket = TokenBucket(
        capacity=10,
        refill_rate=2.0,  # 2 tokens per second
        tokens=4.0,
        last_refill=time.time(),
    )

    # Need 6 more tokens, at 2 per second = 3 seconds
    assert bucket.reset_time() == 3.0


# ============================================================================
# RateLimitService Tests
# ============================================================================


def test_rate_limit_enforced():
    """Test that rate limit is enforced (task 6.2)."""
    service = RateLimitService(
        default_rate_limit=5,  # 5 requests per minute
        default_burst=5,
    )

    # Create mock request
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # First 5 requests should succeed
    for i in range(5):
        info = service.check_rate_limit(request)
        assert info.allowed is True
        assert info.remaining == 4 - i

    # 6th request should be rate limited
    info = service.check_rate_limit(request)
    assert info.allowed is False
    assert info.remaining == 0


def test_rate_limit_headers():
    """Test that rate limit headers are set correctly (task 6.3)."""
    service = RateLimitService(
        default_rate_limit=10,
        default_burst=10,
    )

    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # Make first request
    info = service.check_rate_limit(request)

    assert info.allowed is True
    assert info.limit == 10
    assert info.remaining == 9
    assert info.reset_time > time.time()


def test_per_endpoint_limits():
    """Test different rate limits for different endpoints (task 6.4)."""
    service = RateLimitService(
        default_rate_limit=100,
        default_burst=100,
        expensive_rate_limit=5,
        expensive_burst=5,
    )

    # Regular endpoint
    regular_request = MagicMock(spec=Request)
    regular_request.url.path = "/test"
    regular_request.headers.get.return_value = None
    regular_request.client.host = "127.0.0.1"

    # Expensive endpoint
    expensive_request = MagicMock(spec=Request)
    expensive_request.url.path = "/tools/analyze_call"
    expensive_request.headers.get.return_value = None
    expensive_request.client.host = "127.0.0.1"

    # Regular endpoint should have higher limit
    info = service.check_rate_limit(regular_request)
    assert info.limit == 100

    # Expensive endpoint should have lower limit
    info = service.check_rate_limit(expensive_request)
    assert info.limit == 5


def test_per_user_limits():
    """Test rate limits are tracked separately per user (task 6.5)."""
    service = RateLimitService(
        default_rate_limit=5,
        default_burst=5,
    )

    # User 1
    request1 = MagicMock(spec=Request)
    request1.url.path = "/test"
    request1.headers.get.return_value = "user1@example.com"
    request1.client.host = "127.0.0.1"

    # User 2
    request2 = MagicMock(spec=Request)
    request2.url.path = "/test"
    request2.headers.get.return_value = "user2@example.com"
    request2.client.host = "127.0.0.2"

    # Exhaust user1's limit
    for _ in range(5):
        info = service.check_rate_limit(request1)
        assert info.allowed is True

    # User1 should be rate limited
    info = service.check_rate_limit(request1)
    assert info.allowed is False

    # User2 should still have full quota
    info = service.check_rate_limit(request2)
    assert info.allowed is True
    assert info.remaining == 4


def test_rate_limit_reset():
    """Test rate limit resets over time (task 6.6)."""
    service = RateLimitService(
        default_rate_limit=60,  # 60 per minute = 1 per second
        default_burst=2,
    )

    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # Consume all tokens
    for _ in range(2):
        info = service.check_rate_limit(request)
        assert info.allowed is True

    # Should be rate limited
    info = service.check_rate_limit(request)
    assert info.allowed is False

    # Wait for 1 second (should refill 1 token)
    time.sleep(1.1)

    # Should now have 1 token available
    info = service.check_rate_limit(request)
    assert info.allowed is True


def test_user_identifier_priority():
    """Test user identification priority: email > API key > IP."""
    service = RateLimitService()

    # Email header present
    request = MagicMock(spec=Request)
    request.headers.get.side_effect = lambda k: "user@example.com" if k == "X-User-Email" else None
    request.client.host = "127.0.0.1"
    user_id = service._get_user_identifier(request)
    assert user_id == "user:user@example.com"

    # API key present (no email)
    request = MagicMock(spec=Request)
    request.headers.get.side_effect = lambda k: "sk-1234567890abcdef" if k == "X-API-Key" else None
    request.client.host = "127.0.0.1"
    user_id = service._get_user_identifier(request)
    assert user_id == "key:sk-1234567890abc"

    # Only IP (no email or API key)
    request = MagicMock(spec=Request)
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"
    user_id = service._get_user_identifier(request)
    assert user_id == "ip:127.0.0.1"


def test_health_check_skips_rate_limit():
    """Test health check endpoints skip rate limiting."""
    service = RateLimitService(default_rate_limit=1, default_burst=1)

    request = MagicMock(spec=Request)
    request.url.path = "/health"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # Should never rate limit health checks
    for _ in range(100):
        info = service.check_rate_limit(request)
        assert info.allowed is True


def test_bucket_cleanup():
    """Test cleanup of old rate limit buckets."""
    service = RateLimitService()

    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # Create a bucket
    service.check_rate_limit(request)
    assert len(service.user_buckets) == 1

    # Set last_refill to old time
    bucket_key = list(service.user_buckets.keys())[0]
    service.user_buckets[bucket_key].last_refill = time.time() - 7200  # 2 hours ago

    # Cleanup buckets older than 1 hour
    service.cleanup_old_buckets(max_age_seconds=3600)

    # Bucket should be removed
    assert len(service.user_buckets) == 0


# ============================================================================
# FastAPI Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_check_rate_limit_dependency_success():
    """Test rate limit dependency allows valid requests."""
    service = RateLimitService(default_rate_limit=10, default_burst=10)

    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # Should not raise exception
    info = await check_rate_limit(request, service)
    assert info.allowed is True
    assert info.remaining == 9


@pytest.mark.asyncio
async def test_check_rate_limit_dependency_blocked():
    """Test rate limit dependency raises HTTPException when blocked."""
    service = RateLimitService(default_rate_limit=1, default_burst=1)

    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = None
    request.client.host = "127.0.0.1"

    # First request succeeds
    await check_rate_limit(request, service)

    # Second request should raise 429
    with pytest.raises(HTTPException) as exc_info:
        await check_rate_limit(request, service)

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value.detail)
    assert "X-RateLimit-Limit" in exc_info.value.headers
    assert "Retry-After" in exc_info.value.headers


def test_expensive_endpoints_configuration():
    """Test expensive endpoints are correctly identified."""
    service = RateLimitService()

    # These should be identified as expensive
    expensive_paths = [
        "/tools/analyze_call",
        "/tools/analyze_opportunity",
        "/tools/get_learning_insights",
    ]

    for path in expensive_paths:
        request = MagicMock(spec=Request)
        request.url.path = path
        request.headers.get.return_value = None
        request.client.host = "127.0.0.1"

        bucket = service._get_rate_limit_bucket("test_user", path)
        # Expensive endpoints should have smaller capacity
        assert bucket.capacity == service.expensive_burst


def test_concurrent_requests_thread_safety():
    """Test thread safety of rate limit service."""
    import threading

    service = RateLimitService(default_rate_limit=100, default_burst=100)

    results = []
    errors = []

    def make_request():
        try:
            request = MagicMock(spec=Request)
            request.url.path = "/test"
            request.headers.get.return_value = None
            request.client.host = "127.0.0.1"

            info = service.check_rate_limit(request)
            results.append(info.allowed)
        except Exception as e:
            errors.append(e)

    # Create 50 concurrent requests
    threads = [threading.Thread(target=make_request) for _ in range(50)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # All requests should succeed (within limit)
    assert len(errors) == 0
    assert len(results) == 50
    assert all(results)
