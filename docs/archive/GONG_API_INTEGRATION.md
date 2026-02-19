# Gong API Integration (Archived)

> **Note**: This documentation is archived. The Call Coach application no longer uses direct Gong API integration. Data is now sourced from BigQuery via the DLT pipeline. This document is preserved for historical reference.

## Overview

Prior to February 2026, Call Coach used direct integration with the Gong API for fetching call recordings, transcripts, and metadata. This integration was replaced with a BigQuery-to-Postgres DLT pipeline that sources data from Fivetran-synced Gong data in BigQuery.

## Migration Date

February 2026

## Reason for Migration

1. **Performance**: BigQuery batch processing is more efficient than individual API calls
2. **Cost**: Reduces Gong API rate limit consumption
3. **Reliability**: Fivetran handles Gong API sync with retry logic
4. **Data Freshness**: Hourly DLT sync provides acceptable 1-hour data lag

## Previous Architecture

```
Gong API → webhook_server.py → gong/client.py → Database
```

## Current Architecture

```
Gong → Fivetran → BigQuery → DLT Pipeline → Postgres
```

## Removed Components

The following files were removed as part of this migration:

- `gong/client.py` - Gong API client
- `gong/webhook.py` - Gong webhook handlers
- `webhook_server.py` - Webhook HTTP server
- `flows/daily_gong_sync.py` - Daily Gong sync flow
- `tests/test_auth_methods.py` - Gong API auth tests

## Environment Variables (No Longer Used)

The following environment variables were used by the Gong API integration:

- `GONG_API_KEY` - Gong access key
- `GONG_API_SECRET` - Gong secret key (JWT)
- `GONG_API_BASE_URL` - Tenant-specific Gong API URL
- `GONG_WEBHOOK_SECRET` - Webhook signature verification

## Rollback Information

The Gong client code is preserved in git history. To rollback:

1. Checkout the commit before the DLT migration
2. Restore Gong environment variables
3. Redeploy the previous version

The code will be available in git history for at least 90 days from the migration date.

## Related Documentation

- [DLT Pipeline Documentation](../../README.md#dlt-pipeline)
- [BigQuery Data Architecture](../../README.md#architecture)
