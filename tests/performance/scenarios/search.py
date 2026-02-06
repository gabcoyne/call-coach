"""
Search Query Performance Scenario

Tests performance of complex search queries.
Measures various filter combinations and their impact on query time.
"""
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytest


@pytest.mark.performance
class TestSearchPerformanceScenario:
    """Search query performance scenarios."""

    @pytest.fixture
    def search_client(self):
        """Create HTTP client for search."""
        import httpx
        return httpx.Client(base_url="http://localhost:8000", timeout=60.0)

    @pytest.fixture
    def search_params(self) -> Dict[str, Any]:
        """Common search parameters."""
        return {
            "rep_emails": [f"rep_{i:02d}@example.com" for i in range(1, 26)],
            "products": ["product_a", "product_b", "product_c", "product_d"],
            "call_types": ["discovery", "demo", "negotiation", "closing"],
        }

    def test_simple_search(
        self,
        search_client,
        search_params: Dict[str, Any],
        benchmark,
    ):
        """Benchmark simple search with minimal filters."""
        def simple_search():
            total_time = 0
            successful = 0

            for _ in range(20):
                start = time.time()
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={"limit": 20},
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                except:
                    pass

            return {
                "queries": 20,
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / 20,
            }

        result = benchmark(simple_search)
        print(f"\nSimple Search (20 queries):")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")

    def test_search_by_product(
        self,
        search_client,
        search_params: Dict[str, Any],
        benchmark,
    ):
        """Benchmark search filtered by product."""
        def search_by_product():
            total_time = 0
            successful = 0

            for product in search_params["products"]:
                start = time.time()
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={
                            "product": product,
                            "limit": 20,
                        },
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                except:
                    pass

            return {
                "queries": len(search_params["products"]),
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / len(search_params["products"]),
            }

        result = benchmark(search_by_product)
        print(f"\nSearch by Product ({len(search_params['products'])} products):")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")

    def test_search_by_rep(
        self,
        search_client,
        search_params: Dict[str, Any],
        benchmark,
    ):
        """Benchmark search filtered by sales rep."""
        def search_by_rep():
            total_time = 0
            successful = 0

            for rep_email in search_params["rep_emails"][:10]:
                start = time.time()
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={
                            "rep_email": rep_email,
                            "limit": 20,
                        },
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                except:
                    pass

            return {
                "queries": 10,
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / 10,
            }

        result = benchmark(search_by_rep)
        print(f"\nSearch by Rep (10 reps):")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")

    def test_search_by_date_range(
        self,
        search_client,
        benchmark,
    ):
        """Benchmark search with date range filters."""
        date_ranges = [
            ("last_7_days", 7),
            ("last_30_days", 30),
            ("last_90_days", 90),
        ]

        results = {}

        for name, days in date_ranges:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            end_date = datetime.now().isoformat()

            start = time.time()
            successful = 0

            for _ in range(5):
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={
                            "date_range": {
                                "start": start_date,
                                "end": end_date,
                            },
                            "limit": 20,
                        },
                        timeout=30,
                    )
                    if response.status_code == 200:
                        successful += 1
                except:
                    pass

            elapsed = time.time() - start
            results[name] = {
                "queries": 5,
                "successful": successful,
                "total_time": elapsed,
                "avg_time": elapsed / 5,
            }

        print(f"\nSearch by Date Range:")
        for name, metrics in results.items():
            print(f"  {name}:")
            print(f"    Successful: {metrics['successful']}/{metrics['queries']}")
            print(f"    Avg Query Time: {metrics['avg_time']:.3f}s")

    def test_search_with_score_filter(
        self,
        search_client,
        benchmark,
    ):
        """Benchmark search with score filters."""
        def search_with_scores():
            score_ranges = [
                {"min_score": 60, "max_score": 70},
                {"min_score": 70, "max_score": 80},
                {"min_score": 80, "max_score": 90},
                {"min_score": 90, "max_score": 100},
            ]

            total_time = 0
            successful = 0

            for scores in score_ranges:
                start = time.time()
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={
                            "min_score": scores["min_score"],
                            "max_score": scores["max_score"],
                            "limit": 20,
                        },
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                except:
                    pass

            return {
                "queries": len(score_ranges),
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / len(score_ranges),
            }

        result = benchmark(search_with_scores)
        print(f"\nSearch with Score Filters:")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")

    def test_complex_search(
        self,
        search_client,
        search_params: Dict[str, Any],
        benchmark,
    ):
        """Benchmark complex search with multiple filters."""
        def complex_search():
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
            end_date = datetime.now().isoformat()

            total_time = 0
            successful = 0

            for rep_email in search_params["rep_emails"][:5]:
                for product in search_params["products"][:2]:
                    start = time.time()
                    try:
                        response = search_client.post(
                            "/tools/search_calls",
                            json={
                                "rep_email": rep_email,
                                "product": product,
                                "call_type": "discovery",
                                "date_range": {
                                    "start": start_date,
                                    "end": end_date,
                                },
                                "min_score": 70,
                                "limit": 50,
                            },
                            timeout=30,
                        )
                        elapsed = time.time() - start
                        total_time += elapsed

                        if response.status_code == 200:
                            successful += 1
                    except:
                        pass

            total_queries = 5 * 2
            return {
                "queries": total_queries,
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / total_queries if total_queries > 0 else 0,
            }

        result = benchmark(complex_search)
        print(f"\nComplex Search (Multi-filter):")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")

    def test_search_result_pagination(
        self,
        search_client,
        benchmark,
    ):
        """Benchmark search with different result limits."""
        def paginated_search():
            limits = [10, 20, 50, 100]
            total_time = 0
            successful = 0

            for limit in limits:
                start = time.time()
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={"limit": limit},
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                except:
                    pass

            return {
                "queries": len(limits),
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / len(limits),
            }

        result = benchmark(paginated_search)
        print(f"\nSearch Pagination Limits:")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")

    def test_search_result_sorting(
        self,
        search_client,
        benchmark,
    ):
        """Benchmark search with result sorting."""
        def sorted_search():
            # Test searching and then sorting results
            total_time = 0
            successful = 0

            for _ in range(10):
                start = time.time()
                try:
                    response = search_client.post(
                        "/tools/search_calls",
                        json={
                            "limit": 100,
                        },
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                        # Simulate sorting of results
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                _ = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
                        except:
                            pass
                except:
                    pass

            return {
                "queries": 10,
                "successful": successful,
                "total_time": total_time,
                "avg_time": total_time / 10,
            }

        result = benchmark(sorted_search)
        print(f"\nSearch with Result Sorting:")
        print(f"  Successful: {result['successful']}/{result['queries']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Query Time: {result['avg_time']:.3f}s")
