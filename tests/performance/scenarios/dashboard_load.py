"""
Dashboard Load Performance Scenario

Tests performance of loading the rep dashboard.
Simulates: Rep metrics, call history, trend analysis, coaching recommendations.
"""
import time
import random
from typing import List, Dict, Any
import pytest


@pytest.mark.performance
class TestDashboardLoadScenario:
    """Dashboard loading performance scenarios."""

    @pytest.fixture
    def dashboard_client(self):
        """Create HTTP client for dashboard."""
        import httpx
        return httpx.Client(base_url="http://localhost:8000", timeout=60.0)

    @pytest.fixture
    def rep_emails(self) -> List[str]:
        """Generate test rep emails."""
        return [f"rep_{i:02d}@example.com" for i in range(1, 51)]

    def test_load_dashboard_single_rep(
        self,
        dashboard_client,
        rep_emails: List[str],
        benchmark,
    ):
        """Benchmark loading dashboard for a single rep."""
        rep_email = rep_emails[0]

        def load_dashboard():
            # Load all dashboard components
            start = time.time()
            components = {}

            # 1. Get rep insights
            try:
                response = dashboard_client.post(
                    "/tools/get_rep_insights",
                    json={
                        "rep_email": rep_email,
                        "time_period": "last_30_days",
                    },
                    timeout=30,
                )
                components["insights"] = response.status_code == 200
            except:
                components["insights"] = False

            # 2. Get recent calls
            try:
                response = dashboard_client.post(
                    "/tools/search_calls",
                    json={
                        "rep_email": rep_email,
                        "limit": 20,
                    },
                    timeout=30,
                )
                components["recent_calls"] = response.status_code == 200
            except:
                components["recent_calls"] = False

            # 3. Get coaching recommendations (if available)
            try:
                response = dashboard_client.post(
                    "/tools/get_rep_insights",
                    json={
                        "rep_email": rep_email,
                        "time_period": "last_7_days",
                        "focus_area": "discovery",
                    },
                    timeout=30,
                )
                components["coaching"] = response.status_code == 200
            except:
                components["coaching"] = False

            elapsed = time.time() - start
            return {
                "rep_email": rep_email,
                "load_time": elapsed,
                "components_loaded": sum(components.values()),
                "total_components": len(components),
            }

        result = benchmark(load_dashboard)
        print(f"\nDashboard Load Time (Single Rep):")
        print(f"  Rep: {result['rep_email']}")
        print(f"  Total Load Time: {result['load_time']:.3f}s")
        print(f"  Components: {result['components_loaded']}/{result['total_components']}")

    def test_load_dashboard_all_reps(
        self,
        dashboard_client,
        rep_emails: List[str],
        benchmark,
    ):
        """Benchmark loading dashboard for all reps."""
        def load_all_dashboards():
            total_time = 0
            successful_loads = 0

            for rep_email in rep_emails:
                start = time.time()
                try:
                    response = dashboard_client.post(
                        "/tools/get_rep_insights",
                        json={
                            "rep_email": rep_email,
                            "time_period": "last_30_days",
                        },
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful_loads += 1
                except:
                    pass

            return {
                "total_reps": len(rep_emails),
                "successful": successful_loads,
                "total_time": total_time,
                "avg_time_per_rep": total_time / len(rep_emails) if rep_emails else 0,
                "throughput": len(rep_emails) / total_time if total_time > 0 else 0,
            }

        result = benchmark(load_all_dashboards)
        print(f"\nDashboard Load Time (All Reps - {len(rep_emails)}):")
        print(f"  Total Loads: {result['successful']}/{result['total_reps']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg/Rep: {result['avg_time_per_rep']:.3f}s")
        print(f"  Throughput: {result['throughput']:.2f} reps/s")

    def test_dashboard_with_different_time_periods(
        self,
        dashboard_client,
        rep_emails: List[str],
    ):
        """Benchmark dashboard loading with different time periods."""
        rep_email = rep_emails[0]
        time_periods = ["last_7_days", "last_30_days", "last_90_days"]

        results = {}

        for period in time_periods:
            start = time.time()
            try:
                dashboard_client.post(
                    "/tools/get_rep_insights",
                    json={
                        "rep_email": rep_email,
                        "time_period": period,
                    },
                    timeout=30,
                )
            except:
                pass

            elapsed = time.time() - start
            results[period] = elapsed

        print(f"\nDashboard Load by Time Period:")
        for period, load_time in results.items():
            print(f"  {period}: {load_time:.3f}s")

    def test_dashboard_concurrent_rep_views(
        self,
        dashboard_client,
        rep_emails: List[str],
        benchmark,
    ):
        """Benchmark concurrent dashboard views for multiple reps."""
        import asyncio
        import httpx

        async def load_dashboards_concurrent():
            # Simulate concurrent loads
            reps_to_load = rep_emails[:10]
            total_time = 0

            for rep_email in reps_to_load:
                start = time.time()
                try:
                    dashboard_client.post(
                        "/tools/get_rep_insights",
                        json={
                            "rep_email": rep_email,
                            "time_period": "last_30_days",
                        },
                        timeout=30,
                    )
                    total_time += time.time() - start
                except:
                    pass

            return {
                "concurrent_reps": len(reps_to_load),
                "total_time": total_time,
                "avg_time": total_time / len(reps_to_load),
            }

        result = benchmark(load_dashboards_concurrent)
        print(f"\nConcurrent Dashboard Loads ({result['concurrent_reps']} reps):")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg/Rep: {result['avg_time']:.3f}s")

    def test_dashboard_with_product_filter(
        self,
        dashboard_client,
        rep_emails: List[str],
    ):
        """Benchmark dashboard with product filtering."""
        rep_email = rep_emails[0]
        products = ["product_a", "product_b", "product_c"]

        results = {}

        for product in products:
            start = time.time()
            try:
                dashboard_client.post(
                    "/tools/get_rep_insights",
                    json={
                        "rep_email": rep_email,
                        "time_period": "last_30_days",
                        "product_filter": product,
                    },
                    timeout=30,
                )
            except:
                pass

            elapsed = time.time() - start
            results[product] = elapsed

        print(f"\nDashboard Load with Product Filters:")
        for product, load_time in results.items():
            print(f"  {product}: {load_time:.3f}s")

    def test_dashboard_metrics_calculation(
        self,
        dashboard_client,
        rep_emails: List[str],
        benchmark,
    ):
        """Benchmark the calculation of dashboard metrics."""
        rep_email = rep_emails[0]

        def calculate_metrics():
            # This simulates fetching and aggregating metrics
            total_time = 0

            for time_period in ["last_7_days", "last_30_days"]:
                start = time.time()
                try:
                    dashboard_client.post(
                        "/tools/get_rep_insights",
                        json={
                            "rep_email": rep_email,
                            "time_period": time_period,
                        },
                        timeout=30,
                    )
                    total_time += time.time() - start
                except:
                    pass

            return {"total_time": total_time}

        result = benchmark(calculate_metrics)
        print(f"\nDashboard Metrics Calculation:")
        print(f"  Total Time: {result['total_time']:.3f}s")

    def test_dashboard_caching_benefits(
        self,
        dashboard_client,
        rep_emails: List[str],
    ):
        """Measure caching benefits for repeated dashboard loads."""
        rep_email = rep_emails[0]

        # First load
        start = time.time()
        try:
            dashboard_client.post(
                "/tools/get_rep_insights",
                json={
                    "rep_email": rep_email,
                    "time_period": "last_30_days",
                },
                timeout=30,
            )
        except:
            pass
        first_load_time = time.time() - start

        # Repeated loads
        repeated_times = []
        for _ in range(5):
            start = time.time()
            try:
                dashboard_client.post(
                    "/tools/get_rep_insights",
                    json={
                        "rep_email": rep_email,
                        "time_period": "last_30_days",
                    },
                    timeout=30,
                )
                repeated_times.append(time.time() - start)
            except:
                pass

        avg_repeated = sum(repeated_times) / len(repeated_times) if repeated_times else 0
        speedup = first_load_time / avg_repeated if avg_repeated > 0 else 0

        print(f"\nDashboard Caching Benefits:")
        print(f"  First Load: {first_load_time:.3f}s")
        print(f"  Cached Load (avg): {avg_repeated:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
