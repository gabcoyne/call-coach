"""
Notifications system for Call Coach.

Provides multi-channel notification delivery:
- Email notifications via templates
- Slack formatted messages
- In-app notification storage and retrieval
- Notification preferences management
"""

from notifications.in_app import InAppNotification, NotificationStore
from notifications.slack_formatter import SlackFormatter

__all__ = [
    "SlackFormatter",
    "InAppNotification",
    "NotificationStore",
]
