"""
MCP tool for analyzing opportunities with holistic coaching insights.
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from analysis.opportunity_coaching import (
    analyze_objection_progression,
    analyze_opportunity_patterns,
    assess_relationship_strength,
    generate_coaching_recommendations,
    identify_recurring_themes,
)
from db import queries

logger = logging.getLogger(__name__)


def register_analyze_opportunity_tool(server: Server):
    """Register the analyze_opportunity MCP tool."""

    @server.call_tool()
    async def analyze_opportunity(arguments: dict[str, Any]) -> list[TextContent]:
        """
        Analyze an opportunity and provide holistic coaching insights.

        This tool analyzes all calls and emails for an opportunity to identify:
        - Coaching score patterns across all touchpoints
        - Recurring themes and how they evolve
        - Objection handling patterns (resolved vs recurring)
        - Relationship strength trends
        - Specific coaching recommendations for next steps

        Args:
            arguments: Dict with opportunity_id

        Returns:
            List of TextContent with comprehensive analysis
        """
        opportunity_id = arguments.get("opportunity_id")

        if not opportunity_id:
            return [TextContent(type="text", text="Error: opportunity_id is required")]

        try:
            # Verify opportunity exists
            opp = queries.get_opportunity(opportunity_id)
            if not opp:
                return [
                    TextContent(type="text", text=f"Error: Opportunity not found: {opportunity_id}")
                ]

            # Run all analyses
            patterns = analyze_opportunity_patterns(opportunity_id)
            themes = identify_recurring_themes(opportunity_id)
            objections = analyze_objection_progression(opportunity_id)
            relationship = assess_relationship_strength(opportunity_id)
            recommendations = generate_coaching_recommendations(opportunity_id)

            # Format response
            response = f"""# Opportunity Coaching Analysis

**Opportunity:** {opp['name']}
**Account:** {opp['account_name']}
**Owner:** {opp['owner_email']}
**Stage:** {opp['stage']}
**Health Score:** {opp.get('health_score', 'N/A')}

---

## Coaching Score Patterns

Calls Analyzed: {patterns['call_count']}

"""

            for dimension, data in patterns.get("average_scores", {}).items():
                response += f"\n**{dimension}:**\n"
                response += f"- Average Score: {data['average']:. 1f}\n"
                response += f"- Trend: {data['trend']}\n"
                response += f"- Data Points: {data['data_points']}\n"

            response += f"""

---

## Recurring Themes

{themes['themes']}

---

## Objection Handling Patterns

{objections['objection_analysis']}

---

## Relationship Strength Assessment

- Total Calls: {relationship['call_count']}
- Total Emails: {relationship['email_count']}
- Email/Call Ratio: {relationship['email_to_call_ratio']}
- Call Duration Trend: {relationship['call_duration_trend']}

---

## Coaching Recommendations

"""

            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. {rec}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error analyzing opportunity {opportunity_id}: {e}", exc_info=True)
            return [TextContent(type="text", text=f"Error analyzing opportunity: {str(e)}")]


# Tool definition for MCP registration
ANALYZE_OPPORTUNITY_TOOL = Tool(
    name="analyze_opportunity",
    description=(
        "Analyze an opportunity with holistic coaching insights across all calls and emails. "
        "Provides coaching score patterns, recurring themes, objection progression, relationship strength, "
        "and specific recommendations for next steps."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "opportunity_id": {
                "type": "string",
                "description": "UUID of the opportunity to analyze",
            },
        },
        "required": ["opportunity_id"],
    },
)
