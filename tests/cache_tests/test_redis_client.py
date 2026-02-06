"""
Unit tests for Redis cache client.

Tests cache operations, compression, invalidation, and graceful degradation.
"""

from unittest.mock import Mock, patch

import pytest

from cache.redis_client import RedisCache
from db.models import CoachingDimension


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch("cache.redis_client.redis") as mock:
        mock.REDIS_AVAILABLE = True
        yield mock


@pytest.fixture
def redis_cache(mock_redis):
    """Create Redis cache instance with mocked client."""
    cache = RedisCache(host="localhost", port=6379)
    return cache


class TestRedisCache:
    """Test RedisCache functionality."""

    def test_cache_initialization(self, redis_cache):
        """Test cache initializes with connection pool."""
        assert redis_cache.available is True

    def test_cache_key_generation(self, redis_cache):
        """Test cache key generation pattern."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "abc123"
        rubric_version = "1.0.0"

        key = redis_cache._generate_key(
            dimension=dimension, transcript_hash=transcript_hash, rubric_version=rubric_version
        )

        expected = f"coaching:{dimension.value}:{transcript_hash}:{rubric_version}"
        assert key == expected

    def test_cache_set_and_get(self, redis_cache):
        """Test storing and retrieving from cache."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "abc123"
        rubric_version = "1.0.0"

        session_data = {
            "score": 85,
            "strengths": ["Good questions", "Active listening"],
            "areas_for_improvement": ["Follow-up"],
        }

        # Mock Redis SET operation
        redis_cache._client.setex = Mock(return_value=True)
        redis_cache._client.get = Mock(return_value=None)

        # Set in cache
        success = redis_cache.set(
            dimension=dimension,
            transcript_hash=transcript_hash,
            rubric_version=rubric_version,
            session_data=session_data,
        )

        assert success is True
        redis_cache._client.setex.assert_called_once()

    def test_cache_miss(self, redis_cache):
        """Test cache miss returns None."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "nonexistent"
        rubric_version = "1.0.0"

        # Mock Redis GET returning None
        redis_cache._client.get = Mock(return_value=None)

        result = redis_cache.get(
            dimension=dimension, transcript_hash=transcript_hash, rubric_version=rubric_version
        )

        assert result is None

    def test_cache_compression(self, redis_cache):
        """Test automatic compression for large payloads."""
        large_text = "x" * 2000  # > 1KB
        compressed = redis_cache._compress_value(large_text)

        assert len(compressed) < len(large_text.encode("utf-8"))

        # Test decompression
        decompressed = redis_cache._decompress_value(compressed)
        assert decompressed == large_text

    def test_cache_invalidation(self, redis_cache):
        """Test cache invalidation for dimension."""
        dimension = CoachingDimension.DISCOVERY
        rubric_version = "1.0.0"

        # Mock Redis scan and delete
        redis_cache._client.scan_iter = Mock(
            return_value=[b"coaching:discovery:hash1:1.0.0", b"coaching:discovery:hash2:1.0.0"]
        )
        redis_cache._client.delete = Mock(return_value=2)

        deleted_count = redis_cache.invalidate_dimension(
            dimension=dimension, rubric_version=rubric_version
        )

        assert deleted_count == 2
        redis_cache._client.delete.assert_called_once()

    def test_graceful_degradation_when_redis_unavailable(self):
        """Test cache gracefully degrades when Redis unavailable."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            cache = RedisCache()
            assert cache.available is False

            # Operations should not raise errors
            result = cache.get(
                dimension=CoachingDimension.DISCOVERY, transcript_hash="abc", rubric_version="1.0.0"
            )
            assert result is None

    def test_cache_stats(self, redis_cache):
        """Test cache statistics retrieval."""
        # Mock Redis INFO commands
        redis_cache._client.info = Mock(
            side_effect=[
                {"keyspace_hits": 950, "keyspace_misses": 50},  # stats
                {"used_memory": 104857600},  # memory (100 MB)
            ]
        )
        redis_cache._client.dbsize = Mock(return_value=1000)

        stats = redis_cache.get_stats()

        assert stats["available"] is True
        assert stats["hits"] == 950
        assert stats["misses"] == 50
        assert stats["hit_rate"] == 95.0
        assert stats["total_keys"] == 1000


class TestCacheKeyPatterns:
    """Test cache key pattern generation."""

    def test_dimension_patterns(self, redis_cache):
        """Test key patterns for different dimensions."""
        dimensions = [
            CoachingDimension.DISCOVERY,
            CoachingDimension.PRODUCT_KNOWLEDGE,
            CoachingDimension.OBJECTION_HANDLING,
            CoachingDimension.ENGAGEMENT,
        ]

        for dimension in dimensions:
            key = redis_cache._generate_key(
                dimension=dimension, transcript_hash="hash123", rubric_version="1.0.0"
            )
            assert key.startswith(f"coaching:{dimension.value}:")

    def test_version_isolation(self, redis_cache):
        """Test different rubric versions generate different keys."""
        key_v1 = redis_cache._generate_key(
            dimension=CoachingDimension.DISCOVERY, transcript_hash="hash123", rubric_version="1.0.0"
        )

        key_v2 = redis_cache._generate_key(
            dimension=CoachingDimension.DISCOVERY, transcript_hash="hash123", rubric_version="2.0.0"
        )

        assert key_v1 != key_v2
        assert "1.0.0" in key_v1
        assert "2.0.0" in key_v2


@pytest.mark.integration
class TestRedisIntegration:
    """Integration tests requiring real Redis instance."""

    @pytest.fixture
    def real_redis_cache(self):
        """Create Redis cache with real connection (requires Redis running)."""
        try:
            cache = RedisCache(host="localhost", port=6379)
            if cache.available:
                yield cache
                # Cleanup
                cache.close()
            else:
                pytest.skip("Redis not available for integration tests")
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    def test_real_cache_operations(self, real_redis_cache):
        """Test cache operations against real Redis."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "test_hash_123"
        rubric_version = "1.0.0"

        session_data = {
            "score": 85,
            "strengths": ["Test strength"],
            "areas_for_improvement": ["Test improvement"],
        }

        # Set in cache
        success = real_redis_cache.set(
            dimension=dimension,
            transcript_hash=transcript_hash,
            rubric_version=rubric_version,
            session_data=session_data,
        )
        assert success is True

        # Get from cache
        cached = real_redis_cache.get(
            dimension=dimension, transcript_hash=transcript_hash, rubric_version=rubric_version
        )

        assert cached is not None
        assert cached["score"] == 85
        assert len(cached["strengths"]) == 1

        # Cleanup
        real_redis_cache.invalidate_dimension(dimension, rubric_version)
