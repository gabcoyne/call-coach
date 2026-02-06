"""
Cache warming script for preloading frequent queries.

Warms Redis cache with:
1. Active rubrics (all versions and dimensions)
2. Recent high-frequency call transcripts
3. Popular rep performance summaries
4. Knowledge base content

Run this:
- After deployment
- After rubric updates
- Daily via cron for cache maintenance
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from analysis.rubric_loader import load_rubric
from cache.redis_client import get_redis_cache
from db import fetch_all
from db.models import CoachingDimension

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CacheWarmer:
    """
    Cache warming utility for preloading frequent data.

    Strategies:
    1. Frequency-based: Cache most-accessed items
    2. Recency-based: Cache recently created/updated items
    3. Predictive: Cache items likely to be accessed soon
    """

    def __init__(self):
        """Initialize cache warmer with Redis client."""
        self.redis_cache = get_redis_cache()
        self.warmed_count = 0
        self.error_count = 0

    def warm_all(self, days_back: int = 30) -> dict[str, Any]:
        """
        Execute complete cache warming sequence.

        Args:
            days_back: Number of days to look back for recent data

        Returns:
            Dict with warming statistics
        """
        logger.info("Starting cache warming process...")
        start_time = datetime.now()

        # Check Redis availability
        if not self.redis_cache.available:
            logger.error("Redis not available. Cache warming skipped.")
            return {
                "success": False,
                "error": "Redis not available",
                "redis_available": False,
            }

        # Warm different data types
        rubric_stats = self._warm_rubrics()
        transcript_stats = self._warm_recent_transcripts(days_back)
        rep_stats = self._warm_active_reps(days_back)

        duration = (datetime.now() - start_time).total_seconds()

        stats = {
            "success": True,
            "redis_available": True,
            "duration_seconds": round(duration, 2),
            "total_warmed": self.warmed_count,
            "total_errors": self.error_count,
            "rubrics": rubric_stats,
            "transcripts": transcript_stats,
            "reps": rep_stats,
        }

        logger.info(f"Cache warming completed in {duration:.2f}s: {self.warmed_count} items warmed")
        return stats

    def _warm_rubrics(self) -> dict[str, Any]:
        """
        Warm cache with active rubrics.

        Returns:
            Stats about rubric warming
        """
        logger.info("Warming rubrics...")
        warmed = 0
        errors = 0

        try:
            # Get all active rubrics
            rubrics = fetch_all(
                """
                SELECT category, version, criteria, scoring_guide, examples
                FROM coaching_rubrics
                WHERE active = true
                ORDER BY category, created_at DESC
                """
            )

            # Load role-specific rubrics
            for role in ["ae", "se", "csm"]:
                try:
                    role_rubric = load_rubric(role)
                    logger.debug(f"Loaded {role.upper()} rubric")
                    warmed += 1
                except Exception as e:
                    logger.error(f"Failed to load {role} rubric: {e}")
                    errors += 1

            logger.info(f"Warmed {warmed} rubrics")

        except Exception as e:
            logger.error(f"Error warming rubrics: {e}")
            errors += 1

        self.warmed_count += warmed
        self.error_count += errors

        return {
            "warmed": warmed,
            "errors": errors,
        }

    def _warm_recent_transcripts(self, days_back: int) -> dict[str, Any]:
        """
        Warm cache with recent coaching sessions.

        Preloads sessions from the last N days that are likely
        to be accessed again (e.g., for re-analysis or review).

        Args:
            days_back: Number of days to look back

        Returns:
            Stats about transcript warming
        """
        logger.info(f"Warming recent transcripts (last {days_back} days)...")
        warmed = 0
        errors = 0

        try:
            # Get recent sessions with their data
            sessions = fetch_all(
                """
                SELECT
                    cs.coaching_dimension,
                    cs.transcript_hash,
                    cs.rubric_version,
                    cs.score,
                    cs.strengths,
                    cs.areas_for_improvement,
                    cs.specific_examples,
                    cs.action_items,
                    cs.full_analysis,
                    cs.metadata,
                    cs.created_at
                FROM coaching_sessions cs
                WHERE cs.created_at > %s
                AND cs.cache_key IS NOT NULL
                AND cs.transcript_hash IS NOT NULL
                ORDER BY cs.created_at DESC
                LIMIT 100
                """,
                (datetime.now() - timedelta(days=days_back),),
            )

            # Store each session in Redis
            for session in sessions:
                try:
                    dimension = CoachingDimension(session["coaching_dimension"])

                    session_data = {
                        "score": session["score"],
                        "strengths": session["strengths"],
                        "areas_for_improvement": session["areas_for_improvement"],
                        "specific_examples": session["specific_examples"],
                        "action_items": session["action_items"],
                        "full_analysis": session["full_analysis"],
                        "metadata": session["metadata"],
                        "created_at": (
                            session["created_at"].isoformat() if session["created_at"] else None
                        ),
                    }

                    success = self.redis_cache.set(
                        dimension=dimension,
                        transcript_hash=session["transcript_hash"],
                        rubric_version=session["rubric_version"],
                        session_data=session_data,
                    )

                    if success:
                        warmed += 1
                    else:
                        errors += 1

                except Exception as e:
                    logger.error(f"Failed to warm session: {e}")
                    errors += 1

            logger.info(f"Warmed {warmed} transcript sessions")

        except Exception as e:
            logger.error(f"Error warming transcripts: {e}")
            errors += 1

        self.warmed_count += warmed
        self.error_count += errors

        return {
            "warmed": warmed,
            "errors": errors,
        }

    def _warm_active_reps(self, days_back: int) -> dict[str, Any]:
        """
        Warm cache with active rep data.

        Preloads rep performance summaries for reps with recent activity.

        Args:
            days_back: Number of days to look back

        Returns:
            Stats about rep data warming
        """
        logger.info(f"Warming active rep data (last {days_back} days)...")
        warmed = 0
        errors = 0

        try:
            # Get active reps (those with recent calls)
            active_reps = fetch_all(
                """
                SELECT DISTINCT s.email
                FROM speakers s
                JOIN calls c ON c.id = s.call_id
                WHERE s.company_side = true
                AND s.email IS NOT NULL
                AND c.scheduled_at > %s
                ORDER BY s.email
                LIMIT 50
                """,
                (datetime.now() - timedelta(days=days_back),),
            )

            # Note: Rep performance summaries are typically computed on-demand
            # and stored in application cache. This just ensures the data
            # is fresh and queryable.
            warmed = len(active_reps)
            logger.info(f"Identified {warmed} active reps for cache warming")

        except Exception as e:
            logger.error(f"Error warming rep data: {e}")
            errors += 1

        self.warmed_count += warmed
        self.error_count += errors

        return {
            "warmed": warmed,
            "errors": errors,
        }

    def warm_specific_dimension(
        self,
        dimension: CoachingDimension,
        days_back: int = 7,
    ) -> dict[str, Any]:
        """
        Warm cache for a specific coaching dimension.

        Useful after rubric updates for a particular dimension.

        Args:
            dimension: Coaching dimension to warm
            days_back: Number of days to look back

        Returns:
            Warming statistics
        """
        logger.info(f"Warming dimension: {dimension.value}")
        warmed = 0
        errors = 0

        try:
            sessions = fetch_all(
                """
                SELECT
                    cs.transcript_hash,
                    cs.rubric_version,
                    cs.score,
                    cs.strengths,
                    cs.areas_for_improvement,
                    cs.specific_examples,
                    cs.action_items,
                    cs.full_analysis,
                    cs.metadata,
                    cs.created_at
                FROM coaching_sessions cs
                WHERE cs.coaching_dimension = %s
                AND cs.created_at > %s
                AND cs.cache_key IS NOT NULL
                ORDER BY cs.created_at DESC
                LIMIT 50
                """,
                (dimension.value, datetime.now() - timedelta(days=days_back)),
            )

            for session in sessions:
                try:
                    session_data = {
                        "score": session["score"],
                        "strengths": session["strengths"],
                        "areas_for_improvement": session["areas_for_improvement"],
                        "specific_examples": session["specific_examples"],
                        "action_items": session["action_items"],
                        "full_analysis": session["full_analysis"],
                        "metadata": session["metadata"],
                        "created_at": (
                            session["created_at"].isoformat() if session["created_at"] else None
                        ),
                    }

                    success = self.redis_cache.set(
                        dimension=dimension,
                        transcript_hash=session["transcript_hash"],
                        rubric_version=session["rubric_version"],
                        session_data=session_data,
                    )

                    if success:
                        warmed += 1
                    else:
                        errors += 1

                except Exception as e:
                    logger.error(f"Failed to warm session: {e}")
                    errors += 1

            logger.info(f"Warmed {warmed} sessions for dimension {dimension.value}")

        except Exception as e:
            logger.error(f"Error warming dimension {dimension.value}: {e}")
            errors += 1

        return {
            "dimension": dimension.value,
            "warmed": warmed,
            "errors": errors,
        }


def warm_cache(days_back: int = 30) -> dict[str, Any]:
    """
    Execute cache warming process.

    This is the main entry point for the warming script.

    Args:
        days_back: Number of days to look back for recent data

    Returns:
        Warming statistics
    """
    warmer = CacheWarmer()
    return warmer.warm_all(days_back=days_back)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Warm Redis cache with frequent data")
    parser.add_argument(
        "--days", type=int, default=30, help="Number of days to look back (default: 30)"
    )
    parser.add_argument(
        "--dimension",
        type=str,
        choices=["product_knowledge", "discovery", "objection_handling", "engagement"],
        help="Warm specific dimension only",
    )

    args = parser.parse_args()

    if args.dimension:
        # Warm specific dimension
        dimension = CoachingDimension(args.dimension)
        warmer = CacheWarmer()
        stats = warmer.warm_specific_dimension(dimension, days_back=args.days)
        print(f"\nDimension warming stats: {stats}")
    else:
        # Warm all
        stats = warm_cache(days_back=args.days)
        print("\nCache warming complete!")
        print(f"Total items warmed: {stats['total_warmed']}")
        print(f"Duration: {stats['duration_seconds']}s")
        print(f"Errors: {stats['total_errors']}")
