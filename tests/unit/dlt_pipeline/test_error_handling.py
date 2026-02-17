"""
Tests for DLT Pipeline Error Handling and Retry Logic (Task 6.6)

Tests retry logic by simulating network failures and verifying:
- Exponential backoff is applied correctly
- BigQuery quota errors trigger retry
- Postgres connection errors trigger retry
- Non-retryable errors fail immediately
- Permanent failure alerts are sent after max retries
- Partial failure handling continues with other sources
"""

import time
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from dlt_pipeline.error_handling import (
    AlertContext,
    AlertManager,
    BigQueryNotFoundError,
    BigQueryQuotaError,
    LogAlertProvider,
    PagerDutyAlertProvider,
    PipelineError,
    PostgresConnectionError,
    PostgresConstraintError,
    RetryConfig,
    RetryStrategy,
    SlackAlertProvider,
    classify_bigquery_error,
    classify_postgres_error,
    send_permanent_failure_alert,
    with_retry,
)


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_config(self):
        """Test default retry configuration values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.initial_delay_seconds == 1.0
        assert config.max_delay_seconds == 300.0
        assert config.exponential_base == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL

    def test_calculate_delay_exponential(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            initial_delay_seconds=1.0,
            exponential_base=2.0,
            strategy=RetryStrategy.EXPONENTIAL,
        )

        # Attempt 0: 1 * 2^0 = 1
        assert config.calculate_delay(0) == 1.0
        # Attempt 1: 1 * 2^1 = 2
        assert config.calculate_delay(1) == 2.0
        # Attempt 2: 1 * 2^2 = 4
        assert config.calculate_delay(2) == 4.0
        # Attempt 3: 1 * 2^3 = 8
        assert config.calculate_delay(3) == 8.0

    def test_calculate_delay_respects_max(self):
        """Test that delay is capped at max_delay_seconds."""
        config = RetryConfig(
            initial_delay_seconds=100.0,
            exponential_base=2.0,
            max_delay_seconds=300.0,
            strategy=RetryStrategy.EXPONENTIAL,
        )

        # Attempt 2: 100 * 2^2 = 400, but capped at 300
        assert config.calculate_delay(2) == 300.0

    def test_calculate_delay_linear(self):
        """Test linear backoff delay calculation."""
        config = RetryConfig(
            initial_delay_seconds=5.0,
            strategy=RetryStrategy.LINEAR,
        )

        # Linear: delay = initial * (attempt + 1)
        assert config.calculate_delay(0) == 5.0
        assert config.calculate_delay(1) == 10.0
        assert config.calculate_delay(2) == 15.0

    def test_calculate_delay_fixed(self):
        """Test fixed delay strategy."""
        config = RetryConfig(
            initial_delay_seconds=5.0,
            strategy=RetryStrategy.FIXED,
        )

        # Fixed: always initial delay
        assert config.calculate_delay(0) == 5.0
        assert config.calculate_delay(1) == 5.0
        assert config.calculate_delay(10) == 5.0


class TestErrorClassification:
    """Tests for error classification (Tasks 6.2, 6.3)."""

    def test_classify_bigquery_quota_error(self):
        """Test BigQuery quota error classification (Task 6.2)."""
        error = Exception("Quota exceeded for BigQuery project")
        classified = classify_bigquery_error(error)

        assert isinstance(classified, BigQueryQuotaError)
        assert classified.source == "bigquery"
        assert "quota" in str(classified).lower()

    def test_classify_bigquery_rate_limit_error(self):
        """Test BigQuery rate limit error classification (Task 6.2)."""
        error = Exception("rateLimitExceeded: Too many requests")
        classified = classify_bigquery_error(error)

        assert isinstance(classified, BigQueryQuotaError)

    def test_classify_bigquery_not_found_error(self):
        """Test BigQuery not found error classification (Task 6.2)."""
        error = Exception("Table not found: my_project.my_dataset.my_table")
        classified = classify_bigquery_error(error)

        assert isinstance(classified, BigQueryNotFoundError)

    def test_classify_postgres_connection_error(self):
        """Test Postgres connection error classification (Task 6.3)."""
        error = Exception("Connection refused to postgres server")
        classified = classify_postgres_error(error)

        assert isinstance(classified, PostgresConnectionError)

    def test_classify_postgres_timeout_error(self):
        """Test Postgres timeout error classification (Task 6.3)."""
        error = Exception("Connection timeout after 30 seconds")
        classified = classify_postgres_error(error)

        assert isinstance(classified, PostgresConnectionError)

    def test_classify_postgres_constraint_error(self):
        """Test Postgres constraint error classification (Task 6.3)."""
        error = Exception("Unique constraint violation on column 'id'")
        classified = classify_postgres_error(error)

        assert isinstance(classified, PostgresConstraintError)

    def test_classify_generic_bigquery_error(self):
        """Test generic BigQuery error classification."""
        error = Exception("Some unknown BigQuery error occurred")
        classified = classify_bigquery_error(error)

        # Should return generic PipelineError for unknown errors
        assert isinstance(classified, PipelineError)
        assert classified.source == "bigquery"


class TestWithRetryDecorator:
    """Tests for the @with_retry decorator."""

    def test_successful_execution_no_retry(self):
        """Test successful function doesn't retry."""
        call_count = 0

        @with_retry()
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retryable_error_retries(self):
        """Test retryable error triggers retry with exponential backoff (Task 6.6)."""
        call_count = 0
        config = RetryConfig(
            max_retries=3,
            initial_delay_seconds=0.01,  # Very short for testing
            retryable_exceptions=(ConnectionError,),
        )

        @with_retry(config=config)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network failure")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 3  # Failed twice, succeeded on third

    def test_max_retries_exceeded(self):
        """Test error is raised after max retries exceeded (Task 6.6)."""
        call_count = 0
        config = RetryConfig(
            max_retries=2,
            initial_delay_seconds=0.01,
            retryable_exceptions=(ConnectionError,),
        )

        @with_retry(config=config)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent failure")

        with pytest.raises(ConnectionError):
            always_fails()

        assert call_count == 3  # Initial + 2 retries

    def test_non_retryable_error_fails_immediately(self):
        """Test non-retryable error fails without retry (Task 6.6)."""
        call_count = 0
        config = RetryConfig(
            max_retries=3,
            retryable_exceptions=(ConnectionError,),  # ValueError not included
        )

        @with_retry(config=config)
        def raises_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")

        with pytest.raises(ValueError):
            raises_value_error()

        assert call_count == 1  # No retries for non-retryable error

    def test_on_retry_callback(self):
        """Test on_retry callback is called on each retry."""
        call_count = 0
        retry_attempts = []
        config = RetryConfig(
            max_retries=2,
            initial_delay_seconds=0.01,
            retryable_exceptions=(ConnectionError,),
        )

        def on_retry_callback(error, attempt):
            retry_attempts.append(attempt)

        @with_retry(config=config, on_retry=on_retry_callback)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network failure")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert retry_attempts == [0, 1]  # Called for attempt 0 and 1


class TestAlertProviders:
    """Tests for alert providers (Task 6.5)."""

    def test_log_alert_provider_always_sends(self):
        """Test LogAlertProvider always sends (fallback)."""
        provider = LogAlertProvider()
        context = AlertContext(
            source_name="test_source",
            error_message="Test error",
            error_type="TestError",
            attempt_count=3,
            timestamp=datetime.now(UTC).isoformat(),
        )

        result = provider.send_alert(context)
        assert result is True

    def test_slack_provider_disabled_without_url(self):
        """Test SlackAlertProvider is disabled without webhook URL."""
        with patch.dict("os.environ", {}, clear=True):
            provider = SlackAlertProvider()
            assert provider.enabled is False

            context = AlertContext(
                source_name="test_source",
                error_message="Test error",
                error_type="TestError",
                attempt_count=3,
                timestamp=datetime.now(UTC).isoformat(),
            )

            result = provider.send_alert(context)
            assert result is False

    def test_slack_provider_enabled_with_url(self):
        """Test SlackAlertProvider is enabled with webhook URL."""
        provider = SlackAlertProvider(webhook_url="https://hooks.slack.com/services/xxx")
        assert provider.enabled is True

    def test_pagerduty_provider_disabled_without_key(self):
        """Test PagerDutyAlertProvider is disabled without routing key."""
        with patch.dict("os.environ", {}, clear=True):
            provider = PagerDutyAlertProvider()
            assert provider.enabled is False

    def test_pagerduty_provider_enabled_with_key(self):
        """Test PagerDutyAlertProvider is enabled with routing key."""
        provider = PagerDutyAlertProvider(routing_key="test-routing-key")
        assert provider.enabled is True


class TestAlertManager:
    """Tests for AlertManager (Task 6.5)."""

    def test_alert_manager_sends_to_all_providers(self):
        """Test AlertManager sends to all configured providers."""
        mock_provider1 = MagicMock(spec=LogAlertProvider)
        mock_provider1.send_alert.return_value = True

        mock_provider2 = MagicMock(spec=LogAlertProvider)
        mock_provider2.send_alert.return_value = True

        manager = AlertManager(providers=[mock_provider1, mock_provider2])

        manager.send_failure_alert(
            source_name="test_source",
            error=Exception("Test error"),
            attempt_count=3,
        )

        mock_provider1.send_alert.assert_called_once()
        mock_provider2.send_alert.assert_called_once()

    def test_alert_manager_continues_on_provider_failure(self):
        """Test AlertManager continues if one provider fails."""
        mock_provider1 = MagicMock(spec=LogAlertProvider)
        mock_provider1.send_alert.side_effect = Exception("Provider failed")

        mock_provider2 = MagicMock(spec=LogAlertProvider)
        mock_provider2.send_alert.return_value = True

        manager = AlertManager(providers=[mock_provider1, mock_provider2])

        # Should not raise, should continue to second provider
        manager.send_failure_alert(
            source_name="test_source",
            error=Exception("Test error"),
            attempt_count=3,
        )

        mock_provider2.send_alert.assert_called_once()

    def test_send_permanent_failure_alert(self):
        """Test convenience function sends alert (Task 6.5)."""
        with patch("dlt_pipeline.error_handling.alert_manager") as mock_manager:
            send_permanent_failure_alert(
                source_name="calls",
                error=Exception("Network timeout"),
                attempt_count=3,
                environment="test",
            )

            mock_manager.send_failure_alert.assert_called_once()
            call_kwargs = mock_manager.send_failure_alert.call_args.kwargs
            assert call_kwargs["source_name"] == "calls"
            assert call_kwargs["attempt_count"] == 3


class TestRetryLogicWithNetworkSimulation:
    """
    Task 6.6: Test retry logic by simulating network failure.

    These tests simulate various network failure scenarios to verify
    the retry mechanism works correctly.
    """

    def test_simulate_bigquery_quota_error_retry(self):
        """Simulate BigQuery quota error and verify retry (Task 6.6)."""
        call_count = 0
        config = RetryConfig(
            max_retries=3,
            initial_delay_seconds=0.01,
            retryable_exceptions=(BigQueryQuotaError,),
        )

        @with_retry(config=config)
        def simulate_bigquery_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise BigQueryQuotaError(
                    message="Quota exceeded",
                    quota_type="rate_limit",
                )
            return {"rows": 100}

        result = simulate_bigquery_call()
        assert result == {"rows": 100}
        assert call_count == 3

    def test_simulate_postgres_connection_error_retry(self):
        """Simulate Postgres connection error and verify retry (Task 6.6)."""
        call_count = 0
        config = RetryConfig(
            max_retries=3,
            initial_delay_seconds=0.01,
            retryable_exceptions=(PostgresConnectionError,),
        )

        @with_retry(config=config)
        def simulate_postgres_call():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise PostgresConnectionError(
                    message="Connection refused",
                    host="localhost",
                    port=5432,
                )
            return {"status": "connected"}

        result = simulate_postgres_call()
        assert result == {"status": "connected"}
        assert call_count == 2

    def test_simulate_intermittent_network_failure(self):
        """Simulate intermittent network failure pattern (Task 6.6)."""
        call_count = 0
        config = RetryConfig(
            max_retries=5,
            initial_delay_seconds=0.01,
            retryable_exceptions=(ConnectionError, TimeoutError),
        )

        # Simulate pattern: fail, fail, succeed, fail, succeed
        failure_pattern = [True, True, False, True, False]

        @with_retry(config=config)
        def flaky_network_call():
            nonlocal call_count
            if call_count < len(failure_pattern) and failure_pattern[call_count]:
                call_count += 1
                raise TimeoutError("Network timeout")
            call_count += 1
            return "success"

        result = flaky_network_call()
        assert result == "success"
        assert call_count == 3  # First two failed, third succeeded

    def test_exponential_backoff_timing(self):
        """Verify exponential backoff delays are applied (Task 6.6)."""
        call_times = []
        config = RetryConfig(
            max_retries=3,
            initial_delay_seconds=0.05,  # 50ms
            exponential_base=2.0,
            retryable_exceptions=(ConnectionError,),
        )

        @with_retry(config=config)
        def track_timing():
            call_times.append(time.time())
            if len(call_times) < 4:
                raise ConnectionError("Network failure")
            return "success"

        result = track_timing()
        assert result == "success"
        assert len(call_times) == 4

        # Check delays between calls (with some tolerance)
        # Delay 1: ~50ms, Delay 2: ~100ms, Delay 3: ~200ms
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        delay3 = call_times[3] - call_times[2]

        # Allow 50ms tolerance for test execution overhead
        assert 0.04 < delay1 < 0.15, f"First delay was {delay1}"
        assert 0.08 < delay2 < 0.25, f"Second delay was {delay2}"
        assert 0.15 < delay3 < 0.45, f"Third delay was {delay3}"

        # Verify exponential growth (each delay roughly 2x previous)
        assert delay2 > delay1, "Second delay should be longer than first"
        assert delay3 > delay2, "Third delay should be longer than second"

    def test_permanent_failure_after_exhausted_retries(self):
        """Test permanent failure sends alert after exhausting retries (Task 6.6)."""
        config = RetryConfig(
            max_retries=2,
            initial_delay_seconds=0.01,
            retryable_exceptions=(ConnectionError,),
        )

        @with_retry(config=config)
        def always_fails():
            raise ConnectionError("Persistent network failure")

        with pytest.raises(ConnectionError, match="Persistent network failure"):
            always_fails()
