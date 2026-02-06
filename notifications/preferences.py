"""
User notification preferences management.

Allows users to control:
- Which notification types they receive
- Delivery channels (email, Slack, in-app)
- Frequency and timing
- Opt-out options
"""
import logging
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel
from db import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class DeliveryChannel(str, Enum):
    """Available notification delivery channels."""

    EMAIL = "email"
    SLACK = "slack"
    IN_APP = "in_app"


class NotificationTypePreference(BaseModel):
    """User preference for a notification type."""

    notification_type: str
    enabled: bool = True
    email: bool = True
    slack: bool = True
    in_app: bool = True
    frequency: str = "immediate"  # "immediate", "daily_digest", "weekly_digest", "never"


class UserNotificationPreferences(BaseModel):
    """Complete notification preferences for a user."""

    user_id: UUID
    weekly_reports: NotificationTypePreference
    coaching_insights: NotificationTypePreference
    score_improvements: NotificationTypePreference
    score_declines: NotificationTypePreference
    objection_patterns: NotificationTypePreference
    manager_summaries: NotificationTypePreference
    system_alerts: NotificationTypePreference
    opt_out_all: bool = False


class NotificationPreferencesManager:
    """Manages user notification preferences."""

    # Default preferences for new users
    DEFAULT_PREFERENCES = {
        "weekly_reports": {
            "notification_type": "weekly_reports",
            "enabled": True,
            "email": True,
            "slack": False,
            "in_app": True,
            "frequency": "immediate",
        },
        "coaching_insights": {
            "notification_type": "coaching_insights",
            "enabled": True,
            "email": True,
            "slack": True,
            "in_app": True,
            "frequency": "immediate",
        },
        "score_improvements": {
            "notification_type": "score_improvements",
            "enabled": True,
            "email": True,
            "slack": True,
            "in_app": True,
            "frequency": "immediate",
        },
        "score_declines": {
            "notification_type": "score_declines",
            "enabled": True,
            "email": True,
            "slack": False,
            "in_app": True,
            "frequency": "immediate",
        },
        "objection_patterns": {
            "notification_type": "objection_patterns",
            "enabled": True,
            "email": False,
            "slack": True,
            "in_app": True,
            "frequency": "weekly_digest",
        },
        "manager_summaries": {
            "notification_type": "manager_summaries",
            "enabled": True,
            "email": True,
            "slack": True,
            "in_app": True,
            "frequency": "immediate",
        },
        "system_alerts": {
            "notification_type": "system_alerts",
            "enabled": True,
            "email": True,
            "slack": False,
            "in_app": True,
            "frequency": "immediate",
        },
    }

    @staticmethod
    def get_preferences(user_id: UUID) -> UserNotificationPreferences:
        """
        Get notification preferences for a user.

        Args:
            user_id: User UUID

        Returns:
            UserNotificationPreferences object
        """
        try:
            prefs = fetch_all(
                """
                SELECT notification_type, enabled, email, slack, in_app, frequency
                FROM user_notification_preferences
                WHERE user_id = %s
                """,
                (user_id,),
            )

            if not prefs:
                return NotificationPreferencesManager._create_default_preferences(user_id)

            pref_dict = {}
            for pref in prefs:
                pref_dict[pref["notification_type"]] = NotificationTypePreference(
                    notification_type=pref["notification_type"],
                    enabled=pref["enabled"],
                    email=pref["email"],
                    slack=pref["slack"],
                    in_app=pref["in_app"],
                    frequency=pref["frequency"],
                )

            result = UserNotificationPreferences(user_id=user_id)
            for key, value in pref_dict.items():
                setattr(result, key, value)

            return result

        except Exception as e:
            logger.error(f"Failed to get preferences for user {user_id}: {e}")
            return NotificationPreferencesManager._create_default_preferences(user_id)

    @staticmethod
    def _create_default_preferences(user_id: UUID) -> UserNotificationPreferences:
        """Create default preferences for a user."""
        prefs = UserNotificationPreferences(user_id=user_id)
        for key, value in NotificationPreferencesManager.DEFAULT_PREFERENCES.items():
            setattr(prefs, key, NotificationTypePreference(**value))
        return prefs

    @staticmethod
    def update_notification_type_preference(
        user_id: UUID,
        notification_type: str,
        enabled: Optional[bool] = None,
        email: Optional[bool] = None,
        slack: Optional[bool] = None,
        in_app: Optional[bool] = None,
        frequency: Optional[str] = None,
    ) -> bool:
        """
        Update preference for a specific notification type.

        Args:
            user_id: User UUID
            notification_type: Type of notification to update
            enabled: Whether notifications are enabled
            email: Whether to send via email
            slack: Whether to send via Slack
            in_app: Whether to send in-app
            frequency: Frequency of notifications

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build update clause dynamically
            updates = []
            params = []

            if enabled is not None:
                updates.append("enabled = %s")
                params.append(enabled)

            if email is not None:
                updates.append("email = %s")
                params.append(email)

            if slack is not None:
                updates.append("slack = %s")
                params.append(slack)

            if in_app is not None:
                updates.append("in_app = %s")
                params.append(in_app)

            if frequency is not None:
                updates.append("frequency = %s")
                params.append(frequency)

            if not updates:
                return False

            params.extend([user_id, notification_type])

            execute_query(
                f"""
                INSERT INTO user_notification_preferences
                (user_id, notification_type, enabled, email, slack, in_app, frequency)
                VALUES (%s, %s, COALESCE(%s, true), COALESCE(%s, true),
                        COALESCE(%s, false), COALESCE(%s, true), COALESCE(%s, 'immediate'))
                ON CONFLICT (user_id, notification_type) DO UPDATE SET
                {', '.join(updates)}
                """,
                [user_id, notification_type] + params[:4] + (params[4:5] or [False])
                + (params[5:6] or [True])
                + (params[6:7] or ["immediate"])
                + params[7:],
            )

            logger.info(f"Updated preference for {notification_type} for user {user_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to update preference for {notification_type} for user {user_id}: {e}"
            )
            return False

    @staticmethod
    def set_opt_out_all(user_id: UUID, opt_out: bool) -> bool:
        """
        Opt out of all notifications.

        Args:
            user_id: User UUID
            opt_out: Whether to opt out of all notifications

        Returns:
            True if successful, False otherwise
        """
        try:
            execute_query(
                """
                UPDATE user_notification_preferences
                SET enabled = %s
                WHERE user_id = %s
                """,
                (not opt_out, user_id),
            )

            logger.info(f"Set opt_out_all={opt_out} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to set opt_out_all for user {user_id}: {e}")
            return False

    @staticmethod
    def should_send_notification(
        user_id: UUID,
        notification_type: str,
        channel: DeliveryChannel,
    ) -> bool:
        """
        Check if a notification should be sent to a user via a specific channel.

        Args:
            user_id: User UUID
            notification_type: Type of notification
            channel: Delivery channel

        Returns:
            True if notification should be sent, False otherwise
        """
        try:
            pref = fetch_one(
                """
                SELECT enabled, email, slack, in_app
                FROM user_notification_preferences
                WHERE user_id = %s
                AND notification_type = %s
                """,
                (user_id, notification_type),
            )

            if not pref:
                # Use defaults
                default = NotificationPreferencesManager.DEFAULT_PREFERENCES.get(notification_type)
                if not default:
                    return False
                pref = default

            if not pref.get("enabled", True):
                return False

            channel_key = channel.value
            return pref.get(channel_key, False)

        except Exception as e:
            logger.error(
                f"Failed to check notification preference for user {user_id}: {e}"
            )
            return False

    @staticmethod
    def get_users_with_preference_enabled(
        notification_type: str,
        channel: DeliveryChannel,
    ) -> list[UUID]:
        """
        Get all users who have a notification type enabled for a specific channel.

        Args:
            notification_type: Type of notification
            channel: Delivery channel

        Returns:
            List of user UUIDs
        """
        try:
            channel_column = channel.value
            rows = fetch_all(
                f"""
                SELECT user_id
                FROM user_notification_preferences
                WHERE notification_type = %s
                AND enabled = true
                AND {channel_column} = true
                """,
                (notification_type,),
            )

            return [row["user_id"] for row in rows]

        except Exception as e:
            logger.error(f"Failed to get users with preference enabled: {e}")
            return []
