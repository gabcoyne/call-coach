#!/usr/bin/env python3
"""
Import opportunities data from BigQuery into local database.

Usage:
    uv run python scripts/import_opportunities_from_bigquery.py [--limit N] [--dry-run]
"""

import argparse
from typing import Any

import psycopg2
from google.cloud import bigquery

from coaching_mcp.shared import settings


def get_bigquery_client() -> bigquery.Client:
    """Initialize BigQuery client using gcloud credentials."""
    import subprocess  # nosec B404 - subprocess needed for gcloud CLI

    try:
        # Try to use gcloud auth to get access token
        result = subprocess.run(  # nosec B603, B607 - gcloud is a trusted command
            ["gcloud", "auth", "print-access-token"], capture_output=True, text=True, check=True
        )
        token = result.stdout.strip()

        # Create credentials from access token
        from google.oauth2.credentials import Credentials

        credentials = Credentials(token=token)
        return bigquery.Client(project="prefect-data-warehouse", credentials=credentials)
    except Exception as e:
        print(f"Warning: Could not use gcloud auth ({e}), trying default credentials...")
        # Fall back to default credentials
        return bigquery.Client(project="prefect-data-warehouse")


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(settings.database_url)


def check_bigquery_tables(bq_client: bigquery.Client) -> dict[str, bool]:
    """Check which tables exist in BigQuery."""
    tables = {}

    # Check Salesforce Fivetran tables (salesforce_ft)
    for table in ["opportunity", "account", "user"]:
        query = f"""
        SELECT COUNT(*) as cnt
        FROM `prefect-data-warehouse.salesforce_ft.{table}`
        LIMIT 1
        """
        try:
            list(bq_client.query(query).result())  # Check if table exists
            tables[f"salesforce_ft.{table}"] = True
            print(f"  ✓ salesforce_ft.{table} - available")
        except Exception as e:
            tables[f"salesforce_ft.{table}"] = False
            print(f"  ✗ salesforce_ft.{table} - not available ({str(e)[:50]})")

    # Check Gong tables
    for table in ["opportunity", "call"]:
        query = f"""
        SELECT COUNT(*) as cnt
        FROM `prefect-data-warehouse.gongio_ft.{table}`
        LIMIT 1
        """
        try:
            list(bq_client.query(query).result())  # Check if table exists
            tables[f"gongio_ft.{table}"] = True
            print(f"  ✓ gongio_ft.{table} - available")
        except Exception as e:
            tables[f"gongio_ft.{table}"] = False
            print(f"  ✗ gongio_ft.{table} - not available ({str(e)[:50]})")

    return tables


def import_opportunities_from_salesforce(
    bq_client: bigquery.Client, conn, limit: int | None = None, dry_run: bool = False
) -> dict[str, Any]:
    """
    Import opportunities from BigQuery Salesforce tables.

    Joins opportunity with account and user tables for complete data.
    """
    stats: dict[str, Any] = {
        "opportunities_found": 0,
        "opportunities_imported": 0,
        "opportunities_updated": 0,
        "errors": [],
    }

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
    WHERE o.is_deleted = FALSE
    ORDER BY o.system_modstamp DESC
    {f'LIMIT {limit}' if limit else ''}
    """

    print("Fetching opportunities from BigQuery (Salesforce)...")
    try:
        opps_df = bq_client.query(query).to_dataframe()
    except Exception as e:
        stats["errors"].append(f"Query failed: {e}")
        return stats

    stats["opportunities_found"] = len(opps_df)
    print(f"Found {len(opps_df)} opportunities")

    if dry_run:
        print("\n[DRY RUN] Would import the following opportunities:")
        for _, row in opps_df.head(10).iterrows():
            print(
                f"  - {row['name']} ({row['account_name']}) - {row['stage']} - ${row['amount'] or 0:,.0f}"
            )
        if len(opps_df) > 10:
            print(f"  ... and {len(opps_df) - 10} more")
        return stats

    with conn.cursor() as cursor:
        for _, row in opps_df.iterrows():
            try:
                # Check if opportunity already exists
                cursor.execute(
                    "SELECT id FROM opportunities WHERE gong_opportunity_id = %s",
                    (row["gong_opportunity_id"],),
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing opportunity
                    cursor.execute(
                        """
                        UPDATE opportunities SET
                            name = %s,
                            account_name = %s,
                            owner_email = %s,
                            stage = %s,
                            close_date = %s,
                            amount = %s,
                            updated_at = NOW()
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
                    stats["opportunities_updated"] += 1
                else:
                    # Insert new opportunity
                    cursor.execute(
                        """
                        INSERT INTO opportunities (
                            gong_opportunity_id, name, account_name, owner_email,
                            stage, close_date, amount, health_score, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            row["gong_opportunity_id"],
                            row["name"],
                            row["account_name"],
                            row["owner_email"],
                            row["stage"],
                            row["close_date"],
                            row["amount"],
                            None,  # health_score - will be calculated
                            psycopg2.extras.Json({"source": "salesforce"}),
                        ),
                    )
                    stats["opportunities_imported"] += 1

            except Exception as e:
                stats["errors"].append(f"Error processing {row['name']}: {e}")
                continue

        conn.commit()

    return stats


def import_opportunities_from_gong(
    bq_client: bigquery.Client, conn, limit: int | None = None, dry_run: bool = False
) -> dict[str, Any]:
    """
    Import opportunities from BigQuery Gong tables (fallback).
    """
    stats: dict[str, Any] = {
        "opportunities_found": 0,
        "opportunities_imported": 0,
        "opportunities_updated": 0,
        "errors": [],
    }

    query = f"""
    SELECT
        id as gong_opportunity_id,
        name,
        account_name,
        owner_email,
        stage,
        close_date,
        amount,
        health_score,
        _fivetran_synced as last_modified
    FROM `prefect-data-warehouse.gongio_ft.opportunity`
    WHERE _fivetran_deleted = FALSE
    ORDER BY _fivetran_synced DESC
    {f'LIMIT {limit}' if limit else ''}
    """

    print("Fetching opportunities from BigQuery (Gong)...")
    try:
        opps_df = bq_client.query(query).to_dataframe()
    except Exception as e:
        stats["errors"].append(f"Query failed: {e}")
        return stats

    stats["opportunities_found"] = len(opps_df)
    print(f"Found {len(opps_df)} opportunities")

    if dry_run:
        print("\n[DRY RUN] Would import the following opportunities:")
        for _, row in opps_df.head(10).iterrows():
            print(
                f"  - {row['name']} ({row.get('account_name', 'N/A')}) - {row.get('stage', 'N/A')}"
            )
        if len(opps_df) > 10:
            print(f"  ... and {len(opps_df) - 10} more")
        return stats

    with conn.cursor() as cursor:
        for _, row in opps_df.iterrows():
            try:
                # Check if opportunity already exists
                cursor.execute(
                    "SELECT id FROM opportunities WHERE gong_opportunity_id = %s",
                    (str(row["gong_opportunity_id"]),),
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing opportunity
                    cursor.execute(
                        """
                        UPDATE opportunities SET
                            name = %s,
                            account_name = %s,
                            owner_email = %s,
                            stage = %s,
                            close_date = %s,
                            amount = %s,
                            health_score = %s,
                            updated_at = NOW()
                        WHERE gong_opportunity_id = %s
                        """,
                        (
                            row["name"],
                            row.get("account_name"),
                            row.get("owner_email"),
                            row.get("stage"),
                            row.get("close_date"),
                            row.get("amount"),
                            row.get("health_score"),
                            str(row["gong_opportunity_id"]),
                        ),
                    )
                    stats["opportunities_updated"] += 1
                else:
                    # Insert new opportunity
                    cursor.execute(
                        """
                        INSERT INTO opportunities (
                            gong_opportunity_id, name, account_name, owner_email,
                            stage, close_date, amount, health_score, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            str(row["gong_opportunity_id"]),
                            row["name"],
                            row.get("account_name"),
                            row.get("owner_email"),
                            row.get("stage"),
                            row.get("close_date"),
                            row.get("amount"),
                            row.get("health_score"),
                            psycopg2.extras.Json({"source": "gong"}),
                        ),
                    )
                    stats["opportunities_imported"] += 1

            except Exception as e:
                stats["errors"].append(f"Error processing {row['name']}: {e}")
                continue

        conn.commit()

    return stats


def update_sync_status(conn, items_synced: int, status: str = "success"):
    """Update the sync_status table for opportunities."""
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sync_status (entity_type, last_sync_timestamp, last_sync_status, items_synced, updated_at)
            VALUES ('opportunities', NOW(), %s, %s, NOW())
            ON CONFLICT (entity_type) DO UPDATE SET
                last_sync_timestamp = NOW(),
                last_sync_status = %s,
                items_synced = %s,
                updated_at = NOW()
            """,
            (status, items_synced, status, items_synced),
        )
        conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Import opportunities from BigQuery")
    parser.add_argument("--limit", type=int, help="Limit number of opportunities to import")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be imported without making changes",
    )
    parser.add_argument(
        "--source",
        choices=["salesforce", "gong", "auto"],
        default="auto",
        help="Data source to use (default: auto-detect)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("BigQuery Opportunities Import")
    print("=" * 60)
    if args.limit:
        print(f"Limit: {args.limit} opportunities")
    if args.dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    print()

    bq_client = get_bigquery_client()

    print("Checking available BigQuery tables...")
    tables = check_bigquery_tables(bq_client)
    print()

    with get_db_connection() as conn:
        # Determine which source to use
        if args.source == "salesforce" or (
            args.source == "auto" and tables.get("salesforce_ft.opportunity")
        ):
            print("Using Salesforce as data source...")
            stats = import_opportunities_from_salesforce(bq_client, conn, args.limit, args.dry_run)
        elif args.source == "gong" or (
            args.source == "auto" and tables.get("gongio_ft.opportunity")
        ):
            print("Using Gong as data source...")
            stats = import_opportunities_from_gong(bq_client, conn, args.limit, args.dry_run)
        else:
            print("ERROR: No valid opportunity data source found!")
            return

        if not args.dry_run:
            total_processed = stats["opportunities_imported"] + stats["opportunities_updated"]
            update_sync_status(conn, total_processed)

    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"Opportunities found: {stats['opportunities_found']}")
    print(f"Opportunities imported (new): {stats['opportunities_imported']}")
    print(f"Opportunities updated: {stats['opportunities_updated']}")

    if stats["errors"]:
        print(f"\nErrors encountered: {len(stats['errors'])}")
        for err in stats["errors"][:10]:
            print(f"  - {err}")
    else:
        print("\n✓ No errors!")
    print("=" * 60)


if __name__ == "__main__":
    main()
