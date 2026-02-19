"""
DLT BigQuery to Postgres sync.

Syncs calls, emails, and opportunities from BigQuery (Fivetran-synced Gong data)
to Neon PostgreSQL using DLT for incremental loading.

Usage:
    uv run python -m flows.dlt_sync_flow

Schedule via cron (hourly):
    0 * * * * cd /path/to/call-coach && uv run python -m flows.dlt_sync_flow >> /var/log/dlt-sync.log 2>&1
"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import dlt

from dlt_pipeline.sources.calls import gong_calls_source
from dlt_pipeline.sources.emails import gong_emails_source
from dlt_pipeline.sources.opportunities import gong_opportunities_source

logger = logging.getLogger(__name__)


def _get_postgres_destination():
    """Get postgres destination with credentials from DATABASE_URL.

    For Neon Postgres, DLT requires a direct (unpooled) connection because it
    uses search_path in connection options, which is not supported by the pooler.
    This function automatically converts pooler URLs to direct URLs.
    """
    database_url = os.environ.get("DATABASE_URL_DIRECT") or os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    # Convert Neon pooler URL to direct URL by removing '-pooler' from hostname
    # Pooler URLs: ep-xxx-pooler.region.aws.neon.tech
    # Direct URLs: ep-xxx.region.aws.neon.tech
    if "-pooler" in database_url:
        database_url = database_url.replace("-pooler", "")
        logger.info("Converted pooler URL to direct URL for DLT compatibility")

    return dlt.destinations.postgres(credentials=database_url)


def sync_calls() -> dict[str, Any]:
    """
    Sync calls, transcripts, and speakers from BigQuery to Postgres.

    Uses DLT incremental loading based on _fivetran_synced timestamp.

    Returns:
        Dict with sync stats: {rows_synced: int, duration_seconds: float, status: str}
    """
    logger.info("Starting calls sync from BigQuery")
    start_time = datetime.now(UTC)

    try:
        pipeline = dlt.pipeline(
            pipeline_name="gong_calls_sync",
            destination=_get_postgres_destination(),
            dataset_name="public",
        )

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

        logger.info(f"Calls sync completed: {rows_synced} rows in {duration:.2f}s")
        return {
            "source": "calls",
            "status": "success",
            "rows_synced": rows_synced,
            "duration_seconds": round(duration, 2),
        }

    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        logger.error(f"Calls sync failed: {e}", exc_info=True)
        return {
            "source": "calls",
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
        }


def sync_emails() -> dict[str, Any]:
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
        pipeline = dlt.pipeline(
            pipeline_name="gong_emails_sync",
            destination=_get_postgres_destination(),
            dataset_name="public",
        )

        source = gong_emails_source()
        load_info = pipeline.run(source)

        duration = (datetime.now(UTC) - start_time).total_seconds()

        rows_synced = 0
        if load_info and hasattr(load_info, "load_packages"):
            for package in load_info.load_packages:
                if hasattr(package, "jobs"):
                    for job in package.jobs.get("completed_jobs", []):
                        if hasattr(job, "row_count"):
                            rows_synced += job.row_count

        logger.info(f"Emails sync completed: {rows_synced} rows in {duration:.2f}s")
        return {
            "source": "emails",
            "status": "success",
            "rows_synced": rows_synced,
            "duration_seconds": round(duration, 2),
        }

    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        logger.error(f"Emails sync failed: {e}", exc_info=True)
        return {
            "source": "emails",
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
        }


def sync_opportunities() -> dict[str, Any]:
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
        pipeline = dlt.pipeline(
            pipeline_name="gong_opportunities_sync",
            destination=_get_postgres_destination(),
            dataset_name="public",
        )

        source = gong_opportunities_source()
        load_info = pipeline.run(source)

        duration = (datetime.now(UTC) - start_time).total_seconds()

        rows_synced = 0
        if load_info and hasattr(load_info, "load_packages"):
            for package in load_info.load_packages:
                if hasattr(package, "jobs"):
                    for job in package.jobs.get("completed_jobs", []):
                        if hasattr(job, "row_count"):
                            rows_synced += job.row_count

        logger.info(f"Opportunities sync completed: {rows_synced} rows in {duration:.2f}s")
        return {
            "source": "opportunities",
            "status": "success",
            "rows_synced": rows_synced,
            "duration_seconds": round(duration, 2),
        }

    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        logger.error(f"Opportunities sync failed: {e}", exc_info=True)
        return {
            "source": "opportunities",
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
        }


def run_sync(
    sync_calls_enabled: bool = True,
    sync_emails_enabled: bool = True,
    sync_opportunities_enabled: bool = True,
) -> dict[str, Any]:
    """
    Run DLT sync from BigQuery to Postgres.

    Syncs:
    - Calls (with transcripts and speakers)
    - Emails (with sender and recipients)
    - Opportunities (with call linkages)

    Args:
        sync_calls_enabled: Enable calls/transcripts/speakers sync
        sync_emails_enabled: Enable emails sync
        sync_opportunities_enabled: Enable opportunities sync

    Returns:
        Dict with overall sync results and per-source stats

    Example:
        >>> result = run_sync()
        >>> result = run_sync(sync_emails_enabled=False)
    """
    logger.info("Starting BigQuery to Postgres DLT sync")
    start_time = datetime.now(UTC)

    results: dict[str, Any] = {
        "sync_name": "bigquery-dlt-sync",
        "start_time": start_time.isoformat(),
        "sources": {},
    }

    all_success = True
    total_rows = 0

    if sync_calls_enabled:
        calls_result = sync_calls()
        results["sources"]["calls"] = calls_result
        if calls_result["status"] != "success":
            all_success = False
        else:
            total_rows += calls_result.get("rows_synced", 0)

    if sync_emails_enabled:
        emails_result = sync_emails()
        results["sources"]["emails"] = emails_result
        if emails_result["status"] != "success":
            all_success = False
        else:
            total_rows += emails_result.get("rows_synced", 0)

    if sync_opportunities_enabled:
        opps_result = sync_opportunities()
        results["sources"]["opportunities"] = opps_result
        if opps_result["status"] != "success":
            all_success = False
        else:
            total_rows += opps_result.get("rows_synced", 0)

    end_time = datetime.now(UTC)
    duration = (end_time - start_time).total_seconds()

    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = round(duration, 2)
    results["total_rows_synced"] = total_rows
    results["status"] = "success" if all_success else "partial_failure"

    if all_success:
        logger.info(f"BigQuery DLT sync completed: {total_rows} rows in {duration:.2f}s")
    else:
        failed = [n for n, r in results["sources"].items() if r["status"] != "success"]
        logger.warning(
            f"BigQuery DLT sync partial failure: {failed}, {total_rows} rows in {duration:.2f}s"
        )

    return results


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    result = run_sync()

    print("\n" + "=" * 80)
    print("BIGQUERY DLT SYNC RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))
