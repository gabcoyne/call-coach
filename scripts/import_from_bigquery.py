#!/usr/bin/env python3
"""
Import historical call data from BigQuery into local database.

Usage:
    uv run python scripts/import_from_bigquery.py [--limit N] [--since YYYY-MM-DD]
"""

import argparse
from typing import Any

import psycopg2
from google.cloud import bigquery
from psycopg2.extras import execute_batch

from coaching_mcp.shared import settings


def get_bigquery_client() -> bigquery.Client:
    """Initialize BigQuery client using gcloud credentials."""
    import subprocess

    try:
        # Try to use gcloud auth to get access token
        result = subprocess.run(
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


def import_calls(
    bq_client: bigquery.Client, conn, since_date: str, limit: int | None = None
) -> dict[str, Any]:
    """
    Import calls from BigQuery.

    Returns dict with statistics about imported data.
    """
    stats = {
        "calls_imported": 0,
        "speakers_imported": 0,
        "transcripts_imported": 0,
        "errors": [],
    }

    # Query to get calls with participants
    query = f"""
    SELECT
        c.id,
        c.title,
        c.scheduled,
        c.duration,
        c.purpose,
        c.url,
        c.started
    FROM `prefect-data-warehouse.gongio_ft.call` c
    WHERE c.scheduled >= '{since_date}'
        AND c._fivetran_deleted = FALSE
    ORDER BY c.scheduled DESC
    {f'LIMIT {limit}' if limit else ''}
    """

    print(f"Fetching calls from BigQuery (since {since_date})...")
    calls_df = bq_client.query(query).to_dataframe()
    print(f"Found {len(calls_df)} calls to import")

    with conn.cursor() as cursor:
        # Import calls
        call_values = []
        for _, row in calls_df.iterrows():
            # Check if call already exists
            cursor.execute("SELECT 1 FROM calls WHERE gong_call_id = %s", (row["id"],))
            if cursor.fetchone():
                print(f"  Skip (exists): {row['id']} - {row['title']}")
                continue

            call_values.append(
                (
                    row["id"],  # gong_call_id
                    row["title"],
                    row["scheduled"],
                    row["duration"],
                    row["purpose"],  # call_type placeholder
                    None,  # product (will need manual classification)
                    row["scheduled"].date() if row["scheduled"] else None,  # date
                    row["scheduled"],  # processed_at (mark as ingested)
                    psycopg2.extras.Json(
                        {
                            "gong_url": row["url"],
                            "started": str(row["started"]) if row["started"] else None,
                        }
                    ),
                )
            )

        if call_values:
            print(f"Inserting {len(call_values)} new calls...")
            execute_batch(
                cursor,
                """
                INSERT INTO calls (
                    gong_call_id, title, scheduled_at, duration_seconds,
                    call_type, product, date, processed_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (gong_call_id) DO NOTHING
                """,
                call_values,
                page_size=100,
            )
            stats["calls_imported"] = len(call_values)
            conn.commit()
            print(f"✓ Imported {len(call_values)} calls")
        else:
            print("✓ No new calls to import")

        # Import speakers for imported calls
        print("\nFetching speakers from BigQuery...")
        speaker_query = f"""
        SELECT DISTINCT
            cs.call_id,
            cs.user_id,
            cs.talk_time,
            u.email_address,
            u.title
        FROM `prefect-data-warehouse.gongio_ft.call` c
        JOIN `prefect-data-warehouse.gongio_ft.call_speaker` cs ON c.id = cs.call_id
        LEFT JOIN `prefect-data-warehouse.gongio_ft.users` u ON CAST(cs.user_id AS STRING) = u.id
        WHERE c.scheduled >= '{since_date}'
            AND c._fivetran_deleted = FALSE
            AND cs._fivetran_deleted = FALSE
        {f'LIMIT {limit * 50 if limit else ""}'}
        """

        speakers_df = bq_client.query(speaker_query).to_dataframe()
        print(f"Found {len(speakers_df)} speaker records")

        speaker_values = []
        for _, row in speakers_df.iterrows():
            # Get call internal ID
            cursor.execute("SELECT id FROM calls WHERE gong_call_id = %s", (row["call_id"],))
            call_result = cursor.fetchone()
            if not call_result:
                continue
            call_internal_id = call_result[0]

            # Extract name from email if available
            email = row["email_address"]
            if email:
                # Extract name from email (e.g., "george@prefect.io" -> "George")
                name_part = email.split("@")[0]
                # Handle names like "brian.r" or "george.coyne"
                name_parts = name_part.replace(".", " ").split()
                full_name = " ".join(part.capitalize() for part in name_parts)
            else:
                full_name = f"Speaker {row['user_id']}"

            # Check if speaker already exists for this call
            cursor.execute(
                "SELECT 1 FROM speakers WHERE call_id = %s AND email = %s",
                (call_internal_id, email),
            )
            if cursor.fetchone():
                continue

            # Determine if company side (Prefect employee)
            is_company = email and "@prefect.io" in email

            # Convert talk_time to seconds (it's in seconds already as float)
            talk_time_seconds = int(row["talk_time"]) if row["talk_time"] else None

            speaker_values.append(
                (
                    call_internal_id,
                    full_name,
                    email,
                    row["title"],  # Use job title as role placeholder
                    is_company,
                    talk_time_seconds,
                    None,  # talk_time_percentage (will calculate later if needed)
                )
            )

        if speaker_values:
            print(f"Inserting {len(speaker_values)} speakers...")
            execute_batch(
                cursor,
                """
                INSERT INTO speakers (
                    call_id, name, email, role, company_side,
                    talk_time_seconds, talk_time_percentage
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                speaker_values,
                page_size=100,
            )
            stats["speakers_imported"] = len(speaker_values)
            conn.commit()
            print(f"✓ Imported {len(speaker_values)} speakers")
        else:
            print("✓ No new speakers to import")

        # Update prefect_reps array for all calls
        print("\nUpdating prefect_reps arrays...")
        cursor.execute(
            """
            UPDATE calls c
            SET prefect_reps = (
                SELECT array_agg(DISTINCT s.name)
                FROM speakers s
                WHERE s.call_id = c.id AND s.company_side = true
            )
            WHERE prefect_reps = '{}'
        """
        )
        updated_count = cursor.rowcount
        conn.commit()
        print(f"✓ Updated prefect_reps for {updated_count} calls")

        # Import transcripts (sample - first sentence per speaker per call)
        print("\nFetching transcript samples from BigQuery...")
        transcript_query = f"""
        SELECT
            t.call_id,
            t.speaker_id,
            t.sentence,
            t.index
        FROM `prefect-data-warehouse.gongio_ft.transcript` t
        WHERE t.call_id IN (
            SELECT id
            FROM `prefect-data-warehouse.gongio_ft.call`
            WHERE scheduled >= '{since_date}'
                AND _fivetran_deleted = FALSE
        )
        AND t._fivetran_deleted = FALSE
        ORDER BY t.call_id, t.index
        {f'LIMIT {limit * 50 if limit else "5000"}'}
        """

        transcripts_df = bq_client.query(transcript_query).to_dataframe()
        print(f"Found {len(transcripts_df)} transcript segments")

        transcript_values = []
        for _, row in transcripts_df.iterrows():
            # Get call internal ID
            cursor.execute("SELECT id FROM calls WHERE gong_call_id = %s", (row["call_id"],))
            call_result = cursor.fetchone()
            if not call_result:
                continue
            call_internal_id = call_result[0]

            # Get speaker internal ID
            cursor.execute(
                """
                SELECT id FROM speakers
                WHERE call_id = %s
                LIMIT 1
                """,
                (call_internal_id,),
            )
            speaker_result = cursor.fetchone()
            if not speaker_result:
                continue
            speaker_internal_id = speaker_result[0]

            transcript_values.append(
                (
                    call_internal_id,
                    speaker_internal_id,
                    row["index"],
                    None,  # start_time_ms (not available in this data)
                    row["sentence"],
                )
            )

        if transcript_values:
            print(f"Inserting {len(transcript_values)} transcript segments...")
            execute_batch(
                cursor,
                """
                INSERT INTO transcripts (
                    call_id, speaker_id, sequence_number,
                    start_time_ms, text
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                transcript_values,
                page_size=100,
            )
            stats["transcripts_imported"] = len(transcript_values)
            conn.commit()
            print(f"✓ Imported {len(transcript_values)} transcript segments")
        else:
            print("✓ No transcript segments to import")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Import call data from BigQuery")
    parser.add_argument(
        "--since", default="2026-01-01", help="Import calls since this date (YYYY-MM-DD)"
    )
    parser.add_argument("--limit", type=int, help="Limit number of calls to import (for testing)")
    args = parser.parse_args()

    print("=" * 60)
    print("BigQuery to PostgreSQL Import")
    print("=" * 60)
    print(f"Date range: {args.since} onwards")
    if args.limit:
        print(f"Limit: {args.limit} calls")
    print()

    bq_client = get_bigquery_client()

    with get_db_connection() as conn:
        stats = import_calls(bq_client, conn, args.since, args.limit)

    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"Calls imported: {stats['calls_imported']}")
    print(f"Speakers imported: {stats['speakers_imported']}")
    print(f"Transcript segments imported: {stats['transcripts_imported']}")

    if stats["errors"]:
        print(f"\nErrors encountered: {len(stats['errors'])}")
        for err in stats["errors"][:10]:
            print(f"  - {err}")
    else:
        print("\n✓ No errors!")
    print("=" * 60)


if __name__ == "__main__":
    main()
