# BigQuery DLT Refactor Proposal

## Why

The application currently maintains dual data sources (Gong API and BigQuery) creating unnecessary complexity, API costs, and rate limiting constraints. All source data (calls, transcripts, emails, opportunities) already flows through Fivetran into BigQuery. The Gong API client code is largely unused by MCP tools, which query Postgres directly. By adopting DLT (Data Load Tool) for BigQuery→Postgres replication, we eliminate API dependencies while gaining production-grade data pipeline capabilities.

## What Changes

- **Remove Gong API Integration**: Delete `gong/client.py`, `gong/webhook.py`, `webhook_server.py` (~500 lines)
- **Add DLT Pipeline**: Implement DLT pipeline for BigQuery→Postgres sync with incremental loading
- **Remove Environment Variables**: Remove `GONG_API_KEY`, `GONG_API_SECRET`, `GONG_WEBHOOK_SECRET`, `GONG_API_BASE_URL`
- **Expand Data Coverage**: Sync emails and opportunities in addition to existing calls/transcripts
- **Add Scheduled Orchestration**: Deploy Prefect flow for hourly pipeline runs
- **Update Startup Validation**: Remove Gong API connectivity checks from MCP server startup

## Capabilities

### New Capabilities

- `dlt-pipeline`: DLT-based data pipeline for BigQuery→Postgres replication with incremental loading, state management, retry logic, and schema evolution handling
- `email-sync`: Email data replication from BigQuery `gongio_ft.email` tables to Postgres `emails` table with sender/recipient mapping
- `opportunity-sync`: Opportunity and account data replication from BigQuery Salesforce tables to Postgres `opportunities` table

### Modified Capabilities

- None (existing coaching analysis specs remain unchanged; this refactor only affects data ingestion layer)

## Impact

**Code Changes:**

- Delete: `gong/client.py`, `gong/webhook.py`, `webhook_server.py`, `flows/daily_gong_sync.py`
- Add: `dlt_pipeline/bigquery_to_postgres.py`, `dlt_pipeline/sources/`, `dlt_pipeline/destinations/`
- Modify: `coaching_mcp/shared/config.py` (remove Gong config), `coaching_mcp/server.py` (remove API validation)
- Replace: `scripts/import_from_bigquery.py` functionality absorbed by DLT

**Database:**

- No schema changes (DLT maps to existing tables: calls, transcripts, speakers, emails, opportunities)
- Incremental sync uses existing `sync_status` table for state tracking

**Dependencies:**

- Add: `dlt[postgres,bigquery]` (~5MB package)
- Remove: Custom Gong API client dependencies
- Keep: `psycopg2`, `anthropic`, existing database libraries

**Deployment:**

- Remove: 4 environment variables (Gong API credentials)
- Add: DLT state directory for checkpoint persistence
- Update: Prefect deployments to include DLT pipeline schedule

**Operations:**

- Startup time: ~6 seconds faster (no Gong API validation)
- No API rate limits (3 req/sec removed)
- No API costs (replaced with minimal BigQuery query costs)
- Monitoring: DLT built-in observability replaces custom webhook logging

**Breaking Changes:**

- **BREAKING**: Gong webhook endpoint removed (replaced by scheduled batch sync)
- **BREAKING**: Real-time call ingestion replaced with hourly batch updates (acceptable for coaching use case)
