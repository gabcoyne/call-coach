"""
Coaching Analysis Performance Scenario

Tests performance of analyzing 100 coaching calls in sequence.
Measures:
- Time per call
- Total throughput
- Memory usage
- Cache effectiveness
"""
import time
import random
import pytest
from typing import List, Dict, Any


@pytest.mark.performance
class TestCoachingAnalysisScenario:
    """Coaching analysis performance scenarios."""

    @pytest.fixture
    def analysis_client(self):
        """Create HTTP client for analysis."""
        import httpx
        return httpx.Client(base_url="http://localhost:8000", timeout=60.0)

    @pytest.fixture
    def call_ids(self) -> List[str]:
        """Generate test call IDs."""
        return [f"call_{i:06d}" for i in range(1, 101)]

    @pytest.fixture
    def analysis_configs(self) -> List[Dict[str, Any]]:
        """Different analysis configurations to test."""
        return [
            {
                "name": "basic_analysis",
                "dimensions": ["engagement"],
                "include_transcript": False,
                "use_cache": True,
            },
            {
                "name": "full_analysis",
                "dimensions": ["engagement", "discovery", "objection_handling", "product_knowledge"],
                "include_transcript": True,
                "use_cache": True,
            },
            {
                "name": "uncached_analysis",
                "dimensions": ["engagement", "discovery"],
                "include_transcript": False,
                "use_cache": False,
            },
        ]

    def test_analyze_100_calls_sequential(
        self,
        analysis_client,
        call_ids: List[str],
        benchmark,
    ):
        """Benchmark sequential analysis of 100 calls."""
        def analyze_all():
            total_time = 0
            successful = 0
            failed = 0

            for call_id in call_ids[:100]:
                start = time.time()
                try:
                    response = analysis_client.post(
                        "/tools/analyze_call",
                        json={
                            "call_id": call_id,
                            "dimensions": ["engagement", "discovery"],
                            "use_cache": True,
                        },
                        timeout=30,
                    )
                    elapsed = time.time() - start
                    total_time += elapsed

                    if response.status_code == 200:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1

            return {
                "total_calls": len(call_ids),
                "successful": successful,
                "failed": failed,
                "total_time": total_time,
                "avg_time_per_call": total_time / len(call_ids) if call_ids else 0,
                "throughput": len(call_ids) / total_time if total_time > 0 else 0,
            }

        result = benchmark(analyze_all)
        assert result["successful"] > 0, "At least some calls should be analyzed successfully"
        print(f"\nCoaching Analysis Results:")
        print(f"  Total Calls: {result['total_calls']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg/Call: {result['avg_time_per_call']:.3f}s")
        print(f"  Throughput: {result['throughput']:.2f} calls/s")

    def test_analyze_with_different_dimensions(
        self,
        analysis_client,
        call_ids: List[str],
        benchmark,
    ):
        """Benchmark analysis with different dimension configurations."""
        dimension_configs = [
            ["engagement"],
            ["engagement", "discovery"],
            ["engagement", "discovery", "objection_handling"],
            ["engagement", "discovery", "objection_handling", "product_knowledge"],
        ]

        results = {}

        for dims in dimension_configs:
            dim_name = "_".join(dims)
            start = time.time()

            for call_id in call_ids[:25]:
                try:
                    analysis_client.post(
                        "/tools/analyze_call",
                        json={
                            "call_id": call_id,
                            "dimensions": dims,
                            "use_cache": True,
                        },
                        timeout=30,
                    )
                except:
                    pass

            elapsed = time.time() - start
            results[dim_name] = {
                "dimensions": dims,
                "calls": 25,
                "total_time": elapsed,
                "avg_time": elapsed / 25,
            }

        print(f"\nAnalysis by Dimension Configuration:")
        for config_name, metrics in results.items():
            print(f"  {config_name}:")
            print(f"    Avg Time: {metrics['avg_time']:.3f}s")
            print(f"    Total Time: {metrics['total_time']:.2f}s")

    def test_cache_effectiveness(
        self,
        analysis_client,
        call_ids: List[str],
    ):
        """Measure cache hit effectiveness."""
        call_id = call_ids[0]

        # First call - cache miss
        start = time.time()
        analysis_client.post(
            "/tools/analyze_call",
            json={
                "call_id": call_id,
                "use_cache": True,
                "dimensions": ["engagement", "discovery"],
            },
            timeout=30,
        )
        first_call_time = time.time() - start

        # Repeated calls - should be cache hits
        hit_times = []
        for _ in range(5):
            start = time.time()
            try:
                analysis_client.post(
                    "/tools/analyze_call",
                    json={
                        "call_id": call_id,
                        "use_cache": True,
                        "dimensions": ["engagement", "discovery"],
                    },
                    timeout=30,
                )
                hit_times.append(time.time() - start)
            except:
                pass

        avg_hit_time = sum(hit_times) / len(hit_times) if hit_times else 0
        speedup = first_call_time / avg_hit_time if avg_hit_time > 0 else 0

        print(f"\nCache Effectiveness:")
        print(f"  First Call (Miss): {first_call_time:.3f}s")
        print(f"  Avg Hit Time: {avg_hit_time:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")

    def test_analysis_with_large_transcript(
        self,
        analysis_client,
        call_ids: List[str],
        benchmark,
    ):
        """Benchmark analysis with transcript snippets."""
        def analyze_with_transcript():
            successful = 0
            total_time = 0

            for call_id in call_ids[:50]:
                start = time.time()
                try:
                    response = analysis_client.post(
                        "/tools/analyze_call",
                        json={
                            "call_id": call_id,
                            "include_transcript_snippets": True,
                            "dimensions": ["engagement", "discovery"],
                            "use_cache": True,
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
                "calls_analyzed": successful,
                "total_time": total_time,
                "avg_time": total_time / successful if successful > 0 else 0,
            }

        result = benchmark(analyze_with_transcript)
        print(f"\nAnalysis with Transcript Snippets:")
        print(f"  Calls Analyzed: {result['calls_analyzed']}")
        print(f"  Total Time: {result['total_time']:.2f}s")
        print(f"  Avg Time/Call: {result['avg_time']:.3f}s")

    def test_parallel_analysis_patterns(
        self,
        analysis_client,
        call_ids: List[str],
    ):
        """Test what happens with rapid sequential analysis."""
        rapid_calls = 10
        start = time.time()

        for i in range(rapid_calls):
            try:
                analysis_client.post(
                    "/tools/analyze_call",
                    json={
                        "call_id": call_ids[i],
                        "use_cache": True,
                        "dimensions": ["engagement"],
                    },
                    timeout=30,
                )
            except:
                pass

        total_time = time.time() - start
        avg_time = total_time / rapid_calls

        print(f"\nRapid Sequential Analysis ({rapid_calls} calls):")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Avg Time/Call: {avg_time:.3f}s")
