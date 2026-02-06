# Vercel Deployment Guide

Complete guide for deploying the Call Coach application to Vercel.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Database Setup](#database-setup)
4. [Vercel Project Setup](#vercel-project-setup)
5. [First Deployment](#first-deployment)
6. [Testing Production Deployment](#testing-production-deployment)
7. [Cron Job Configuration](#cron-job-configuration)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [CI/CD Integration](#cicd-integration)

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] Neon Postgres database (sign up at [neon.tech](https://neon.tech))
- [ ] Clerk account for authentication (sign up at [clerk.com](https://clerk.com))
- [ ] Gong API credentials (from Gong admin console)
- [ ] Anthropic API key (from [console.anthropic.com](https://console.anthropic.com))
- [ ] Vercel CLI installed: `npm i -g vercel`

---

## Environment Variables

All environment variables are configured in the Vercel dashboard.

### Required Variables

These MUST be set for the application to function:

#### 1. Clerk Authentication

```bash
# Get from: https://dashboard.clerk.com/apps/<your-app>/api-keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...

# Sign-in/sign-up URLs (standard)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

#### 2. Database

```bash
# Neon Postgres with connection pooling
# IMPORTANT: Use the pooler endpoint, not direct connection
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach?sslmode=require

# Connection pool settings (adjust based on Neon plan)
DATABASE_POOL_MIN_SIZE=2
DATABASE_POOL_MAX_SIZE=10
```

#### 3. Gong API

```bash
# Get from: Gong Settings > Integrations > API
GONG_API_KEY=your_access_key
GONG_API_SECRET=your_secret_key
GONG_WEBHOOK_SECRET=your_webhook_secret
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
```

#### 4. Anthropic Claude

```bash
# Get from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-api03-...
```

#### 5. Application URLs

```bash
# Production URL
NEXT_PUBLIC_APP_URL=https://coaching.prefect.io

# MCP Backend (leave blank for integrated serverless)
NEXT_PUBLIC_MCP_BACKEND_URL=
```

#### 6. Cron Authentication

```bash
# Generate with: openssl rand -base64 32
CRON_SECRET=<generated-secret>
```

### Optional Variables

These enhance functionality but are not required:

```bash
# Caching and analysis
ENABLE_CACHING=true
CACHE_TTL_DAYS=90
MAX_CHUNK_SIZE_TOKENS=80000
CHUNK_OVERLAP_PERCENTAGE=20

# Logging
LOG_LEVEL=INFO

# Rate limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# Feature flags
NEXT_PUBLIC_FEATURE_COACHING_FEED=true

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

---

## Database Setup

### 1. Create Neon Project

1. Go to [Neon Console](https://console.neon.tech)
2. Click "New Project"
3. Name: "call-coach-production"
4. Region: Choose closest to Vercel region (e.g., US East)
5. Postgres version: 15 or higher

### 2. Enable Connection Pooling

Connection pooling is CRITICAL for serverless:

1. In Neon dashboard, go to project settings
2. Enable "Connection Pooling"
3. Note the pooler endpoint (ends with `.us-east-2.aws.neon.tech`)
4. Use this endpoint in `DATABASE_URL`, NOT the direct connection

### 3. Run Database Migrations

From your local machine:

```bash
# Set DATABASE_URL to production database
export DATABASE_URL="postgresql://..."

# Run migrations (if you have a migration system)
# OR manually run schema creation scripts
psql $DATABASE_URL < db/schema.sql
```

### 4. Verify Schema

Ensure all tables exist:

```bash
psql $DATABASE_URL -c "\\dt"
```

Expected tables:
- `calls`
- `opportunities`
- `emails`
- `opportunity_calls`
- `call_analyses`
- `sync_status`
- `coaching_insights`

---

## Vercel Project Setup

### 1. Import Project

**Option A: Via Vercel Dashboard**

1. Go to [vercel.com/new](https://vercel.com/new)
2. Select your Git provider (GitHub recommended)
3. Import `call-coach` repository
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

**Option B: Via CLI**

```bash
cd /path/to/call-coach
vercel
# Follow prompts to link project
```

### 2. Configure Build Settings

In Vercel dashboard > Project Settings > General:

- **Build Command**: `cd frontend && npm run build`
- **Output Directory**: `frontend/.next`
- **Install Command**: `npm install`
- **Root Directory**: `.` (project root)

### 3. Add Environment Variables

In Vercel dashboard > Project Settings > Environment Variables:

1. Click "Add New"
2. For each variable in [Environment Variables](#environment-variables):
   - Enter variable name
   - Enter value
   - Select environments: Production, Preview, Development
   - Click "Save"

**Tip**: Use Vercel CLI to bulk import:

```bash
# Create .env.production file with all variables
vercel env pull .env.production

# Or add from file
vercel env add < .env.production
```

### 4. Configure Custom Domain

In Vercel dashboard > Project Settings > Domains:

1. Add domain: `coaching.prefect.io`
2. Update DNS records (Vercel provides instructions)
3. Wait for SSL certificate provisioning (automatic)

---

## First Deployment

### 1. Deploy via Git Push

Vercel automatically deploys on git push:

```bash
git add .
git commit -m "feat: configure Vercel deployment"
git push origin main
```

Vercel will:
1. Detect the push
2. Run build command
3. Deploy to production
4. Generate unique URL

### 2. Monitor Build

Watch build progress:

1. Go to Vercel dashboard > Deployments
2. Click latest deployment
3. View build logs

### 3. Verify Deployment

Once deployed:

1. Visit production URL
2. Test authentication (sign in/sign up)
3. Check database connectivity
4. Verify API routes work

**Health Check Endpoints**:

```bash
# Verify cron configuration
curl https://coaching.prefect.io/api/cron/daily-sync

# Test API routes (requires auth)
curl https://coaching.prefect.io/api/opportunities
```

---

## Testing Production Deployment

### 1. Authentication Flow

1. Go to `https://coaching.prefect.io`
2. Click "Sign In"
3. Complete Clerk authentication
4. Verify redirect to dashboard

### 2. Database Connectivity

Test database queries:

```bash
# Check opportunities endpoint
curl -H "Authorization: Bearer <clerk-token>" \
  https://coaching.prefect.io/api/opportunities
```

### 3. Cold Start Performance

Serverless functions experience "cold starts":

1. Wait 5 minutes for function to go cold
2. Make API request
3. Measure response time (should be < 3s)

### 4. Cron Job

Test cron endpoint manually:

```bash
# Generate CRON_SECRET
openssl rand -base64 32

# Test cron endpoint
curl -X POST \
  -H "Authorization: Bearer <CRON_SECRET>" \
  https://coaching.prefect.io/api/cron/daily-sync
```

Expected response:

```json
{
  "job": "daily-gong-sync",
  "startTime": "2025-02-05T10:00:00.000Z",
  "endTime": "2025-02-05T10:02:30.000Z",
  "status": "success",
  "output": "..."
}
```

---

## Cron Job Configuration

The daily Gong sync runs automatically via Vercel Cron.

### Schedule

Configured in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/daily-sync",
      "schedule": "0 6 * * *"
    }
  ]
}
```

Schedule: Daily at 6:00 AM UTC

### Monitoring Cron Execution

View cron logs:

1. Go to Vercel dashboard > Functions
2. Select `app/api/cron/daily-sync/route.ts`
3. View execution logs

### Manual Trigger

Trigger sync manually:

```bash
curl -X POST \
  -H "Authorization: Bearer $CRON_SECRET" \
  https://coaching.prefect.io/api/cron/daily-sync
```

### Adjusting Schedule

To change cron schedule:

1. Edit `vercel.json`:
   ```json
   {
     "crons": [
       {
         "path": "/api/cron/daily-sync",
         "schedule": "0 */4 * * *"  // Every 4 hours
       }
     ]
   }
   ```

2. Commit and push:
   ```bash
   git add vercel.json
   git commit -m "chore: update cron schedule"
   git push
   ```

Cron syntax: Standard cron format (minute hour day month weekday)

---

## Monitoring and Troubleshooting

### Vercel Dashboard

Monitor deployments:

1. **Deployments**: View build status, logs, errors
2. **Functions**: Serverless function logs and metrics
3. **Analytics**: Page views, API calls, performance
4. **Logs**: Real-time and historical logs

### Common Issues

#### 1. Build Failures

**Symptom**: Build fails with TypeScript errors

**Solution**:
```bash
# Test build locally
cd frontend
npm run build

# Fix TypeScript errors
npm run lint
```

#### 2. Database Connection Errors

**Symptom**: "Connection refused" or "Too many connections"

**Solution**:
- Verify `DATABASE_URL` uses pooler endpoint
- Reduce `DATABASE_POOL_MAX_SIZE` to match Neon plan limits
- Check Neon dashboard for connection count

#### 3. Cold Start Timeouts

**Symptom**: API requests timeout after function is idle

**Solution**:
- Increase function `maxDuration` in `vercel.json`
- Optimize database queries
- Consider Vercel Pro plan for faster cold starts

#### 4. Cron Job Failures

**Symptom**: Sync doesn't run or fails silently

**Solution**:
- Check function logs in Vercel dashboard
- Verify `CRON_SECRET` is set correctly
- Test endpoint manually with curl
- Check for Python dependency issues

### Log Analysis

View logs via CLI:

```bash
# Real-time logs
vercel logs --follow

# Filter by function
vercel logs --function=app/api/cron/daily-sync/route.ts

# Search logs
vercel logs --query="error"
```

### Performance Monitoring

Track key metrics:

1. **Function Duration**: Should be < 300s for cron
2. **Database Query Time**: Should be < 1s per query
3. **Memory Usage**: Should stay under limits
4. **Error Rate**: Should be < 1%

---

## CI/CD Integration

### Automatic Deployments

Vercel automatically deploys:

- **Production**: Pushes to `main` branch
- **Preview**: Pushes to feature branches
- **Development**: Local with `vercel dev`

### Branch Protection

Configure in GitHub:

1. Require pull requests for `main`
2. Require status checks (Vercel build)
3. Require review approvals

### Deployment Hooks

Configure in `vercel.json`:

```json
{
  "github": {
    "enabled": true,
    "autoAlias": true
  }
}
```

### Preview Deployments

Each PR gets a unique preview URL:

1. Open PR on GitHub
2. Vercel comments with preview URL
3. Test changes before merging
4. Merge to deploy to production

---

## Rollback Procedure

If production deployment has issues:

### Via Dashboard

1. Go to Vercel dashboard > Deployments
2. Find last working deployment
3. Click "..." menu > "Promote to Production"

### Via CLI

```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url>
```

---

## Security Checklist

Before going live:

- [ ] All environment variables use production values
- [ ] Clerk uses live keys (pk_live_*, sk_live_*)
- [ ] Database uses strong passwords
- [ ] CRON_SECRET is securely generated
- [ ] CSP headers configured (in vercel.json)
- [ ] HTTPS enforced (automatic with Vercel)
- [ ] API routes have authentication
- [ ] Rate limiting enabled
- [ ] Sensitive data not logged

---

## Support and Resources

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Next.js Docs**: [nextjs.org/docs](https://nextjs.org/docs)
- **Neon Docs**: [neon.tech/docs](https://neon.tech/docs)
- **Clerk Docs**: [clerk.com/docs](https://clerk.com/docs)

For issues, check:
1. Vercel build logs
2. Function runtime logs
3. Database connection status
4. Environment variable configuration

---

## Post-Deployment Tasks

After successful deployment:

1. [ ] Test all features end-to-end
2. [ ] Verify cron job runs successfully
3. [ ] Set up monitoring alerts (if using external service)
4. [ ] Document production URLs
5. [ ] Update README with deployment info
6. [ ] Share access with team members
7. [ ] Schedule first sync if needed

---

## Maintenance

Regular maintenance tasks:

- **Weekly**: Review function logs for errors
- **Monthly**: Check database size and connection usage
- **Quarterly**: Review and rotate API keys
- **As needed**: Update dependencies

---

## Cost Estimates

Vercel pricing (as of 2025):

**Hobby Plan** (Free):
- 100 GB bandwidth
- Serverless function execution
- Automatic HTTPS
- Suitable for: Development, small teams

**Pro Plan** ($20/month):
- 1 TB bandwidth
- Faster builds and cold starts
- Commercial use
- Suitable for: Production deployment

**Additional Costs**:
- Neon Postgres: Free tier includes 0.5 GB storage
- Clerk: Free tier includes 10,000 MAUs
- Anthropic: Pay-as-you-go API usage

Estimated total: $20-50/month for small team usage.
