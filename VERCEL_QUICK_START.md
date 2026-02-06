# Vercel Deployment - Quick Start

5-minute guide to deploy Call Coach to Vercel.

## Prerequisites

- [x] Vercel account
- [x] Neon Postgres database
- [x] Clerk account (authentication)
- [x] Gong API credentials
- [x] Anthropic API key

## Setup (One-Time)

### 1. Import to Vercel (2 minutes)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `call-coach` repository
3. Configure:
   - **Root Directory**: `.` (project root)
   - **Framework**: Next.js (auto-detected)
   - **Build Command**: `cd frontend && npm run build`

### 2. Add Environment Variables (3 minutes)

In Vercel Project Settings > Environment Variables, add:

```bash
# Authentication (from Clerk dashboard)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Database (from Neon dashboard - use pooler endpoint!)
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach?sslmode=require
DATABASE_POOL_MIN_SIZE=2
DATABASE_POOL_MAX_SIZE=10

# APIs
GONG_API_KEY=your_key
GONG_API_SECRET=your_secret
GONG_WEBHOOK_SECRET=your_webhook_secret
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
ANTHROPIC_API_KEY=sk-ant-api03-...

# Application
NEXT_PUBLIC_APP_URL=https://coaching.prefect.io

# Cron (generate with: openssl rand -base64 32)
CRON_SECRET=your_generated_secret
```

**Tip**: Select "All Environments" when adding each variable.

## Deploy

### Option 1: Auto-deploy on Push (Recommended)

```bash
git push origin main
```

Vercel automatically deploys main branch to production.

### Option 2: Manual Deploy via CLI

```bash
npm i -g vercel
vercel --prod
```

## Verify Deployment

### 1. Check Build Status

Visit Vercel Dashboard > Deployments and verify:

- [x] Build succeeded
- [x] No errors in logs
- [x] Function deployed successfully

### 2. Test Application

```bash
# Visit production URL
open https://coaching.prefect.io

# Test authentication
# Click "Sign In" and verify Clerk flow works

# Test API (requires auth token from browser)
curl https://coaching.prefect.io/api/opportunities
```

### 3. Test Cron Job

```bash
# Manual trigger
curl -X POST \
  -H "Authorization: Bearer YOUR_CRON_SECRET" \
  https://coaching.prefect.io/api/cron/daily-sync

# Expected response:
# {
#   "job": "daily-gong-sync",
#   "status": "success",
#   "startTime": "...",
#   "endTime": "..."
# }
```

### 4. Check Logs

Vercel Dashboard > Functions > `daily-sync` > View Logs

## Daily Operation

### Automatic Sync

Cron job runs daily at **6:00 AM UTC** automatically.

### Manual Sync

Trigger sync anytime:

```bash
curl -X POST \
  -H "Authorization: Bearer $CRON_SECRET" \
  https://coaching.prefect.io/api/cron/daily-sync
```

### Monitor Logs

```bash
# Via CLI
vercel logs --follow

# Via Dashboard
Vercel Dashboard > Functions > View Logs
```

## Troubleshooting

### Build Fails

```bash
# Test locally first
cd frontend
npm install
npm run build
```

### Database Connection Error

Check:

- [x] Using Neon **pooler endpoint** (not direct)
- [x] `DATABASE_URL` includes `?sslmode=require`
- [x] Pool sizes set correctly (MIN=2, MAX=10)

### Cron Job Not Running

Check:

- [x] `CRON_SECRET` is set in Vercel env vars
- [x] Function logs in Vercel dashboard
- [x] Python dependencies installed (automatic via pyproject.toml)

### 401 Unauthorized (Clerk)

- [x] Using **live keys** (pk*live\*\*, sk*live\*\*) not test keys
- [x] Clerk domain matches production URL
- [x] Sign-in URL configured correctly

## Configuration Files

All configuration is ready in this repo:

- `vercel.json` - Vercel settings
- `frontend/app/api/cron/daily-sync/route.ts` - Cron endpoint
- `.env.production.example` - Environment variable reference
- `DEPLOYMENT.md` - Detailed guide
- `DATABASE_POOLING.md` - Connection pooling docs

## Next Steps

After successful deployment:

1. [ ] Set up custom domain (Project Settings > Domains)
2. [ ] Enable Vercel Analytics (Dashboard > Analytics)
3. [ ] Configure monitoring alerts (if using external service)
4. [ ] Test end-to-end user flows
5. [ ] Share access with team

## Support

**Full Documentation**: See `DEPLOYMENT.md` for comprehensive guide.

**Quick Checks**:

```bash
# Verify config files
bash scripts/verify-deployment-config.sh

# Check deployment status
vercel ls

# View recent logs
vercel logs --limit 50
```

**Common Issues**: See `DEPLOYMENT.md` > Troubleshooting section.

---

**Deployment Time**: ~5 minutes
**First Build**: ~3-5 minutes
**Subsequent Builds**: ~2-3 minutes

Ready? Push to deploy! 🚀
