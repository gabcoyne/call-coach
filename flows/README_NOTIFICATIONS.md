# Notification System Documentation

## Overview

The Call Coach notification system provides multi-channel delivery of coaching insights, score updates, and weekly reports to sales reps. Notifications can be delivered via:

- **Email** - HTML templates with responsive design
- **Slack** - Formatted Block Kit messages with interactive buttons
- **In-App** - Stored in database, displayed in web UI in real-time or via polling

Users control how they receive notifications through comprehensive preference management.

## Architecture

### Components

1. **Email Templates** (`reports/templates/`)
   - `weekly_report_enhanced.html` - Enhanced weekly report with score visualization
   - `coaching_insight.html` - Single coaching insight notification
   - `skill_improvement.html` - Celebration email for score improvements
   - `manager_summary.html` - Team overview for managers
   - `welcome.html` - Onboarding email for new users

2. **Slack Formatter** (`notifications/slack_formatter.py`)
   - `SlackFormatter` class with static methods for each notification type
   - Returns Block Kit formatted JSON for Slack API
   - Includes interactive buttons for CTAs

3. **In-App Notification System** (`notifications/in_app.py`)
   - `InAppNotification` - Pydantic model for notifications
   - `NotificationStore` - CRUD operations and querying
   - `NotificationBuilder` - Fluent API for building notifications
   - Database backed storage with expiration support

4. **Notification Preferences** (`notifications/preferences.py`)
   - `NotificationPreferencesManager` - User preference management
   - Per-notification-type control (enabled/disabled)
   - Per-channel control (email, Slack, in-app)
   - Frequency settings (immediate, daily digest, weekly digest)

5. **Notification Flow** (`flows/notifications.py`)
   - Prefect flow for orchestrating multi-channel delivery
   - Tasks for email, Slack, and in-app delivery
   - Preference-aware routing

## Usage

### Sending Coaching Insights

```python
from flows.notifications import send_coaching_insight_notifications

results = send_coaching_insight_notifications(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    user_email="rep@example.com",
    slack_webhook_url="https://hooks.slack.com/services/...",
    rep_name="John Smith",
    dimension_label="Objection Handling",
    insight_description="You could improve your handling of price objections...",
    current_score=65.0,
    insight_id="insight-123",
    app_url="https://callcoach.ai"
)

# Results: {"email": True, "slack": True, "in_app": True}
```

### Sending Score Improvements

```python
from flows.notifications import send_score_improvement_notifications

results = send_score_improvement_notifications(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    user_email="rep@example.com",
    slack_webhook_url="https://hooks.slack.com/services/...",
    rep_name="John Smith",
    dimension="Objection Handling",
    previous_score=60.0,
    current_score=75.0,
    app_url="https://callcoach.ai"
)
```

### Creating In-App Notifications Directly

```python
from notifications.in_app import NotificationStore, NotificationBuilder, NotificationType, NotificationPriority

# Using builder pattern
notification = (
    NotificationBuilder(user_id, NotificationType.COACHING_INSIGHT)
    .title("Objection Handling Insight")
    .message("You could improve your handling of price objections...")
    .priority(NotificationPriority.HIGH)
    .action("https://callcoach.ai/insights/123", "View")
    .expires_in(24)  # 24 hours
    .build()
)

notification_id = NotificationStore.create(notification)
```

### Managing User Preferences

```python
from notifications.preferences import NotificationPreferencesManager

# Get current preferences
prefs = NotificationPreferencesManager.get_preferences(user_id)

# Update a specific notification type
NotificationPreferencesManager.update_notification_type_preference(
    user_id=user_id,
    notification_type="coaching_insights",
    email=True,
    slack=True,
    in_app=True,
    frequency="immediate"
)

# Check if user should receive notification
should_send = NotificationPreferencesManager.should_send_notification(
    user_id=user_id,
    notification_type="coaching_insights",
    channel=DeliveryChannel.EMAIL
)
```

### Retrieving Notifications

```python
from notifications.in_app import NotificationStore

# Get all unread notifications for a user
unread = NotificationStore.get_user_notifications(
    user_id=user_id,
    unread_only=True,
    limit=20
)

# Get unread count
count = NotificationStore.get_unread_count(user_id)

# Mark as read
NotificationStore.mark_as_read(notification_id)

# Archive old notifications
NotificationStore.archive(notification_id)
```

## Database Schema

### notifications table
Stores all in-app notifications with support for expiration and archival.

```sql
- id (UUID, PK) - Unique notification ID
- user_id (UUID, FK) - User receiving the notification
- type (VARCHAR) - Notification type (coaching_insight, score_improvement, etc.)
- title (VARCHAR) - Short title
- message (TEXT) - Full message content
- priority (VARCHAR) - low/medium/high/critical
- read (BOOLEAN) - Whether notification has been read
- archived (BOOLEAN) - Whether notification is archived
- action_url (VARCHAR) - Optional URL for action button
- action_label (VARCHAR) - Optional label for action button
- data (JSONB) - Additional structured data
- created_at (TIMESTAMP) - When created
- expires_at (TIMESTAMP) - Optional expiration time
- read_at (TIMESTAMP) - When marked as read
```

### user_notification_preferences table
Stores user's notification delivery preferences.

```sql
- user_id (UUID, FK) - User
- notification_type (VARCHAR) - Type of notification
- enabled (BOOLEAN) - Whether enabled
- email (BOOLEAN) - Send via email
- slack (BOOLEAN) - Send via Slack
- in_app (BOOLEAN) - Send in-app
- frequency (VARCHAR) - immediate/daily_digest/weekly_digest/never
```

### notification_delivery_log table
Audit log of all notification deliveries.

```sql
- id (UUID, PK)
- notification_id (UUID, FK)
- user_id (UUID)
- channel (VARCHAR) - email/slack/in_app
- status (VARCHAR) - sent/failed/bounced/unsubscribed
- error_message (TEXT)
- sent_at (TIMESTAMP)
```

## Email Templates

All templates are responsive and built with:
- Mobile-first design
- Inline CSS for email compatibility
- Dark/light mode awareness
- Accessible color contrast
- Interactive CTAs

### Template Variables

Each template expects specific context variables. Examples:

**coaching_insight.html**
```python
{
    "rep_name": "John Smith",
    "dimension_label": "Objection Handling",
    "insight_description": "...",
    "current_score": 65,
    "previous_score": 60,
    "score_class": "low|medium|high",
    "quote": "...",
    "call_reference": {...},
    "app_url": "https://callcoach.ai",
    "insight_id": "...",
    "unsubscribe_token": "..."
}
```

**skill_improvement.html**
```python
{
    "rep_name": "John Smith",
    "dimension_label": "Objection Handling",
    "previous_score": 60,
    "current_score": 75,
    "improvement_points": 15,
    "improvement_percent": 25,
    "performance_streak": 3,
    "calls_analyzed": 12,
    "coaching_sessions": 5,
    "overall_score": 72,
    "peer_percentile": 75,
    "next_focus_areas": [...],
    "app_url": "https://callcoach.ai"
}
```

**manager_summary.html**
```python
{
    "period_label": "This Week",
    "week_start": "2025-02-03",
    "week_end": "2025-02-09",
    "team_size": 8,
    "total_calls": 45,
    "avg_team_score": 72,
    "improved_count": 6,
    "team_members": [
        {
            "name": "John Smith",
            "calls": 5,
            "sessions": 2,
            "score": 75,
            "trend": "up",
            "trend_change": "+5"
        },
        ...
    ],
    "key_insights": [...],
    "team_recommendations": [...],
    "app_url": "https://callcoach.ai"
}
```

## Slack Messages

Slack notifications use Block Kit format for rich formatting and interactivity.

```python
from notifications.slack_formatter import SlackFormatter

# Coaching insight
blocks = SlackFormatter.coaching_insight(
    rep_name="John Smith",
    dimension="Objection Handling",
    score=65,
    insight_description="...",
    insight_id="123"
)

# Score improvement
blocks = SlackFormatter.score_improvement(
    rep_name="John Smith",
    dimension="Objection Handling",
    previous_score=60,
    current_score=75
)

# Weekly summary
blocks = SlackFormatter.weekly_summary(
    week_start=datetime.now(),
    team_members=[...],
    team_avg_score=72
)
```

## Configuration

### Environment Variables

Email delivery requires one of:
- `SENDGRID_API_KEY` - SendGrid API key
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` - SMTP settings
- Default to console logging if none configured

Slack delivery requires:
- User's Slack webhook URL (stored in user preferences or passed directly)

### Default Preferences

New users get these default preferences:

```python
{
    "weekly_reports": {
        "enabled": True,
        "email": True,
        "slack": False,
        "in_app": True,
        "frequency": "immediate"
    },
    "coaching_insights": {
        "enabled": True,
        "email": True,
        "slack": True,
        "in_app": True,
        "frequency": "immediate"
    },
    "score_improvements": {
        "enabled": True,
        "email": True,
        "slack": True,
        "in_app": True,
        "frequency": "immediate"
    },
    "score_declines": {
        "enabled": True,
        "email": True,
        "slack": False,
        "in_app": True,
        "frequency": "immediate"
    },
    "objection_patterns": {
        "enabled": True,
        "email": False,
        "slack": True,
        "in_app": True,
        "frequency": "weekly_digest"
    }
}
```

## Best Practices

1. **Always check preferences before sending** - Use `NotificationPreferencesManager.should_send_notification()`

2. **Use expiration times** - Set `expires_at` for time-sensitive notifications (24-48 hours typically)

3. **Include action URLs** - Provide direct links to relevant sections of the app

4. **Batch notifications** - Use `send_notifications_flow()` with lists of requests

5. **Monitor delivery failures** - Query `notification_delivery_log` regularly

6. **Clean up old notifications** - Run `NotificationStore.cleanup_expired()` periodically

7. **Test email rendering** - Use Litmus or Email on Acid to validate HTML

## Monitoring

### Key Metrics

```python
# Get unread count
unread = NotificationStore.get_unread_count(user_id)

# Get delivery stats
from db.queries.notifications import get_delivery_stats_by_channel
stats = get_delivery_stats_by_channel(user_id)

# Monitor failed deliveries
failed = fetch_all("""
    SELECT * FROM notification_delivery_log
    WHERE status = 'failed'
    AND sent_at > NOW() - INTERVAL '1 day'
""")
```

### Performance Considerations

- Notifications table uses partitioning by month for performance
- Indexes on `user_id`, `created_at`, `type` for common queries
- Expired notifications are automatically cleaned up
- Recommend archiving read notifications after 30 days

## Troubleshooting

### Notifications not appearing

1. Check user preferences: `NotificationPreferencesManager.get_preferences(user_id)`
2. Check delivery log: `notification_delivery_log` table
3. Check expiration: `expires_at` field in `notifications` table
4. Verify email configuration: Check environment variables

### Email sending failures

1. Verify SendGrid API key or SMTP settings
2. Check email address format
3. Review `notification_delivery_log` for error messages
4. Test with console provider for debugging

### Performance issues

1. Check notification count per user (recommend archiving old ones)
2. Review partition strategy in migration
3. Monitor database query performance
4. Consider batch operations for bulk sends

## Future Enhancements

- SMS notifications
- Push notifications for mobile app
- Digest scheduling with preferences
- Advanced segmentation (time zones, role-based)
- A/B testing for subject lines
- Webhook integrations for custom channels
