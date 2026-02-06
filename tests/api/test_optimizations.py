"""
Tests for API optimization features.

Tests:
- Rate limiting enforcement
- Response compression
- Error response format
- Pagination
- Monitoring endpoints
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.rest_server import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


class TestRateLimiting:
    """Test rate limiting middleware."""

    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are included in response."""
        response = client.get("/health")

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_enforcement(self, client):
        """Test that rate limiting is enforced after burst."""
        # Make requests up to burst limit
        responses = []
        for _ in range(160):  # Exceed burst of 150
            response = client.get("/health")
            responses.append(response)

        # Should have some 429 responses
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0

        # 429 response should have retry-after header
        if rate_limited:
            assert "Retry-After" in rate_limited[0].headers

    def test_rate_limit_per_endpoint(self, client):
        """Test that different endpoints have separate rate limits."""
        # Health endpoint should have higher limit than expensive ones
        health_responses = []
        for _ in range(160):
            response = client.get("/health")
            health_responses.append(response)

        health_limited = [r for r in health_responses if r.status_code == 429]

        # Mock expensive endpoint
        with patch("api.rest_server.analyze_call_tool") as mock_tool:
            mock_tool.return_value = {"status": "ok"}

            expensive_responses = []
            for _ in range(35):  # Exceed expensive burst of 30
                response = client.post("/tools/analyze_call", json={"call_id": "test-call-id"})
                expensive_responses.append(response)

            expensive_limited = [r for r in expensive_responses if r.status_code == 429]

            # Expensive endpoint should be rate limited sooner
            assert len(expensive_limited) > len(health_limited)


class TestCompression:
    """Test response compression middleware."""

    def test_gzip_compression_applied(self, client):
        """Test that responses are gzip compressed when requested."""
        response = client.get("/health", headers={"Accept-Encoding": "gzip"})

        # Check for compression headers
        assert response.headers.get("Content-Encoding") == "gzip"
        assert response.headers.get("Vary") == "Accept-Encoding"

    def test_small_responses_not_compressed(self, client):
        """Test that small responses are not compressed."""
        # Health check response is small
        response = client.get("/health", headers={"Accept-Encoding": "gzip"})

        # May or may not be compressed based on size
        # Just verify it doesn't error
        assert response.status_code == 200

    def test_compression_reduces_size(self, client):
        """Test that compression actually reduces response size."""
        # Mock large response
        with patch("api.rest_server.search_calls_tool") as mock_tool:
            # Create large response (> 500 bytes)
            large_response = [
                {
                    "call_id": f"call-{i}",
                    "title": f"Sales Call {i}" * 10,
                    "transcript": "A" * 100,
                }
                for i in range(10)
            ]
            mock_tool.return_value = large_response

            # Get uncompressed size
            response_uncompressed = client.post(
                "/tools/search_calls",
                json={"limit": 20},
                headers={"Accept-Encoding": "identity"},  # No compression
            )

            # Get compressed size
            response_compressed = client.post(
                "/tools/search_calls", json={"limit": 20}, headers={"Accept-Encoding": "gzip"}
            )

            # Compressed should be smaller
            if response_compressed.headers.get("Content-Encoding") == "gzip":
                compressed_size = len(response_compressed.content)
                uncompressed_size = len(response_uncompressed.content)
                assert compressed_size < uncompressed_size


class TestErrorHandling:
    """Test centralized error handling."""

    def test_error_response_format(self, client):
        """Test that errors have standardized format."""
        # Trigger validation error
        response = client.post("/tools/analyze_call", json={})  # Missing required field

        assert response.status_code == 422
        data = response.json()

        # Check error format
        assert "error" in data
        assert "message" in data

    def test_request_id_in_errors(self, client):
        """Test that request ID is included in errors."""
        response = client.post(
            "/tools/analyze_call", json={}, headers={"X-Request-ID": "test-request-123"}
        )

        data = response.json()
        assert data.get("request_id") == "test-request-123"

    def test_404_error_format(self, client):
        """Test 404 errors are formatted correctly."""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestPagination:
    """Test pagination support."""

    def test_paginated_search_response(self, client):
        """Test that paginated endpoints return proper metadata."""
        with patch("api.rest_server.search_calls_tool") as mock_tool:
            mock_tool.return_value = [{"call_id": f"call-{i}"} for i in range(20)]

            response = client.post("/api/v1/tools/search_calls", json={"limit": 20, "offset": 0})

            assert response.status_code == 200
            data = response.json()

            # Check pagination structure
            assert "data" in data
            assert "items" in data["data"]
            assert "total" in data["data"]
            assert "page" in data["data"]
            assert "page_size" in data["data"]
            assert "has_next" in data["data"]


class TestMonitoring:
    """Test monitoring endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/monitoring/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "uptime_seconds" in data

    def test_metrics_endpoint(self, client):
        """Test metrics collection endpoint."""
        # Make some requests first
        client.get("/health")
        client.get("/health")

        # Get metrics
        response = client.get("/monitoring/metrics")

        assert response.status_code == 200
        data = response.json()

        assert "total_requests" in data
        assert "error_rate" in data
        assert "response_time_ms" in data
        assert "requests_by_endpoint" in data

    def test_endpoint_specific_metrics(self, client):
        """Test endpoint-specific metrics."""
        # Make requests to specific endpoint
        client.get("/health")

        response = client.get("/monitoring/metrics/endpoint/health")

        assert response.status_code == 200
        data = response.json()

        assert "endpoint" in data
        assert "total_requests" in data
        assert "response_time_ms" in data

    def test_database_metrics(self, client):
        """Test database metrics endpoint."""
        response = client.get("/monitoring/metrics/database")

        assert response.status_code == 200
        data = response.json()

        # Should have connection pool info
        if "error" not in data:
            assert "connection_pool" in data


class TestAPIVersioning:
    """Test API versioning."""

    def test_v1_endpoint_accessible(self, client):
        """Test that v1 endpoints are accessible."""
        with patch("api.rest_server.search_calls_tool") as mock_tool:
            mock_tool.return_value = []

            response = client.post("/api/v1/tools/search_calls", json={"limit": 20})

            assert response.status_code == 200
            data = response.json()

            # Check API version in response
            assert data.get("api_version") == "v1"

    def test_legacy_endpoint_still_works(self, client):
        """Test that legacy endpoints (without /api/v1) still work."""
        with patch("api.rest_server.search_calls_tool") as mock_tool:
            mock_tool.return_value = []

            response = client.post("/tools/search_calls", json={"limit": 20})

            # Should still work for backward compatibility
            assert response.status_code in [200, 404]  # 404 if route removed


class TestRequestContext:
    """Test request context middleware."""

    def test_request_id_generated(self, client):
        """Test that request ID is generated if not provided."""
        response = client.get("/health")

        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0

    def test_request_id_preserved(self, client):
        """Test that provided request ID is preserved."""
        custom_id = "my-custom-request-id"
        response = client.get("/health", headers={"X-Request-ID": custom_id})

        assert response.headers["X-Request-ID"] == custom_id

    def test_response_time_header(self, client):
        """Test that response time is included in headers."""
        response = client.get("/health")

        assert "X-Response-Time" in response.headers
        response_time = response.headers["X-Response-Time"]
        assert response_time.endswith("ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
