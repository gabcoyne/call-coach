"""
DLT Pipeline Error Handling and Retry Logic

Provides custom exceptions, retry configuration, and alerting hooks
for robust error handling in the BigQuery to Postgres sync pipeline.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC
from enum import Enum
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Custom Exceptions
# =============================================================================


class PipelineError(Exception):
    """Base exception for all pipeline errors."""

    def __init__(self, message: str, source: str | None = None, details: dict | None = None):
        self.source = source
        self.details = details or {}
        super().__init__(message)


class BigQueryQuotaError(PipelineError):
    """Raised when BigQuery quota or rate limits are exceeded.

    These errors are retryable after a backoff period.
    Common scenarios:
    - Quota exceeded: rateLimitExceeded, quotaExceeded
    - Too many concurrent queries
    - Bytes billed quota exceeded
    """

    def __init__(
        self,
        message: str,
        quota_type: str | None = None,
        retry_after_seconds: int | None = None,
        **kwargs,
    ):
        self.quota_type = quota_type
        self.retry_after_seconds = retry_after_seconds or 60
        super().__init__(message, **kwargs)


class BigQueryNotFoundError(PipelineError):
    """Raised when BigQuery table or dataset is not found.

    These errors are NOT retryable - they indicate configuration issues.
    """

    def __init__(self, message: str, table_name: str | None = None, **kwargs):
        self.table_name = table_name
        super().__init__(message, **kwargs)


class PostgresConnectionError(PipelineError):
    """Raised when Postgres connection fails.

    These errors are retryable - they may indicate transient network issues.
    Common scenarios:
    - Connection timeout
    - Too many connections
    - Server unavailable
    """

    def __init__(
        self,
        message: str,
        host: str | None = None,
        port: int | None = None,
        **kwargs,
    ):
        self.host = host
        self.port = port
        super().__init__(message, **kwargs)


class PostgresConstraintError(PipelineError):
    """Raised when Postgres constraint violations occur.

    These errors are NOT retryable for the same data.
    Common scenarios:
    - Unique constraint violation
    - Foreign key constraint violation
    - Check constraint violation
    """

    def __init__(self, message: str, constraint_name: str | None = None, **kwargs):
        self.constraint_name = constraint_name
        super().__init__(message, **kwargs)


class SourceFailureError(PipelineError):
    """Raised when a source fails permanently after all retries."""

    def __init__(
        self,
        message: str,
        source_name: str,
        original_error: Exception | None = None,
        **kwargs,
    ):
        self.source_name = source_name
        self.original_error = original_error
        super().__init__(message, source=source_name, **kwargs)


# =============================================================================
# Retry Configuration
# =============================================================================


class RetryStrategy(Enum):
    """Retry strategies for different error types."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay_seconds: Initial delay before first retry (default: 1)
        max_delay_seconds: Maximum delay between retries (default: 300)
        exponential_base: Base for exponential backoff (default: 2)
        strategy: Retry strategy to use (default: EXPONENTIAL)
        retryable_exceptions: Tuple of exception types that should trigger retry
    """

    max_retries: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 300.0
    exponential_base: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retryable_exceptions: tuple = field(
        default_factory=lambda: (
            BigQueryQuotaError,
            PostgresConnectionError,
            ConnectionError,
            TimeoutError,
        )
    )

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt.

        Args:
            attempt: The current retry attempt (0-indexed)

        Returns:
            Delay in seconds before the next retry
        """
        if self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay_seconds * (self.exponential_base**attempt)
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.initial_delay_seconds * (attempt + 1)
        else:  # FIXED
            delay = self.initial_delay_seconds

        return min(delay, self.max_delay_seconds)


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay_seconds=1.0,
    max_delay_seconds=300.0,
    exponential_base=2.0,
    strategy=RetryStrategy.EXPONENTIAL,
)


def with_retry(
    config: RetryConfig | None = None,
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """Decorator to add retry logic to a function.

    Args:
        config: Retry configuration (defaults to DEFAULT_RETRY_CONFIG)
        on_retry: Optional callback called on each retry (exception, attempt)

    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = DEFAULT_RETRY_CONFIG

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt < config.max_retries:
                        delay = config.calculate_delay(attempt)
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. Retrying in %.1f seconds...",
                            attempt + 1,
                            config.max_retries + 1,
                            func.__name__,
                            str(e),
                            delay,
                        )

                        if on_retry:
                            on_retry(e, attempt)

                        time.sleep(delay)
                    else:
                        logger.error(
                            "All %d attempts failed for %s. Last error: %s",
                            config.max_retries + 1,
                            func.__name__,
                            str(e),
                        )
                except Exception as e:
                    # Non-retryable exception, re-raise immediately
                    logger.error(
                        "Non-retryable error in %s: %s",
                        func.__name__,
                        str(e),
                    )
                    raise

            # All retries exhausted
            raise last_exception

        return wrapper

    return decorator


# =============================================================================
# Error Classification and Mapping
# =============================================================================


def classify_bigquery_error(error: Exception) -> PipelineError:
    """Classify a BigQuery error into the appropriate custom exception.

    Args:
        error: The original BigQuery exception

    Returns:
        A classified PipelineError subclass
    """
    error_str = str(error).lower()

    # Quota/rate limit errors (retryable)
    quota_keywords = [
        "quota",
        "rate limit",
        "ratelimit",
        "exceeded",
        "too many",
        "resource exhausted",
        "429",
    ]
    if any(keyword in error_str for keyword in quota_keywords):
        return BigQueryQuotaError(
            message=str(error),
            quota_type="rate_limit" if "rate" in error_str else "quota",
            source="bigquery",
            details={"original_error": type(error).__name__},
        )

    # Not found errors (not retryable)
    not_found_keywords = ["not found", "404", "does not exist", "no such"]
    if any(keyword in error_str for keyword in not_found_keywords):
        return BigQueryNotFoundError(
            message=str(error),
            source="bigquery",
            details={"original_error": type(error).__name__},
        )

    # Default to generic pipeline error
    return PipelineError(
        message=str(error),
        source="bigquery",
        details={"original_error": type(error).__name__},
    )


def classify_postgres_error(error: Exception) -> PipelineError:
    """Classify a Postgres error into the appropriate custom exception.

    Args:
        error: The original Postgres exception

    Returns:
        A classified PipelineError subclass
    """
    error_str = str(error).lower()

    # Connection errors (retryable)
    connection_keywords = [
        "connection",
        "timeout",
        "refused",
        "unavailable",
        "too many connections",
        "ssl",
        "network",
    ]
    if any(keyword in error_str for keyword in connection_keywords):
        return PostgresConnectionError(
            message=str(error),
            source="postgres",
            details={"original_error": type(error).__name__},
        )

    # Constraint violations (not retryable)
    constraint_keywords = [
        "constraint",
        "unique",
        "foreign key",
        "violates",
        "duplicate",
    ]
    if any(keyword in error_str for keyword in constraint_keywords):
        return PostgresConstraintError(
            message=str(error),
            source="postgres",
            details={"original_error": type(error).__name__},
        )

    # Default to generic pipeline error
    return PipelineError(
        message=str(error),
        source="postgres",
        details={"original_error": type(error).__name__},
    )


# =============================================================================
# Alerting Hooks
# =============================================================================


@dataclass
class AlertContext:
    """Context for alert notifications."""

    source_name: str
    error_message: str
    error_type: str
    attempt_count: int
    timestamp: str
    pipeline_name: str = "gong_to_postgres"
    environment: str = "production"
    details: dict = field(default_factory=dict)


class AlertProvider:
    """Base class for alert providers."""

    def send_alert(self, context: AlertContext) -> bool:
        """Send an alert notification.

        Args:
            context: Alert context with error details

        Returns:
            True if alert was sent successfully
        """
        raise NotImplementedError


class SlackAlertProvider(AlertProvider):
    """Slack alert provider for sending failure notifications.

    To use, set SLACK_WEBHOOK_URL environment variable or pass webhook_url.
    """

    def __init__(self, webhook_url: str | None = None):
        """Initialize Slack alert provider.

        Args:
            webhook_url: Slack incoming webhook URL (or set SLACK_WEBHOOK_URL env var)
        """
        import os

        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)

        if not self.enabled:
            logger.info("Slack alerting disabled - SLACK_WEBHOOK_URL not configured")

    def send_alert(self, context: AlertContext) -> bool:
        """Send alert to Slack channel.

        Args:
            context: Alert context with error details

        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Slack alerting disabled, skipping alert")
            return False

        try:
            import json
            import urllib.request

            message = {
                "text": ":rotating_light: *Pipeline Failure Alert*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":rotating_light: Pipeline Failure Alert",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Pipeline:*\n{context.pipeline_name}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Source:*\n{context.source_name}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Error Type:*\n{context.error_type}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Attempts:*\n{context.attempt_count}",
                            },
                        ],
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Error Message:*\n```{context.error_message[:500]}```",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Environment: {context.environment} | Time: {context.timestamp}",
                            }
                        ],
                    },
                ],
            }

            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(message).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)

            logger.info("Slack alert sent for %s failure", context.source_name)
            return True

        except Exception as e:
            logger.error("Failed to send Slack alert: %s", str(e))
            return False


class PagerDutyAlertProvider(AlertProvider):
    """PagerDuty alert provider for sending failure notifications.

    To use, set PAGERDUTY_ROUTING_KEY environment variable or pass routing_key.
    """

    def __init__(self, routing_key: str | None = None):
        """Initialize PagerDuty alert provider.

        Args:
            routing_key: PagerDuty Events API v2 routing key
        """
        import os

        self.routing_key = routing_key or os.getenv("PAGERDUTY_ROUTING_KEY")
        self.enabled = bool(self.routing_key)
        self.events_url = "https://events.pagerduty.com/v2/enqueue"

        if not self.enabled:
            logger.info("PagerDuty alerting disabled - PAGERDUTY_ROUTING_KEY not configured")

    def send_alert(self, context: AlertContext) -> bool:
        """Send alert to PagerDuty.

        Args:
            context: Alert context with error details

        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("PagerDuty alerting disabled, skipping alert")
            return False

        try:
            import json
            import urllib.request

            payload = {
                "routing_key": self.routing_key,
                "event_action": "trigger",
                "dedup_key": f"{context.pipeline_name}-{context.source_name}-{context.timestamp[:10]}",
                "payload": {
                    "summary": f"DLT Pipeline failure: {context.source_name} - {context.error_type}",
                    "severity": "error",
                    "source": context.pipeline_name,
                    "timestamp": context.timestamp,
                    "custom_details": {
                        "error_message": context.error_message,
                        "source_name": context.source_name,
                        "attempt_count": context.attempt_count,
                        "environment": context.environment,
                        **context.details,
                    },
                },
            }

            req = urllib.request.Request(
                self.events_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)

            logger.info("PagerDuty alert sent for %s failure", context.source_name)
            return True

        except Exception as e:
            logger.error("Failed to send PagerDuty alert: %s", str(e))
            return False


class LogAlertProvider(AlertProvider):
    """Simple logging-based alert provider (always enabled for fallback)."""

    def send_alert(self, context: AlertContext) -> bool:
        """Log the alert.

        Args:
            context: Alert context with error details

        Returns:
            Always True
        """
        logger.critical(
            "PIPELINE FAILURE ALERT | Pipeline: %s | Source: %s | Error: %s | Type: %s | Attempts: %d | Time: %s",
            context.pipeline_name,
            context.source_name,
            context.error_message,
            context.error_type,
            context.attempt_count,
            context.timestamp,
        )
        return True


class AlertManager:
    """Manages multiple alert providers and sends alerts on permanent failures."""

    def __init__(self, providers: list[AlertProvider] | None = None):
        """Initialize alert manager with providers.

        Args:
            providers: List of alert providers (defaults to Slack, PagerDuty, Log)
        """
        if providers is None:
            # Default providers - will only send if credentials configured
            providers = [
                SlackAlertProvider(),
                PagerDutyAlertProvider(),
                LogAlertProvider(),  # Always enabled as fallback
            ]
        self.providers = providers

    def send_failure_alert(
        self,
        source_name: str,
        error: Exception,
        attempt_count: int,
        environment: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Send failure alerts to all configured providers.

        Args:
            source_name: Name of the failed source
            error: The exception that caused the failure
            attempt_count: Number of attempts before failure
            environment: Environment name (default: from env var or 'production')
            details: Additional details to include in the alert
        """
        import os
        from datetime import datetime

        context = AlertContext(
            source_name=source_name,
            error_message=str(error),
            error_type=type(error).__name__,
            attempt_count=attempt_count,
            timestamp=datetime.now(UTC).isoformat(),
            environment=environment or os.getenv("ENVIRONMENT", "production"),
            details=details or {},
        )

        for provider in self.providers:
            try:
                provider.send_alert(context)
            except Exception as e:
                logger.error(
                    "Alert provider %s failed: %s",
                    type(provider).__name__,
                    str(e),
                )


# Global alert manager instance
alert_manager = AlertManager()


def send_permanent_failure_alert(
    source_name: str,
    error: Exception,
    attempt_count: int = 0,
    **kwargs: Any,
) -> None:
    """Convenience function to send a permanent failure alert.

    Args:
        source_name: Name of the failed source
        error: The exception that caused the failure
        attempt_count: Number of attempts before failure
        **kwargs: Additional arguments passed to AlertManager.send_failure_alert
    """
    alert_manager.send_failure_alert(
        source_name=source_name,
        error=error,
        attempt_count=attempt_count,
        **kwargs,
    )
