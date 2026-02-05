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


class GongSentence(BaseModel):
    """Single sentence in a transcript monologue.

    Note: Times are in milliseconds from call start, not seconds.
    """
    start: int  # milliseconds from call start
    end: int  # milliseconds from call start
    text: str


class GongMonologue(BaseModel):
    """Monologue (continuous speech by one speaker on a topic).

    The Gong API groups transcript by speaker and topic, not individual sentences.
    Each monologue contains multiple sentences on the same topic.
    """
    speaker_id: str
    topic: str | None = None  # e.g., "Objections", "Introduction", "Product Demo"
    sentences: list[GongSentence]


class GongTranscript(BaseModel):
    """Full call transcript from Gong.

    Official API returns transcript as list of monologues, where each monologue
    is a continuous block of speech by one speaker on a specific topic.
    """
    call_id: str
    monologues: list[GongMonologue]

    def get_flat_segments(self) -> list[dict]:
        """
        Convert monologue structure to flat segments for backward compatibility.

        Returns list of dicts with: speaker_id, start_time_seconds, duration_seconds, text
        """
        segments = []
        for monologue in self.monologues:
            for sentence in monologue.sentences:
                segments.append({
                    "speaker_id": monologue.speaker_id,
                    "topic": monologue.topic,
                    "start_time_seconds": sentence.start / 1000.0,
                    "duration_seconds": (sentence.end - sentence.start) / 1000.0,
                    "text": sentence.text,
                })
        return segments


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
