"""
Manager Reviews API

Enables managers to review AI-analyzed calls and provide their own ratings.
Creates feedback training data for continuous model improvement.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from db import execute_query, fetch_all, fetch_one
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/manager-reviews", tags=["Manager Reviews"])


# ============================================================================
# Request/Response Models
# ============================================================================


class KeyMoment(BaseModel):
    """A timestamped moment from the call to highlight"""

    timestamp: int = Field(..., description="Timestamp in seconds")
    note: str = Field(..., description="Manager's note about this moment")
    type: str = Field(default="neutral", description="Type: positive, negative, or neutral")


class SubmitManagerReviewRequest(BaseModel):
    """Manager's review of an AI-analyzed call"""

    # Manager's ratings
    overall_score: int = Field(..., ge=0, le=100, description="Manager's overall score")
    dimension_scores: dict[str, int] = Field(
        ..., description="Manager's scores per dimension (discovery, engagement, etc.)"
    )

    # AI comparison
    agreement_level: str = Field(
        ...,
        description="Level of agreement with AI: 'agree', 'mostly', or 'disagree'",
        pattern="^(agree|mostly|disagree)$",
    )

    # Feedback
    what_ai_missed: str | None = Field(None, description="What the AI got wrong or missed")
    key_moments: list[KeyMoment] = Field(
        default_factory=list, description="Timestamped moments to highlight for rep"
    )
    coaching_notes: str | None = Field(None, description="Private coaching notes for the rep")

    # Options
    share_with_rep: bool = Field(
        default=False, description="Whether to share this review with the rep"
    )
    review_duration_seconds: int | None = Field(
        None, description="How long manager spent reviewing (for metrics)"
    )


class ManagerReviewResponse(BaseModel):
    """Response after submitting a manager review"""

    id: str
    call_id: str
    manager_id: str
    overall_score: int
    dimension_scores: dict[str, int]
    ai_overall_score: int
    ai_dimension_scores: dict[str, int]
    agreement_level: str
    shared_with_rep: bool
    created_at: str
    training_data_created: int = Field(
        ..., description="Number of training examples created from this review"
    )


class ManagerReviewStats(BaseModel):
    """Statistics about a manager's review patterns"""

    manager_id: str
    total_reviews: int
    avg_review_duration_seconds: float | None

    # Agreement rates
    agree_count: int
    mostly_count: int
    disagree_count: int
    agree_pct: float
    mostly_pct: float
    disagree_pct: float

    # Score deltas
    avg_overall_delta: float

    # Rep engagement
    shared_count: int
    acknowledged_count: int


class DimensionDelta(BaseModel):
    """How a manager scores differently from AI for a specific dimension"""

    dimension: str
    review_count: int
    avg_manager_score: float
    avg_ai_score: float
    avg_score_delta: float
    stddev_score_delta: float | None


# ============================================================================
# Helper Functions
# ============================================================================


def _get_ai_scores_from_call(call_id: UUID) -> tuple[int, dict[str, int]]:
    """
    Get the most recent AI analysis scores for a call.

    Returns:
        (overall_score, dimension_scores)
    """
    # Get all coaching sessions for this call
    sessions = fetch_all(
        """
        SELECT coaching_dimension, score
        FROM coaching_sessions
        WHERE call_id = %s
        ORDER BY created_at DESC
        """,
        (str(call_id),),
    )

    if not sessions:
        raise HTTPException(status_code=404, detail=f"No AI analysis found for call {call_id}")

    # Extract dimension scores
    dimension_scores = {}
    for session in sessions:
        dim = session["coaching_dimension"]
        score = session["score"]
        # Only take the first (most recent) score for each dimension
        if dim not in dimension_scores and score is not None:
            dimension_scores[dim] = score

    # Calculate overall score (average of dimensions)
    if dimension_scores:
        overall_score = round(sum(dimension_scores.values()) / len(dimension_scores))
    else:
        overall_score = 0

    return overall_score, dimension_scores


def _create_training_data_from_review(
    review_id: UUID, call_id: UUID, manager_scores: dict, ai_scores: dict
) -> int:
    """
    Create feedback training data entries from a manager review.

    For each dimension where manager and AI disagree, create a training example.

    Returns:
        Number of training examples created
    """
    training_count = 0

    for dimension, manager_score in manager_scores.items():
        ai_score = ai_scores.get(dimension)
        if ai_score is None:
            continue

        score_delta = manager_score - ai_score

        # Only create training data if there's meaningful disagreement (>5 points)
        if abs(score_delta) <= 5:
            continue

        # Get AI reasoning from coaching session
        session = fetch_one(
            """
            SELECT score, strengths, areas_for_improvement, action_items
            FROM coaching_sessions
            WHERE call_id = %s AND coaching_dimension = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (str(call_id), dimension),
        )

        if not session:
            continue

        # Combine AI reasoning
        ai_reasoning_parts = []
        if session.get("strengths"):
            ai_reasoning_parts.append(f"Strengths: {', '.join(session['strengths'])}")
        if session.get("areas_for_improvement"):
            ai_reasoning_parts.append(
                f"Improvements: {', '.join(session['areas_for_improvement'])}"
            )
        ai_reasoning = "; ".join(ai_reasoning_parts) if ai_reasoning_parts else None

        # Get manager reasoning from review
        manager_reasoning = fetch_one(
            """
            SELECT what_ai_missed
            FROM manager_reviews
            WHERE id = %s
            """,
            (str(review_id),),
        )

        # Insert training data
        execute_query(
            """
            INSERT INTO feedback_training_data (
                manager_review_id,
                call_id,
                dimension,
                ai_score,
                ai_reasoning,
                manager_score,
                manager_reasoning,
                score_delta
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(review_id),
                str(call_id),
                dimension,
                ai_score,
                ai_reasoning,
                manager_score,
                manager_reasoning.get("what_ai_missed") if manager_reasoning else None,
                score_delta,
            ),
        )

        training_count += 1
        logger.info(
            f"Created training data: {dimension} - AI: {ai_score}, Manager: {manager_score}, Delta: {score_delta}"
        )

    return training_count


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/calls/{call_id}/review", response_model=ManagerReviewResponse)
async def submit_manager_review(
    call_id: str,
    review: SubmitManagerReviewRequest,
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Submit a manager review for a call.

    Requires X-User-Email header with manager's email.
    Creates feedback training data for dimensions with significant disagreement.
    """
    try:
        call_uuid = UUID(call_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid call ID format")

    # Get manager user ID
    manager = fetch_one(
        """
        SELECT id FROM users WHERE email = %s AND role = 'manager'
        """,
        (x_user_email,),
    )

    if not manager:
        raise HTTPException(status_code=403, detail="Only managers can submit reviews")

    manager_id = UUID(manager["id"])

    # Verify call exists
    call = fetch_one(
        """
        SELECT id FROM calls WHERE id = %s
        """,
        (str(call_uuid),),
    )

    if not call:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found")

    # Get AI scores for comparison
    ai_overall_score, ai_dimension_scores = _get_ai_scores_from_call(call_uuid)

    # Validate dimension scores match AI dimensions
    for dim in review.dimension_scores.keys():
        if dim not in ai_dimension_scores:
            logger.warning(f"Manager scored dimension {dim} which AI did not analyze")

    # Convert key moments to JSONB format
    import json

    key_moments_json = [
        {"timestamp": km.timestamp, "note": km.note, "type": km.type} for km in review.key_moments
    ]

    # Insert manager review and create training data in a transaction
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Insert manager review
                cur.execute(
                    """
                    INSERT INTO manager_reviews (
                        call_id,
                        manager_id,
                        overall_score,
                        dimension_scores,
                        ai_overall_score,
                        ai_dimension_scores,
                        agreement_level,
                        what_ai_missed,
                        key_moments,
                        coaching_notes,
                        shared_with_rep,
                        review_duration_seconds,
                        reviewed_at
                    ) VALUES (%s, %s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s::jsonb, %s, %s, %s, NOW())
                    RETURNING id, created_at
                    """,
                    (
                        str(call_uuid),
                        str(manager_id),
                        review.overall_score,
                        json.dumps(review.dimension_scores),
                        ai_overall_score,
                        json.dumps(ai_dimension_scores),
                        review.agreement_level,
                        review.what_ai_missed,
                        json.dumps(key_moments_json),
                        review.coaching_notes,
                        review.share_with_rep,
                        review.review_duration_seconds,
                    ),
                )
                review_result = cur.fetchone()
                review_id = UUID(review_result[0])
                created_at = review_result[1]

                logger.info(
                    f"Manager review created: {review_id} by {x_user_email} for call {call_id}"
                )

                # Create training data within same transaction
                training_count = 0
                for dimension, manager_score in review.dimension_scores.items():
                    ai_score = ai_dimension_scores.get(dimension)
                    if ai_score is None:
                        continue

                    score_delta = manager_score - ai_score

                    # Only create training data if meaningful disagreement (>5 points)
                    if abs(score_delta) <= 5:
                        continue

                    # Get AI reasoning
                    cur.execute(
                        """
                        SELECT score, strengths, areas_for_improvement
                        FROM coaching_sessions
                        WHERE call_id = %s AND coaching_dimension = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                        """,
                        (str(call_uuid), dimension),
                    )
                    session_row = cur.fetchone()
                    if not session_row:
                        continue

                    # Combine AI reasoning
                    ai_reasoning_parts = []
                    if session_row[1]:  # strengths
                        ai_reasoning_parts.append(f"Strengths: {', '.join(session_row[1])}")
                    if session_row[2]:  # areas_for_improvement
                        ai_reasoning_parts.append(f"Improvements: {', '.join(session_row[2])}")
                    ai_reasoning = "; ".join(ai_reasoning_parts) if ai_reasoning_parts else None

                    # Insert training data
                    cur.execute(
                        """
                        INSERT INTO feedback_training_data (
                            manager_review_id,
                            call_id,
                            dimension,
                            ai_score,
                            ai_reasoning,
                            manager_score,
                            manager_reasoning,
                            score_delta
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            str(review_id),
                            str(call_uuid),
                            dimension,
                            ai_score,
                            ai_reasoning,
                            manager_score,
                            review.what_ai_missed,
                            score_delta,
                        ),
                    )
                    training_count += 1

                conn.commit()

    except Exception as e:
        if "manager_reviews_unique_call_manager" in str(e):
            raise HTTPException(
                status_code=409,
                detail="You have already reviewed this call. Use PATCH to update.",
            )
        raise HTTPException(status_code=500, detail=f"Failed to save review: {str(e)}")

    logger.info(
        f"Created {training_count} training examples from review {review_id} "
        f"(agreement: {review.agreement_level})"
    )

    return ManagerReviewResponse(
        id=str(review_id),
        call_id=str(call_uuid),
        manager_id=str(manager_id),
        overall_score=review.overall_score,
        dimension_scores=review.dimension_scores,
        ai_overall_score=ai_overall_score,
        ai_dimension_scores=ai_dimension_scores,
        agreement_level=review.agreement_level,
        shared_with_rep=review.share_with_rep,
        created_at=created_at.isoformat(),
        training_data_created=training_count,
    )


@router.get("/calls/{call_id}/review")
async def get_manager_review(
    call_id: str,
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Get the manager review for a call (if exists).

    Returns 404 if no review exists yet.
    """
    try:
        call_uuid = UUID(call_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid call ID format")

    # Get manager user ID
    manager = fetch_one(
        """
        SELECT id FROM users WHERE email = %s
        """,
        (x_user_email,),
    )

    if not manager:
        raise HTTPException(status_code=404, detail="User not found")

    manager_id = UUID(manager["id"])

    # Get review
    review = fetch_one(
        """
        SELECT
            id, call_id, manager_id,
            overall_score, dimension_scores,
            ai_overall_score, ai_dimension_scores,
            agreement_level,
            what_ai_missed, key_moments, coaching_notes,
            reviewed_at, review_duration_seconds,
            shared_with_rep, rep_acknowledged_at,
            created_at, updated_at
        FROM manager_reviews
        WHERE call_id = %s AND manager_id = %s
        """,
        (str(call_uuid), str(manager_id)),
    )

    if not review:
        raise HTTPException(status_code=404, detail="No review found for this call by this manager")

    return review


@router.get("/stats", response_model=ManagerReviewStats)
async def get_manager_stats(
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Get review statistics for the current manager.

    Shows agreement rates, score deltas, and overall review patterns.
    """
    # Get manager user ID
    manager = fetch_one(
        """
        SELECT id FROM users WHERE email = %s
        """,
        (x_user_email,),
    )

    if not manager:
        raise HTTPException(status_code=404, detail="User not found")

    manager_id = UUID(manager["id"])

    # Get stats from view
    stats = fetch_one(
        """
        SELECT * FROM manager_review_stats WHERE manager_id = %s
        """,
        (str(manager_id),),
    )

    if not stats:
        # Return empty stats if no reviews yet
        return ManagerReviewStats(
            manager_id=str(manager_id),
            total_reviews=0,
            avg_review_duration_seconds=None,
            agree_count=0,
            mostly_count=0,
            disagree_count=0,
            agree_pct=0.0,
            mostly_pct=0.0,
            disagree_pct=0.0,
            avg_overall_delta=0.0,
            shared_count=0,
            acknowledged_count=0,
        )

    return ManagerReviewStats(**stats)


@router.get("/dimension-deltas", response_model=list[DimensionDelta])
async def get_dimension_deltas(
    x_user_email: str = Header(..., alias="X-User-Email"),
):
    """
    Get per-dimension scoring differences between manager and AI.

    Shows where manager consistently scores higher or lower than AI.
    """
    # Get manager user ID
    manager = fetch_one(
        """
        SELECT id FROM users WHERE email = %s
        """,
        (x_user_email,),
    )

    if not manager:
        raise HTTPException(status_code=404, detail="User not found")

    manager_id = UUID(manager["id"])

    # Get dimension deltas from view
    deltas = fetch_all(
        """
        SELECT * FROM dimension_score_deltas
        WHERE manager_id = %s
        ORDER BY dimension
        """,
        (str(manager_id),),
    )

    return [DimensionDelta(**delta) for delta in deltas]


@router.get("/training-data/summary")
async def get_training_data_summary():
    """
    Get summary of available training data for model improvement.

    Shows counts by dimension and delta category (over/underestimate).
    Requires admin role.
    """
    summary = fetch_all(
        """
        SELECT * FROM training_data_summary
        ORDER BY dimension, delta_category
        """
    )

    return summary


@router.get("/training-data/export")
async def export_training_data(
    dimension: str | None = None,
    unused_only: bool = True,
    limit: int = 1000,
):
    """
    Export training data for model fine-tuning.

    Returns examples where managers disagreed with AI scores.
    Requires admin role.
    """
    where_clauses = []
    params = []

    if dimension:
        where_clauses.append("dimension = %s")
        params.append(dimension)

    if unused_only:
        where_clauses.append("used_for_training = FALSE")

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    examples = fetch_all(
        f"""
        SELECT
            ftd.id,
            ftd.dimension,
            ftd.ai_score,
            ftd.ai_reasoning,
            ftd.manager_score,
            ftd.manager_reasoning,
            ftd.score_delta,
            ftd.delta_category,
            ftd.created_at,
            c.title as call_title,
            c.scheduled_at as call_date
        FROM feedback_training_data ftd
        JOIN calls c ON ftd.call_id = c.id
        {where_sql}
        ORDER BY ABS(ftd.score_delta) DESC
        LIMIT %s
        """,
        (*params, limit),
    )

    return examples
