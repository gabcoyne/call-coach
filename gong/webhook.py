"""
Webhook handler for Gong call completed events.
Implements HMAC-SHA256 signature verification for security.
"""
import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import ValidationError

from config import settings
from db import execute_query, fetch_one
from db.models import WebhookEvent, WebhookEventStatus
from .types import GongWebhookPayload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Gong webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request body bytes
        signature: Signature from X-Gong-Signature header
        secret: Webhook secret from Gong settings

    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


class WebhookHandler:
    """Handles webhook events from Gong."""

    @staticmethod
    def store_webhook_event(
        gong_webhook_id: str,
        event_type: str,
        payload: dict[str, Any],
        signature_valid: bool,
    ) -> WebhookEvent:
        """
        Store webhook event in database with idempotency check.

        Args:
            gong_webhook_id: Unique webhook ID from Gong
            event_type: Event type (e.g., "call.completed")
            payload: Webhook payload
            signature_valid: Whether signature verification passed

        Returns:
            WebhookEvent object

        Raises:
            Exception: If database operation fails
        """
        # Check for duplicate (idempotency)
        existing = fetch_one(
            "SELECT * FROM webhook_events WHERE gong_webhook_id = %s",
            (gong_webhook_id,),
        )

        if existing:
            logger.info(f"Webhook {gong_webhook_id} already processed (idempotency)")
            return WebhookEvent(**existing)

        # Insert new event
        execute_query(
            """
            INSERT INTO webhook_events (
                gong_webhook_id, event_type, payload, signature_valid, status
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                gong_webhook_id,
                event_type,
                payload,
                signature_valid,
                WebhookEventStatus.RECEIVED.value,
            ),
        )

        # Fetch inserted event
        event = fetch_one(
            "SELECT * FROM webhook_events WHERE gong_webhook_id = %s",
            (gong_webhook_id,),
        )

        logger.info(f"Stored webhook event {gong_webhook_id}: {event_type}")
        return WebhookEvent(**event)

    @staticmethod
    def update_webhook_status(
        gong_webhook_id: str,
        status: WebhookEventStatus,
        error_message: str | None = None,
    ) -> None:
        """
        Update webhook event status.

        Args:
            gong_webhook_id: Webhook ID
            status: New status
            error_message: Optional error message if failed
        """
        execute_query(
            """
            UPDATE webhook_events
            SET status = %s,
                error_message = %s,
                processed_at = CASE WHEN %s IN ('completed', 'failed') THEN NOW() ELSE processed_at END
            WHERE gong_webhook_id = %s
            """,
            (status.value, error_message, status.value, gong_webhook_id),
        )

        logger.info(f"Updated webhook {gong_webhook_id} status to {status.value}")


@router.post("/gong", status_code=status.HTTP_200_OK)
async def receive_gong_webhook(request: Request) -> dict[str, str]:
    """
    Receive and validate Gong webhooks.
    Returns 200 OK immediately after validation and storage.
    Actual processing happens asynchronously via Prefect flow.

    Expected headers:
    - X-Gong-Signature: HMAC-SHA256 signature
    - X-Gong-Webhook-Id: Unique webhook ID for idempotency

    Returns:
        Success message
    """
    # Get raw body for signature verification
    body = await request.body()

    # Get headers
    signature = request.headers.get("X-Gong-Signature", "")
    webhook_id = request.headers.get("X-Gong-Webhook-Id", "")

    if not webhook_id:
        logger.error("Missing X-Gong-Webhook-Id header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing webhook ID",
        )

    # Verify signature
    signature_valid = verify_webhook_signature(
        payload=body,
        signature=signature,
        secret=settings.gong_webhook_secret,
    )

    if not signature_valid:
        logger.error(f"Invalid webhook signature for {webhook_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # Parse payload
    try:
        payload = await request.json()
        webhook_payload = GongWebhookPayload(**payload)
    except (ValidationError, ValueError) as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload: {e}",
        )

    # Store webhook event (idempotent)
    try:
        webhook_event = WebhookHandler.store_webhook_event(
            gong_webhook_id=webhook_id,
            event_type=webhook_payload.event,
            payload=payload,
            signature_valid=signature_valid,
        )
    except Exception as e:
        logger.error(f"Failed to store webhook event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store event",
        )

    # TODO: Trigger Prefect flow asynchronously (Phase 1 completion)
    # from flows.process_new_call import trigger_process_new_call
    # trigger_process_new_call(call_id=webhook_payload.call_id, webhook_event_id=webhook_event.id)

    logger.info(f"Successfully received webhook {webhook_id}: {webhook_payload.event}")

    return {
        "status": "received",
        "webhook_id": webhook_id,
        "event": webhook_payload.event,
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
