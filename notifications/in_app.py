"""
In-app notification system for Call Coach.

Manages storage, retrieval, and lifecycle of notifications displayed in the application.
Supports real-time updates via WebSocket and polling-based delivery.
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from db import execute_query, fetch_all, fetch_one

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of in-app notifications."""

    COACHING_INSIGHT = "coaching_insight"
    SCORE_IMPROVEMENT = "score_improvement"
    SCORE_DECLINE = "score_decline"
    WEEKLY_REPORT = "weekly_report"
    MANAGER_SUMMARY = "manager_summary"
    OBJECTION_PATTERN = "objection_pattern"
    ACHIEVEMENT = "achievement"
    ALERT = "alert"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    """Priority levels for notifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InAppNotification(BaseModel):
    """Model for in-app notifications."""

    id: UUID | None = Field(default_factory=uuid4)
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    read: bool = False
    archived: bool = False
    action_url: str | None = None
    action_label: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    read_at: datetime | None = None

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class NotificationStore:
    """Manages in-app notification storage and retrieval."""

    @staticmethod
    def create(notification: InAppNotification) -> UUID:
        """
        Create a new notification.

        Args:
            notification: InAppNotification instance

        Returns:
            Notification UUID
        """
        try:
            query = """
            INSERT INTO notifications (
                id, user_id, type, title, message, priority, read,
                archived, action_url, action_label, data, created_at,
                expires_at, read_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            execute_query(
                query,
                (
                    notification.id,
                    notification.user_id,
                    notification.type.value,
                    notification.title,
                    notification.message,
                    notification.priority.value,
                    notification.read,
                    notification.archived,
                    notification.action_url,
                    notification.action_label,
                    json.dumps(notification.data),
                    notification.created_at,
                    notification.expires_at,
                    notification.read_at,
                ),
            )
            logger.info(f"Created notification {notification.id} for user {notification.user_id}")
            return notification.id

        except Exception as e:
            logger.error(f"Failed to create notification: {e}", exc_info=True)
            raise

    @staticmethod
    def get(notification_id: UUID) -> InAppNotification | None:
        """
        Get a notification by ID.

        Args:
            notification_id: Notification UUID

        Returns:
            InAppNotification or None if not found
        """
        try:
            row = fetch_one(
                """
                SELECT id, user_id, type, title, message, priority, read,
                       archived, action_url, action_label, data, created_at,
                       expires_at, read_at
                FROM notifications
                WHERE id = %s
                """,
                (notification_id,),
            )

            if not row:
                return None

            return _row_to_notification(row)

        except Exception as e:
            logger.error(f"Failed to get notification {notification_id}: {e}", exc_info=True)
            return None

    @staticmethod
    def get_user_notifications(
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
        include_archived: bool = False,
    ) -> list[InAppNotification]:
        """
        Get notifications for a user.

        Args:
            user_id: User UUID
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            unread_only: Only return unread notifications
            include_archived: Include archived notifications

        Returns:
            List of InAppNotification
        """
        try:
            where_clauses = ["user_id = %s"]
            params = [user_id]

            if not include_archived:
                where_clauses.append("archived = false")

            if unread_only:
                where_clauses.append("read = false")

            # Filter out expired notifications
            where_clauses.append("(expires_at IS NULL OR expires_at > NOW())")

            where_clause = " AND ".join(where_clauses)

            rows = fetch_all(
                f"""
                SELECT id, user_id, type, title, message, priority, read,
                       archived, action_url, action_label, data, created_at,
                       expires_at, read_at
                FROM notifications
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )

            return [_row_to_notification(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get notifications for user {user_id}: {e}", exc_info=True)
            return []

    @staticmethod
    def mark_as_read(notification_id: UUID) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: Notification UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            execute_query(
                """
                UPDATE notifications
                SET read = true, read_at = NOW()
                WHERE id = %s
                """,
                (notification_id,),
            )
            logger.info(f"Marked notification {notification_id} as read")
            return True

        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {e}")
            return False

    @staticmethod
    def mark_multiple_as_read(notification_ids: list[UUID]) -> bool:
        """
        Mark multiple notifications as read.

        Args:
            notification_ids: List of notification UUIDs

        Returns:
            True if successful, False otherwise
        """
        try:
            placeholders = ",".join(["%s"] * len(notification_ids))
            execute_query(
                f"""
                UPDATE notifications
                SET read = true, read_at = NOW()
                WHERE id IN ({placeholders})
                """,
                notification_ids,
            )
            logger.info(f"Marked {len(notification_ids)} notifications as read")
            return True

        except Exception as e:
            logger.error(f"Failed to mark notifications as read: {e}")
            return False

    @staticmethod
    def archive(notification_id: UUID) -> bool:
        """
        Archive a notification.

        Args:
            notification_id: Notification UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            execute_query(
                """
                UPDATE notifications
                SET archived = true
                WHERE id = %s
                """,
                (notification_id,),
            )
            logger.info(f"Archived notification {notification_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to archive notification {notification_id}: {e}")
            return False

    @staticmethod
    def archive_multiple(notification_ids: list[UUID]) -> bool:
        """
        Archive multiple notifications.

        Args:
            notification_ids: List of notification UUIDs

        Returns:
            True if successful, False otherwise
        """
        try:
            placeholders = ",".join(["%s"] * len(notification_ids))
            execute_query(
                f"""
                UPDATE notifications
                SET archived = true
                WHERE id IN ({placeholders})
                """,
                notification_ids,
            )
            logger.info(f"Archived {len(notification_ids)} notifications")
            return True

        except Exception as e:
            logger.error(f"Failed to archive notifications: {e}")
            return False

    @staticmethod
    def delete(notification_id: UUID) -> bool:
        """
        Delete a notification.

        Args:
            notification_id: Notification UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            execute_query(
                """
                DELETE FROM notifications
                WHERE id = %s
                """,
                (notification_id,),
            )
            logger.info(f"Deleted notification {notification_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete notification {notification_id}: {e}")
            return False

    @staticmethod
    def get_unread_count(user_id: UUID) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user_id: User UUID

        Returns:
            Count of unread notifications
        """
        try:
            result = fetch_one(
                """
                SELECT COUNT(*) as count
                FROM notifications
                WHERE user_id = %s
                AND read = false
                AND archived = false
                AND (expires_at IS NULL OR expires_at > NOW())
                """,
                (user_id,),
            )
            return result.get("count", 0) if result else 0

        except Exception as e:
            logger.error(f"Failed to get unread count for user {user_id}: {e}")
            return 0

    @staticmethod
    def cleanup_expired() -> int:
        """
        Delete expired notifications (older than expiry date).

        Returns:
            Number of notifications deleted
        """
        try:
            # Get count of expired
            count_result = fetch_one(
                """
                SELECT COUNT(*) as count
                FROM notifications
                WHERE expires_at IS NOT NULL
                AND expires_at < NOW()
                """
            )
            count = count_result.get("count", 0) if count_result else 0

            # Delete expired
            if count > 0:
                execute_query(
                    """
                    DELETE FROM notifications
                    WHERE expires_at IS NOT NULL
                    AND expires_at < NOW()
                    """
                )
                logger.info(f"Cleaned up {count} expired notifications")

            return count

        except Exception as e:
            logger.error(f"Failed to cleanup expired notifications: {e}")
            return 0


class NotificationBuilder:
    """Builder for creating notifications with fluent API."""

    def __init__(self, user_id: UUID, notification_type: NotificationType):
        """Initialize notification builder."""
        self.notification = InAppNotification(
            user_id=user_id,
            type=notification_type,
            title="",
            message="",
        )

    def title(self, title: str) -> "NotificationBuilder":
        """Set notification title."""
        self.notification.title = title
        return self

    def message(self, message: str) -> "NotificationBuilder":
        """Set notification message."""
        self.notification.message = message
        return self

    def priority(self, priority: NotificationPriority) -> "NotificationBuilder":
        """Set notification priority."""
        self.notification.priority = priority
        return self

    def action(self, url: str, label: str = "View") -> "NotificationBuilder":
        """Set notification action."""
        self.notification.action_url = url
        self.notification.action_label = label
        return self

    def expires_in(self, hours: int) -> "NotificationBuilder":
        """Set notification expiration time."""
        self.notification.expires_at = datetime.utcnow() + timedelta(hours=hours)
        return self

    def data(self, data: dict[str, Any]) -> "NotificationBuilder":
        """Set notification data."""
        self.notification.data = data
        return self

    def build(self) -> InAppNotification:
        """Build and return the notification."""
        return self.notification


def _row_to_notification(row: dict[str, Any]) -> InAppNotification:
    """Convert database row to InAppNotification."""
    data = {}
    if row.get("data"):
        if isinstance(row["data"], str):
            data = json.loads(row["data"])
        else:
            data = row["data"]

    return InAppNotification(
        id=row["id"],
        user_id=row["user_id"],
        type=NotificationType(row["type"]),
        title=row["title"],
        message=row["message"],
        priority=NotificationPriority(row["priority"]),
        read=row["read"],
        archived=row["archived"],
        action_url=row.get("action_url"),
        action_label=row.get("action_label"),
        data=data,
        created_at=row["created_at"],
        expires_at=row.get("expires_at"),
        read_at=row.get("read_at"),
    )
