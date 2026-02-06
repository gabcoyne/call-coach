"""
Response compression dependency using FastAPI dependency injection.

Refactored from middleware to use dependency injection for better:
- Testability (can inject mocks easily)
- Type safety (documented in OpenAPI schema)
- Explicit control (compress only when needed)
- Maintainability (no Starlette version issues)

Usage:
    @app.get("/endpoint")
    async def endpoint(
        compression: CompressionInfo = Depends(check_compression_support)
    ):
        # compression.should_compress indicates if client supports gzip
        result = get_large_data()
        if compression.should_compress:
            return compress_response(result)
        return result
"""

import gzip
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Annotated

from fastapi import Depends, Request, Response

logger = logging.getLogger(__name__)


@dataclass
class CompressionInfo:
    """Information about compression support and settings."""

    should_compress: bool
    accept_encoding: str
    minimum_size: int
    compression_level: int


class CompressionService:
    """
    Response compression service with gzip support.

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
        minimum_size: int = 500,  # Only compress responses > 500 bytes
        compression_level: int = 6,  # gzip compression level (1-9)
    ):
        self.minimum_size = minimum_size
        self.compression_level = compression_level

    def check_compression_support(self, request: Request) -> CompressionInfo:
        """
        Check if request supports and should use compression.

        Returns:
            CompressionInfo with support status and settings
        """
        accept_encoding = request.headers.get("Accept-Encoding", "")
        should_compress = "gzip" in accept_encoding.lower()

        return CompressionInfo(
            should_compress=should_compress,
            accept_encoding=accept_encoding,
            minimum_size=self.minimum_size,
            compression_level=self.compression_level,
        )

    def should_compress_response(
        self,
        body: bytes,
        content_type: str | None,
        compression_info: CompressionInfo,
    ) -> bool:
        """
        Determine if response should be compressed.

        Args:
            body: Response body bytes
            content_type: Response content type
            compression_info: Compression support information

        Returns:
            True if response should be compressed
        """
        # Check if client supports gzip
        if not compression_info.should_compress:
            return False

        # Check response size
        if len(body) < compression_info.minimum_size:
            return False

        # Check content type
        if not content_type:
            return False

        content_type_base = content_type.split(";")[0].strip()
        return content_type_base in self.COMPRESSIBLE_TYPES

    def compress_body(self, body: bytes, compression_level: int | None = None) -> bytes:
        """
        Compress response body with gzip.

        Args:
            body: Response body to compress
            compression_level: Optional compression level override

        Returns:
            Compressed body bytes
        """
        level = compression_level or self.compression_level

        buf = BytesIO()
        with gzip.GzipFile(
            fileobj=buf,
            mode="wb",
            compresslevel=level,
        ) as gz:
            gz.write(body)
        return buf.getvalue()

    def compress_response(
        self,
        response: Response,
        body: bytes,
        compression_info: CompressionInfo,
    ) -> Response:
        """
        Compress response if appropriate.

        Args:
            response: Original response
            body: Response body bytes
            compression_info: Compression support information

        Returns:
            Possibly compressed response
        """
        # Check if we should compress
        content_type = response.headers.get("Content-Type")
        if not self.should_compress_response(body, content_type, compression_info):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Compress response
        try:
            compressed_body = self.compress_body(body, compression_info.compression_level)
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


# Global compression service instance
_compression_service = CompressionService()


def get_compression_service() -> CompressionService:
    """Get the global compression service instance."""
    return _compression_service


async def check_compression_support(
    request: Request,
    service: CompressionService = Depends(get_compression_service),
) -> CompressionInfo:
    """
    FastAPI dependency for checking compression support.

    Usage:
        @app.get("/endpoint")
        async def endpoint(
            compression: CompressionInfo = Depends(check_compression_support)
        ):
            # compression.should_compress indicates support
            ...
    """
    return service.check_compression_support(request)


# Type alias for dependency injection
CompressionDep = Annotated[CompressionInfo, Depends(check_compression_support)]
