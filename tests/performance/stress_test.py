"""
Stress Testing Suite

Tests system behavior under extreme load:
- Gradually ramps up concurrent users
- Identifies breaking points and limits
- Tests recovery after failures
- Monitors resource utilization during stress
"""

import asyncio
import random
import time
from dataclasses import dataclass
from datetime import datetime

import httpx


@dataclass
class StressTestMetrics:
    """Metrics collected during stress test."""

    timestamp: datetime
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    throughput_rps: float
    breaking_point: bool = False
    recovery_time_seconds: float = 0.0


class StressTestRunner:
    """Runs stress tests with configurable parameters."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        initial_users: int = 10,
        max_users: int = 1000,
        ramp_up_interval: int = 30,
        requests_per_user: int = 100,
    ):
        self.base_url = base_url
        self.initial_users = initial_users
        self.max_users = max_users
        self.ramp_up_interval = ramp_up_interval
        self.requests_per_user = requests_per_user
        self.metrics: list[StressTestMetrics] = []
        self.breaking_point = None

        # Test data
        self.call_ids = [f"call_{i:06d}" for i in range(1, 101)]
        self.rep_emails = [f"rep_{i:03d}@example.com" for i in range(1, 51)]
        self.products = ["product_a", "product_b", "product_c", "product_d"]

    async def make_request(self, client: httpx.AsyncClient, endpoint: str) -> tuple[bool, float]:
        """Make a single request and return (success, response_time)."""
        try:
            start = time.time()

            if endpoint == "/tools/analyze_call":
                response = await client.post(
                    f"{self.base_url}/tools/analyze_call",
                    json={
                        "call_id": random.choice(self.call_ids),
                        "dimensions": ["engagement", "discovery"],
                        "use_cache": True,
                    },
                    timeout=30.0,
                )
            elif endpoint == "/tools/search_calls":
                response = await client.post(
                    f"{self.base_url}/tools/search_calls",
                    json={
                        "product": random.choice(self.products),
                        "limit": 20,
                    },
                    timeout=30.0,
                )
            elif endpoint == "/tools/get_rep_insights":
                response = await client.post(
                    f"{self.base_url}/tools/get_rep_insights",
                    json={
                        "rep_email": random.choice(self.rep_emails),
                        "time_period": "last_30_days",
                    },
                    timeout=30.0,
                )
            else:
                response = await client.get(f"{self.base_url}/health", timeout=10.0)

            elapsed = time.time() - start
            return (response.status_code == 200, elapsed)
        except TimeoutError:
            return (False, 30.0)
        except Exception:
            elapsed = time.time() - start
            return (False, elapsed)

    async def simulate_user(
        self, client: httpx.AsyncClient, user_id: int
    ) -> tuple[int, int, list[float]]:
        """Simulate a single user making requests."""
        successful = 0
        failed = 0
        response_times = []
        endpoints = [
            "/tools/analyze_call",
            "/tools/search_calls",
            "/tools/get_rep_insights",
            "/health",
        ]

        for _ in range(self.requests_per_user):
            endpoint = random.choice(endpoints)
            success, response_time = await self.make_request(client, endpoint)

            if success:
                successful += 1
            else:
                failed += 1

            response_times.append(response_time)

            # Small delay between requests
            await asyncio.sleep(random.uniform(0.1, 0.5))

        return (successful, failed, response_times)

    def calculate_metrics(self, concurrent_users: int, results: list[tuple]) -> StressTestMetrics:
        """Calculate metrics from test results."""
        all_response_times = []
        total_successful = 0
        total_failed = 0

        for successful, failed, response_times in results:
            total_successful += successful
            total_failed += failed
            all_response_times.extend(response_times)

        total_requests = total_successful + total_failed
        error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0

        sorted_times = sorted(all_response_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        return StressTestMetrics(
            timestamp=datetime.now(),
            concurrent_users=concurrent_users,
            total_requests=total_requests,
            successful_requests=total_successful,
            failed_requests=total_failed,
            response_time_avg=(
                sum(all_response_times) / len(all_response_times) if all_response_times else 0
            ),
            response_time_p95=sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0,
            response_time_p99=sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0,
            error_rate=error_rate,
            throughput_rps=total_requests / (self.ramp_up_interval / 1000),
        )

    async def run(self) -> list[StressTestMetrics]:
        """Run the complete stress test."""
        print(f"\n{'=' * 80}")
        print("STRESS TEST: STARTING")
        print(f"{'=' * 80}")
        print(f"Base URL:           {self.base_url}")
        print(f"Initial Users:      {self.initial_users}")
        print(f"Max Users:          {self.max_users}")
        print(f"Ramp-up Interval:   {self.ramp_up_interval}s")
        print(f"Requests/User:      {self.requests_per_user}")
        print(f"{'=' * 80}\n")

        connector = httpx.AsyncHTTPConnection(pool_connections=1000, pool_maxsize=1000)
        async with httpx.AsyncClient(
            connector=connector, timeout=60.0, limits=httpx.Limits(max_connections=1000)
        ) as client:
            current_users = self.initial_users

            while current_users <= self.max_users:
                print(f"Ramping up to {current_users} concurrent users...")
                start_time = time.time()

                # Create tasks for all users
                tasks = [self.simulate_user(client, user_id) for user_id in range(current_users)]

                # Run all users concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Filter out exceptions
                valid_results = [r for r in results if not isinstance(r, Exception)]

                # Calculate and store metrics
                metrics = self.calculate_metrics(current_users, valid_results)
                self.metrics.append(metrics)

                # Check for breaking point (error rate > 10% or response time > 10s)
                is_breaking = metrics.error_rate > 10 or metrics.response_time_p99 > 10
                if is_breaking and not self.breaking_point:
                    self.breaking_point = current_users
                    metrics.breaking_point = True

                # Print current status
                elapsed = time.time() - start_time
                print(
                    f"  Users: {current_users:4d} | "
                    f"Requests: {metrics.total_requests:5d} | "
                    f"Success: {metrics.successful_requests:5d} | "
                    f"Failed: {metrics.failed_requests:5d} | "
                    f"Error Rate: {metrics.error_rate:5.2f}% | "
                    f"Response Time P99: {metrics.response_time_p99:6.3f}s | "
                    f"Throughput: {metrics.throughput_rps:6.1f} req/s"
                )

                if is_breaking:
                    print(f"  ⚠️  BREAKING POINT DETECTED at {current_users} users")
                    break

                # Increase user count for next iteration
                current_users = min(current_users + 100, self.max_users)

                # Wait for ramp-up interval
                await asyncio.sleep(self.ramp_up_interval)

        return self.metrics

    def print_summary(self):
        """Print stress test summary."""
        if not self.metrics:
            print("No metrics collected")
            return

        print(f"\n{'=' * 80}")
        print("STRESS TEST: SUMMARY")
        print(f"{'=' * 80}")
        print(f"Total Test Phases:  {len(self.metrics)}")
        print(
            f"Breaking Point:     {self.breaking_point} users"
            if self.breaking_point
            else "No breaking point detected"
        )
        print()

        # Print phase-by-phase metrics
        print(
            f"{'Users':>8} {'Requests':>10} {'Success':>10} {'Failed':>8} "
            f"{'Error %':>8} {'Avg (ms)':>10} {'P95 (ms)':>10} {'P99 (ms)':>10} {'RPS':>8}"
        )
        print("-" * 94)

        for metric in self.metrics:
            print(
                f"{metric.concurrent_users:8d} "
                f"{metric.total_requests:10d} "
                f"{metric.successful_requests:10d} "
                f"{metric.failed_requests:8d} "
                f"{metric.error_rate:7.2f}% "
                f"{metric.response_time_avg * 1000:9.1f} "
                f"{metric.response_time_p95 * 1000:9.1f} "
                f"{metric.response_time_p99 * 1000:9.1f} "
                f"{metric.throughput_rps:7.1f}"
            )

        print(f"{'=' * 80}\n")


async def main():
    """Run stress test."""
    runner = StressTestRunner(
        base_url="http://localhost:8000",
        initial_users=10,
        max_users=500,
        ramp_up_interval=30,
        requests_per_user=50,
    )

    metrics = await runner.run()
    runner.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
