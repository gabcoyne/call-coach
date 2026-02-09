"""
Thematic Grouping Module

Groups coaching insights by theme rather than by dimension to reduce overwhelming granularity.
Preserves prompt caching by operating as post-processing layer after analysis completes.
"""

from typing import Any

# Theme taxonomy with keyword matching and dimension mapping
THEME_TAXONOMY = {
    "Discovery & Qualification": {
        "keywords": [
            "question",
            "pain",
            "impact",
            "SPICED",
            "discovery",
            "qualification",
            "requirements",
            "use case",
            "criteria",
        ],
        "dimensions": ["discovery"],
        "priority": 1,  # Highest priority theme
    },
    "Technical Knowledge": {
        "keywords": [
            "product",
            "feature",
            "technical",
            "architecture",
            "capability",
            "functionality",
            "integration",
            "API",
        ],
        "dimensions": ["product_knowledge"],
        "priority": 2,
    },
    "Engagement & Communication": {
        "keywords": [
            "listening",
            "rapport",
            "energy",
            "talk-listen",
            "engagement",
            "communication",
            "relationship",
            "enthusiasm",
        ],
        "dimensions": ["engagement"],
        "priority": 3,
    },
    "Objection Handling": {
        "keywords": [
            "objection",
            "concern",
            "reframe",
            "address",
            "pushback",
            "hesitation",
            "risk",
            "challenge",
        ],
        "dimensions": ["objection_handling"],
        "priority": 4,
    },
}


def _score_insight_for_theme(insight: str, theme_config: dict[str, Any]) -> int:
    """
    Score how well an insight matches a theme based on keyword frequency.

    Args:
        insight: The strength or improvement text
        theme_config: Theme configuration with keywords

    Returns:
        Score (0-100) indicating match quality
    """
    insight_lower = insight.lower()
    keyword_matches = sum(1 for kw in theme_config["keywords"] if kw in insight_lower)

    # Score based on keyword density
    words = len(insight.split())
    if words == 0:
        return 0

    # Normalize: (matches / total_words) * 100, capped at 100
    score = min(100, int((keyword_matches / words) * 1000))

    return score


def group_insights_by_theme(
    all_strengths: list[str],
    all_improvements: list[str],
    dimension_details: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """
    Group insights into thematic categories using keyword matching and dimension mapping.

    Args:
        all_strengths: Aggregated strengths from all dimensions
        all_improvements: Aggregated improvements from all dimensions
        dimension_details: Dimension-specific analysis results

    Returns:
        Dictionary of themes with grouped insights:
        {
            "Technical Knowledge": {
                "strengths": [...],
                "improvements": [...],
                "count": 5,
                "priority": 2
            },
            ...
        }
    """
    # Initialize theme groups
    themed_insights: dict[str, dict[str, Any]] = {}
    for theme_name, config in THEME_TAXONOMY.items():
        themed_insights[theme_name] = {
            "strengths": [],
            "improvements": [],
            "count": 0,
            "priority": config["priority"],
        }

    # First pass: Assign insights based on dimension mapping
    for dim_name in dimension_details:
        dim_data = dimension_details[dim_name]
        if not isinstance(dim_data, dict):
            continue

        # Find matching theme for this dimension
        matching_theme = None
        for theme_name, config in THEME_TAXONOMY.items():
            if dim_name in config["dimensions"]:
                matching_theme = theme_name
                break

        if matching_theme:
            # Extract strengths and improvements from dimension
            dim_strengths = dim_data.get("strengths", [])
            dim_improvements = dim_data.get("improvements", []) or dim_data.get(
                "needs_improvement", []
            )

            if isinstance(dim_strengths, list):
                themed_insights[matching_theme]["strengths"].extend(dim_strengths)

            if isinstance(dim_improvements, list):
                themed_insights[matching_theme]["improvements"].extend(dim_improvements)

    # Second pass: Use keyword matching for unassigned insights from aggregated lists
    # (This handles cases where insights weren't assigned by dimension)
    assigned_strengths = {s for theme in themed_insights.values() for s in theme["strengths"]}
    assigned_improvements = {i for theme in themed_insights.values() for i in theme["improvements"]}

    for strength in all_strengths:
        if strength not in assigned_strengths:
            # Find best matching theme
            best_theme = None
            best_score = 0
            for theme_name, config in THEME_TAXONOMY.items():
                score = _score_insight_for_theme(strength, config)
                if score > best_score:
                    best_score = score
                    best_theme = theme_name

            if best_theme and best_score > 20:  # Threshold for assignment
                themed_insights[best_theme]["strengths"].append(strength)

    for improvement in all_improvements:
        if improvement not in assigned_improvements:
            # Find best matching theme
            best_theme = None
            best_score = 0
            for theme_name, config in THEME_TAXONOMY.items():
                score = _score_insight_for_theme(improvement, config)
                if score > best_score:
                    best_score = score
                    best_theme = theme_name

            if best_theme and best_score > 20:  # Threshold for assignment
                themed_insights[best_theme]["improvements"].append(improvement)

    # Third pass: Deduplicate similar insights within each theme
    for theme_name in themed_insights:
        themed_insights[theme_name]["strengths"] = _deduplicate_insights(
            themed_insights[theme_name]["strengths"]
        )
        themed_insights[theme_name]["improvements"] = _deduplicate_insights(
            themed_insights[theme_name]["improvements"]
        )

        # Update count
        themed_insights[theme_name]["count"] = len(themed_insights[theme_name]["strengths"]) + len(
            themed_insights[theme_name]["improvements"]
        )

    # Filter out empty themes
    themed_insights = {theme: data for theme, data in themed_insights.items() if data["count"] > 0}

    # Sort by priority (lower number = higher priority)
    themed_insights = dict(sorted(themed_insights.items(), key=lambda x: x[1]["priority"]))

    return themed_insights


def _deduplicate_insights(insights: list[str]) -> list[str]:
    """
    Remove duplicate or very similar insights from a list.

    Args:
        insights: List of insight strings

    Returns:
        Deduplicated list maintaining order
    """
    if not insights:
        return []

    seen: list[str] = []
    deduplicated = []

    for insight in insights:
        # Normalize for comparison
        normalized = insight.lower().strip()

        # Check if very similar to any seen insight
        is_duplicate = False
        for seen_insight in seen:
            # Simple similarity: if 80%+ of words overlap, consider duplicate
            insight_words = set(normalized.split())
            seen_words = set(seen_insight.split())

            if not insight_words or not seen_words:
                continue

            overlap = len(insight_words & seen_words)
            similarity = overlap / max(len(insight_words), len(seen_words))

            if similarity > 0.8:
                is_duplicate = True
                break

        if not is_duplicate:
            seen.append(normalized)
            deduplicated.append(insight)

    return deduplicated
