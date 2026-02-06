"""
Cache layer with Redis for high-performance coaching session storage.
Implements distributed caching with automatic invalidation on rubric updates.
"""

from .prompt_cache import PromptCacheManager
from .redis_client import RedisCache, get_redis_cache

__all__ = [
    "RedisCache",
    "get_redis_cache",
    "PromptCacheManager",
]
