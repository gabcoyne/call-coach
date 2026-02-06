"""
Database queries for notification system.

Complements the NotificationStore class with raw SQL operations.
"""


def get_user_notification_summary(user_id: str) -> str:
    """Get summary counts for a user's notifications."""
    return """
    SELECT
        COUNT(*) FILTER (WHERE read = false AND archived = false) as unread_count,
        COUNT(*) FILTER (WHERE archived = false) as total_unarchived,
        MAX(created_at) as latest_notification
    FROM notifications
    WHERE user_id = %s
    AND (expires_at IS NULL OR expires_at > NOW())
    """


def get_notifications_by_type_and_user(user_id: str, notification_type: str) -> str:
    """Get notifications of a specific type for a user."""
    return """
    SELECT id, user_id, type, title, message, priority, read, archived,
           action_url, action_label, data, created_at, expires_at, read_at
    FROM notifications
    WHERE user_id = %s
    AND type = %s
    AND (expires_at IS NULL OR expires_at > NOW())
    AND archived = false
    ORDER BY created_at DESC
    LIMIT 50
    """


def get_notifications_by_priority(user_id: str, priority: str) -> str:
    """Get notifications of a specific priority level."""
    return """
    SELECT id, user_id, type, title, message, priority, read, archived,
           action_url, action_label, data, created_at, expires_at, read_at
    FROM notifications
    WHERE user_id = %s
    AND priority = %s
    AND (expires_at IS NULL OR expires_at > NOW())
    AND archived = false
    ORDER BY created_at DESC
    LIMIT 50
    """


def get_unread_count_by_type(user_id: str) -> str:
    """Get unread notification counts grouped by type."""
    return """
    SELECT type, COUNT(*) as count
    FROM notifications
    WHERE user_id = %s
    AND read = false
    AND archived = false
    AND (expires_at IS NULL OR expires_at > NOW())
    GROUP BY type
    ORDER BY count DESC
    """


def cleanup_old_read_notifications(days: int = 30) -> str:
    """Delete read notifications older than specified days."""
    return f"""
    DELETE FROM notifications
    WHERE read = true
    AND read_at < NOW() - INTERVAL '{days} days'
    AND archived = true
    """


def delete_expired_notifications() -> str:
    """Delete all expired notifications."""
    return """
    DELETE FROM notifications
    WHERE expires_at IS NOT NULL
    AND expires_at < NOW()
    """


def get_delivery_stats_for_notification(notification_id: str) -> str:
    """Get delivery statistics for a notification."""
    return """
    SELECT
        channel,
        status,
        COUNT(*) as count
    FROM notification_delivery_log
    WHERE notification_id = %s
    GROUP BY channel, status
    """


def get_delivery_stats_by_channel(user_id: str, since: str = None) -> str:
    """Get user's delivery statistics by channel."""
    where_clause = "WHERE user_id = %s"
    if since:
        where_clause += " AND sent_at >= %s"

    return f"""
    SELECT
        channel,
        status,
        COUNT(*) as count
    FROM notification_delivery_log
    {where_clause}
    GROUP BY channel, status
    """


def get_failed_delivery_attempts(limit: int = 100) -> str:
    """Get recent failed delivery attempts."""
    return f"""
    SELECT
        ndl.id,
        ndl.notification_id,
        ndl.user_id,
        ndl.channel,
        ndl.error_message,
        ndl.sent_at,
        n.type as notification_type,
        n.title
    FROM notification_delivery_log ndl
    LEFT JOIN notifications n ON ndl.notification_id = n.id
    WHERE ndl.status = 'failed'
    ORDER BY ndl.sent_at DESC
    LIMIT {limit}
    """


def get_users_not_receiving_notifications() -> str:
    """Get users who have all notifications disabled."""
    return """
    SELECT user_id, COUNT(*) as disabled_types
    FROM user_notification_preferences
    WHERE enabled = false
    GROUP BY user_id
    HAVING COUNT(*) = (SELECT COUNT(DISTINCT notification_type) FROM user_notification_preferences)
    """
