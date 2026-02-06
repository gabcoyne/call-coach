#!/usr/bin/env python3
"""
Load transcripts for all calls from Gong API.

This script fetches transcripts and speaker data for all calls that don't have
transcripts yet. Must be run before batch_analyze_calls.py.
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

from db import fetch_all, fetch_one
from flows.process_new_call import (
    fetch_call_from_gong,
    fetch_transcript_from_gong,
    store_speakers,
    store_transcript,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "load_transcripts.log"),
    ],
)
logger = logging.getLogger(__name__)


def get_calls_needing_transcripts() -> list[dict[str, Any]]:
    """
    Get all calls that don't have transcripts yet.

    Returns:
        List of call records
    """
    logger.info("Querying calls without transcripts...")

    calls = fetch_all(
        """
        SELECT c.id, c.gong_call_id, c.title, c.scheduled_at
        FROM calls c
        LEFT JOIN transcripts t ON c.id = t.call_id
        WHERE t.id IS NULL
        GROUP BY c.id, c.gong_call_id, c.title, c.scheduled_at
        ORDER BY c.scheduled_at DESC
    """
    )

    logger.info(f"Found {len(calls)} calls needing transcripts")
    return calls


def load_transcript_for_call(call: dict[str, Any]) -> dict[str, Any]:
    """
    Load transcript for a single call from Gong.

    Args:
        call: Call record from database

    Returns:
        Dict with load results and metadata
    """
    call_id = UUID(call["id"])
    gong_call_id = call["gong_call_id"]
    title = call["title"] or "Untitled Call"

    start_time = time.time()
    logger.info(f"Loading transcript for {gong_call_id}: {title}")

    result = {
        "call_id": str(call_id),
        "gong_call_id": gong_call_id,
        "title": title,
        "success": False,
        "transcript_sentences": 0,
        "speakers": 0,
        "error": None,
        "duration_seconds": 0,
    }

    try:
        # Fetch call metadata from Gong
        logger.info("  Fetching call metadata from Gong...")
        gong_call_data = fetch_call_from_gong(gong_call_id)

        # Fetch transcript from Gong
        logger.info("  Fetching transcript from Gong...")
        transcript_data = fetch_transcript_from_gong(gong_call_id, gong_call_data)

        # Store speakers
        logger.info("  Storing speakers...")
        participants = gong_call_data.get("participants", [])

        # If no participants from Gong API, create a default rep speaker for analysis
        if not participants:
            logger.warning("  No participants from Gong API - creating default rep speaker")
            from uuid import uuid4

            from db import execute_query

            default_speaker_id = uuid4()
            execute_query(
                """
                INSERT INTO speakers (
                    id, call_id, name, email, role, company_side,
                    talk_time_seconds, talk_time_percentage
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(default_speaker_id),
                    str(call_id),
                    "Unknown Rep",
                    None,
                    "ae",  # Default to AE role
                    True,  # company_side = true
                    None,
                    None,
                ),
            )
            speaker_mapping = {}
            result["speakers"] = 1
        else:
            speaker_mapping = store_speakers(call_id, participants)
            result["speakers"] = len(speaker_mapping)

        # Store transcript
        logger.info("  Storing transcript...")
        transcript_hash = store_transcript(call_id, transcript_data, speaker_mapping)

        # Count transcript sentences stored
        count = fetch_one(
            "SELECT COUNT(*) as count FROM transcripts WHERE call_id = %s",
            (str(call_id),),
        )
        result["transcript_sentences"] = count["count"]

        # Mark call as processed
        execute_query(
            "UPDATE calls SET processed_at = NOW() WHERE id = %s",
            (str(call_id),),
        )

        result["success"] = True
        result["duration_seconds"] = round(time.time() - start_time, 2)

        logger.info(
            f"  ✓ Loaded {result['transcript_sentences']} sentences, "
            f"{result['speakers']} speakers ({result['duration_seconds']}s)"
        )

    except Exception as e:
        error_msg = f"Failed to load transcript: {str(e)}"
        logger.error(f"  ✗ {error_msg}", exc_info=True)
        result["error"] = error_msg
        result["duration_seconds"] = round(time.time() - start_time, 2)

    return result


def batch_load_transcripts(max_workers: int = 3) -> dict[str, Any]:
    """
    Batch load transcripts for all calls using concurrent execution.

    Args:
        max_workers: Number of concurrent workers (default: 3 for Gong API rate limits)

    Returns:
        Summary statistics of the batch load
    """
    logger.info("=" * 80)
    logger.info("Starting batch transcript loading from Gong")
    logger.info("=" * 80)

    # Ensure logs directory exists
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Get calls to load
    calls = get_calls_needing_transcripts()

    if not calls:
        logger.info("No calls need transcripts. Exiting.")
        return {
            "total_calls": 0,
            "successful": 0,
            "failed": 0,
            "total_sentences": 0,
        }

    logger.info(f"Loading transcripts for {len(calls)} calls with {max_workers} concurrent workers")
    logger.info("Note: Using lower concurrency to respect Gong API rate limits")
    logger.info("")

    # Track results
    results = []
    start_time = time.time()

    # Use ThreadPoolExecutor for concurrent loading
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_call = {executor.submit(load_transcript_for_call, call): call for call in calls}

        # Process completed tasks
        completed = 0
        for future in as_completed(future_to_call):
            call = future_to_call[future]
            completed += 1

            try:
                result = future.result()
                results.append(result)

                # Log progress
                status = "✓" if result["success"] else "✗"
                logger.info(
                    f"[{completed}/{len(calls)}] {status} {result['gong_call_id']}: "
                    f"{result['transcript_sentences']} sentences, "
                    f"{result['speakers']} speakers "
                    f"({result['duration_seconds']}s)"
                )

                if result["error"]:
                    logger.warning(f"  Error: {result['error']}")

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
                        "transcript_sentences": 0,
                        "speakers": 0,
                        "error": str(e),
                        "duration_seconds": 0,
                    }
                )

    # Calculate summary statistics
    total_duration = time.time() - start_time
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    total_sentences = sum(r["transcript_sentences"] for r in results)
    total_speakers = sum(r["speakers"] for r in results)

    logger.info("")
    logger.info("=" * 80)
    logger.info("Batch transcript loading complete!")
    logger.info("=" * 80)
    logger.info(f"Total calls processed: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total transcript sentences: {total_sentences:,}")
    logger.info(f"Total speakers: {total_speakers}")
    logger.info(f"Total duration: {round(total_duration/60, 2)} minutes")
    logger.info(f"Average per call: {round(total_duration/len(results), 2)} seconds")

    # Verify transcripts in database
    transcript_count = fetch_one("SELECT COUNT(*) as count FROM transcripts")
    logger.info(f"\nTranscript sentences in database: {transcript_count['count']:,}")

    calls_with_transcripts = fetch_one(
        """
        SELECT COUNT(DISTINCT call_id) as count FROM transcripts
    """
    )
    logger.info(f"Calls with transcripts: {calls_with_transcripts['count']}")

    return {
        "total_calls": len(results),
        "successful": successful,
        "failed": failed,
        "total_sentences": total_sentences,
        "total_speakers": total_speakers,
        "total_duration_seconds": round(total_duration, 2),
        "results": results,
    }


def main():
    """Main entry point for batch transcript loading."""
    try:
        summary = batch_load_transcripts(max_workers=3)

        # Exit with error code if any calls failed
        if summary["failed"] > 0:
            logger.warning(f"{summary['failed']} calls had errors")
            sys.exit(1)
        else:
            logger.info("All transcripts loaded successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\nBatch transcript loading interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Batch transcript loading failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
