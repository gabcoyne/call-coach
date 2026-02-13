# Opportunity Sync Specification

## ADDED Requirements

### Requirement: Opportunity data replication

The system SHALL replicate opportunity data from BigQuery Salesforce tables to Postgres opportunities table.

#### Scenario: Opportunity synced from Salesforce

- **WHEN** the sync processes an opportunity from `salesforce.opportunity` in BigQuery
- **THEN** it SHALL create or update a record in the `opportunities` table with all core fields

#### Scenario: Opportunity fields mapped correctly

- **WHEN** creating an opportunity record
- **THEN** it SHALL map Salesforce fields to Postgres columns: Id→gong_opportunity_id, Name→name, StageName→stage, CloseDate→close_date, Amount→amount

#### Scenario: Fallback to Gong opportunity table

- **WHEN** Salesforce connector is not available in BigQuery
- **THEN** the sync SHALL query `gongio_ft.opportunity` as fallback data source

### Requirement: Account name resolution

The system SHALL resolve account names by joining with Salesforce account table.

#### Scenario: Account name joined from Salesforce

- **WHEN** processing an opportunity with AccountId
- **THEN** the sync SHALL join with `salesforce.account` table and populate `account_name` from Account.Name

#### Scenario: Account not found

- **WHEN** AccountId does not match any account record
- **THEN** the sync SHALL set `account_name` to NULL and log a warning

#### Scenario: Account name stored in metadata

- **WHEN** account information is synced
- **THEN** the sync SHALL also store full account details in the `metadata` JSONB field

### Requirement: Owner email mapping

The system SHALL map opportunity owner to email address for filtering and assignment.

#### Scenario: Owner email resolved from Salesforce user

- **WHEN** processing an opportunity with OwnerId
- **THEN** the sync SHALL resolve the email address from Salesforce user table and populate `owner_email`

#### Scenario: Owner not found

- **WHEN** OwnerId does not resolve to a user
- **THEN** the sync SHALL set `owner_email` to NULL and log a warning

### Requirement: Health score synchronization

The system SHALL sync Gong's native health score when available.

#### Scenario: Health score synced from Gong

- **WHEN** Gong provides a health_score field in BigQuery
- **THEN** the sync SHALL populate the `health_score` field with the value (0-100 scale)

#### Scenario: Health score not available

- **WHEN** Gong health_score is not available in BigQuery
- **THEN** the sync SHALL set `health_score` to NULL

#### Scenario: Health score normalized to 0-10 scale

- **WHEN** displaying health score in UI
- **THEN** the application SHALL normalize the 0-100 score to 0-10 scale (divide by 10)

### Requirement: Call-opportunity linkage

The system SHALL create many-to-many relationships between calls and opportunities.

#### Scenario: Call linked to opportunity

- **WHEN** Gong metadata indicates a call is associated with an opportunity
- **THEN** the sync SHALL create a record in `call_opportunities` junction table

#### Scenario: Multiple calls per opportunity

- **WHEN** an opportunity has multiple associated calls
- **THEN** the sync SHALL create multiple `call_opportunities` records linking each call to the opportunity

#### Scenario: Call without opportunity

- **WHEN** a call has no opportunity association
- **THEN** the sync SHALL not create any `call_opportunities` records for that call

#### Scenario: Duplicate linkage prevention

- **WHEN** a call-opportunity linkage already exists
- **THEN** the sync SHALL skip creating a duplicate junction record (enforced by PRIMARY KEY constraint)

### Requirement: Incremental opportunity sync

The system SHALL sync only new or modified opportunities using timestamp-based incremental loading.

#### Scenario: First sync loads all opportunities

- **WHEN** the opportunity sync runs for the first time
- **THEN** it SHALL load all opportunity records from BigQuery

#### Scenario: Subsequent syncs load modified opportunities

- **WHEN** the opportunity sync runs with existing state
- **THEN** it SHALL query only opportunities where `LastModifiedDate` is greater than `sync_status.last_sync_timestamp` for entity_type 'opportunities'

#### Scenario: Sync status updated after completion

- **WHEN** the opportunity sync completes successfully
- **THEN** it SHALL update `sync_status` table with latest timestamp, items_synced count, and status 'success'

### Requirement: Opportunity deduplication and updates

The system SHALL handle both new opportunities and updates to existing opportunities.

#### Scenario: New opportunity inserted

- **WHEN** an opportunity with a new gong_opportunity_id is synced
- **THEN** the sync SHALL insert a new record in the `opportunities` table

#### Scenario: Existing opportunity updated

- **WHEN** an opportunity with an existing gong_opportunity_id is synced
- **THEN** the sync SHALL update the existing record with new values and set `updated_at` to current timestamp

#### Scenario: Unchanged opportunity skipped

- **WHEN** an opportunity has not changed since last sync
- **THEN** the sync SHALL skip processing it to optimize performance

### Requirement: Stage and close date tracking

The system SHALL track opportunity stage changes and close date for pipeline analysis.

#### Scenario: Stage field populated

- **WHEN** syncing an opportunity
- **THEN** the sync SHALL populate the `stage` field with values like 'Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'

#### Scenario: Close date populated

- **WHEN** syncing an opportunity with CloseDate
- **THEN** the sync SHALL populate the `close_date` field as a DATE type

#### Scenario: Historical stage changes tracked in metadata

- **WHEN** Salesforce provides stage history
- **THEN** the sync SHALL store stage change history in the `metadata` JSONB field

### Requirement: Error handling for incomplete opportunities

The system SHALL handle incomplete or malformed opportunity data gracefully.

#### Scenario: Opportunity with missing required fields

- **WHEN** an opportunity lacks gong_opportunity_id or name
- **THEN** the sync SHALL skip the record, log an error, and increment error_count in sync_status

#### Scenario: Invalid amount values

- **WHEN** amount field is not a valid decimal
- **THEN** the sync SHALL set amount to NULL and log a warning

#### Scenario: Invalid date values

- **WHEN** close_date cannot be parsed
- **THEN** the sync SHALL set close_date to NULL and log a warning

### Requirement: Query performance optimization

The system SHALL index opportunity data for efficient filtering and sorting.

#### Scenario: Index on owner and updated_at

- **WHEN** filtering opportunities by owner
- **THEN** the query SHALL use index `idx_opportunities_owner` on (owner_email, updated_at DESC)

#### Scenario: Index on stage and close_date

- **WHEN** filtering opportunities by stage and sorting by close date
- **THEN** the query SHALL use index `idx_opportunities_stage` on (stage, close_date)

#### Scenario: Index on health_score

- **WHEN** filtering opportunities by health score range
- **THEN** the query SHALL use index `idx_opportunities_health` on (health_score) WHERE health_score IS NOT NULL
