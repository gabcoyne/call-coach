## 1. Clerk Authentication Setup (BLOCKER)

- [x] 1.1 Create Clerk application at dashboard.clerk.com with name "Gong Call Coaching"
- [x] 1.2 Enable email/password authentication method in Clerk Dashboard
- [x] 1.3 Enable Google OAuth authentication method in Clerk Dashboard
- [x] 1.4 Configure publicMetadata schema to include `role` field (string type)
- [x] 1.5 Copy publishable key (pk_test_*) and secret key (sk_test_*) from Clerk Dashboard
- [x] 1.6 Update frontend/.env.local with NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
- [x] 1.7 Update frontend/.env.local with CLERK_SECRET_KEY
- [x] 1.8 Restart Next.js dev server and verify app loads without authentication error
- [ ] 1.9 Create first test user via sign-up flow
- [ ] 1.10 Set publicMetadata.role = "manager" for first user in Clerk Dashboard

## 2. Coaching Design System Components

- [x] 2.1 Create frontend/components/coaching/ directory structure
- [x] 2.2 Create frontend/lib/colors.ts with coaching color palette constants (green/yellow/red for scores)
- [x] 2.3 Implement ScoreCard component with props: score, title, optional subtitle
- [x] 2.4 Add ScoreCard color logic: green (>=80), yellow (60-79), red (<60)
- [x] 2.5 Implement TrendChart component using Recharts LineChart with responsive sizing
- [x] 2.6 Add TrendChart support for multiple dimension series with legend
- [x] 2.7 Implement InsightCard component using Radix Accordion for collapsible content
- [x] 2.8 Add Lucide icons to InsightCard: CheckCircle for strengths, AlertCircle for improvements
- [x] 2.9 Implement ActionItem component with checkbox and priority badge (high/medium/low)
- [x] 2.10 Add ActionItem priority color coding: red (high), yellow (medium), blue (low)
- [ ] 2.11 Write unit tests for all coaching components using React Testing Library
- [ ] 2.12 Run accessibility audit on coaching components with axe-core

## 3. SWR Hooks for MCP Backend Integration

- [x] 3.1 Create frontend/lib/hooks/use-call-analysis.ts SWR hook
- [x] 3.2 Implement useCallAnalysis(callId) that calls mcpClient.analyzeCall
- [x] 3.3 Add Clerk auth token to MCPClient Authorization header
- [x] 3.4 Create frontend/lib/hooks/use-rep-insights.ts SWR hook
- [x] 3.5 Implement useRepInsights(email, timeRange) that calls mcpClient.getRepInsights
- [x] 3.6 Add role-based access check: reps can only fetch their own email
- [x] 3.7 Create frontend/lib/hooks/use-search-calls.ts SWR hook
- [x] 3.8 Implement useSearchCalls(filters) that calls mcpClient.searchCalls with debounced keyword
- [x] 3.9 Configure SWR revalidation intervals: 5 minutes for historical data
- [x] 3.10 Add error handling and retry logic to all hooks

## 4. Call Analysis Viewer Page

- [x] 4.1 Update frontend/app/calls/[callId]/page.tsx to use useCallAnalysis hook
- [x] 4.2 Implement call metadata section: title, participants, date, duration, type
- [x] 4.3 Implement transcript viewer with speaker labels and timestamps
- [x] 4.4 Add "Transcript not available" fallback when transcript is null
- [x] 4.5 Implement coaching insights section organized by dimension
- [x] 4.6 Display dimension scores using ScoreCard components
- [x] 4.7 Display strengths and improvement areas using InsightCard components
- [x] 4.8 Display action items using ActionItem components
- [x] 4.9 Add "Analyze this call" button when call not yet analyzed
- [x] 4.10 Implement loading skeletons for metadata, transcript, and insights sections
- [x] 4.11 Implement error boundary with retry button
- [x] 4.12 Add responsive layout for mobile/tablet/desktop viewports

## 5. Rep Dashboard Pages

- [x] 5.1 Update frontend/app/dashboard/page.tsx for manager view (all reps list)
- [x] 5.2 Implement manager dashboard table with rep name, email, average scores, recent activity
- [x] 5.3 Add click handler to navigate to individual rep dashboard
- [x] 5.4 Hide manager dashboard features for rep role users
- [x] 5.5 Update frontend/app/dashboard/[repEmail]/page.tsx to use useRepInsights hook
- [x] 5.6 Implement performance overview section with average scores and total calls
- [x] 5.7 Display performance trend charts using TrendChart component
- [x] 5.8 Add "Not enough data" message when rep has fewer than 3 calls
- [x] 5.9 Display recent calls list (10 most recent) with date, type, score, and link
- [x] 5.10 Implement aggregated metrics: average dimension scores and call type distribution
- [x] 5.11 Add time range filter dropdown (7 days, 30 days, 90 days, all time)
- [x] 5.12 Implement role-based access check: rep users return 403 for other reps' dashboards
- [x] 5.13 Add loading skeletons for metrics and charts
- [x] 5.14 Implement error handling with retry button

## 6. Search and Filter Page

- [x] 6.1 Update frontend/app/search/page.tsx to use useSearchCalls hook
- [x] 6.2 Implement date range filter with start and end date pickers
- [x] 6.3 Add validation: end date must be after start date
- [x] 6.4 Implement rep filter dropdown (manager only, hidden for reps)
- [x] 6.5 Implement call type filter with multi-select (discovery, demo, follow-up)
- [x] 6.6 Implement minimum score filter with slider input (0-100)
- [x] 6.7 Implement keyword search input with 300ms debounce using lodash.debounce
- [x] 6.8 Add controlled form state using React useState for all filters
- [x] 6.9 Submit search on any filter change
- [x] 6.10 Implement "Clear filters" button to reset all filters
- [x] 6.11 Display search results table with date, rep, type, score, and link
- [x] 6.12 Add pagination controls for results over 20 items
- [x] 6.13 Display "No calls match your filters" message when results empty
- [x] 6.14 Add loading spinner during search execution
- [x] 6.15 Implement error handling with retry button

## 7. Role-Based Access Control

- [x] 7.1 Extract user role from auth().sessionClaims.metadata.role in page components
- [x] 7.2 Implement frontend role check utility function: isManager(role)
- [x] 7.3 Conditionally render manager-only features based on role
- [x] 7.4 Add 403 error page for unauthorized access attempts
- [x] 7.5 Test manager role: verify access to all reps' data
- [x] 7.6 Test rep role: verify access restricted to own data only
- [x] 7.7 Document role assignment process in CLERK_SETUP.md

## 8. Responsive Design and Accessibility

- [ ] 8.1 Test all pages on mobile viewport (<768px width)
- [ ] 8.2 Verify components stack vertically and adjust font sizes on mobile
- [ ] 8.3 Test all pages on tablet viewport (768-1024px width)
- [ ] 8.4 Verify 2-column grid layout on tablet where appropriate
- [ ] 8.5 Test all pages on desktop viewport (>1024px width)
- [ ] 8.6 Verify 3-column grid layout on desktop where appropriate
- [ ] 8.7 Run axe DevTools accessibility audit on all pages
- [ ] 8.8 Fix any color contrast issues (minimum 4.5:1 ratio)
- [ ] 8.9 Verify keyboard navigation works for all interactive elements
- [ ] 8.10 Add ARIA labels to all components for screen reader support

## 9. Testing and Quality Assurance

- [ ] 9.1 Write unit tests for ScoreCard component
- [ ] 9.2 Write unit tests for TrendChart component
- [ ] 9.3 Write unit tests for InsightCard component
- [ ] 9.4 Write unit tests for ActionItem component
- [ ] 9.5 Write unit tests for useCallAnalysis hook
- [ ] 9.6 Write unit tests for useRepInsights hook
- [ ] 9.7 Write unit tests for useSearchCalls hook
- [ ] 9.8 Test call analysis viewer with real coaching data from backend
- [ ] 9.9 Test dashboard with multiple reps and various data scenarios
- [ ] 9.10 Test search with all filter combinations
- [ ] 9.11 Run npm run test:coverage and verify >80% coverage
- [ ] 9.12 Fix any failing tests or bugs identified

## 10. Vercel Deployment Configuration

- [ ] 10.1 Connect GitHub repository to Vercel account
- [ ] 10.2 Configure Vercel project settings: framework (Next.js), root directory (frontend/)
- [ ] 10.3 Add production environment variable: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (pk_live_*)
- [ ] 10.4 Add production environment variable: CLERK_SECRET_KEY (sk_live_*)
- [ ] 10.5 Add production environment variable: NEXT_PUBLIC_MCP_BACKEND_URL (production backend URL)
- [ ] 10.6 Add production environment variable: NEXT_PUBLIC_APP_URL (https://coaching.prefect.io)
- [ ] 10.7 Configure custom domain: coaching.prefect.io pointing to Vercel
- [ ] 10.8 Enable Vercel Analytics in project settings
- [x] 10.9 Configure security headers in vercel.json: CSP, HSTS, X-Frame-Options
- [ ] 10.10 Deploy to staging (automatic preview deployment from branch)
- [ ] 10.11 Smoke test staging deployment: sign-in, view dashboard, search calls
- [ ] 10.12 Promote staging to production via Vercel dashboard
- [ ] 10.13 Verify production deployment at coaching.prefect.io
- [ ] 10.14 Monitor Vercel logs for first 24 hours post-deployment

## 11. Documentation and Handoff

- [ ] 11.1 Update README.md with Clerk setup instructions
- [ ] 11.2 Document manager role assignment process
- [ ] 11.3 Create troubleshooting guide for common issues
- [ ] 11.4 Document environment variable requirements for each environment
- [ ] 11.5 Add monitoring and alerting recommendations
- [ ] 11.6 Create user guide for managers and reps
- [ ] 11.7 Schedule demo/training session with sales leadership
