#!/usr/bin/env python3
"""
BigQuery Data Sync Script

Incrementally syncs data from BigQuery (Salesforce/Gong) to Neon PostgreSQL.
Can be run as a background task or cron job.

Data sources:
- Opportunities: salesforce_ft.opportunity (with account and user joins)
- Calls: gongio_ft.call (with speakers and transcripts)

Usage:
    # Incremental sync (default)
    uv run python scripts/sync_bigquery_data.py

    # Full sync (ignore last sync timestamp)
    uv run python scripts/sync_bigquery_data.py --full-sync

    # Sync only opportunities or calls
    uv run python scripts/sync_bigquery_data.py --opportunities-only
    uv run python scripts/sync_bigquery_data.py --calls-only
"""

import argparse
import json
import logging
from datetime import UTC, datetime
from typing import Any

import psycopg2
import psycopg2.extras
from google.cloud import bigquery

from coaching_mcp.shared import settings

logger = logging.getLogger(__name__)


def get_bigquery_client() -> bigquery.Client:
    """Initialize BigQuery client using gcloud credentials."""
    import subprocess  # nosec B404 - subprocess needed for gcloud CLI

    try:
        result = subprocess.run(  # nosec B603, B607 - gcloud is a trusted command
            ["gcloud", "auth", "print-access-token"], capture_output=True, text=True, check=True
        )
        token = result.stdout.strip()
        from google.oauth2.credentials import Credentials

        credentials = Credentials(token=token)
        return bigquery.Client(project="prefect-data-warehouse", credentials=credentials)
    except Exception as e:
        logger.warning(f"Could not use gcloud auth ({e}), trying default credentials...")
        return bigquery.Client(project="prefect-data-warehouse")


def get_db_connection():
    """Get database connection from settings."""
    return psycopg2.connect(settings.database_url)


def get_last_sync_timestamp(entity_type: str) -> datetime | None:
    """Get last sync timestamp from sync_status table."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT last_sync_timestamp FROM sync_status WHERE entity_type = %s", (entity_type,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                ts = result[0]
                return ts if isinstance(ts, datetime) else None
            return None


def update_sync_status(
    entity_type: str,
    status: str,
    items_synced: int,
    errors_count: int = 0,
) -> None:
    """Update sync_status table after sync completes."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sync_status (entity_type, last_sync_timestamp, last_sync_status, items_synced, errors_count, updated_at)
                VALUES (%s, NOW(), %s, %s, %s, NOW())
                ON CONFLICT (entity_type) DO UPDATE SET
                    last_sync_timestamp = NOW(),
                    last_sync_status = %s,
                    items_synced = %s,
                    errors_count = %s,
                    updated_at = NOW()
                """,
                (
                    entity_type,
                    status,
                    items_synced,
                    errors_count,
                    status,
                    items_synced,
                    errors_count,
                ),
            )
            conn.commit()


def sync_opportunities(last_sync: datetime | None = None) -> dict[str, int]:
    """
    Incrementally sync opportunities from BigQuery.

    Args:
        last_sync: Only fetch records modified after this timestamp

    Returns:
        Dict with counts: {found, inserted, updated, errors}
    """
    stats = {"found": 0, "inserted": 0, "updated": 0, "errors": 0}

    bq_client = get_bigquery_client()

    # Build query with optional incremental filter
    where_clause = "WHERE o.is_deleted = FALSE"
    if last_sync:
        where_clause += f" AND o.system_modstamp > '{last_sync.isoformat()}'"

    query = f"""
    SELECT
        o.id as gong_opportunity_id,
        o.name as name,
        a.name as account_name,
        u.email as owner_email,
        o.stage_name as stage,
        o.close_date as close_date,
        o.amount as amount,
        o.system_modstamp as last_modified
    FROM `prefect-data-warehouse.salesforce_ft.opportunity` o
    LEFT JOIN `prefect-data-warehouse.salesforce_ft.account` a ON o.account_id = a.id
    LEFT JOIN `prefect-data-warehouse.salesforce_ft.user` u ON o.owner_id = u.id
    {where_clause}
    ORDER BY o.system_modstamp ASC
    """

    logger.info(f"Fetching opportunities from BigQuery (since: {last_sync})")

    try:
        opps_df = bq_client.query(query).to_dataframe()
        stats["found"] = len(opps_df)
        logger.info(f"Found {len(opps_df)} opportunities to sync")

        if len(opps_df) == 0:
            return stats

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                for _, row in opps_df.iterrows():
                    try:
                        cursor.execute(
                            "SELECT id FROM opportunities WHERE gong_opportunity_id = %s",
                            (row["gong_opportunity_id"],),
                        )
                        existing = cursor.fetchone()

                        if existing:
                            cursor.execute(
                                """
                                UPDATE opportunities SET
                                    name = %s, account_name = %s, owner_email = %s,
                                    stage = %s, close_date = %s, amount = %s, updated_at = NOW()
                                WHERE gong_opportunity_id = %s
                                """,
                                (
                                    row["name"],
                                    row["account_name"],
                                    row["owner_email"],
                                    row["stage"],
                                    row["close_date"],
                                    row["amount"],
                                    row["gong_opportunity_id"],
                                ),
                            )
                            stats["updated"] += 1
                        else:
                            cursor.execute(
                                """
                                INSERT INTO opportunities (
                                    gong_opportunity_id, name, account_name, owner_email,
                                    stage, close_date, amount, metadata
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    row["gong_opportunity_id"],
                                    row["name"],
                                    row["account_name"],
                                    row["owner_email"],
                                    row["stage"],
                                    row["close_date"],
                                    row["amount"],
                                    psycopg2.extras.Json({"source": "salesforce_ft"}),
                                ),
                            )
                            stats["inserted"] += 1

                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error syncing opportunity {row['name']}: {e}")

                conn.commit()

    except Exception as e:
        logger.error(f"BigQuery query failed: {e}")
        stats["errors"] += 1
        raise

    return stats


def sync_calls(last_sync: datetime | None = None) -> dict[str, int]:
    """
    Incrementally sync calls from BigQuery.

    Args:
        last_sync: Only fetch records modified after this timestamp

    Returns:
        Dict with counts: {found, inserted, updated, errors}
    """
    stats = {"found": 0, "inserted": 0, "updated": 0, "errors": 0}

    bq_client = get_bigquery_client()

    # Build query with optional incremental filter
    where_clause = "WHERE c._fivetran_deleted = FALSE"
    if last_sync:
        where_clause += f" AND c._fivetran_synced > '{last_sync.isoformat()}'"

    query = f"""
    SELECT
        c.id,
        c.title,
        c.scheduled,
        c.duration,
        c.purpose,
        c.url,
        c.started,
        c._fivetran_synced
    FROM `prefect-data-warehouse.gongio_ft.call` c
    {where_clause}
    ORDER BY c._fivetran_synced ASC
    LIMIT 1000
    """

    logger.info(f"Fetching calls from BigQuery (since: {last_sync})")

    try:
        calls_df = bq_client.query(query).to_dataframe()
        stats["found"] = len(calls_df)
        logger.info(f"Found {len(calls_df)} calls to sync")

        if len(calls_df) == 0:
            return stats

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                for _, row in calls_df.iterrows():
                    try:
                        cursor.execute("SELECT id FROM calls WHERE gong_call_id = %s", (row["id"],))
                        existing = cursor.fetchone()

                        if existing:
                            cursor.execute(
                                """
                                UPDATE calls SET
                                    title = %s, scheduled_at = %s, duration_seconds = %s,
                                    call_type = %s
                                WHERE gong_call_id = %s
                                """,
                                (
                                    row["title"],
                                    row["scheduled"],
                                    int(row["duration"]) if row["duration"] else None,
                                    row["purpose"],
                                    row["id"],
                                ),
                            )
                            stats["updated"] += 1
                        else:
                            cursor.execute(
                                """
                                INSERT INTO calls (
                                    gong_call_id, title, scheduled_at, duration_seconds,
                                    call_type, date, processed_at, metadata
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (gong_call_id) DO NOTHING
                                """,
                                (
                                    row["id"],
                                    row["title"],
                                    row["scheduled"],
                                    int(row["duration"]) if row["duration"] else None,
                                    row["purpose"],
                                    row["scheduled"].date() if row["scheduled"] else None,
                                    row["scheduled"],
                                    psycopg2.extras.Json({"gong_url": row["url"]}),
                                ),
                            )
                            stats["inserted"] += 1
                        conn.commit()

                    except Exception as e:
                        conn.rollback()
                        stats["errors"] += 1
                        logger.error(f"Error syncing call {row['id']}: {e}")

    except Exception as e:
        logger.error(f"BigQuery query failed: {e}")
        stats["errors"] += 1
        raise

    return stats


def sync_bigquery_data(
    sync_opportunities_flag: bool = True,
    sync_calls_flag: bool = True,
    full_sync: bool = False,
) -> dict[str, Any]:
    """
    Main sync function: Sync data from BigQuery to Postgres.

    Args:
        sync_opportunities_flag: Whether to sync opportunities
        sync_calls_flag: Whether to sync calls
        full_sync: If True, ignore last_sync and do full refresh

    Returns:
        Dict with sync results for each entity type
    """
    start_time = datetime.now(UTC)
    logger.info(f"BigQuery sync started at {start_time.isoformat()}")
    logger.info(f"Full sync: {full_sync}")

    results: dict[str, Any] = {
        "start_time": start_time.isoformat(),
        "full_sync": full_sync,
        "opportunities": None,
        "calls": None,
    }

    # Sync opportunities
    if sync_opportunities_flag:
        last_sync = None if full_sync else get_last_sync_timestamp("opportunities")
        opp_stats = sync_opportunities(last_sync)
        results["opportunities"] = opp_stats

        status = "success" if opp_stats["errors"] == 0 else "partial"
        total_synced = opp_stats["inserted"] + opp_stats["updated"]
        update_sync_status("opportunities", status, total_synced, opp_stats["errors"])

        logger.info(f"Opportunities sync: {opp_stats}")

    # Sync calls
    if sync_calls_flag:
        last_sync = None if full_sync else get_last_sync_timestamp("calls")
        call_stats = sync_calls(last_sync)
        results["calls"] = call_stats

        status = "success" if call_stats["errors"] == 0 else "partial"
        total_synced = call_stats["inserted"] + call_stats["updated"]
        update_sync_status("calls", status, total_synced, call_stats["errors"])

        logger.info(f"Calls sync: {call_stats}")

    end_time = datetime.now(UTC)
    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = (end_time - start_time).total_seconds()

    logger.info(f"BigQuery sync completed in {results['duration_seconds']:.1f}s")

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Sync data from BigQuery to Postgres")
    parser.add_argument("--full-sync", action="store_true", help="Ignore last sync timestamp")
    parser.add_argument("--opportunities-only", action="store_true", help="Only sync opportunities")
    parser.add_argument("--calls-only", action="store_true", help="Only sync calls")
    args = parser.parse_args()

    # Determine what to sync
    sync_opps = not args.calls_only
    sync_calls_flag = not args.opportunities_only

    result = sync_bigquery_data(
        sync_opportunities_flag=sync_opps,
        sync_calls_flag=sync_calls_flag,
        full_sync=args.full_sync,
    )

    print("\n" + "=" * 60)
    print("BIGQUERY SYNC RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    main()
