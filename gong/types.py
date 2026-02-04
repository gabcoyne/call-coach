"""Type definitions for Gong API responses."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class GongSpeaker(BaseModel):
    """Speaker information from Gong."""
    speaker_id: str
    name: str
    email: str | None = None
    title: str | None = None
    is_internal: bool = False
    talk_time_seconds: int = 0


class GongTranscriptSegment(BaseModel):
    """Single transcript segment."""
    speaker_id: str
    start_time: float  # seconds
    duration: float  # seconds
    text: str
    sentiment: str | None = None


class GongTranscript(BaseModel):
    """Full call transcript from Gong."""
    call_id: str
    segments: list[GongTranscriptSegment]


class GongCall(BaseModel):
    """Call metadata from Gong."""
    id: str
    title: str | None = None
    scheduled: datetime | None = None
    started: datetime | None = None
    duration: int | None = None  # seconds
    primary_user_id: str | None = None
    direction: str | None = None  # inbound, outbound
    system: str | None = None  # zoom, teams, etc
    scope: str | None = None  # internal, external
    media: str | None = None  # video, audio
    language: str | None = None
    workspace_id: str | None = None
    url: str | None = None
    participants: list[GongSpeaker] | None = None
    custom_data: dict[str, Any] | None = None


class GongWebhookPayload(BaseModel):
    """Webhook payload from Gong."""
    event: str
    resource_type: str
    resource_id: str
    call_id: str | None = None
    timestamp: datetime
    data: dict[str, Any] | None = None
