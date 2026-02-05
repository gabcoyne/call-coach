# Vercel Deployment Guide

This guide walks through deploying the Call Coach Next.js frontend to Vercel, including production and preview environment setup, custom domain configuration, security headers, analytics, and monitoring.

## Prerequisites

- GitHub repository with call-coach monorepo
- Vercel account (free tier supports all required features)
- Access to Prefect DNS settings (for custom domain)
- Clerk production application configured
- Production MCP backend URL

## Table of Contents

1. [Initial Vercel Setup](#1-initial-vercel-setup)
2. [Monorepo Configuration](#2-monorepo-configuration)
3. [Environment Variables](#3-environment-variables)
4. [Custom Domain Setup](#4-custom-domain-setup)
5. [SSL and HTTPS Configuration](#5-ssl-and-https-configuration)
6. [Deployment Settings](#6-deployment-settings)
7. [Notifications](#7-notifications)
8. [Analytics Setup](#8-analytics-setup)
9. [Security Headers](#9-security-headers)
10. [Verification and Testing](#10-verification-and-testing)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Initial Vercel Setup

### 1.1 Create Vercel Account

1. Navigate to [vercel.com](https://vercel.com)
2. Click "Sign Up" and choose "Continue with GitHub"
3. Authorize Vercel to access your GitHub account
4. Complete the account setup wizard

### 1.2 Import GitHub Repository

1. From the Vercel dashboard, click "Add New..." → "Project"
2. In the "Import Git Repository" section, find `prefect/call-coach`
3. Click "Import" next to the repository
4. If the repository isn't visible:
   - Click "Adjust GitHub App Permissions"
   - Grant Vercel access to the `call-coach` repository
   - Return to the import screen

---

## 2. Monorepo Configuration

### 2.1 Framework Preset

On the project configuration screen:

1. **Framework Preset**: Select "Next.js" from the dropdown
2. **Root Directory**: Click "Edit" and set to `frontend`
   - This tells Vercel to build from the `frontend/` subdirectory
3. **Build Command**: Override with `npm run build`
   - Vercel will automatically detect this from `package.json`
4. **Output Directory**: Leave as `.next` (default for Next.js)
5. **Install Command**: Leave as `npm install`

### 2.2 Build Settings Explanation

The `vercel.json` at the repository root defines additional configuration:

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "installCommand": "npm install",
  "framework": "nextjs"
}
```

These settings ensure Vercel correctly handles the monorepo structure.

---

## 3. Environment Variables

### 3.1 Production Environment Variables

Navigate to **Project Settings** → **Environment Variables** and add:

#### Clerk Authentication (Production)

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_...` from Clerk production app | Production |
| `CLERK_SECRET_KEY` | `sk_live_...` from Clerk production app | Production |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` | Production |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` | Production |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` | `/dashboard` | Production |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` | `/dashboard` | Production |

**Get Clerk Keys:**
1. Go to [dashboard.clerk.com](https://dashboard.clerk.com)
2. Navigate to your production application
3. Click "API Keys" in the sidebar
4. Copy the "Publishable key" and "Secret key"

#### MCP Backend (Production)

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_MCP_BACKEND_URL` | `https://mcp.prefect.io` (or your production URL) | Production |

#### Application URLs

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_APP_URL` | `https://coaching.prefect.io` | Production |

### 3.2 Preview Environment Variables (Staging)

For preview deployments (pull requests), configure staging variables:

Navigate to **Project Settings** → **Environment Variables** and add with "Preview" selected:

#### Clerk Authentication (Staging)

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_...` from Clerk development app | Preview |
| `CLERK_SECRET_KEY` | `sk_test_...` from Clerk development app | Preview |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` | Preview |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` | Preview |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` | `/dashboard` | Preview |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` | `/dashboard` | Preview |

#### MCP Backend (Staging)

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_MCP_BACKEND_URL` | `https://mcp-staging.prefect.io` | Preview |

#### Application URLs

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_APP_URL` | Auto-populated by Vercel (`VERCEL_URL`) | Preview |

### 3.3 Environment Variable Best Practices

- **Never commit secrets** to `.env` files in git
- Use `.env.local` for local development (gitignored)
- Keep `.env.example` updated with required variable names (without values)
- Rotate secrets regularly (quarterly recommended)
- Use separate Clerk applications for development/staging/production

---

## 4. Custom Domain Setup

### 4.1 Add Domain to Vercel

1. Navigate to **Project Settings** → **Domains**
2. Click "Add Domain"
3. Enter `coaching.prefect.io`
4. Click "Add"

### 4.2 Configure DNS (Prefect DNS Provider)

Vercel will display DNS configuration instructions. You need to add a CNAME record:

#### Using Cloudflare (or other DNS provider):

1. Log into your DNS provider (e.g., Cloudflare)
2. Navigate to DNS settings for `prefect.io`
3. Add a CNAME record:
   - **Name**: `coaching`
   - **Target**: `cname.vercel-dns.com`
   - **Proxy status**: DNS only (gray cloud in Cloudflare)
   - **TTL**: Auto or 300 seconds
4. Save the record

#### Verification

DNS propagation can take 24-48 hours, but typically completes within minutes.

1. Vercel will automatically verify the DNS record
2. Once verified, you'll see a green checkmark next to the domain
3. Vercel will automatically provision an SSL certificate (see next section)

### 4.3 Set Primary Domain

1. In the Domains list, find `coaching.prefect.io`
2. Click the three-dot menu → "Set as Primary Domain"
3. This ensures all traffic redirects to the custom domain

---

## 5. SSL and HTTPS Configuration

### 5.1 Automatic SSL Certificate

Vercel automatically provisions SSL certificates via Let's Encrypt:

1. Once DNS is verified, Vercel requests a certificate
2. Certificate provisioning typically takes 1-5 minutes
3. You'll see "Certificate Active" status when ready
4. Certificates auto-renew 30 days before expiration

### 5.2 HTTPS Enforcement

The `vercel.json` configuration includes security headers that enforce HTTPS:

```json
{
  "key": "Strict-Transport-Security",
  "value": "max-age=63072000; includeSubDomains; preload"
}
```

This header (HSTS):
- Forces browsers to use HTTPS for 2 years (`max-age=63072000`)
- Applies to all subdomains (`includeSubDomains`)
- Eligible for browser HSTS preload lists (`preload`)

### 5.3 HSTS Preload Submission (Optional)

For maximum security, submit your domain to the HSTS preload list:

1. Navigate to [hstspreload.org](https://hstspreload.org)
2. Enter `coaching.prefect.io`
3. Click "Check HSTS preload status and eligibility"
4. If eligible, click "Submit"

**Warning**: HSTS preload is a one-way commitment. Removal can take months.

---

## 6. Deployment Settings

### 6.1 Enable Automatic Preview Deployments

1. Navigate to **Project Settings** → **Git**
2. Under "Preview Deployments", ensure "Automatic Preview Deployments" is **enabled**
3. Configure preview settings:
   - **All branches**: Deploy every branch push
   - **Only production branch**: Deploy only main/master branch
   - **Recommended**: All branches (for maximum preview coverage)

### 6.2 Configure Production Branch

1. In **Project Settings** → **Git**
2. Under "Production Branch", set to `main` (or `master`)
3. Enable "Automatic Production Deployments on Branch Push"

This ensures:
- Pushing to `main` triggers production deployment
- Opening a PR triggers preview deployment
- Preview URL format: `call-coach-git-<branch>-<team>.vercel.app`

### 6.3 Branch Protection (GitHub)

Protect the production branch to prevent accidental deployments:

1. In GitHub, navigate to repository settings → Branches
2. Add a branch protection rule for `main`:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass (Vercel preview)
   - ✅ Require branches to be up to date before merging
   - ✅ Require deployments to succeed before merging

---

## 7. Notifications

### 7.1 Slack Integration

#### Setup Slack App

1. Navigate to **Project Settings** → **Integrations**
2. Search for "Slack" and click "Add"
3. Click "Add to Slack"
4. Select your Slack workspace and authorize
5. Choose a channel (e.g., `#engineering-deployments`)

#### Configure Notification Events

Enable notifications for:
- ✅ Deployment Started
- ✅ Deployment Ready (Success)
- ✅ Deployment Failed
- ✅ Deployment Canceled
- ⬜ Comment on Deployment (optional)

#### Notification Format

Slack messages will include:
- Deployment status (success/failure)
- Environment (production/preview)
- Branch and commit info
- Deployment URL
- Build logs link

### 7.2 Email Notifications

Vercel sends email notifications automatically to project members:

1. Navigate to **Project Settings** → **Notifications**
2. Configure email preferences:
   - Production deployment failures (recommended: enabled)
   - Preview deployment failures (recommended: disabled for high-volume repos)

---

## 8. Analytics Setup

### 8.1 Enable Vercel Analytics

Vercel Analytics tracks Core Web Vitals and real user performance data.

1. Navigate to **Project Settings** → **Analytics**
2. Click "Enable Analytics"
3. Choose plan:
   - **Hobby (Free)**: 2,500 data points/month
   - **Pro**: 100,000 data points/month
   - Recommended: Start with Free tier

### 8.2 Install Analytics Package (Next.js)

The Next.js integration is automatic for Vercel deployments. No code changes required.

For self-hosted Next.js (non-Vercel), install:

```bash
npm install @vercel/analytics
```

And add to `app/layout.tsx`:

```tsx
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### 8.3 Vercel Speed Insights (Optional)

For deeper performance insights:

1. Navigate to **Project Settings** → **Speed Insights**
2. Click "Enable Speed Insights"
3. Install package (if self-hosted):

```bash
npm install @vercel/speed-insights
```

4. Add to `app/layout.tsx`:

```tsx
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

### 8.4 Core Web Vitals Monitoring

View Core Web Vitals in the Vercel dashboard:

1. Navigate to your project → **Analytics**
2. View metrics:
   - **LCP (Largest Contentful Paint)**: Target < 2.5s
   - **FID (First Input Delay)**: Target < 100ms
   - **CLS (Cumulative Layout Shift)**: Target < 0.1
   - **TTFB (Time to First Byte)**: Target < 600ms

Set up alerts:
1. Click "Configure Alerts"
2. Set thresholds for each metric
3. Configure notification channel (email/Slack)

---

## 9. Security Headers

### 9.1 Verify Security Headers

The `vercel.json` configuration includes comprehensive security headers. Verify they're working:

1. Deploy the application
2. Visit [securityheaders.com](https://securityheaders.com)
3. Enter `https://coaching.prefect.io`
4. Click "Scan"
5. Target score: **A** or **A+**

### 9.2 Security Header Breakdown

#### Strict-Transport-Security (HSTS)
```
max-age=63072000; includeSubDomains; preload
```
- Forces HTTPS for 2 years
- Applies to all subdomains
- Prevents SSL stripping attacks

#### X-Frame-Options
```
SAMEORIGIN
```
- Prevents clickjacking attacks
- Only allows framing from same origin

#### X-Content-Type-Options
```
nosniff
```
- Prevents MIME type sniffing
- Forces browsers to respect Content-Type header

#### Content-Security-Policy (CSP)
```
default-src 'self';
script-src 'self' 'unsafe-eval' 'unsafe-inline' https://clerk.prefect.io;
connect-src 'self' https://api.clerk.com https://*.vercel-insights.com;
...
```
- Restricts resource loading to trusted sources
- Prevents XSS attacks
- Allows Clerk authentication and Vercel analytics

#### Referrer-Policy
```
strict-origin-when-cross-origin
```
- Controls referrer information sent with requests
- Sends full URL for same-origin, origin only for cross-origin

#### Permissions-Policy
```
camera=(), microphone=(), geolocation=()
```
- Disables camera, microphone, and geolocation APIs
- Reduces attack surface for sensitive features

### 9.3 CSP Customization

If you encounter CSP violations:

1. Open browser DevTools Console
2. Look for CSP violation errors
3. Update `vercel.json` CSP header to allow legitimate sources
4. Redeploy

**Common additions:**
- **External fonts**: Add to `font-src`
- **External images**: Add to `img-src`
- **External APIs**: Add to `connect-src`

---

## 10. Verification and Testing

### 10.1 Production Deployment Checklist

After initial deployment, verify:

- [ ] Custom domain resolves correctly
- [ ] HTTPS certificate is active
- [ ] Authentication flow works (sign in/sign up)
- [ ] Dashboard loads and displays data
- [ ] Call analysis page renders
- [ ] Search functionality works
- [ ] API routes respond correctly
- [ ] Security headers present (check securityheaders.com)
- [ ] Core Web Vitals within target ranges
- [ ] Mobile responsive design works
- [ ] Slack notifications arrive on deployment

### 10.2 Preview Deployment Testing

Test preview deployments:

1. Create a new branch: `git checkout -b test-deployment`
2. Make a trivial change (e.g., update README)
3. Push: `git push origin test-deployment`
4. Open a pull request
5. Wait for Vercel preview deployment
6. Click "Visit Preview" in GitHub PR status checks
7. Test authentication and core functionality
8. Verify preview environment variables (staging backend)

### 10.3 Rollback Procedure

If a production deployment fails:

1. Navigate to **Deployments** in Vercel dashboard
2. Find the last successful deployment
3. Click three-dot menu → "Promote to Production"
4. Confirm promotion
5. Deployment rolls back instantly (no rebuild required)

### 10.4 Deployment Logs

Access logs for debugging:

1. Navigate to **Deployments**
2. Click on a deployment
3. View tabs:
   - **Building**: Build logs (npm install, build output)
   - **Functions**: Serverless function logs (API routes)
   - **Static**: Static asset logs
4. Use search and filtering to find issues

---

## 11. Troubleshooting

### 11.1 Build Failures

**Symptom**: Deployment fails during build phase

**Solutions**:
1. Check build logs in Vercel dashboard
2. Verify `package.json` scripts are correct
3. Ensure all dependencies are in `dependencies` (not `devDependencies`)
4. Test build locally: `cd frontend && npm run build`
5. Check for TypeScript errors: `npm run lint`

**Common issues**:
- Missing environment variables (check `.env.example`)
- TypeScript strict mode errors
- Clerk configuration issues

### 11.2 Environment Variable Issues

**Symptom**: Application works locally but fails in production

**Solutions**:
1. Verify all environment variables are set in Vercel
2. Check variable names (typos in `NEXT_PUBLIC_*`)
3. Ensure Clerk keys are from production app (not development)
4. Restart deployment after adding variables

**Testing**:
```bash
# In browser console on deployed app:
console.log(process.env.NEXT_PUBLIC_MCP_BACKEND_URL)
```

### 11.3 DNS and Domain Issues

**Symptom**: Domain not resolving or SSL errors

**Solutions**:
1. Verify CNAME record points to `cname.vercel-dns.com`
2. Check DNS propagation: `nslookup coaching.prefect.io`
3. Wait 24 hours for DNS propagation
4. Remove and re-add domain in Vercel
5. Contact Vercel support if SSL provisioning fails

**Check DNS**:
```bash
# Should return Vercel IP addresses
dig coaching.prefect.io

# Or use online tool: https://dnschecker.org
```

### 11.4 Clerk Authentication Failures

**Symptom**: Sign in redirects fail or "Invalid publishable key"

**Solutions**:
1. Verify `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` matches production app
2. Check `CLERK_SECRET_KEY` is from same Clerk app
3. Ensure Clerk domain matches: `https://coaching.prefect.io`
4. Add `coaching.prefect.io` to Clerk allowed domains:
   - Clerk Dashboard → Domains → Add domain

### 11.5 CSP Violations

**Symptom**: Resources blocked by Content Security Policy

**Solutions**:
1. Open browser DevTools Console
2. Note the blocked resource URL
3. Update `vercel.json` CSP header to allow the source
4. Redeploy

**Example**:
```
Refused to load script from 'https://example.com/script.js'
```

Add `https://example.com` to `script-src` in CSP:
```json
"script-src 'self' 'unsafe-inline' https://example.com"
```

### 11.6 API Route Timeouts

**Symptom**: API routes return 504 Gateway Timeout

**Solutions**:
1. Increase function timeout in `vercel.json`:
```json
"functions": {
  "app/api/**/*.ts": {
    "maxDuration": 30
  }
}
```
2. Optimize API route logic (reduce database queries)
3. Implement caching (SWR on frontend)
4. Consider upgrading Vercel plan (Hobby: 10s max, Pro: 60s max)

### 11.7 Support and Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Support**: Support tab in dashboard (Pro plan)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Next.js Discord**: [nextjs.org/discord](https://nextjs.org/discord)
- **Clerk Support**: [clerk.com/support](https://clerk.com/support)

---

## Summary

This guide covered:
1. ✅ Creating Vercel account and linking GitHub repository
2. ✅ Configuring Next.js framework with monorepo root directory
3. ✅ Setting up production and preview environment variables
4. ✅ Configuring custom domain with DNS and SSL
5. ✅ Enabling automatic deployments on branch push and PR
6. ✅ Setting up Slack notifications
7. ✅ Enabling Vercel Analytics for Core Web Vitals
8. ✅ Configuring comprehensive security headers (CSP, HSTS, etc.)

Your Call Coach frontend is now production-ready on Vercel with enterprise-grade security, monitoring, and deployment automation.

**Next Steps:**
1. Complete the initial deployment following Section 1-3
2. Test preview deployments with a pull request
3. Monitor Core Web Vitals in Vercel Analytics
4. Set up alerts for performance degradation
5. Schedule weekly review of deployment logs and analytics
