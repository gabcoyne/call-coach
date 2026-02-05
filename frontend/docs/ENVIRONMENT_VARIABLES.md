# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the Gong Call Coaching frontend application.

## Table of Contents

- [Required Variables](#required-variables)
- [Optional Variables](#optional-variables)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Security Best Practices](#security-best-practices)

## Required Variables

These environment variables **must** be configured for the application to function properly.

### Clerk Authentication

#### `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`

- **Type**: Public key (can be exposed to client)
- **Required**: Yes
- **Description**: Clerk publishable key for client-side authentication
- **Example**: `pk_test_c2FtcGxlLWNsZXJrLWtleS1mb3ItdGVzdGluZw==`
- **Where to get it**: [Clerk Dashboard](https://dashboard.clerk.com) → Your App → API Keys

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
```

#### `CLERK_SECRET_KEY`

- **Type**: Secret key (server-side only)
- **Required**: Yes
- **Description**: Clerk secret key for server-side authentication and API operations
- **Example**: `sk_test_c2FtcGxlLWNsZXJrLXNlY3JldC1rZXktZm9yLXRlc3Rpbmc=`
- **Where to get it**: [Clerk Dashboard](https://dashboard.clerk.com) → Your App → API Keys
- **Security**: Never commit this to git or expose to client-side code

```bash
CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

### MCP Backend

#### `NEXT_PUBLIC_MCP_BACKEND_URL`

- **Type**: Public URL
- **Required**: Yes
- **Description**: URL of the FastMCP backend server that provides coaching tools
- **Default**: `http://localhost:8000` (development)
- **Production Example**: `https://coaching-api.prefect.io`

```bash
# Development
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000

# Production
NEXT_PUBLIC_MCP_BACKEND_URL=https://coaching-api.prefect.io
```

## Optional Variables

These variables have sensible defaults but can be customized.

### Clerk URLs and Redirects

#### `NEXT_PUBLIC_CLERK_SIGN_IN_URL`

- **Type**: Path
- **Required**: No
- **Default**: `/sign-in`
- **Description**: Path to the sign-in page

```bash
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
```

#### `NEXT_PUBLIC_CLERK_SIGN_UP_URL`

- **Type**: Path
- **Required**: No
- **Default**: `/sign-up`
- **Description**: Path to the sign-up page

```bash
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

#### `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL`

- **Type**: Path
- **Required**: No
- **Default**: `/dashboard`
- **Description**: Where to redirect users after successful sign-in

```bash
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
```

#### `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL`

- **Type**: Path
- **Required**: No
- **Default**: `/dashboard`
- **Description**: Where to redirect users after successful sign-up

```bash
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## Environment-Specific Configuration

### Local Development (`.env.local`)

For local development, create a `.env.local` file in the frontend directory:

```bash
# Clerk Authentication (Development Keys)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_dev_key
CLERK_SECRET_KEY=sk_test_your_dev_secret

# Clerk URLs (defaults work for most cases)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# MCP Backend (local server)
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000
```

### Preview/Staging (Vercel)

For preview deployments (PRs), configure in Vercel dashboard under **Settings → Environment Variables → Preview**:

```bash
# Clerk Authentication (can use same dev keys or separate staging keys)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_staging_key
CLERK_SECRET_KEY=sk_test_staging_secret

# MCP Backend (staging server)
NEXT_PUBLIC_MCP_BACKEND_URL=https://coaching-api-staging.prefect.io
```

### Production (Vercel)

For production deployments, configure in Vercel dashboard under **Settings → Environment Variables → Production**:

```bash
# Clerk Authentication (PRODUCTION KEYS)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_production_key
CLERK_SECRET_KEY=sk_live_production_secret

# Clerk URLs (production paths)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# MCP Backend (production server)
NEXT_PUBLIC_MCP_BACKEND_URL=https://coaching-api.prefect.io
```

## Security Best Practices

### Secret Management

1. **Never commit secrets**: Use `.env.local` for local development and add it to `.gitignore`
2. **Use different keys per environment**: Separate keys for dev, staging, and production
3. **Rotate keys periodically**: Update production keys every 90 days
4. **Limit access**: Only give Vercel dashboard access to team members who need it

### Public vs. Secret Variables

- **Public (`NEXT_PUBLIC_*`)**: Can be exposed to client-side code, included in browser bundle
- **Secret (no prefix)**: Only available server-side (API routes, middleware)

### Examples of What Goes Where

**Public variables** (safe for client):
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - needed for Clerk client SDK
- `NEXT_PUBLIC_MCP_BACKEND_URL` - needed for client-side API calls
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` - URL redirect paths

**Secret variables** (server-only):
- `CLERK_SECRET_KEY` - used for server-side Clerk operations
- API keys for external services
- Database connection strings (if added)

### Vercel Environment Variables Configuration

1. Go to your Vercel project dashboard
2. Navigate to **Settings → Environment Variables**
3. Add each variable with appropriate scope:
   - **Production**: Only for production deployments
   - **Preview**: For PR preview deployments
   - **Development**: For local development (optional, use `.env.local` instead)

4. Choose exposure:
   - Variables starting with `NEXT_PUBLIC_` are automatically exposed to client
   - Other variables remain server-side only

### Checking Current Configuration

To verify your environment variables are loaded:

```bash
# In development, check console logs (server-side)
console.log('MCP Backend URL:', process.env.NEXT_PUBLIC_MCP_BACKEND_URL);

# NEVER log secret keys in production!
# For debugging, check variable existence only:
console.log('Clerk secret configured:', !!process.env.CLERK_SECRET_KEY);
```

## Common Issues

### Issue: Clerk authentication not working

**Cause**: Missing or incorrect Clerk keys

**Solution**:
1. Verify keys are set in `.env.local` (dev) or Vercel dashboard (production)
2. Check keys match your Clerk application (dev vs. production instance)
3. Ensure `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starts with `pk_`
4. Ensure `CLERK_SECRET_KEY` starts with `sk_`

### Issue: MCP backend requests failing

**Cause**: Incorrect or unreachable backend URL

**Solution**:
1. Verify `NEXT_PUBLIC_MCP_BACKEND_URL` is set correctly
2. For local dev, ensure MCP server is running on specified port
3. For production, verify backend URL is accessible and CORS is configured
4. Check browser console for network errors

### Issue: Environment variables not updating

**Cause**: Next.js caches environment variables

**Solution**:
1. **Local dev**: Restart the dev server (`npm run dev`)
2. **Vercel**: Redeploy the application after changing environment variables
3. Clear browser cache if public variables changed

### Issue: Variables work locally but not in Vercel

**Cause**: Variables not configured in Vercel dashboard

**Solution**:
1. Go to Vercel project → Settings → Environment Variables
2. Add all required variables with correct scope (Production/Preview)
3. Trigger new deployment to apply changes

## Validation Checklist

Before deploying, verify:

- [ ] All required variables are set
- [ ] Clerk keys match the correct environment (dev vs. prod)
- [ ] MCP backend URL is reachable from the deployment environment
- [ ] Secret keys are not committed to version control
- [ ] `.env.local` is in `.gitignore`
- [ ] Vercel environment variables are configured for Production and Preview
- [ ] Test authentication flow works in each environment
- [ ] API routes can reach the MCP backend

## Template Files

### `.env.local` Template (for local development)

```bash
# Copy this to .env.local and fill in your values

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_
CLERK_SECRET_KEY=sk_test_

# Clerk URLs (optional, these are defaults)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# MCP Backend
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000
```

### `.env.example` (checked into git)

See the `.env.example` file in the frontend root for a complete template with comments.

## Additional Resources

- [Next.js Environment Variables Documentation](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [Clerk Environment Variables Guide](https://clerk.com/docs/deployments/clerk-environment-variables)
- [Vercel Environment Variables Documentation](https://vercel.com/docs/projects/environment-variables)
