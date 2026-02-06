"""
Performance profiling for identifying bottlenecks and slow requests.

Generates flame graphs and performance reports for coaching analysis operations.
Helps identify optimization opportunities in API and analysis pipelines.
"""

import cProfile
import io
import logging
import pstats
import time
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Profiles function execution time and resource usage."""

    def __init__(self, output_dir: Path | None = None):
        """
        Initialize performance profiler.

        Args:
            output_dir: Directory to save profile reports
        """
        self.output_dir = output_dir or Path("./profiling_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.profiles: dict[str, dict[str, Any]] = {}

    @contextmanager
    def profile_block(self, block_name: str):
        """
        Context manager for profiling a code block.

        Args:
            block_name: Name of the block being profiled
        """
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            memory_delta = self._get_memory_usage() - start_memory

            if block_name not in self.profiles:
                self.profiles[block_name] = {
                    "calls": 0,
                    "total_time": 0,
                    "min_time": float("inf"),
                    "max_time": 0,
                    "total_memory": 0,
                    "call_times": [],
                }

            profile = self.profiles[block_name]
            profile["calls"] += 1
            profile["total_time"] += duration
            profile["min_time"] = min(profile["min_time"], duration)
            profile["max_time"] = max(profile["max_time"], duration)
            profile["total_memory"] += memory_delta
            profile["call_times"].append(duration)

            logger.debug(
                f"Profile [{block_name}]: {duration:.3f}s, memory: {memory_delta / 1024 / 1024:.2f}MB"
            )

    def profile_function(self, func: Callable) -> Callable:
        """
        Decorator to profile function execution.

        Args:
            func: Function to profile
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__
            with self.profile_block(func_name):
                return func(*args, **kwargs)

        return wrapper

    async def profile_async_function(self, func: Callable) -> Callable:
        """
        Decorator to profile async function execution.

        Args:
            func: Async function to profile
        """

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__
            with self.profile_block(func_name):
                return await func(*args, **kwargs)

        return wrapper

    def get_report(self, block_name: str | None = None) -> str:
        """
        Get profiling report for a specific block or all blocks.

        Args:
            block_name: Name of block to report on (None for all)

        Returns:
            Formatted profiling report
        """
        report = []
        report.append("=" * 80)
        report.append("Performance Profile Report")
        report.append(f"Generated: {datetime.utcnow().isoformat()}Z")
        report.append("=" * 80)
        report.append("")

        profiles_to_report = (
            {block_name: self.profiles[block_name]}
            if block_name and block_name in self.profiles
            else self.profiles
        )

        for name, data in sorted(
            profiles_to_report.items(), key=lambda x: x[1]["total_time"], reverse=True
        ):
            report.append(f"Block: {name}")
            report.append(f"  Calls: {data['calls']}")
            report.append(f"  Total Time: {data['total_time']:.3f}s")
            report.append(f"  Average Time: {data['total_time'] / data['calls']:.3f}s")
            report.append(f"  Min Time: {data['min_time']:.3f}s")
            report.append(f"  Max Time: {data['max_time']:.3f}s")
            report.append(f"  Total Memory: {data['total_memory'] / 1024 / 1024:.2f}MB")

            # Show slowest calls
            if data["call_times"]:
                slowest = sorted(data["call_times"], reverse=True)[:3]
                report.append(f"  Slowest Calls: {', '.join(f'{t:.3f}s' for t in slowest)}")

            report.append("")

        return "\n".join(report)

    def save_report(self, block_name: str | None = None) -> Path:
        """
        Save profiling report to file.

        Args:
            block_name: Name of block to save (None for all)

        Returns:
            Path to saved report
        """
        report = self.get_report(block_name)
        filename = f"profile_{datetime.utcnow().isoformat()}_{block_name or 'all'}.txt"
        filepath = self.output_dir / filename
        filepath.write_text(report)
        logger.info(f"Profiling report saved to {filepath}")
        return filepath

    def reset(self) -> None:
        """Clear all profiling data."""
        self.profiles.clear()

    @staticmethod
    def _get_memory_usage() -> int:
        """Get current process memory usage in bytes."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0


class CPUProfiler:
    """CPU profiler using cProfile for detailed function-level profiling."""

    def __init__(self, output_dir: Path | None = None):
        """
        Initialize CPU profiler.

        Args:
            output_dir: Directory to save profile data
        """
        self.output_dir = output_dir or Path("./profiling_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def profile_cpu(self, profile_name: str):
        """
        Context manager for CPU profiling.

        Args:
            profile_name: Name for the profile
        """
        profiler = cProfile.Profile()
        profiler.enable()

        try:
            yield profiler
        finally:
            profiler.disable()
            self._save_profile(profiler, profile_name)

    def _save_profile(self, profiler: cProfile.Profile, name: str) -> Path:
        """Save profile data and generate report."""
        # Save raw profile data
        filename = f"cpu_profile_{datetime.utcnow().isoformat()}_{name}.prof"
        filepath = self.output_dir / filename
        profiler.dump_stats(str(filepath))

        # Generate text report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # Top 20 functions

        report_filename = f"cpu_profile_{datetime.utcnow().isoformat()}_{name}.txt"
        report_filepath = self.output_dir / report_filename
        report_filepath.write_text(s.getvalue())

        logger.info(f"CPU profile saved to {filepath}")
        logger.info(f"CPU profile report saved to {report_filepath}")

        return filepath

    def profile_function(self, func: Callable) -> Callable:
        """
        Decorator for CPU profiling a function.

        Args:
            func: Function to profile
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__
            with self.profile_cpu(func_name):
                return func(*args, **kwargs)

        return wrapper


class SlowRequestDetector:
    """Detects and logs slow requests for analysis."""

    def __init__(self, threshold_seconds: float = 2.0):
        """
        Initialize slow request detector.

        Args:
            threshold_seconds: Threshold for considering request slow
        """
        self.threshold_seconds = threshold_seconds
        self.slow_requests: list[dict[str, Any]] = []

    def check_request(
        self,
        request_id: str,
        endpoint: str,
        duration: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Check if request was slow and log if needed.

        Args:
            request_id: Unique request ID
            endpoint: API endpoint
            duration: Request duration in seconds
            metadata: Additional request metadata
        """
        if duration > self.threshold_seconds:
            slow_request = {
                "request_id": request_id,
                "endpoint": endpoint,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
            self.slow_requests.append(slow_request)

            logger.warning(
                f"Slow request detected: {endpoint} took {duration:.2f}s (threshold: {self.threshold_seconds}s)"
            )

    def get_slow_requests(self, limit: int | None = None) -> list[dict[str, Any]]:
        """
        Get slow requests, optionally limited.

        Args:
            limit: Maximum number of requests to return

        Returns:
            List of slow requests
        """
        requests = sorted(self.slow_requests, key=lambda x: x["duration"], reverse=True)
        return requests[:limit] if limit else requests

    def clear(self) -> None:
        """Clear slow request log."""
        self.slow_requests.clear()


# Global profiler instances
_performance_profiler: PerformanceProfiler | None = None
_cpu_profiler: CPUProfiler | None = None
_slow_detector: SlowRequestDetector | None = None


def get_performance_profiler() -> PerformanceProfiler:
    """Get or create global performance profiler."""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler


def get_cpu_profiler() -> CPUProfiler:
    """Get or create global CPU profiler."""
    global _cpu_profiler
    if _cpu_profiler is None:
        _cpu_profiler = CPUProfiler()
    return _cpu_profiler


def get_slow_request_detector() -> SlowRequestDetector:
    """Get or create global slow request detector."""
    global _slow_detector
    if _slow_detector is None:
        _slow_detector = SlowRequestDetector()
    return _slow_detector


def profile_request(func: Callable) -> Callable:
    """
    Decorator to profile a request handler.

    Args:
        func: Request handler function
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        profiler = get_performance_profiler()
        func_name = func.__qualname__
        with profiler.profile_block(func_name):
            return await func(*args, **kwargs)

    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        profiler = get_performance_profiler()
        func_name = func.__qualname__
        with profiler.profile_block(func_name):
            return func(*args, **kwargs)

    # Return appropriate wrapper based on function type
    import inspect

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def initialize_profiling(output_dir: str | None = None) -> None:
    """Initialize profiling infrastructure."""
    global _performance_profiler, _cpu_profiler, _slow_detector
    _performance_profiler = PerformanceProfiler(Path(output_dir) if output_dir else None)
    _cpu_profiler = CPUProfiler(Path(output_dir) if output_dir else None)
    _slow_detector = SlowRequestDetector()
    logger.info("Profiling infrastructure initialized")
