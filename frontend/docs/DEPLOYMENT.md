# Deployment Guide - Vercel

Complete guide for deploying the Gong Call Coaching frontend to Vercel with zero-downtime deployment and instant rollback capabilities.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment Workflows](#deployment-workflows)
- [Rollback Procedures](#rollback-procedures)
- [Domain Configuration](#domain-configuration)
- [Monitoring and Analytics](#monitoring-and-analytics)
- [Security Configuration](#security-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The frontend is deployed on [Vercel](https://vercel.com), a platform optimized for Next.js applications with:

- **Automatic Deployments**: Every push triggers a build
- **Preview Deployments**: Each PR gets a unique preview URL
- **Zero-Downtime Deploys**: New versions go live atomically
- **Instant Rollbacks**: One-click rollback to previous versions
- **Edge Network**: Global CDN for fast load times
- **Analytics**: Built-in performance monitoring

### Deployment Environments

1. **Development**: Local development (`npm run dev`)
2. **Preview**: PR preview deployments (staging backend)
3. **Production**: Main branch deployments (production backend)

## Prerequisites

Before deploying, ensure you have:

- [ ] GitHub repository with the frontend code
- [ ] Vercel account (sign up at [vercel.com](https://vercel.com))
- [ ] Clerk production account with API keys
- [ ] MCP backend production URL
- [ ] Admin access to DNS for custom domain (optional)

## Initial Setup

### Step 1: Create Vercel Project

1. **Sign in to Vercel**

   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Import Repository**

   - Click "Add New Project"
   - Select your GitHub repository
   - Authorize Vercel to access the repo

3. **Configure Build Settings**

   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend/` (for monorepo)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

4. **Set Node.js Version**

   - In `package.json`, add:

   ```json
   {
     "engines": {
       "node": "20.x"
     }
   }
   ```

5. **Click Deploy**
   - Initial deployment will fail due to missing environment variables
   - This is expected; we'll add them next

### Step 2: Configure Environment Variables

See the [Environment Variables](#environment-configuration) section below for detailed configuration.

### Step 3: Redeploy

After adding environment variables:

1. Go to **Deployments** tab
2. Click "..." on the latest deployment
3. Select "Redeploy"
4. Deployment should succeed

## Environment Configuration

### Required Environment Variables

Configure these in **Settings → Environment Variables**:

#### Production Environment

Set these variables with **Production** scope:

```bash
# Clerk Authentication (PRODUCTION KEYS)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
CLERK_SECRET_KEY=sk_live_xxxxx

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# MCP Backend (Production)
NEXT_PUBLIC_MCP_BACKEND_URL=https://coaching-api.prefect.io
```

#### Preview Environment

Set these variables with **Preview** scope:

```bash
# Clerk Authentication (TEST KEYS or separate staging keys)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# MCP Backend (Staging)
NEXT_PUBLIC_MCP_BACKEND_URL=https://coaching-api-staging.prefect.io
```

### Adding Environment Variables

**Via Vercel Dashboard**:

1. Go to your project in Vercel
2. Navigate to **Settings → Environment Variables**
3. For each variable:
   - Click "Add New"
   - Enter **Name** (e.g., `CLERK_SECRET_KEY`)
   - Enter **Value**
   - Select **Environments**: Production, Preview, or both
   - Click "Save"

**Via Vercel CLI** (optional):

```bash
# Install Vercel CLI
npm i -g vercel

# Link project
vercel link

# Add production variable
vercel env add CLERK_SECRET_KEY production

# Add preview variable
vercel env add CLERK_SECRET_KEY preview
```

### Environment Variable Updates

When you change environment variables:

1. **Automatic**: Changes apply to new deployments
2. **Manual**: Redeploy to apply immediately
   - Go to **Deployments** tab
   - Find latest production deployment
   - Click "..." → "Redeploy"

## Deployment Workflows

### Production Deployment (Main Branch)

**Automatic Deployment**:

1. Create PR and merge to `main` branch
2. Vercel automatically detects push to `main`
3. Triggers production build and deployment
4. Deploys to production domain
5. Posts deployment status to GitHub commit

**Manual Deployment** (via CLI):

```bash
# Navigate to frontend directory
cd frontend/

# Deploy to production
vercel --prod

# Or deploy specific branch
vercel --prod --branch main
```

### Preview Deployment (Pull Requests)

**Automatic Preview**:

1. Create pull request
2. Vercel automatically builds preview
3. Posts unique preview URL to PR comments
4. Every push to PR updates preview

**Preview URL Format**:

```
https://gong-coaching-<pr-branch>-<team-name>.vercel.app
```

**Manual Preview** (via CLI):

```bash
# Deploy preview without production
vercel

# Deploy specific branch
vercel --branch feature/new-feature
```

### Preview Deployment Lifecycle

- **Created**: When PR is opened
- **Updated**: On every push to PR branch
- **Persists**: Preview remains live until PR is closed
- **Cleaned Up**: Deleted 7 days after PR is closed/merged

## Rollback Procedures

Vercel provides instant rollback to any previous deployment.

### Rollback via Dashboard

**Method 1: Promote Previous Deployment**

1. Go to **Deployments** tab
2. Find the last known good deployment
3. Click "..." menu on that deployment
4. Select "Promote to Production"
5. Confirm promotion
6. Deployment goes live immediately

**Method 2: Redeploy Previous Commit**

1. Go to **Deployments** tab
2. Find deployment from working commit
3. Click "..." menu
4. Select "Redeploy"
5. Deployment rebuilds and goes live

### Rollback via CLI

```bash
# List recent deployments
vercel ls

# Promote specific deployment to production
vercel promote <deployment-url>

# Example
vercel promote gong-coaching-abc123.vercel.app
```

### Rollback via Git

If needed, rollback at the git level:

```bash
# Find commit to rollback to
git log --oneline

# Create revert commit
git revert <bad-commit-hash>

# Or reset to previous commit (use with caution)
git reset --hard <good-commit-hash>
git push --force

# Vercel automatically deploys the reverted code
```

### Rollback Checklist

When rolling back:

- [ ] Identify last known good deployment
- [ ] Note timestamp and commit SHA
- [ ] Perform rollback (dashboard or CLI)
- [ ] Verify production site is working
- [ ] Check monitoring/logs for errors
- [ ] Notify team of rollback
- [ ] Investigate root cause
- [ ] Fix issue in new PR
- [ ] Document incident

## Domain Configuration

### Adding Custom Domain

**Step 1: Add Domain in Vercel**

1. Go to **Settings → Domains**
2. Click "Add Domain"
3. Enter your domain: `coaching.prefect.io`
4. Click "Add"

**Step 2: Configure DNS**

Vercel provides DNS records to configure:

**Option A: CNAME Record** (recommended for subdomains)

```
Type:  CNAME
Name:  coaching
Value: cname.vercel-dns.com
TTL:   3600
```

**Option B: A Record** (for apex domains)

```
Type:  A
Name:  @
Value: 76.76.21.21
TTL:   3600
```

**Step 3: Verify DNS Configuration**

1. Configure DNS records with your DNS provider
2. Return to Vercel dashboard
3. Vercel automatically verifies DNS (may take 5-10 minutes)
4. Once verified, domain shows "Valid Configuration"

### SSL/HTTPS Configuration

Vercel automatically:

- Provisions Let's Encrypt SSL certificate
- Enables HTTPS
- Redirects HTTP to HTTPS
- Renews certificate before expiry

No manual configuration needed.

### WWW Redirect

To redirect `www.coaching.prefect.io` to `coaching.prefect.io`:

1. Add `www.coaching.prefect.io` as second domain
2. Vercel automatically redirects to primary domain

## Monitoring and Analytics

### Vercel Analytics

**Enable Analytics**:

1. Go to **Analytics** tab in project
2. Click "Enable Vercel Analytics"
3. Free tier: 1M events/month

**Metrics Tracked**:

- Page views
- Unique visitors
- Core Web Vitals (LCP, FID, CLS)
- Top pages
- Geographic distribution

**Viewing Analytics**:

- Dashboard → Analytics tab
- Filter by time range (24h, 7d, 30d)
- View real-time data

### Vercel Speed Insights

Tracks Core Web Vitals in production:

**Enable Speed Insights**:

1. Install package:

```bash
npm install @vercel/speed-insights
```

2. Add to root layout:

```typescript
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

3. Deploy and view in **Speed Insights** tab

### Function Logs

View logs for API routes:

1. Go to **Deployments** tab
2. Click on a deployment
3. Click **Functions** to see API route invocations
4. Click on a function to view logs

**CLI Logs**:

```bash
# Tail production logs in real-time
vercel logs --follow

# View specific deployment logs
vercel logs <deployment-url>
```

### Deployment Notifications

**Slack Integration**:

1. Go to **Settings → Notifications**
2. Click "Add Notification"
3. Select "Slack"
4. Authorize Vercel for your Slack workspace
5. Choose channel (e.g., `#engineering`)
6. Select events:
   - Deployment started
   - Deployment ready
   - Deployment error

**Email Notifications**:

- Automatic for deployment failures
- Configure in **Settings → Notifications**

## Security Configuration

### Security Headers

Add security headers in `next.config.ts`:

```typescript
// next.config.ts
const nextConfig = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

### Content Security Policy (CSP)

Add CSP header for XSS protection:

```typescript
{
  key: 'Content-Security-Policy',
  value: [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Adjust based on needs
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self' https://api.clerk.com https://coaching-api.prefect.io",
    "frame-ancestors 'none'",
  ].join('; '),
}
```

### Environment Variable Encryption

Vercel automatically encrypts all environment variables:

- Encrypted at rest
- Only decrypted at build/runtime
- Never exposed in logs or client code (unless `NEXT_PUBLIC_*`)

### Restricting Access (Optional)

**Password Protection** (for preview deployments):

1. Go to **Settings → Deployment Protection**
2. Enable "Password Protection"
3. Set password for preview deployments
4. Users must enter password to access preview URLs

**Vercel Authentication** (Enterprise):

- Requires users to sign in with Vercel account
- Available on Enterprise plans only

## Troubleshooting

### Build Failures

**Issue: TypeScript errors during build**

```
Type error: Property 'x' does not exist on type 'Y'
```

**Solution**:

1. Fix TypeScript errors locally
2. Run `npm run build` to verify
3. Run `npx tsc --noEmit` to check types
4. Push fixes and redeploy

**Issue: Missing dependencies**

```
Cannot find module '@/lib/utils'
```

**Solution**:

1. Verify all imports use correct paths
2. Check `tsconfig.json` path aliases match
3. Ensure all dependencies in `package.json`
4. Delete `node_modules` and `npm install` locally

### Runtime Errors

**Issue: Environment variables not found**

```
MCP_BACKEND_URL is undefined
```

**Solution**:

1. Verify variables are set in Vercel dashboard
2. Check variable names match exactly (including `NEXT_PUBLIC_` prefix)
3. Redeploy after adding variables
4. Check environment scope (Production vs Preview)

**Issue: API routes returning 500 errors**

**Solution**:

1. Check function logs in Vercel dashboard
2. Verify MCP backend URL is correct and reachable
3. Check Clerk API keys are valid
4. Review API route code for errors

### Performance Issues

**Issue: Slow page loads**

**Solution**:

1. Check Vercel Analytics → Speed Insights
2. Optimize images (use Next.js Image component)
3. Enable ISR for static pages
4. Reduce JavaScript bundle size
5. Review Vercel Function logs for slow API routes

**Issue: High bandwidth usage**

**Solution**:

1. Optimize images (WebP format, responsive sizes)
2. Enable caching headers
3. Use Vercel Image Optimization
4. Audit large dependencies

### Deployment Stuck

**Issue: Deployment queued indefinitely**

**Solution**:

1. Check Vercel Status page: [vercel-status.com](https://www.vercel-status.com/)
2. Cancel stuck deployment and retry
3. Contact Vercel support if persists

### Domain Issues

**Issue: Domain not resolving**

**Solution**:

1. Verify DNS records are correct
2. Wait 5-10 minutes for DNS propagation
3. Use DNS checker tool: `dig coaching.prefect.io`
4. Contact DNS provider if issues persist

**Issue: SSL certificate not provisioning**

**Solution**:

1. Ensure DNS is correctly configured
2. Remove and re-add domain
3. Wait 30 minutes for certificate provisioning
4. Contact Vercel support if not resolved

## Best Practices

### Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests pass locally
- [ ] TypeScript compiles without errors (`npx tsc --noEmit`)
- [ ] ESLint passes (`npm run lint`)
- [ ] Production build succeeds (`npm run build`)
- [ ] Environment variables are configured in Vercel
- [ ] Changes tested in preview deployment
- [ ] Team reviewed and approved changes
- [ ] Documentation updated (if needed)

### Deployment Schedule

**Recommended Schedule**:

- **Monday-Thursday**: Safe to deploy
- **Friday**: Avoid unless critical
- **Weekends**: Emergency fixes only

**Deploy During**:

- Off-peak hours (if downtime expected)
- When team is available to monitor
- When you can quickly rollback if needed

### Monitoring After Deployment

After deploying to production:

1. **Immediate (0-5 minutes)**:

   - [ ] Visit production URL and verify it loads
   - [ ] Test authentication (sign in)
   - [ ] Test critical user flows (view call, search)
   - [ ] Check browser console for errors

2. **Short-term (5-30 minutes)**:

   - [ ] Monitor Vercel function logs for errors
   - [ ] Check Vercel Analytics for traffic
   - [ ] Review user reports (if any)

3. **Long-term (1-24 hours)**:
   - [ ] Review Core Web Vitals in Speed Insights
   - [ ] Check for increased error rates
   - [ ] Monitor performance metrics

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Vercel Status Page](https://www.vercel-status.com/)
- [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

**Need Help?**

- Vercel Support: [vercel.com/support](https://vercel.com/support)
- Internal: Contact DevOps team
- Emergency: Follow [RUNBOOK.md](./RUNBOOK.md) incident procedures
