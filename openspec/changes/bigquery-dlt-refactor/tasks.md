# Implementation Tasks: BigQuery DLT Refactor

## 1. DLT Setup and Infrastructure

- [x] 1.1 Install DLT with BigQuery and Postgres extras (`uv pip install "dlt[postgres,bigquery]==0.4.*"`)
- [x] 1.2 Create `dlt_pipeline/` directory structure with `__init__.py`, `bigquery_to_postgres.py`, `sources/` subdirectory
- [x] 1.3 Create DLT config file (`dlt_pipeline/config.toml`) with BigQuery and Postgres credentials
- [x] 1.4 Initialize DLT state directory (`.dlt/`) and add to git tracking
- [x] 1.5 Add `.dlt/state.json` to .gitignore if state should not be committed (or keep it for audit trail)

## 2. Calls Source Implementation

- [x] 2.1 Create `dlt_pipeline/sources/calls.py` with DLT resource decorators
- [x] 2.2 Implement BigQuery query for `gongio_ft.call` with incremental loading using `_fivetran_synced` cursor
- [x] 2.3 Implement BigQuery query for `gongio_ft.transcript` with foreign key mapping to calls
- [x] 2.4 Implement BigQuery query for `gongio_ft.call_speaker` joined with `users` table for speaker metadata
- [x] 2.5 Add schema hints for critical columns (timestamp_seconds→INT, sentiment→VARCHAR, topics→VARCHAR[])
- [x] 2.6 Map BigQuery results to Postgres schema (gong_call_id, title, scheduled_at, duration_seconds, etc.)
- [x] 2.7 Add deduplication logic using `gong_call_id` as merge key
- [x] 2.8 Test calls source locally with small dataset (limit 100 rows)

## 3. Email Source Implementation

- [x] 3.1 Create `dlt_pipeline/sources/emails.py` with DLT resource decorators
- [x] 3.2 Implement BigQuery query joining `gongio_ft.email`, `email_sender`, and `email_recipient` tables
- [x] 3.3 Add recipient aggregation logic to create Postgres array field from multiple recipient rows
- [x] 3.4 Implement body snippet extraction (truncate to 500 characters for `body_snippet` field)
- [x] 3.5 Add opportunity linkage logic using Gong metadata to populate `opportunity_id` foreign key
- [x] 3.6 Map email metadata to JSONB field (full body, headers, thread info)
- [x] 3.7 Add incremental loading using `_fivetran_synced` cursor and `sync_status` table
- [x] 3.8 Add deduplication logic using `gong_email_id` as merge key
- [x] 3.9 Test email source locally with small dataset (limit 50 emails)

## 4. Opportunity Source Implementation

- [x] 4.1 Create `dlt_pipeline/sources/opportunities.py` with DLT resource decorators
- [x] 4.2 Implement BigQuery query for Salesforce opportunity table (`salesforce.opportunity` or fallback to `gongio_ft.opportunity`)
- [x] 4.3 Add account join to resolve `account_name` from `salesforce.account` table
- [x] 4.4 Add owner email resolution from Salesforce user table
- [x] 4.5 Map Salesforce fields to Postgres schema (Id→gong_opportunity_id, Name→name, StageName→stage, CloseDate→close_date, Amount→amount)
- [x] 4.6 Add health_score sync from Gong if available, handle NULL if not present
- [x] 4.7 Implement call-opportunity linkage by creating `call_opportunities` junction records
- [x] 4.8 Add incremental loading using `LastModifiedDate` cursor and `sync_status` table
- [x] 4.9 Add upsert logic for existing opportunities (update on duplicate `gong_opportunity_id`)
- [x] 4.10 Test opportunity source locally with small dataset (limit 20 opportunities)

## 5. Main Pipeline Assembly

- [x] 5.1 Create `dlt_pipeline/bigquery_to_postgres.py` main entry point
- [x] 5.2 Initialize DLT pipeline with `pipeline_name="gong_to_postgres"`, `destination="postgres"`, `dataset_name="public"`
- [x] 5.3 Register calls, emails, and opportunities sources as DLT resources
- [x] 5.4 Configure parallel execution for independent sources
- [x] 5.5 Add error handling with try/except blocks around each source
- [x] 5.6 Implement dead letter queue for failed records (log to `sync_status.error_details`)
- [x] 5.7 Add logging for sync progress (row counts, duration, checkpoint timestamps)
- [x] 5.8 Update `sync_status` table after each successful source sync
- [x] 5.9 Test full pipeline run locally (all sources in sequence)
- [x] 5.10 Verify state persistence in `.dlt/state.json` after run

## 6. Error Handling and Retry Logic

- [x] 6.1 Configure DLT retry settings (max_retries=3, exponential backoff)
- [x] 6.2 Add custom exception handling for BigQuery quota errors
- [x] 6.3 Add custom exception handling for Postgres connection errors
- [x] 6.4 Implement partial failure handling (continue processing other sources if one fails)
- [x] 6.5 Add alerting for permanent failures (send to Slack or PagerDuty)
- [x] 6.6 Test retry logic by simulating network failure

## 7. Monitoring and Observability

- [x] 7.1 Add structured logging using Python logging library (log level INFO for progress, ERROR for failures)
- [x] 7.2 Expose metrics: rows_synced, errors_count, duration_seconds per source
- [x] 7.3 Add sync status summary log at end of run (total rows synced, total errors, elapsed time)
- [x] 7.4 Integrate with DLT's built-in observability (enable DLT logging)
- [x] 7.5 Add data quality checks (row count delta comparison between BigQuery and Postgres)
- [x] 7.6 Test monitoring by running pipeline and inspecting logs

## 8. Prefect Deployment

- [ ] 8.1 Create Prefect flow wrapper in `flows/dlt_sync_flow.py`
- [ ] 8.2 Add `@flow` decorator with name "bigquery-dlt-sync"
- [ ] 8.3 Import and call `run_pipeline()` from `dlt_pipeline/bigquery_to_postgres.py`
- [ ] 8.4 Add Prefect task for each DLT source (calls, emails, opportunities) for granular observability
- [ ] 8.5 Configure flow retries (max_retries=2, retry_delay_seconds=300)
- [ ] 8.6 Build Prefect deployment with cron schedule "0 \* \* \* \*" (hourly)
- [ ] 8.7 Deploy to Prefect Cloud using `prefect deployment apply`
- [ ] 8.8 Test manual trigger from Prefect UI
- [ ] 8.9 Wait for scheduled run and verify success in Prefect UI

## 9. Gong API Removal

- [ ] 9.1 Delete `gong/client.py`
- [ ] 9.2 Delete `gong/webhook.py`
- [ ] 9.3 Delete `webhook_server.py`
- [ ] 9.4 Delete `flows/daily_gong_sync.py`
- [ ] 9.5 Remove Gong imports from `coaching_mcp/server.py`
- [ ] 9.6 Remove Gong API validation from `coaching_mcp/server.py` startup checks
- [ ] 9.7 Remove Gong config fields from `coaching_mcp/shared/config.py` (gong_api_key, gong_api_secret, gong_webhook_secret, gong_api_base_url)
- [ ] 9.8 Remove Gong environment variables from `.env.example`
- [ ] 9.9 Test MCP server startup (should be faster, no Gong validation)
- [ ] 9.10 Run `ruff check` and fix any unused import errors

## 10. Documentation Updates

- [ ] 10.1 Update README.md to remove Gong API setup instructions
- [ ] 10.2 Add DLT pipeline section to README.md (installation, running locally, Prefect deployment)
- [ ] 10.3 Update deployment docs (remove Gong API keys, add DLT state directory persistence)
- [ ] 10.4 Document data freshness SLA (1-hour lag for hourly sync)
- [ ] 10.5 Add troubleshooting guide for DLT state corruption and recovery
- [ ] 10.6 Update CLAUDE.md with new data pipeline architecture

## 11. Testing and Validation

- [ ] 11.1 Run full pipeline in development environment with production-like data volume (100K rows)
- [ ] 11.2 Verify data fidelity (compare row counts and sample records between BigQuery and Postgres)
- [ ] 11.3 Test incremental loading (run pipeline twice, verify only new records synced on second run)
- [ ] 11.4 Test schema evolution (add a column in BigQuery, verify DLT handles it)
- [ ] 11.5 Test error recovery (simulate BigQuery failure, verify retry logic)
- [ ] 11.6 Test state corruption recovery (delete `.dlt/state.json`, verify full refresh)
- [ ] 11.7 Run MCP tools (`analyze_call`, `get_rep_insights`) to verify coaching functionality unchanged
- [ ] 11.8 Test frontend (verify API endpoints work, data displays correctly)
- [ ] 11.9 Load test: run pipeline with 500K rows, measure duration and resource usage
- [ ] 11.10 Test Prefect concurrent run prevention (trigger manual run while scheduled run is active)

## 12. Staging Deployment

- [ ] 12.1 Deploy DLT pipeline to staging environment
- [ ] 12.2 Run pipeline manually in staging, verify data synced correctly
- [ ] 12.3 Enable scheduled runs in staging (hourly)
- [ ] 12.4 Monitor first 24 hours in staging (check Prefect logs, Postgres data freshness, BigQuery costs)
- [ ] 12.5 Test frontend in staging environment
- [ ] 12.6 Verify startup time improvement (measure MCP server startup latency)

## 13. Production Deployment

- [ ] 13.1 Deploy DLT pipeline to production
- [ ] 13.2 Run pipeline manually in production to backfill historical data
- [ ] 13.3 Verify backfill completed successfully (check row counts in Postgres)
- [ ] 13.4 Enable scheduled runs in production (hourly)
- [ ] 13.5 Remove Gong API environment variables from production secrets manager
- [ ] 13.6 Monitor first 48 hours (Prefect runs, data freshness, error rates)
- [ ] 13.7 Verify zero Gong API requests (check API logs)
- [ ] 13.8 Monitor BigQuery costs (should be <$10/month)
- [ ] 13.9 Verify user-facing functionality unchanged (run smoke tests on production)

## 14. Rollback Plan (if needed)

- [ ] 14.1 Document rollback procedure (restore Gong environment variables, redeploy previous git commit)
- [ ] 14.2 Keep Gong client code in git history for 90 days before archiving
- [ ] 14.3 Preserve DLT pipeline in separate branch for reference
- [ ] 14.4 Test rollback procedure in staging before production deployment

## 15. Cleanup and Optimization

- [ ] 15.1 Remove unused Gong-related tests from test suite
- [ ] 15.2 Update CI/CD pipeline to remove Gong API mock setup
- [ ] 15.3 Archive Gong API documentation to `docs/archive/`
- [ ] 15.4 Review and optimize DLT batch size (benchmark 500 vs 1000 vs 5000 row batches)
- [ ] 15.5 Add indexes to Postgres if query performance degrades (monitor slow query log)
- [ ] 15.6 Consider implementing dbt transformations if post-load transformations needed (defer unless needed)
