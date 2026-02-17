"""
Prefect flow for DLT BigQuery to Postgres sync.

Orchestrates the DLT pipeline to sync calls, emails, and opportunities from
BigQuery (Fivetran-synced Gong data) to Neon PostgreSQL.

Provides granular observability with separate tasks for each data source.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

import dlt
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from dlt_pipeline.sources.calls import gong_calls_source
from dlt_pipeline.sources.emails import gong_emails_source
from dlt_pipeline.sources.opportunities import gong_opportunities_source

logger = logging.getLogger(__name__)


# ============================================================================
# DLT SOURCE TASKS
# ============================================================================


@task(name="sync_calls", retries=2, retry_delay_seconds=60)
def sync_calls_task() -> dict[str, Any]:
    """
    Sync calls, transcripts, and speakers from BigQuery to Postgres.

    Uses DLT incremental loading based on _fivetran_synced timestamp.

    Returns:
        Dict with sync stats: {rows_synced: int, duration_seconds: float, status: str}
    """
    logger.info("Starting calls sync from BigQuery")
    start_time = datetime.now(UTC)

    try:
        # Initialize DLT pipeline
        pipeline = dlt.pipeline(
            pipeline_name="gong_calls_sync",
            destination="postgres",
            dataset_name="public",
        )

        # Run the calls source
        source = gong_calls_source()
        load_info = pipeline.run(source)

        duration = (datetime.now(UTC) - start_time).total_seconds()

        # Extract row counts from load_info
        rows_synced = 0
        if load_info and hasattr(load_info, "load_packages"):
            for package in load_info.load_packages:
                if hasattr(package, "jobs"):
                    for job in package.jobs.get("completed_jobs", []):
                        if hasattr(job, "row_count"):
                            rows_synced += job.row_count

        result = {
            "source": "calls",
            "status": "success",
            "rows_synced": rows_synced,
            "duration_seconds": round(duration, 2),
        }

        logger.info(f"Calls sync completed: {rows_synced} rows in {duration:.2f}s")
        return result

    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        logger.error(f"Calls sync failed: {e}", exc_info=True)
        return {
            "source": "calls",
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
        }


@task(name="sync_emails", retries=2, retry_delay_seconds=60)
def sync_emails_task() -> dict[str, Any]:
    """
    Sync emails from BigQuery to Postgres.

    Includes sender, recipients, and opportunity linkage.
    Uses DLT incremental loading based on _fivetran_synced timestamp.

    Returns:
        Dict with sync stats: {rows_synced: int, duration_seconds: float, status: str}
    """
    logger.info("Starting emails sync from BigQuery")
    start_time = datetime.now(UTC)

    try:
        # Initialize DLT pipeline
        pipeline = dlt.pipeline(
            pipeline_name="gong_emails_sync",
            destination="postgres",
            dataset_name="public",
        )

        # Run the emails source
        source = gong_emails_source()
        load_info = pipeline.run(source)

        duration = (datetime.now(UTC) - start_time).total_seconds()

        # Extract row counts from load_info
        rows_synced = 0
        if load_info and hasattr(load_info, "load_packages"):
            for package in load_info.load_packages:
                if hasattr(package, "jobs"):
                    for job in package.jobs.get("completed_jobs", []):
                        if hasattr(job, "row_count"):
                            rows_synced += job.row_count

        result = {
            "source": "emails",
            "status": "success",
            "rows_synced": rows_synced,
            "duration_seconds": round(duration, 2),
        }

        logger.info(f"Emails sync completed: {rows_synced} rows in {duration:.2f}s")
        return result

    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        logger.error(f"Emails sync failed: {e}", exc_info=True)
        return {
            "source": "emails",
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
        }


@task(name="sync_opportunities", retries=2, retry_delay_seconds=60)
def sync_opportunities_task() -> dict[str, Any]:
    """
    Sync opportunities and call-opportunity linkages from BigQuery to Postgres.

    Includes account resolution and owner email mapping.
    Uses DLT incremental loading based on LastModifiedDate.

    Returns:
        Dict with sync stats: {rows_synced: int, duration_seconds: float, status: str}
    """
    logger.info("Starting opportunities sync from BigQuery")
    start_time = datetime.now(UTC)

    try:
        # Initialize DLT pipeline
        pipeline = dlt.pipeline(
            pipeline_name="gong_opportunities_sync",
            destination="postgres",
            dataset_name="public",
        )

        # Run the opportunities source
        source = gong_opportunities_source()
        load_info = pipeline.run(source)

        duration = (datetime.now(UTC) - start_time).total_seconds()

        # Extract row counts from load_info
        rows_synced = 0
        if load_info and hasattr(load_info, "load_packages"):
            for package in load_info.load_packages:
                if hasattr(package, "jobs"):
                    for job in package.jobs.get("completed_jobs", []):
                        if hasattr(job, "row_count"):
                            rows_synced += job.row_count

        result = {
            "source": "opportunities",
            "status": "success",
            "rows_synced": rows_synced,
            "duration_seconds": round(duration, 2),
        }

        logger.info(f"Opportunities sync completed: {rows_synced} rows in {duration:.2f}s")
        return result

    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        logger.error(f"Opportunities sync failed: {e}", exc_info=True)
        return {
            "source": "opportunities",
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
        }


# ============================================================================
# MAIN FLOW
# ============================================================================


@flow(
    name="bigquery-dlt-sync",
    description="Sync Gong data from BigQuery to Postgres using DLT",
    task_runner=ConcurrentTaskRunner(),
    retries=2,
    retry_delay_seconds=300,
)
def bigquery_dlt_sync_flow(
    sync_calls: bool = True,
    sync_emails: bool = True,
    sync_opportunities: bool = True,
) -> dict[str, Any]:
    """
    Main flow for syncing Gong data from BigQuery to Postgres.

    Orchestrates DLT pipeline to sync:
    - Calls (with transcripts and speakers)
    - Emails (with sender and recipients)
    - Opportunities (with call linkages)

    Each source runs as a separate Prefect task for granular observability.
    Sources can be selectively enabled/disabled.

    Args:
        sync_calls: Enable calls/transcripts/speakers sync (default: True)
        sync_emails: Enable emails sync (default: True)
        sync_opportunities: Enable opportunities sync (default: True)

    Returns:
        Dict with overall sync results and per-source stats

    Example:
        >>> # Run full sync
        >>> result = bigquery_dlt_sync_flow()
        >>>
        >>> # Sync only calls
        >>> result = bigquery_dlt_sync_flow(sync_emails=False, sync_opportunities=False)
    """
    logger.info("Starting BigQuery to Postgres DLT sync")
    start_time = datetime.now(UTC)

    results = {
        "flow_name": "bigquery-dlt-sync",
        "start_time": start_time.isoformat(),
        "sources": {},
    }

    # Track overall status
    all_success = True
    total_rows = 0

    # Run enabled sources
    # Note: Using ConcurrentTaskRunner, these can run in parallel
    sources: dict[str, Any] = results["sources"]  # type: ignore[assignment]
    if sync_calls:
        calls_result = sync_calls_task()
        sources["calls"] = calls_result
        if calls_result["status"] != "success":
            all_success = False
        else:
            total_rows += calls_result.get("rows_synced", 0)

    if sync_emails:
        emails_result = sync_emails_task()
        sources["emails"] = emails_result
        if emails_result["status"] != "success":
            all_success = False
        else:
            total_rows += emails_result.get("rows_synced", 0)

    if sync_opportunities:
        opps_result = sync_opportunities_task()
        sources["opportunities"] = opps_result
        if opps_result["status"] != "success":
            all_success = False
        else:
            total_rows += opps_result.get("rows_synced", 0)

    # Calculate totals
    end_time = datetime.now(UTC)
    duration = (end_time - start_time).total_seconds()

    results["sources"] = sources  # type: ignore[index]
    results["end_time"] = end_time.isoformat()  # type: ignore[index]
    results["duration_seconds"] = round(duration, 2)  # type: ignore[index,arg-type]
    results["total_rows_synced"] = total_rows  # type: ignore[index,assignment]
    results["status"] = "success" if all_success else "partial_failure"  # type: ignore[index]

    # Log summary
    if all_success:
        logger.info(
            f"BigQuery DLT sync completed successfully: "
            f"{total_rows} total rows in {duration:.2f}s"
        )
    else:
        failed_sources = [name for name, res in sources.items() if res["status"] != "success"]
        logger.warning(
            f"BigQuery DLT sync completed with failures: "
            f"failed sources: {failed_sources}, "
            f"{total_rows} rows synced in {duration:.2f}s"
        )

    return results


# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================

# NOTE: Tasks 8.6-8.9 require Prefect Cloud deployment credentials
#
# To deploy this flow to Prefect Cloud:
#
# 1. Authenticate with Prefect Cloud:
#    prefect cloud login
#
# 2. Create deployment with hourly schedule:
#    from prefect.deployments import Deployment
#    from prefect.server.schemas.schedules import CronSchedule
#
#    deployment = Deployment.build_from_flow(
#        flow=bigquery_dlt_sync_flow,
#        name="bigquery-dlt-sync-hourly",
#        schedule=CronSchedule(cron="0 * * * *", timezone="UTC"),  # Hourly
#        work_pool_name="default",
#    )
#    deployment.apply()
#
# 3. Or apply via CLI:
#    prefect deployment apply bigquery-dlt-sync-deployment.yaml
#
# Requires: PREFECT_API_URL and PREFECT_API_KEY environment variables


if __name__ == "__main__":
    """
    Local execution for testing:

    uv run python -m flows.dlt_sync_flow

    Or run with specific sources:

    uv run python -c "from flows.dlt_sync_flow import bigquery_dlt_sync_flow; print(bigquery_dlt_sync_flow(sync_emails=False))"
    """
    from dotenv import load_dotenv

    load_dotenv()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run full sync
    result = bigquery_dlt_sync_flow()

    # Print results
    print("\n" + "=" * 80)
    print("BIGQUERY DLT SYNC RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))
