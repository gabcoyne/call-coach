"""
Engagement analysis prompt template.
Evaluates rapport building, talk-listen ratio, energy, and customer engagement.
"""

from typing import Any


def analyze_engagement_prompt(
    transcript: str,
    rubric: dict[str, Any],
    call_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate Claude API messages for engagement analysis.

    Args:
        transcript: Full call transcript
        rubric: Engagement rubric from database
        call_metadata: Optional call metadata

    Returns:
        List of message dicts for Claude API (with cache control)
    """
    # Extract role-specific context if available
    role_context = ""
    if "role_rubric" in rubric and "evaluated_as_role" in rubric:
        role_name = rubric["role_rubric"].get("role_name", "Account Executive")
        role_desc = rubric["role_rubric"].get("description", "")
        role_context = f"""
## ROLE-SPECIFIC EVALUATION CONTEXT

This call is being evaluated using the **{role_name}** rubric.

{role_desc}

The evaluation criteria and scoring have been tailored to reflect the responsibilities and success metrics specific to this role.
"""

    system_prompt = f"""You are an expert sales coach analyzing a call for overall engagement quality.

Your task is to evaluate the quality of interaction, rapport, energy, and customer engagement based on the rubric below.
{role_context}
## ENGAGEMENT RUBRIC v{rubric['version']}

{_format_rubric(rubric)}

## SCORING GUIDE

{_format_scoring_guide(rubric['scoring_guide'])}

## EVALUATION CRITERIA

{_format_criteria(rubric['criteria'])}

## CALL STRUCTURE BEST PRACTICES

{_format_call_structure(rubric.get('call_structure', {}))}

## ANTI-PATTERNS TO AVOID

{_format_anti_patterns(rubric.get('anti_patterns', {}))}

## OUTPUT REQUIREMENTS

Provide a structured analysis in JSON format:

{{
  "score": <integer 0-100>,
  "strengths": [
    "<specific strength with evidence>"
  ],
  "areas_for_improvement": [
    "<specific area with evidence>"
  ],
  "specific_examples": {{
    "good": [
      {{
        "quote": "<exact quote from transcript>",
        "timestamp": <seconds>,
        "analysis": "<why this was effective engagement>"
      }}
    ],
    "needs_work": [
      {{
        "quote": "<exact quote from transcript>",
        "timestamp": <seconds>,
        "analysis": "<why this needs improvement>"
      }}
    ]
  }},
  "action_items": [
    "<specific, actionable recommendation>"
  ],
  "engagement_metrics": {{
    "rapport_score": <0-100>,
    "talk_listen_ratio": {{
      "rep_percentage": <estimated percentage>,
      "customer_percentage": <estimated percentage>,
      "assessment": "<whether ratio is appropriate for call type>",
      "longest_rep_monologue_seconds": <estimated duration>
    }},
    "energy_score": <0-100>,
    "customer_engagement_score": <0-100>
  }},
  "customer_signals": {{
    "positive_signals": [
      "<quote or description of positive engagement signal>"
    ],
    "negative_signals": [
      "<quote or description of negative engagement signal>"
    ]
  }},
  "anti_patterns_observed": [
    {{
      "pattern": "<monologuing|interrupting|filler_words|reading_script>",
      "evidence": "<specific quote or description>",
      "impact": "<how this affected engagement>"
    }}
  ],
  "call_structure_assessment": {{
    "opening_quality": "<assessment of opening>",
    "closing_quality": "<assessment of closing>",
    "transition_quality": "<assessment of transitions between topics>"
  }},
  "full_analysis": "<comprehensive 2-3 paragraph analysis>"
}}

## EVALUATION INSTRUCTIONS

1. **Rapport Building** (25%): Connection and trust with customer
   - Did rep find common ground or shared interests?
   - Was customer's name used naturally?
   - Were previous interactions or research referenced?
   - Did rep show genuine curiosity about customer's business?
   - Was appropriate humor or personality displayed?
   - Or was the interaction overly formal, robotic, or impersonal?

2. **Talk-Listen Ratio** (30%): Balance of speaking time
   - Estimate percentage of time rep vs. customer spoke
   - Compare to targets for call type:
     - Discovery: Rep 30-40%, Customer 60-70%
     - Demo: Rep 50-60%, Customer 40-50%
     - Technical Deep Dive: Rep 40-50%, Customer 50-60%
   - Did customer speak in substantial blocks (not just yes/no)?
   - Was there back-and-forth dialogue vs. monologue?
   - Identify longest rep monologue (concerning if >2 minutes)

3. **Energy & Enthusiasm** (20%): Rep's energy level
   - Was tone upbeat and positive?
   - Did rep demonstrate genuine excitement?
   - Did rep match or slightly elevate customer's energy?
   - Was energy maintained throughout call?
   - Or was delivery monotone, low energy, or sounded scripted?

4. **Customer Engagement Signals** (25%): Customer's participation level
   - **Positive signals**: Questions asked, volunteered information, referenced use cases, suggested next steps, introduced stakeholders
   - **Negative signals**: One-word answers, long silences, multitasking, vague responses, asked to reschedule
   - Quote specific examples of engagement or disengagement

Assess the call opening (agenda setting, objective clarity) and closing (summarization, next steps, follow-up confirmation). Identify any anti-patterns (monologuing, interrupting, excessive filler words, reading script). Be specific with timestamps and quotes."""

    call_context = ""
    if call_metadata:
        call_type = call_metadata.get("call_type", "unknown")
        call_context = f"""
## CALL CONTEXT

- Title: {call_metadata.get('title', 'N/A')}
- Duration: {call_metadata.get('duration_seconds', 0) // 60} minutes
- Call Type: {call_type}
- Expected Talk-Listen Ratio: {_get_target_ratio(call_type)}
"""

    user_prompt = f"""{call_context}

## CALL TRANSCRIPT

{transcript}

---

Please analyze this call for engagement quality. Focus on rapport building, talk-listen ratio, energy level, and customer engagement signals. Identify the call structure (opening/closing quality) and any anti-patterns. Provide specific quotes and actionable coaching."""

    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}},
                {
                    "type": "text",
                    "text": user_prompt,
                },
            ],
        }
    ]


def _format_rubric(rubric: dict[str, Any]) -> str:
    """Format rubric header."""
    return f"""**{rubric['name']}**
Version: {rubric['version']}

{rubric.get('description', '')}"""


def _format_scoring_guide(scoring_guide: dict[str, Any]) -> str:
    """Format scoring guide."""
    lines = []
    for score_range, description in scoring_guide.items():
        lines.append(f"- **{score_range}**: {description}")
    return "\n".join(lines)


def _format_criteria(criteria: dict[str, Any]) -> str:
    """Format evaluation criteria."""
    lines = []
    for criterion, details in criteria.items():
        weight = details.get("weight", 0)
        description = details.get("description", "")
        lines.append(f"### {criterion.replace('_', ' ').title()} ({weight}%)")
        lines.append(f"{description}\n")

        # Handle talk_listen_ratio targets
        if "targets" in details:
            lines.append("**Target ratios by call type:**")
            for call_type, target in details["targets"].items():
                lines.append(f"- {call_type.replace('_', ' ').title()}: {target}")
            lines.append("")

        # Handle customer_engagement_signals lists
        if "positive_signals" in details:
            lines.append("**Positive signals:**")
            for signal in details["positive_signals"]:
                lines.append(f"- {signal}")
            lines.append("")

        if "negative_signals" in details:
            lines.append("**Negative signals:**")
            for signal in details["negative_signals"]:
                lines.append(f"- {signal}")
            lines.append("")

        # Handle standard indicators
        if "indicators" in details:
            indicators = details["indicators"]
            if "excellent" in indicators:
                lines.append("**Excellent indicators:**")
                for indicator in indicators["excellent"]:
                    lines.append(f"- {indicator}")
                lines.append("")

            if "poor" in indicators:
                lines.append("**Poor indicators:**")
                for indicator in indicators["poor"]:
                    lines.append(f"- {indicator}")
                lines.append("")

    return "\n".join(lines)


def _format_call_structure(call_structure: dict[str, Any]) -> str:
    """Format call structure best practices."""
    if not call_structure:
        return "Standard call structure practices"

    lines = []

    if "strong_opening" in call_structure:
        lines.append("### Strong Opening")
        for practice in call_structure["strong_opening"]:
            lines.append(f"- {practice}")
        lines.append("")

    if "strong_closing" in call_structure:
        lines.append("### Strong Closing")
        for practice in call_structure["strong_closing"]:
            lines.append(f"- {practice}")
        lines.append("")

    return "\n".join(lines)


def _format_anti_patterns(anti_patterns: dict[str, Any]) -> str:
    """Format anti-patterns to watch for."""
    if not anti_patterns:
        return "Watch for common engagement anti-patterns"

    lines = []
    for pattern_name, details in anti_patterns.items():
        lines.append(f"### {pattern_name.replace('_', ' ').title()}")
        lines.append(f"**Issue**: {details.get('description', '')}")
        lines.append(f"**Fix**: {details.get('fix', '')}")
        lines.append("")

    return "\n".join(lines)


def _get_target_ratio(call_type: str) -> str:
    """Get target talk-listen ratio for call type."""
    ratios = {
        "discovery": "Rep 30-40%, Customer 60-70%",
        "demo": "Rep 50-60%, Customer 40-50%",
        "technical_deep_dive": "Rep 40-50%, Customer 50-60%",
    }
    return ratios.get(call_type.lower(), "Balanced conversation")
