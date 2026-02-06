## ADDED Requirements

### Requirement: Vercel Project Configuration

The deployment SHALL create Vercel project with proper framework detection and build settings.

#### Scenario: Next.js framework detection

- **WHEN** connecting repository to Vercel
- **THEN** system auto-detects Next.js 15 framework and configures build command (`next build`) and output directory (`.next`)

#### Scenario: Root directory configuration

- **WHEN** deploying monorepo with frontend in subdirectory
- **THEN** system sets root directory to `frontend/` so Vercel builds from correct location

#### Scenario: Node.js version specification

- **WHEN** deploying application
- **THEN** system uses Node.js 20.x (LTS) as specified in `package.json` engines field

### Requirement: Environment Variables Management

The deployment SHALL securely manage environment variables across development, preview, and production environments.

#### Scenario: Production environment variables

- **WHEN** deploying to production
- **THEN** system loads environment variables: `MCP_BACKEND_URL`, `CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, and other production secrets

#### Scenario: Preview environment variables

- **WHEN** deploying PR preview
- **THEN** system uses separate preview environment variables pointing to staging MCP backend

#### Scenario: Development environment variables

- **WHEN** running locally
- **THEN** system loads from `.env.local` file with local development values

#### Scenario: Secret encryption

- **WHEN** storing sensitive variables in Vercel
- **THEN** system encrypts secrets at rest and only exposes to build/runtime environments

### Requirement: Preview Deployments for Pull Requests

The deployment SHALL automatically create preview deployments for every pull request.

#### Scenario: PR preview creation

- **WHEN** developer opens pull request
- **THEN** system automatically deploys preview build with unique URL (e.g., `pr-123-gong-coaching.vercel.app`)

#### Scenario: PR preview comments

- **WHEN** preview deployment completes
- **THEN** system posts comment on GitHub PR with preview URL and deployment status

#### Scenario: PR preview updates

- **WHEN** developer pushes new commits to PR
- **THEN** system redeploys preview with latest changes and updates PR comment

#### Scenario: Preview cleanup

- **WHEN** PR is closed or merged
- **THEN** system automatically deletes preview deployment after 7 days

### Requirement: Production Deployment Pipeline

The deployment SHALL deploy to production on merge to main branch with zero-downtime rollout.

#### Scenario: Automatic production deploy

- **WHEN** PR merges to main branch
- **THEN** system automatically triggers production build and deployment

#### Scenario: Build validation

- **WHEN** production build starts
- **THEN** system runs type checking (`tsc --noEmit`), linting (`eslint`), and tests before deploying

#### Scenario: Zero-downtime deployment

- **WHEN** deploying new version to production
- **THEN** system uses atomic deployment (new version receives traffic only after health checks pass)

#### Scenario: Instant rollback

- **WHEN** production deployment has issues
- **THEN** system allows instant rollback to previous deployment via Vercel dashboard or CLI

### Requirement: Custom Domain Configuration

The deployment SHALL support custom domain with HTTPS and automatic certificate management.

#### Scenario: Add custom domain

- **WHEN** configuring domain (e.g., `coaching.prefect.io`)
- **THEN** system provides DNS records (CNAME or A record) to configure

#### Scenario: SSL certificate provisioning

- **WHEN** domain DNS is configured
- **THEN** system automatically provisions Let's Encrypt SSL certificate and enforces HTTPS

#### Scenario: WWW redirect

- **WHEN** user visits `www.coaching.prefect.io`
- **THEN** system redirects to `coaching.prefect.io` (or vice versa based on preference)

### Requirement: Build Performance Optimization

The deployment SHALL optimize build time and bundle size for fast deployments and page loads.

#### Scenario: Incremental static regeneration

- **WHEN** deploying updates
- **THEN** system uses ISR to rebuild only changed pages, not entire site

#### Scenario: Image optimization

- **WHEN** serving images
- **THEN** system automatically optimizes images using Vercel Image Optimization (WebP format, responsive sizes)

#### Scenario: Bundle analysis

- **WHEN** running production build
- **THEN** system generates bundle analysis report showing JavaScript bundle sizes by route

### Requirement: Monitoring and Analytics

The deployment SHALL integrate monitoring and analytics for observability.

#### Scenario: Vercel Analytics

- **WHEN** user interacts with application
- **THEN** system tracks Core Web Vitals (LCP, FID, CLS) and page views in Vercel Analytics

#### Scenario: Error tracking

- **WHEN** runtime error occurs
- **THEN** system captures error with stack trace and user context (via Vercel Error Tracking or external tool)

#### Scenario: Performance insights

- **WHEN** viewing analytics dashboard
- **THEN** system shows p75 page load times, API route latencies, and slowest pages

### Requirement: Deployment Notifications

The deployment SHALL notify team members of deployment status via Slack or email.

#### Scenario: Deployment success notification

- **WHEN** production deployment succeeds
- **THEN** system sends Slack message to #engineering channel with deployment URL and commit info

#### Scenario: Deployment failure notification

- **WHEN** production deployment fails
- **THEN** system sends urgent Slack notification with build logs and error details

#### Scenario: Preview deployment ready

- **WHEN** PR preview finishes deploying
- **THEN** system posts preview URL in GitHub PR comments

### Requirement: Edge Functions for API Routes

The deployment SHALL use Vercel Edge Functions for API routes requiring low latency.

#### Scenario: Edge runtime configuration

- **WHEN** API route requires <50ms latency
- **THEN** system configures route to use Edge runtime instead of Node.js runtime

#### Scenario: Edge function limitations

- **WHEN** API route uses Node.js-specific APIs (fs, child_process)
- **THEN** system uses Node.js runtime (serverless function) instead of Edge runtime

### Requirement: Security Headers

The deployment SHALL configure security headers for production environment.

#### Scenario: Content Security Policy

- **WHEN** serving HTML pages
- **THEN** system includes CSP header restricting script sources to same-origin and trusted CDNs

#### Scenario: HSTS header

- **WHEN** serving responses over HTTPS
- **THEN** system includes Strict-Transport-Security header enforcing HTTPS for 1 year

#### Scenario: Frame protection

- **WHEN** serving pages
- **THEN** system includes X-Frame-Options: DENY to prevent clickjacking attacks
