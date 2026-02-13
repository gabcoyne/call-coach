# DLT Pipeline Specification

## ADDED Requirements

### Requirement: Pipeline initialization and configuration

The system SHALL initialize a DLT pipeline with BigQuery source and Postgres destination using environment-based configuration.

#### Scenario: Pipeline initializes with valid credentials

- **WHEN** the pipeline starts with valid BigQuery and Postgres credentials
- **THEN** the pipeline establishes connections to both systems without error

#### Scenario: Pipeline fails with invalid credentials

- **WHEN** the pipeline starts with invalid or missing credentials
- **THEN** the pipeline raises a clear error message indicating which credential is invalid

#### Scenario: Pipeline uses environment configuration

- **WHEN** the pipeline reads configuration from environment variables
- **THEN** it SHALL use `DATABASE_URL` for Postgres and GCP credentials for BigQuery

### Requirement: Incremental data loading

The system SHALL perform incremental loading using state management to sync only new or modified records.

#### Scenario: First run loads all data

- **WHEN** the pipeline runs for the first time with no prior state
- **THEN** it SHALL load all historical records from BigQuery

#### Scenario: Subsequent runs load only new records

- **WHEN** the pipeline runs with existing state
- **THEN** it SHALL load only records where `_fivetran_synced` is greater than the last checkpoint timestamp

#### Scenario: Pipeline persists state after successful run

- **WHEN** the pipeline completes a successful sync
- **THEN** it SHALL persist the latest checkpoint timestamp for the next run

#### Scenario: Pipeline resumes from last checkpoint on failure

- **WHEN** the pipeline fails mid-sync
- **THEN** it SHALL resume from the last successful checkpoint on the next run

### Requirement: Schema evolution handling

The system SHALL automatically detect and handle schema changes in BigQuery source tables.

#### Scenario: New columns added to source table

- **WHEN** BigQuery source table has new columns
- **THEN** the pipeline SHALL add those columns to the destination table automatically

#### Scenario: Column type changes in source table

- **WHEN** a column type changes in BigQuery
- **THEN** the pipeline SHALL migrate the destination column type or raise a warning if incompatible

#### Scenario: Columns removed from source table

- **WHEN** columns are removed from BigQuery source
- **THEN** the pipeline SHALL preserve destination columns but stop populating them

### Requirement: Error handling and retry logic

The system SHALL implement retry logic with exponential backoff for transient failures.

#### Scenario: Temporary network failure

- **WHEN** a network error occurs during sync
- **THEN** the pipeline SHALL retry up to 3 times with exponential backoff

#### Scenario: Permanent error after retries

- **WHEN** a sync fails after all retry attempts
- **THEN** the pipeline SHALL log the error details and exit with non-zero status

#### Scenario: Partial batch failure

- **WHEN** a subset of records fail validation
- **THEN** the pipeline SHALL write failed records to a dead letter queue and continue processing

### Requirement: Data source coverage

The system SHALL replicate calls, transcripts, speakers, emails, and opportunities from BigQuery to Postgres.

#### Scenario: Calls sync from gongio_ft.call

- **WHEN** the pipeline runs the calls sync
- **THEN** it SHALL query `prefect-data-warehouse.gongio_ft.call` and insert into `calls` table

#### Scenario: Transcripts sync from gongio_ft.transcript

- **WHEN** the pipeline runs the transcripts sync
- **THEN** it SHALL query `prefect-data-warehouse.gongio_ft.transcript` and insert into `transcripts` table

#### Scenario: Speakers sync from gongio_ft.call_speaker

- **WHEN** the pipeline runs the speakers sync
- **THEN** it SHALL query `prefect-data-warehouse.gongio_ft.call_speaker` joined with `users` and insert into `speakers` table

#### Scenario: Emails sync handled by email-sync capability

- **WHEN** the pipeline runs the email sync
- **THEN** it SHALL delegate to the email-sync capability specification

#### Scenario: Opportunities sync handled by opportunity-sync capability

- **WHEN** the pipeline runs the opportunity sync
- **THEN** it SHALL delegate to the opportunity-sync capability specification

### Requirement: Monitoring and observability

The system SHALL provide logging, metrics, and alerting for pipeline health.

#### Scenario: Pipeline logs sync progress

- **WHEN** the pipeline is running
- **THEN** it SHALL log row counts, duration, and checkpoint timestamps

#### Scenario: Pipeline exposes metrics

- **WHEN** the pipeline completes a sync
- **THEN** it SHALL expose metrics including rows_synced, errors_count, and duration_seconds

#### Scenario: Pipeline alerts on failures

- **WHEN** the pipeline fails after all retries
- **THEN** it SHALL send an alert via configured notification channel (Slack or PagerDuty)

### Requirement: Scheduled execution

The system SHALL run on a configurable schedule via Prefect orchestration.

#### Scenario: Default hourly schedule

- **WHEN** deployed without schedule override
- **THEN** the pipeline SHALL run every hour on the hour

#### Scenario: Manual trigger support

- **WHEN** an operator triggers the pipeline manually
- **THEN** the pipeline SHALL run immediately regardless of schedule

#### Scenario: Concurrent run prevention

- **WHEN** a pipeline run is already in progress
- **THEN** subsequent scheduled runs SHALL skip until the current run completes

### Requirement: Performance optimization

The system SHALL optimize for throughput using batching and parallel processing.

#### Scenario: Batch inserts to Postgres

- **WHEN** syncing large datasets
- **THEN** the pipeline SHALL use batch inserts with configurable batch size (default 1000 rows)

#### Scenario: Parallel table syncs

- **WHEN** syncing multiple tables
- **THEN** the pipeline SHALL process independent tables in parallel

#### Scenario: Connection pooling

- **WHEN** the pipeline connects to Postgres
- **THEN** it SHALL use connection pooling to reuse connections across batches
