"""
Weekly Review Automation Flow

Generates comprehensive weekly coaching reports for each rep, including:
- Coaching scores aggregated by dimension
- Recurring objections and common themes
- Trend analysis vs previous weeks
- Actionable recommendations
- Distribution via email and Slack

Scheduled to run every Monday at 6am.
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from db import fetch_all, fetch_one, queries
from db.models import CoachingDimension

logger = logging.getLogger(__name__)


# ============================================================================
# DATA COLLECTION TASKS
# ============================================================================


@task(name="get_reps_with_calls")
def get_reps_with_calls(start_date: datetime, end_date: datetime) -> list[dict[str, Any]]:
    """
    Get all reps who had calls in the specified date range.

    Args:
        start_date: Start of date range
        end_date: End of date range

    Returns:
        List of rep dicts with id, name, email, role
    """
    logger.info(f"Finding reps with calls between {start_date} and {end_date}")

    reps = fetch_all(
        """
        SELECT DISTINCT
            s.id,
            s.name,
            s.email,
            s.role
        FROM speakers s
        JOIN calls c ON s.call_id = c.id
        WHERE s.company_side = true
        AND s.email IS NOT NULL
        AND c.scheduled_at BETWEEN %s AND %s
        ORDER BY s.name
        """,
        (start_date, end_date),
    )

    logger.info(f"Found {len(reps)} reps with calls in date range")
    return reps


@task(name="get_rep_calls_for_week")
def get_rep_calls_for_week(
    rep_email: str, start_date: datetime, end_date: datetime
) -> list[dict[str, Any]]:
    """
    Get all calls for a rep in the specified week.

    Args:
        rep_email: Rep's email address
        start_date: Start of week
        end_date: End of week

    Returns:
        List of call dicts with metadata
    """
    calls = fetch_all(
        """
        SELECT DISTINCT
            c.id,
            c.gong_call_id,
            c.title,
            c.scheduled_at,
            c.duration_seconds,
            c.call_type,
            c.product
        FROM calls c
        JOIN speakers s ON c.id = s.call_id
        WHERE s.email = %s
        AND s.company_side = true
        AND c.scheduled_at BETWEEN %s AND %s
        ORDER BY c.scheduled_at DESC
        """,
        (rep_email, start_date, end_date),
    )

    logger.info(f"Found {len(calls)} calls for {rep_email}")
    return calls


@task(name="aggregate_coaching_scores")
def aggregate_coaching_scores(
    rep_email: str, start_date: datetime, end_date: datetime
) -> dict[str, Any]:
    """
    Aggregate coaching scores by dimension for a rep.

    Args:
        rep_email: Rep's email address
        start_date: Start of period
        end_date: End of period

    Returns:
        Dict with average scores by dimension and overall stats
    """
    scores = fetch_all(
        """
        SELECT
            cs.coaching_dimension,
            AVG(cs.score) as avg_score,
            MIN(cs.score) as min_score,
            MAX(cs.score) as max_score,
            COUNT(*) as session_count
        FROM coaching_sessions cs
        JOIN speakers s ON cs.rep_id = s.id
        WHERE s.email = %s
        AND cs.created_at BETWEEN %s AND %s
        GROUP BY cs.coaching_dimension
        """,
        (rep_email, start_date, end_date),
    )

    # Calculate overall average
    overall_avg = (
        sum(score["avg_score"] for score in scores) / len(scores) if scores else None
    )

    result = {
        "by_dimension": {
            score["coaching_dimension"]: {
                "avg_score": round(score["avg_score"], 1),
                "min_score": score["min_score"],
                "max_score": score["max_score"],
                "session_count": score["session_count"],
            }
            for score in scores
        },
        "overall_avg": round(overall_avg, 1) if overall_avg else None,
        "total_sessions": sum(score["session_count"] for score in scores),
    }

    logger.info(
        f"Aggregated scores for {rep_email}: {result['total_sessions']} sessions, "
        f"avg {result['overall_avg']}"
    )

    return result


@task(name="identify_recurring_objections")
def identify_recurring_objections(
    rep_email: str, start_date: datetime, end_date: datetime
) -> list[dict[str, Any]]:
    """
    Identify recurring objections and common themes from coaching sessions.

    Args:
        rep_email: Rep's email address
        start_date: Start of period
        end_date: End of period

    Returns:
        List of objection/theme patterns with frequency and examples
    """
    # Get all objection handling coaching sessions
    sessions = fetch_all(
        """
        SELECT
            cs.id,
            cs.call_id,
            cs.specific_examples,
            cs.areas_for_improvement,
            c.title as call_title,
            c.scheduled_at
        FROM coaching_sessions cs
        JOIN speakers s ON cs.rep_id = s.id
        JOIN calls c ON cs.call_id = c.id
        WHERE s.email = %s
        AND cs.coaching_dimension = 'objection_handling'
        AND cs.created_at BETWEEN %s AND %s
        ORDER BY c.scheduled_at DESC
        """,
        (rep_email, start_date, end_date),
    )

    # Extract and count objection types from specific_examples and areas_for_improvement
    objection_patterns = {}

    for session in sessions:
        # Parse specific examples (JSONB)
        examples = session.get("specific_examples") or {}
        if isinstance(examples, str):
            examples = json.loads(examples)

        needs_work = examples.get("needs_work", [])
        for example in needs_work:
            if isinstance(example, dict):
                text = example.get("analysis", "")
                # Simple keyword extraction for common objection types
                if "pricing" in text.lower() or "cost" in text.lower():
                    key = "pricing_objections"
                    label = "Pricing/Cost Concerns"
                elif "timing" in text.lower() or "not ready" in text.lower():
                    key = "timing_objections"
                    label = "Timing/Readiness"
                elif "technical" in text.lower() or "integration" in text.lower():
                    key = "technical_objections"
                    label = "Technical Concerns"
                elif "competitor" in text.lower():
                    key = "competitor_objections"
                    label = "Competitive Comparison"
                else:
                    key = "other_objections"
                    label = "Other Objections"

                if key not in objection_patterns:
                    objection_patterns[key] = {
                        "type": label,
                        "count": 0,
                        "examples": [],
                    }

                objection_patterns[key]["count"] += 1
                if len(objection_patterns[key]["examples"]) < 3:  # Keep top 3
                    objection_patterns[key]["examples"].append(
                        {
                            "call_title": session.get("call_title"),
                            "date": session.get("scheduled_at"),
                            "quote": example.get("quote", "")[:200],  # Truncate
                        }
                    )

    # Sort by frequency
    result = sorted(
        objection_patterns.values(), key=lambda x: x["count"], reverse=True
    )

    logger.info(f"Identified {len(result)} objection patterns for {rep_email}")
    return result


@task(name="calculate_trend_vs_previous_week")
def calculate_trend_vs_previous_week(
    rep_email: str, current_week_start: datetime, current_week_end: datetime
) -> dict[str, Any]:
    """
    Calculate score trends compared to previous week.

    Args:
        rep_email: Rep's email address
        current_week_start: Start of current week
        current_week_end: End of current week

    Returns:
        Dict with trend data by dimension
    """
    # Calculate previous week range
    prev_week_start = current_week_start - timedelta(days=7)
    prev_week_end = current_week_end - timedelta(days=7)

    # Get scores for both weeks
    current_scores = aggregate_coaching_scores(rep_email, current_week_start, current_week_end)
    previous_scores = aggregate_coaching_scores(rep_email, prev_week_start, prev_week_end)

    trends = {}

    for dimension in CoachingDimension:
        dim_value = dimension.value
        current = current_scores["by_dimension"].get(dim_value, {}).get("avg_score")
        previous = previous_scores["by_dimension"].get(dim_value, {}).get("avg_score")

        if current is not None and previous is not None:
            change = current - previous
            percent_change = (change / previous * 100) if previous > 0 else 0

            trends[dim_value] = {
                "current_score": current,
                "previous_score": previous,
                "change": round(change, 1),
                "percent_change": round(percent_change, 1),
                "direction": "up" if change > 0 else "down" if change < 0 else "stable",
            }
        elif current is not None:
            trends[dim_value] = {
                "current_score": current,
                "previous_score": None,
                "change": None,
                "percent_change": None,
                "direction": "new",
            }

    overall_current = current_scores.get("overall_avg")
    overall_previous = previous_scores.get("overall_avg")

    if overall_current and overall_previous:
        overall_change = overall_current - overall_previous
        trends["overall"] = {
            "current_score": overall_current,
            "previous_score": overall_previous,
            "change": round(overall_change, 1),
            "percent_change": round((overall_change / overall_previous * 100), 1)
            if overall_previous > 0
            else 0,
            "direction": (
                "up" if overall_change > 0 else "down" if overall_change < 0 else "stable"
            ),
        }

    logger.info(f"Calculated trends for {rep_email}: {len(trends)} dimensions tracked")
    return trends


# ============================================================================
# REPORT GENERATION TASKS
# ============================================================================


@task(name="generate_rep_report_markdown")
def generate_rep_report_markdown(
    rep: dict[str, Any],
    calls: list[dict[str, Any]],
    scores: dict[str, Any],
    objections: list[dict[str, Any]],
    trends: dict[str, Any],
    week_start: datetime,
    week_end: datetime,
) -> str:
    """
    Generate markdown report for a single rep.

    Args:
        rep: Rep information dict
        calls: List of calls for the week
        scores: Aggregated scores dict
        objections: Recurring objections list
        trends: Trend data vs previous week
        week_start: Start of week
        week_end: End of week

    Returns:
        Markdown-formatted report string
    """
    week_str = week_start.strftime("%B %d, %Y")

    # Build report
    report_lines = [
        f"# Weekly Coaching Report - {rep['name']}",
        f"**Week of {week_str}**",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total Calls:** {len(calls)}",
        f"- **Coaching Sessions:** {scores.get('total_sessions', 0)}",
    ]

    # Overall score with trend
    if scores.get("overall_avg"):
        overall_line = f"- **Overall Score:** {scores['overall_avg']}/100"
        if "overall" in trends:
            trend = trends["overall"]
            emoji = "📈" if trend["direction"] == "up" else "📉" if trend["direction"] == "down" else "➡️"
            overall_line += f" {emoji} ({trend['change']:+.1f} from last week)"
        report_lines.append(overall_line)

    report_lines.extend(["", "---", "", "## Score Breakdown by Dimension", ""])

    # Scores by dimension
    for dimension in CoachingDimension:
        dim_value = dimension.value
        dim_label = dimension.value.replace("_", " ").title()
        dim_scores = scores["by_dimension"].get(dim_value)

        if dim_scores:
            score_line = f"### {dim_label}: {dim_scores['avg_score']}/100"

            # Add trend indicator
            if dim_value in trends:
                trend = trends[dim_value]
                if trend["direction"] == "up":
                    score_line += f" 📈 +{trend['change']:.1f}"
                elif trend["direction"] == "down":
                    score_line += f" 📉 {trend['change']:.1f}"

            report_lines.extend(
                [
                    score_line,
                    "",
                    f"- Range: {dim_scores['min_score']}-{dim_scores['max_score']}",
                    f"- Sessions: {dim_scores['session_count']}",
                    "",
                ]
            )

    # Recurring objections
    if objections:
        report_lines.extend(["---", "", "## Recurring Themes & Objections", ""])
        for obj in objections[:5]:  # Top 5
            report_lines.extend(
                [f"### {obj['type']} ({obj['count']} occurrences)", ""]
            )

            if obj["examples"]:
                report_lines.append("**Examples:**")
                for ex in obj["examples"][:2]:  # Top 2 examples
                    call_title = ex.get("call_title") or "Unknown Call"
                    report_lines.extend(
                        [
                            "",
                            f"- *{call_title}*",
                            f'  > "{ex["quote"][:150]}..."',
                        ]
                    )
                report_lines.append("")

    # Call list
    report_lines.extend(["---", "", "## Calls This Week", ""])
    for call in calls:
        call_title = call.get("title") or "Untitled Call"
        call_date = call["scheduled_at"].strftime("%a %b %d")
        call_type = call.get("call_type", "").replace("_", " ").title() if call.get("call_type") else "General"
        report_lines.append(f"- **{call_title}** ({call_type}) - {call_date}")

    # Action items
    report_lines.extend(
        [
            "",
            "---",
            "",
            "## Recommended Focus Areas",
            "",
        ]
    )

    # Generate recommendations based on lowest scores
    if scores["by_dimension"]:
        sorted_dims = sorted(
            scores["by_dimension"].items(), key=lambda x: x[1]["avg_score"]
        )
        lowest_dim = sorted_dims[0]
        dim_label = lowest_dim[0].replace("_", " ").title()
        report_lines.append(
            f"1. **{dim_label}** - Current score: {lowest_dim[1]['avg_score']}/100"
        )

        if len(sorted_dims) > 1:
            second_dim = sorted_dims[1]
            dim_label = second_dim[0].replace("_", " ").title()
            report_lines.append(
                f"2. **{dim_label}** - Current score: {second_dim[1]['avg_score']}/100"
            )

    # Add objection handling recommendation if recurring patterns found
    if objections and len(objections) > 0:
        top_objection = objections[0]
        report_lines.append(
            f"3. **Address {top_objection['type']}** - Recurring {top_objection['count']} times"
        )

    report_lines.extend(["", "---", "", f"*Report generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*", ""])

    return "\n".join(report_lines)


# ============================================================================
# DELIVERY TASKS
# ============================================================================


@task(name="send_email_report", retries=2, retry_delay_seconds=30)
def send_email_report(
    recipient_email: str, recipient_name: str, report_markdown: str, week_start: datetime
) -> bool:
    """
    Send email report to rep.

    Note: This is a placeholder. Actual email sending requires:
    - Email service configuration (SendGrid, AWS SES, etc.)
    - Email credentials in environment

    Args:
        recipient_email: Rep's email address
        recipient_name: Rep's name
        report_markdown: Markdown report content
        week_start: Start of week for subject line

    Returns:
        True if sent successfully, False otherwise
    """
    logger.warning(
        f"Email sending not implemented. Would send report to {recipient_email}"
    )
    logger.info(f"Report preview (first 200 chars):\n{report_markdown[:200]}")

    # TODO: Implement actual email sending
    # Example with SendGrid:
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    #
    # message = Mail(
    #     from_email='coach@prefect.io',
    #     to_emails=recipient_email,
    #     subject=f'Weekly Coaching Report - Week of {week_start.strftime("%b %d, %Y")}',
    #     html_content=markdown_to_html(report_markdown)
    # )
    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    # response = sg.send(message)

    return False  # Change to True when implemented


@task(name="post_to_slack", retries=2, retry_delay_seconds=30)
def post_to_slack(summary_text: str, webhook_url: str | None = None) -> bool:
    """
    Post summary to Slack webhook.

    Args:
        summary_text: Summary text to post
        webhook_url: Slack webhook URL (or from settings)

    Returns:
        True if posted successfully, False otherwise
    """
    from coaching_mcp.shared import settings
    import httpx

    url = webhook_url or settings.slack_webhook_url

    if not url:
        logger.warning("SLACK_WEBHOOK_URL not configured, skipping Slack notification")
        return False

    try:
        payload = {"text": summary_text}
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()

        logger.info("Successfully posted summary to Slack")
        return True

    except Exception as e:
        logger.error(f"Failed to post to Slack: {e}")
        return False


# ============================================================================
# MAIN FLOW
# ============================================================================


@flow(
    name="weekly_review",
    description="Generate and distribute weekly coaching reports for all reps",
    task_runner=ConcurrentTaskRunner(),
)
def weekly_review_flow(
    week_start: datetime | None = None,
    week_end: datetime | None = None,
    send_emails: bool = False,
    send_slack: bool = True,
) -> dict[str, Any]:
    """
    Weekly review automation flow.

    Generates comprehensive coaching reports for each rep with:
    1. Aggregated coaching scores by dimension
    2. Recurring objections and common themes
    3. Trend analysis vs previous week
    4. Actionable recommendations

    Reports are distributed via email (if enabled) and Slack summary.

    Args:
        week_start: Start of week (defaults to 7 days ago)
        week_end: End of week (defaults to today)
        send_emails: Enable email delivery (requires email service setup)
        send_slack: Enable Slack summary posting

    Returns:
        Dict with processing results and statistics

    Example:
        >>> # Run for current week
        >>> result = weekly_review_flow()
        >>>
        >>> # Run for specific week
        >>> from datetime import datetime
        >>> start = datetime(2025, 1, 1)
        >>> end = datetime(2025, 1, 8)
        >>> result = weekly_review_flow(week_start=start, week_end=end)
    """
    logger.info("Starting weekly review flow")

    # Default to last 7 days if not specified
    if not week_end:
        week_end = datetime.now(timezone.utc)
    if not week_start:
        week_start = week_end - timedelta(days=7)

    logger.info(f"Processing week: {week_start.date()} to {week_end.date()}")

    # Get all reps who had calls this week
    reps = get_reps_with_calls(week_start, week_end)

    if not reps:
        logger.warning("No reps found with calls in specified date range")
        return {
            "status": "completed",
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "reps_processed": 0,
            "reports_generated": 0,
            "emails_sent": 0,
            "slack_posted": False,
        }

    # Process each rep
    reports_generated = 0
    emails_sent = 0
    summary_stats = []

    for rep in reps:
        logger.info(f"Processing report for {rep['name']} ({rep['email']})")

        try:
            # Gather data
            calls = get_rep_calls_for_week(rep["email"], week_start, week_end)
            scores = aggregate_coaching_scores(rep["email"], week_start, week_end)
            objections = identify_recurring_objections(rep["email"], week_start, week_end)
            trends = calculate_trend_vs_previous_week(rep["email"], week_start, week_end)

            # Generate report
            report_md = generate_rep_report_markdown(
                rep, calls, scores, objections, trends, week_start, week_end
            )

            # Save report to database (optional - for audit trail)
            # TODO: Create weekly_reports table to store generated reports

            reports_generated += 1

            # Send email if enabled
            if send_emails:
                email_success = send_email_report(
                    rep["email"], rep["name"], report_md, week_start
                )
                if email_success:
                    emails_sent += 1

            # Collect summary stats
            summary_stats.append(
                {
                    "name": rep["name"],
                    "email": rep["email"],
                    "calls": len(calls),
                    "overall_score": scores.get("overall_avg"),
                    "trend": trends.get("overall", {}).get("direction"),
                }
            )

        except Exception as e:
            logger.error(f"Failed to process report for {rep['email']}: {e}", exc_info=True)

    # Post summary to Slack
    slack_posted = False
    if send_slack and summary_stats:
        summary_text = _build_slack_summary(summary_stats, week_start, week_end)
        slack_posted = post_to_slack(summary_text)

    result = {
        "status": "completed",
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "reps_processed": len(reps),
        "reports_generated": reports_generated,
        "emails_sent": emails_sent,
        "slack_posted": slack_posted,
    }

    logger.info(f"Weekly review completed: {result}")
    return result


def _build_slack_summary(
    stats: list[dict[str, Any]], week_start: datetime, week_end: datetime
) -> str:
    """Build Slack-formatted summary message."""
    week_str = week_start.strftime("%B %d, %Y")

    lines = [
        f"📊 *Weekly Coaching Report - Week of {week_str}*",
        "",
        f"Generated reports for {len(stats)} reps:",
        "",
    ]

    # Sort by overall score (highest first)
    sorted_stats = sorted(
        stats, key=lambda x: x.get("overall_score") or 0, reverse=True
    )

    for stat in sorted_stats:
        name = stat["name"]
        calls = stat["calls"]
        score = stat.get("overall_score")
        trend = stat.get("trend")

        # Trend emoji
        trend_emoji = {
            "up": "📈",
            "down": "📉",
            "stable": "➡️",
            "new": "🆕",
        }.get(trend, "")

        score_str = f"{score:.0f}/100" if score else "N/A"
        lines.append(f"• *{name}*: {score_str} {trend_emoji} ({calls} calls)")

    lines.extend(
        [
            "",
            "_Individual reports sent via email (if enabled)_",
            "",
            f"🤖 Generated by Gong Call Coaching Agent",
        ]
    )

    return "\n".join(lines)


# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================


if __name__ == "__main__":
    """
    Local execution for testing:

    python -m flows.weekly_review

    For scheduling in Prefect Cloud, use Prefect deployment YAML or:

    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import CronSchedule

    deployment = Deployment.build_from_flow(
        flow=weekly_review_flow,
        name="weekly-review-monday-6am",
        schedule=CronSchedule(cron="0 6 * * 1", timezone="UTC"),  # Monday 6am UTC
        work_pool_name="default",
    )
    deployment.apply()
    """
    from dotenv import load_dotenv

    load_dotenv()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run for last 7 days
    result = weekly_review_flow(send_emails=False, send_slack=False)

    # Print results
    print("\n" + "=" * 80)
    print("WEEKLY REVIEW RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))
