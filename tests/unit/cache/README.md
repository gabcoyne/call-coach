# Cache Module Unit Tests

This directory contains comprehensive unit tests for the Redis cache module following TDD principles.

## Test Coverage

### Task 3.1: Redis Available Operations (`TestRedisAvailableOperations`)

Tests Redis cache operations when Redis is available and functioning correctly.

- `test_redis_initialization_successful` - Verifies successful Redis connection and initialization
- `test_redis_set_operation` - Tests storing values in cache with TTL
- `test_redis_get_operation_hit` - Tests retrieving cached values (cache hit)
- `test_redis_get_operation_miss` - Tests cache miss scenario returns None
- `test_redis_stats_available` - Tests retrieval of cache statistics (hits, misses, memory)

### Task 3.2: Redis Unavailable Fallback (`TestRedisUnavailableFallback`)

Tests graceful degradation when Redis is unavailable.

- `test_redis_library_not_installed` - Handles missing Redis library gracefully
- `test_redis_connection_failure` - Handles connection failures without crashing
- `test_get_returns_none_when_unavailable` - Get operations return None safely
- `test_set_returns_false_when_unavailable` - Set operations return False safely
- `test_invalidate_returns_zero_when_unavailable` - Invalidation returns 0 safely
- `test_stats_show_unavailable` - Stats indicate unavailable status
- `test_redis_operation_error_handled_gracefully` - Runtime errors handled without exceptions

### Task 3.3: Cache Key Deterministic (`TestCacheKeyDeterministic`)

Tests cache key generation consistency and uniqueness.

- `test_same_inputs_produce_same_key` - Identical inputs generate identical keys
- `test_different_dimensions_produce_different_keys` - Different dimensions create unique keys
- `test_different_transcript_hashes_produce_different_keys` - Different transcripts create unique keys
- `test_different_rubric_versions_produce_different_keys` - Different versions create unique keys
- `test_key_pattern_format` - Verifies expected key pattern format
- `test_all_dimensions_produce_valid_keys` - All coaching dimensions generate valid keys

### Task 3.4: Invalidate Dimension (`TestInvalidateDimension`)

Tests cache invalidation by dimension and version.

- `test_invalidate_specific_dimension_and_version` - Invalidates specific dimension+version
- `test_invalidate_all_versions_for_dimension` - Invalidates all versions for a dimension
- `test_invalidate_dimension_no_matching_keys` - Handles no matching keys gracefully
- `test_invalidate_different_dimensions_isolated` - Dimensions are isolated in invalidation
- `test_invalidate_handles_redis_error` - Handles Redis errors during invalidation
- `test_invalidate_batch_deletion` - Efficient batch deletion of multiple keys

## Additional Test Coverage

### Compression Tests (`TestCacheCompressionIntegration`)

Tests automatic compression for large payloads.

- `test_compress_large_value` - Large values are compressed
- `test_decompress_compressed_value` - Compressed values decompress correctly
- `test_small_value_not_compressed` - Small values skip compression (optimization)
- `test_decompress_uncompressed_value` - Uncompressed values decode correctly

### Singleton Tests (`TestGetRedisCacheSingleton`)

Tests global cache instance management.

- `test_get_redis_cache_creates_instance` - Creates cache instance on first call
- `test_get_redis_cache_returns_singleton` - Returns same instance on subsequent calls
- `test_get_redis_cache_uses_environment_variables` - Respects environment configuration

## Running Tests

Run all cache tests:

```bash
.venv/bin/python -m pytest tests/unit/cache/test_cache.py -v
```

Run specific test class:

```bash
.venv/bin/python -m pytest tests/unit/cache/test_cache.py::TestRedisAvailableOperations -v
```

Run with coverage (if pytest-cov is installed):

```bash
.venv/bin/python -m pytest tests/unit/cache/test_cache.py --cov=cache.redis_client --cov-report=term-missing
```

## Test Results

All 31 tests pass successfully:

- 5 tests for Redis available operations (Task 3.1)
- 7 tests for Redis unavailable fallback (Task 3.2)
- 6 tests for cache key determinism (Task 3.3)
- 6 tests for dimension invalidation (Task 3.4)
- 4 tests for compression functionality
- 3 tests for singleton pattern

Total execution time: ~0.23 seconds

## TDD Approach

These tests were written following Test-Driven Development principles:

1. Tests written before or alongside implementation
2. Comprehensive coverage of happy paths, edge cases, and error conditions
3. Tests are isolated and independent (no shared state)
4. Mocks used appropriately to avoid external dependencies
5. Clear test names describing what is being tested
6. Tests are fast and deterministic

## Dependencies

- `pytest` - Test framework
- `unittest.mock` - Mocking Redis client
- `cache.redis_client` - Module under test
- `db.models` - CoachingDimension enum
