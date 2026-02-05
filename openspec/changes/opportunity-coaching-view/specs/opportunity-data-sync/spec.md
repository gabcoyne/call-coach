## ADDED Requirements

### Requirement: Daily sync job fetches opportunities from Gong API
The system SHALL run a daily job that fetches all opportunities modified since the last sync from the Gong API and stores them in Neon PostgreSQL.

#### Scenario: First sync fetches all opportunities
- **WHEN** daily sync runs for the first time
- **THEN** system fetches all active opportunities from Gong API
- **THEN** system stores opportunities in database with gong_opportunity_id, name, account, owner, stage, close_date, amount, health_score

#### Scenario: Incremental sync fetches only modified opportunities
- **WHEN** daily sync runs after initial sync
- **THEN** system queries Gong API with modifiedAfter parameter set to last sync timestamp
- **THEN** system only processes opportunities that changed since last sync
- **THEN** system updates existing records or inserts new ones

#### Scenario: Sync updates last sync timestamp
- **WHEN** daily sync completes successfully
- **THEN** system records current timestamp as last_sync_time for opportunities
- **THEN** next sync uses this timestamp for incremental fetch

### Requirement: Daily sync job fetches calls associated with opportunities
The system SHALL fetch all calls linked to synced opportunities and create many-to-many relationships in the database.

#### Scenario: Sync fetches calls for each opportunity
- **WHEN** processing an opportunity during sync
- **THEN** system fetches all calls associated with that opportunity from Gong API
- **THEN** system creates call_opportunities junction records linking calls to opportunities

#### Scenario: Call already exists in database
- **WHEN** sync encounters a call that already exists in calls table
- **THEN** system only creates junction record if missing
- **THEN** system does not duplicate call data

#### Scenario: New call discovered through opportunity sync
- **WHEN** sync finds a call not yet in database
- **THEN** system fetches full call details including transcript
- **THEN** system stores call, speakers, and transcript in database
- **THEN** system creates junction record linking to opportunity

### Requirement: Daily sync job fetches emails associated with opportunities
The system SHALL fetch email interactions for synced opportunities and store email metadata and body snippets in the database.

#### Scenario: Sync fetches emails for each opportunity
- **WHEN** processing an opportunity during sync
- **THEN** system fetches all emails associated with that opportunity from Gong API
- **THEN** system stores email metadata with gong_email_id, subject, sender, recipients, sent_at

#### Scenario: Email body is truncated for storage efficiency
- **WHEN** storing an email from Gong API
- **THEN** system extracts first 500 characters of body as snippet
- **THEN** system stores full email metadata in JSONB field
- **THEN** email body snippet is sufficient for timeline preview

#### Scenario: Sync handles missing or incomplete email data
- **WHEN** Gong API returns email with missing fields
- **THEN** system stores available fields and marks optional fields as NULL
- **THEN** sync continues without failing

### Requirement: Sync job logs progress and errors for observability
The system SHALL log detailed sync progress including counts of processed items and any errors encountered.

#### Scenario: Successful sync logs summary statistics
- **WHEN** daily sync completes successfully
- **THEN** system logs count of opportunities synced
- **THEN** system logs count of calls synced
- **THEN** system logs count of emails synced
- **THEN** system logs total execution time

#### Scenario: Sync failure logs error details
- **WHEN** sync encounters Gong API error
- **THEN** system logs error message with opportunity ID context
- **THEN** system continues processing remaining opportunities
- **THEN** system reports partial success with error count

#### Scenario: Sync respects rate limits
- **WHEN** sync approaches Gong API rate limit
- **THEN** system implements exponential backoff
- **THEN** system logs rate limit warnings
- **THEN** sync completes without exceeding limits

### Requirement: Sync job is idempotent and safe to retry
The system SHALL ensure that running the sync job multiple times produces the same result without duplicating data.

#### Scenario: Re-running sync does not duplicate data
- **WHEN** sync job runs twice with same time range
- **THEN** system uses UPSERT logic based on gong_opportunity_id
- **THEN** no duplicate opportunity records are created
- **THEN** junction records are created only if not already present

#### Scenario: Sync can safely recover from partial failure
- **WHEN** sync fails midway through processing
- **THEN** next sync run processes all modified opportunities since last successful timestamp
- **THEN** system reconciles any inconsistencies
- **THEN** data eventually becomes consistent

### Requirement: Sync job runs locally via Prefect and in production via Vercel cron
The system SHALL support execution in both local development (Prefect flow) and production (Vercel serverless function) environments.

#### Scenario: Local execution via uv run
- **WHEN** developer runs sync locally with `uv run python -m flows.daily_gong_sync`
- **THEN** sync executes using environment variables from .env file
- **THEN** sync connects to Neon database
- **THEN** sync completes and logs results

#### Scenario: Production execution via Vercel cron
- **WHEN** Vercel cron triggers /api/cron/daily-sync endpoint
- **THEN** serverless function invokes same sync logic
- **THEN** sync uses Vercel environment variables
- **THEN** sync completes within Vercel execution time limits

#### Scenario: Sync job is scheduled for daily execution
- **WHEN** deployed to production
- **THEN** Vercel cron runs sync at 6am daily
- **THEN** sync completes before business hours
- **THEN** managers see previous day's data on morning login
