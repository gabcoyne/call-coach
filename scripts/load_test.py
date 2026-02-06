"""Load testing script using Locust for the Call Coaching API."""

import os
import random

from locust import HttpUser, TaskSet, between, task
from locust.contrib.fasthttp import FastHttpUser


class CallCoachingTasks(TaskSet):
    """Define load test tasks."""

    def on_start(self):
        """Called when a user starts."""
        self.call_ids = [
            "1234567890",
            "1234567891",
            "1234567892",
            "1234567893",
            "1234567894",
        ]
        self.rep_emails = [
            "sarah@example.com",
            "john@example.com",
            "jane@example.com",
            "mike@example.com",
            "lisa@example.com",
        ]

    @task(3)
    def health_check(self):
        """Test health check endpoint."""
        self.client.get("/health")

    @task(2)
    def analyze_call(self):
        """Simulate call analysis requests."""
        call_id = random.choice(self.call_ids)
        self.client.post(
            "/tools/analyze_call",
            json={
                "call_id": call_id,
                "use_cache": True,
                "include_transcript_snippets": True,
            },
        )

    @task(2)
    def get_rep_insights(self):
        """Simulate rep insights requests."""
        rep_email = random.choice(self.rep_emails)
        self.client.post(
            "/tools/rep_insights",
            json={
                "rep_email": rep_email,
                "time_period": random.choice(["last_7_days", "last_30_days", "last_quarter"]),
            },
        )

    @task(1)
    def search_calls(self):
        """Simulate call search requests."""
        self.client.post(
            "/tools/search_calls",
            json={
                "rep_email": random.choice(self.rep_emails),
                "min_score": random.randint(50, 80),
                "limit": random.randint(10, 50),
            },
        )

    @task(1)
    def search_calls_by_objection(self):
        """Simulate objection-based searches."""
        self.client.post(
            "/tools/search_calls",
            json={
                "has_objection_type": random.choice(["pricing", "timing", "technical"]),
                "limit": 20,
            },
        )


class CallCoachingUser(HttpUser):
    """User class for load testing."""

    tasks = [CallCoachingTasks]
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests


class CallCoachingFastUser(FastHttpUser):
    """Fast HTTP user for higher throughput testing."""

    tasks = [CallCoachingTasks]
    wait_time = between(0.5, 2)  # Shorter wait time for stress testing


def run_load_test():
    """Run load test programmatically."""
    import sys

    from locust import main

    # Default parameters
    host = os.getenv("LOAD_TEST_HOST", "http://localhost:8000")
    users = int(os.getenv("LOAD_TEST_USERS", "10"))
    spawn_rate = int(os.getenv("LOAD_TEST_SPAWN_RATE", "2"))
    duration = os.getenv("LOAD_TEST_DURATION", "5m")

    # Build command line args
    args = [
        "locust",
        "--host",
        host,
        "--users",
        str(users),
        "--spawn-rate",
        str(spawn_rate),
        "--run-time",
        duration,
        "--headless",
        "--csv=results",
    ]

    # Run locust
    sys.argv = args
    main.main()


if __name__ == "__main__":
    run_load_test()
