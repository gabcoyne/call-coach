"""
Notification delivery and orchestration flow.

Handles sending notifications via multiple channels (email, Slack, in-app)
based on user preferences and notification type.
"""
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from notifications.in_app import InAppNotification, NotificationStore, NotificationBuilder, NotificationType, NotificationPriority
from notifications.preferences import (
    NotificationPreferencesManager,
    DeliveryChannel,
)
from notifications.slack_formatter import SlackFormatter
from reports.email_sender import render_html_report

logger = logging.getLogger(__name__)


# ============================================================================
# EMAIL DELIVERY TASKS
# ============================================================================


@task(name="send_coaching_insight_email", retries=2, retry_delay_seconds=30)
def send_coaching_insight_email(
    user_email: str,
    rep_name: str,
    dimension_label: str,
    insight_description: str,
    current_score: float,
    insight_id: str,
    app_url: str = "https://callcoach.ai",
) -> bool:
    """
    Send coaching insight email.

    Args:
        user_email: User's email address
        rep_name: Rep's name
        dimension_label: Coaching dimension label
        insight_description: Description of the insight
        current_score: Current score
        insight_id: Unique insight ID
        app_url: Base app URL

    Returns:
        True if sent successfully
    """
    from reports.email_sender import send_email_sendgrid, send_email_smtp, send_email_console
    import os

    try:
        context = {
            "rep_name": rep_name,
            "dimension_label": dimension_label,
            "insight_description": insight_description,
            "current_score": current_score,
            "insight_id": insight_id,
            "app_url": app_url,
            "unsubscribe_token": "placeholder",
            "score_class": "high" if current_score >= 80 else "medium" if current_score >= 60 else "low",
        }

        html_content = render_html_report("coaching_insight.html", context)
        subject = f"Coaching Insight: {dimension_label}"

        # Try to send via configured provider
        provider = "auto"
        if os.getenv("SENDGRID_API_KEY"):
            provider = "sendgrid"
        elif os.getenv("SMTP_HOST"):
            provider = "smtp"
        else:
            provider = "console"

        send_fn = {
            "sendgrid": send_email_sendgrid,
            "smtp": send_email_smtp,
            "console": send_email_console,
        }.get(provider, send_email_console)

        success = send_fn(user_email, subject, html_content)
        logger.info(f"Sent coaching insight email to {user_email}: {success}")
        return success

    except Exception as e:
        logger.error(f"Failed to send coaching insight email to {user_email}: {e}", exc_info=True)
        return False


@task(name="send_weekly_report_email", retries=2, retry_delay_seconds=30)
def send_weekly_report_email(
    user_email: str,
    rep_name: str,
    report_data: dict[str, Any],
    app_url: str = "https://callcoach.ai",
) -> bool:
    """
    Send weekly report email.

    Args:
        user_email: User's email address
        rep_name: Rep's name
        report_data: Report data dict
        app_url: Base app URL

    Returns:
        True if sent successfully
    """
    from reports.email_sender import send_weekly_report_email as send_email

    try:
        success = send_email(user_email, rep_name, report_data, provider="auto")
        logger.info(f"Sent weekly report email to {user_email}: {success}")
        return success

    except Exception as e:
        logger.error(f"Failed to send weekly report email to {user_email}: {e}", exc_info=True)
        return False


# ============================================================================
# SLACK DELIVERY TASKS
# ============================================================================


@task(name="send_slack_notification", retries=2, retry_delay_seconds=30)
def send_slack_notification(
    webhook_url: str,
    blocks: dict[str, Any],
) -> bool:
    """
    Send notification to Slack webhook.

    Args:
        webhook_url: Slack webhook URL
        blocks: Slack Block Kit blocks

    Returns:
        True if sent successfully
    """
    import httpx

    try:
        response = httpx.post(webhook_url, json=blocks, timeout=10.0)
        response.raise_for_status()
        logger.info(f"Sent Slack notification")
        return True

    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


@task(name="send_coaching_insight_slack")
def send_coaching_insight_slack(
    webhook_url: str,
    rep_name: str,
    dimension: str,
    score: float,
    insight_description: str,
    insight_id: str,
    app_url: str = "https://callcoach.ai",
) -> bool:
    """Send coaching insight to Slack."""
    blocks = SlackFormatter.coaching_insight(
        rep_name=rep_name,
        dimension=dimension,
        score=score,
        insight_description=insight_description,
        insight_id=insight_id,
        app_url=app_url,
    )
    return send_slack_notification(webhook_url, blocks)


# ============================================================================
# IN-APP NOTIFICATION TASKS
# ============================================================================


@task(name="create_inapp_notification")
def create_inapp_notification(
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    action_url: str | None = None,
    action_label: str | None = None,
    data: dict[str, Any] | None = None,
    expires_hours: int | None = None,
) -> UUID | None:
    """
    Create an in-app notification.

    Args:
        user_id: User UUID
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        priority: Notification priority
        action_url: Optional URL for action button
        action_label: Optional label for action button
        data: Optional additional data
        expires_hours: Optional expiration time in hours

    Returns:
        Notification ID or None if failed
    """
    try:
        builder = NotificationBuilder(user_id, notification_type)
        builder.title(title).message(message).priority(priority)

        if action_url:
            builder.action(action_url, action_label or "View")

        if data:
            builder.data(data)

        if expires_hours:
            builder.expires_in(expires_hours)

        notification = builder.build()
        notification_id = NotificationStore.create(notification)
        logger.info(f"Created in-app notification {notification_id} for user {user_id}")
        return notification_id

    except Exception as e:
        logger.error(f"Failed to create in-app notification for user {user_id}: {e}")
        return None


# ============================================================================
# NOTIFICATION ORCHESTRATION
# ============================================================================


@task(name="send_coaching_insight_notifications")
def send_coaching_insight_notifications(
    user_id: UUID,
    user_email: str,
    slack_webhook_url: str | None,
    rep_name: str,
    dimension_label: str,
    insight_description: str,
    current_score: float,
    insight_id: str,
    app_url: str = "https://callcoach.ai",
) -> dict[str, bool]:
    """
    Send coaching insight via all enabled channels.

    Args:
        user_id: User UUID
        user_email: User's email
        slack_webhook_url: Slack webhook URL (if applicable)
        rep_name: Rep's name
        dimension_label: Dimension label
        insight_description: Insight description
        current_score: Current score
        insight_id: Insight ID
        app_url: Base app URL

    Returns:
        Dict with delivery status per channel
    """
    results = {
        "email": False,
        "slack": False,
        "in_app": False,
    }

    try:
        # Check preferences and send via enabled channels
        prefs_mgr = NotificationPreferencesManager()

        # Email
        if prefs_mgr.should_send_notification(user_id, "coaching_insights", DeliveryChannel.EMAIL):
            results["email"] = send_coaching_insight_email(
                user_email,
                rep_name,
                dimension_label,
                insight_description,
                current_score,
                insight_id,
                app_url,
            )

        # Slack
        if slack_webhook_url and prefs_mgr.should_send_notification(
            user_id, "coaching_insights", DeliveryChannel.SLACK
        ):
            results["slack"] = send_coaching_insight_slack(
                slack_webhook_url,
                rep_name,
                dimension_label,
                current_score,
                insight_description,
                insight_id,
                app_url,
            )

        # In-app
        if prefs_mgr.should_send_notification(user_id, "coaching_insights", DeliveryChannel.IN_APP):
            notification_id = create_inapp_notification(
                user_id,
                NotificationType.COACHING_INSIGHT,
                f"Insight: {dimension_label}",
                insight_description,
                priority=NotificationPriority.HIGH,
                action_url=f"{app_url}/insights/{insight_id}",
                action_label="View",
            )
            results["in_app"] = notification_id is not None

        logger.info(f"Sent coaching insight for user {user_id}: {results}")
        return results

    except Exception as e:
        logger.error(f"Failed to send coaching insight notifications: {e}", exc_info=True)
        return results


@task(name="send_score_improvement_notifications")
def send_score_improvement_notifications(
    user_id: UUID,
    user_email: str,
    slack_webhook_url: str | None,
    rep_name: str,
    dimension: str,
    previous_score: float,
    current_score: float,
    app_url: str = "https://callcoach.ai",
) -> dict[str, bool]:
    """
    Send score improvement notification via all enabled channels.

    Args:
        user_id: User UUID
        user_email: User's email
        slack_webhook_url: Slack webhook URL
        rep_name: Rep's name
        dimension: Dimension name
        previous_score: Previous score
        current_score: Current score
        app_url: Base app URL

    Returns:
        Dict with delivery status per channel
    """
    results = {
        "email": False,
        "slack": False,
        "in_app": False,
    }

    try:
        prefs_mgr = NotificationPreferencesManager()
        improvement = current_score - previous_score
        improvement_percent = (improvement / previous_score * 100) if previous_score > 0 else 0

        # Slack
        if slack_webhook_url and prefs_mgr.should_send_notification(
            user_id, "score_improvements", DeliveryChannel.SLACK
        ):
            blocks = SlackFormatter.score_improvement(
                rep_name, dimension, previous_score, current_score, app_url
            )
            results["slack"] = send_slack_notification(slack_webhook_url, blocks)

        # In-app
        if prefs_mgr.should_send_notification(
            user_id, "score_improvements", DeliveryChannel.IN_APP
        ):
            notification_id = create_inapp_notification(
                user_id,
                NotificationType.SCORE_IMPROVEMENT,
                f"Great improvement in {dimension}!",
                f"Your {dimension} score improved from {previous_score:.0f} to {current_score:.0f} (+{improvement_percent:.0f}%)",
                priority=NotificationPriority.HIGH,
                action_url=f"{app_url}/dashboard",
                action_label="View Progress",
            )
            results["in_app"] = notification_id is not None

        logger.info(f"Sent score improvement notification for user {user_id}: {results}")
        return results

    except Exception as e:
        logger.error(f"Failed to send score improvement notifications: {e}", exc_info=True)
        return results


# ============================================================================
# MAIN FLOW
# ============================================================================


@flow(
    name="send_notifications",
    description="Send notifications via multiple channels based on user preferences",
    task_runner=ConcurrentTaskRunner(),
)
def send_notifications_flow(
    notification_requests: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Send notifications via multiple channels.

    Args:
        notification_requests: List of notification request dicts

    Returns:
        Dict with delivery results

    Example:
        requests = [
            {
                "user_id": "...",
                "type": "coaching_insight",
                "data": {...}
            }
        ]
        result = send_notifications_flow(requests)
    """
    logger.info(f"Starting notification flow with {len(notification_requests)} requests")

    results = {
        "total_requests": len(notification_requests),
        "successful": 0,
        "failed": 0,
        "details": [],
    }

    for request in notification_requests:
        try:
            notification_type = request.get("type")
            user_id = request.get("user_id")
            data = request.get("data", {})

            if not user_id:
                results["failed"] += 1
                continue

            request_result = {
                "user_id": str(user_id),
                "type": notification_type,
            }

            # Route to appropriate handler
            if notification_type == "coaching_insight":
                delivery = send_coaching_insight_notifications(**data)
            elif notification_type == "score_improvement":
                delivery = send_score_improvement_notifications(**data)
            else:
                logger.warning(f"Unknown notification type: {notification_type}")
                request_result["status"] = "unknown_type"
                results["failed"] += 1
                results["details"].append(request_result)
                continue

            request_result["delivery"] = delivery
            request_result["status"] = "sent"
            results["successful"] += 1
            results["details"].append(request_result)

        except Exception as e:
            logger.error(f"Failed to process notification request: {e}", exc_info=True)
            results["failed"] += 1
            request_result = {
                "user_id": str(request.get("user_id", "unknown")),
                "type": request.get("type"),
                "status": "error",
                "error": str(e),
            }
            results["details"].append(request_result)

    logger.info(f"Notification flow completed: {results['successful']} successful, {results['failed']} failed")
    return results


if __name__ == "__main__":
    """
    Local execution for testing:

    python -m flows.notifications
    """
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Example notification requests
    example_requests = [
        {
            "type": "coaching_insight",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "data": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_email": "rep@example.com",
                "slack_webhook_url": None,
                "rep_name": "John Smith",
                "dimension_label": "Objection Handling",
                "insight_description": "You could improve your handling of price objections. In your last call, you didn't address the cost concern directly.",
                "current_score": 65,
                "insight_id": "insight-123",
            },
        }
    ]

    result = send_notifications_flow(example_requests)
    print(f"\nNotification Results: {result}")
