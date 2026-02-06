"""
Cache Performance Benchmarks

Measures Redis cache performance including:
- Cache hit/miss rates
- Operation latency
- Memory usage patterns
"""
import pytest
import json
from typing import Dict, Any
from unittest.mock import MagicMock, patch
from cache.redis_client import RedisClient


@pytest.fixture
def redis_client():
    """Mock Redis client for benchmarking."""
    return MagicMock(spec=RedisClient)


@pytest.fixture
def sample_cached_objects():
    """Sample objects to cache."""
    return {
        "call_analysis": {
            "call_id": "call_000001",
            "engagement_score": 85,
            "discovery_score": 78,
            "objection_handling_score": 82,
            "strengths": ["Clear value proposition", "Good discovery questions"],
            "areas_for_improvement": ["Product knowledge", "Closing techniques"],
            "transcript_snippets": [
                {"time": "00:15", "speaker": "rep", "text": "Example quote"},
            ],
        },
        "rep_insights": {
            "rep_email": "rep_01@example.com",
            "avg_score": 78,
            "score_trend": 2.5,
            "skill_gaps": ["Product knowledge", "Objection handling"],
            "improvement_areas": ["Discovery", "Closing"],
            "calls_analyzed": 50,
        },
        "search_results": {
            "total": 100,
            "calls": [
                {
                    "call_id": f"call_{i:06d}",
                    "rep": "rep_01@example.com",
                    "date": "2025-01-15",
                    "score": 75 + (i % 20),
                }
                for i in range(20)
            ],
        },
    }


class TestCacheBenchmarks:
    """Cache operation performance benchmarks."""

    def test_cache_set_operation(self, benchmark, redis_client, sample_cached_objects):
        """Benchmark cache SET operation."""
        call_analysis = sample_cached_objects["call_analysis"]
        cache_key = f"call_analysis:call_000001"

        def set_cache():
            redis_client.set(cache_key, json.dumps(call_analysis), ttl=3600)

        benchmark(set_cache)

    def test_cache_get_operation(self, benchmark, redis_client, sample_cached_objects):
        """Benchmark cache GET operation."""
        call_analysis = sample_cached_objects["call_analysis"]
        cache_key = f"call_analysis:call_000001"
        redis_client.get.return_value = json.dumps(call_analysis)

        def get_cache():
            data = redis_client.get(cache_key)
            return json.loads(data) if data else None

        benchmark(get_cache)

    def test_cache_get_miss(self, benchmark, redis_client):
        """Benchmark cache miss (key not found)."""
        redis_client.get.return_value = None

        def get_cache_miss():
            return redis_client.get("nonexistent_key")

        benchmark(get_cache_miss)

    def test_cache_delete_operation(self, benchmark, redis_client):
        """Benchmark cache DELETE operation."""
        cache_key = "cache_key_to_delete"

        def delete_cache():
            redis_client.delete(cache_key)

        benchmark(delete_cache)

    def test_cache_exists_check(self, benchmark, redis_client):
        """Benchmark cache EXISTS check."""
        cache_key = "cache_key_to_check"
        redis_client.exists.return_value = True

        def check_exists():
            return redis_client.exists(cache_key)

        benchmark(check_exists)

    def test_cache_ttl_expiry(self, benchmark, redis_client):
        """Benchmark TTL (time-to-live) check."""
        cache_key = "cache_with_ttl"
        redis_client.ttl.return_value = 3599

        def check_ttl():
            return redis_client.ttl(cache_key)

        benchmark(check_ttl)

    def test_large_object_serialization(self, benchmark, sample_cached_objects):
        """Benchmark serialization of large cached objects."""
        search_results = sample_cached_objects["search_results"]

        def serialize():
            return json.dumps(search_results)

        benchmark(serialize)

    def test_large_object_deserialization(self, benchmark, sample_cached_objects):
        """Benchmark deserialization of large cached objects."""
        search_results = sample_cached_objects["search_results"]
        serialized = json.dumps(search_results)

        def deserialize():
            return json.loads(serialized)

        benchmark(deserialize)

    def test_cache_key_generation(self, benchmark):
        """Benchmark cache key generation."""
        call_id = "call_000001"

        def generate_key():
            return f"call_analysis:{call_id}"

        benchmark(generate_key)

    def test_batch_cache_operations(self, benchmark, redis_client):
        """Benchmark batch cache operations."""
        cache_keys = [f"key_{i}" for i in range(100)]
        redis_client.mget.return_value = {k: f"value_{i}" for i, k in enumerate(cache_keys)}

        def batch_get():
            return redis_client.mget(cache_keys)

        benchmark(batch_get)


class TestCacheHitRate:
    """Benchmarks for cache hit rate analysis."""

    def test_cache_hit_scenario(self, benchmark, redis_client, sample_cached_objects):
        """Benchmark repeated access with high hit rate."""
        call_analysis = sample_cached_objects["call_analysis"]
        redis_client.get.return_value = json.dumps(call_analysis)

        def repeated_access():
            for _ in range(10):
                data = redis_client.get("call_analysis:call_000001")
                json.loads(data)

        benchmark(repeated_access)

    def test_cache_mixed_hit_miss(self, benchmark, redis_client, sample_cached_objects):
        """Benchmark mixed hit/miss scenario."""
        call_analysis = sample_cached_objects["call_analysis"]

        def mixed_access(call_id):
            if call_id < 5:
                redis_client.get.return_value = json.dumps(call_analysis)
                data = redis_client.get(f"call_{call_id}")
            else:
                redis_client.get.return_value = None
                data = redis_client.get(f"call_{call_id}")
            return data

        def benchmark_func():
            for i in range(10):
                mixed_access(i)

        benchmark(benchmark_func)


class TestCacheEviction:
    """Benchmarks for cache eviction and memory pressure."""

    def test_cache_invalidation(self, benchmark, redis_client):
        """Benchmark cache invalidation."""
        def invalidate():
            redis_client.delete("call_analysis:call_000001")
            redis_client.delete("call_analysis:call_000002")
            redis_client.delete("call_analysis:call_000003")

        benchmark(invalidate)

    def test_pattern_based_invalidation(self, benchmark, redis_client):
        """Benchmark pattern-based cache invalidation."""
        redis_client.delete_pattern.return_value = 100

        def invalidate_pattern():
            return redis_client.delete_pattern("call_analysis:*")

        benchmark(invalidate_pattern)

    def test_cache_memory_management(self, benchmark, redis_client):
        """Benchmark cache memory stats retrieval."""
        redis_client.info.return_value = {
            "used_memory": 1024 * 1024 * 100,  # 100MB
            "used_memory_peak": 1024 * 1024 * 150,
            "evicted_keys": 1000,
        }

        def get_memory_stats():
            return redis_client.info()

        benchmark(get_memory_stats)


class TestCacheCompression:
    """Benchmarks for cache data compression."""

    def test_compression_vs_no_compression(self, benchmark, sample_cached_objects):
        """Benchmark compression overhead."""
        import gzip

        search_results = sample_cached_objects["search_results"]
        serialized = json.dumps(search_results)

        def compress():
            return gzip.compress(serialized.encode())

        benchmark(compress)

    def test_decompression_performance(self, benchmark, sample_cached_objects):
        """Benchmark decompression performance."""
        import gzip

        search_results = sample_cached_objects["search_results"]
        serialized = json.dumps(search_results)
        compressed = gzip.compress(serialized.encode())

        def decompress():
            return gzip.decompress(compressed).decode()

        benchmark(decompress)


class TestCacheWarming:
    """Benchmarks for cache warming strategies."""

    def test_sequential_cache_warming(self, benchmark, redis_client, sample_cached_objects):
        """Benchmark sequential cache warming."""
        call_analysis = sample_cached_objects["call_analysis"]

        def warm_cache():
            for i in range(50):
                key = f"call_analysis:call_{i:06d}"
                redis_client.set(key, json.dumps(call_analysis), ttl=3600)

        benchmark(warm_cache)

    def test_batch_cache_warming(self, benchmark, redis_client):
        """Benchmark batch cache warming."""
        def warm_cache_batch():
            cache_data = {f"key_{i}": f"value_{i}" for i in range(100)}
            redis_client.mset(cache_data)

        benchmark(warm_cache_batch)
