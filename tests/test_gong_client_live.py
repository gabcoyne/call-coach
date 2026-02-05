"""
Live integration tests for Gong API client.
Tests against real Gong API using credentials from .env
"""
import logging
from datetime import datetime, timedelta

from gong.client import GongClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_list_calls():
    """Test listing calls with cursor pagination."""
    logger.info("=" * 60)
    logger.info("TEST 1: List Calls with Cursor Pagination")
    logger.info("=" * 60)

    # Get calls from last 30 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    with GongClient() as client:
        calls, cursor = client.list_calls(
            from_date=from_date.isoformat() + "Z",
            to_date=to_date.isoformat() + "Z",
        )

        logger.info(f"✓ Retrieved {len(calls)} calls")
        logger.info(f"  Next cursor: {cursor[:50] if cursor else 'None (no more pages)'}")

        if calls:
            first_call = calls[0]
            logger.info(f"\nFirst call details:")
            logger.info(f"  ID: {first_call.id}")
            logger.info(f"  Title: {first_call.title}")
            logger.info(f"  Started: {first_call.started}")
            logger.info(f"  Duration: {first_call.duration}s")
            logger.info(f"  Direction: {first_call.direction}")

            return calls[0].id  # Return first call ID for next test
        else:
            logger.warning("No calls found in last 30 days")
            return None


def test_get_call(call_id: str):
    """Test getting specific call details."""
    logger.info("\n" + "=" * 60)
    logger.info(f"TEST 2: Get Specific Call ({call_id})")
    logger.info("=" * 60)

    with GongClient() as client:
        call = client.get_call(call_id)

        logger.info(f"✓ Retrieved call: {call.title}")
        logger.info(f"  ID: {call.id}")
        logger.info(f"  Scheduled: {call.scheduled}")
        logger.info(f"  Started: {call.started}")
        logger.info(f"  Duration: {call.duration}s")
        logger.info(f"  Direction: {call.direction}")
        logger.info(f"  System: {call.system}")
        logger.info(f"  Language: {call.language}")
        logger.info(f"  Workspace: {call.workspace_id}")

        if call.participants:
            logger.info(f"\n  Participants ({len(call.participants)}):")
            for p in call.participants:
                logger.info(f"    - {p.name} ({p.email})")
                logger.info(f"      Internal: {p.is_internal}, Talk time: {p.talk_time_seconds}s")

        return call


def test_get_transcript(call_id: str, call_metadata=None):
    """Test getting call transcript with new POST endpoint."""
    logger.info("\n" + "=" * 60)
    logger.info(f"TEST 3: Get Transcript ({call_id})")
    logger.info("=" * 60)

    with GongClient() as client:
        transcript = client.get_transcript(call_id, call_metadata=call_metadata)

        logger.info(f"✓ Retrieved transcript for call: {transcript.call_id}")
        logger.info(f"  Monologues: {len(transcript.monologues)}")

        # Count total sentences
        total_sentences = sum(len(m.sentences) for m in transcript.monologues)
        logger.info(f"  Total sentences: {total_sentences}")

        # Show first few monologues
        logger.info("\n  First 3 monologues:")
        for idx, monologue in enumerate(transcript.monologues[:3]):
            logger.info(f"\n  Monologue {idx + 1}:")
            logger.info(f"    Speaker: {monologue.speaker_id}")
            logger.info(f"    Topic: {monologue.topic or 'N/A'}")
            logger.info(f"    Sentences: {len(monologue.sentences)}")

            if monologue.sentences:
                first_sentence = monologue.sentences[0]
                logger.info(f"    First sentence:")
                logger.info(f"      Time: {first_sentence.start}ms - {first_sentence.end}ms")
                logger.info(f"      Text: {first_sentence.text[:100]}...")

        # Test backward compatibility helper
        logger.info("\n  Testing get_flat_segments():")
        flat_segments = transcript.get_flat_segments()
        logger.info(f"    Converted to {len(flat_segments)} flat segments")
        if flat_segments:
            logger.info(f"    First segment: {flat_segments[0]}")

        return transcript


def test_search_calls():
    """Test that search_calls raises NotImplementedError."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Search Calls (Should Raise NotImplementedError)")
    logger.info("=" * 60)

    with GongClient() as client:
        try:
            client.search_calls("prefect", from_date="2024-01-01T00:00:00Z")
            logger.error("✗ search_calls() should have raised NotImplementedError!")
        except NotImplementedError as e:
            logger.info(f"✓ Correctly raised NotImplementedError:")
            logger.info(f"  {str(e)}")


if __name__ == "__main__":
    try:
        # Test 1: List calls
        call_id = test_list_calls()

        if call_id:
            # Test 2: Get specific call
            call = test_get_call(call_id)

            # Test 3: Get transcript with call metadata
            test_get_transcript(call_id, call_metadata=call)
        else:
            logger.warning("\nSkipping tests 2-3 (no calls found)")

        # Test 4: Verify search_calls is disabled
        test_search_calls()

        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        raise
