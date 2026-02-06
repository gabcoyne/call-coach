"""
Product knowledge analysis prompt template.
Evaluates technical accuracy and ability to connect features to business value.
"""

from typing import Any


def analyze_product_knowledge_prompt(
    transcript: str,
    rubric: dict[str, Any],
    knowledge_base: str,
    call_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate Claude API messages for product knowledge analysis.

    Args:
        transcript: Full call transcript
        rubric: Product knowledge rubric from database
        knowledge_base: Product documentation and competitive positioning
        call_metadata: Optional call metadata (title, participants, etc.)

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

    # System prompt with rubric (cacheable)
    system_prompt = f"""You are an expert sales coach analyzing a call for product knowledge quality.

Your task is to evaluate how well the sales representative demonstrates product knowledge based on the rubric below.
{role_context}
## PRODUCT KNOWLEDGE RUBRIC v{rubric['version']}

{_format_rubric(rubric)}

## SCORING GUIDE

{_format_scoring_guide(rubric['scoring_guide'])}

## PRODUCT KNOWLEDGE BASE

{knowledge_base}

## EVALUATION CRITERIA

{_format_criteria(rubric['criteria'])}

## OUTPUT REQUIREMENTS

Provide a structured analysis in JSON format:

{{
  "score": <integer 0-100>,
  "strengths": [
    "<specific strength with evidence>",
    "<another strength>"
  ],
  "areas_for_improvement": [
    "<specific area with evidence>",
    "<another area>"
  ],
  "specific_examples": {{
    "good": [
      {{
        "timestamp_start": <seconds into call>,
        "timestamp_end": <seconds into call>,
        "exchange_summary": "<1-2 sentence summary of multi-turn dialogue showing effective product knowledge>",
        "impact": "<why this exchange demonstrates strong product knowledge>"
      }}
    ],
    "needs_work": [
      {{
        "timestamp_start": <seconds into call>,
        "timestamp_end": <seconds into call>,
        "exchange_summary": "<1-2 sentence summary of multi-turn dialogue showing gap in product knowledge>",
        "impact": "<why this exchange needs improvement and how to fix>"
      }}
    ]
  }},
  "action_items": [
    "<specific, actionable recommendation>",
    "<another recommendation>"
  ],
  "technical_accuracy": {{
    "correct_statements": [
      {{
        "timestamp_start": <seconds>,
        "timestamp_end": <seconds>,
        "exchange_summary": "<summary of accurate technical explanation>",
        "validation": "<why this is correct per knowledge base>"
      }}
    ],
    "inaccurate_statements": [
      {{
        "timestamp_start": <seconds>,
        "timestamp_end": <seconds>,
        "exchange_summary": "<summary of inaccurate statement or explanation>",
        "issue": "<what's wrong>",
        "correction": "<what should have been said>"
      }}
    ],
    "missed_opportunities": [
      {{
        "timestamp_start": <seconds>,
        "timestamp_end": <seconds>,
        "context": "<summary of when this came up>",
        "missed_point": "<what wasn't mentioned>",
        "suggestion": "<what should have been said>"
      }}
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

1. **Technical Accuracy** (35%): Verify every product claim against the knowledge base
   - Flag any misstatements or unclear explanations
   - Note missed opportunities to provide technical depth
   - Validate competitive positioning claims

2. **Feature-to-Value Connection** (30%): Assess how well features are connected to business outcomes
   - Look for quantified impact (time saved, cost reduction, etc.)
   - Check if customer-specific examples are used
   - Evaluate if value is tailored to this customer's needs

3. **Competitive Positioning** (25%): Evaluate competitive differentiation
   - Accuracy of competitor comparisons
   - Focus on relevant differentiators for this customer
   - Appropriate acknowledgment of competitor strengths

4. **Use Case Relevance** (10%): Relevance of examples provided
   - Similar customer examples
   - Industry/tech stack alignment

5. **5 Wins Coverage** - Score each win 0-100 based on product knowledge quality:
   - **Technical Win** (25%): Deep technical knowledge demonstrated - use cases, infrastructure, CI/CD, POC scoping
   - **Business Win** (35%): Product value connected to business outcomes, ROI articulated
   - **Security Win** (15%): InfoSec requirements addressed, security features explained accurately
   - **Commercial Win** (15%): Scope and pricing discussed with product knowledge
   - **Legal Win** (10%): Contract terms, compliance requirements explained

Be specific in your feedback. Quote exact statements from the transcript and explain why they're effective or need improvement."""

    # User prompt with transcript (not cacheable - varies per call)
    call_context = ""
    if call_metadata:
        call_context = f"""
## CALL CONTEXT

- Title: {call_metadata.get('title', 'N/A')}
- Duration: {call_metadata.get('duration_seconds', 0) // 60} minutes
- Participants: {', '.join([p.get('name', 'Unknown') for p in call_metadata.get('participants', [])])}
"""

    user_prompt = f"""{call_context}

## CALL TRANSCRIPT

{transcript}

---

Please analyze this call for product knowledge quality according to the rubric above. Focus on technical accuracy, feature-to-value connection, competitive positioning, and use case relevance. Provide specific quotes and actionable coaching."""

    # Return messages with cache control
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},  # Cache rubric + knowledge base
                },
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
Category: {rubric['category']}

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
