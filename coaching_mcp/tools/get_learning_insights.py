"""
MCP tool for getting learning insights from top performers.
"""
import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from analysis.learning_insights import get_learning_insights

logger = logging.getLogger(__name__)


def register_learning_insights_tool(server: Server):
    """Register the get_learning_insights MCP tool."""

    @server.call_tool()
    async def get_learning_insights_tool(arguments: dict[str, Any]) -> list[TextContent]:
        """
        Get learning insights by comparing rep to top performers on closed-won deals.

        This tool shows:
        - How the rep's performance compares to top performers
        - Specific behavioral differences with examples
        - Concrete call moments from top performers (with timestamps)
        - Actionable patterns to learn from

        Args:
            arguments: Dict with rep_email and focus_area

        Returns:
            List of TextContent with comparative analysis
        """
        rep_email = arguments.get("rep_email")
        focus_area = arguments.get("focus_area", "discovery")

        if not rep_email:
            return [TextContent(type="text", text="Error: rep_email is required")]

        valid_focus_areas = ["discovery", "objections", "product_knowledge", "rapport", "next_steps"]
        if focus_area not in valid_focus_areas:
            return [
                TextContent(
                    type="text",
                    text=f"Error: focus_area must be one of: {', '.join(valid_focus_areas)}",
                )
            ]

        try:
            insights = get_learning_insights(rep_email, focus_area)

            if "error" in insights:
                return [TextContent(type="text", text=f"Error: {insights['error']}")]

            # Format response
            response = f"""# Learning Insights: {rep_email}

**Focus Area:** {focus_area}

---

## Performance Comparison

**{rep_email}'s Performance:**
- Opportunities: {insights['rep_performance']['opportunities']}
- Calls Analyzed: {insights['rep_performance']['calls']}
- Average Score: {insights['rep_performance']['average_score']}

**Top Performers (Closed Won):**
- Opportunities: {insights['top_performer_benchmark']['opportunities']}
- Calls Analyzed: {insights['top_performer_benchmark']['calls']}
- Average Score: {insights['top_performer_benchmark']['average_score']}

---

## What Top Performers Do Differently

{insights['behavioral_differences']}

---

## Exemplar Call Moments

"""

            for exemplar in insights.get("exemplar_moments", []):
                response += f"""
### {exemplar['opportunity_name']} (Score: {exemplar['score']})

**Date:** {exemplar['call_date']}

**What They Did:**
{exemplar['what_they_did']}

**Transcript Excerpt:**
{exemplar['transcript_excerpt']}

---
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting learning insights for {rep_email}: {e}", exc_info=True)
            return [TextContent(type="text", text=f"Error getting learning insights: {str(e)}")]


# Tool definition for MCP registration
GET_LEARNING_INSIGHTS_TOOL = Tool(
    name="get_learning_insights",
    description=(
        "Compare a rep's performance to top performers on closed-won deals. "
        "Shows specific behavioral differences with concrete examples from successful calls. "
        "Focus areas: discovery, objections, product_knowledge, rapport, next_steps."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "rep_email": {
                "type": "string",
                "description": "Email of the rep to analyze",
            },
            "focus_area": {
                "type": "string",
                "description": "Area to focus on: discovery, objections, product_knowledge, rapport, or next_steps",
                "enum": ["discovery", "objections", "product_knowledge", "rapport", "next_steps"],
            },
        },
        "required": ["rep_email"],
    },
)
