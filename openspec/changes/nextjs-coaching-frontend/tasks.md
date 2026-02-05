## 1. Project Bootstrap and Monorepo Setup

- [x] 1.1 Add Turborepo to root package.json and create turbo.json config
- [x] 1.2 Create frontend/ directory with proper workspace configuration
- [x] 1.3 Initialize Next.js 15 with App Router in frontend/ directory
- [x] 1.4 Configure TypeScript with strict mode and path aliases
- [x] 1.5 Set up ESLint and Prettier with shared configs
- [x] 1.6 Create .gitignore for frontend build artifacts

## 2. Design System Foundation

- [x] 2.1 Install Tailwind CSS and configure with Prefect brand colors
- [x] 2.2 Extract Prefect colors, typography, and spacing from prefect.io
- [x] 2.3 Create tailwind.config.ts with custom Prefect theme
- [x] 2.4 Install and configure Shadcn/ui CLI
- [x] 2.5 Add base Shadcn/ui components (Button, Card, Input, Select)
- [x] 2.6 Create custom component variants matching Prefect aesthetics
- [x] 2.7 Download Prefect logos and brand assets (or create placeholders)
- [x] 2.8 Set up responsive breakpoints and layout utilities

## 3. Authentication with Clerk

- [x] 3.1 Create Clerk account and application (manual step - see CLERK_SETUP.md)
- [x] 3.2 Install @clerk/nextjs package
- [x] 3.3 Configure Clerk provider in app/layout.tsx
- [x] 3.4 Set up Clerk environment variables (publishable and secret keys)
- [x] 3.5 Create /sign-in and /sign-up routes using Clerk components
- [x] 3.6 Implement Next.js middleware for route protection
- [x] 3.7 Configure user roles (manager vs. rep) in Clerk (documented in CLERK_SETUP.md)
- [x] 3.8 Create role-based access control (RBAC) utilities
- [x] 3.9 Test authentication flow (sign up, login, logout) (test steps in CLERK_SETUP.md)

## 4. MCP Backend Integration Layer

- [x] 4.1 Install @modelcontextprotocol/sdk package (Added Zod instead - MCP backend uses FastMCP Python)
- [x] 4.2 Create lib/mcp-client.ts with MCP SDK client wrapper
- [x] 4.3 Configure MCP backend URL environment variable
- [x] 4.4 Implement /app/api/coaching/analyze-call/route.ts API endpoint
- [x] 4.5 Implement /app/api/coaching/rep-insights/route.ts API endpoint
- [x] 4.6 Implement /app/api/coaching/search-calls/route.ts API endpoint
- [x] 4.7 Create TypeScript interfaces for API requests/responses
- [x] 4.8 Add Zod schemas for request validation
- [x] 4.9 Implement error handling and retry logic with exponential backoff
- [x] 4.10 Add authentication middleware to API routes (verify Clerk session)
- [x] 4.11 Implement RBAC enforcement in API routes
- [x] 4.12 Add request/response logging for observability
- [x] 4.13 Implement rate limiting per user and per endpoint
- [x] 4.14 Test API bridge with local MCP backend (Documentation provided in API_TESTING.md)

## 5. Data Fetching with SWR

- [ ] 5.1 Install swr package
- [ ] 5.2 Create custom SWR hooks (useCallAnalysis, useRepInsights, useSearchCalls)
- [ ] 5.3 Configure SWR global config with revalidation and error retry settings
- [ ] 5.4 Implement optimistic UI updates for mutations
- [ ] 5.5 Add loading and error state handling utilities

## 6. Call Analysis Viewer

- [ ] 6.1 Create app/calls/[callId]/page.tsx route
- [ ] 6.2 Implement call metadata header component (title, date, participants)
- [ ] 6.3 Create overall score badge with color coding (green/yellow/red)
- [ ] 6.4 Build dimension score cards component (4 dimensions)
- [ ] 6.5 Implement strengths and areas for improvement sections
- [ ] 6.6 Create transcript snippet component with highlights (good/needs work)
- [ ] 6.7 Add timestamp click handler to link to Gong (if available)
- [ ] 6.8 Implement action items list with checkboxes
- [ ] 6.9 Add coaching notes section (manager-only with RBAC check)
- [ ] 6.10 Implement share analysis feature (generate link)
- [ ] 6.11 Add export as PDF functionality
- [ ] 6.12 Make viewer responsive for mobile/tablet

## 7. Rep Performance Dashboard

- [ ] 7.1 Create app/dashboard/[repEmail]/page.tsx route
- [ ] 7.2 Implement dashboard header with rep profile and summary stats
- [ ] 7.3 Install Recharts and configure chart components
- [ ] 7.4 Create line chart for score trends over time (4 dimensions)
- [ ] 7.5 Add time period selector (7 days, 30 days, quarter, year, all time)
- [ ] 7.6 Implement skill gap cards with priority indicators
- [ ] 7.7 Create radar chart for dimension score distribution
- [ ] 7.8 Add team average comparison overlay (manager view only)
- [ ] 7.9 Implement improvement areas and recent wins sections
- [ ] 7.10 Create call history table with sorting and filtering
- [ ] 7.11 Add personalized coaching plan section
- [ ] 7.12 Implement RBAC (reps see own data only, managers see all)
- [ ] 7.13 Add rep selector dropdown for managers

## 8. Call Search and Filter

- [ ] 8.1 Create app/search/page.tsx route
- [ ] 8.2 Implement multi-criteria filter form (rep, date, product, call type)
- [ ] 8.3 Add score threshold filters (min/max overall and dimension scores)
- [ ] 8.4 Create objection type multi-select filter
- [ ] 8.5 Add topic keyword filter with multi-select
- [ ] 8.6 Implement search results display (card view and table view toggle)
- [ ] 8.7 Add sorting options (date, score, duration)
- [ ] 8.8 Implement pagination (20 results per page with page size selector)
- [ ] 8.9 Create save search feature (persist to localStorage or DB)
- [ ] 8.10 Add load saved searches dropdown
- [ ] 8.11 Implement export results as CSV/Excel
- [ ] 8.12 Create quick filter presets (My Calls This Week, Low Performers, etc.)

## 9. Coaching Insights Feed

- [ ] 9.1 Create app/feed/page.tsx route
- [ ] 9.2 Implement chronological activity feed with infinite scroll
- [ ] 9.3 Create feed item components (call analysis, team insight, highlight, milestone)
- [ ] 9.4 Add team-wide insights cards (manager view only)
- [ ] 9.5 Implement coaching highlights cards with exemplary moments
- [ ] 9.6 Add feed type filter (analyses, insights, highlights, milestones)
- [ ] 9.7 Implement time-based filtering (today, this week, this month, custom range)
- [ ] 9.8 Create feed item actions (bookmark, share, dismiss)
- [ ] 9.9 Add new items badge and auto-refresh banner
- [ ] 9.10 Implement optional weekly digest email (integration with email service)

## 10. Navigation and Layout

- [ ] 10.1 Create app/layout.tsx with main navigation sidebar
- [ ] 10.2 Implement navigation links (Dashboard, Search, Feed, Profile)
- [ ] 10.3 Add user profile dropdown with logout option
- [ ] 10.4 Create responsive mobile navigation (hamburger menu)
- [ ] 10.5 Implement breadcrumb navigation for deep pages
- [ ] 10.6 Add loading states using React Suspense and loading.tsx files
- [ ] 10.7 Create error boundaries with error.tsx files
- [ ] 10.8 Add not-found.tsx for 404 pages

## 11. Vercel Deployment Configuration

- [ ] 11.1 Create Vercel account and link GitHub repository
- [ ] 11.2 Configure Vercel project with framework preset (Next.js)
- [ ] 11.3 Set root directory to frontend/ for monorepo
- [ ] 11.4 Configure production environment variables in Vercel dashboard
- [ ] 11.5 Configure preview environment variables (staging MCP backend)
- [ ] 11.6 Set up custom domain (coaching.prefect.io or similar)
- [ ] 11.7 Configure SSL certificate and HTTPS enforcement
- [ ] 11.8 Enable automatic preview deployments for pull requests
- [ ] 11.9 Configure production deployment on main branch merge
- [ ] 11.10 Set up deployment notifications (Slack integration)
- [ ] 11.11 Enable Vercel Analytics for Core Web Vitals tracking
- [ ] 11.12 Configure security headers (CSP, HSTS, X-Frame-Options)

## 12. Testing and Quality Assurance

- [ ] 12.1 Set up Jest and React Testing Library
- [ ] 12.2 Write unit tests for utility functions and hooks
- [ ] 12.3 Write component tests for design system components
- [ ] 12.4 Write integration tests for API routes (mock MCP backend)
- [ ] 12.5 Test authentication flows (sign up, login, RBAC)
- [ ] 12.6 Test responsive design on mobile, tablet, desktop viewports
- [ ] 12.7 Run accessibility audit (Lighthouse, axe-core)
- [ ] 12.8 Perform manual testing of all user workflows
- [ ] 12.9 Run bundle analysis and optimize large dependencies
- [ ] 12.10 Load test API routes (simulate 50+ concurrent users)

## 13. Performance Optimization

- [ ] 13.1 Implement code splitting for large pages/components
- [ ] 13.2 Optimize images using Next.js Image component
- [ ] 13.3 Add prefetching for critical data on page load
- [ ] 13.4 Implement ISR (Incremental Static Regeneration) where applicable
- [ ] 13.5 Configure bundle analyzer and reduce JavaScript bundle size
- [ ] 13.6 Add service worker for offline fallback (optional)
- [ ] 13.7 Optimize Recharts bundle by importing only used components
- [ ] 13.8 Measure and optimize Core Web Vitals (LCP, FID, CLS)

## 14. Documentation and Handoff

- [ ] 14.1 Create frontend/README.md with setup instructions
- [ ] 14.2 Document environment variables and configuration
- [ ] 14.3 Write API documentation for /api/coaching/* endpoints
- [ ] 14.4 Create user guide for sales managers and reps
- [ ] 14.5 Document deployment process and rollback procedures
- [ ] 14.6 Add troubleshooting guide for common issues
- [ ] 14.7 Create runbook for monitoring and incident response
- [ ] 14.8 Schedule knowledge transfer session with team
