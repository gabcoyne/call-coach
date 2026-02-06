"""
Response compression middleware with gzip support.

Automatically compresses responses based on:
- Content-Type (JSON, HTML, etc.)
- Response size threshold
- Client Accept-Encoding header
"""
import gzip
import logging
from io import BytesIO
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Gzip compression middleware for API responses.

    Only compresses responses that:
    - Are larger than minimum_size bytes
    - Have compressible content types
    - Client supports gzip (Accept-Encoding header)
    """

    # Content types that benefit from compression
    COMPRESSIBLE_TYPES = {
        "application/json",
        "application/javascript",
        "application/xml",
        "text/html",
        "text/css",
        "text/plain",
        "text/xml",
    }

    def __init__(
        self,
        app,
        minimum_size: int = 500,  # Only compress responses > 500 bytes
        compression_level: int = 6,  # gzip compression level (1-9)
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level

    def _should_compress(
        self,
        request: Request,
        response: Response,
        body: bytes,
    ) -> bool:
        """Determine if response should be compressed."""
        # Check if already compressed
        if response.headers.get("Content-Encoding"):
            return False

        # Check if client supports gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False

        # Check response size
        if len(body) < self.minimum_size:
            return False

        # Check content type
        content_type = response.headers.get("Content-Type", "")
        content_type_base = content_type.split(";")[0].strip()

        return content_type_base in self.COMPRESSIBLE_TYPES

    def _compress_body(self, body: bytes) -> bytes:
        """Compress response body with gzip."""
        buf = BytesIO()
        with gzip.GzipFile(
            fileobj=buf,
            mode="wb",
            compresslevel=self.compression_level,
        ) as gz:
            gz.write(body)
        return buf.getvalue()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and compress response if appropriate."""
        # Get response
        response = await call_next(request)

        # Skip compression for streaming responses
        if hasattr(response, "body_iterator"):
            return response

        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Check if we should compress
        if not self._should_compress(request, response, body):
            # Return uncompressed response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Compress response
        try:
            compressed_body = self._compress_body(body)
            compression_ratio = len(body) / len(compressed_body) if compressed_body else 1

            logger.debug(
                f"Compressed response: {len(body)} -> {len(compressed_body)} bytes "
                f"(ratio: {compression_ratio:.2f}x)"
            )

            # Update headers
            headers = dict(response.headers)
            headers["Content-Encoding"] = "gzip"
            headers["Content-Length"] = str(len(compressed_body))
            headers["Vary"] = "Accept-Encoding"

            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # Return uncompressed on error
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
