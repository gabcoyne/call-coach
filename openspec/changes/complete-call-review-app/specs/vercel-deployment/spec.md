## ADDED Requirements

### Requirement: Environment variable configuration

The system SHALL support deployment-specific environment variables for Vercel environments.

#### Scenario: Production environment variables

- **WHEN** application is deployed to Vercel production
- **THEN** the system uses production Clerk keys (pk*live\*\*, sk*live\*\*) and production MCP backend URL

#### Scenario: Preview environment variables

- **WHEN** application is deployed to Vercel preview
- **THEN** the system uses test Clerk keys (pk*test\*\*, sk*test\*\*) and staging MCP backend URL

#### Scenario: Development environment variables

- **WHEN** application runs locally via npm run dev
- **THEN** the system uses .env.local file with local configuration

### Requirement: API route configuration

The system SHALL configure API routes to proxy requests to MCP backend.

#### Scenario: API route receives request

- **WHEN** frontend makes request to /api/calls/[callId]
- **THEN** the API route forwards request to MCP backend at $NEXT_PUBLIC_MCP_BACKEND_URL/analyze_call

#### Scenario: API route adds authentication

- **WHEN** API route forwards request
- **THEN** the route includes Clerk authentication token in backend request

#### Scenario: API route handles errors

- **WHEN** MCP backend returns error
- **THEN** the API route returns appropriate HTTP status code and error message

### Requirement: Edge runtime for API routes

The system SHALL use Next.js Edge Runtime for API routes to minimize cold start latency.

#### Scenario: API route cold start

- **WHEN** API route receives first request after idle period
- **THEN** the route responds within 500ms (Edge Runtime)

#### Scenario: API route warm response

- **WHEN** API route receives request with warm runtime
- **THEN** the route responds within 100ms

### Requirement: Deployment build configuration

The system SHALL configure Next.js build settings for optimal Vercel deployment.

#### Scenario: Production build

- **WHEN** Vercel runs production build
- **THEN** Next.js generates optimized static pages and API routes

#### Scenario: Build caching

- **WHEN** Vercel detects no code changes
- **THEN** the build process uses cached dependencies and assets

### Requirement: Security headers

The system SHALL configure security headers for production deployment.

#### Scenario: Content Security Policy

- **WHEN** application serves pages in production
- **THEN** responses include CSP header restricting script sources

#### Scenario: HTTPS enforcement

- **WHEN** user accesses site via HTTP
- **THEN** Vercel redirects to HTTPS

#### Scenario: HSTS header

- **WHEN** application serves pages
- **THEN** responses include Strict-Transport-Security header

### Requirement: CORS configuration

The system SHALL configure CORS headers for API routes.

#### Scenario: Same-origin API request

- **WHEN** frontend makes API request to same domain
- **THEN** the request succeeds without CORS restrictions

#### Scenario: Cross-origin preflight

- **WHEN** browser sends OPTIONS preflight request
- **THEN** API route returns appropriate Access-Control-Allow-\* headers

### Requirement: Deployment preview URLs

The system SHALL generate unique preview URLs for each pull request.

#### Scenario: PR deployment

- **WHEN** a pull request is opened or updated
- **THEN** Vercel generates preview URL at <branch>-<repo>.vercel.app

#### Scenario: Preview environment variables

- **WHEN** preview deployment is created
- **THEN** the deployment uses preview-specific environment variables

### Requirement: Production domain configuration

The system SHALL use custom domain for production deployment.

#### Scenario: Production URL

- **WHEN** application is deployed to production
- **THEN** the application is accessible at coaching.prefect.io

#### Scenario: DNS configuration

- **WHEN** user navigates to coaching.prefect.io
- **THEN** DNS resolves to Vercel production deployment

### Requirement: Monitoring and logging

The system SHALL integrate Vercel Analytics and logging.

#### Scenario: Page view tracking

- **WHEN** user visits any page
- **THEN** Vercel Analytics records page view with load time

#### Scenario: Error logging

- **WHEN** application throws runtime error
- **THEN** error is logged to Vercel logs with stack trace

### Requirement: Deployment rollback

The system SHALL support instant rollback to previous deployment.

#### Scenario: Rollback deployment

- **WHEN** production deployment has critical bug
- **THEN** administrator can rollback to previous deployment via Vercel dashboard within 1 minute
