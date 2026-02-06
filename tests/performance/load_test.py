"""
Load Testing Suite using Locust

Simulates realistic user load on the Call Coaching API:
- 100 concurrent users
- 1000 coaching analyses
- Search queries with various filters
- Measures response times, throughput, and error rates
"""

import random
import time
from datetime import datetime, timedelta

from locust import HttpUser, TaskSet, between, events, task


# Statistics tracking
class LoadTestStats:
    """Track performance metrics during load test."""

    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = None

    def add_response(self, response_time: float, success: bool):
        """Record a response."""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def get_percentile(self, percentile: int) -> float:
        """Calculate percentile response time."""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * (percentile / 100))
        return sorted_times[min(index, len(sorted_times) - 1)]

    def get_summary(self) -> dict:
        """Get summary statistics."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        total = self.success_count + self.error_count

        return {
            "total_requests": total,
            "successful": self.success_count,
            "failed": self.error_count,
            "error_rate": self.error_count / total * 100 if total > 0 else 0,
            "elapsed_seconds": elapsed,
            "throughput_rps": total / elapsed if elapsed > 0 else 0,
            "response_time_p50": self.get_percentile(50),
            "response_time_p95": self.get_percentile(95),
            "response_time_p99": self.get_percentile(99),
            "response_time_avg": (
                sum(self.response_times) / len(self.response_times) if self.response_times else 0
            ),
            "response_time_max": max(self.response_times) if self.response_times else 0,
        }


# Global stats
load_test_stats = LoadTestStats()


class CoachingAPITasks(TaskSet):
    """API endpoint load test tasks."""

    def on_start(self):
        """Initialize test data."""
        self.call_ids = [f"call_{i:06d}" for i in range(1, 101)]
        self.rep_emails = [f"rep_{i:03d}@example.com" for i in range(1, 51)]
        self.opportunity_ids = [f"opp_{i:06d}" for i in range(1, 51)]
        self.products = ["product_a", "product_b", "product_c", "product_d"]
        self.call_types = ["discovery", "demo", "negotiation", "closing"]

    @task(5)
    def analyze_call(self):
        """Analyze a coaching call."""
        call_id = random.choice(self.call_ids)
        start = time.time()
        try:
            response = self.client.post(
                "/tools/analyze_call",
                json={
                    "call_id": call_id,
                    "dimensions": ["engagement", "discovery", "objection_handling"],
                    "use_cache": random.choice([True, False]),
                    "include_transcript_snippets": True,
                    "force_reanalysis": False,
                },
                timeout=30,
            )
            elapsed = time.time() - start
            success = response.status_code == 200
            load_test_stats.add_response(elapsed, success)
            if not success:
                self.client.request_failure(
                    "POST",
                    "/tools/analyze_call",
                    response.status_code,
                    response.text,
                )
        except Exception as e:
            elapsed = time.time() - start
            load_test_stats.add_response(elapsed, False)
            self.client.request_failure("POST", "/tools/analyze_call", 0, str(e))

    @task(3)
    def get_rep_insights(self):
        """Get sales rep insights."""
        rep_email = random.choice(self.rep_emails)
        start = time.time()
        try:
            response = self.client.post(
                "/tools/get_rep_insights",
                json={
                    "rep_email": rep_email,
                    "time_period": random.choice(["last_7_days", "last_30_days", "last_90_days"]),
                    "product_filter": random.choice(self.products + [None]),
                },
                timeout=30,
            )
            elapsed = time.time() - start
            success = response.status_code == 200
            load_test_stats.add_response(elapsed, success)
            if not success:
                self.client.request_failure(
                    "POST",
                    "/tools/get_rep_insights",
                    response.status_code,
                    response.text,
                )
        except Exception as e:
            elapsed = time.time() - start
            load_test_stats.add_response(elapsed, False)
            self.client.request_failure("POST", "/tools/get_rep_insights", 0, str(e))

    @task(4)
    def search_calls(self):
        """Search for calls with various filters."""
        start = time.time()
        date_range_days = random.choice([7, 30, 90])
        start_date = (datetime.now() - timedelta(days=date_range_days)).isoformat()
        end_date = datetime.now().isoformat()

        try:
            response = self.client.post(
                "/tools/search_calls",
                json={
                    "rep_email": random.choice(self.rep_emails + [None]),
                    "product": random.choice(self.products + [None]),
                    "call_type": random.choice(self.call_types + [None]),
                    "date_range": {
                        "start": start_date,
                        "end": end_date,
                    },
                    "min_score": random.choice([None, 60, 70]),
                    "max_score": random.choice([None, 80, 90]),
                    "limit": random.choice([10, 20, 50]),
                },
                timeout=30,
            )
            elapsed = time.time() - start
            success = response.status_code == 200
            load_test_stats.add_response(elapsed, success)
            if not success:
                self.client.request_failure(
                    "POST",
                    "/tools/search_calls",
                    response.status_code,
                    response.text,
                )
        except Exception as e:
            elapsed = time.time() - start
            load_test_stats.add_response(elapsed, False)
            self.client.request_failure("POST", "/tools/search_calls", 0, str(e))

    @task(2)
    def analyze_opportunity(self):
        """Analyze an opportunity."""
        opp_id = random.choice(self.opportunity_ids)
        start = time.time()
        try:
            response = self.client.post(
                "/tools/analyze_opportunity",
                json={"opportunity_id": opp_id},
                timeout=30,
            )
            elapsed = time.time() - start
            success = response.status_code == 200
            load_test_stats.add_response(elapsed, success)
            if not success:
                self.client.request_failure(
                    "POST",
                    "/tools/analyze_opportunity",
                    response.status_code,
                    response.text,
                )
        except Exception as e:
            elapsed = time.time() - start
            load_test_stats.add_response(elapsed, False)
            self.client.request_failure("POST", "/tools/analyze_opportunity", 0, str(e))

    @task(1)
    def health_check(self):
        """Check API health."""
        start = time.time()
        try:
            response = self.client.get("/health", timeout=10)
            elapsed = time.time() - start
            success = response.status_code == 200
            load_test_stats.add_response(elapsed, success)
        except Exception:
            elapsed = time.time() - start
            load_test_stats.add_response(elapsed, False)


class CoachingAPIUser(HttpUser):
    """Simulated API user."""

    tasks = [CoachingAPITasks]
    wait_time = between(0.5, 2.0)


# Event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize stats when test starts."""
    load_test_stats.start_time = datetime.now()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print final statistics."""
    stats = load_test_stats.get_summary()
    print("\n" + "=" * 80)
    print("LOAD TEST SUMMARY")
    print("=" * 80)
    print(f"Total Requests:     {stats['total_requests']}")
    print(f"Successful:         {stats['successful']}")
    print(f"Failed:             {stats['failed']}")
    print(f"Error Rate:         {stats['error_rate']:.2f}%")
    print(f"Duration:           {stats['elapsed_seconds']:.1f}s")
    print(f"Throughput:         {stats['throughput_rps']:.2f} req/s")
    print(f"Response Time P50:  {stats['response_time_p50']:.3f}s")
    print(f"Response Time P95:  {stats['response_time_p95']:.3f}s")
    print(f"Response Time P99:  {stats['response_time_p99']:.3f}s")
    print(f"Response Time Avg:  {stats['response_time_avg']:.3f}s")
    print(f"Response Time Max:  {stats['response_time_max']:.3f}s")
    print("=" * 80)


if __name__ == "__main__":
    # For local testing:
    # locust -f tests/performance/load_test.py \
    #   --host=http://localhost:8000 \
    #   --users=100 \
    #   --spawn-rate=5 \
    #   --run-time=5m
    pass
