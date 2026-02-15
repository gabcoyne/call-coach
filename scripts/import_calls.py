"""
Import calls from Gong API directly (without opportunity sync).

Usage:
    uv run python scripts/import_calls.py --days 30
"""

import argparse
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from psycopg2.extras import RealDictCursor

from db import queries
from db.connection import get_db_connection
from gong.client import GongClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def import_call_with_transcript(client: GongClient, call: Any) -> bool:
    """
    Import a single call with its transcript.

    Args:
        client: Gong API client
        call: GongCall model with basic call metadata (from list_calls)

    Returns:
        True if successful, False otherwise
    """
    gong_call_id = call.id

    # Use single database connection for entire import to avoid transaction isolation issues
    with get_db_connection() as conn:
        try:
            logger.info(f"Fetching full call details and transcript for {gong_call_id}")

            # Get full call details including participants
            # list_calls() doesn't return participants, so we need to fetch them separately
            full_call = client.get_call(gong_call_id)

            # Get transcript
            transcript = client.get_transcript(call_id=gong_call_id, call_metadata=full_call)

            if not transcript or not transcript.monologues:
                logger.warning(f"No transcript found for call {gong_call_id}")
                return False

            # Store call in database using GongCall model attributes
            insert_call_query = """
                INSERT INTO calls (gong_call_id, title, scheduled_at, duration_seconds, metadata, processed_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW())
                ON CONFLICT (gong_call_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    scheduled_at = EXCLUDED.scheduled_at,
                    duration_seconds = EXCLUDED.duration_seconds,
                    metadata = EXCLUDED.metadata,
                    processed_at = NOW()
                RETURNING id
            """

            # Use model_dump with mode='json' to handle datetime serialization
            metadata_json = json.dumps(
                full_call.model_dump(mode="json") if hasattr(full_call, "model_dump") else {}
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    insert_call_query,
                    (
                        gong_call_id,
                        full_call.title or "Unknown Call",
                        full_call.scheduled,
                        full_call.duration,
                        metadata_json,
                    ),
                )
                result = cur.fetchone()

            call_id = result["id"]
            logger.info(f"Stored call {gong_call_id} with ID {call_id}")

            # Store speakers from call participants and build mapping
            speaker_id_map = {}  # Map Gong speaker_id to database speaker UUID
            if not full_call.participants:
                logger.warning(
                    f"Call {gong_call_id} has no participants with speaker IDs, skipping transcripts"
                )
            else:
                insert_speaker_query = """
                    INSERT INTO speakers (call_id, speaker_id, name, email, company_side)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, speaker_id
                """

                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    for speaker in full_call.participants:
                        cur.execute(
                            insert_speaker_query,
                            (
                                call_id,
                                speaker.speaker_id,
                                speaker.name,
                                speaker.email,
                                speaker.is_internal,
                            ),
                        )
                        result = cur.fetchone()
                        # Map Gong speaker_id to database UUID
                        speaker_id_map[speaker.speaker_id] = result["id"]

            # Store transcript from monologues
            # Note: Gong API returns times in milliseconds
            insert_transcript_query = """
                INSERT INTO transcripts (call_id, speaker_id, sequence_number, start_time_ms, text)
                VALUES (%s, %s, %s, %s, %s)
            """

            sequence = 0
            with conn.cursor() as cur:
                for monologue in transcript.monologues:
                    # Look up database speaker UUID from Gong speaker_id
                    db_speaker_id = speaker_id_map.get(monologue.speaker_id)
                    if not db_speaker_id:
                        logger.warning(
                            f"Speaker {monologue.speaker_id} not found in mapping, skipping monologue"
                        )
                        continue

                    for sentence in monologue.sentences:
                        # Store start time in milliseconds
                        start_time_ms = sentence.start
                        cur.execute(
                            insert_transcript_query,
                            (call_id, db_speaker_id, sequence, start_time_ms, sentence.text),
                        )
                        sequence += 1

            logger.info(f"Stored {sequence} transcript entries for call {gong_call_id}")
            conn.commit()  # Explicitly commit the transaction
            return True

        except Exception as e:
            conn.rollback()  # Rollback on error
            logger.error(f"Failed to import call {gong_call_id}: {e}", exc_info=True)
            return False


def import_calls(days: int = 30, limit: int = 10) -> dict:
    """
    Import recent calls from Gong.

    Args:
        days: Number of days back to fetch calls
        limit: Maximum number of calls to import

    Returns:
        Dict with import stats
    """
    logger.info(f"Starting call import for last {days} days (limit: {limit})")

    # Calculate date range
    to_date = datetime.now(UTC)
    from_date = to_date - timedelta(days=days)

    from_date_str = from_date.isoformat().replace("+00:00", "Z")
    to_date_str = to_date.isoformat().replace("+00:00", "Z")

    logger.info(f"Date range: {from_date_str} to {to_date_str}")

    imported_count = 0
    error_count = 0
    skipped_count = 0

    try:
        with GongClient() as client:
            # Fetch calls
            logger.info("Fetching calls from Gong API...")
            calls, cursor = client.list_calls(
                from_date=from_date_str,
                to_date=to_date_str,
            )

            logger.info(f"Found {len(calls)} calls")

            # Process each call (up to limit)
            for i, call in enumerate(calls[:limit]):
                gong_call_id = call.id
                title = call.title or "Unknown"

                logger.info(f"[{i+1}/{min(len(calls), limit)}] Processing: {title}")

                # Check if already imported
                existing_call = queries.get_call_by_gong_id(gong_call_id)
                if existing_call:
                    logger.info(f"Call {gong_call_id} already exists, skipping")
                    skipped_count += 1
                    continue

                # Import call with transcript
                if import_call_with_transcript(client, call):
                    imported_count += 1
                else:
                    error_count += 1

            results = {
                "status": "success",
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": error_count,
                "total_found": len(calls),
            }

            logger.info(
                f"Import complete: {imported_count} imported, {skipped_count} skipped, {error_count} errors"
            )
            return results

    except Exception as e:
        logger.error(f"Call import failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": error_count,
        }


def main():
    parser = argparse.ArgumentParser(description="Import calls from Gong")
    parser.add_argument("--days", type=int, default=30, help="Number of days back to fetch")
    parser.add_argument("--limit", type=int, default=10, help="Maximum calls to import")
    args = parser.parse_args()

    # Run import
    result = main()

    # Print results
    print("\n" + "=" * 80)
    print("CALL IMPORT RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    parser = argparse.ArgumentParser(description="Import calls from Gong")
    parser.add_argument("--days", type=int, default=30, help="Number of days back to fetch")
    parser.add_argument("--limit", type=int, default=10, help="Maximum calls to import")
    args = parser.parse_args()

    result = import_calls(days=args.days, limit=args.limit)

    print("\n" + "=" * 80)
    print("CALL IMPORT RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))
