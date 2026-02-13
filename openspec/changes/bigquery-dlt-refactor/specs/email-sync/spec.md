# Email Sync Specification

## ADDED Requirements

### Requirement: Email metadata replication

The system SHALL replicate email metadata from BigQuery to Postgres emails table.

#### Scenario: Email record synced from gongio_ft.email

- **WHEN** the sync processes an email from `gongio_ft.email`
- **THEN** it SHALL create a record in the `emails` table with id, gong_email_id, subject, sent_at, and metadata fields

#### Scenario: Email linked to opportunity

- **WHEN** an email has an associated opportunity in BigQuery metadata
- **THEN** the sync SHALL populate the `opportunity_id` foreign key linking to the `opportunities` table

#### Scenario: Email without opportunity

- **WHEN** an email has no associated opportunity
- **THEN** the sync SHALL create the email record with `opportunity_id` set to NULL

### Requirement: Sender information mapping

The system SHALL map email sender information from BigQuery to Postgres.

#### Scenario: Sender email extracted

- **WHEN** processing an email with sender information from `gongio_ft.email_sender`
- **THEN** the sync SHALL populate the `sender_email` field with the sender's email address

#### Scenario: Sender information missing

- **WHEN** sender information is not available in BigQuery
- **THEN** the sync SHALL set `sender_email` to NULL and log a warning

### Requirement: Recipient list aggregation

The system SHALL aggregate multiple recipients into a Postgres array field.

#### Scenario: Multiple recipients aggregated

- **WHEN** an email has multiple recipients in `gongio_ft.email_recipient`
- **THEN** the sync SHALL create a single email record with all recipient email addresses in the `recipients` array field

#### Scenario: Single recipient

- **WHEN** an email has one recipient
- **THEN** the sync SHALL create the `recipients` array with a single element

#### Scenario: No recipients recorded

- **WHEN** recipient information is missing in BigQuery
- **THEN** the sync SHALL set `recipients` to an empty array

### Requirement: Body snippet extraction

The system SHALL extract email body snippets for timeline preview.

#### Scenario: Body truncated to 500 characters

- **WHEN** email body exceeds 500 characters
- **THEN** the sync SHALL store only the first 500 characters in `body_snippet` field

#### Scenario: Short body preserved

- **WHEN** email body is less than 500 characters
- **THEN** the sync SHALL store the complete body in `body_snippet` field

#### Scenario: Body metadata preserved

- **WHEN** processing an email
- **THEN** the sync SHALL store full email body and headers in the `metadata` JSONB field

### Requirement: Incremental email sync

The system SHALL sync only new or modified emails using timestamp-based incremental loading.

#### Scenario: First sync loads all historical emails

- **WHEN** the email sync runs for the first time
- **THEN** it SHALL load all email records from BigQuery

#### Scenario: Subsequent syncs load new emails only

- **WHEN** the email sync runs with existing state
- **THEN** it SHALL query only emails where `_fivetran_synced` is greater than `sync_status.last_sync_timestamp` for entity_type 'emails'

#### Scenario: Sync status updated after successful run

- **WHEN** the email sync completes successfully
- **THEN** it SHALL update `sync_status` table with the latest sync timestamp, items_synced count, and status 'success'

### Requirement: Email deduplication

The system SHALL prevent duplicate email records using Gong email ID.

#### Scenario: Duplicate email skipped

- **WHEN** an email with the same `gong_email_id` already exists in Postgres
- **THEN** the sync SHALL skip the insert and log a debug message

#### Scenario: Email updated on change

- **WHEN** an existing email has modified metadata in BigQuery
- **THEN** the sync SHALL update the existing Postgres record with new values

### Requirement: Error handling for malformed emails

The system SHALL handle malformed or incomplete email data gracefully.

#### Scenario: Email with missing required fields

- **WHEN** an email record lacks required fields like gong_email_id or sent_at
- **THEN** the sync SHALL skip the record, log an error, and increment error_count in sync_status

#### Scenario: Invalid email addresses

- **WHEN** sender or recipient email addresses are malformed
- **THEN** the sync SHALL store the raw value and add a validation warning to the metadata field

#### Scenario: Unparseable dates

- **WHEN** sent_at timestamp cannot be parsed
- **THEN** the sync SHALL set sent_at to NULL and log the parsing error

### Requirement: Timeline query optimization

The system SHALL index email data for efficient opportunity timeline queries.

#### Scenario: Index on opportunity_id and sent_at

- **WHEN** querying emails for an opportunity timeline
- **THEN** the query SHALL use the index `idx_emails_opportunity` on (opportunity_id, sent_at DESC)

#### Scenario: Index on sent_at for global timeline

- **WHEN** querying recent emails across all opportunities
- **THEN** the query SHALL use the index `idx_emails_sent_at` on (sent_at DESC)
