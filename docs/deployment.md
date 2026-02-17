# Deployment Guide

This document covers deploying Call Coach to Google Cloud Platform.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GCP Project: prefect-sbx-sales-engineering       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │   Cloud Run      │    │   Cloud Run      │    │  Cloud Run     │ │
│  │   (Frontend)     │───▶│   (REST API)     │    │  Jobs (DLT)    │ │
│  │   Next.js        │    │   FastAPI        │    │  Hourly Sync   │ │
│  │   Port 3000      │    │   Port 8000      │    │                │ │
│  └──────────────────┘    └────────┬─────────┘    └───────┬────────┘ │
│                                   │                       │          │
│                                   ▼                       ▼          │
│                          ┌──────────────────┐    ┌──────────────────┐│
│                          │  Secret Manager  │    │   BigQuery       ││
│                          └──────────────────┘    └──────────────────┘│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   Neon Postgres          │
                    │   (External)             │
                    └──────────────────────────┘
```

## Prerequisites

1. **GCP Access**: Access to `prefect-sbx-sales-engineering` project
2. **Terraform**: Version 1.5.0 or higher
3. **gcloud CLI**: Authenticated with appropriate permissions
4. **GitHub**: Repository access with admin permissions

## Deployment Workflow

### Automated (CI/CD)

1. **Push to main branch** triggers deployment workflow
2. Tests run (backend + frontend)
3. Docker images built and pushed to Artifact Registry
4. Cloud Run services updated with new images
5. Health checks verify deployment success

### Manual Deployment

For emergency deployments or debugging:

```bash
# Authenticate
gcloud auth login
gcloud config set project prefect-sbx-sales-engineering

# Configure Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push API
docker build -f Dockerfile.api -t us-central1-docker.pkg.dev/prefect-sbx-sales-engineering/call-coach/api:manual .
docker push us-central1-docker.pkg.dev/prefect-sbx-sales-engineering/call-coach/api:manual

# Deploy to Cloud Run
gcloud run deploy call-coach-api \
  --image=us-central1-docker.pkg.dev/prefect-sbx-sales-engineering/call-coach/api:manual \
  --region=us-central1

# Verify
gcloud run services describe call-coach-api --region=us-central1 --format='value(status.url)'
```

## Environment Configuration

### Required Secrets (Secret Manager)

| Secret                              | Description                     | How to Obtain     |
| ----------------------------------- | ------------------------------- | ----------------- |
| `DATABASE_URL`                      | Neon Postgres connection string | Neon Console      |
| `ANTHROPIC_API_KEY`                 | Claude API key                  | Anthropic Console |
| `BIGQUERY_CREDENTIALS`              | Service account JSON            | GCP Console → IAM |
| `CLERK_SECRET_KEY`                  | Authentication secret           | Clerk Dashboard   |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Auth public key                 | Clerk Dashboard   |

### Updating Secrets

```bash
# Add new version to existing secret
echo -n "new_value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Or via Console
# https://console.cloud.google.com/security/secret-manager?project=prefect-sbx-sales-engineering
```

## Service URLs

| Service  | URL                                          |
| -------- | -------------------------------------------- |
| API      | `https://call-coach-api-<hash>.run.app`      |
| Frontend | `https://call-coach-frontend-<hash>.run.app` |

Get actual URLs:

```bash
gcloud run services list --region=us-central1
```

## Monitoring

### View Logs

```bash
# API logs
gcloud run services logs read call-coach-api --region=us-central1 --limit=100

# Frontend logs
gcloud run services logs read call-coach-frontend --region=us-central1 --limit=100

# DLT job logs
gcloud run jobs executions list call-coach-dlt-sync --region=us-central1
gcloud run jobs logs read call-coach-dlt-sync --region=us-central1
```

### Check Service Status

```bash
# Service status
gcloud run services describe call-coach-api --region=us-central1

# Health check
curl $(gcloud run services describe call-coach-api --region=us-central1 --format='value(status.url)')/health
```

### Alerts

Alerts are configured via Terraform in `infra/monitoring.tf`:

- API error rate > 5%
- API latency p95 > 2s
- DLT sync job failure
- Frontend error rate > 5%

## Rollback Procedures

### Rollback to Previous Revision

```bash
# List revisions
gcloud run revisions list --service=call-coach-api --region=us-central1

# Route all traffic to previous revision
gcloud run services update-traffic call-coach-api \
  --region=us-central1 \
  --to-revisions=call-coach-api-00002-abc=100
```

### Rollback via Git

```bash
# Find the last working commit
git log --oneline

# Revert to previous commit
git revert HEAD
git push origin main
# CI/CD will deploy the reverted code
```

## DLT Sync Job

### Manual Trigger

```bash
gcloud run jobs execute call-coach-dlt-sync --region=us-central1
```

### Check Execution Status

```bash
gcloud run jobs executions list call-coach-dlt-sync --region=us-central1
```

### Pause Scheduled Runs

```bash
gcloud scheduler jobs pause dlt-sync-hourly-trigger --location=us-central1
```

### Resume Scheduled Runs

```bash
gcloud scheduler jobs resume dlt-sync-hourly-trigger --location=us-central1
```

## Troubleshooting

### Service Won't Start

1. Check logs for startup errors:

   ```bash
   gcloud run services logs read call-coach-api --region=us-central1 --limit=50
   ```

2. Verify secrets exist and have values:

   ```bash
   gcloud secrets versions list DATABASE_URL
   gcloud secrets versions list ANTHROPIC_API_KEY
   ```

3. Check service account permissions:

   ```bash
   gcloud projects get-iam-policy prefect-sbx-sales-engineering \
     --filter="bindings.members:call-coach-runtime" \
     --format="table(bindings.role)"
   ```

### DLT Sync Failing

1. Check job execution logs:

   ```bash
   gcloud run jobs logs read call-coach-dlt-sync --region=us-central1
   ```

2. Verify BigQuery credentials:

   ```bash
   gcloud secrets versions list BIGQUERY_CREDENTIALS
   ```

3. Check BigQuery access:

   ```bash
   bq query --use_legacy_sql=false "SELECT 1"
   ```

### Database Connection Issues

1. Verify DATABASE_URL is correct:

   ```bash
   gcloud secrets versions access latest --secret=DATABASE_URL
   ```

2. Test connection from Cloud Shell:

   ```bash
   psql "$(gcloud secrets versions access latest --secret=DATABASE_URL)" -c "SELECT 1"
   ```

### Preview Environment Issues

1. Check preview revision exists:

   ```bash
   gcloud run revisions list --service=call-coach-api --region=us-central1
   ```

2. Get preview URL:

   ```bash
   gcloud run services describe call-coach-api --region=us-central1 \
     --format='value(status.traffic[].url)'
   ```

## Scaling

### Increase API Capacity

Edit `infra/variables.tf` or use Terraform:

```hcl
variable "api_max_instances" {
  default = 20  # Increase from 10
}
```

### Manual Scaling

```bash
gcloud run services update call-coach-api \
  --region=us-central1 \
  --max-instances=20 \
  --min-instances=2
```

## Cost Management

### View Current Costs

<https://console.cloud.google.com/billing/>

### Reduce Costs

1. Scale to zero when not in use:

   ```bash
   gcloud run services update call-coach-api --min-instances=0 --region=us-central1
   ```

2. Pause DLT sync during off-hours:

   ```bash
   gcloud scheduler jobs pause dlt-sync-hourly-trigger --location=us-central1
   ```
