# Vercel Deployment Checklist

Quick reference for deploying Call Coach to Vercel.

## Pre-Deployment Checklist

### 1. Configuration Files

- [x] `vercel.json` - Vercel configuration with build, functions, and cron settings
- [x] `.env.production.example` - Production environment variables documentation
- [x] `frontend/app/api/cron/daily-sync/route.ts` - Cron job endpoint
- [x] `DEPLOYMENT.md` - Comprehensive deployment guide
- [x] `DATABASE_POOLING.md` - Database connection pooling documentation
- [x] `scripts/verify-deployment-config.sh` - Configuration verification script

### 2. Environment Variables

Run verification:
```bash
bash scripts/verify-deployment-config.sh
```

Required variables (set in Vercel dashboard):

#### Authentication
- [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (pk_live_*)
- [ ] `CLERK_SECRET_KEY` (sk_live_*)
- [ ] `NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in`
- [ ] `NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up`
- [ ] `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard`
- [ ] `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard`

#### Database
- [ ] `DATABASE_URL` (Neon pooler endpoint)
- [ ] `DATABASE_POOL_MIN_SIZE=2`
- [ ] `DATABASE_POOL_MAX_SIZE=10`

#### APIs
- [ ] `GONG_API_KEY`
- [ ] `GONG_API_SECRET`
- [ ] `GONG_WEBHOOK_SECRET`
- [ ] `GONG_API_BASE_URL`
- [ ] `ANTHROPIC_API_KEY`

#### Application
- [ ] `NEXT_PUBLIC_APP_URL=https://coaching.prefect.io`
- [ ] `CRON_SECRET` (generate with: `openssl rand -base64 32`)

### 3. Database Setup

- [ ] Neon project created
- [ ] Connection pooling enabled
- [ ] Database schema deployed
- [ ] Tables created and verified
- [ ] Sample data loaded (optional)

### 4. Vercel Project Setup

- [ ] Project imported from GitHub
- [ ] Custom domain configured
- [ ] Environment variables added
- [ ] Build settings configured

## Deployment Steps

### 1. Test Locally

```bash
# Install dependencies
npm install

# Build frontend
cd frontend && npm run build

# Test cron script
cd .. && uv run python -m flows.daily_gong_sync
```

### 2. Push to Git

```bash
git add .
git commit -m "feat: configure Vercel deployment"
git push origin main
```

### 3. Verify Deployment

1. Check Vercel dashboard for build status
2. Visit production URL
3. Test authentication flow
4. Verify API endpoints work
5. Test cron endpoint manually

```bash
curl -X POST \
  -H "Authorization: Bearer $CRON_SECRET" \
  https://coaching.prefect.io/api/cron/daily-sync
```

### 4. Monitor First Cron Run

Wait for scheduled run at 6am UTC or trigger manually:

```bash
curl -X POST \
  -H "Authorization: Bearer $CRON_SECRET" \
  https://coaching.prefect.io/api/cron/daily-sync
```

Check logs in Vercel dashboard > Functions.

## Post-Deployment

- [ ] Authentication works
- [ ] Database queries work
- [ ] Cron job runs successfully
- [ ] No errors in logs
- [ ] Performance is acceptable
- [ ] SSL certificate active
- [ ] Custom domain resolves

## Configuration Summary

### vercel.json Highlights

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "functions": {
    "frontend/app/api/**/*.ts": {
      "maxDuration": 30,
      "memory": 1024
    },
    "frontend/app/api/cron/daily-sync/route.ts": {
      "maxDuration": 300,
      "memory": 3008
    }
  },
  "crons": [
    {
      "path": "/api/cron/daily-sync",
      "schedule": "0 6 * * *"
    }
  ]
}
```

### Key Features

1. **Build Configuration**
   - Builds frontend from root directory
   - Outputs to `frontend/.next`
   - Uses Next.js framework detection

2. **Serverless Functions**
   - Standard API routes: 30s timeout, 1GB memory
   - Cron job: 300s timeout, 3GB memory (for large syncs)

3. **Cron Jobs**
   - Daily sync at 6am UTC
   - Authenticated with `CRON_SECRET`
   - Syncs opportunities, calls, and emails

4. **Security Headers**
   - CSP configured for Clerk and analytics
   - HSTS enabled
   - XSS protection
   - Frame options set

### Database Connection Pooling

For serverless deployment:

```bash
DATABASE_POOL_MIN_SIZE=2    # Smaller than local dev
DATABASE_POOL_MAX_SIZE=10   # Matches Neon plan limits
```

Why smaller pools?
- Each serverless function gets its own pool
- Many concurrent functions = many pools
- Neon pooler handles connection management

### Cron Job Architecture

```
Vercel Cron (6am UTC)
    ↓
POST /api/cron/daily-sync (with CRON_SECRET)
    ↓
Execute: uv run python -m flows.daily_gong_sync
    ↓
1. Sync opportunities from Gong
2. Link calls to opportunities
3. Sync emails for opportunities
    ↓
Update sync_status table
    ↓
Return results (200 OK)
```

## Troubleshooting

### Build Fails

```bash
# Test build locally
cd frontend
npm install
npm run build
```

### Database Connection Errors

- Verify using Neon pooler endpoint (not direct)
- Check connection pool settings
- Review Neon dashboard for connection count

### Cron Job Doesn't Run

- Check function logs in Vercel dashboard
- Verify `CRON_SECRET` is set
- Test endpoint manually with curl
- Ensure all Python dependencies are installed

### Function Timeouts

- Check function `maxDuration` in vercel.json
- Optimize database queries
- Add indexes to database tables
- Consider breaking large syncs into smaller batches

## Resources

- **Deployment Guide**: `DEPLOYMENT.md`
- **Database Pooling**: `DATABASE_POOLING.md`
- **Verification Script**: `scripts/verify-deployment-config.sh`
- **Environment Variables**: `.env.production.example`

## Support

For issues:
1. Check Vercel build logs
2. Review function runtime logs
3. Verify environment variables
4. Test locally first
5. Check database connection status

---

**Ready to deploy?** Follow steps in `DEPLOYMENT.md`.
