"""
Analyze Call Tool - Deep-dive coaching analysis for a specific call.
"""

import logging
from typing import Any, TypedDict
from uuid import UUID

from db import fetch_all, fetch_one
from db.models import CoachingDimension

logger = logging.getLogger(__name__)


class WinData(TypedDict):
    score: int
    max_score: int
    status: str
    evidence: list[dict[str, str]]


def validate_five_wins_scores(five_wins_eval: dict[str, Any]) -> None:
    """
    Validate Five Wins evaluation scoring integrity.

    Ensures:
    1. Sum of individual win scores equals overall_score
    2. Scores are within valid ranges (0-max_score)
    3. Status values are valid ("met", "partial", "missed")

    Args:
        five_wins_eval: Five Wins evaluation dict

    Raises:
        ValueError: If validation fails
    """
    wins = [
        ("business_win", 35),
        ("technical_win", 25),
        ("security_win", 15),
        ("commercial_win", 15),
        ("legal_win", 10),
    ]

    sum_of_wins = 0
    for win_name, max_score in wins:
        win_data = five_wins_eval.get(win_name, {})

        # Validate score exists and is in range
        score = win_data.get("score")
        if score is None:
            raise ValueError(f"{win_name} missing score field")

        if not (0 <= score <= max_score):
            raise ValueError(f"{win_name} score {score} out of range [0, {max_score}]")

        sum_of_wins += score

        # Validate status
        status = win_data.get("status")
        if status not in ["met", "partial", "missed"]:
            raise ValueError(
                f"{win_name} has invalid status '{status}' "
                f"(must be 'met', 'partial', or 'missed')"
            )

        # Validate max_score matches expected
        if win_data.get("max_score") != max_score:
            raise ValueError(
                f"{win_name} max_score mismatch: "
                f"expected {max_score}, got {win_data.get('max_score')}"
            )

    # Validate overall_score equals sum
    overall_score = five_wins_eval.get("overall_score", 0)
    if abs(overall_score - sum_of_wins) > 0.01:  # Floating point tolerance
        raise ValueError(
            f"Five Wins overall_score ({overall_score}) does not match "
            f"sum of win scores ({sum_of_wins})"
        )

    # Validate overall_score is within 0-100
    if not (0 <= overall_score <= 100):
        raise ValueError(f"overall_score {overall_score} out of range [0, 100]")

    logger.debug(
        f"Five Wins validation passed: overall={overall_score}, "
        f"wins_secured={five_wins_eval.get('wins_secured', 0)}"
    )


def aggregate_five_wins(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """
    Aggregate five_wins_coverage from multiple dimension analyses into single evaluation.

    Each dimension (discovery, engagement, product_knowledge, objection_handling) returns
    its own five_wins_coverage assessment. This function combines them by:
    1. Taking the highest score for each win across all dimensions
    2. Collecting all evidence from all dimensions
    3. Computing overall wins_secured count

    Args:
        results: Dict mapping dimension name to analysis results

    Returns:
        Aggregated five_wins_evaluation with:
        - business_win, technical_win, security_win, commercial_win, legal_win
        - Each win has: score, max_score, status, evidence[]
        - wins_secured: count of wins with score > 50
        - overall_score: sum of all win scores
    """
    # Initialize aggregated wins structure
    wins: dict[str, WinData] = {
        "business_win": {"score": 0, "max_score": 35, "status": "missed", "evidence": []},
        "technical_win": {"score": 0, "max_score": 25, "status": "missed", "evidence": []},
        "security_win": {"score": 0, "max_score": 15, "status": "missed", "evidence": []},
        "commercial_win": {"score": 0, "max_score": 15, "status": "missed", "evidence": []},
        "legal_win": {"score": 0, "max_score": 10, "status": "missed", "evidence": []},
    }

    # Aggregate scores and evidence from each dimension
    for dim_name, analysis in results.items():
        if "error" in analysis:
            continue

        five_wins = analysis.get("five_wins_coverage", {})
        if not five_wins:
            continue

        # For each win, take the highest score across dimensions
        for win_name in wins.keys():
            win_data = five_wins.get(win_name, {})
            if not win_data:
                continue

            win_score = win_data.get("score", 0) or 0

            # Update if this dimension has higher score for this win
            if win_score > wins[win_name]["score"]:
                wins[win_name]["score"] = win_score

                # Update status based on score
                if win_score >= 90:
                    wins[win_name]["status"] = "met"
                elif win_score >= 50:
                    wins[win_name]["status"] = "partial"
                else:
                    wins[win_name]["status"] = "missed"

            # Collect evidence from this dimension (limit to avoid bloat)
            # Evidence format from prompts: discovery criteria with covered/notes
            discovery_data = (
                win_data.get("business_discovery")
                or win_data.get("technical_discovery")
                or win_data.get("infosec_discovery")
                or win_data.get("scoping_discovery")
                or win_data.get("legal_discovery")
            )

            if discovery_data and len(wins[win_name]["evidence"]) < 5:
                # Convert discovery notes to evidence format
                for criterion, details in discovery_data.items():
                    if isinstance(details, dict) and details.get("covered"):
                        wins[win_name]["evidence"].append(
                            {
                                "criterion": criterion,
                                "dimension": dim_name,
                                "notes": details.get("notes", ""),
                            }
                        )

    # Compute overall metrics
    wins_secured = sum(1 for win in wins.values() if win["score"] > 50)
    overall_score = sum(win["score"] for win in wins.values())

    # Validate score consistency
    expected_sum = (
        wins["business_win"]["score"]
        + wins["technical_win"]["score"]
        + wins["security_win"]["score"]
        + wins["commercial_win"]["score"]
        + wins["legal_win"]["score"]
    )

    if abs(overall_score - expected_sum) > 0.01:  # Allow floating point tolerance
        logger.warning(
            f"Five Wins score mismatch: overall_score={overall_score}, "
            f"sum of wins={expected_sum}. This should not happen."
        )
        # Use the explicit sum as source of truth
        overall_score = expected_sum

    return {
        "business_win": wins["business_win"],
        "technical_win": wins["technical_win"],
        "security_win": wins["security_win"],
        "commercial_win": wins["commercial_win"],
        "legal_win": wins["legal_win"],
        "wins_secured": wins_secured,
        "overall_score": overall_score,
    }


def analyze_call_tool(
    call_id: str,
    dimensions: list[str] | None = None,
    use_cache: bool = True,
    include_transcript_snippets: bool = True,
    force_reanalysis: bool = False,
    role: str | None = None,
) -> dict[str, Any]:
    """
    Perform comprehensive coaching analysis on a call with role-aware evaluation.

    Args:
        call_id: Gong call ID
        dimensions: Coaching dimensions to analyze
        use_cache: Whether to use cached results
        include_transcript_snippets: Include actual quotes
        force_reanalysis: Force new analysis even if cached
        role: Optional role override (ae, se, csm). If not provided, auto-detects from speaker.

    Returns:
        Comprehensive analysis with scores and coaching insights evaluated against role-specific rubric
    """
    logger.info(f"Analyzing call {call_id} (role override: {role})")

    # Step 1: Verify call exists in database
    call = fetch_one(
        """
        SELECT c.id, c.gong_call_id, c.title, c.scheduled_at,
               c.duration_seconds, c.call_type, c.product, c.metadata
        FROM calls c
        WHERE c.gong_call_id = %s OR c.id::text = %s
        """,
        (call_id, call_id),
        as_dict=True,
    )

    if not call or not isinstance(call, dict):
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
                f"Invalid dimensions: {invalid}. " f"Valid options: {sorted(valid_dimensions)}"
            )

    logger.info(f"Analyzing {len(dimensions)} dimensions: {dimensions}")

    # Step 3: Detect speaker role for role-aware evaluation
    from analysis.engine import detect_speaker_role

    # Use provided role or auto-detect
    if role:
        valid_roles = ["ae", "se", "csm"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role: {role}. Valid options: {valid_roles}")
        detected_role = role
        logger.info(f"Using provided role: {role}")
    else:
        detected_role = detect_speaker_role(str(db_call_id))
        logger.info(f"Auto-detected role: {detected_role}")

    # Get call participants
    speakers_result = fetch_all(
        """
        SELECT id, name, email, role, company_side,
               talk_time_seconds, talk_time_percentage
        FROM speakers
        WHERE call_id = %s
        """,
        (str(db_call_id),),
        as_dict=True,
    )

    # Type guard for speakers
    if not isinstance(speakers_result, list):
        raise TypeError("Expected list from fetch_all with as_dict=True")

    speakers = [s for s in speakers_result if isinstance(s, dict)]

    # Identify the rep (internal speaker)
    rep = next(
        (s for s in speakers if s.get("company_side") and s.get("role") in ["ae", "se", "csm"]),
        None,
    )
    if not rep:
        logger.warning("No Prefect rep found on call - using first internal speaker")
        rep = next(
            (s for s in speakers if s.get("company_side")), speakers[0] if speakers else None
        )

    # Step 4: Run analysis for each dimension
    results: dict[str, dict[str, Any]] = {}
    for dimension in dimensions:
        try:
            # Get transcript for analysis
            from analysis.engine import get_or_create_coaching_session

            segments = fetch_one(
                """
                SELECT STRING_AGG(text, ' ' ORDER BY sequence_number) as full_transcript
                FROM transcripts
                WHERE call_id = %s
                """,
                (str(db_call_id),),
                as_dict=True,
            )

            if segments and isinstance(segments, dict) and segments.get("full_transcript"):
                analysis = get_or_create_coaching_session(
                    call_id=db_call_id,
                    rep_id=UUID(rep["id"]) if rep and isinstance(rep, dict) else db_call_id,
                    dimension=CoachingDimension(dimension),
                    transcript=str(segments["full_transcript"]),
                    force_reanalysis=force_reanalysis,
                )
                results[dimension] = dict(analysis)
            else:
                raise ValueError(f"No transcript found for call {db_call_id}")
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
            as_dict=True,
        )

        # Type guard for transcript_rows
        if isinstance(transcript_rows, list):
            transcript_segments = [
                {
                    "speaker": row.get("name") or "Unknown",
                    "timestamp_seconds": row.get("timestamp_seconds") or 0,
                    "text": row.get("text", ""),
                }
                for row in transcript_rows
                if isinstance(row, dict)
            ]

    # Step 7: Aggregate insights across dimensions
    all_strengths: list[str] = []
    all_improvements: list[str] = []
    all_action_items: list[str] = []
    all_examples: dict[str, list[Any]] = {"good": [], "needs_work": []}

    for _, analysis in results.items():
        if "error" not in analysis:
            all_strengths.extend(analysis.get("strengths", []))
            all_improvements.extend(analysis.get("areas_for_improvement", []))
            all_action_items.extend(analysis.get("action_items", []))

            if include_transcript_snippets:
                examples = analysis.get("specific_examples", {})
                all_examples["good"].extend(examples.get("good", []))
                all_examples["needs_work"].extend(examples.get("needs_work", []))

    # Step 7b: Aggregate Five Wins evaluation across dimensions
    five_wins_evaluation = aggregate_five_wins(results)

    # Validate Five Wins scoring integrity
    validate_five_wins_scores(five_wins_evaluation)

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
        "rep_analyzed": (
            {
                "name": rep["name"] if rep else "Unknown",
                "email": rep["email"] if rep else None,
                "role": rep["role"] if rep else None,
                "evaluated_as_role": detected_role,  # Role used for rubric evaluation
            }
            if rep
            else None
        ),
        "scores": scores,
        "five_wins_evaluation": five_wins_evaluation,  # Primary scoring framework
        "strengths": all_strengths[:10],  # Top 10
        "areas_for_improvement": all_improvements[:10],  # Top 10
        "specific_examples": all_examples if include_transcript_snippets else None,
        "action_items": all_action_items,
        "dimension_details": results,  # Supplementary frameworks (discovery, engagement, etc.)
        "comparison_to_average": calculate_comparison_to_average(scores, call["product"]),
        "transcript": transcript_segments if include_transcript_snippets else None,
    }

    logger.info(f"Analysis complete. Overall score: {overall_score}/100")
    return response


def calculate_comparison_to_average(
    scores: dict[str, int | None], product: str | None
) -> list[dict]:
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
        as_dict=True,
    )

    comparisons = []
    if isinstance(team_avg, list):
        for avg in team_avg:
            if not isinstance(avg, dict):
                continue

            dim = avg.get("coaching_dimension")
            if not dim:
                continue

            rep_score = scores.get(dim)

            if rep_score is not None and avg.get("avg_score") is not None:
                comparisons.append(
                    {
                        "metric": dim,
                        "rep_score": rep_score,
                        "team_average": round(float(avg["avg_score"]), 1),
                        "difference": round(rep_score - float(avg["avg_score"]), 1),
                        "percentile": calculate_percentile(rep_score, dim),
                        "sample_size": avg.get("sample_size", 0),
                    }
                )

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
        as_dict=True,
    )

    return (
        round(float(result["percentile"]))
        if result and isinstance(result, dict) and result["percentile"]
        else 50
    )
