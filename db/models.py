"""
Pydantic models for database entities.
Provides type safety and validation for data flowing through the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator

# ============================================================================
# ENUMS
# ============================================================================


class WebhookEventStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CallType(str, Enum):
    DISCOVERY = "discovery"
    DEMO = "demo"
    NEGOTIATION = "negotiation"
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"
    FOLLOW_UP = "follow_up"
    EXECUTIVE_BRIEFING = "executive_briefing"


class Product(str, Enum):
    PREFECT = "prefect"
    HORIZON = "horizon"
    BOTH = "both"


class Role(str, Enum):
    AE = "ae"  # Account Executive
    SE = "se"  # Sales Engineer
    CSM = "csm"  # Customer Success Manager
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    PARTNER = "partner"


class CoachingDimension(str, Enum):
    PRODUCT_KNOWLEDGE = "product_knowledge"
    DISCOVERY = "discovery"
    OBJECTION_HANDLING = "objection_handling"
    ENGAGEMENT = "engagement"


class SessionType(str, Enum):
    REAL_TIME = "real_time"
    WEEKLY_REVIEW = "weekly_review"
    ON_DEMAND = "on_demand"


class FeedbackType(str, Enum):
    ACCURATE = "accurate"
    INACCURATE = "inaccurate"
    MISSING_CONTEXT = "missing_context"
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


# ============================================================================
# WEBHOOK EVENTS
# ============================================================================


class WebhookEvent(BaseModel):
    """Webhook event from Gong."""

    id: UUID | None = None
    gong_webhook_id: str
    event_type: str
    payload: dict[str, Any]
    signature_valid: bool
    status: WebhookEventStatus
    error_message: str | None = None
    received_at: datetime | None = None
    processed_at: datetime | None = None


# ============================================================================
# CALLS & TRANSCRIPTS
# ============================================================================


class Call(BaseModel):
    """Call metadata from Gong."""

    id: UUID | None = None
    gong_call_id: str
    title: str | None = None
    scheduled_at: datetime | None = None
    duration_seconds: int | None = None
    call_type: CallType | None = None
    product: Product | None = None
    created_at: datetime | None = None
    processed_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class Speaker(BaseModel):
    """Call participant."""

    id: UUID | None = None
    call_id: UUID
    name: str
    email: str | None = None
    role: Role | None = None
    company_side: bool = False  # true = Prefect employee
    talk_time_seconds: int | None = None
    talk_time_percentage: float | None = None

    @field_validator("talk_time_percentage")
    def validate_talk_time_percentage(cls, v: float | None) -> float | None:
        if v is not None and not 0 <= v <= 100:
            raise ValueError("talk_time_percentage must be between 0 and 100")
        return v


class ChunkMetadata(BaseModel):
    """Metadata for transcript chunking."""

    chunk_id: int
    start_token: int
    end_token: int
    overlap_tokens: int


class Transcript(BaseModel):
    """Transcript segment from a call."""

    id: UUID | None = None
    call_id: UUID
    speaker_id: UUID | None = None
    sequence_number: int
    timestamp_seconds: int | None = None
    text: str
    sentiment: str | None = None  # positive, neutral, negative
    topics: list[str] | None = None
    chunk_metadata: ChunkMetadata | None = None


# ============================================================================
# ANALYSIS RUNS
# ============================================================================


class AnalysisRun(BaseModel):
    """Analysis run tracking for observability."""

    id: UUID | None = None
    call_id: UUID | None = None
    webhook_event_id: UUID | None = None
    flow_run_id: UUID | None = None  # Prefect flow run ID
    status: AnalysisRunStatus
    dimensions_analyzed: list[CoachingDimension] | None = None
    cache_hit: bool = False
    total_tokens_used: int | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


# ============================================================================
# COACHING SESSIONS
# ============================================================================


class SpecificExample(BaseModel):
    """Specific example from coaching analysis."""

    quote: str
    timestamp: int | None = None
    analysis: str


class CoachingSession(BaseModel):
    """Coaching session result."""

    id: UUID | None = None
    call_id: UUID
    rep_id: UUID
    coaching_dimension: CoachingDimension
    session_type: SessionType
    analyst: str  # e.g., "claude-sonnet-4.5"
    created_at: datetime | None = None

    # Caching metadata
    cache_key: str | None = None
    transcript_hash: str | None = None
    rubric_version: str | None = None

    # Analysis results
    score: int | None = None
    strengths: list[str] | None = None
    areas_for_improvement: list[str] | None = None
    specific_examples: dict[str, list[SpecificExample]] | None = None
    action_items: list[str] | None = None
    full_analysis: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("score")
    def validate_score(cls, v: int | None) -> int | None:
        if v is not None and not 0 <= v <= 100:
            raise ValueError("score must be between 0 and 100")
        return v


class CoachingMetric(BaseModel):
    """Granular metric for trending analysis."""

    id: UUID | None = None
    coaching_session_id: UUID
    metric_name: str
    metric_value: float
    metric_context: dict[str, Any] | None = None
    created_at: datetime | None = None


# ============================================================================
# KNOWLEDGE BASE
# ============================================================================


class KnowledgeBaseCategory(str, Enum):
    FEATURE = "feature"
    DIFFERENTIATION = "differentiation"
    USE_CASE = "use_case"
    PRICING = "pricing"
    COMPETITOR = "competitor"


class KnowledgeBaseEntry(BaseModel):
    """Product knowledge base entry."""

    id: UUID | None = None
    product: Product
    category: KnowledgeBaseCategory
    content: str
    metadata: dict[str, Any] | None = None
    last_updated: datetime | None = None


# ============================================================================
# COACHING RUBRICS
# ============================================================================


class CoachingRubric(BaseModel):
    """Coaching rubric with versioning."""

    id: UUID | None = None
    name: str
    version: str  # Semantic version (e.g., "1.0.0")
    category: CoachingDimension
    criteria: dict[str, Any]
    scoring_guide: dict[str, Any] | None = None
    examples: dict[str, Any] | None = None
    active: bool = True
    created_at: datetime | None = None
    deprecated_at: datetime | None = None


# ============================================================================
# COACHING FEEDBACK
# ============================================================================


class CoachingFeedback(BaseModel):
    """Feedback on coaching sessions."""

    id: UUID | None = None
    coaching_session_id: UUID
    rep_id: UUID
    feedback_type: FeedbackType
    feedback_text: str | None = None
    created_at: datetime | None = None


# ============================================================================
# HELPER MODELS FOR QUERIES
# ============================================================================


class RepPerformanceSummary(BaseModel):
    """Summary of rep performance from view."""

    rep_id: UUID
    rep_name: str
    rep_email: str | None
    rep_role: Role | None
    total_calls: int
    avg_score: float | None
    total_coaching_sessions: int
    last_coached: datetime | None


class CallAnalysisStatus(BaseModel):
    """Call analysis status from view."""

    call_id: UUID
    gong_call_id: str
    title: str | None
    scheduled_at: datetime | None
    processed_at: datetime | None
    analysis_status: AnalysisRunStatus | None
    dimensions_analyzed: list[CoachingDimension] | None
    cache_hit: bool | None
    analysis_completed_at: datetime | None
    coaching_sessions_count: int
