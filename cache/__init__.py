"""
Cache layer with Redis for high-performance coaching session storage.
Implements distributed caching with automatic invalidation on rubric updates.
"""
from .redis_client import RedisCache, get_redis_cache
from .prompt_cache import PromptCacheManager

__all__ = [
    "RedisCache",
    "get_redis_cache",
    "PromptCacheManager",
]
