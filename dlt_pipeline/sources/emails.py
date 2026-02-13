"""
DLT Source: Emails

Syncs emails from BigQuery gongio_ft tables to Postgres.
Includes sender/recipient aggregation and opportunity linkage.
Uses incremental loading based on _fivetran_synced timestamp.
"""

import dlt
from google.cloud import bigquery


@dlt.source(name="gong_emails")
def gong_emails_source(
    project_id: str = "prefect-data-warehouse",
    dataset: str = "gongio_ft",
):
    """
    DLT source for Gong email data from BigQuery.

    Yields one resource:
    - emails: Email metadata with sender, recipients array, and opportunity linkage
    """
    return emails_resource(project_id, dataset)


@dlt.resource(
    name="emails",
    write_disposition="merge",
    primary_key="gong_email_id",
    merge_key="gong_email_id",
)
def emails_resource(project_id: str, dataset: str):
    """
    Extract emails from BigQuery gongio_ft.email table.

    Joins with email_sender and email_recipient tables.
    Aggregates multiple recipients into Postgres array.
    Extracts body snippet (first 500 characters).
    Incremental loading based on _fivetran_synced timestamp.
    """
    client = bigquery.Client(project=project_id)

    # Incremental cursor on _fivetran_synced
    last_synced = dlt.sources.incremental(
        "_fivetran_synced",
        initial_value="1970-01-01T00:00:00Z",
    )

    query = f"""
    WITH email_data AS (
        SELECT
            e.id as gong_email_id,
            e.subject,
            e.sent_at,
            e.body,
            e.opportunity_id,
            e._fivetran_synced
        FROM `{project_id}.{dataset}.email` e
        WHERE e._fivetran_deleted = FALSE
            AND e._fivetran_synced > @last_synced
    ),
    email_senders AS (
        SELECT
            es.email_id,
            es.email_address as sender_email
        FROM `{project_id}.{dataset}.email_sender` es
        WHERE es._fivetran_deleted = FALSE
    ),
    email_recipients AS (
        SELECT
            er.email_id,
            ARRAY_AGG(er.email_address ORDER BY er.email_address) as recipients
        FROM `{project_id}.{dataset}.email_recipient` er
        WHERE er._fivetran_deleted = FALSE
        GROUP BY er.email_id
    )
    SELECT
        ed.gong_email_id,
        ed.subject,
        es.sender_email,
        COALESCE(er.recipients, ARRAY<STRING>[]) as recipients,
        ed.sent_at,
        CASE
            WHEN LENGTH(ed.body) > 500 THEN SUBSTR(ed.body, 1, 500)
            ELSE ed.body
        END as body_snippet,
        STRUCT(
            ed.body as full_body,
            ed.opportunity_id as opportunity_id
        ) as metadata,
        ed.opportunity_id,
        ed._fivetran_synced
    FROM email_data ed
    LEFT JOIN email_senders es ON ed.gong_email_id = es.email_id
    LEFT JOIN email_recipients er ON ed.gong_email_id = er.email_id
    ORDER BY ed._fivetran_synced ASC
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
