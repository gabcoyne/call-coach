"""
DLT Pipeline Monitoring and Observability

Provides structured logging, metrics collection, and data quality checks
for the BigQuery to Postgres data sync pipeline.

Tasks completed:
- 7.1 Structured logging with INFO for progress, ERROR for failures
- 7.2 Metrics: rows_synced, errors_count, duration_seconds per source
- 7.3 Sync status summary at end of run
- 7.4 DLT built-in observability integration
- 7.5 Data quality checks (row count delta comparison)
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from google.cloud import bigquery

# Configure structured logging for DLT pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create logger for DLT pipeline
logger = logging.getLogger("dlt_pipeline")
logger.setLevel(logging.INFO)

# Also configure DLT's internal logging
dlt_logger = logging.getLogger("dlt")
dlt_logger.setLevel(logging.INFO)


@dataclass
class SourceMetrics:
    """Metrics for a single data source sync."""

    source_name: str
    rows_synced: int = 0
    errors_count: int = 0
    duration_seconds: float = 0.0
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    error_details: list[str] = field(default_factory=list)

    def complete(self, rows: int = 0, errors: int = 0) -> None:
        """Mark source sync as complete with final metrics."""
        self.end_time = time.time()
        self.duration_seconds = self.end_time - self.start_time
        self.rows_synced = rows
        self.errors_count = errors

    def add_error(self, error_msg: str) -> None:
        """Record an error during sync."""
        self.errors_count += 1
        self.error_details.append(error_msg)
        logger.error(f"[{self.source_name}] Error: {error_msg}")

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for logging/storage."""
        return {
            "source_name": self.source_name,
            "rows_synced": self.rows_synced,
            "errors_count": self.errors_count,
            "duration_seconds": round(self.duration_seconds, 2),
            "error_details": self.error_details if self.error_details else None,
        }


@dataclass
class PipelineMetrics:
    """Aggregate metrics for entire pipeline run."""

    run_id: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    source_metrics: dict[str, SourceMetrics] = field(default_factory=dict)

    def start_source(self, source_name: str) -> SourceMetrics:
        """Begin tracking metrics for a source."""
        logger.info(f"[{source_name}] Starting sync...")
        metrics = SourceMetrics(source_name=source_name)
        self.source_metrics[source_name] = metrics
        return metrics

    def complete_source(self, source_name: str, rows: int = 0, errors: int = 0) -> None:
        """Complete metrics tracking for a source."""
        if source_name in self.source_metrics:
            self.source_metrics[source_name].complete(rows, errors)
            metrics = self.source_metrics[source_name]
            logger.info(
                f"[{source_name}] Completed: "
                f"{metrics.rows_synced} rows synced, "
                f"{metrics.errors_count} errors, "
                f"{metrics.duration_seconds:.2f}s duration"
            )

    def get_source_metrics(self, source_name: str) -> SourceMetrics | None:
        """Get metrics for a specific source."""
        return self.source_metrics.get(source_name)

    @property
    def total_rows_synced(self) -> int:
        """Total rows synced across all sources."""
        return sum(m.rows_synced for m in self.source_metrics.values())

    @property
    def total_errors(self) -> int:
        """Total errors across all sources."""
        return sum(m.errors_count for m in self.source_metrics.values())

    @property
    def total_duration_seconds(self) -> float:
        """Total elapsed time for pipeline run."""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def complete(self) -> None:
        """Mark pipeline run as complete."""
        self.end_time = time.time()

    def log_summary(self) -> None:
        """Log final sync status summary (Task 7.3)."""
        self.complete()

        logger.info("=" * 60)
        logger.info("SYNC STATUS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Run ID: {self.run_id}")
        logger.info(f"Total Duration: {self.total_duration_seconds:.2f} seconds")
        logger.info(f"Total Rows Synced: {self.total_rows_synced}")
        logger.info(f"Total Errors: {self.total_errors}")
        logger.info("-" * 60)

        for source_name, metrics in self.source_metrics.items():
            status = "SUCCESS" if metrics.errors_count == 0 else "PARTIAL"
            logger.info(
                f"  {source_name}: {status} - "
                f"{metrics.rows_synced} rows, "
                f"{metrics.errors_count} errors, "
                f"{metrics.duration_seconds:.2f}s"
            )

        logger.info("=" * 60)

        # Log final status
        if self.total_errors == 0:
            logger.info("Pipeline completed successfully")
        else:
            logger.warning(f"Pipeline completed with {self.total_errors} total errors")

    def to_dict(self) -> dict[str, Any]:
        """Convert pipeline metrics to dictionary."""
        return {
            "run_id": self.run_id,
            "total_rows_synced": self.total_rows_synced,
            "total_errors": self.total_errors,
            "total_duration_seconds": round(self.total_duration_seconds, 2),
            "sources": {name: metrics.to_dict() for name, metrics in self.source_metrics.items()},
        }


class DataQualityChecker:
    """
    Data quality checks for BigQuery to Postgres sync (Task 7.5).

    Compares row counts between source (BigQuery) and destination (Postgres)
    to detect data loss or sync issues.
    """

    def __init__(
        self,
        bigquery_project: str = "prefect-data-warehouse",
        bigquery_dataset: str = "gongio_ft",
    ):
        self.bigquery_project = bigquery_project
        self.bigquery_dataset = bigquery_dataset
        self._bq_client: bigquery.Client | None = None

    @property
    def bq_client(self) -> bigquery.Client:
        """Lazy-load BigQuery client."""
        if self._bq_client is None:
            self._bq_client = bigquery.Client(project=self.bigquery_project)
        return self._bq_client

    def get_bigquery_count(self, table_name: str) -> int:
        """Get row count from BigQuery table."""
        query = f"""
        SELECT COUNT(*) as count
        FROM `{self.bigquery_project}.{self.bigquery_dataset}.{table_name}`
        WHERE _fivetran_deleted = FALSE
        """
        try:
            result = self.bq_client.query(query).result()
            for row in result:
                return int(row.count)
        except Exception as e:
            logger.error(f"Failed to get BigQuery count for {table_name}: {e}")
            return -1
        return 0

    def get_postgres_count(self, table_name: str) -> int:
        """Get row count from Postgres table."""
        # Import here to avoid circular dependency
        from db.connection import fetch_one

        try:
            result = fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
            return int(result["count"]) if result else 0
        except Exception as e:
            logger.error(f"Failed to get Postgres count for {table_name}: {e}")
            return -1

    def check_row_count_delta(
        self,
        bigquery_table: str,
        postgres_table: str,
        threshold_pct: float = 5.0,
    ) -> dict[str, Any]:
        """
        Compare row counts between BigQuery and Postgres.

        Args:
            bigquery_table: Source table name in BigQuery
            postgres_table: Destination table name in Postgres
            threshold_pct: Maximum acceptable difference percentage

        Returns:
            Dict with comparison results and pass/fail status
        """
        bq_count = self.get_bigquery_count(bigquery_table)
        pg_count = self.get_postgres_count(postgres_table)

        # Handle error cases
        if bq_count < 0 or pg_count < 0:
            return {
                "bigquery_table": bigquery_table,
                "postgres_table": postgres_table,
                "bigquery_count": bq_count,
                "postgres_count": pg_count,
                "delta": None,
                "delta_pct": None,
                "passed": False,
                "error": "Failed to retrieve row counts",
            }

        delta = bq_count - pg_count
        delta_pct = (abs(delta) / bq_count * 100) if bq_count > 0 else 0.0
        passed = delta_pct <= threshold_pct

        result = {
            "bigquery_table": bigquery_table,
            "postgres_table": postgres_table,
            "bigquery_count": bq_count,
            "postgres_count": pg_count,
            "delta": delta,
            "delta_pct": round(delta_pct, 2),
            "threshold_pct": threshold_pct,
            "passed": passed,
        }

        if passed:
            logger.info(
                f"Data quality check PASSED: {bigquery_table} -> {postgres_table} "
                f"(BQ: {bq_count}, PG: {pg_count}, delta: {delta_pct:.2f}%)"
            )
        else:
            logger.warning(
                f"Data quality check FAILED: {bigquery_table} -> {postgres_table} "
                f"(BQ: {bq_count}, PG: {pg_count}, delta: {delta_pct:.2f}% > {threshold_pct}%)"
            )

        return result

    def run_all_checks(self, threshold_pct: float = 5.0) -> list[dict[str, Any]]:
        """
        Run data quality checks for all synced tables.

        Returns:
            List of check results for each table pair
        """
        logger.info("Running data quality checks...")

        # Table mappings: BigQuery table -> Postgres table
        table_mappings = [
            ("call", "calls"),
            ("transcript", "transcripts"),
            ("call_speaker", "speakers"),
            # Emails and opportunities may not exist yet
        ]

        results = []
        for bq_table, pg_table in table_mappings:
            try:
                result = self.check_row_count_delta(bq_table, pg_table, threshold_pct)
                results.append(result)
            except Exception as e:
                logger.error(f"Quality check failed for {bq_table}: {e}")
                results.append(
                    {
                        "bigquery_table": bq_table,
                        "postgres_table": pg_table,
                        "passed": False,
                        "error": str(e),
                    }
                )

        # Summary
        passed_count = sum(1 for r in results if r.get("passed", False))
        total_count = len(results)
        logger.info(f"Data quality checks complete: {passed_count}/{total_count} passed")

        return results


def configure_dlt_logging(log_level: str = "INFO") -> None:
    """
    Configure DLT's built-in logging (Task 7.4).

    DLT uses Python's standard logging module. This function ensures
    DLT logs are captured and formatted consistently with pipeline logs.
    """
    # Set DLT's internal loggers
    dlt_loggers = [
        "dlt",
        "dlt.common",
        "dlt.extract",
        "dlt.normalize",
        "dlt.load",
        "dlt.pipeline",
    ]

    level = getattr(logging, log_level.upper(), logging.INFO)

    for logger_name in dlt_loggers:
        dlt_logger = logging.getLogger(logger_name)
        dlt_logger.setLevel(level)

    logger.info(f"DLT logging configured at {log_level} level")


def create_pipeline_metrics(run_id: str | None = None) -> PipelineMetrics:
    """
    Create a new pipeline metrics tracker.

    Args:
        run_id: Optional unique identifier for this run.
                If not provided, generates one from timestamp.

    Returns:
        PipelineMetrics instance for tracking this run
    """
    if run_id is None:
        run_id = f"run_{int(time.time())}"

    logger.info(f"Starting pipeline run: {run_id}")
    return PipelineMetrics(run_id=run_id)
