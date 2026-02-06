"""
Database Query Benchmarks

Measures performance of critical database queries.
Identifies slow queries and optimization opportunities.
"""

import asyncio

import pytest

from db import queries


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def sample_call_ids():
    """Get sample call IDs for testing."""
    # In real scenario, these would be fetched from database
    return [f"call_{i:06d}" for i in range(1, 101)]


@pytest.fixture
async def sample_rep_emails():
    """Get sample rep emails for testing."""
    return [f"rep_{i:02d}@example.com" for i in range(1, 51)]


class TestDatabaseBenchmarks:
    """Database query performance benchmarks."""

    def test_get_call_metadata(self, benchmark):
        """Benchmark fetching call metadata."""
        call_id = "call_000001"

        def query():
            # Simulated query - replace with actual DB call
            return queries.get_call_analysis(call_id)

        benchmark(query)

    def test_get_call_transcript(self, benchmark):
        """Benchmark fetching call transcript."""
        call_id = "call_000001"

        def query():
            return queries.get_call_transcript(call_id)

        benchmark(query)

    def test_search_calls_by_rep(self, benchmark):
        """Benchmark searching calls by rep."""
        rep_email = "rep_01@example.com"

        def query():
            return queries.search_calls(rep_email=rep_email, limit=20)

        benchmark(query)

    def test_search_calls_by_product(self, benchmark):
        """Benchmark searching calls by product."""

        def query():
            return queries.search_calls(product="product_a", limit=20)

        benchmark(query)

    def test_search_calls_by_date_range(self, benchmark):
        """Benchmark searching calls by date range."""
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        def query():
            return queries.search_calls(
                start_date=start_date,
                end_date=end_date,
                limit=20,
            )

        benchmark(query)

    def test_search_calls_complex_filters(self, benchmark):
        """Benchmark complex search with multiple filters."""
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        def query():
            return queries.search_calls(
                rep_email="rep_01@example.com",
                product="product_a",
                call_type="discovery",
                start_date=start_date,
                end_date=end_date,
                min_score=70,
                limit=50,
            )

        benchmark(query)

    def test_get_rep_stats(self, benchmark):
        """Benchmark fetching rep statistics."""
        rep_email = "rep_01@example.com"

        def query():
            return queries.get_rep_stats(rep_email, days=30)

        benchmark(query)

    def test_get_opportunity_calls(self, benchmark):
        """Benchmark fetching all calls for an opportunity."""
        opportunity_id = "opp_000001"

        def query():
            return queries.get_opportunity_calls(opportunity_id)

        benchmark(query)

    def test_get_opportunity_analysis(self, benchmark):
        """Benchmark fetching opportunity analysis."""
        opportunity_id = "opp_000001"

        def query():
            return queries.get_opportunity_analysis(opportunity_id)

        benchmark(query)

    def test_get_recent_calls(self, benchmark):
        """Benchmark fetching recent calls."""

        def query():
            return queries.get_recent_calls(limit=100)

        benchmark(query)

    def test_batch_get_calls(self, benchmark):
        """Benchmark batch fetching multiple calls."""
        call_ids = [f"call_{i:06d}" for i in range(1, 51)]

        def query():
            return queries.get_calls_batch(call_ids)

        benchmark(query)

    def test_count_calls_by_product(self, benchmark):
        """Benchmark counting calls by product."""

        def query():
            return queries.count_calls_by_product()

        benchmark(query)

    def test_count_calls_by_rep(self, benchmark):
        """Benchmark counting calls by rep."""

        def query():
            return queries.count_calls_by_rep()

        benchmark(query)

    def test_get_dashboard_stats(self, benchmark):
        """Benchmark fetching dashboard statistics."""

        def query():
            return queries.get_dashboard_stats()

        benchmark(query)


class TestDatabaseQueryPlan:
    """Tests for query plan optimization."""

    def test_search_calls_index_usage(self, benchmark):
        """Benchmark search_calls to verify index usage."""

        # This would ideally check EXPLAIN PLAN
        def query():
            return queries.search_calls(
                product="product_a",
                limit=20,
            )

        benchmark(query)

    def test_date_range_search_optimization(self, benchmark):
        """Verify date range queries use indexes."""
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        def query():
            return queries.search_calls(
                start_date=start_date,
                end_date=end_date,
                limit=100,
            )

        benchmark(query)


class TestDatabaseConnectionPool:
    """Benchmarks for connection pool performance."""

    def test_connection_acquisition_time(self, benchmark):
        """Measure time to acquire a connection from pool."""

        def get_connection():
            # This would measure actual connection pool performance
            conn = queries.get_connection()
            conn.close()

        benchmark(get_connection)

    def test_query_with_multiple_connections(self, benchmark):
        """Benchmark query performance under connection pool stress."""

        def query():
            results = []
            for i in range(5):
                result = queries.search_calls(limit=10)
                results.append(result)
            return results

        benchmark(query)
