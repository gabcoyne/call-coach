"""
Objection handling analysis prompt template.
Evaluates identification, acknowledgment, response quality, and resolution.
"""

from typing import Any


def analyze_objection_handling_prompt(
    transcript: str,
    rubric: dict[str, Any],
    call_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate Claude API messages for objection handling analysis.

    Args:
        transcript: Full call transcript
        rubric: Objection handling rubric from database
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

    system_prompt = f"""You are an expert sales coach analyzing a call for objection handling quality.

Your task is to evaluate how well the sales representative handles customer objections based on the rubric below.
{role_context}
## OBJECTION HANDLING RUBRIC v{rubric['version']}

{_format_rubric(rubric)}

## SCORING GUIDE

{_format_scoring_guide(rubric['scoring_guide'])}

## EVALUATION CRITERIA

{_format_criteria(rubric['criteria'])}

## COMMON OBJECTIONS & STRONG RESPONSES

{_format_common_objections(rubric.get('common_objections', {}))}

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
        "timestamp_start": <seconds>,
        "timestamp_end": <seconds>,
        "exchange_summary": "<1-2 sentence summary of multi-turn objection handling dialogue>",
        "impact": "<why this exchange demonstrates effective objection handling>"
      }}
    ],
    "needs_work": [
      {{
        "timestamp_start": <seconds>,
        "timestamp_end": <seconds>,
        "exchange_summary": "<1-2 sentence summary of multi-turn objection handling dialogue>",
        "impact": "<why this exchange needs improvement>"
      }}
    ]
  }},
  "action_items": [
    "<specific, actionable recommendation>"
  ],
  "objection_breakdown": {{
    "total_objections_identified": <count>,
    "objections_by_type": {{
      "pricing": <count>,
      "timing": <count>,
      "technical_fit": <count>,
      "competitive": <count>,
      "other": <count>
    }},
    "objections_resolved": <count>,
    "objections_unresolved": <count>
  }},
  "handling_analysis": {{
    "identification_score": <0-100>,
    "acknowledgment_score": <0-100>,
    "response_quality_score": <0-100>,
    "resolution_score": <0-100>,
    "patterns": [
      "<observed pattern in how objections were handled>"
    ]
  }},
  "five_wins_coverage": {{
    "business_win": {{
      "covered": <boolean>,
      "score": <0-100>,
      "business_discovery": {{
        "current_state_and_problems": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "future_state_and_outcomes": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "success_metrics": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "executive_priorities": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "evaluation_and_decision": {{"covered": <boolean>, "notes": "<brief assessment>"}}
      }},
      "business_case": {{"covered": <boolean>, "notes": "<assessment of business case strength>"}}
    }},
    "technical_win": {{
      "covered": <boolean>,
      "score": <0-100>,
      "technical_discovery": {{
        "technical_requirements": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "use_case_alignment": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "infrastructure_requirements": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "ci_cd_requirements": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "other_requirements": {{"covered": <boolean>, "notes": "<brief assessment>"}}
      }},
      "demo_solution_presentation": {{"planned": <boolean>, "notes": "<assessment>"}},
      "poc_scoping_and_poc": {{"discussed": <boolean>, "notes": "<assessment>"}}
    }},
    "security_win": {{
      "covered": <boolean>,
      "score": <0-100>,
      "infosec_discovery": {{
        "infosec_requirements": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "infosec_process_and_timeline": {{"covered": <boolean>, "notes": "<brief assessment>"}},
        "questionnaire": {{"discussed": <boolean>, "notes": "<assessment>"}}
      }}
    }},
    "commercial_win": {{
      "covered": <boolean>,
      "score": <0-100>,
      "scoping_discovery": {{"covered": <boolean>, "notes": "<assessment of scope discussion>"}}
    }},
    "legal_win": {{
      "covered": <boolean>,
      "score": <0-100>,
      "legal_discovery": {{"covered": <boolean>, "notes": "<assessment of legal discussion>"}}
    }},
    "wins_count": <number of wins with >50 score>,
    "overall_assessment": "<which wins are strong, which need work>"
  }},
  "full_analysis": "<comprehensive 2-3 paragraph analysis>"
}}

## EVALUATION INSTRUCTIONS

1. **Objection Identification** (20%): Recognize and surface objections
   - Did rep identify both explicit and implicit objections?
   - Were proactive questions asked to surface concerns?
   - Did rep distinguish between real blockers and smokescreens?
   - Quote specific examples of objections (explicit and missed implicit ones)

2. **Acknowledgment & Empathy** (25%): Validate concerns before responding
   - Did rep acknowledge the objection as valid?
   - Was empathy shown ("I understand why that's important")?
   - Did rep paraphrase to confirm understanding?
   - Or did rep dismiss, minimize, or interrupt?

3. **Response Quality** (35%): Effectiveness of objection response
   - Did rep provide specific evidence (data, case studies, demos)?
   - Was the root concern addressed, not just surface objection?
   - Were responses tailored to this customer's situation?
   - Did rep use social proof from similar customers?
   - Or were responses generic, vague, or defensive?

4. **Resolution Confirmation** (20%): Confirm objection is resolved
   - Did rep check for understanding ("Does that address your concern?")?
   - Was alignment ensured before proceeding?
   - Did rep ask if additional concerns exist?
   - Or did rep assume resolution without confirmation?

5. **5 Wins Coverage** - Score each win 0-100 based on objection handling quality:
   - **Business Win** (35%): Business case objections handled effectively (ROI concerns, budget objections)
   - **Technical Win** (25%): Technical fit objections addressed with depth (integration concerns, requirements gaps)
   - **Security Win** (15%): Security/compliance objections resolved (InfoSec concerns, data privacy)
   - **Commercial Win** (15%): Pricing/scope objections navigated (cost concerns, contract terms)
   - **Legal Win** (10%): Legal/procurement objections managed (contract requirements, approval process)

Categorize each objection by type (pricing, timing, technical_fit, competitive, other) and assess whether it was resolved. Be specific - quote the objection, the response, and explain why it was effective or needs work."""

    call_context = ""
    if call_metadata:
        call_context = f"""
## CALL CONTEXT

- Title: {call_metadata.get('title', 'N/A')}
- Duration: {call_metadata.get('duration_seconds', 0) // 60} minutes
- Call Type: {call_metadata.get('call_type', 'N/A')}
"""

    user_prompt = f"""{call_context}

## CALL TRANSCRIPT

{transcript}

---

Please analyze this call for objection handling quality. Identify all objections (explicit and implicit), categorize them by type, and evaluate how effectively they were handled. Provide specific quotes and actionable coaching."""

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


def _format_common_objections(common_objections: dict[str, Any]) -> str:
    """Format common objections and strong responses."""
    if not common_objections:
        return "Standard objection handling framework"

    lines = []
    for objection_type, details in common_objections.items():
        lines.append(f"### {objection_type.replace('_', ' ').title()}")

        if "examples" in details:
            lines.append("\n**Common examples:**")
            for example in details["examples"]:
                lines.append(f"- {example}")

        if "strong_responses" in details:
            lines.append("\n**Strong response patterns:**")
            for response in details["strong_responses"]:
                lines.append(f"- {response}")

        lines.append("")

    return "\n".join(lines)
