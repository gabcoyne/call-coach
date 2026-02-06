"""
Analyze Call Tool - Deep-dive coaching analysis for a specific call.
"""
import logging
from typing import Any
from uuid import UUID

from analysis.engine import analyze_call as run_analysis
from db import fetch_one, fetch_all
from db.models import CoachingDimension

logger = logging.getLogger(__name__)


def analyze_call_tool(
    call_id: str,
    dimensions: list[str] | None = None,
    use_cache: bool = True,
    include_transcript_snippets: bool = True,
    force_reanalysis: bool = False,
) -> dict[str, Any]:
    """
    Perform comprehensive coaching analysis on a call.

    Args:
        call_id: Gong call ID
        dimensions: Coaching dimensions to analyze
        use_cache: Whether to use cached results
        include_transcript_snippets: Include actual quotes
        force_reanalysis: Force new analysis even if cached

    Returns:
        Comprehensive analysis with scores and coaching insights
    """
    logger.info(f"Analyzing call {call_id}")

    # Step 1: Verify call exists in database
    call = fetch_one(
        """
        SELECT c.id, c.gong_call_id, c.title, c.scheduled_at,
               c.duration_seconds, c.call_type, c.product, c.metadata
        FROM calls c
        WHERE c.gong_call_id = %s OR c.id::text = %s
        """,
        (call_id, call_id),
    )

    if not call:
        raise ValueError(f"Call {call_id} not found in database. Has it been processed yet?")

    db_call_id = UUID(call["id"])
    logger.info(f"Found call: {call['title']}")

    # Step 2: Determine dimensions to analyze
    if dimensions is None:
        dimensions = [d.value for d in CoachingDimension]
    else:
        # Validate dimensions
        valid_dimensions = {d.value for d in CoachingDimension}
        invalid = [d for d in dimensions if d not in valid_dimensions]
        if invalid:
            raise ValueError(
                f"Invalid dimensions: {invalid}. "
                f"Valid options: {sorted(valid_dimensions)}"
            )

    logger.info(f"Analyzing {len(dimensions)} dimensions: {dimensions}")

    # Step 3: Get call participants
    speakers = fetch_all(
        """
        SELECT id, name, email, role, company_side,
               talk_time_seconds, talk_time_percentage
        FROM speakers
        WHERE call_id = %s
        """,
        (str(db_call_id),),
    )

    # Identify the rep (internal speaker)
    rep = next((s for s in speakers if s["company_side"] and s["role"] in ["ae", "se", "csm"]), None)
    if not rep:
        logger.warning("No Prefect rep found on call - using first internal speaker")
        rep = next((s for s in speakers if s["company_side"]), speakers[0] if speakers else None)

    # Step 4: Run analysis for each dimension
    results = {}
    for dimension in dimensions:
        try:
            analysis = run_analysis(
                call_id=str(db_call_id),
                dimension=CoachingDimension(dimension),
                use_cache=use_cache and not force_reanalysis,
            )
            results[dimension] = analysis
        except Exception as e:
            logger.error(f"Failed to analyze {dimension}: {e}", exc_info=True)
            results[dimension] = {
                "error": str(e),
                "score": None,
            }

    # Step 5: Aggregate scores
    scores = {}
    overall_score = 0
    valid_scores = 0

    for dim, analysis in results.items():
        score = analysis.get("score")
        scores[dim] = score
        if score is not None:
            overall_score += score
            valid_scores += 1

    if valid_scores > 0:
        overall_score = round(overall_score / valid_scores)
    scores["overall"] = overall_score

    # Step 6: Fetch transcript segments
    transcript_segments = []
    if include_transcript_snippets:
        transcript_rows = fetch_all(
            """
            SELECT s.name, t.timestamp_seconds, t.text
            FROM transcripts t
            LEFT JOIN speakers s ON t.speaker_id = s.id
            WHERE t.call_id = %s
            ORDER BY t.sequence_number ASC
            """,
            (str(db_call_id),),
        )
        transcript_segments = [
            {
                "speaker": row["name"] or "Unknown",
                "timestamp_seconds": row["timestamp_seconds"] or 0,
                "text": row["text"],
            }
            for row in transcript_rows
        ]

    # Step 7: Aggregate insights across dimensions
    all_strengths = []
    all_improvements = []
    all_action_items = []
    all_examples = {"good": [], "needs_work": []}

    for dim, analysis in results.items():
        if "error" not in analysis:
            all_strengths.extend(analysis.get("strengths", []))
            all_improvements.extend(analysis.get("areas_for_improvement", []))
            all_action_items.extend(analysis.get("action_items", []))

            if include_transcript_snippets:
                examples = analysis.get("specific_examples", {})
                all_examples["good"].extend(examples.get("good", []))
                all_examples["needs_work"].extend(examples.get("needs_work", []))

    # Step 8: Build response
    # Extract gong_url from metadata if available
    metadata = call.get("metadata") or {}
    gong_url = metadata.get("gong_url") or f"https://app.gong.io/call?id={call['gong_call_id']}"

    response = {
        "call_metadata": {
            "id": call["gong_call_id"],
            "title": call["title"],
            "date": str(call["scheduled_at"]) if call["scheduled_at"] else None,
            "duration_seconds": call["duration_seconds"],
            "call_type": call["call_type"],
            "product": call["product"],
            "gong_url": gong_url,
            "recording_url": metadata.get("recording_url"),
            "participants": [
                {
                    "name": s["name"],
                    "email": s["email"],
                    "role": s["role"],
                    "is_internal": s["company_side"],
                    "talk_time_seconds": s["talk_time_seconds"],
                }
                for s in speakers
            ],
        },
        "rep_analyzed": {
            "name": rep["name"] if rep else "Unknown",
            "email": rep["email"] if rep else None,
            "role": rep["role"] if rep else None,
        } if rep else None,
        "scores": scores,
        "strengths": all_strengths[:10],  # Top 10
        "areas_for_improvement": all_improvements[:10],  # Top 10
        "specific_examples": all_examples if include_transcript_snippets else None,
        "action_items": all_action_items,
        "dimension_details": results,
        "comparison_to_average": calculate_comparison_to_average(scores, call["product"]),
        "transcript": transcript_segments if include_transcript_snippets else None,
    }

    logger.info(f"Analysis complete. Overall score: {overall_score}/100")
    return response


def calculate_comparison_to_average(scores: dict[str, int | None], product: str | None) -> list[dict]:
    """
    Compare rep scores to team averages.

    Args:
        scores: Rep's scores for this call
        product: Product being sold

    Returns:
        List of comparisons showing rep vs team average
    """
    # Query team averages
    team_avg = fetch_all(
        """
        SELECT
            coaching_dimension,
            AVG(score) as avg_score,
            COUNT(*) as sample_size
        FROM coaching_sessions
        WHERE score IS NOT NULL
            AND created_at > NOW() - INTERVAL '90 days'
            AND (%s IS NULL OR EXISTS (
                SELECT 1 FROM calls
                WHERE calls.id = coaching_sessions.call_id
                AND calls.product = %s
            ))
        GROUP BY coaching_dimension
        """,
        (product, product),
    )

    comparisons = []
    for avg in team_avg:
        dim = avg["coaching_dimension"]
        rep_score = scores.get(dim)

        if rep_score is not None:
            comparisons.append({
                "metric": dim,
                "rep_score": rep_score,
                "team_average": round(float(avg["avg_score"]), 1),
                "difference": round(rep_score - float(avg["avg_score"]), 1),
                "percentile": calculate_percentile(rep_score, dim),
                "sample_size": avg["sample_size"],
            })

    return comparisons


def calculate_percentile(score: int, dimension: str) -> int:
    """
    Calculate what percentile this score falls into.

    Args:
        score: Rep's score
        dimension: Coaching dimension

    Returns:
        Percentile (0-100)
    """
    result = fetch_one(
        """
        SELECT
            COUNT(CASE WHEN score < %s THEN 1 END)::float /
            NULLIF(COUNT(*), 0) * 100 as percentile
        FROM coaching_sessions
        WHERE coaching_dimension = %s
            AND score IS NOT NULL
            AND created_at > NOW() - INTERVAL '90 days'
        """,
        (score, dimension),
    )

    return round(float(result["percentile"])) if result and result["percentile"] else 50
