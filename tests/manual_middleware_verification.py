"""
Manual verification script for middleware dependencies.

Run this to verify that both rate limiting and compression dependencies work correctly.
This demonstrates the middleware can be integrated into the REST API.
"""

import asyncio
from unittest.mock import MagicMock

from fastapi import Request

from api.dependencies.compression import CompressionService, check_compression_support
from api.dependencies.rate_limit import RateLimitService, check_rate_limit


async def test_rate_limiting():
    """Verify rate limiting works as expected."""
    print("\n" + "=" * 60)
    print("RATE LIMITING VERIFICATION")
    print("=" * 60)

    service = RateLimitService(default_rate_limit=5, default_burst=5)

    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.headers.get.return_value = "test@example.com"
    request.client.host = "127.0.0.1"

    # Make 5 requests (should all succeed)
    print("\n✓ Making 5 requests (should all succeed):")
    for i in range(5):
        info = await check_rate_limit(request, service)
        print(f"  Request {i+1}: Allowed={info.allowed}, Remaining={info.remaining}")
        assert info.allowed, f"Request {i+1} should be allowed"

    # 6th request should be rate limited
    print("\n✓ Making 6th request (should be rate limited):")
    try:
        await check_rate_limit(request, service)
        print("  ERROR: Request should have been blocked!")
        assert False
    except Exception as e:
        print(f"  ✓ Rate limited as expected: {e.status_code} {e.detail['error']}")
        assert e.status_code == 429

    print("\n✓ Rate limiting works correctly!")


async def test_compression():
    """Verify compression works as expected."""
    print("\n" + "=" * 60)
    print("COMPRESSION VERIFICATION")
    print("=" * 60)

    service = CompressionService(minimum_size=100, compression_level=6)

    # Client supports gzip
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "gzip, deflate, br"

    info = await check_compression_support(request, service)
    print(f"\n✓ Client supports gzip: {info.should_compress}")
    assert info.should_compress

    # Large response should be compressed
    large_body = b"x" * 1000
    response = MagicMock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.media_type = "application/json"

    result = service.compress_response(response, large_body, info)
    print("\n✓ Large response compression:")
    print(f"  Original size: {len(large_body)} bytes")
    print(f"  Compressed size: {len(result.body)} bytes")
    print(f"  Compression ratio: {len(large_body) / len(result.body):.2f}x")
    print(f"  Content-Encoding: {result.headers.get('Content-Encoding')}")
    assert result.headers["Content-Encoding"] == "gzip"

    # Small response should NOT be compressed
    small_body = b'{"test": "data"}'
    result = service.compress_response(response, small_body, info)
    print("\n✓ Small response (no compression):")
    print(f"  Size: {len(small_body)} bytes")
    print(f"  Compressed: {'Content-Encoding' in result.headers}")
    assert "Content-Encoding" not in result.headers

    print("\n✓ Compression works correctly!")


async def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("MIDDLEWARE DEPENDENCY VERIFICATION")
    print("=" * 60)

    await test_rate_limiting()
    await test_compression()

    print("\n" + "=" * 60)
    print("✅ ALL MIDDLEWARE DEPENDENCIES WORKING CORRECTLY")
    print("=" * 60)
    print("\nThe refactored middleware is ready for production use!")
    print("Next steps:")
    print("  1. Update REST API endpoints to use the new dependencies")
    print("  2. Remove old middleware files")
    print("  3. Deploy and monitor in production")
    print()


if __name__ == "__main__":
    asyncio.run(main())
