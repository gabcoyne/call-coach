"""
BigQuery to Postgres DLT Pipeline

Main entry point for syncing Gong data from BigQuery to Postgres.
Orchestrates calls, emails, and opportunities sources with:
- Parallel execution for independent sources
- Error handling with dead letter queue logging
- Progress logging with row counts and duration
- Sync status tracking in database
- DLT built-in observability integration (Task 7.4)
- Data quality checks (Task 7.5)
- Retry logic with exponential backoff (max_retries=3) (Task 6.1)
- Custom exception handling for BigQuery quota errors (Task 6.2)
- Custom exception handling for Postgres connection errors (Task 6.3)
- Partial failure handling (continue processing other sources if one fails) (Task 6.4)
- Alerting hooks for permanent failures (Slack/PagerDuty) (Task 6.5)
"""

import json
import logging
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import dlt
from dlt.common.runtime.telemetry import stop_telemetry
from dlt.pipeline.exceptions import PipelineStepFailed

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.queries import update_sync_status
from dlt_pipeline.error_handling import (
    DEFAULT_RETRY_CONFIG,
    BigQueryQuotaError,
    PipelineError,
    PostgresConnectionError,
    RetryConfig,
    classify_bigquery_error,
    classify_postgres_error,
    send_permanent_failure_alert,
)
from dlt_pipeline.monitoring import DataQualityChecker, configure_dlt_logging
from dlt_pipeline.sources.calls import gong_calls_source
from dlt_pipeline.sources.emails import gong_emails_source
from dlt_pipeline.sources.opportunities import gong_opportunities_source

# Configure logging with structured format (Task 7.1)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("dlt_pipeline")

# Configure DLT's built-in logging (Task 7.4)
configure_dlt_logging(log_level="INFO")

# Disable DLT telemetry for privacy
stop_telemetry()


@dataclass
class SyncResult:
    """Result of syncing a single source."""

    source_name: str
    entity_type: str
    status: str  # "success", "partial", "failed"
    rows_synced: int = 0
    errors_count: int = 0
    error_details: dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    checkpoint_timestamp: str | None = None


@dataclass
class DeadLetterRecord:
    """Record for failed items that couldn't be processed."""

    source: str
    timestamp: str
    error_type: str
    error_message: str
    stack_trace: str | None = None
    record_data: dict[str, Any] | None = None


class DeadLetterQueue:
    """
    Dead letter queue for tracking failed records.

    Collects failed records during sync and logs them to sync_status.error_details.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.records: list[DeadLetterRecord] = []

    def add(
        self,
        error_type: str,
        error_message: str,
        stack_trace: str | None = None,
        record_data: dict[str, Any] | None = None,
    ) -> None:
        """Add a failed record to the dead letter queue."""
        record = DeadLetterRecord(
            source=self.source_name,
            timestamp=datetime.now(UTC).isoformat(),
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            record_data=record_data,
        )
        self.records.append(record)
        logger.warning(
            f"Dead letter record added for {self.source_name}: {error_type} - {error_message}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert dead letter queue to dict for JSON serialization."""
        return {
            "source": self.source_name,
            "total_failed": len(self.records),
            "records": [
                {
                    "timestamp": r.timestamp,
                    "error_type": r.error_type,
                    "error_message": r.error_message,
                    "stack_trace": r.stack_trace,
                    "record_id": r.record_data.get("id") if r.record_data else None,
                }
                for r in self.records[:100]  # Limit to first 100 for storage
            ],
        }

    def __len__(self) -> int:
        return len(self.records)


def create_pipeline() -> dlt.Pipeline:
    """
    Create and configure the DLT pipeline.

    Returns:
        Configured DLT pipeline instance for gong_to_postgres.
    """
    # Get DATABASE_URL from environment (prefer direct URL over pooler)
    database_url = os.environ.get("DATABASE_URL_DIRECT") or os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    # Convert Neon pooler URL to direct URL by removing '-pooler' from hostname
    # Pooler URLs: ep-xxx-pooler.region.aws.neon.tech
    # Direct URLs: ep-xxx.region.aws.neon.tech
    # DLT requires direct connection because it uses search_path in connection options
    if "-pooler" in database_url:
        database_url = database_url.replace("-pooler", "")
        logger.info("Converted pooler URL to direct URL for DLT compatibility")

    # Initialize pipeline with postgres destination
    pipeline = dlt.pipeline(
        pipeline_name="gong_to_postgres",
        destination=dlt.destinations.postgres(credentials=database_url),
        dataset_name="public",
        progress="log",  # Log progress to stdout
    )

    logger.info(f"Pipeline created: {pipeline.pipeline_name}")
    logger.info("Destination: postgres")
    logger.info("Dataset: public")

    return pipeline


def classify_error(error: Exception) -> PipelineError:
    """
    Classify an error into appropriate PipelineError subclass (Tasks 6.2, 6.3).

    Args:
        error: The original exception

    Returns:
        A classified PipelineError subclass instance
    """
    error_str = str(error).lower()

    # Check for BigQuery-related errors (Task 6.2)
    bigquery_keywords = ["bigquery", "google.cloud", "bq", "quota exceeded", "rateLimitExceeded"]
    if any(kw.lower() in error_str for kw in bigquery_keywords):
        return classify_bigquery_error(error)

    # Check for Postgres-related errors (Task 6.3)
    postgres_keywords = ["postgres", "psycopg", "pg_", "connection refused", "ssl", "connection"]
    if any(kw.lower() in error_str for kw in postgres_keywords):
        return classify_postgres_error(error)

    # Default to generic pipeline error
    return PipelineError(
        message=str(error),
        details={"original_error": type(error).__name__},
    )


def is_retryable_error(error: Exception) -> bool:
    """
    Check if an error is retryable (Task 6.1).

    Retryable errors include:
    - BigQuery quota/rate limit errors
    - Postgres connection errors
    - Generic connection/timeout errors

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable
    """
    # Classify the error first
    classified = classify_error(error)

    # These error types are retryable
    retryable_types = (
        BigQueryQuotaError,
        PostgresConnectionError,
        ConnectionError,
        TimeoutError,
    )

    return isinstance(classified, retryable_types)


def run_source_sync(
    pipeline: dlt.Pipeline,
    source: dlt.sources.DltSource,
    entity_type: str,
) -> SyncResult:
    """
    Run sync for a single DLT source with error handling.

    Args:
        pipeline: DLT pipeline instance
        source: DLT source to sync
        entity_type: Entity type for sync_status tracking (calls, emails, opportunities)

    Returns:
        SyncResult with status, row counts, and any errors
    """
    start_time = time.time()
    dlq = DeadLetterQueue(source.name)
    result = SyncResult(
        source_name=source.name,
        entity_type=entity_type,
        status="failed",  # Default to failed, update on success
    )

    logger.info(f"Starting sync for source: {source.name}")

    try:
        # Run the pipeline
        load_info = pipeline.run(
            source,
            write_disposition="merge",
        )

        # Calculate duration
        result.duration_seconds = time.time() - start_time

        # Extract row counts from load info
        if load_info.load_packages:
            for package in load_info.load_packages:
                for _table_name, table_info in package.jobs.get("completed_jobs", {}).items():
                    if isinstance(table_info, list):
                        for job in table_info:
                            if hasattr(job, "row_counts"):
                                result.rows_synced += sum(job.row_counts.values())

        # If we can't get row counts from load_info, try to get from metrics
        if result.rows_synced == 0 and hasattr(load_info, "metrics"):
            try:
                metrics = load_info.metrics
                if metrics:
                    for metric in metrics:
                        if hasattr(metric, "rows_count"):
                            result.rows_synced += metric.rows_count
            except Exception:
                pass  # Row count is best effort

        # Check for any failed jobs
        failed_jobs = []
        if load_info.load_packages:
            for package in load_info.load_packages:
                failed = package.jobs.get("failed_jobs", {})
                if failed:
                    for table_name, jobs in failed.items():
                        for job in jobs if isinstance(jobs, list) else [jobs]:
                            failed_jobs.append(
                                {
                                    "table": table_name,
                                    "error": str(job) if job else "Unknown error",
                                }
                            )
                            dlq.add(
                                error_type="LoadJobFailed",
                                error_message=f"Failed to load table {table_name}",
                                record_data={"table": table_name},
                            )

        # Determine final status
        if len(dlq) == 0 and not failed_jobs:
            result.status = "success"
        elif result.rows_synced > 0:
            result.status = "partial"
        else:
            result.status = "failed"

        result.errors_count = len(dlq)
        if len(dlq) > 0:
            result.error_details = dlq.to_dict()

        # Get checkpoint timestamp from pipeline state
        try:
            state = pipeline.state
            if state:
                result.checkpoint_timestamp = datetime.now(UTC).isoformat()
        except Exception:
            pass

        logger.info(
            f"Sync completed for {source.name}: "
            f"status={result.status}, "
            f"rows={result.rows_synced}, "
            f"errors={result.errors_count}, "
            f"duration={result.duration_seconds:.2f}s"
        )

        # Log load info for debugging
        logger.debug(f"Load info: {load_info}")

    except PipelineStepFailed as e:
        result.duration_seconds = time.time() - start_time
        result.status = "failed"
        result.errors_count = 1
        dlq.add(
            error_type="PipelineStepFailed",
            error_message=str(e),
            stack_trace=traceback.format_exc(),
        )
        result.error_details = dlq.to_dict()
        logger.error(f"Pipeline step failed for {source.name}: {e}")

    except Exception as e:
        result.duration_seconds = time.time() - start_time
        result.status = "failed"
        result.errors_count = 1
        dlq.add(
            error_type=type(e).__name__,
            error_message=str(e),
            stack_trace=traceback.format_exc(),
        )
        result.error_details = dlq.to_dict()
        logger.error(f"Unexpected error syncing {source.name}: {e}")
        logger.error(traceback.format_exc())

    return result


def run_source_sync_with_retry(
    pipeline: dlt.Pipeline,
    source: dlt.sources.DltSource,
    entity_type: str,
    retry_config: RetryConfig | None = None,
    send_alerts: bool = True,
) -> SyncResult:
    """
    Run sync for a single DLT source with retry logic (Task 6.1).

    Implements:
    - Exponential backoff retry (max_retries=3)
    - Custom exception handling for BigQuery quota errors (Task 6.2)
    - Custom exception handling for Postgres connection errors (Task 6.3)
    - Alerting for permanent failures (Task 6.5)

    Args:
        pipeline: DLT pipeline instance
        source: DLT source to sync
        entity_type: Entity type for sync_status tracking (calls, emails, opportunities)
        retry_config: Optional retry configuration (defaults to DEFAULT_RETRY_CONFIG)
        send_alerts: If True, send alerts for permanent failures (Task 6.5)

    Returns:
        SyncResult with status, row counts, and any errors
    """
    if retry_config is None:
        retry_config = DEFAULT_RETRY_CONFIG

    start_time = time.time()
    last_error: Exception | None = None
    attempt_count = 0

    # Retry loop with exponential backoff (Task 6.1)
    for attempt in range(retry_config.max_retries + 1):
        attempt_count = attempt + 1

        logger.info(
            f"Starting sync for source: {source.name} "
            f"(attempt {attempt_count}/{retry_config.max_retries + 1})"
        )

        try:
            # Use the base sync function for actual work
            result = run_source_sync(pipeline, source, entity_type)

            # If successful or partial success, return immediately
            if result.status in ("success", "partial"):
                if attempt > 0:
                    logger.info(
                        f"Source {source.name} succeeded on attempt {attempt_count} "
                        f"after {attempt} retries"
                    )
                return result

            # If failed but no exception, check if it's retryable
            # (e.g., load job failures that aren't raised as exceptions)
            if attempt < retry_config.max_retries:
                delay = retry_config.calculate_delay(attempt)
                logger.warning(
                    f"Source {source.name} failed on attempt {attempt_count}. "
                    f"Retrying in {delay:.1f} seconds..."
                )
                time.sleep(delay)
                continue

            # Max retries exceeded without success
            return result

        except Exception as e:
            last_error = e
            classified_error = classify_error(e)

            # Check if retryable (Tasks 6.2, 6.3)
            if is_retryable_error(e) and attempt < retry_config.max_retries:
                delay = retry_config.calculate_delay(attempt)
                error_type = type(classified_error).__name__
                logger.warning(
                    f"Retryable error ({error_type}) in source {source.name} "
                    f"(attempt {attempt_count}/{retry_config.max_retries + 1}): {e}. "
                    f"Retrying in {delay:.1f} seconds..."
                )
                time.sleep(delay)
                continue

            # Non-retryable or max retries exceeded
            dlq = DeadLetterQueue(source.name)
            dlq.add(
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )

            result = SyncResult(
                source_name=source.name,
                entity_type=entity_type,
                status="failed",
                errors_count=1,
                error_details=dlq.to_dict(),
                duration_seconds=time.time() - start_time,
            )
            result.error_details["classified_error"] = type(classified_error).__name__
            result.error_details["attempt_count"] = attempt_count
            result.error_details["is_retryable"] = is_retryable_error(e)

            logger.error(f"Source {source.name} failed after {attempt_count} attempts: {e}")
            break

    # If we get here with an error, send permanent failure alert (Task 6.5)
    if last_error is not None and send_alerts:
        logger.error(
            f"Source {source.name} failed permanently after {attempt_count} attempts. "
            f"Sending alert..."
        )
        send_permanent_failure_alert(
            source_name=source.name,
            error=last_error,
            attempt_count=attempt_count,
            environment=os.environ.get("ENVIRONMENT", "development"),
            details={
                "duration_seconds": time.time() - start_time,
                "pipeline_name": "gong_to_postgres",
                "entity_type": entity_type,
            },
        )

    # Return failed result if we haven't returned yet
    return SyncResult(
        source_name=source.name,
        entity_type=entity_type,
        status="failed",
        errors_count=1,
        error_details={
            "error": str(last_error) if last_error else "Unknown error",
            "attempt_count": attempt_count,
        },
        duration_seconds=time.time() - start_time,
    )


def update_sync_status_from_result(result: SyncResult) -> None:
    """
    Update sync_status table from a SyncResult.

    Args:
        result: SyncResult from source sync
    """
    try:
        update_sync_status(
            entity_type=result.entity_type,
            status=result.status,
            items_synced=result.rows_synced,
            errors_count=result.errors_count,
            error_details=result.error_details if result.error_details else None,
        )
        logger.info(f"Updated sync_status for {result.entity_type}: {result.status}")
    except Exception as e:
        logger.error(f"Failed to update sync_status for {result.entity_type}: {e}")


def run_pipeline(
    parallel: bool = True,
    sources: list[str] | None = None,
    run_quality_checks: bool = True,
    continue_on_failure: bool = True,
    retry_config: RetryConfig | None = None,
    send_alerts: bool = True,
) -> dict[str, SyncResult]:
    """
    Run the full BigQuery to Postgres sync pipeline.

    Implements partial failure handling (Task 6.4): continues processing
    other sources even if one fails.

    Args:
        parallel: If True, run independent sources in parallel
        sources: Optional list of sources to run (calls, emails, opportunities).
                 If None, runs all sources.
        run_quality_checks: If True, run data quality checks after sync (Task 7.5)
        continue_on_failure: If True, continue processing other sources if one fails (Task 6.4)
        retry_config: Optional retry configuration for sources (Task 6.1)
        send_alerts: If True, send alerts for permanent failures (Task 6.5)

    Returns:
        Dict mapping source names to their SyncResult
    """
    if retry_config is None:
        retry_config = DEFAULT_RETRY_CONFIG

    start_time = time.time()
    run_id = f"run_{int(start_time)}"
    results: dict[str, SyncResult] = {}
    failed_sources: list[str] = []

    logger.info("=" * 60)
    logger.info("Starting BigQuery to Postgres DLT Pipeline")
    logger.info("=" * 60)
    logger.info(
        f"Retry config: max_retries={retry_config.max_retries}, "
        f"initial_delay={retry_config.initial_delay_seconds}s, "
        f"exponential_base={retry_config.exponential_base}"
    )
    logger.info(f"Continue on failure: {continue_on_failure}")

    # Create pipeline
    pipeline = create_pipeline()

    # Define sources with their entity types
    all_sources = {
        "calls": (gong_calls_source, "calls"),
        "emails": (gong_emails_source, "emails"),
        "opportunities": (gong_opportunities_source, "opportunities"),
    }

    # Filter to requested sources
    if sources:
        sources_to_run = {k: v for k, v in all_sources.items() if k in sources}
    else:
        sources_to_run = all_sources

    logger.info(f"Sources to sync: {list(sources_to_run.keys())}")
    logger.info(f"Parallel execution: {parallel}")

    if parallel and len(sources_to_run) > 1:
        # Run sources in parallel using ThreadPoolExecutor
        # Note: DLT sources are independent, so parallel execution is safe
        # Task 6.4: Parallel execution inherently supports partial failure
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for source_name, (source_factory, entity_type) in sources_to_run.items():
                # Create a new pipeline instance for each parallel source
                # to avoid state conflicts
                source_pipeline = create_pipeline()
                source = source_factory()
                future = executor.submit(
                    run_source_sync_with_retry,
                    source_pipeline,
                    source,
                    entity_type,
                    retry_config,
                    send_alerts,
                )
                futures[future] = source_name

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    result = future.result()
                    results[source_name] = result
                    # Update sync_status in database
                    update_sync_status_from_result(result)

                    if result.status == "failed":
                        failed_sources.append(source_name)

                except Exception as e:
                    logger.error(f"Source {source_name} raised exception: {e}")
                    failed_sources.append(source_name)
                    results[source_name] = SyncResult(
                        source_name=source_name,
                        entity_type=sources_to_run[source_name][1],
                        status="failed",
                        errors_count=1,
                        error_details={
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                    )
                    update_sync_status_from_result(results[source_name])

                    # Send alert for unexpected exceptions
                    if send_alerts:
                        send_permanent_failure_alert(
                            source_name=source_name,
                            error=e,
                            attempt_count=1,
                            environment=os.environ.get("ENVIRONMENT", "development"),
                        )
    else:
        # Run sources sequentially with partial failure handling (Task 6.4)
        for source_name, (source_factory, entity_type) in sources_to_run.items():
            try:
                source = source_factory()
                result = run_source_sync_with_retry(
                    pipeline,
                    source,
                    entity_type,
                    retry_config,
                    send_alerts,
                )
                results[source_name] = result
                # Update sync_status in database
                update_sync_status_from_result(result)

                if result.status == "failed":
                    failed_sources.append(source_name)
                    if not continue_on_failure:
                        logger.error(
                            f"Source {source_name} failed and continue_on_failure=False. "
                            f"Stopping pipeline."
                        )
                        break

            except Exception as e:
                logger.error(f"Source {source_name} raised unexpected exception: {e}")
                failed_sources.append(source_name)
                results[source_name] = SyncResult(
                    source_name=source_name,
                    entity_type=entity_type,
                    status="failed",
                    errors_count=1,
                    error_details={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                )
                update_sync_status_from_result(results[source_name])

                # Send alert for unexpected exceptions
                if send_alerts:
                    send_permanent_failure_alert(
                        source_name=source_name,
                        error=e,
                        attempt_count=1,
                        environment=os.environ.get("ENVIRONMENT", "development"),
                    )

                if not continue_on_failure:
                    logger.error(
                        f"Source {source_name} failed and continue_on_failure=False. "
                        f"Stopping pipeline."
                    )
                    break

    # Log sync status summary (Task 7.3)
    total_duration = time.time() - start_time
    total_rows = sum(r.rows_synced for r in results.values())
    total_errors = sum(r.errors_count for r in results.values())

    logger.info("=" * 60)
    logger.info("SYNC STATUS SUMMARY (Task 7.3)")
    logger.info("=" * 60)
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Total Duration: {total_duration:.2f} seconds")
    logger.info(f"Total Rows Synced: {total_rows}")
    logger.info(f"Total Errors: {total_errors}")
    logger.info("-" * 60)

    # Per-source metrics (Task 7.2)
    for source_name, result in results.items():
        status_str = "SUCCESS" if result.status == "success" else result.status.upper()
        logger.info(
            f"  {source_name}: {status_str} - "
            f"{result.rows_synced} rows, "
            f"{result.errors_count} errors, "
            f"{result.duration_seconds:.2f}s"
        )

    logger.info("=" * 60)

    # Run data quality checks (Task 7.5)
    if run_quality_checks:
        logger.info("Running data quality checks...")
        try:
            checker = DataQualityChecker()
            quality_results = checker.run_all_checks()

            # Store quality results in the first result's error_details for tracking
            # This is a simple approach; could be expanded to separate table
            for _source_name, result in results.items():
                if result.error_details is None:
                    result.error_details = {}
                if not isinstance(result.error_details, dict):
                    result.error_details = {"original": result.error_details}
                result.error_details["quality_checks"] = quality_results

        except Exception as e:
            logger.error(f"Data quality checks failed: {e}")

    # Final status log
    if total_errors == 0:
        logger.info("Pipeline completed successfully")
    else:
        logger.warning(f"Pipeline completed with {total_errors} total errors")

    return results


def verify_state_persistence() -> bool:
    """
    Verify that DLT state is being persisted correctly.

    Returns:
        True if state file exists and is valid JSON
    """
    state_path = os.path.join(os.path.dirname(__file__), "..", ".dlt", "state.json")
    state_path = os.path.normpath(state_path)

    if not os.path.exists(state_path):
        logger.warning(f"State file not found at {state_path}")
        return False

    try:
        with open(state_path) as f:
            state = json.load(f)
        logger.info(f"State file verified: {state_path}")
        logger.debug(f"State contents: {json.dumps(state, indent=2)}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"State file is not valid JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"Error reading state file: {e}")
        return False


def main():
    """Main entry point for CLI execution."""
    import argparse

    parser = argparse.ArgumentParser(description="BigQuery to Postgres DLT Pipeline for Gong data")
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run sources sequentially instead of in parallel",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["calls", "emails", "opportunities"],
        help="Specific sources to sync (default: all)",
    )
    parser.add_argument(
        "--verify-state",
        action="store_true",
        help="Verify state persistence after run",
    )
    parser.add_argument(
        "--skip-quality-checks",
        action="store_true",
        help="Skip data quality checks after sync (Task 7.5)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )
    # Task 6.1: Retry configuration
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed sources (Task 6.1, default: 3)",
    )
    parser.add_argument(
        "--initial-delay",
        type=float,
        default=1.0,
        help="Initial delay in seconds before first retry (Task 6.1, default: 1.0)",
    )
    # Task 6.4: Partial failure handling
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop pipeline if any source fails (disables Task 6.4 partial failure handling)",
    )
    # Task 6.5: Alerting
    parser.add_argument(
        "--no-alerts",
        action="store_true",
        help="Disable alerting for permanent failures (Task 6.5)",
    )

    args = parser.parse_args()

    # Update log level (Task 7.1 - structured logging)
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    # Also update DLT logging level (Task 7.4)
    configure_dlt_logging(log_level=args.log_level)

    # Create retry config from CLI args (Task 6.1)
    retry_config = RetryConfig(
        max_retries=args.max_retries,
        initial_delay_seconds=args.initial_delay,
    )

    # Run pipeline
    results = run_pipeline(
        parallel=not args.sequential,
        sources=args.sources,
        run_quality_checks=not args.skip_quality_checks,
        continue_on_failure=not args.stop_on_failure,
        retry_config=retry_config,
        send_alerts=not args.no_alerts,
    )

    # Verify state persistence if requested
    if args.verify_state:
        logger.info("\nVerifying state persistence...")
        if verify_state_persistence():
            logger.info("State persistence verified successfully")
        else:
            logger.error("State persistence verification failed")

    # Exit with error code if any source failed
    if any(r.status == "failed" for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
