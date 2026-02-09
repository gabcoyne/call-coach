"""
Key Moments Extraction Module

Transforms verbose specific examples into concise, impactful key moments.
Limits to top 10 most important moments to reduce overwhelming detail.
"""

from typing import Any


def extract_key_moments(
    dimension_details: dict[str, Any],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Transform specific_examples into concise key moments.

    Algorithm:
    1. Parse all good/needs_work examples across dimensions
    2. Score impact (timestamp diversity, dimension importance, insight quality)
    3. Deduplicate similar moments (same timestamp ±30s)
    4. Select top N most impactful
    5. Format as: {timestamp, moment_type, summary}

    Args:
        dimension_details: Dimension-specific analysis results
        limit: Maximum number of moments to return (default 10)

    Returns:
        List of key moments sorted chronologically:
        [
            {
                "timestamp": 125,  # seconds
                "moment_type": "strength",  # or "improvement"
                "summary": "Asked clarifying question about deployment architecture",
                "dimension": "discovery"
            },
            ...
        ]
    """
    # Dimension weights (higher = more important)
    dimension_weights = {
        "discovery": 4,
        "product_knowledge": 3,
        "objection_handling": 2,
        "engagement": 1,
    }

    raw_moments: list[dict[str, Any]] = []

    # Extract moments from each dimension
    for dim_name, dim_data in dimension_details.items():
        if not isinstance(dim_data, dict):
            continue

        dim_weight = dimension_weights.get(dim_name, 1)

        # Extract from specific_examples if available
        specific_examples = dim_data.get("specific_examples", {})
        if isinstance(specific_examples, dict):
            # Good examples (strengths)
            good_examples = specific_examples.get("good", [])
            if isinstance(good_examples, list):
                for example in good_examples:
                    if isinstance(example, dict):
                        moment = _parse_example_to_moment(example, "strength", dim_name, dim_weight)
                        if moment:
                            raw_moments.append(moment)

            # Needs work examples (improvements)
            needs_work = specific_examples.get("needs_work", [])
            if isinstance(needs_work, list):
                for example in needs_work:
                    if isinstance(example, dict):
                        moment = _parse_example_to_moment(
                            example, "improvement", dim_name, dim_weight
                        )
                        if moment:
                            raw_moments.append(moment)

    # If no moments found, return empty list
    if not raw_moments:
        return []

    # Score each moment
    for moment in raw_moments:
        moment["score"] = _score_moment(moment, raw_moments)

    # Deduplicate moments that are too close in time
    deduplicated = _deduplicate_by_timestamp(raw_moments, threshold_seconds=30)

    # Sort by score and take top N
    top_moments = sorted(deduplicated, key=lambda m: m["score"], reverse=True)[:limit]

    # Sort final list chronologically
    top_moments_sorted = sorted(top_moments, key=lambda m: m["timestamp"])

    # Remove score from final output (internal only)
    for moment in top_moments_sorted:
        moment.pop("score", None)

    return top_moments_sorted


def _parse_example_to_moment(
    example: dict[str, Any],
    moment_type: str,
    dimension: str,
    dim_weight: int,
) -> dict[str, Any] | None:
    """
    Parse a specific example into a key moment.

    Args:
        example: Raw example from dimension analysis
        moment_type: "strength" or "improvement"
        dimension: Source dimension name
        dim_weight: Dimension importance weight

    Returns:
        Moment dict or None if invalid
    """
    timestamp = example.get("timestamp")
    if timestamp is None:
        return None

    # Try to extract a concise summary
    summary = None

    # Priority 1: Use 'analysis' field (most concise)
    if "analysis" in example and example["analysis"]:
        summary = example["analysis"]

    # Priority 2: Use 'quote' field but truncate if too long
    elif "quote" in example and example["quote"]:
        quote = example["quote"]
        if len(quote) > 150:
            summary = quote[:147] + "..."
        else:
            summary = quote

    # Priority 3: Use any other text field
    else:
        for key in ["notes", "description", "text"]:
            if key in example and example[key]:
                text = example[key]
                if len(text) > 150:
                    summary = text[:147] + "..."
                else:
                    summary = text
                break

    if not summary:
        return None

    return {
        "timestamp": int(timestamp),
        "moment_type": moment_type,
        "summary": summary.strip(),
        "dimension": dimension,
        "dim_weight": dim_weight,
    }


def _score_moment(moment: dict[str, Any], all_moments: list[dict[str, Any]]) -> float:
    """
    Score a moment's impact based on multiple factors.

    Scoring factors:
    - Dimension weight (discovery > product > objection > engagement)
    - Timestamp diversity (penalize clustering)
    - Insight quality (length, specificity)
    - Sentiment balance (mix of positive/negative)

    Args:
        moment: Moment to score
        all_moments: All moments for context (used for diversity calculation)

    Returns:
        Impact score (0-100)
    """
    score = 0.0

    # Factor 1: Dimension weight (0-40 points)
    score += moment["dim_weight"] * 10

    # Factor 2: Timestamp diversity (0-30 points)
    # Penalize if many moments are clustered near this timestamp
    timestamp = moment["timestamp"]
    nearby_count = sum(
        1 for m in all_moments if abs(m["timestamp"] - timestamp) < 60  # Within 1 minute
    )
    diversity_score = max(0, 30 - (nearby_count * 5))
    score += diversity_score

    # Factor 3: Insight quality (0-20 points)
    # Longer, more specific summaries score higher
    summary_length = len(moment["summary"])
    if summary_length > 100:
        score += 20
    elif summary_length > 50:
        score += 15
    elif summary_length > 20:
        score += 10
    else:
        score += 5

    # Factor 4: Sentiment type (0-10 points)
    # Slight boost for improvements (actionable)
    if moment["moment_type"] == "improvement":
        score += 5

    return score


def _deduplicate_by_timestamp(
    moments: list[dict[str, Any]], threshold_seconds: int = 30
) -> list[dict[str, Any]]:
    """
    Remove moments that are too close in time (likely duplicates).

    Args:
        moments: List of moments
        threshold_seconds: Time window for deduplication

    Returns:
        Deduplicated list
    """
    if not moments:
        return []

    # Sort by timestamp
    sorted_moments = sorted(moments, key=lambda m: m["timestamp"])

    deduplicated = [sorted_moments[0]]

    for moment in sorted_moments[1:]:
        # Check if this moment is too close to the last kept moment
        last_timestamp = deduplicated[-1]["timestamp"]
        if abs(moment["timestamp"] - last_timestamp) > threshold_seconds:
            deduplicated.append(moment)
        else:
            # Keep the higher-scored moment
            if moment.get("score", 0) > deduplicated[-1].get("score", 0):
                deduplicated[-1] = moment

    return deduplicated


def format_timestamp(seconds: int) -> str:
    """
    Format seconds as MM:SS.

    Args:
        seconds: Timestamp in seconds

    Returns:
        Formatted string like "12:34"
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"
