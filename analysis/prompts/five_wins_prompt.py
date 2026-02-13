"""
Five Wins Unified Prompt - Methodology-Free Coaching Analysis

This prompt evaluates calls against the Five Wins framework WITHOUT mentioning
any sales methodology jargon (SPICED, Challenger, Sandler, MEDDIC).

Key principles:
1. Focus on exit criteria, not process
2. Reference specific call moments with timestamps
3. Generate ONE actionable recommendation
4. Keep narrative to 2-3 sentences
"""

from typing import Any

from analysis.rubrics.five_wins_unified import (
    FIVE_WINS_UNIFIED,
    get_primary_win_for_call_type,
    get_secondary_wins_for_call_type,
)


def analyze_five_wins_prompt(
    transcript: str,
    call_type: str = "discovery",
    call_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate Claude API messages for Five Wins coaching analysis.

    This prompt produces structured JSON output with:
    - Five Wins evaluation (business, technical, security, commercial, legal)
    - 2-3 sentence narrative summary
    - ONE primary action item with timestamp reference
    - Key moments from the call

    Args:
        transcript: Full call transcript
        call_type: Type of call (discovery, demo, etc.)
        call_metadata: Optional call metadata

    Returns:
        List of message dicts for Claude API
    """
    # Determine primary and secondary wins for this call type
    primary_win = get_primary_win_for_call_type(call_type)  # type: ignore
    secondary_wins = get_secondary_wins_for_call_type(call_type)  # type: ignore

    # Build the wins definitions section
    wins_definitions = _format_wins_definitions()

    # Build call context
    call_context = ""
    if call_metadata:
        call_context = f"""
## Call Context

- Title: {call_metadata.get('title', 'N/A')}
- Duration: {call_metadata.get('duration_seconds', 0) // 60} minutes
- Call Type: {call_type.replace('_', ' ').title()}
"""

    system_prompt = f"""You are a sales coach evaluating a call for Prefect Cloud.

Your job is to assess progress toward the Five Wins and provide ONE actionable recommendation.

## The Five Wins Framework

Every deal requires securing five wins. Your evaluation should assess progress toward each.

{wins_definitions}

## This Call's Context

- Call Type: {call_type.replace('_', ' ').title()}
- Primary Win to Advance: {FIVE_WINS_UNIFIED[primary_win]['name']}
- Secondary Wins to Seed: {', '.join(FIVE_WINS_UNIFIED[w]['name'] for w in secondary_wins) or 'None'}

## Evaluation Instructions

For each win, assess:
1. What discovery was completed toward exit criteria?
2. What specific progress was made?
3. What's blocking this win from being secured?

Then provide:
1. A 2-3 sentence narrative summary (what went well, what's at risk)
2. ONE specific action for the rep before their next call

## Output Format

Respond with valid JSON matching this schema:

{{
  "five_wins_evaluation": {{
    "business": {{
      "score": <0-35>,
      "exit_criteria_met": <boolean>,
      "discovery_complete": <boolean>,
      "blockers": ["<specific blocker>"],
      "evidence": ["<quote or moment supporting score>"],
      "champion": {{
        "identified": <boolean>,
        "name": "<name if known>",
        "incentive_clear": <boolean>,
        "influence_confirmed": <boolean>,
        "information_flowing": <boolean>
      }},
      "budget_confirmed": <boolean>,
      "exec_sponsor_engaged": <boolean>,
      "business_case_strength": "<weak|moderate|strong>"
    }},
    "technical": {{
      "score": <0-25>,
      "exit_criteria_met": <boolean>,
      "discovery_complete": <boolean>,
      "blockers": ["<specific blocker>"],
      "evidence": ["<quote or moment supporting score>"],
      "vendor_of_choice_confirmed": <boolean>,
      "poc_scoped": <boolean>,
      "poc_success_criteria_defined": <boolean>
    }},
    "security": {{
      "score": <0-15>,
      "exit_criteria_met": <boolean>,
      "discovery_complete": <boolean>,
      "blockers": ["<specific blocker>"],
      "evidence": ["<quote or moment supporting score>"],
      "infosec_timeline_known": <boolean>,
      "trust_portal_shared": <boolean>,
      "architecture_review_scheduled": <boolean>
    }},
    "commercial": {{
      "score": <0-15>,
      "exit_criteria_met": <boolean>,
      "discovery_complete": <boolean>,
      "blockers": ["<specific blocker>"],
      "evidence": ["<quote or moment supporting score>"],
      "exec_sponsor_aligned": <boolean>,
      "scope_agreed": <boolean>,
      "pricing_discussed": <boolean>
    }},
    "legal": {{
      "score": <0-10>,
      "exit_criteria_met": <boolean>,
      "discovery_complete": <boolean>,
      "blockers": ["<specific blocker>"],
      "evidence": ["<quote or moment supporting score>"],
      "terms_impact_discussed": <boolean>,
      "legal_timeline_known": <boolean>,
      "redlines_in_progress": <boolean>
    }}
  }},
  "narrative": "<2-3 sentence summary: what went well, what's at risk, net assessment>",
  "wins_addressed": {{
    "<win_name>": "<what was accomplished>"
  }},
  "wins_missed": {{
    "<win_name>": "<what was missed or needs work>"
  }},
  "primary_action": {{
    "win": "<which win this relates to>",
    "action": "<specific instruction: exactly what to do/say before next call>",
    "context": "<why this matters, what happened in the call>",
    "related_moment": {{
      "timestamp_seconds": <seconds into call>,
      "speaker": "<who was speaking>",
      "summary": "<what happened at this moment>"
    }}
  }},
  "key_moments": [
    {{
      "timestamp_seconds": <seconds>,
      "speaker": "<speaker>",
      "summary": "<what happened and why it matters>"
    }}
  ]
}}

## Important Guidelines

- NEVER mention sales methodologies by name (SPICED, Challenger, Sandler, MEDDIC, Spin, etc.)
- Focus on the Five Wins exit criteria - what does the rep need to secure this deal?
- Reference specific moments from the call with timestamps (seconds from start)
- Make the action item specific enough that the rep knows exactly what to say/do
- The action should be one thing they can prepare BEFORE their next call
- Narrative should be 2-3 sentences maximum, no platitudes
- Scores must sum to 100 max (Business 35, Technical 25, Security 15, Commercial 15, Legal 10)
"""

    user_prompt = f"""{call_context}

## Call Transcript

{transcript}

---

Evaluate this {call_type.replace('_', ' ')} call for Five Wins progress.

The rep should be primarily advancing: {FIVE_WINS_UNIFIED[primary_win]['name']}

Provide your evaluation in the specified JSON format. Remember:
- ONE primary action item only (the most important thing)
- Reference specific timestamps from the call
- No methodology jargon - focus on exit criteria
- Narrative is 2-3 sentences max"""

    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "text",
                    "text": user_prompt,
                },
            ],
        }
    ]


def _format_wins_definitions() -> str:
    """Format the Five Wins definitions for the prompt."""
    lines: list[str] = []

    for win_data in FIVE_WINS_UNIFIED.values():
        lines.append(f"### {win_data['name']} ({win_data['weight']}%)")
        lines.append(f"\n**Exit Criteria:** {win_data['exit_criteria']}")
        lines.append("\n**What good looks like:**")
        for item in win_data["what_good_looks_like"]:
            lines.append(f"- {item}")

        # Add coaching focus
        lines.append(f"\n**Coaching focus:** {win_data['coaching_focus']}")
        lines.append("")

    return "\n".join(lines)
