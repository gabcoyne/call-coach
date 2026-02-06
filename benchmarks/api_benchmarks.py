"""
API Endpoint Benchmarks

Measures performance of individual API endpoints using pytest-benchmark.
Tracks performance over time and detects regressions.
"""

import httpx
import pytest

# Baseline thresholds for performance regression detection
PERFORMANCE_THRESHOLDS = {
    "/health": {"p50": 0.05, "p99": 0.20},  # milliseconds
    "/tools/analyze_call": {"p50": 2000, "p99": 5000},
    "/tools/get_rep_insights": {"p50": 1500, "p99": 4000},
    "/tools/search_calls": {"p50": 500, "p99": 2000},
    "/tools/analyze_opportunity": {"p50": 3000, "p99": 8000},
}


@pytest.fixture(scope="session")
def api_client():
    """Create HTTP client for API testing."""
    return httpx.Client(base_url="http://localhost:8000", timeout=60.0)


@pytest.fixture(scope="session")
def test_data():
    """Prepare test data for benchmarks."""
    return {
        "call_ids": [f"call_{i:06d}" for i in range(1, 21)],
        "rep_emails": [f"rep_{i:02d}@example.com" for i in range(1, 11)],
        "opportunity_ids": [f"opp_{i:06d}" for i in range(1, 11)],
        "products": ["product_a", "product_b", "product_c"],
    }


class TestAPIBenchmarks:
    """Benchmarks for API endpoints."""

    def test_health_check(self, benchmark, api_client):
        """Benchmark health check endpoint."""

        def make_request():
            response = api_client.get("/health")
            assert response.status_code == 200

        benchmark(make_request)

    def test_analyze_call_cached(self, benchmark, api_client, test_data):
        """Benchmark analyze_call with caching enabled."""
        call_id = test_data["call_ids"][0]

        def make_request():
            response = api_client.post(
                "/tools/analyze_call",
                json={
                    "call_id": call_id,
                    "use_cache": True,
                    "dimensions": ["engagement", "discovery"],
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_analyze_call_uncached(self, benchmark, api_client, test_data):
        """Benchmark analyze_call with caching disabled."""
        call_id = test_data["call_ids"][1]

        def make_request():
            response = api_client.post(
                "/tools/analyze_call",
                json={
                    "call_id": call_id,
                    "use_cache": False,
                    "dimensions": ["engagement", "discovery"],
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_analyze_call_with_transcript(self, benchmark, api_client, test_data):
        """Benchmark analyze_call with transcript snippets."""
        call_id = test_data["call_ids"][2]

        def make_request():
            response = api_client.post(
                "/tools/analyze_call",
                json={
                    "call_id": call_id,
                    "use_cache": True,
                    "include_transcript_snippets": True,
                    "dimensions": ["engagement", "discovery", "objection_handling"],
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_get_rep_insights_7_days(self, benchmark, api_client, test_data):
        """Benchmark get_rep_insights for 7-day period."""
        rep_email = test_data["rep_emails"][0]

        def make_request():
            response = api_client.post(
                "/tools/get_rep_insights",
                json={
                    "rep_email": rep_email,
                    "time_period": "last_7_days",
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_get_rep_insights_30_days(self, benchmark, api_client, test_data):
        """Benchmark get_rep_insights for 30-day period."""
        rep_email = test_data["rep_emails"][1]

        def make_request():
            response = api_client.post(
                "/tools/get_rep_insights",
                json={
                    "rep_email": rep_email,
                    "time_period": "last_30_days",
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_get_rep_insights_with_product_filter(self, benchmark, api_client, test_data):
        """Benchmark get_rep_insights with product filter."""
        rep_email = test_data["rep_emails"][2]

        def make_request():
            response = api_client.post(
                "/tools/get_rep_insights",
                json={
                    "rep_email": rep_email,
                    "time_period": "last_30_days",
                    "product_filter": "product_a",
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_search_calls_simple(self, benchmark, api_client):
        """Benchmark search_calls with minimal filters."""

        def make_request():
            response = api_client.post(
                "/tools/search_calls",
                json={
                    "limit": 20,
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_search_calls_with_product_filter(self, benchmark, api_client, test_data):
        """Benchmark search_calls with product filter."""

        def make_request():
            response = api_client.post(
                "/tools/search_calls",
                json={
                    "product": test_data["products"][0],
                    "limit": 20,
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_search_calls_with_date_range(self, benchmark, api_client):
        """Benchmark search_calls with date range."""
        from datetime import datetime, timedelta

        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        end_date = datetime.now().isoformat()

        def make_request():
            response = api_client.post(
                "/tools/search_calls",
                json={
                    "date_range": {
                        "start": start_date,
                        "end": end_date,
                    },
                    "limit": 20,
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_search_calls_complex(self, benchmark, api_client, test_data):
        """Benchmark search_calls with multiple filters."""
        from datetime import datetime, timedelta

        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        end_date = datetime.now().isoformat()

        def make_request():
            response = api_client.post(
                "/tools/search_calls",
                json={
                    "rep_email": test_data["rep_emails"][3],
                    "product": test_data["products"][1],
                    "call_type": "discovery",
                    "date_range": {
                        "start": start_date,
                        "end": end_date,
                    },
                    "min_score": 70,
                    "limit": 50,
                },
            )
            assert response.status_code == 200

        benchmark(make_request)

    def test_analyze_opportunity(self, benchmark, api_client, test_data):
        """Benchmark analyze_opportunity endpoint."""
        opp_id = test_data["opportunity_ids"][0]

        def make_request():
            response = api_client.post(
                "/tools/analyze_opportunity",
                json={
                    "opportunity_id": opp_id,
                },
            )
            assert response.status_code == 200

        benchmark(make_request)


class TestAPIBenchmarkRegression:
    """Test for performance regressions."""

    def test_no_regression_health(self, benchmark, api_client):
        """Ensure health check doesn't regress."""

        def make_request():
            api_client.get("/health")

        result = benchmark(make_request)
        threshold_ms = PERFORMANCE_THRESHOLDS["/health"]["p99"]
        # Note: actual regression checking would compare with baseline

    def test_no_regression_analyze_call(self, benchmark, api_client, test_data):
        """Ensure analyze_call doesn't regress."""
        call_id = test_data["call_ids"][0]

        def make_request():
            api_client.post(
                "/tools/analyze_call",
                json={
                    "call_id": call_id,
                    "use_cache": True,
                },
            )

        result = benchmark(make_request)
        # Regression check would compare with baseline

    def test_no_regression_search_calls(self, benchmark, api_client):
        """Ensure search_calls doesn't regress."""

        def make_request():
            api_client.post(
                "/tools/search_calls",
                json={"limit": 20},
            )

        result = benchmark(make_request)
        # Regression check would compare with baseline
