"""
Slack notification formatter for coaching insights and alerts.

Formats coaching data into Slack Block Kit blocks for rich, interactive messages.
Supports multiple notification types with appropriate styling and CTAs.
"""
import logging
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackFormatter:
    """Format coaching data into Slack Block Kit messages."""

    # Color constants
    COLOR_SUCCESS = "#16a34a"
    COLOR_WARNING = "#f59e0b"
    COLOR_INFO = "#2563eb"
    COLOR_DANGER = "#dc2626"

    @staticmethod
    def coaching_insight(
        rep_name: str,
        dimension: str,
        score: float,
        insight_description: str,
        insight_id: str,
        app_url: str = "https://callcoach.ai",
    ) -> dict[str, Any]:
        """
        Format a coaching insight for Slack.

        Args:
            rep_name: Name of the sales rep
            dimension: Coaching dimension (e.g., "Objection Handling")
            score: Current score (0-100)
            insight_description: Description of the insight
            insight_id: Unique insight ID
            app_url: Base URL for app links

        Returns:
            Slack message payload (dict)
        """
        score_color = (
            SlackFormatter.COLOR_SUCCESS
            if score >= 80
            else SlackFormatter.COLOR_WARNING if score >= 60 else SlackFormatter.COLOR_DANGER
        )

        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "💡 New Coaching Insight",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{rep_name}* – {dimension}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": insight_description,
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Current Score*\n{score:.0f}/100",
                        },
                    ],
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Insight",
                                "emoji": True,
                            },
                            "url": f"{app_url}/insights/{insight_id}",
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Dismiss",
                                "emoji": True,
                            },
                            "url": f"{app_url}/api/insights/{insight_id}/dismiss",
                        },
                    ],
                },
                {
                    "type": "divider",
                },
            ],
        }

    @staticmethod
    def score_improvement(
        rep_name: str,
        dimension: str,
        previous_score: float,
        current_score: float,
        app_url: str = "https://callcoach.ai",
    ) -> dict[str, Any]:
        """
        Format a score improvement alert for Slack.

        Args:
            rep_name: Name of the sales rep
            dimension: Coaching dimension
            previous_score: Previous period score
            current_score: Current period score
            app_url: Base URL for app links

        Returns:
            Slack message payload (dict)
        """
        improvement = current_score - previous_score
        percent_improvement = (improvement / previous_score * 100) if previous_score > 0 else 0

        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎉 Score Improvement",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Great job *{rep_name}*! Your {dimension} score improved.",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Previous*\n{previous_score:.0f}/100",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Current*\n{current_score:.0f}/100",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Improvement*\n+{improvement:.0f} ({percent_improvement:.0f}%)",
                        },
                    ],
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Progress",
                                "emoji": True,
                            },
                            "url": f"{app_url}/dashboard",
                            "style": "primary",
                        },
                    ],
                },
                {
                    "type": "divider",
                },
            ],
        }

    @staticmethod
    def weekly_summary(
        week_start: datetime,
        team_members: list[dict[str, Any]],
        team_avg_score: float,
        app_url: str = "https://callcoach.ai",
    ) -> dict[str, Any]:
        """
        Format a weekly team summary for Slack.

        Args:
            week_start: Start date of the week
            team_members: List of team member data dicts with 'name', 'score', 'trend'
            team_avg_score: Average team score
            app_url: Base URL for app links

        Returns:
            Slack message payload (dict)
        """
        week_str = week_start.strftime("%b %d")

        # Build team member list
        member_blocks = []
        for member in team_members[:10]:  # Limit to 10 to avoid message size limits
            trend_emoji = {
                "up": "📈",
                "down": "📉",
                "stable": "➡️",
            }.get(member.get("trend"), "")
            score = member.get("score", 0)
            member_blocks.append(
                {
                    "type": "mrkdwn",
                    "text": f"• *{member['name']}*: {score:.0f}/100 {trend_emoji}",
                }
            )

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Weekly Coaching Summary",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Week of {week_str}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Team Members*\n{len(team_members)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Team Average*\n{team_avg_score:.0f}/100",
                    },
                ],
            },
            {
                "type": "divider",
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Team Performance*",
                },
            },
        ]

        # Add member fields in groups of 3
        for i in range(0, len(member_blocks), 3):
            section = {
                "type": "section",
                "fields": member_blocks[i : i + 3],
            }
            blocks.append(section)

        blocks.extend(
            [
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Team Dashboard",
                                "emoji": True,
                            },
                            "url": f"{app_url}/manager/team",
                            "style": "primary",
                        },
                    ],
                },
                {
                    "type": "divider",
                },
            ]
        )

        return {"blocks": blocks}

    @staticmethod
    def alert_low_score(
        rep_name: str,
        dimension: str,
        score: float,
        recommendation: str,
        app_url: str = "https://callcoach.ai",
    ) -> dict[str, Any]:
        """
        Format a low score alert for Slack.

        Args:
            rep_name: Name of the sales rep
            dimension: Coaching dimension
            score: Current score
            recommendation: Recommended action
            app_url: Base URL for app links

        Returns:
            Slack message payload (dict)
        """
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚠️ Coaching Alert",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{rep_name}* – {dimension}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Current score: {score:.0f}/100\n\n_{recommendation}_",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Get Coaching Insights",
                                "emoji": True,
                            },
                            "url": f"{app_url}/coaching?dimension={dimension.lower().replace(' ', '_')}",
                            "style": "danger",
                        },
                    ],
                },
                {
                    "type": "divider",
                },
            ],
        }

    @staticmethod
    def objection_pattern_alert(
        rep_name: str,
        objection_type: str,
        occurrence_count: int,
        examples: list[str],
        app_url: str = "https://callcoach.ai",
    ) -> dict[str, Any]:
        """
        Format a recurring objection pattern alert for Slack.

        Args:
            rep_name: Name of the sales rep
            objection_type: Type of objection (e.g., "Price Objections")
            occurrence_count: Number of occurrences
            examples: List of example quotes or situations
            app_url: Base URL for app links

        Returns:
            Slack message payload (dict)
        """
        examples_text = "\n".join([f"• _{ex}_" for ex in examples[:3]])

        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎯 Recurring Objection Pattern",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{rep_name}* is encountering *{objection_type}* frequently.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Occurrences*: {occurrence_count} times\n\n*Recent Examples*\n{examples_text}",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Analysis",
                                "emoji": True,
                            },
                            "url": f"{app_url}/coaching/objections",
                            "style": "primary",
                        },
                    ],
                },
                {
                    "type": "divider",
                },
            ],
        }

    @staticmethod
    def call_coaching_feedback(
        rep_name: str,
        call_title: str,
        coaching_summary: str,
        key_strengths: list[str],
        areas_for_improvement: list[str],
        app_url: str = "https://callcoach.ai",
    ) -> dict[str, Any]:
        """
        Format real-time call coaching feedback for Slack.

        Args:
            rep_name: Name of the sales rep
            call_title: Title of the call
            coaching_summary: Brief summary of coaching feedback
            key_strengths: List of things done well
            areas_for_improvement: List of areas to focus on
            app_url: Base URL for app links

        Returns:
            Slack message payload (dict)
        """
        strengths_text = "\n".join([f"• {s}" for s in key_strengths[:3]])
        improvements_text = "\n".join([f"• {i}" for i in areas_for_improvement[:3]])

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📞 Call Coaching Feedback",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{rep_name}* – {call_title}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": coaching_summary,
                },
            },
        ]

        if key_strengths:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*✓ Strengths*\n{strengths_text}",
                    },
                }
            )

        if areas_for_improvement:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*→ Areas to Focus*\n{improvements_text}",
                    },
                }
            )

        blocks.extend(
            [
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Full Feedback",
                                "emoji": True,
                            },
                            "url": f"{app_url}/calls",
                            "style": "primary",
                        },
                    ],
                },
                {
                    "type": "divider",
                },
            ]
        )

        return {"blocks": blocks}
