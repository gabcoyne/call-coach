#!/usr/bin/env python3
"""
Batch analyze all calls with coaching AI.

This script analyzes all calls that don't have coaching sessions yet,
generating insights for all four coaching dimensions:
- discovery
- objections (objection_handling)
- product_knowledge
- engagement

Uses concurrent execution to speed up analysis while respecting API rate limits.
"""
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from uuid import UUID

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analysis.engine import analyze_call
from db import fetch_all, fetch_one
from db.models import CoachingDimension

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "batch_analyze.log"),
    ],
)
logger = logging.getLogger(__name__)


def get_calls_needing_analysis() -> list[dict[str, Any]]:
    """
    Get all calls that don't have coaching sessions yet.

    Returns:
        List of call records with id and metadata
    """
    logger.info("Querying calls without coaching sessions...")

    calls = fetch_all(
        """
        SELECT c.id, c.gong_call_id, c.title, c.scheduled_at,
               c.duration_seconds, c.call_type, c.product
        FROM calls c
        LEFT JOIN coaching_sessions cs ON c.id = cs.call_id
        WHERE cs.id IS NULL
        ORDER BY c.scheduled_at DESC
    """
    )

    logger.info(f"Found {len(calls)} calls needing analysis")
    return calls


def analyze_single_call(call: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze a single call across all dimensions.

    Args:
        call: Call record from database

    Returns:
        Dict with analysis results and metadata
    """
    call_id = UUID(call["id"])
    gong_call_id = call["gong_call_id"]
    title = call["title"] or "Untitled Call"

    start_time = time.time()
    logger.info(f"Starting analysis for call {gong_call_id}: {title}")

    result = {
        "call_id": str(call_id),
        "gong_call_id": gong_call_id,
        "title": title,
        "success": False,
        "dimensions_completed": [],
        "errors": {},
        "duration_seconds": 0,
    }

    # Analyze each dimension
    dimensions = [
        CoachingDimension.DISCOVERY,
        CoachingDimension.OBJECTION_HANDLING,
        CoachingDimension.PRODUCT_KNOWLEDGE,
        CoachingDimension.ENGAGEMENT,
    ]

    for dimension in dimensions:
        try:
            logger.info(f"  Analyzing {dimension.value} for {gong_call_id}...")

            # This will get or create coaching session
            session_result = analyze_call(
                call_id=call_id,
                dimensions=[dimension],
                force_reanalysis=False,  # Use cache if available
            )

            result["dimensions_completed"].append(dimension.value)
            logger.info(f"  ✓ Completed {dimension.value}")

        except Exception as e:
            error_msg = f"Failed to analyze {dimension.value}: {str(e)}"
            logger.error(f"  ✗ {error_msg}", exc_info=True)
            result["errors"][dimension.value] = error_msg

    result["success"] = len(result["dimensions_completed"]) > 0
    result["duration_seconds"] = round(time.time() - start_time, 2)

    return result


def batch_analyze_calls(max_workers: int = 5) -> dict[str, Any]:
    """
    Batch analyze all calls using concurrent execution.

    Args:
        max_workers: Number of concurrent workers (default: 5)

    Returns:
        Summary statistics of the batch run
    """
    logger.info("=" * 80)
    logger.info("Starting batch analysis of calls")
    logger.info("=" * 80)

    # Ensure logs directory exists
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Get calls to analyze
    calls = get_calls_needing_analysis()

    if not calls:
        logger.info("No calls need analysis. Exiting.")
        return {
            "total_calls": 0,
            "successful": 0,
            "failed": 0,
            "total_dimensions": 0,
        }

    logger.info(f"Analyzing {len(calls)} calls with {max_workers} concurrent workers")
    logger.info("")

    # Track results
    results = []
    start_time = time.time()

    # Use ThreadPoolExecutor for concurrent analysis
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_call = {executor.submit(analyze_single_call, call): call for call in calls}

        # Process completed tasks
        completed = 0
        for future in as_completed(future_to_call):
            call = future_to_call[future]
            completed += 1

            try:
                result = future.result()
                results.append(result)

                # Log progress
                dimensions_count = len(result["dimensions_completed"])
                status = "✓" if result["success"] else "✗"
                logger.info(
                    f"[{completed}/{len(calls)}] {status} {result['gong_call_id']}: "
                    f"{dimensions_count}/4 dimensions completed "
                    f"({result['duration_seconds']}s)"
                )

                if result["errors"]:
                    for dim, error in result["errors"].items():
                        logger.warning(f"  - {dim}: {error}")

            except Exception as e:
                logger.error(
                    f"[{completed}/{len(calls)}] ✗ Exception for call {call['gong_call_id']}: {e}",
                    exc_info=True,
                )
                results.append(
                    {
                        "call_id": str(call["id"]),
                        "gong_call_id": call["gong_call_id"],
                        "title": call["title"],
                        "success": False,
                        "dimensions_completed": [],
                        "errors": {"exception": str(e)},
                        "duration_seconds": 0,
                    }
                )

    # Calculate summary statistics
    total_duration = time.time() - start_time
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    total_dimensions = sum(len(r["dimensions_completed"]) for r in results)

    logger.info("")
    logger.info("=" * 80)
    logger.info("Batch analysis complete!")
    logger.info("=" * 80)
    logger.info(f"Total calls processed: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total dimensions analyzed: {total_dimensions}")
    logger.info(f"Total duration: {round(total_duration/60, 2)} minutes")
    logger.info(f"Average per call: {round(total_duration/len(results), 2)} seconds")

    # Verify coaching sessions created
    total_sessions = fetch_one("SELECT COUNT(*) as count FROM coaching_sessions")
    logger.info(f"\nCoaching sessions in database: {total_sessions['count']}")

    calls_with_sessions = fetch_one(
        """
        SELECT COUNT(DISTINCT call_id) as count FROM coaching_sessions
    """
    )
    logger.info(f"Calls with coaching sessions: {calls_with_sessions['count']}")

    return {
        "total_calls": len(results),
        "successful": successful,
        "failed": failed,
        "total_dimensions": total_dimensions,
        "total_duration_seconds": round(total_duration, 2),
        "results": results,
    }


def main():
    """Main entry point for batch analysis."""
    try:
        summary = batch_analyze_calls(max_workers=5)

        # Exit with error code if any calls failed
        if summary["failed"] > 0:
            logger.warning(f"{summary['failed']} calls had errors")
            sys.exit(1)
        else:
            logger.info("All calls analyzed successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\nBatch analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
