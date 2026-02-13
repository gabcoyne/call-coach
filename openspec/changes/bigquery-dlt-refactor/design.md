# BigQuery DLT Refactor - Technical Design

## Context

The Call Coach application currently maintains dual data ingestion paths: (1) custom BigQuery import scripts and (2) Gong API client with webhook ingestion. The Gong API client adds complexity without benefit, as MCP tools query Postgres directly rather than calling Gong APIs. All source data (calls, transcripts, emails, opportunities) flows through Fivetran into BigQuery, making it the natural single source of truth.

DLT (Data Load Tool) from dlthub.com is a production-grade Python library for ELT pipelines that provides incremental loading, state management, schema evolution, retry logic, and observability out of the box. It reduces custom data pipeline code from ~500 lines to ~100 lines while adding reliability features.

**Current State:**

- `scripts/import_from_bigquery.py`: 353 lines of custom sync logic
- `gong/client.py`: 312 lines for API integration (unused by MCP tools)
- `gong/webhook.py`: 187 lines for webhook validation and processing
- Startup validation: 8 seconds (includes Gong API health check)
- Rate limits: 3 req/sec, 10k req/day on Gong API

**Constraints:**

- Must maintain existing Postgres schema (migrations already deployed)
- Must support incremental sync (avoid full table scans)
- Must run on Prefect Cloud for orchestration
- Must preserve data lineage for audit purposes

**Stakeholders:**

- Backend team: Simplified data pipeline maintenance
- DevOps: Reduced environment variables and API keys
- End users: No impact (internal refactor)

## Goals / Non-Goals

**Goals:**

1. Replace Gong API client with DLT-powered BigQuery sync
2. Extend data coverage to include emails and opportunities
3. Achieve sub-3-second startup time by removing API validation
4. Implement production-grade retry logic and error handling
5. Enable hourly scheduled sync via Prefect
6. Maintain backward compatibility with existing database schema

**Non-Goals:**

- Real-time data sync (hourly batch is sufficient for coaching use case)
- Multi-tenant data isolation (single Prefect workspace)
- Schema migration automation (existing Alembic migrations remain)
- Historical data backfill beyond Fivetran retention (rely on existing BigQuery history)
- Data transformations (DLT loads raw; transformations happen in Postgres or via dbt if needed)

## Decisions

### Decision 1: DLT over Airbyte/Fivetran-to-Postgres

**Chosen:** DLT (Python library)

**Alternatives Considered:**

- **Airbyte**: Full platform with UI, but heavyweight (Docker containers, separate service). Adds operational overhead.
- **Fivetran Postgres Connector**: Would create BigQuery→Postgres direct sync, but costs ~$1-2k/month and doesn't support custom transformations.
- **Custom Script Enhancement**: Keep `import_from_bigquery.py`, but would require ~1000 LOC to match DLT features (state management, retries, schema evolution).

**Rationale:**

- DLT is lightweight (Python pip install, ~5MB)
- Integrates natively with Prefect (existing orchestration)
- Python-first (matches team skills)
- Open source with active community
- Cost: Free (only BigQuery query costs)
- Flexible for custom transformations and mappings

### Decision 2: Incremental Loading Strategy

**Chosen:** Use `_fivetran_synced` column from Fivetran as incremental cursor

**Alternatives Considered:**

- **updated_at/modified_at columns**: Salesforce tables have LastModifiedDate, but not all Gong tables have reliable update timestamps
- **DLT built-in append mode**: Would require primary key deduplication logic
- **Full refresh every run**: Too expensive on BigQuery and Postgres

**Rationale:**

- Fivetran adds `_fivetran_synced` to all tables (UTC timestamp of Fivetran sync)
- Reliable cursor for "what's new since last run"
- DLT's `incremental()` function natively supports timestamp cursors
- Existing `sync_status` table can store last_sync_timestamp for each entity type

### Decision 3: State Persistence

**Chosen:** DLT filesystem state backend stored in project directory

**Alternatives Considered:**

- **DLT SQL state backend**: Store state in Postgres, but adds complexity
- **Prefect state**: Store checkpoints in Prefect API, but requires custom integration
- **Manual state management**: Use `sync_status` table, but duplicates DLT functionality

**Rationale:**

- DLT filesystem backend writes `.dlt/` directory with JSON state files
- Simple to deploy (no additional infrastructure)
- Version controlled (can track state changes in git for debugging)
- Prefect workspace has persistent disk for state retention
- Easy to reset state (delete `.dlt/` directory for full refresh)

### Decision 4: Pipeline Structure

**Chosen:** Separate DLT sources per entity type (calls, emails, opportunities) with parallel execution

**Alternatives Considered:**

- **Single monolithic pipeline**: Load all tables in one DLT pipeline, but slower and harder to debug
- **Per-table pipelines**: Separate Prefect deployments per table, but excessive orchestration overhead

**Rationale:**

- Parallel execution (DLT supports concurrent resources)
- Independent error handling (email sync failure doesn't block call sync)
- Easier to monitor (separate metrics per entity type)
- Aligns with `sync_status` table design (one row per entity_type)

### Decision 5: Schema Mapping

**Chosen:** DLT auto-detect with manual column hints for type preservation

**Alternatives Considered:**

- **Full schema declaration**: Explicitly declare all columns, but brittle to schema changes
- **Pure auto-detect**: Let DLT infer everything, but risks type mismatches

**Rationale:**

- DLT's schema inference works well for 90% of columns
- Manual hints for critical columns (e.g., `amount DECIMAL(15,2)`, `recipients TEXT[]`)
- Balances flexibility (auto-detect new columns) with safety (preserve key types)

### Decision 6: Deployment and Scheduling

**Chosen:** Prefect deployment with hourly cron schedule

**Alternatives Considered:**

- **Cron job on VM**: Simple, but no observability or retry logic
- **GitHub Actions**: Free compute, but limited to 6-hour max runtime
- **Kubernetes CronJob**: Requires K8s cluster setup

**Rationale:**

- Prefect already used for other flows (consistent tooling)
- Prefect UI provides run history, logs, and alerting
- Prefect Cloud handles scheduling, retries, and notifications
- Easy to trigger manual runs or adjust schedule

## Risks / Trade-offs

### Risk: BigQuery query costs

**Impact:** DLT runs incremental queries against BigQuery hourly. Costs depend on data scanned.

**Mitigation:**

- Use partitioned tables in BigQuery (Fivetran creates partition by `_fivetran_synced`)
- Incremental queries scan only new partitions (minimal cost)
- Estimated cost: ~$5-10/month for hourly sync of 100K rows/day
- Monitor BigQuery billing dashboard for unexpected spikes

### Risk: Fivetran sync lag

**Impact:** If Fivetran sync fails, DLT pipeline syncs stale data. Coaching data is 1-2 hours behind.

**Mitigation:**

- Monitor Fivetran sync status (webhook or API)
- Alert if Fivetran sync hasn't run in >4 hours
- DLT will catch up on next run when Fivetran recovers
- Coaching use case tolerates 1-2 hour lag (not real-time monitoring)

### Risk: DLT state corruption

**Impact:** If `.dlt/` state directory is lost or corrupted, pipeline may duplicate data or miss updates.

**Mitigation:**

- Version control `.dlt/` state directory in git (commit after successful runs)
- DLT's upsert mode uses `gong_call_id`/`gong_email_id` as merge keys (prevents duplicates)
- Manual recovery: delete `.dlt/` state and run full refresh (safe but slow)

### Risk: Schema evolution breaking changes

**Impact:** If BigQuery column is dropped or type changed incompatibly, DLT may fail.

**Mitigation:**

- DLT logs schema warnings before failing
- Test schema changes in staging environment first
- Prefect alerts on pipeline failure
- Rollback strategy: revert BigQuery schema change or add DLT column mapping

### Risk: Hourly sync insufficient for some workflows

**Impact:** Some users may expect near-real-time data updates (e.g., coaching within minutes of call ending).

**Mitigation:**

- Document 1-hour data freshness SLA
- For urgent needs, provide manual "Sync Now" button that triggers Prefect flow
- Consider 15-minute schedule if needed (minimal cost increase)

### Trade-off: Loss of real-time webhook ingestion

**Current:** Gong webhook calls ingestion endpoint within seconds of call ending
**New:** Hourly batch sync with 0-60 minute lag

**Justification:**

- Coaching is not time-sensitive (managers review calls async)
- Hourly sync simplifies architecture and reduces failure modes
- Webhook infrastructure (FastAPI server, signature validation) eliminated

### Trade-off: DLT dependency introduces new failure mode

**Current:** Custom script failures are predictable and debuggable
**New:** DLT library issues (bugs, breaking changes) add external dependency risk

**Justification:**

- DLT is actively maintained with 3.5k GitHub stars, 50+ contributors
- Pin DLT version in requirements.txt (e.g., `dlt[postgres,bigquery]==0.4.x`)
- DLT has extensive test coverage and production usage at scale
- Custom script has no tests, retry logic, or schema evolution support

## Migration Plan

### Phase 1: DLT Implementation (Week 1)

1. **Install DLT and dependencies**

   ```bash
   uv pip install "dlt[postgres,bigquery]==0.4.*"
   ```

2. **Create DLT pipeline structure**

   ```
   dlt_pipeline/
   ├── __init__.py
   ├── bigquery_to_postgres.py   # Main pipeline
   ├── sources/
   │   ├── calls.py               # Calls + transcripts + speakers
   │   ├── emails.py              # Emails with sender/recipients
   │   └── opportunities.py       # Opportunities + call linkage
   ├── config.toml                # DLT config (credentials, destinations)
   └── .dlt/                      # State directory (git-tracked)
   ```

3. **Implement calls source (reuse existing logic)**

   - Query `gongio_ft.call`, `gongio_ft.transcript`, `gongio_ft.call_speaker`
   - Map to `calls`, `transcripts`, `speakers` tables
   - Use incremental loading with `_fivetran_synced` cursor

4. **Test in development environment**
   - Run pipeline manually: `python dlt_pipeline/bigquery_to_postgres.py`
   - Verify data in Postgres matches BigQuery
   - Check state file created in `.dlt/`

### Phase 2: Email and Opportunity Sync (Week 1-2)

1. **Implement email source**

   - Query `gongio_ft.email` joined with `email_sender`, `email_recipient`
   - Aggregate recipients into Postgres array
   - Map to `emails` table

2. **Implement opportunity source**

   - Query `salesforce.opportunity` joined with `account`, `user`
   - Create `call_opportunities` junction records
   - Map to `opportunities` table

3. **Test incremental loading**
   - Run pipeline, verify checkpoint in `.dlt/`
   - Manually insert new records in BigQuery
   - Run pipeline again, verify only new records synced

### Phase 3: Prefect Deployment (Week 2)

1. **Create Prefect flow wrapper**

   ```python
   from prefect import flow
   from dlt_pipeline.bigquery_to_postgres import run_pipeline

   @flow(name="bigquery-dlt-sync")
   def dlt_sync_flow():
       run_pipeline()

   if __name__ == "__main__":
       dlt_sync_flow.serve(cron="0 * * * *")  # Hourly
   ```

2. **Deploy to Prefect Cloud**

   ```bash
   prefect deployment build --name bigquery-sync --cron "0 * * * *"
   prefect deployment apply
   ```

3. **Test scheduled run**
   - Wait for hourly trigger or manually trigger run
   - Monitor Prefect UI for logs and status
   - Verify data synced to Postgres

### Phase 4: Gong API Removal (Week 2)

1. **Delete Gong client code**

   - Remove `gong/client.py`, `gong/webhook.py`, `webhook_server.py`
   - Remove `flows/daily_gong_sync.py`

2. **Update configuration**

   - Remove from `coaching_mcp/shared/config.py`: `gong_api_key`, `gong_api_secret`, `gong_webhook_secret`, `gong_api_base_url`
   - Remove from `.env.example`

3. **Update server validation**

   - Remove Gong API health check from `coaching_mcp/server.py`
   - Keep database and Anthropic API validation

4. **Update documentation**
   - Remove Gong API setup from README
   - Add DLT pipeline section to deployment docs

### Phase 5: Production Deployment (Week 3)

1. **Deploy to staging environment**

   - Run pipeline, verify data correctness
   - Test with frontend (verify API endpoints still work)
   - Load test: verify pipeline handles 100K rows

2. **Monitor first 48 hours**

   - Check Prefect runs every hour
   - Verify data freshness (query recent records)
   - Monitor BigQuery costs and Postgres disk usage

3. **Deploy to production**

   - Run pipeline once manually to backfill
   - Enable scheduled runs
   - Remove Gong API environment variables from production secrets

4. **Rollback strategy if needed**
   - Restore Gong API environment variables
   - Redeploy previous git commit with Gong client
   - DLT pipeline can run in parallel without conflicts (different tables)

### Success Criteria

- [ ] DLT pipeline syncs calls, transcripts, speakers with 100% data fidelity
- [ ] Email and opportunity data appears in Postgres within 1 hour of BigQuery update
- [ ] Startup time reduced from 8s to <3s (no Gong API validation)
- [ ] Zero Gong API requests (verified via API logs)
- [ ] Prefect pipeline runs successfully for 7 consecutive days
- [ ] BigQuery query costs under $10/month
- [ ] No user-facing impact (frontend works identically)

## Open Questions

1. **Should we implement dbt transformations post-load?**

   - DLT loads raw data; dbt could handle denormalization, aggregations
   - Decision: Defer until coaching_sessions queries show performance issues

2. **How to handle BigQuery schema changes that break DLT?**

   - Schema evolution works for additive changes, but not breaking changes
   - Decision: Monitor Fivetran schema change notifications, test in staging first

3. **Should state be backed up separately?**

   - `.dlt/` state directory tracked in git, but could use external backup
   - Decision: Git tracking sufficient; manual recovery (full refresh) acceptable

4. **What's the alerting threshold for sync failures?**

   - How many consecutive failures before paging someone?
   - Decision: Alert on 3 consecutive failures (3 hours of no data updates)

5. **Should we add data quality checks?**
   - E.g., row count comparisons, null percentage checks
   - Decision: Add basic checks (row count deltas) in Prefect flow post-load
