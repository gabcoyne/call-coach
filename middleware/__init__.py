"""
Middleware components for API optimization.

This package provides:
- Rate limiting per-user and per-endpoint
- Response compression (gzip)
- Caching headers and ETag support
- Performance monitoring
"""

from .compression import CompressionMiddleware
from .rate_limit import RateLimitMiddleware

__all__ = [
    "RateLimitMiddleware",
    "CompressionMiddleware",
]
