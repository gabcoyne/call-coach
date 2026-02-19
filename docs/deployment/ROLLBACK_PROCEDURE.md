# Rollback Procedure: BigQuery DLT Migration

This document describes how to rollback from the BigQuery DLT pipeline to the previous Gong API direct integration, if needed.

## When to Rollback

Consider rollback if:

- DLT pipeline fails persistently with no quick fix
- BigQuery data source becomes unavailable
- Data quality issues cannot be resolved
- Critical production issues require immediate rollback

## Pre-Rollback Checklist

- [ ] Confirm rollback is necessary (not a transient issue)
- [ ] Notify stakeholders of pending rollback
- [ ] Verify Gong API credentials are still valid
- [ ] Ensure previous commit is identified and tested in staging

## Rollback Steps

### 1. Identify the Previous Commit

The last commit with Gong API integration:

```bash
# Find the commit before DLT migration
git log --oneline --all | grep -i "gong" | head -5

# Or find commits before a specific date
git log --oneline --before="2026-02-01" -10
```

### 2. Restore Gong Environment Variables

Add the following environment variables to your deployment:

```env
GONG_API_KEY=<your_gong_access_key>
GONG_API_SECRET=<your_gong_jwt_secret>
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
GONG_WEBHOOK_SECRET=<your_webhook_secret>
```

**Where to restore:**

- **Local Development**: Add to `.env` file
- **Staging/Production**: Add via Vercel/Horizon environment variables UI
- **Secrets Manager**: Restore from backup or regenerate in Gong dashboard

### 3. Checkout Previous Code

```bash
# Create rollback branch from previous commit
git checkout -b rollback/gong-api <previous-commit-hash>

# Or cherry-pick specific files if only partial rollback needed
git checkout <previous-commit-hash> -- gong/ webhook_server.py flows/daily_gong_sync.py
```

### 4. Verify Dependencies

```bash
# Ensure Gong dependencies are installed
uv pip install httpx pydantic
```

### 5. Test Rollback Locally

```bash
# Start the webhook server
uv run python webhook_server.py

# Test Gong API connectivity
curl http://localhost:8001/health
```

### 6. Deploy Rollback

```bash
# Push rollback branch
git push origin rollback/gong-api

# Deploy via CI/CD or manual deployment
```

### 7. Verify Rollback

- [ ] Webhook server starts without errors
- [ ] Gong API authentication succeeds
- [ ] Calls are synced from Gong
- [ ] MCP tools return correct data
- [ ] Frontend displays call data correctly

## Post-Rollback Tasks

1. **Monitor**: Watch for any issues in the first 24-48 hours
2. **Document**: Record why rollback was needed
3. **Root Cause**: Investigate and fix the DLT pipeline issue
4. **Plan Forward**: Schedule re-migration when issue is resolved

## Code Preservation Policy

The Gong client code is preserved in git history for **90 days** from the migration date (February 2026). After this period, the code will be archived to a separate branch.

To access historical Gong code:

```bash
# List commits containing Gong code
git log --all --oneline -- gong/

# Checkout specific version
git checkout <commit-hash> -- gong/
```

## Rollback Contacts

- **Platform Team**: Contact for deployment issues
- **Data Team**: Contact for BigQuery/DLT issues
- **Gong Admin**: Contact for Gong API credential issues

## Related Documentation

- [Archived Gong API Integration](./archive/GONG_API_INTEGRATION.md)
- [DLT Pipeline Documentation](../README.md#dlt-pipeline)
- [Deployment Guide](./deployment.md)
