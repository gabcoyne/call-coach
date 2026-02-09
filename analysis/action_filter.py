"""
Action Item Filtering Module

Filters coaching action items to show only concrete, specific, actionable next steps.
Removes vague recommendations like "build a repository" or "practice more".
"""

import re

# Patterns that indicate vague, non-actionable advice
VAGUE_PATTERNS = [
    r"build.*repository",
    r"build.*library",
    r"practice.*framework",
    r"practice.*regularly",
    r"study.*methodology",
    r"learn more about",
    r"improve.*overall",
    r"work on.*general",
    r"focus on.*better",
    r"try to.*more",
    r"should.*always",
    r"need to.*more",
]

# Patterns that indicate concrete, actionable advice
CONCRETE_INDICATORS = [
    r"before next call",  # Time-bound
    r"before \[date\]",
    r"by \[date\]",
    r"ask.*specific question",  # Example provided
    r"prepare.*for \[name\]",  # Named stakeholder
    r"send.*by",  # Deadline
    r"schedule.*with",  # Specific action
    r"review.*\[document\]",  # Named artifact
    r"\d+ (minutes|days|hours)",  # Quantified
    r"next time.*when",  # Conditional action
    r"in the.*call",  # Call-specific
]


def filter_actionable_items(
    action_items: list[str],
    min_score: int = 60,
    max_items: int = 7,
) -> list[str]:
    """
    Filter action items for specificity and actionability.

    Criteria for concrete action items:
    - Contains specific WHO, WHAT, WHEN, or WHERE
    - Avoids generic verbs (practice, study, work on)
    - Has measurable outcome or clear completion state
    - References call context or specific examples

    Args:
        action_items: List of raw action items from analysis
        min_score: Minimum actionability score (0-100) to include
        max_items: Maximum number of items to return

    Returns:
        Filtered list of concrete action items, prioritized by score
    """
    if not action_items:
        return []

    scored_items: list[tuple[str, int]] = []

    for item in action_items:
        score = _score_actionability(item)
        if score >= min_score:
            scored_items.append((item, score))

    # Sort by score (descending)
    scored_items.sort(key=lambda x: x[1], reverse=True)

    # Take top N items
    filtered = [item for item, score in scored_items[:max_items]]

    return filtered


def _score_actionability(action_item: str) -> int:
    """
    Score an action item's actionability (0-100).

    Higher scores = more concrete, specific, actionable.

    Args:
        action_item: Action item text

    Returns:
        Actionability score (0-100)
    """
    score = 50  # Start at neutral

    item_lower = action_item.lower()

    # Penalty: Contains vague patterns (-30 points)
    for pattern in VAGUE_PATTERNS:
        if re.search(pattern, item_lower):
            score -= 30
            break  # Only apply penalty once

    # Bonus: Contains concrete indicators (+10 points each, max +40)
    concrete_matches = 0
    for pattern in CONCRETE_INDICATORS:
        if re.search(pattern, item_lower):
            concrete_matches += 1

    score += min(40, concrete_matches * 10)

    # Bonus: Mentions specific names/entities (+10 points)
    # Look for capitalized words (likely names) or bracketed placeholders
    if re.search(r"\[[\w\s]+\]", action_item) or re.search(
        r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", action_item
    ):
        score += 10

    # Bonus: Contains numbers/quantification (+10 points)
    if re.search(r"\d+", action_item):
        score += 10

    # Bonus: Contains specific verbs (not generic) (+10 points)
    specific_verbs = [
        r"\bprepare\b",
        r"\breview\b",
        r"\bschedule\b",
        r"\bsend\b",
        r"\bconfirm\b",
        r"\bfollow up\b",
        r"\bshare\b",
        r"\bdocument\b",
    ]
    for verb in specific_verbs:
        if re.search(verb, item_lower):
            score += 10
            break

    # Bonus: Reasonable length (20-150 chars) (+5 points)
    length = len(action_item)
    if 20 <= length <= 150:
        score += 5
    elif length < 20:
        score -= 10  # Too short, likely vague
    elif length > 200:
        score -= 5  # Too long, likely unfocused

    # Penalty: Contains generic coaching advice (-20 points)
    generic_coaching = [
        r"be more",
        r"be better",
        r"improve your",
        r"work on your",
        r"focus on being",
        r"remember to",
    ]
    for pattern in generic_coaching:
        if re.search(pattern, item_lower):
            score -= 20
            break

    # Clamp score to 0-100
    return max(0, min(100, score))


def categorize_action_items(
    action_items: list[str],
) -> dict[str, list[str]]:
    """
    Categorize action items by type for better organization.

    Categories:
    - Pre-call prep: Things to do before next call
    - During call: Techniques to apply in conversations
    - Post-call follow-up: Actions after the call

    Args:
        action_items: List of action items

    Returns:
        Dictionary of categorized items
    """
    categories: dict[str, list[str]] = {
        "pre_call": [],
        "during_call": [],
        "post_call": [],
        "general": [],
    }

    pre_call_keywords = [
        "before next call",
        "prepare",
        "research",
        "review",
        "study",
        "practice",
    ]
    during_call_keywords = [
        "next time",
        "in the call",
        "when speaking",
        "ask",
        "listen for",
        "probe",
    ]
    post_call_keywords = [
        "after the call",
        "follow up",
        "send",
        "document",
        "share",
        "debrief",
    ]

    for item in action_items:
        item_lower = item.lower()

        if any(kw in item_lower for kw in pre_call_keywords):
            categories["pre_call"].append(item)
        elif any(kw in item_lower for kw in during_call_keywords):
            categories["during_call"].append(item)
        elif any(kw in item_lower for kw in post_call_keywords):
            categories["post_call"].append(item)
        else:
            categories["general"].append(item)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}
