"""
Test script for DLT pipeline monitoring and observability (Task 7.6).

Tests:
- Structured logging configuration
- Metrics collection per source
- Sync status summary generation
- DLT logging integration
- Data quality checks (mocked)

Run: uv run python dlt_pipeline/test_monitoring.py
"""

import logging
import os
import sys
import time
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dlt_pipeline.monitoring import (
    DataQualityChecker,
    SourceMetrics,
    configure_dlt_logging,
    create_pipeline_metrics,
    logger,
)


def test_structured_logging():
    """Test 7.1: Verify structured logging with INFO for progress, ERROR for failures."""
    print("\n" + "=" * 60)
    print("Test 7.1: Structured Logging")
    print("=" * 60)

    # Verify logger is configured at INFO level
    assert logger.level == logging.INFO or logger.level == logging.NOTSET
    print("  Logger level: INFO (or inherited)")

    # Test INFO level logging (progress)
    logger.info("Test progress message")
    print("  INFO logging works")

    # Test ERROR level logging (failures)
    logger.error("Test error message")
    print("  ERROR logging works")

    print("  Structured logging configured correctly")


def test_source_metrics():
    """Test 7.2: Verify metrics collection per source."""
    print("\n" + "=" * 60)
    print("Test 7.2: Source Metrics (rows_synced, errors_count, duration_seconds)")
    print("=" * 60)

    # Create source metrics
    metrics = SourceMetrics(source_name="test_source")
    print(f"  Created SourceMetrics: {metrics.source_name}")

    # Simulate work
    time.sleep(0.1)

    # Complete with results
    metrics.complete(rows=1000, errors=2)
    print(f"  Rows synced: {metrics.rows_synced}")
    print(f"  Errors count: {metrics.errors_count}")
    print(f"  Duration: {metrics.duration_seconds:.3f}s")

    # Verify metrics
    assert metrics.rows_synced == 1000
    assert metrics.errors_count == 2
    assert metrics.duration_seconds >= 0.1

    # Test error tracking
    metrics.add_error("Test error 1")
    metrics.add_error("Test error 2")
    assert metrics.errors_count == 4  # 2 initial + 2 added
    assert len(metrics.error_details) == 2

    # Test serialization
    metrics_dict = metrics.to_dict()
    assert "source_name" in metrics_dict
    assert "rows_synced" in metrics_dict
    assert "errors_count" in metrics_dict
    assert "duration_seconds" in metrics_dict

    print("  Source metrics collection verified")


def test_pipeline_metrics():
    """Test 7.2 + 7.3: Verify aggregate metrics and summary logging."""
    print("\n" + "=" * 60)
    print("Test 7.2 + 7.3: Pipeline Metrics and Summary")
    print("=" * 60)

    # Create pipeline metrics
    pipeline = create_pipeline_metrics(run_id="test_run_001")
    print(f"  Created PipelineMetrics: {pipeline.run_id}")

    # Simulate calls source sync
    pipeline.start_source("calls")
    time.sleep(0.05)
    pipeline.complete_source("calls", rows=500, errors=0)

    # Simulate emails source sync
    pipeline.start_source("emails")
    time.sleep(0.05)
    pipeline.complete_source("emails", rows=300, errors=1)

    # Simulate opportunities source sync
    pipeline.start_source("opportunities")
    time.sleep(0.05)
    pipeline.complete_source("opportunities", rows=100, errors=0)

    # Verify totals
    print(f"  Total rows synced: {pipeline.total_rows_synced}")
    print(f"  Total errors: {pipeline.total_errors}")
    print(f"  Total duration: {pipeline.total_duration_seconds:.3f}s")

    assert pipeline.total_rows_synced == 900
    assert pipeline.total_errors == 1

    # Test summary logging (Task 7.3)
    print("\n  Testing summary log output:")
    pipeline.log_summary()

    # Test serialization
    pipeline_dict = pipeline.to_dict()
    assert "run_id" in pipeline_dict
    assert "total_rows_synced" in pipeline_dict
    assert "total_errors" in pipeline_dict
    assert "sources" in pipeline_dict
    assert len(pipeline_dict["sources"]) == 3

    print("\n  Pipeline metrics and summary verified")


def test_dlt_logging_configuration():
    """Test 7.4: Verify DLT logging integration."""
    print("\n" + "=" * 60)
    print("Test 7.4: DLT Logging Integration")
    print("=" * 60)

    # Configure DLT logging at different levels
    configure_dlt_logging(log_level="INFO")
    print("  DLT logging configured at INFO level")

    # Verify DLT loggers are configured
    dlt_logger = logging.getLogger("dlt")
    assert dlt_logger.level == logging.INFO
    print(f"  dlt logger level: {logging.getLevelName(dlt_logger.level)}")

    # Test DEBUG level
    configure_dlt_logging(log_level="DEBUG")
    assert dlt_logger.level == logging.DEBUG
    print("  DLT logging configured at DEBUG level")

    # Reset to INFO
    configure_dlt_logging(log_level="INFO")

    print("  DLT logging integration verified")


def test_data_quality_checker_mocked():
    """Test 7.5: Verify data quality check logic (mocked)."""
    print("\n" + "=" * 60)
    print("Test 7.5: Data Quality Checks (Mocked)")
    print("=" * 60)

    checker = DataQualityChecker()

    # Mock the database methods
    with (
        patch.object(checker, "get_bigquery_count") as mock_bq,
        patch.object(checker, "get_postgres_count") as mock_pg,
    ):

        # Test passing check (counts match)
        mock_bq.return_value = 1000
        mock_pg.return_value = 995  # 0.5% difference

        result = checker.check_row_count_delta("call", "calls", threshold_pct=5.0)

        print(f"  BigQuery count: {result['bigquery_count']}")
        print(f"  Postgres count: {result['postgres_count']}")
        print(f"  Delta: {result['delta']}")
        print(f"  Delta %: {result['delta_pct']}%")
        print(f"  Passed: {result['passed']}")

        assert result["passed"] is True
        assert result["delta_pct"] == 0.5

        # Test failing check (counts differ too much)
        mock_bq.return_value = 1000
        mock_pg.return_value = 800  # 20% difference

        result = checker.check_row_count_delta("call", "calls", threshold_pct=5.0)

        print("\n  Failing check:")
        print(f"  BigQuery count: {result['bigquery_count']}")
        print(f"  Postgres count: {result['postgres_count']}")
        print(f"  Delta %: {result['delta_pct']}%")
        print(f"  Passed: {result['passed']}")

        assert result["passed"] is False
        assert result["delta_pct"] == 20.0

    print("\n  Data quality check logic verified")


def test_run_all_quality_checks_mocked():
    """Test 7.5: Verify run_all_checks with mocked data."""
    print("\n" + "=" * 60)
    print("Test 7.5: Run All Quality Checks (Mocked)")
    print("=" * 60)

    checker = DataQualityChecker()

    # Mock check_row_count_delta to return test results
    with patch.object(checker, "check_row_count_delta") as mock_check:
        mock_check.side_effect = [
            {"bigquery_table": "call", "postgres_table": "calls", "passed": True},
            {"bigquery_table": "transcript", "postgres_table": "transcripts", "passed": True},
            {"bigquery_table": "call_speaker", "postgres_table": "speakers", "passed": False},
        ]

        results = checker.run_all_checks()

        print(f"  Checks run: {len(results)}")
        print(f"  Passed: {sum(1 for r in results if r.get('passed', False))}")
        print(f"  Failed: {sum(1 for r in results if not r.get('passed', True))}")

        assert len(results) == 3
        assert sum(1 for r in results if r.get("passed", False)) == 2

    print("  Run all quality checks verified")


def test_error_handling():
    """Test error handling in metrics."""
    print("\n" + "=" * 60)
    print("Test: Error Handling")
    print("=" * 60)

    metrics = SourceMetrics(source_name="error_test")

    # Add multiple errors
    metrics.add_error("Connection timeout")
    metrics.add_error("Invalid data format")
    metrics.add_error("Schema mismatch")

    print(f"  Errors recorded: {metrics.errors_count}")
    print(f"  Error details: {metrics.error_details}")

    assert metrics.errors_count == 3
    assert len(metrics.error_details) == 3

    # Verify errors are in to_dict output
    metrics_dict = metrics.to_dict()
    assert metrics_dict["error_details"] is not None

    print("  Error handling verified")


def run_all_tests():
    """Run all monitoring tests."""
    print("\n" + "=" * 60)
    print("DLT Pipeline Monitoring Tests (Task 7.6)")
    print("=" * 60)

    tests = [
        test_structured_logging,
        test_source_metrics,
        test_pipeline_metrics,
        test_dlt_logging_configuration,
        test_data_quality_checker_mocked,
        test_run_all_quality_checks_mocked,
        test_error_handling,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n  FAILED: {test.__name__}")
            print(f"  Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n  ERROR: {test.__name__}")
            print(f"  Exception: {e}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("\nAll monitoring tests passed (Task 7.6 verified)")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
