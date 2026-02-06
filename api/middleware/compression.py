"""
Response compression middleware for FastAPI.

Compresses responses using gzip for bandwidth optimization.
Critical for large coaching analysis responses with transcripts.

Features:
- Automatic gzip compression for responses > 1KB
- Configurable compression level
- Respects Accept-Encoding header
- Skips already-compressed content types
"""
import gzip
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for gzip compression of HTTP responses.

    Compresses responses when:
    - Client accepts gzip (Accept-Encoding: gzip)
    - Response size > min_size (default: 1KB)
    - Content-Type is compressible (text/*, application/json, etc.)
    """

    # Content types that should be compressed
    COMPRESSIBLE_TYPES = {
        "text/html",
        "text/css",
        "text/plain",
        "text/xml",
        "text/javascript",
        "application/json",
        "application/javascript",
        "application/xml",
        "application/xhtml+xml",
        "application/rss+xml",
        "application/atom+xml",
    }

    def __init__(
        self,
        app: ASGIApp,
        min_size: int = 1024,
        compression_level: int = 6,
    ):
        """
        Initialize compression middleware.

        Args:
            app: ASGI application
            min_size: Minimum response size to compress (bytes)
            compression_level: gzip compression level (1-9, default: 6)
        """
        super().__init__(app)
        self.min_size = min_size
        self.compression_level = compression_level

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process request and compress response if applicable.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response (possibly compressed)
        """
        # Get response from downstream
        response = await call_next(request)

        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # Check if response should be compressed
        if not self._should_compress(response):
            return response

        # Get response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Check size threshold
        if len(body) < self.min_size:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Compress response
        compressed_body = gzip.compress(
            body,
            compresslevel=self.compression_level
        )

        # Calculate compression ratio
        original_size = len(body)
        compressed_size = len(compressed_body)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        logger.debug(
            f"Compressed response: {original_size} -> {compressed_size} bytes "
            f"({ratio:.1f}% reduction)"
        )

        # Update headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(compressed_size)
        headers["x-original-size"] = str(original_size)
        headers["x-compression-ratio"] = f"{ratio:.1f}%"

        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )

    def _should_compress(self, response: Response) -> bool:
        """
        Check if response should be compressed.

        Args:
            response: HTTP response

        Returns:
            True if response should be compressed
        """
        # Don't compress if already encoded
        if response.headers.get("content-encoding"):
            return False

        # Don't compress error responses
        if response.status_code >= 300:
            return False

        # Check content type
        content_type = response.media_type or ""
        base_type = content_type.split(";")[0].strip().lower()

        # Check if content type is compressible
        for compressible in self.COMPRESSIBLE_TYPES:
            if base_type == compressible or base_type.startswith(compressible):
                return True

        return False


def get_compression_stats() -> dict:
    """
    Get compression statistics.

    This would typically integrate with a metrics system
    to track compression ratios and bandwidth savings.

    Returns:
        Dict with compression statistics
    """
    # This is a placeholder for actual metrics collection
    return {
        "enabled": True,
        "min_size": 1024,
        "compression_level": 6,
    }
