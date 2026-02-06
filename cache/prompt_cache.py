"""
Prompt caching optimization for Claude API.
Reduces token costs by 90% for repeated content (rubrics, knowledge base).

Claude Prompt Caching:
- Caches system prompts and large context blocks
- 5-minute TTL per cache entry
- Drastically reduces input token costs for repeated content
- Especially effective for rubrics and knowledge base (rarely change)

Cache Blocks:
1. Role-specific rubric (AE/SE/CSM) - changes quarterly
2. Knowledge base content - changes monthly
3. Dimension-specific scoring guide - changes rarely

Reference: https://docs.anthropic.com/claude/docs/prompt-caching
"""
import logging
from typing import Any

from db.models import CoachingDimension

logger = logging.getLogger(__name__)


class PromptCacheManager:
    """
    Manages prompt caching for Claude API calls.

    Caches static content that rarely changes:
    - Rubrics (quarterly updates)
    - Knowledge base (monthly updates)
    - Scoring guides (rare updates)

    This reduces token costs by 90% for cached content.
    """

    def __init__(self):
        """Initialize prompt cache manager."""
        self._cache_enabled = True
        logger.info("Prompt caching enabled for Claude API")

    def build_cached_system_prompt(
        self,
        dimension: CoachingDimension,
        rubric: dict[str, Any],
        knowledge_base: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Build system prompt with cache control markers.

        Cache strategy:
        1. General coaching instructions (cacheable)
        2. Role-specific rubric (cacheable - changes quarterly)
        3. Knowledge base if needed (cacheable - changes monthly)
        4. Dimension-specific criteria (cacheable - changes rarely)

        Args:
            dimension: Coaching dimension being analyzed
            rubric: Rubric data with role-specific context
            knowledge_base: Optional product knowledge base

        Returns:
            List of message blocks with cache control
        """
        messages = []

        # Block 1: General coaching instructions (always cached)
        general_instructions = self._build_general_instructions(dimension)
        messages.append({
            "type": "text",
            "text": general_instructions,
            "cache_control": {"type": "ephemeral"}
        })

        # Block 2: Role-specific rubric (cached - changes quarterly)
        if rubric.get("role_rubric"):
            role_rubric_text = self._format_role_rubric(
                rubric["role_rubric"],
                rubric.get("evaluated_as_role", "ae")
            )
            messages.append({
                "type": "text",
                "text": role_rubric_text,
                "cache_control": {"type": "ephemeral"}
            })

        # Block 3: Knowledge base (cached - changes monthly)
        if knowledge_base and dimension == CoachingDimension.PRODUCT_KNOWLEDGE:
            messages.append({
                "type": "text",
                "text": f"# Product Knowledge Base\n\n{knowledge_base}",
                "cache_control": {"type": "ephemeral"}
            })

        # Block 4: Dimension-specific criteria (cached - rare changes)
        criteria_text = self._format_dimension_criteria(dimension, rubric)
        messages.append({
            "type": "text",
            "text": criteria_text,
            "cache_control": {"type": "ephemeral"}
        })

        logger.debug(
            f"Built cached system prompt with {len(messages)} blocks "
            f"for dimension={dimension.value}"
        )

        return messages

    def build_user_prompt(
        self,
        transcript: str,
        call_metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Build user prompt with call transcript.
        This is NOT cached as it changes per call.

        Args:
            transcript: Call transcript
            call_metadata: Optional call metadata

        Returns:
            Formatted user prompt
        """
        prompt = "# Call Transcript\n\n"

        if call_metadata:
            prompt += "## Call Metadata\n"
            prompt += f"- Title: {call_metadata.get('title', 'N/A')}\n"
            prompt += f"- Duration: {call_metadata.get('duration_seconds', 0) / 60:.1f} minutes\n"
            prompt += f"- Type: {call_metadata.get('call_type', 'N/A')}\n"
            prompt += f"- Product: {call_metadata.get('product', 'N/A')}\n\n"

        prompt += "## Transcript\n\n"
        prompt += transcript

        prompt += "\n\n# Task\n\n"
        prompt += (
            "Analyze this call transcript according to the coaching rubric provided. "
            "Return your analysis as a JSON object with the following structure:\n"
            "{\n"
            '  "score": <0-100>,\n'
            '  "strengths": [<list of specific strengths with examples>],\n'
            '  "areas_for_improvement": [<list of specific areas with examples>],\n'
            '  "specific_examples": {\n'
            '    "good": [<positive examples from transcript>],\n'
            '    "needs_work": [<examples needing improvement>]\n'
            "  },\n"
            '  "action_items": [<concrete, actionable recommendations>],\n'
            '  "full_analysis": "<comprehensive narrative analysis>"\n'
            "}\n"
        )

        return prompt

    def _build_general_instructions(self, dimension: CoachingDimension) -> str:
        """Build general coaching instructions."""
        return f"""# Sales Coaching Agent - {dimension.value.replace('_', ' ').title()} Analysis

You are an expert sales coach analyzing call transcripts to provide actionable coaching insights.
Your goal is to help sales professionals improve their skills through specific, constructive feedback.

## Analysis Principles

1. Be specific: Always reference exact quotes from the transcript
2. Be constructive: Frame feedback as opportunities for growth
3. Be actionable: Provide concrete steps for improvement
4. Be fair: Acknowledge both strengths and areas for development
5. Be consistent: Apply the rubric criteria uniformly

## Role Context

The rubric provided is tailored for specific sales roles (AE, SE, CSM).
Apply role-appropriate expectations when evaluating performance.
"""

    def _format_role_rubric(self, role_rubric: dict[str, Any], role: str) -> str:
        """Format role-specific rubric for caching."""
        rubric_text = f"# Role-Specific Rubric: {role.upper()}\n\n"
        rubric_text += f"**Role**: {role_rubric.get('role_name', role.upper())}\n"
        rubric_text += f"**Description**: {role_rubric.get('description', '')}\n\n"

        if role_rubric.get("key_responsibilities"):
            rubric_text += "## Key Responsibilities\n\n"
            for resp in role_rubric["key_responsibilities"]:
                rubric_text += f"- {resp}\n"
            rubric_text += "\n"

        if role_rubric.get("coaching_focus"):
            rubric_text += "## Coaching Focus Areas\n\n"
            for focus in role_rubric["coaching_focus"]:
                rubric_text += f"- {focus}\n"
            rubric_text += "\n"

        return rubric_text

    def _format_dimension_criteria(
        self,
        dimension: CoachingDimension,
        rubric: dict[str, Any],
    ) -> str:
        """Format dimension-specific criteria for caching."""
        criteria_text = f"# {dimension.value.replace('_', ' ').title()} Evaluation Criteria\n\n"

        criteria_text += f"**Rubric Version**: {rubric.get('version', 'N/A')}\n"
        criteria_text += f"**Category**: {rubric.get('category', 'N/A')}\n\n"

        if rubric.get("criteria"):
            criteria_text += "## Evaluation Criteria\n\n"
            criteria_obj = rubric["criteria"]
            if isinstance(criteria_obj, dict):
                for key, value in criteria_obj.items():
                    criteria_text += f"### {key}\n{value}\n\n"
            else:
                criteria_text += f"{criteria_obj}\n\n"

        if rubric.get("scoring_guide"):
            criteria_text += "## Scoring Guide\n\n"
            scoring = rubric["scoring_guide"]
            if isinstance(scoring, dict):
                for score_range, description in scoring.items():
                    criteria_text += f"**{score_range}**: {description}\n"
            else:
                criteria_text += f"{scoring}\n"
            criteria_text += "\n"

        if rubric.get("examples"):
            criteria_text += "## Examples\n\n"
            examples = rubric["examples"]
            if isinstance(examples, dict):
                for category, example_list in examples.items():
                    criteria_text += f"### {category}\n"
                    if isinstance(example_list, list):
                        for ex in example_list:
                            criteria_text += f"- {ex}\n"
                    else:
                        criteria_text += f"{example_list}\n"
                    criteria_text += "\n"

        return criteria_text

    def format_cached_messages(
        self,
        dimension: CoachingDimension,
        transcript: str,
        rubric: dict[str, Any],
        knowledge_base: str | None = None,
        call_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Format complete message array with prompt caching.

        This is the main entry point for building Claude API messages
        with optimal caching strategy.

        Args:
            dimension: Coaching dimension
            transcript: Call transcript
            rubric: Rubric data
            knowledge_base: Optional knowledge base
            call_metadata: Optional call metadata

        Returns:
            List of messages formatted for Claude API
        """
        # Build cached system content
        system_content = self.build_cached_system_prompt(
            dimension=dimension,
            rubric=rubric,
            knowledge_base=knowledge_base,
        )

        # Build user prompt (not cached)
        user_prompt = self.build_user_prompt(
            transcript=transcript,
            call_metadata=call_metadata,
        )

        # Return message array in Claude API format
        return [
            {
                "role": "user",
                "content": system_content + [
                    {"type": "text", "text": user_prompt}
                ]
            }
        ]

    def estimate_cache_savings(
        self,
        rubric_size_tokens: int = 2000,
        knowledge_base_size_tokens: int = 5000,
        calls_per_day: int = 20,
    ) -> dict[str, Any]:
        """
        Estimate token and cost savings from prompt caching.

        Assumptions:
        - Rubric: ~2K tokens (cached)
        - Knowledge base: ~5K tokens (cached)
        - Cache hit rate: 95% (5-min TTL, frequent analysis)
        - Cost: $0.003/K input tokens (normal), $0.0003/K (cached)

        Args:
            rubric_size_tokens: Size of rubric in tokens
            knowledge_base_size_tokens: Size of KB in tokens
            calls_per_day: Number of calls analyzed per day

        Returns:
            Dict with savings estimates
        """
        cached_tokens_per_call = rubric_size_tokens + knowledge_base_size_tokens
        cache_hit_rate = 0.95  # 95% hit rate with 5-min TTL

        # Calculate monthly volume
        calls_per_month = calls_per_day * 30
        total_cached_tokens = cached_tokens_per_call * calls_per_month

        # Calculate costs
        # Without caching: all tokens at full price
        cost_without_caching = (total_cached_tokens / 1000) * 0.003

        # With caching: 5% at full price, 95% at cache price
        full_price_tokens = total_cached_tokens * (1 - cache_hit_rate)
        cached_tokens = total_cached_tokens * cache_hit_rate
        cost_with_caching = (
            (full_price_tokens / 1000) * 0.003 +
            (cached_tokens / 1000) * 0.0003
        )

        savings = cost_without_caching - cost_with_caching
        savings_pct = (savings / cost_without_caching) * 100 if cost_without_caching > 0 else 0

        return {
            "calls_per_month": calls_per_month,
            "cached_tokens_per_call": cached_tokens_per_call,
            "total_cached_tokens_monthly": total_cached_tokens,
            "cache_hit_rate": cache_hit_rate,
            "cost_without_caching": round(cost_without_caching, 2),
            "cost_with_caching": round(cost_with_caching, 2),
            "monthly_savings": round(savings, 2),
            "savings_percentage": round(savings_pct, 1),
        }
