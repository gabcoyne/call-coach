"""
Example usage of the notification system.

These examples demonstrate how to integrate notifications into your workflow.
"""
from datetime import datetime
from uuid import UUID

from notifications.in_app import NotificationStore, NotificationBuilder, NotificationType, NotificationPriority
from notifications.preferences import NotificationPreferencesManager, DeliveryChannel
from notifications.slack_formatter import SlackFormatter
from flows.notifications import (
    send_coaching_insight_notifications,
    send_score_improvement_notifications,
    send_notifications_flow,
)


# Example 1: Send a coaching insight to a single user
def example_coaching_insight():
    """Send a coaching insight via all enabled channels."""
    user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    user_email = "john.smith@company.com"
    slack_webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

    results = send_coaching_insight_notifications(
        user_id=user_id,
        user_email=user_email,
        slack_webhook_url=slack_webhook,
        rep_name="John Smith",
        dimension_label="Objection Handling",
        insight_description=(
            "You encountered price objections in 3 recent calls but didn't directly "
            "address the cost concern. Try reframing the value proposition before "
            "discussing pricing."
        ),
        current_score=65.0,
        insight_id="insight-abc123",
        app_url="https://callcoach.ai",
    )

    print(f"Coaching insight delivery results: {results}")
    # Output: {"email": True, "slack": True, "in_app": True}


# Example 2: Send score improvement celebration
def example_score_improvement():
    """Send a celebration when a rep improves their score."""
    user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    user_email = "john.smith@company.com"
    slack_webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

    results = send_score_improvement_notifications(
        user_id=user_id,
        user_email=user_email,
        slack_webhook_url=slack_webhook,
        rep_name="John Smith",
        dimension="Objection Handling",
        previous_score=60.0,
        current_score=75.0,
        app_url="https://callcoach.ai",
    )

    print(f"Score improvement notification sent: {results}")


# Example 3: Create in-app notification directly
def example_create_inapp_notification():
    """Create a custom in-app notification."""
    user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    notification = (
        NotificationBuilder(user_id, NotificationType.COACHING_INSIGHT)
        .title("Objection Handling Improvement Needed")
        .message(
            "We noticed you're struggling with price objections. "
            "Check out our objection handling playbook."
        )
        .priority(NotificationPriority.HIGH)
        .action("https://callcoach.ai/playbooks/objections", "View Playbook")
        .expires_in(48)  # Expires in 48 hours
        .data({
            "dimension": "objection_handling",
            "current_score": 65,
            "playbook_id": "objections-101"
        })
        .build()
    )

    notification_id = NotificationStore.create(notification)
    print(f"Created in-app notification: {notification_id}")


# Example 4: Retrieve and manage notifications
def example_manage_notifications():
    """Retrieve and manage user notifications."""
    user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    # Get unread count
    unread_count = NotificationStore.get_unread_count(user_id)
    print(f"Unread notifications: {unread_count}")

    # Get all unread notifications
    unread = NotificationStore.get_user_notifications(
        user_id=user_id,
        unread_only=True,
        limit=10
    )

    for notif in unread:
        print(f"- [{notif.type}] {notif.title}")
        # Mark as read
        NotificationStore.mark_as_read(notif.id)

    # Archive old notifications
    all_notifications = NotificationStore.get_user_notifications(
        user_id=user_id,
        limit=50
    )
    old_notifs = [n for n in all_notifications if (datetime.utcnow() - n.created_at).days > 7]
    for notif in old_notifs:
        NotificationStore.archive(notif.id)


# Example 5: Manage user preferences
def example_manage_preferences():
    """Get and update user notification preferences."""
    user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    # Get current preferences
    prefs = NotificationPreferencesManager.get_preferences(user_id)
    print(f"Current preferences: {prefs}")

    # Update specific preference
    NotificationPreferencesManager.update_notification_type_preference(
        user_id=user_id,
        notification_type="coaching_insights",
        email=True,
        slack=True,
        in_app=True,
        frequency="immediate"
    )

    # Disable score decline emails (but keep other channels)
    NotificationPreferencesManager.update_notification_type_preference(
        user_id=user_id,
        notification_type="score_declines",
        email=False  # Turn off emails but keep Slack and in-app
    )

    # Check if should send
    should_send = NotificationPreferencesManager.should_send_notification(
        user_id=user_id,
        notification_type="coaching_insights",
        channel=DeliveryChannel.EMAIL
    )
    print(f"Should send coaching_insights via email: {should_send}")


# Example 6: Batch notification delivery
def example_batch_notifications():
    """Send notifications to multiple users at once."""
    requests = [
        {
            "type": "coaching_insight",
            "user_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
            "data": {
                "user_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
                "user_email": "john@example.com",
                "slack_webhook_url": "https://hooks.slack.com/...",
                "rep_name": "John Smith",
                "dimension_label": "Discovery",
                "insight_description": "Try asking more probing questions.",
                "current_score": 70,
                "insight_id": "insight-001",
            }
        },
        {
            "type": "coaching_insight",
            "user_id": UUID("660e8400-e29b-41d4-a716-446655440001"),
            "data": {
                "user_id": UUID("660e8400-e29b-41d4-a716-446655440001"),
                "user_email": "jane@example.com",
                "slack_webhook_url": "https://hooks.slack.com/...",
                "rep_name": "Jane Doe",
                "dimension_label": "Engagement",
                "insight_description": "Your engagement score improved!",
                "current_score": 85,
                "insight_id": "insight-002",
            }
        }
    ]

    result = send_notifications_flow(requests)
    print(f"Batch notification results: {result}")
    # Output:
    # {
    #     "total_requests": 2,
    #     "successful": 2,
    #     "failed": 0,
    #     "details": [...]
    # }


# Example 7: Format Slack messages manually
def example_slack_formatting():
    """Format various notification types as Slack messages."""
    from flows.notifications import send_slack_notification

    # Coaching insight
    insight_blocks = SlackFormatter.coaching_insight(
        rep_name="John Smith",
        dimension="Objection Handling",
        score=65,
        insight_description="Focus on price objection rebuttals",
        insight_id="insight-123"
    )

    # Score improvement
    improvement_blocks = SlackFormatter.score_improvement(
        rep_name="John Smith",
        dimension="Discovery",
        previous_score=70,
        current_score=82
    )

    # Weekly summary
    summary_blocks = SlackFormatter.weekly_summary(
        week_start=datetime.now(),
        team_members=[
            {"name": "John Smith", "score": 75, "trend": "up"},
            {"name": "Jane Doe", "score": 82, "trend": "stable"},
        ],
        team_avg_score=78.5
    )

    # Low score alert
    alert_blocks = SlackFormatter.alert_low_score(
        rep_name="John Smith",
        dimension="Product Knowledge",
        score=55,
        recommendation="Review the product sheet and demo script"
    )

    # Objection pattern
    objection_blocks = SlackFormatter.objection_pattern_alert(
        rep_name="John Smith",
        objection_type="Price Objections",
        occurrence_count=5,
        examples=[
            "Client said 'That's too expensive'",
            "Customer asked for a 20% discount",
            "They want to compare with competitors first"
        ]
    )

    # Send to Slack
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    send_slack_notification(webhook_url, insight_blocks)


# Example 8: Integration with coaching analysis
def example_with_coaching_analysis():
    """Integrate notifications with coaching analysis results."""
    user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    user_email = "john@example.com"
    slack_webhook = "https://hooks.slack.com/services/..."

    # This would come from your coaching analysis
    coaching_results = {
        "user_id": user_id,
        "rep_name": "John Smith",
        "dimension": "objection_handling",
        "current_score": 65,
        "previous_score": 60,
        "improved": True,
        "insight": "Focus on directly addressing price concerns",
        "call_examples": [
            {
                "title": "Demo Call - Acme Corp",
                "quote": "The customer raised pricing concerns...",
            }
        ]
    }

    # Send notifications based on analysis
    if coaching_results["improved"]:
        # Send improvement celebration
        send_score_improvement_notifications(
            user_id=coaching_results["user_id"],
            user_email=user_email,
            slack_webhook_url=slack_webhook,
            rep_name=coaching_results["rep_name"],
            dimension=coaching_results["dimension"].replace("_", " ").title(),
            previous_score=coaching_results["previous_score"],
            current_score=coaching_results["current_score"],
        )
    else:
        # Send coaching insight
        send_coaching_insight_notifications(
            user_id=coaching_results["user_id"],
            user_email=user_email,
            slack_webhook_url=slack_webhook,
            rep_name=coaching_results["rep_name"],
            dimension_label=coaching_results["dimension"].replace("_", " ").title(),
            insight_description=coaching_results["insight"],
            current_score=coaching_results["current_score"],
            insight_id=f"insight-{user_id}",
        )


if __name__ == "__main__":
    # Run examples (comment out as needed)
    print("=" * 80)
    print("Notification System Examples")
    print("=" * 80)

    print("\n1. Coaching Insight:")
    # example_coaching_insight()

    print("\n2. Score Improvement:")
    # example_score_improvement()

    print("\n3. Create In-App Notification:")
    # example_create_inapp_notification()

    print("\n4. Manage Notifications:")
    # example_manage_notifications()

    print("\n5. Manage Preferences:")
    # example_manage_preferences()

    print("\n6. Batch Notifications:")
    # example_batch_notifications()

    print("\n7. Slack Formatting:")
    # example_slack_formatting()

    print("\n8. Integration Example:")
    # example_with_coaching_analysis()

    print("\nNote: Uncomment examples to run them")
