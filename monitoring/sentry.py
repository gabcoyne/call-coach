"""
Sentry error tracking and exception reporting.

Captures exceptions with rich context including user information, call IDs,
request correlation IDs, and performance metrics for debugging and monitoring.
"""
import logging
import os
from typing import Any, Optional
from datetime import datetime

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

logger = logging.getLogger(__name__)


class SentryConfig:
    """Sentry configuration and initialization."""

    def __init__(
        self,
        dsn: Optional[str] = None,
        environment: Optional[str] = None,
        traces_sample_rate: float = 0.1,
        profiles_sample_rate: float = 0.1,
        error_sample_rate: float = 1.0,
        enable_profiling: bool = True,
    ):
        """
        Initialize Sentry configuration.

        Args:
            dsn: Sentry DSN (defaults to SENTRY_DSN env var)
            environment: Environment name (development, staging, production)
            traces_sample_rate: Proportion of transactions to sample (0.0-1.0)
            profiles_sample_rate: Proportion of profiles to sample (0.0-1.0)
            error_sample_rate: Proportion of errors to sample (0.0-1.0)
            enable_profiling: Enable performance profiling
        """
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.traces_sample_rate = traces_sample_rate
        self.profiles_sample_rate = profiles_sample_rate
        self.error_sample_rate = error_sample_rate
        self.enable_profiling = enable_profiling
        self.is_enabled = bool(self.dsn)

    def initialize(self) -> bool:
        """
        Initialize Sentry client.

        Returns:
            True if Sentry was successfully initialized, False otherwise
        """
        if not self.is_enabled:
            logger.warning("Sentry disabled (no DSN configured)")
            return False

        try:
            integrations = [
                FastApiIntegration(transaction_style="endpoint"),
                StarletteIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.WARNING,
                ),
                HttpxIntegration(),
            ]

            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=integrations,
                traces_sample_rate=self.traces_sample_rate,
                profiles_sample_rate=self.profiles_sample_rate if self.enable_profiling else 0.0,
                sample_rate=self.error_sample_rate,
                attach_stacktrace=True,
                max_breadcrumbs=50,
                include_local_variables=True,
                release=os.getenv("APP_VERSION", "unknown"),
            )

            logger.info(f"Sentry initialized for {self.environment} environment")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
            return False


def capture_exception(
    exception: Exception,
    context: Optional[dict[str, Any]] = None,
    level: str = "error",
) -> Optional[str]:
    """
    Capture an exception with context.

    Args:
        exception: Exception to capture
        context: Additional context data (user, call_id, rep_id, etc.)
        level: Error level (error, warning, info)

    Returns:
        Event ID for tracking, or None if Sentry is disabled
    """
    if not sentry_sdk.Hub.current.client:
        logger.error(f"Exception occurred: {exception}", exc_info=True)
        return None

    with sentry_sdk.push_scope() as scope:
        # Set user context
        if context:
            if "user_id" in context:
                scope.user = {"id": context["user_id"]}
            if "email" in context:
                scope.user = {**(scope.user or {}), "email": context["email"]}

            # Set call and request context
            if "call_id" in context:
                scope.set_tag("call_id", context["call_id"])
            if "rep_id" in context:
                scope.set_tag("rep_id", context["rep_id"])
            if "opportunity_id" in context:
                scope.set_tag("opportunity_id", context["opportunity_id"])
            if "correlation_id" in context:
                scope.set_tag("correlation_id", context["correlation_id"])

            # Set additional context data
            for key, value in context.items():
                if key not in ["user_id", "email", "call_id", "rep_id", "opportunity_id", "correlation_id"]:
                    scope.set_context("request_context", {key: value})

        # Capture exception with level
        scope.level = level
        event_id = sentry_sdk.capture_exception(exception)
        logger.error(f"Exception captured (ID: {event_id}): {exception}")
        return event_id


def capture_message(
    message: str,
    context: Optional[dict[str, Any]] = None,
    level: str = "info",
) -> Optional[str]:
    """
    Capture a message with context.

    Args:
        message: Message to capture
        context: Additional context data
        level: Log level (debug, info, warning, error)

    Returns:
        Event ID for tracking, or None if Sentry is disabled
    """
    if not sentry_sdk.Hub.current.client:
        logger.log(
            getattr(logging, level.upper(), logging.INFO),
            message
        )
        return None

    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context("message_context", {key: value})

        scope.level = level
        event_id = sentry_sdk.capture_message(message, level=level)
        return event_id


def add_breadcrumb(
    message: str,
    category: str = "custom",
    level: str = "info",
    data: Optional[dict[str, Any]] = None,
) -> None:
    """
    Add a breadcrumb for request tracing.

    Args:
        message: Breadcrumb message
        category: Breadcrumb category (ui.click, http, database, etc.)
        level: Log level (debug, info, warning, error)
        data: Additional breadcrumb data
    """
    if not sentry_sdk.Hub.current.client:
        return

    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {},
        timestamp=datetime.utcnow(),
    )


def set_user_context(user_id: str, email: Optional[str] = None) -> None:
    """
    Set user context for error tracking.

    Args:
        user_id: User ID
        email: User email address
    """
    if not sentry_sdk.Hub.current.client:
        return

    sentry_sdk.set_user({
        "id": user_id,
        **({"email": email} if email else {})
    })


def set_tags(tags: dict[str, str]) -> None:
    """
    Set tags for filtering and grouping errors.

    Args:
        tags: Dictionary of tag keys and values
    """
    if not sentry_sdk.Hub.current.client:
        return

    for key, value in tags.items():
        sentry_sdk.set_tag(key, value)


# Global Sentry configuration instance
_sentry_config: Optional[SentryConfig] = None


def get_sentry_config() -> SentryConfig:
    """Get or create global Sentry configuration."""
    global _sentry_config
    if _sentry_config is None:
        _sentry_config = SentryConfig()
    return _sentry_config


def initialize_sentry(
    dsn: Optional[str] = None,
    environment: Optional[str] = None,
) -> bool:
    """Initialize Sentry monitoring."""
    config = SentryConfig(dsn=dsn, environment=environment)
    result = config.initialize()
    globals()["_sentry_config"] = config
    return result
