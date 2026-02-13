"""
DLT Source: Calls

Syncs calls, transcripts, and speakers from BigQuery gongio_ft tables to Postgres.
Uses incremental loading based on _fivetran_synced timestamp.
"""

import dlt
from google.cloud import bigquery


@dlt.source(name="gong_calls")
def gong_calls_source(
    project_id: str = "prefect-data-warehouse",
    dataset: str = "gongio_ft",
):
    """
    DLT source for Gong call data from BigQuery.

    Yields three resources:
    - calls: Call metadata
    - transcripts: Call transcripts with speaker attribution
    - speakers: Call participants with talk time
    """

    return [
        calls_resource(project_id, dataset),
        transcripts_resource(project_id, dataset),
        speakers_resource(project_id, dataset),
    ]


@dlt.resource(
    name="calls",
    write_disposition="merge",
    primary_key="gong_call_id",
    merge_key="gong_call_id",
)
def calls_resource(project_id: str, dataset: str):
    """
    Extract calls from BigQuery gongio_ft.call table.

    Incremental loading based on _fivetran_synced timestamp.
    Maps BigQuery schema to Postgres calls table.
    """
    # Get BigQuery client (uses ADC or GOOGLE_APPLICATION_CREDENTIALS)
    client = bigquery.Client(project=project_id)

    # Incremental cursor on _fivetran_synced
    # DLT tracks last synced value automatically
    last_synced = dlt.sources.incremental(
        "_fivetran_synced",
        initial_value="1970-01-01T00:00:00Z",
    )

    query = f"""
    SELECT
        c.id as gong_call_id,
        c.title,
        c.scheduled as scheduled_at,
        c.duration as duration_seconds,
        c.purpose as call_type,
        NULL as product,
        DATE(c.scheduled) as date,
        c.scheduled as processed_at,
        STRUCT(
            c.url as gong_url,
            CAST(c.started AS STRING) as started
        ) as metadata,
        c._fivetran_synced
    FROM `{project_id}.{dataset}.call` c
    WHERE c._fivetran_deleted = FALSE
        AND c._fivetran_synced > @last_synced
    ORDER BY c._fivetran_synced ASC
    """

    # Configure query with parameter
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("last_synced", "TIMESTAMP", last_synced.last_value)
        ]
    )

    # Execute query and yield rows
    query_job = client.query(query, job_config=job_config)
    for row in query_job:
        yield dict(row)


@dlt.resource(
    name="transcripts",
    write_disposition="merge",
    primary_key="id",
)
def transcripts_resource(project_id: str, dataset: str):
    """
    Extract transcripts from BigQuery gongio_ft.transcript table.

    Incremental loading based on _fivetran_synced timestamp.
    Maps BigQuery schema to Postgres transcripts table.
    """
    client = bigquery.Client(project=project_id)

    last_synced = dlt.sources.incremental(
        "_fivetran_synced",
        initial_value="1970-01-01T00:00:00Z",
    )

    query = f"""
    SELECT
        GENERATE_UUID() as id,
        t.call_id,
        t.speaker_id,
        t.index as sequence_number,
        NULL as start_time_ms,
        t.sentence as text,
        NULL as sentiment,
        ARRAY<STRING>[] as topics,
        NULL as chunk_metadata,
        t._fivetran_synced
    FROM `{project_id}.{dataset}.transcript` t
    WHERE t._fivetran_deleted = FALSE
        AND t._fivetran_synced > @last_synced
    ORDER BY t._fivetran_synced ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("last_synced", "TIMESTAMP", last_synced.last_value)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    for row in query_job:
        yield dict(row)


@dlt.resource(
    name="speakers",
    write_disposition="merge",
    primary_key="id",
)
def speakers_resource(project_id: str, dataset: str):
    """
    Extract speakers from BigQuery gongio_ft.call_speaker table.

    Joins with users table to get email and name.
    Incremental loading based on _fivetran_synced timestamp.
    """
    client = bigquery.Client(project=project_id)

    last_synced = dlt.sources.incremental(
        "_fivetran_synced",
        initial_value="1970-01-01T00:00:00Z",
    )

    query = f"""
    SELECT
        GENERATE_UUID() as id,
        cs.call_id,
        u.email_address as email,
        CASE
            WHEN u.email_address IS NOT NULL THEN
                CONCAT(
                    UPPER(SUBSTR(SPLIT(SPLIT(u.email_address, '@')[OFFSET(0)], '.')[OFFSET(0)], 1, 1)),
                    SUBSTR(SPLIT(SPLIT(u.email_address, '@')[OFFSET(0)], '.')[OFFSET(0)], 2)
                )
            ELSE
                CONCAT('Speaker ', CAST(cs.user_id AS STRING))
        END as name,
        u.title as role,
        CASE
            WHEN u.email_address LIKE '%@prefect.io' THEN TRUE
            ELSE FALSE
        END as company_side,
        CAST(cs.talk_time AS INT64) as talk_time_seconds,
        NULL as talk_time_percentage,
        cs._fivetran_synced
    FROM `{project_id}.{dataset}.call_speaker` cs
    LEFT JOIN `{project_id}.{dataset}.users` u ON CAST(cs.user_id AS STRING) = u.id
    WHERE cs._fivetran_deleted = FALSE
        AND cs._fivetran_synced > @last_synced
    ORDER BY cs._fivetran_synced ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("last_synced", "TIMESTAMP", last_synced.last_value)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    for row in query_job:
        yield dict(row)
