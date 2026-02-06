"""
Cache statistics collector and dashboard.

Provides:
- Real-time cache hit/miss rates
- Performance metrics (latency, throughput)
- Cost savings calculations
- Prometheus metrics export
- Dashboard-ready JSON API
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from cache.redis_client import get_redis_cache
from db import fetch_all, fetch_one

logger = logging.getLogger(__name__)


class CacheStatsCollector:
    """
    Collects and aggregates cache performance statistics.

    Metrics tracked:
    - Cache hit/miss rates (Redis + Database)
    - Token savings from caching
    - Cost savings estimates
    - Cache size and memory usage
    - Query performance improvements
    """

    def __init__(self):
        """Initialize cache stats collector."""
        self.redis_cache = get_redis_cache()

    def get_comprehensive_stats(self, days_back: int = 7) -> dict[str, Any]:
        """
        Get comprehensive cache statistics.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dict with all cache metrics
        """
        # Get Redis stats
        redis_stats = self._get_redis_stats()

        # Get database cache stats
        db_stats = self._get_database_cache_stats(days_back)

        # Get cost savings
        cost_stats = self._calculate_cost_savings(db_stats)

        # Get performance metrics
        perf_stats = self._get_performance_metrics(days_back)

        return {
            "timestamp": datetime.now().isoformat(),
            "period_days": days_back,
            "redis": redis_stats,
            "database": db_stats,
            "cost_savings": cost_stats,
            "performance": perf_stats,
            "health": self._assess_cache_health(redis_stats, db_stats),
        }

    def _get_redis_stats(self) -> dict[str, Any]:
        """Get Redis-specific statistics."""
        if not self.redis_cache.available:
            return {"available": False, "reason": "Redis not configured or not reachable"}

        return self.redis_cache.get_stats()

    def _get_database_cache_stats(self, days_back: int) -> dict[str, Any]:
        """
        Get cache statistics from database.

        Analyzes coaching_sessions table to determine cache effectiveness.
        """
        try:
            cutoff = datetime.now() - timedelta(days=days_back)

            # Query database for cache statistics
            stats = fetch_one(
                """
                SELECT
                    COUNT(*) as total_analyses,
                    COUNT(DISTINCT transcript_hash) as unique_transcripts,
                    COUNT(DISTINCT cache_key) as unique_cache_keys,
                    COUNT(*) - COUNT(DISTINCT transcript_hash) as estimated_cache_hits,
                    COUNT(DISTINCT call_id) as unique_calls,
                    COUNT(DISTINCT rep_id) as unique_reps,
                    ROUND(AVG(score), 2) as avg_score,
                    COUNT(DISTINCT coaching_dimension) as dimensions_analyzed
                FROM coaching_sessions
                WHERE created_at > %s
                """,
                (cutoff,),
            )

            if not stats or stats["total_analyses"] == 0:
                return {
                    "total_analyses": 0,
                    "cache_hit_rate": 0.0,
                    "message": "No analyses in time period",
                }

            total = stats["total_analyses"]
            cache_hits = stats["estimated_cache_hits"]
            hit_rate = (cache_hits / total * 100) if total > 0 else 0

            return {
                "total_analyses": total,
                "unique_transcripts": stats["unique_transcripts"],
                "unique_cache_keys": stats["unique_cache_keys"],
                "estimated_cache_hits": cache_hits,
                "cache_misses": total - cache_hits,
                "cache_hit_rate": round(hit_rate, 2),
                "unique_calls": stats["unique_calls"],
                "unique_reps": stats["unique_reps"],
                "avg_score": float(stats["avg_score"]) if stats["avg_score"] else 0,
                "dimensions_analyzed": stats["dimensions_analyzed"],
            }

        except Exception as e:
            logger.error(f"Error getting database cache stats: {e}")
            return {"error": str(e)}

    def _calculate_cost_savings(self, db_stats: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate cost savings from caching.

        Assumptions:
        - Average analysis: 30K input tokens
        - Cost per 1K tokens: $0.003 (Sonnet)
        - Cache reduces repeat analysis cost to ~$0
        """
        if "error" in db_stats or db_stats.get("total_analyses", 0) == 0:
            return {
                "tokens_saved": 0,
                "cost_savings_usd": 0.0,
                "analysis_cost_with_cache": 0.0,
                "analysis_cost_without_cache": 0.0,
            }

        cache_hits = db_stats.get("estimated_cache_hits", 0)
        total_analyses = db_stats.get("total_analyses", 0)

        # Token calculations
        avg_tokens_per_analysis = 30000  # Conservative estimate
        tokens_saved = cache_hits * avg_tokens_per_analysis
        tokens_used = total_analyses * avg_tokens_per_analysis

        # Cost calculations (Sonnet pricing)
        cost_per_1k_tokens = 0.003
        cost_without_cache = (tokens_used / 1000) * cost_per_1k_tokens
        cost_saved = (tokens_saved / 1000) * cost_per_1k_tokens
        cost_with_cache = cost_without_cache - cost_saved

        return {
            "tokens_saved": tokens_saved,
            "tokens_used": tokens_used,
            "cost_savings_usd": round(cost_saved, 2),
            "analysis_cost_with_cache": round(cost_with_cache, 2),
            "analysis_cost_without_cache": round(cost_without_cache, 2),
            "savings_percentage": round(
                (cost_saved / cost_without_cache * 100) if cost_without_cache > 0 else 0, 1
            ),
        }

    def _get_performance_metrics(self, days_back: int) -> dict[str, Any]:
        """
        Get query performance metrics.

        Measures impact of caching and indexes on query speed.
        """
        try:
            cutoff = datetime.now() - timedelta(days=days_back)

            # Get analysis run statistics
            perf_stats = fetch_one(
                """
                SELECT
                    COUNT(*) as total_runs,
                    COUNT(*) FILTER (WHERE cache_hit = true) as cache_hits,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed,
                    ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - started_at))), 2) as avg_duration_seconds,
                    ROUND(AVG(total_tokens_used), 0) as avg_tokens_per_run
                FROM analysis_runs
                WHERE started_at > %s
                """,
                (cutoff,),
            )

            if not perf_stats:
                return {}

            total = perf_stats.get("total_runs", 0)
            cache_hits = perf_stats.get("cache_hits", 0)
            hit_rate = (cache_hits / total * 100) if total > 0 else 0

            return {
                "total_runs": total,
                "cache_hits": cache_hits,
                "cache_hit_rate": round(hit_rate, 2),
                "completed_runs": perf_stats.get("completed", 0),
                "failed_runs": perf_stats.get("failed", 0),
                "success_rate": round(
                    (perf_stats.get("completed", 0) / total * 100) if total > 0 else 0, 2
                ),
                "avg_duration_seconds": (
                    float(perf_stats["avg_duration_seconds"])
                    if perf_stats.get("avg_duration_seconds")
                    else 0
                ),
                "avg_tokens_per_run": (
                    int(perf_stats["avg_tokens_per_run"])
                    if perf_stats.get("avg_tokens_per_run")
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}

    def _assess_cache_health(
        self, redis_stats: dict[str, Any], db_stats: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Assess overall cache health.

        Returns health status and recommendations.
        """
        health = {
            "status": "healthy",
            "issues": [],
            "recommendations": [],
        }

        # Check Redis availability
        if not redis_stats.get("available"):
            health["status"] = "degraded"
            health["issues"].append("Redis cache not available")
            health["recommendations"].append("Check Redis connection and ensure service is running")

        # Check cache hit rate
        hit_rate = db_stats.get("cache_hit_rate", 0)
        if hit_rate < 50:
            health["status"] = "degraded"
            health["issues"].append(f"Low cache hit rate: {hit_rate}%")
            health["recommendations"].append(
                "Consider increasing cache TTL or warming cache more frequently"
            )
        elif hit_rate < 70:
            if health["status"] == "healthy":
                health["status"] = "warning"
            health["issues"].append(f"Below target cache hit rate: {hit_rate}% (target: 70%+)")

        # Check Redis memory usage
        if redis_stats.get("available"):
            memory_mb = redis_stats.get("memory_used_mb", 0)
            if memory_mb > 1000:  # More than 1GB
                health["issues"].append(f"High Redis memory usage: {memory_mb}MB")
                health["recommendations"].append(
                    "Consider reducing cache TTL or implementing cache eviction"
                )

        # Add positive notes if healthy
        if health["status"] == "healthy":
            health["recommendations"].append("Cache performing optimally")

        return health

    def get_dimension_breakdown(self, days_back: int = 7) -> dict[str, Any]:
        """
        Get cache statistics broken down by coaching dimension.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dict with per-dimension statistics
        """
        try:
            cutoff = datetime.now() - timedelta(days=days_back)

            dimension_stats = fetch_all(
                """
                SELECT
                    coaching_dimension,
                    COUNT(*) as total_analyses,
                    COUNT(DISTINCT transcript_hash) as unique_transcripts,
                    COUNT(*) - COUNT(DISTINCT transcript_hash) as cache_hits,
                    ROUND(AVG(score), 2) as avg_score,
                    COUNT(DISTINCT rubric_version) as rubric_versions
                FROM coaching_sessions
                WHERE created_at > %s
                GROUP BY coaching_dimension
                ORDER BY total_analyses DESC
                """,
                (cutoff,),
            )

            breakdown = {}
            for row in dimension_stats:
                dimension = row["coaching_dimension"]
                total = row["total_analyses"]
                cache_hits = row["cache_hits"]
                hit_rate = (cache_hits / total * 100) if total > 0 else 0

                breakdown[dimension] = {
                    "total_analyses": total,
                    "unique_transcripts": row["unique_transcripts"],
                    "cache_hits": cache_hits,
                    "cache_hit_rate": round(hit_rate, 2),
                    "avg_score": float(row["avg_score"]) if row["avg_score"] else 0,
                    "rubric_versions": row["rubric_versions"],
                }

            return breakdown

        except Exception as e:
            logger.error(f"Error getting dimension breakdown: {e}")
            return {"error": str(e)}

    def export_prometheus_metrics(self) -> str:
        """
        Export cache metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics string
        """
        stats = self.get_comprehensive_stats(days_back=1)

        lines = [
            "# HELP cache_hit_rate Cache hit rate percentage",
            "# TYPE cache_hit_rate gauge",
            f"cache_hit_rate{{source=\"database\"}} {stats['database'].get('cache_hit_rate', 0)}",
        ]

        if stats["redis"].get("available"):
            lines.extend(
                [
                    "# HELP redis_cache_hit_rate Redis cache hit rate percentage",
                    "# TYPE redis_cache_hit_rate gauge",
                    f"redis_cache_hit_rate {stats['redis'].get('hit_rate', 0)}",
                    "",
                    "# HELP redis_memory_used_mb Redis memory usage in MB",
                    "# TYPE redis_memory_used_mb gauge",
                    f"redis_memory_used_mb {stats['redis'].get('memory_used_mb', 0)}",
                    "",
                    "# HELP redis_total_keys Total keys in Redis",
                    "# TYPE redis_total_keys gauge",
                    f"redis_total_keys {stats['redis'].get('total_keys', 0)}",
                ]
            )

        lines.extend(
            [
                "",
                "# HELP cache_cost_savings_usd Cost savings from caching in USD",
                "# TYPE cache_cost_savings_usd counter",
                f"cache_cost_savings_usd {stats['cost_savings'].get('cost_savings_usd', 0)}",
                "",
                "# HELP cache_tokens_saved Total tokens saved by caching",
                "# TYPE cache_tokens_saved counter",
                f"cache_tokens_saved {stats['cost_savings'].get('tokens_saved', 0)}",
                "",
                "# HELP analysis_runs_total Total analysis runs",
                "# TYPE analysis_runs_total counter",
                f"analysis_runs_total {stats['performance'].get('total_runs', 0)}",
                "",
                "# HELP analysis_success_rate Analysis success rate percentage",
                "# TYPE analysis_success_rate gauge",
                f"analysis_success_rate {stats['performance'].get('success_rate', 0)}",
            ]
        )

        return "\n".join(lines)


def get_cache_metrics(days_back: int = 7) -> dict[str, Any]:
    """
    Get cache metrics for dashboard or API.

    Args:
        days_back: Number of days to analyze

    Returns:
        Dict with cache metrics
    """
    collector = CacheStatsCollector()
    return collector.get_comprehensive_stats(days_back=days_back)


if __name__ == "__main__":
    # CLI for cache statistics
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Get cache statistics")
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "prometheus"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--dimension-breakdown", action="store_true", help="Show per-dimension breakdown"
    )

    args = parser.parse_args()

    collector = CacheStatsCollector()

    if args.format == "prometheus":
        print(collector.export_prometheus_metrics())
    elif args.dimension_breakdown:
        breakdown = collector.get_dimension_breakdown(days_back=args.days)
        print(json.dumps(breakdown, indent=2))
    else:
        stats = collector.get_comprehensive_stats(days_back=args.days)
        print(json.dumps(stats, indent=2))
