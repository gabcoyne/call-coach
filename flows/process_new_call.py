"""
Prefect flow for processing new calls from Gong webhooks.
Handles transcript fetching, chunking, and basic analysis.
"""
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from analysis.chunking import chunk_transcript, count_tokens
from analysis.cache import generate_transcript_hash
from config import settings
from db import execute_query, fetch_one
from db.models import (
    Call,
    Speaker,
    Transcript,
    AnalysisRun,
    AnalysisRunStatus,
    WebhookEventStatus,
    Role,
    CallType,
    Product,
)
from gong.client import GongClient
from gong.webhook import WebhookHandler

logger = logging.getLogger(__name__)


@task(name="fetch_call_from_gong", retries=3, retry_delay_seconds=5)
def fetch_call_from_gong(call_id: str) -> dict[str, Any]:
    """
    Fetch call metadata from Gong API.

    Args:
        call_id: Gong call ID

    Returns:
        Call metadata dict
    """
    logger.info(f"Fetching call {call_id} from Gong API")

    with GongClient() as client:
        gong_call = client.get_call(call_id)

    return gong_call.model_dump()


@task(name="fetch_transcript_from_gong", retries=3, retry_delay_seconds=5)
def fetch_transcript_from_gong(call_id: str, call_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Fetch transcript from Gong API.

    Args:
        call_id: Gong call ID
        call_metadata: Optional call metadata to optimize date range query

    Returns:
        Transcript data dict
    """
    logger.info(f"Fetching transcript for call {call_id} from Gong API")

    with GongClient() as client:
        # Convert call_metadata dict back to GongCall if provided
        from gong.types import GongCall
        call_obj = GongCall(**call_metadata) if call_metadata else None

        transcript = client.get_transcript(call_id, call_metadata=call_obj)

    return transcript.model_dump()


@task(name="store_call_metadata")
def store_call_metadata(gong_call: dict[str, Any]) -> UUID:
    """
    Store call metadata in database.

    Args:
        gong_call: Gong call data

    Returns:
        Database call UUID
    """
    logger.info(f"Storing call metadata: {gong_call.get('id')}")

    # Check if call already exists
    existing = fetch_one(
        "SELECT id FROM calls WHERE gong_call_id = %s",
        (gong_call["id"],),
    )

    if existing:
        logger.info(f"Call {gong_call['id']} already exists in database")
        return UUID(existing["id"])

    # Infer call type and product from title/metadata
    title = gong_call.get("title", "").lower()
    call_type = None
    product = None

    if "discovery" in title:
        call_type = CallType.DISCOVERY.value
    elif "demo" in title:
        call_type = CallType.DEMO.value
    elif "technical" in title:
        call_type = CallType.TECHNICAL_DEEP_DIVE.value

    if "horizon" in title:
        product = Product.HORIZON.value
    elif "prefect" in title:
        product = Product.PREFECT.value

    # Insert call
    call_id = uuid4()
    execute_query(
        """
        INSERT INTO calls (
            id, gong_call_id, title, scheduled_at, duration_seconds,
            call_type, product, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            str(call_id),
            gong_call["id"],
            gong_call.get("title"),
            gong_call.get("scheduled"),
            gong_call.get("duration"),
            call_type,
            product,
            gong_call,
        ),
    )

    logger.info(f"Stored call {call_id} in database")
    return call_id


@task(name="store_speakers")
def store_speakers(call_id: UUID, participants: list[dict[str, Any]]) -> dict[str, UUID]:
    """
    Store call participants in database.

    Args:
        call_id: Database call UUID
        participants: List of participant data from Gong

    Returns:
        Dict mapping speaker_id to database UUID
    """
    logger.info(f"Storing {len(participants)} speakers for call {call_id}")

    speaker_mapping = {}

    for participant in participants:
        speaker_id = uuid4()
        gong_speaker_id = participant["speaker_id"]

        # Infer role from title or is_internal flag
        role = None
        if participant.get("is_internal"):
            title = (participant.get("title") or "").lower()
            if "engineer" in title or "se" in title:
                role = Role.SE.value
            elif "account executive" in title or "ae" in title:
                role = Role.AE.value
            elif "csm" in title or "success" in title:
                role = Role.CSM.value
        else:
            role = Role.PROSPECT.value  # Default for external participants

        execute_query(
            """
            INSERT INTO speakers (
                id, call_id, name, email, role, company_side,
                talk_time_seconds, talk_time_percentage
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(speaker_id),
                str(call_id),
                participant["name"],
                participant.get("email"),
                role,
                participant["is_internal"],
                participant["talk_time_seconds"],
                None,  # Calculate percentage later
            ),
        )

        speaker_mapping[gong_speaker_id] = speaker_id

    logger.info(f"Stored {len(speaker_mapping)} speakers")
    return speaker_mapping


@task(name="store_transcript")
def store_transcript(
    call_id: UUID,
    transcript_data: dict[str, Any],
    speaker_mapping: dict[str, UUID],
) -> str:
    """
    Store transcript in database with chunking support.

    The Gong API returns transcripts as monologues (speaker + topic + sentences).
    We flatten this to individual sentences for storage, preserving topic metadata.

    Args:
        call_id: Database call UUID
        transcript_data: Transcript from Gong (contains "monologues" list)
        speaker_mapping: Mapping of Gong speaker IDs to database UUIDs

    Returns:
        SHA256 hash of full transcript
    """
    logger.info(f"Storing transcript for call {call_id}")

    monologues = transcript_data["monologues"]

    # Flatten monologues to sentences for storage
    # Each sentence gets stored as a transcript row with topic metadata
    all_sentences = []
    for monologue in monologues:
        speaker_id = monologue["speaker_id"]
        topic = monologue.get("topic")

        for sentence in monologue["sentences"]:
            all_sentences.append({
                "speaker_id": speaker_id,
                "topic": topic,
                "start_ms": sentence["start"],  # milliseconds from call start
                "end_ms": sentence["end"],
                "text": sentence["text"],
            })

    # Build full transcript for hashing
    full_text = " ".join([s["text"] for s in all_sentences])
    transcript_hash = generate_transcript_hash(full_text)

    # Count tokens to determine if chunking is needed
    total_tokens = count_tokens(full_text)
    logger.info(f"Transcript has {total_tokens:,} tokens ({len(all_sentences)} sentences)")

    # Chunk if needed
    needs_chunking = total_tokens > settings.max_chunk_size_tokens
    if needs_chunking:
        logger.info(f"Transcript exceeds max size, will chunk during analysis")

    # Store individual sentences
    # Note: timestamp_seconds field stores the START time in milliseconds (schema needs updating)
    for idx, sentence in enumerate(all_sentences):
        speaker_id = speaker_mapping.get(sentence["speaker_id"])

        # Store topic in topics array field (JSONB or VARCHAR[])
        # Store both start and end times in metadata until schema updated
        execute_query(
            """
            INSERT INTO transcripts (
                call_id, speaker_id, sequence_number, timestamp_seconds,
                text, topics, chunk_metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(call_id),
                str(speaker_id) if speaker_id else None,
                idx,
                sentence["start_ms"],  # Note: Field name is misleading, stores milliseconds
                sentence["text"],
                [sentence["topic"]] if sentence["topic"] else [],
                {
                    "start_ms": sentence["start_ms"],
                    "end_ms": sentence["end_ms"],
                    "duration_ms": sentence["end_ms"] - sentence["start_ms"],
                },
            ),
        )

    logger.info(f"Stored {len(all_sentences)} transcript sentences from {len(monologues)} monologues")
    return transcript_hash


@task(name="create_analysis_run")
def create_analysis_run(
    call_id: UUID,
    webhook_event_id: UUID | None = None,
) -> UUID:
    """
    Create analysis run record for tracking.

    Args:
        call_id: Call UUID
        webhook_event_id: Webhook event UUID if triggered by webhook

    Returns:
        Analysis run UUID
    """
    run_id = uuid4()

    execute_query(
        """
        INSERT INTO analysis_runs (
            id, call_id, webhook_event_id, status, dimensions_analyzed
        ) VALUES (%s, %s, %s, %s, %s)
        """,
        (
            str(run_id),
            str(call_id),
            str(webhook_event_id) if webhook_event_id else None,
            AnalysisRunStatus.RUNNING.value,
            [],  # Will be updated as dimensions are analyzed
        ),
    )

    logger.info(f"Created analysis run {run_id}")
    return run_id


@task(name="update_analysis_run")
def update_analysis_run(
    run_id: UUID,
    status: AnalysisRunStatus,
    error_message: str | None = None,
) -> None:
    """
    Update analysis run status.

    Args:
        run_id: Analysis run UUID
        status: New status
        error_message: Optional error message
    """
    execute_query(
        """
        UPDATE analysis_runs
        SET status = %s,
            error_message = %s,
            completed_at = CASE WHEN %s IN ('completed', 'failed') THEN NOW() ELSE completed_at END
        WHERE id = %s
        """,
        (status.value, error_message, status.value, str(run_id)),
    )

    logger.info(f"Updated analysis run {run_id} to status {status.value}")


@flow(
    name="process_new_call",
    description="Process new call from Gong webhook",
    task_runner=ConcurrentTaskRunner(),
    retries=1,
    retry_delay_seconds=30,
)
def process_new_call_flow(
    gong_call_id: str,
    webhook_event_id: UUID | None = None,
) -> dict[str, Any]:
    """
    Main flow for processing a new call from Gong.

    Steps:
    1. Update webhook status to 'processing'
    2. Fetch call metadata from Gong
    3. Fetch transcript from Gong
    4. Store call, speakers, and transcript in database
    5. Calculate transcript hash for caching
    6. Create analysis run record
    7. Mark call as processed
    8. Update webhook status to 'completed'

    Args:
        gong_call_id: Gong call ID
        webhook_event_id: Optional webhook event UUID

    Returns:
        Dict with processing results
    """
    logger.info(f"Starting process_new_call flow for {gong_call_id}")

    analysis_run_id = None

    try:
        # Update webhook status if triggered by webhook
        if webhook_event_id:
            WebhookHandler.update_webhook_status(
                gong_webhook_id=str(webhook_event_id),
                status=WebhookEventStatus.PROCESSING,
            )

        # Fetch call metadata first (needed for efficient transcript fetch)
        gong_call = fetch_call_from_gong(gong_call_id)

        # Fetch transcript with call metadata for date range optimization
        transcript_data = fetch_transcript_from_gong(gong_call_id, gong_call)

        # Store in database
        call_id = store_call_metadata(gong_call)
        speaker_mapping = store_speakers(call_id, gong_call.get("participants", []))
        transcript_hash = store_transcript(call_id, transcript_data, speaker_mapping)

        # Create analysis run
        analysis_run_id = create_analysis_run(call_id, webhook_event_id)

        # Mark call as processed
        execute_query(
            "UPDATE calls SET processed_at = NOW() WHERE id = %s",
            (str(call_id),),
        )

        # Update analysis run to completed
        update_analysis_run(analysis_run_id, AnalysisRunStatus.COMPLETED)

        # Update webhook status
        if webhook_event_id:
            WebhookHandler.update_webhook_status(
                gong_webhook_id=str(webhook_event_id),
                status=WebhookEventStatus.COMPLETED,
            )

        logger.info(f"Successfully processed call {gong_call_id} -> {call_id}")

        return {
            "success": True,
            "gong_call_id": gong_call_id,
            "call_id": str(call_id),
            "analysis_run_id": str(analysis_run_id),
            "transcript_hash": transcript_hash,
        }

    except Exception as e:
        logger.error(f"Failed to process call {gong_call_id}: {e}", exc_info=True)

        # Update analysis run to failed
        if analysis_run_id:
            update_analysis_run(
                analysis_run_id,
                AnalysisRunStatus.FAILED,
                error_message=str(e),
            )

        # Update webhook status to failed
        if webhook_event_id:
            WebhookHandler.update_webhook_status(
                gong_webhook_id=str(webhook_event_id),
                status=WebhookEventStatus.FAILED,
                error_message=str(e),
            )

        raise
