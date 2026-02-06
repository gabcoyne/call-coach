"""
Redis cache client for coaching sessions.
Provides distributed caching with connection pooling and automatic expiration.

Cache Strategy:
- Key Pattern: coaching:{dimension}:{transcript_hash}:{rubric_version}
- TTL: 90 days (configurable)
- Invalidation: Automatic on rubric version updates
- Compression: gzip for large payloads
"""

import gzip
import json
import logging
from datetime import timedelta
from typing import Any

try:
    import redis
    from redis.connection import ConnectionPool

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from coaching_mcp.shared import settings
from db.models import CoachingDimension

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis-backed cache for coaching sessions with connection pooling.

    Features:
    - Connection pooling for high concurrency
    - Automatic compression for payloads > 1KB
    - Cache hit/miss metrics
    - Graceful degradation when Redis unavailable
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        max_connections: int = 50,
        decode_responses: bool = False,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
    ):
        """
        Initialize Redis cache with connection pool.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if required)
            max_connections: Maximum connections in pool
            decode_responses: Decode byte responses to strings
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
        """
        if not REDIS_AVAILABLE:
            logger.warning(
                "Redis library not installed. Cache will be disabled. "
                "Install with: pip install redis"
            )
            self._client = None
            self._available = False
            return

        try:
            # Create connection pool
            self._pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                max_connections=max_connections,
                decode_responses=decode_responses,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
            )

            # Create Redis client
            self._client = redis.Redis(connection_pool=self._pool)

            # Test connection
            self._client.ping()
            self._available = True

            logger.info(
                f"Redis cache initialized: {host}:{port} " f"(pool size: {max_connections})"
            )

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Cache will be disabled. Falling back to database only.")
            self._client = None
            self._available = False

    @property
    def available(self) -> bool:
        """Check if Redis is available."""
        return self._available

    def _compress_value(self, value: str) -> bytes:
        """Compress value using gzip if larger than 1KB."""
        value_bytes = value.encode("utf-8")
        if len(value_bytes) > 1024:
            return gzip.compress(value_bytes)
        return value_bytes

    def _decompress_value(self, value: bytes) -> str:
        """Decompress value if it was compressed."""
        try:
            # Try decompression first
            return gzip.decompress(value).decode("utf-8")
        except (gzip.BadGzipFile, OSError):
            # Not compressed, decode directly
            return value.decode("utf-8")

    def _generate_key(
        self,
        dimension: CoachingDimension,
        transcript_hash: str,
        rubric_version: str,
    ) -> str:
        """
        Generate Redis key for coaching session.

        Key pattern: coaching:{dimension}:{transcript_hash}:{rubric_version}
        """
        return f"coaching:{dimension.value}:{transcript_hash}:{rubric_version}"

    def get(
        self,
        dimension: CoachingDimension,
        transcript_hash: str,
        rubric_version: str,
    ) -> dict[str, Any] | None:
        """
        Get cached coaching session.

        Args:
            dimension: Coaching dimension
            transcript_hash: SHA256 hash of transcript
            rubric_version: Rubric version

        Returns:
            Cached session data or None if cache miss
        """
        if not self._available:
            return None

        try:
            key = self._generate_key(dimension, transcript_hash, rubric_version)
            value = self._client.get(key)

            if value is None:
                logger.debug(f"Cache MISS: {key}")
                return None

            # Decompress and parse JSON
            json_str = self._decompress_value(value)
            data = json.loads(json_str)

            logger.info(f"Cache HIT: {key}")
            return data

        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    def set(
        self,
        dimension: CoachingDimension,
        transcript_hash: str,
        rubric_version: str,
        session_data: dict[str, Any],
        ttl_days: int | None = None,
    ) -> bool:
        """
        Store coaching session in cache.

        Args:
            dimension: Coaching dimension
            transcript_hash: SHA256 hash of transcript
            rubric_version: Rubric version
            session_data: Session data to cache
            ttl_days: Time to live in days (default: from settings)

        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False

        try:
            key = self._generate_key(dimension, transcript_hash, rubric_version)

            # Serialize to JSON and compress
            json_str = json.dumps(session_data)
            value = self._compress_value(json_str)

            # Set with TTL
            ttl = timedelta(days=ttl_days or settings.cache_ttl_days)
            self._client.setex(key, ttl, value)

            logger.info(f"Cache SET: {key} (TTL: {ttl.days} days)")
            return True

        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    def invalidate_dimension(
        self,
        dimension: CoachingDimension,
        rubric_version: str | None = None,
    ) -> int:
        """
        Invalidate all cache entries for a dimension.
        Used when rubric is updated.

        Args:
            dimension: Coaching dimension to invalidate
            rubric_version: Specific version to invalidate (or all if None)

        Returns:
            Number of keys deleted
        """
        if not self._available:
            return 0

        try:
            # Build pattern
            if rubric_version:
                pattern = f"coaching:{dimension.value}:*:{rubric_version}"
            else:
                pattern = f"coaching:{dimension.value}:*"

            # Find matching keys
            keys = []
            for key in self._client.scan_iter(match=pattern, count=100):
                keys.append(key)

            # Delete in batch
            if keys:
                deleted = self._client.delete(*keys)
                logger.info(
                    f"Invalidated {deleted} cache entries for "
                    f"dimension={dimension.value}, version={rubric_version}"
                )
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Redis invalidation error: {e}")
            return 0

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics from Redis.

        Returns:
            Dict with cache stats (hits, misses, memory usage, etc.)
        """
        if not self._available:
            return {"available": False}

        try:
            info = self._client.info("stats")
            memory = self._client.info("memory")

            return {
                "available": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0),
                ),
                "memory_used_mb": round(memory.get("used_memory", 0) / (1024 * 1024), 2),
                "total_keys": self._client.dbsize(),
            }

        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {"available": True, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

    def close(self) -> None:
        """Close Redis connection pool."""
        if self._client:
            self._client.close()
            logger.info("Redis connection pool closed")


# Global Redis cache instance
_redis_cache: RedisCache | None = None


def get_redis_cache() -> RedisCache:
    """
    Get or create global Redis cache instance.

    Configuration from environment:
    - REDIS_HOST (default: localhost)
    - REDIS_PORT (default: 6379)
    - REDIS_DB (default: 0)
    - REDIS_PASSWORD (optional)
    - REDIS_MAX_CONNECTIONS (default: 50)

    Returns:
        RedisCache instance
    """
    global _redis_cache

    if _redis_cache is None:
        import os

        _redis_cache = RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
        )

    return _redis_cache
