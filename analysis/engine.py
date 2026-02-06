"""
Core analysis engine for coaching insights.
Integrates Claude API with caching and chunking.
"""

import json
import logging
from typing import Any
from uuid import UUID

from anthropic import Anthropic

from coaching_mcp.shared import settings
from db import fetch_all, fetch_one
from db.models import CoachingDimension

from .cache import (
    generate_transcript_hash,
    get_active_rubric_version,
    get_cached_analysis,
    store_analysis_with_cache,
)
from .prompts import (
    analyze_discovery_prompt,
    analyze_engagement_prompt,
    analyze_objection_handling_prompt,
    analyze_product_knowledge_prompt,
)
from .rubric_loader import load_rubric

logger = logging.getLogger(__name__)

# Initialize Claude API client
anthropic_client = Anthropic(api_key=settings.anthropic_api_key)


def detect_speaker_role(call_id: str) -> str:
    """
    Detect the role of the primary Prefect speaker on a call.

    Identifies Prefect staff by @prefect.io email domain, selects primary speaker
    by talk time, and looks up their assigned role.

    Args:
        call_id: Call UUID

    Returns:
        Role identifier ('ae', 'se', 'csm'). Defaults to 'ae' if no role assigned.
    """

    # Get all speakers for the call
    speakers = fetch_all(
        """
        SELECT id, name, email, company_side, talk_time_seconds, talk_time_percentage
        FROM speakers
        WHERE call_id = %s
        """,
        (str(call_id),),
    )

    # Filter to Prefect speakers (company_side=true and @prefect.io email)
    prefect_speakers = [
        s
        for s in speakers
        if isinstance(s, dict)
        and s.get("company_side")
        and s.get("email")
        and s["email"].endswith("@prefect.io")
    ]

    if not prefect_speakers:
        logger.info(f"No Prefect speakers found for call {call_id}, defaulting to AE rubric")
        return "ae"

    # Select primary speaker (highest talk time)
    primary_speaker = max(prefect_speakers, key=lambda s: s.get("talk_time_percentage", 0) or 0)

    if not isinstance(primary_speaker, dict) or "email" not in primary_speaker:
        logger.warning(f"Invalid primary speaker data for call {call_id}, defaulting to AE rubric")
        return "ae"

    speaker_email = primary_speaker["email"]
    logger.info(
        f"Primary Prefect speaker on call {call_id}: {speaker_email} "
        f"({primary_speaker.get('talk_time_percentage', 0)}% talk time)"
    )

    # Look up role assignment
    role_result = fetch_one(
        "SELECT role FROM staff_roles WHERE email = %s", (speaker_email,), as_dict=True
    )

    if role_result and isinstance(role_result, dict) and "role" in role_result:
        role = str(role_result["role"])
        logger.info(f"Speaker {speaker_email} has assigned role: {role}")
    else:
        logger.info(f"No role assigned for {speaker_email}, defaulting to 'ae'")
        role = "ae"

    return role


def get_or_create_coaching_session(
    call_id: UUID,
    rep_id: UUID,
    dimension: CoachingDimension,
    transcript: str,
    force_reanalysis: bool = False,
    session_type: str = "on_demand",
) -> dict[str, Any]:
    """
    Get coaching session from cache or create new analysis.
    This is the main entry point for getting coaching insights.

    Args:
        call_id: Call UUID
        rep_id: Rep UUID
        dimension: Coaching dimension to analyze
        transcript: Full call transcript
        force_reanalysis: Bypass cache and regenerate
        session_type: Type of session (on_demand, weekly_review, etc.)

    Returns:
        Coaching session data with analysis
    """
    logger.info(
        f"Getting coaching session: call={call_id}, "
        f"dimension={dimension.value}, force={force_reanalysis}"
    )

    # Generate transcript hash for caching
    transcript_hash = generate_transcript_hash(transcript)

    # Get active rubric version
    try:
        rubric_version = get_active_rubric_version(dimension)
    except ValueError as e:
        logger.error(f"Failed to get rubric version: {e}")
        raise

    # Check cache if not forcing reanalysis
    if not force_reanalysis and settings.enable_caching:
        cached = get_cached_analysis(
            call_id=str(call_id),
            dimension=dimension,
            transcript_hash=transcript_hash,
            rubric_version=rubric_version,
        )

        if cached:
            logger.info(f"Returning cached analysis for call {call_id}")
            return cached

    # Cache miss or forced reanalysis - run new analysis
    logger.info(f"Running new analysis for call {call_id}, dimension={dimension.value}")

    # Get call metadata for context
    call_metadata_result = fetch_one(
        "SELECT * FROM calls WHERE id = %s", (str(call_id),), as_dict=True
    )
    call_metadata = (
        call_metadata_result
        if call_metadata_result and isinstance(call_metadata_result, dict)
        else None
    )

    # Run actual Claude API analysis with role-aware rubric
    analysis_result = _run_claude_analysis(
        call_id=str(call_id),
        dimension=dimension,
        transcript=transcript,
        call_metadata=call_metadata,
    )

    # Store analysis with cache metadata
    session_id = store_analysis_with_cache(
        call_id=str(call_id),
        rep_id=str(rep_id),
        dimension=dimension,
        transcript_hash=transcript_hash,
        rubric_version=rubric_version,
        analysis_result=analysis_result,
        session_type=session_type,
    )

    # Fetch and return stored session
    session = fetch_one(
        "SELECT * FROM coaching_sessions WHERE id = %s",
        (session_id,),
        as_dict=True,
    )

    if not session or not isinstance(session, dict):
        raise ValueError(f"Failed to retrieve coaching session {session_id}")

    return session


def analyze_call(
    call_id: UUID,
    dimensions: list[CoachingDimension] | None = None,
    force_reanalysis: bool = False,
) -> dict[str, Any]:
    """
    Analyze a call across multiple dimensions.
    This is a higher-level function that analyzes all requested dimensions.

    Args:
        call_id: Call UUID
        dimensions: List of dimensions to analyze (default: all)
        force_reanalysis: Bypass cache

    Returns:
        Dict mapping dimension to analysis results
    """
    # Default to all dimensions
    if dimensions is None:
        dimensions = list(CoachingDimension)

    logger.info(
        f"Analyzing call {call_id} across {len(dimensions)} dimensions: "
        f"{[d.value for d in dimensions]}"
    )

    # Get call and transcript
    call = fetch_one("SELECT * FROM calls WHERE id = %s", (str(call_id),), as_dict=True)
    if not call or not isinstance(call, dict):
        raise ValueError(f"Call {call_id} not found")

    # Get transcript segments
    segments = fetch_one(
        """
        SELECT STRING_AGG(text, ' ' ORDER BY sequence_number) as full_transcript
        FROM transcripts
        WHERE call_id = %s
        """,
        (str(call_id),),
        as_dict=True,
    )

    if not segments or not isinstance(segments, dict) or not segments.get("full_transcript"):
        raise ValueError(f"No transcript found for call {call_id}")

    transcript = segments["full_transcript"]

    # Get primary rep (company_side = true speaker with most talk time)
    rep = fetch_one(
        """
        SELECT * FROM speakers
        WHERE call_id = %s
        AND company_side = true
        ORDER BY talk_time_seconds DESC NULLS LAST
        LIMIT 1
        """,
        (str(call_id),),
        as_dict=True,
    )

    if not rep or not isinstance(rep, dict) or "id" not in rep:
        raise ValueError(f"No company rep found for call {call_id}")

    rep_id = rep["id"]

    # Analyze each dimension
    # TODO: Phase 4 - Implement parallel execution with Prefect tasks
    results = {}
    for dimension in dimensions:
        session = get_or_create_coaching_session(
            call_id=call_id,
            rep_id=UUID(rep_id),
            dimension=dimension,
            transcript=transcript,
            force_reanalysis=force_reanalysis,
        )
        results[dimension.value] = session

    logger.info(f"Completed analysis for call {call_id}")

    return {
        "call_id": str(call_id),
        "call_title": call.get("title"),
        "rep_name": rep.get("name"),
        "dimensions_analyzed": [d.value for d in dimensions],
        "results": results,
    }


def _run_claude_analysis(
    call_id: str,
    dimension: CoachingDimension,
    transcript: str,
    call_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run actual Claude API analysis for a coaching dimension.

    Args:
        call_id: Call UUID for role detection
        dimension: Coaching dimension to analyze
        transcript: Full call transcript
        call_metadata: Optional call metadata for context

    Returns:
        Analysis result with scores, strengths, areas for improvement, etc.
    """
    logger.info(f"Running Claude analysis for dimension: {dimension.value}")

    # Detect speaker role for role-aware rubric selection
    speaker_role = detect_speaker_role(call_id)
    logger.info(f"Using {speaker_role.upper()} rubric for call {call_id}")

    # Load role-specific rubric
    try:
        role_rubric = load_rubric(speaker_role)
    except Exception as e:
        logger.warning(f"Failed to load role rubric for {speaker_role}, falling back to AE: {e}")
        role_rubric = load_rubric("ae")

    # Get dimension-specific rubric from database (legacy system)
    rubric_row = fetch_one(
        """
        SELECT id, name, version, category, criteria, scoring_guide, examples
        FROM coaching_rubrics
        WHERE category = %s AND active = true
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (dimension.value,),
        as_dict=True,
    )

    if not rubric_row or not isinstance(rubric_row, dict):
        raise ValueError(f"No active rubric found for dimension: {dimension.value}")

    rubric = {
        "name": rubric_row["name"],
        "version": rubric_row["version"],
        "category": rubric_row["category"],
        "criteria": rubric_row["criteria"],
        "scoring_guide": rubric_row["scoring_guide"],
        "examples": rubric_row.get("examples", {}),
        "role_rubric": role_rubric,  # Add role-specific rubric context
        "evaluated_as_role": speaker_role,  # Track which role was used
    }

    # Get knowledge base if needed for product_knowledge dimension
    knowledge_base = None
    if dimension == CoachingDimension.PRODUCT_KNOWLEDGE:
        kb_rows = fetch_all(
            """
            SELECT product, category, content
            FROM knowledge_base
            ORDER BY product, category
            """
        )

        if kb_rows:
            knowledge_base = "\n\n".join(
                [
                    f"## {row['product'].upper()} - {row['category'].title()}\n{row['content']}"
                    for row in kb_rows
                    if isinstance(row, dict)
                    and "product" in row
                    and "category" in row
                    and "content" in row
                ]
            )
        else:
            knowledge_base = "No product knowledge base loaded."

    # Generate prompt using appropriate template
    messages = _generate_prompt_for_dimension(
        dimension=dimension,
        transcript=transcript,
        rubric=rubric,
        knowledge_base=knowledge_base,
        call_metadata=call_metadata,
    )

    # Call Claude API with prompt caching
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,  # Increased for complex discovery analysis with SPICED/Challenger/Sandler
            temperature=0.3,
            messages=messages,  # type: ignore[arg-type]
        )

        # Extract usage statistics
        usage = response.usage
        tokens_used = usage.input_tokens + usage.output_tokens
        cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0)
        cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0)

        logger.info(
            f"Claude API call successful: "
            f"input={usage.input_tokens}, output={usage.output_tokens}, "
            f"cache_creation={cache_creation_tokens}, cache_read={cache_read_tokens}"
        )

        # Parse response content
        content_block = response.content[0]
        if not hasattr(content_block, "text"):
            raise ValueError(f"Expected TextBlock but got {type(content_block)}")
        response_text = content_block.text

        # Try to parse as JSON (structured output)
        try:
            analysis_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback: extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                try:
                    analysis_data = json.loads(json_str)
                except json.JSONDecodeError as e2:
                    logger.error(f"Failed to parse extracted JSON: {str(e2)}")
                    logger.error(f"Response preview: {response_text[:1000]}...")
                    logger.error(f"Response end: ...{response_text[-500:]}")
                    raise ValueError(f"Claude response JSON is malformed: {str(e2)}") from e2
            else:
                logger.error(
                    f"No JSON code block found. Response preview: {response_text[:1000]}..."
                )
                logger.error(f"Response end: ...{response_text[-500:]}")
                raise ValueError(f"Claude response is not valid JSON: {str(e)}") from e

        # Add metadata including role used for evaluation
        analysis_data["metadata"] = {
            "model": "claude-sonnet-4-5-20250929",
            "tokens_used": tokens_used,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cache_creation_tokens": cache_creation_tokens,
            "cache_read_tokens": cache_read_tokens,
            "rubric_version": rubric["version"],
            "rubric_role": rubric.get(
                "evaluated_as_role", "ae"
            ),  # Track which role rubric was used
        }

        return dict(analysis_data)

    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        raise RuntimeError(f"Claude API call failed: {e}") from e


def _generate_prompt_for_dimension(
    dimension: CoachingDimension,
    transcript: str,
    rubric: dict[str, Any],
    knowledge_base: str | None = None,
    call_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate prompt messages for a specific dimension using appropriate template.

    Args:
        dimension: Coaching dimension
        transcript: Call transcript
        rubric: Rubric data from database
        knowledge_base: Optional knowledge base content (for product_knowledge)
        call_metadata: Optional call metadata

    Returns:
        List of message dicts formatted for Claude API
    """
    if dimension == CoachingDimension.PRODUCT_KNOWLEDGE:
        if not knowledge_base:
            raise ValueError("Knowledge base required for product_knowledge analysis")
        return analyze_product_knowledge_prompt(
            transcript=transcript,
            rubric=rubric,
            knowledge_base=knowledge_base,
            call_metadata=call_metadata,
        )
    elif dimension == CoachingDimension.DISCOVERY:
        return analyze_discovery_prompt(
            transcript=transcript,
            rubric=rubric,
            call_metadata=call_metadata,
        )
    elif dimension == CoachingDimension.OBJECTION_HANDLING:
        return analyze_objection_handling_prompt(
            transcript=transcript,
            rubric=rubric,
            call_metadata=call_metadata,
        )
    elif dimension == CoachingDimension.ENGAGEMENT:
        return analyze_engagement_prompt(
            transcript=transcript,
            rubric=rubric,
            call_metadata=call_metadata,
        )
    else:
        raise ValueError(f"Unsupported dimension: {dimension.value}")
