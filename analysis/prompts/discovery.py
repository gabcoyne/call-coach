"""
Discovery quality analysis prompt template.
Evaluates question quality, active listening, and MEDDIC coverage.
"""
from typing import Any


def analyze_discovery_prompt(
    transcript: str,
    rubric: dict[str, Any],
    call_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Generate Claude API messages for discovery quality analysis.

    Args:
        transcript: Full call transcript
        rubric: Discovery rubric from database
        call_metadata: Optional call metadata

    Returns:
        List of message dicts for Claude API (with cache control)
    """
    system_prompt = f"""You are an expert sales coach analyzing a call for discovery quality.

Your task is to evaluate how well the sales representative conducts discovery based on the rubric below.

## DISCOVERY QUALITY RUBRIC v{rubric['version']}

{_format_rubric(rubric)}

## SCORING GUIDE

{_format_scoring_guide(rubric['scoring_guide'])}

## EVALUATION CRITERIA

{_format_criteria(rubric['criteria'])}

## 5 WINS FRAMEWORK

The 5 Wins elements to assess:
{_format_five_wins(rubric['criteria'].get('five_wins_coverage', {}))}

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
        "analysis": "<why this was effective discovery>"
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
  "talk_listen_metrics": {{
    "rep_talk_percentage": <estimated percentage>,
    "customer_talk_percentage": <estimated percentage>,
    "assessment": "<whether ratio is appropriate for discovery call>"
  }},
  "question_breakdown": {{
    "open_ended_count": <count>,
    "closed_count": <count>,
    "follow_up_count": <count>,
    "quality_assessment": "<overall question quality>"
  }},
  "spiced_assessment": {{
    "situation_covered": <boolean>,
    "situation_notes": "<context established before diving into pain>",
    "pain_covered": <boolean>,
    "pain_depth": "<surface-level | moderate | deep exploration>",
    "impact_quantified": <boolean>,
    "impact_calculation": "<formula used: e.g., 2 FTEs × $200K = $400K/year + delayed projects>",
    "critical_event_identified": <boolean>,
    "critical_event": "<what's the real deadline and what happens if missed>",
    "decision_process_mapped": <boolean>,
    "decision_notes": "<stakeholders, criteria, timeline>"
  }},
  "challenger_assessment": {{
    "teaching_moments_count": <count>,
    "teaching_examples": [
      {{"insight": "<what new perspective did rep bring>", "quote": "<exact quote>"}}
    ],
    "tailoring_score": <0-100>,
    "tailoring_notes": "<how well message adapted to specific stakeholders>",
    "control_score": <0-100>,
    "control_notes": "<comfort with money talk, pressing for commitments>",
    "customer_verifiers_used": <count>
  }},
  "sandler_assessment": {{
    "qualification_discipline": <boolean>,
    "discipline_notes": "<did rep follow Pain-Budget-Decision order or jump to presentation?>",
    "pain_before_budget": <boolean>,
    "budget_before_decision": <boolean>,
    "decision_before_presentation": <boolean>,
    "premature_demo_offered": <boolean>,
    "se_time_protected": <boolean>,
    "earned_right_to_present": <boolean>,
    "red_flags": ["<any discipline violations, e.g., 'offered demo before qualifying pain'>"]
  }},
  "full_analysis": "<comprehensive 2-3 paragraph analysis incorporating SPICED, Challenger, and Sandler frameworks>"
}}

## EVALUATION INSTRUCTIONS

This rubric incorporates SPICED (Situation-Pain-Impact-Critical Event-Decision), Challenger Sale (Teach-Tailor-Take Control), and Sandler Submarine (Pain-Budget-Decision discipline) methodologies.

1. **Question Quality & Teaching** (35%): Assess questions AND teaching ability (Challenger Sale)
   - **SPICED Discovery**: Does rep uncover Situation, Pain, AND quantified Impact (not just Pain)?
   - **Challenger Teaching**: Does rep bring insights customer hasn't considered? (e.g., hidden Airflow costs, scalability limits)
   - **Impact Quantification**: Does rep convert Pain to dollars/time? (Research: Impact-focused reps sold 53% more)
   - **Critical Event**: Does rep identify real business deadline driving urgency (not just seller's quarter-end)?
   - Count open-ended vs. closed questions, note teaching moments where rep reframed customer thinking

2. **Active Listening** (25%): Look for evidence of listening
   - Rep references customer's specific statements
   - Paraphrasing to confirm understanding
   - Building on customer's responses
   - Not interrupting or talking over customer

3. **Impact Quantification & Critical Events** (30%): SPICED methodology assessment
   - **Impact**: Did rep quantify business outcomes? (Cost of problem + Opportunity cost of not solving)
     - Formula: Current Pain × Time/Cost × Opportunity Lost = Total Impact
     - Example: "40% of 5 engineers = 2 FTEs = $400K/year + delayed strategic projects"
   - **Critical Event**: What's the real deadline? What happens if they DON'T solve this by [date]?
   - **Situation Context**: Full understanding of current state before jumping to solutions
   - **Pain Depth**: Emotional + rational business issues explored thoroughly

4. **Tailoring & Control** (20%): Challenger Sale "Tailor & Take Control"
   - **Tailoring**: Does rep adapt message for different stakeholders? (CTO vs VP Eng vs InfoSec)
   - **Take Control**: Is rep comfortable discussing money, pressing for commitments, guiding conversation?
   - **Challenger Moments**: Does rep challenge customer assumptions or reframe objections with insights?
   - **Customer Verifiers**: Does rep check resonance? ("Does that align with your priorities?")

5. **Sandler Discipline** (15%): Qualification before presentation
   - **Pain-Budget-Decision Order**: Does rep qualify Pain deeply before Budget, Budget before Decision?
   - **No Premature Demos**: Does rep resist jumping to features/demos before qualification?
   - **Earning Right to Present**: Does rep validate opportunity before committing SE time?
   - **Red Flags**: Offering demos/POCs before Pain/Budget/Decision are qualified wastes SE time

6. **5 Wins Coverage** - Score each win 0-100 based on discovery depth:
   - **Business Win** (35%): SPICED Situation-Pain-Impact-Critical Event-Decision + Business Case strength
   - **Technical Win** (25%): Technical discovery (BUT only after Business Pain qualified - Sandler discipline)
   - **Security Win** (15%): InfoSec requirements (often the Critical Event driving timeline)
   - **Commercial Win** (15%): Scope, budget discussion (Challenger: be comfortable with money talk)
   - **Legal Win** (10%): Legal/procurement process (part of Decision mapping)

7. **Talk-Listen Ratio** (20%): Discovery calls should be 60-70% customer talking

## COACHING FOCUS AREAS

**SPICED Impact Questions:**
- "What's this costing you?" (quantify Pain)
- "What can't you do because of this problem?" (opportunity cost)
- "If this were solved, what becomes possible?" (positive Impact outcomes)
- "What happens if you DON'T solve this by [date]?" (Critical Event consequences)

**Challenger Teaching Moments:**
- Bring data: "Most teams at your scale hit this wall around 800 DAGs..."
- Reframe assumptions: "You're thinking this is a maintenance problem, but it's actually a revenue problem..."
- Challenge status quo: "Have you calculated the hidden costs of self-hosting?"

**Sandler Qualification Discipline:**
- Don't jump to demo until Pain is fully explored and quantified (Impact)
- Validate Budget exists before building custom proposals or involving SE
- Map complete Decision process before committing to POCs
- Rep should say: "Before we dive into technical details, let's make sure we're solving the right problem..."

Be specific. Quote exact questions, teaching moments, and qualification discipline (or lack thereof)."""

    call_context = ""
    if call_metadata:
        call_context = f"""
## CALL CONTEXT

- Title: {call_metadata.get('title', 'N/A')}
- Duration: {call_metadata.get('duration_seconds', 0) // 60} minutes
- Call Type: Discovery
"""

    user_prompt = f"""{call_context}

## CALL TRANSCRIPT

{transcript}

---

Please analyze this call for discovery quality. Focus on question effectiveness, active listening, MEDDIC coverage, and talk-listen ratio. Provide specific quotes and actionable coaching."""

    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                },
                {
                    "type": "text",
                    "text": user_prompt,
                }
            ]
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
        if criterion == 'five_wins_coverage':
            continue  # Handle separately
        weight = details.get('weight', 0)
        description = details.get('description', '')
        lines.append(f"### {criterion.replace('_', ' ').title()} ({weight}%)")
        lines.append(f"{description}\n")
    return "\n".join(lines)


def _format_five_wins(five_wins_criteria: dict[str, Any]) -> str:
    """Format 5 Wins framework with all wins and their components."""
    if not five_wins_criteria:
        return "Standard 5 Wins framework elements"

    wins = five_wins_criteria.get('wins', {})
    if not wins:
        # Fallback to simple elements format
        elements = five_wins_criteria.get('elements', {})
        lines = []
        for element, description in elements.items():
            lines.append(f"- **{element.replace('_', ' ').title()}**: {description}")
        return "\n".join(lines)

    lines = []
    for win_name, win_details in wins.items():
        weight = win_details.get('weight', 0)
        lines.append(f"\n### {win_name.replace('_', ' ').title()} ({weight}%)")

        components = win_details.get('components', {})
        for component_name, component_value in components.items():
            component_title = component_name.replace('_', ' ').title()

            if isinstance(component_value, dict):
                # Nested sub-components (e.g., business_discovery, technical_discovery)
                lines.append(f"\n**{component_title}:**")
                for sub_name, sub_desc in component_value.items():
                    lines.append(f"- {sub_name.replace('_', ' ').title()}: {sub_desc}")
            else:
                # Simple component description
                lines.append(f"- **{component_title}**: {component_value}")

        lines.append("")

    return "\n".join(lines)
