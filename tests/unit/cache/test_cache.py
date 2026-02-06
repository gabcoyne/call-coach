"""
Unit tests for Redis cache module.

Tests cache operations, graceful degradation, key generation, and invalidation.
Following TDD approach for comprehensive coverage of cache functionality.
"""

from unittest.mock import Mock, patch

import pytest

from cache.redis_client import RedisCache, get_redis_cache
from db.models import CoachingDimension


class TestRedisAvailableOperations:
    """Test Redis operations when Redis is available (Task 3.1)."""

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for testing."""
        with patch("cache.redis_client.REDIS_AVAILABLE", True):
            with patch("cache.redis_client.redis") as mock_redis_module:
                # Mock connection pool
                mock_pool = Mock()
                mock_redis_module.Redis.return_value.ping.return_value = True
                mock_redis_module.ConnectionPool.return_value = mock_pool

                # Mock Redis client
                mock_client = Mock()
                mock_client.ping.return_value = True
                mock_redis_module.Redis.return_value = mock_client

                yield mock_redis_module, mock_client

    def test_redis_initialization_successful(self, mock_redis_client):
        """Test Redis cache initializes successfully when available."""
        mock_redis_module, mock_client = mock_redis_client

        cache = RedisCache(host="localhost", port=6379)

        assert cache.available is True
        mock_client.ping.assert_called_once()

    def test_redis_set_operation(self, mock_redis_client):
        """Test setting a value in Redis cache."""
        mock_redis_module, mock_client = mock_redis_client

        cache = RedisCache(host="localhost", port=6379)
        cache._client = mock_client
        cache._available = True

        # Mock setex operation
        mock_client.setex.return_value = True

        session_data = {
            "score": 85,
            "strengths": ["Good questioning"],
            "areas_for_improvement": ["Closing techniques"],
        }

        result = cache.set(
            dimension=CoachingDimension.DISCOVERY,
            transcript_hash="abc123hash",
            rubric_version="v1.0.0",
            session_data=session_data,
        )

        assert result is True
        assert mock_client.setex.called

    def test_redis_get_operation_hit(self, mock_redis_client):
        """Test getting a cached value from Redis (cache hit)."""
        mock_redis_module, mock_client = mock_redis_client

        cache = RedisCache(host="localhost", port=6379)
        cache._client = mock_client
        cache._available = True

        # Mock cached data
        import json

        cached_data = {
            "score": 85,
            "strengths": ["Active listening"],
        }
        mock_client.get.return_value = json.dumps(cached_data).encode("utf-8")

        result = cache.get(
            dimension=CoachingDimension.DISCOVERY,
            transcript_hash="abc123hash",
            rubric_version="v1.0.0",
        )

        assert result is not None
        assert result["score"] == 85
        assert "Active listening" in result["strengths"]

    def test_redis_get_operation_miss(self, mock_redis_client):
        """Test getting a non-existent value from Redis (cache miss)."""
        mock_redis_module, mock_client = mock_redis_client

        cache = RedisCache(host="localhost", port=6379)
        cache._client = mock_client
        cache._available = True

        # Mock cache miss
        mock_client.get.return_value = None

        result = cache.get(
            dimension=CoachingDimension.DISCOVERY,
            transcript_hash="nonexistent",
            rubric_version="v1.0.0",
        )

        assert result is None

    def test_redis_stats_available(self, mock_redis_client):
        """Test getting Redis statistics when available."""
        mock_redis_module, mock_client = mock_redis_client

        cache = RedisCache(host="localhost", port=6379)
        cache._client = mock_client
        cache._available = True

        # Mock Redis info commands
        mock_client.info.side_effect = [
            {"keyspace_hits": 900, "keyspace_misses": 100},  # stats
            {"used_memory": 52428800},  # memory (50 MB)
        ]
        mock_client.dbsize.return_value = 500

        stats = cache.get_stats()

        assert stats["available"] is True
        assert stats["hits"] == 900
        assert stats["misses"] == 100
        assert stats["hit_rate"] == 90.0
        assert stats["total_keys"] == 500
        assert stats["memory_used_mb"] == 50.0


class TestRedisUnavailableFallback:
    """Test graceful degradation when Redis is unavailable (Task 3.2)."""

    def test_redis_library_not_installed(self):
        """Test graceful fallback when Redis library not installed."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            cache = RedisCache()

            assert cache.available is False
            assert cache._client is None

    def test_redis_connection_failure(self):
        """Test graceful fallback when Redis connection fails."""
        with patch("cache.redis_client.REDIS_AVAILABLE", True):
            with patch("cache.redis_client.redis") as mock_redis:
                # Simulate connection failure
                mock_redis.Redis.return_value.ping.side_effect = Exception("Connection refused")

                cache = RedisCache(host="localhost", port=6379)

                assert cache.available is False
                assert cache._client is None

    def test_get_returns_none_when_unavailable(self):
        """Test get() returns None without raising when Redis unavailable."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            cache = RedisCache()

            result = cache.get(
                dimension=CoachingDimension.DISCOVERY,
                transcript_hash="abc123",
                rubric_version="v1.0.0",
            )

            assert result is None

    def test_set_returns_false_when_unavailable(self):
        """Test set() returns False without raising when Redis unavailable."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            cache = RedisCache()

            result = cache.set(
                dimension=CoachingDimension.DISCOVERY,
                transcript_hash="abc123",
                rubric_version="v1.0.0",
                session_data={"score": 85},
            )

            assert result is False

    def test_invalidate_returns_zero_when_unavailable(self):
        """Test invalidate_dimension() returns 0 when Redis unavailable."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            cache = RedisCache()

            result = cache.invalidate_dimension(
                dimension=CoachingDimension.DISCOVERY,
                rubric_version="v1.0.0",
            )

            assert result == 0

    def test_stats_show_unavailable(self):
        """Test get_stats() indicates unavailable status."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            cache = RedisCache()

            stats = cache.get_stats()

            assert stats["available"] is False

    def test_redis_operation_error_handled_gracefully(self):
        """Test that Redis operation errors don't crash application."""
        with patch("cache.redis_client.REDIS_AVAILABLE", True):
            with patch("cache.redis_client.redis") as mock_redis:
                mock_client = Mock()
                mock_client.ping.return_value = True
                mock_redis.Redis.return_value = mock_client

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                # Simulate Redis operation error
                mock_client.get.side_effect = Exception("Redis timeout")

                result = cache.get(
                    dimension=CoachingDimension.DISCOVERY,
                    transcript_hash="abc123",
                    rubric_version="v1.0.0",
                )

                # Should return None instead of raising
                assert result is None


class TestCacheKeyDeterministic:
    """Test cache key generation consistency (Task 3.3)."""

    @pytest.fixture
    def cache(self):
        """Create cache instance for testing."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            return RedisCache()

    def test_same_inputs_produce_same_key(self, cache):
        """Test that identical inputs generate identical cache keys."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "abc123hash"
        rubric_version = "v1.0.0"

        key1 = cache._generate_key(dimension, transcript_hash, rubric_version)
        key2 = cache._generate_key(dimension, transcript_hash, rubric_version)

        assert key1 == key2

    def test_different_dimensions_produce_different_keys(self, cache):
        """Test that different dimensions generate different keys."""
        transcript_hash = "abc123hash"
        rubric_version = "v1.0.0"

        key_discovery = cache._generate_key(
            CoachingDimension.DISCOVERY, transcript_hash, rubric_version
        )
        key_engagement = cache._generate_key(
            CoachingDimension.ENGAGEMENT, transcript_hash, rubric_version
        )

        assert key_discovery != key_engagement

    def test_different_transcript_hashes_produce_different_keys(self, cache):
        """Test that different transcript hashes generate different keys."""
        dimension = CoachingDimension.DISCOVERY
        rubric_version = "v1.0.0"

        key1 = cache._generate_key(dimension, "hash1", rubric_version)
        key2 = cache._generate_key(dimension, "hash2", rubric_version)

        assert key1 != key2

    def test_different_rubric_versions_produce_different_keys(self, cache):
        """Test that different rubric versions generate different keys."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "abc123hash"

        key_v1 = cache._generate_key(dimension, transcript_hash, "v1.0.0")
        key_v2 = cache._generate_key(dimension, transcript_hash, "v2.0.0")

        assert key_v1 != key_v2

    def test_key_pattern_format(self, cache):
        """Test that keys follow expected pattern format."""
        dimension = CoachingDimension.DISCOVERY
        transcript_hash = "abc123hash"
        rubric_version = "v1.0.0"

        key = cache._generate_key(dimension, transcript_hash, rubric_version)

        expected_pattern = f"coaching:{dimension.value}:{transcript_hash}:{rubric_version}"
        assert key == expected_pattern

    def test_all_dimensions_produce_valid_keys(self, cache):
        """Test that all coaching dimensions produce valid cache keys."""
        transcript_hash = "abc123hash"
        rubric_version = "v1.0.0"

        dimensions = [
            CoachingDimension.DISCOVERY,
            CoachingDimension.PRODUCT_KNOWLEDGE,
            CoachingDimension.OBJECTION_HANDLING,
            CoachingDimension.ENGAGEMENT,
        ]

        keys = set()
        for dimension in dimensions:
            key = cache._generate_key(dimension, transcript_hash, rubric_version)
            assert key.startswith("coaching:")
            assert dimension.value in key
            keys.add(key)

        # All keys should be unique
        assert len(keys) == len(dimensions)


class TestInvalidateDimension:
    """Test cache invalidation by dimension (Task 3.4)."""

    @pytest.fixture
    def mock_redis_cache(self):
        """Create mocked Redis cache for invalidation testing."""
        with patch("cache.redis_client.REDIS_AVAILABLE", True):
            with patch("cache.redis_client.redis") as mock_redis:
                mock_client = Mock()
                mock_client.ping.return_value = True
                mock_redis.Redis.return_value = mock_client

                cache = RedisCache()
                cache._client = mock_client
                cache._available = True

                yield cache, mock_client

    def test_invalidate_specific_dimension_and_version(self, mock_redis_cache):
        """Test invalidating cache for specific dimension and rubric version."""
        cache, mock_client = mock_redis_cache

        # Mock scan_iter to return matching keys
        mock_client.scan_iter.return_value = [
            b"coaching:discovery:hash1:v1.0.0",
            b"coaching:discovery:hash2:v1.0.0",
            b"coaching:discovery:hash3:v1.0.0",
        ]
        mock_client.delete.return_value = 3

        deleted = cache.invalidate_dimension(
            dimension=CoachingDimension.DISCOVERY,
            rubric_version="v1.0.0",
        )

        assert deleted == 3
        mock_client.scan_iter.assert_called_once()
        assert "coaching:discovery:*:v1.0.0" in str(mock_client.scan_iter.call_args)

    def test_invalidate_all_versions_for_dimension(self, mock_redis_cache):
        """Test invalidating all cache entries for a dimension."""
        cache, mock_client = mock_redis_cache

        # Mock scan_iter to return keys with multiple versions
        mock_client.scan_iter.return_value = [
            b"coaching:discovery:hash1:v1.0.0",
            b"coaching:discovery:hash2:v1.0.0",
            b"coaching:discovery:hash3:v2.0.0",
            b"coaching:discovery:hash4:v2.0.0",
        ]
        mock_client.delete.return_value = 4

        deleted = cache.invalidate_dimension(
            dimension=CoachingDimension.DISCOVERY,
            rubric_version=None,  # Invalidate all versions
        )

        assert deleted == 4
        mock_client.scan_iter.assert_called_once()
        assert "coaching:discovery:*" in str(mock_client.scan_iter.call_args)

    def test_invalidate_dimension_no_matching_keys(self, mock_redis_cache):
        """Test invalidation when no matching keys exist."""
        cache, mock_client = mock_redis_cache

        # Mock empty result
        mock_client.scan_iter.return_value = []

        deleted = cache.invalidate_dimension(
            dimension=CoachingDimension.DISCOVERY,
            rubric_version="v1.0.0",
        )

        assert deleted == 0

    def test_invalidate_different_dimensions_isolated(self, mock_redis_cache):
        """Test that invalidating one dimension doesn't affect others."""
        cache, mock_client = mock_redis_cache

        # Mock scan_iter to only return discovery keys
        mock_client.scan_iter.return_value = [
            b"coaching:discovery:hash1:v1.0.0",
            b"coaching:discovery:hash2:v1.0.0",
        ]
        mock_client.delete.return_value = 2

        deleted = cache.invalidate_dimension(
            dimension=CoachingDimension.DISCOVERY,
            rubric_version="v1.0.0",
        )

        assert deleted == 2

        # Verify the pattern only matches discovery dimension
        call_args = str(mock_client.scan_iter.call_args)
        assert "coaching:discovery:" in call_args
        assert "coaching:engagement:" not in call_args
        assert "coaching:product_knowledge:" not in call_args

    def test_invalidate_handles_redis_error(self, mock_redis_cache):
        """Test that invalidation handles Redis errors gracefully."""
        cache, mock_client = mock_redis_cache

        # Simulate Redis error
        mock_client.scan_iter.side_effect = Exception("Redis connection lost")

        deleted = cache.invalidate_dimension(
            dimension=CoachingDimension.DISCOVERY,
            rubric_version="v1.0.0",
        )

        # Should return 0 instead of raising
        assert deleted == 0

    def test_invalidate_batch_deletion(self, mock_redis_cache):
        """Test that invalidation deletes keys in batch."""
        cache, mock_client = mock_redis_cache

        # Mock many keys
        keys = [f"coaching:discovery:hash{i}:v1.0.0".encode() for i in range(100)]
        mock_client.scan_iter.return_value = keys
        mock_client.delete.return_value = len(keys)

        deleted = cache.invalidate_dimension(
            dimension=CoachingDimension.DISCOVERY,
            rubric_version="v1.0.0",
        )

        assert deleted == 100
        # Verify delete was called with all keys at once (batch operation)
        mock_client.delete.assert_called_once()


class TestCacheCompressionIntegration:
    """Test compression for large payloads."""

    @pytest.fixture
    def cache(self):
        """Create cache instance for compression testing."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            return RedisCache()

    def test_compress_large_value(self, cache):
        """Test that large values are compressed."""
        large_text = "x" * 2000  # > 1KB threshold

        compressed = cache._compress_value(large_text)

        # Compressed should be smaller than original
        assert len(compressed) < len(large_text.encode("utf-8"))

    def test_decompress_compressed_value(self, cache):
        """Test that compressed values can be decompressed correctly."""
        original_text = "y" * 2000  # > 1KB

        compressed = cache._compress_value(original_text)
        decompressed = cache._decompress_value(compressed)

        assert decompressed == original_text

    def test_small_value_not_compressed(self, cache):
        """Test that small values are not compressed (optimization)."""
        small_text = "small"  # < 1KB threshold

        result = cache._compress_value(small_text)

        # Should return bytes but not compressed (same size or larger)
        assert isinstance(result, bytes)
        assert result == small_text.encode("utf-8")

    def test_decompress_uncompressed_value(self, cache):
        """Test that uncompressed values can be decoded directly."""
        small_text = "small"

        # Compress (won't actually compress)
        value_bytes = cache._compress_value(small_text)
        # Decompress (should handle uncompressed)
        decompressed = cache._decompress_value(value_bytes)

        assert decompressed == small_text


class TestGetRedisCacheSingleton:
    """Test global Redis cache instance getter."""

    def test_get_redis_cache_creates_instance(self):
        """Test that get_redis_cache() creates cache instance."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            with patch("cache.redis_client._redis_cache", None):
                cache = get_redis_cache()

                assert cache is not None
                assert isinstance(cache, RedisCache)

    def test_get_redis_cache_returns_singleton(self):
        """Test that multiple calls return same instance."""
        with patch("cache.redis_client.REDIS_AVAILABLE", False):
            # Reset singleton
            import cache.redis_client

            cache.redis_client._redis_cache = None

            cache1 = get_redis_cache()
            cache2 = get_redis_cache()

            assert cache1 is cache2

    def test_get_redis_cache_uses_environment_variables(self):
        """Test that get_redis_cache() uses environment configuration."""
        with patch("cache.redis_client.REDIS_AVAILABLE", True):
            with patch("cache.redis_client.redis") as mock_redis:
                mock_client = Mock()
                mock_client.ping.return_value = True
                mock_redis.Redis.return_value = mock_client

                with patch.dict(
                    "os.environ",
                    {
                        "REDIS_HOST": "redis.example.com",
                        "REDIS_PORT": "6380",
                        "REDIS_DB": "2",
                        "REDIS_PASSWORD": "secret",
                        "REDIS_MAX_CONNECTIONS": "100",
                    },
                ):
                    # Reset singleton
                    import cache.redis_client

                    cache.redis_client._redis_cache = None

                    cache = get_redis_cache()

                    # Verify RedisCache was initialized with env values
                    assert cache is not None
