## Context

The Gong Call Coaching Agent project consists of a Python FastMCP backend that provides three coaching tools (analyze_call, get_rep_insights, search_calls) and a Next.js 15 frontend with App Router. The backend is fully operational with database, Gong API, and Claude integration. The frontend has scaffolded pages and components but requires:

1. Valid Clerk authentication credentials (currently placeholder keys block app load)
2. Complete implementation of page components with MCP backend integration
3. Coaching-specific design system components for data visualization
4. Vercel deployment configuration

**Current State:**
- Frontend: Next.js 15.1.6, React 19, TypeScript, Tailwind CSS, Clerk SDK installed
- Layout: ClerkProvider configured, navigation sidebar/mobile components exist
- Middleware: Route protection configured for /dashboard, /calls, /search
- MCP Client: Exists at `frontend/lib/mcp-client.ts` with retry logic, exponential backoff, TypeScript interfaces
- Components: Partial implementations in `frontend/components/{call-viewer,dashboard,search,ui}`
- Backend: Running on localhost:8000 with 3 tools, types defined in mcp-client.ts

**Constraints:**
- Must use Clerk for auth (already integrated, need valid keys)
- Backend URL configured via NEXT_PUBLIC_MCP_BACKEND_URL environment variable
- Must support manager/rep RBAC via Clerk publicMetadata.role
- Recharts library already installed for trend visualization
- SWR already installed for data fetching with automatic caching

**Stakeholders:**
- Prefect sales teams (managers and reps) consuming coaching insights
- Backend MCP server (dependency)
- Vercel platform (deployment target)

## Goals / Non-Goals

**Goals:**
- Unblock frontend app load by configuring valid Clerk credentials
- Complete all page implementations with full MCP backend integration
- Build reusable coaching design system components (ScoreCard, TrendChart, InsightCard, ActionItem)
- Implement role-based access control (managers see all reps, reps see only themselves)
- Configure Vercel deployment with proper environment variables and API routes
- Ensure responsive design works on mobile, tablet, and desktop
- Meet WCAG 2.1 AA accessibility standards for all components

**Non-Goals:**
- Modifying backend MCP server architecture or tools
- Implementing real-time features (websockets, server-sent events)
- Building admin panel for user management (Clerk Dashboard handles this)
- Creating alternative authentication providers beyond Clerk
- Implementing offline support or PWA features
- Multi-language internationalization (English only for now)

## Decisions

### 1. Clerk Authentication Setup

**Decision:** Manually create Clerk application and configure keys via environment variables rather than programmatic setup.

**Rationale:**
- Clerk Dashboard provides UI for key management, OAuth provider setup, and user metadata schema
- Environment variable approach matches Next.js best practices and supports dev/staging/prod environments
- Manual setup is one-time operation, automation adds complexity without significant benefit

**Alternatives Considered:**
- Programmatic Clerk setup via API: Rejected due to additional API key management and limited benefit
- Alternative auth providers (Auth0, Supabase Auth): Rejected because Clerk is already integrated

**Implementation:**
1. Create Clerk application via dashboard.clerk.com
2. Enable email/password and Google OAuth
3. Configure publicMetadata schema with `role` field (string: "manager" | "rep")
4. Add keys to `frontend/.env.local` for development
5. Add keys to Vercel environment variables for production

### 2. API Integration Architecture

**Decision:** Use existing MCPClient class with SWR hooks for data fetching, no API route proxies.

**Rationale:**
- MCPClient already implements retry logic, error handling, and TypeScript types
- SWR provides automatic caching, revalidation, and optimistic updates
- Direct frontend-to-backend communication minimizes latency (no extra hop through API routes)
- MCP backend already handles CORS and authentication

**Alternatives Considered:**
- Next.js API routes as proxy: Rejected due to added latency, complexity, and no security benefit (backend already secured)
- React Query: Rejected because SWR is already installed and team-familiar
- Server Components with direct backend calls: Rejected because coaching data requires dynamic user context (role-based access)

**Implementation:**
1. Create SWR hooks for each page:
   - `useCallAnalysis(callId)` → analyzeCall tool
   - `useRepInsights(email, timeRange)` → getRepInsights tool
   - `useSearchCalls(filters)` → searchCalls tool
2. Pass Clerk auth token via Authorization header in MCPClient
3. Handle loading/error states in UI with existing SWR patterns

### 3. Role-Based Access Control (RBAC)

**Decision:** Enforce RBAC at both frontend (UI hiding) and backend (data filtering) layers.

**Rationale:**
- Frontend RBAC improves UX by hiding unauthorized features
- Backend RBAC ensures security even if frontend is bypassed
- Clerk publicMetadata.role provides single source of truth for roles

**Alternatives Considered:**
- Frontend-only RBAC: Rejected due to security concerns (API endpoints exploitable)
- Database roles table: Rejected because Clerk metadata is already authoritative source
- Permission-based system (vs role-based): Rejected due to simple two-role model (manager/rep)

**Implementation:**
1. Frontend: Use `auth().sessionClaims.metadata.role` to conditionally render manager features
2. Backend: MCP tools filter data by rep_email based on role from Clerk token
3. Rep users: Automatically filter to their own email (extracted from Clerk token)
4. Manager users: Can access any rep's data via email parameter

### 4. Design System Component Library

**Decision:** Build custom coaching components using Radix UI primitives and Tailwind rather than full design system library (Shadcn UI, Chakra UI).

**Rationale:**
- Project already uses Radix UI for base primitives (label, slot, select)
- Custom components allow coaching-specific design patterns (score colors, priority badges)
- Tailwind provides rapid styling without external CSS-in-JS dependencies
- Smaller bundle size compared to full design systems

**Alternatives Considered:**
- Shadcn UI: Rejected because it's component-by-component copy-paste, not a runtime dependency (doesn't reduce code)
- Chakra UI: Rejected due to larger bundle size and CSS-in-JS overhead
- Material UI: Rejected due to opinionated design that doesn't match coaching UX needs

**Implementation:**
1. ScoreCard: Tailwind-styled div with conditional bg-green/yellow/red based on score threshold
2. TrendChart: Recharts LineChart with multiple series, responsive sizing via Tailwind breakpoints
3. InsightCard: Radix Accordion for collapsible insights, Lucide icons for strengths/improvements
4. ActionItem: Checkbox with priority badge (bg-red-500/yellow-500/blue-500)
5. Color palette constants in `frontend/lib/colors.ts` for consistency

### 5. Search and Filtering Strategy

**Decision:** Use controlled form state with React state and submit-on-change behavior, debounce keyword search input.

**Rationale:**
- Instant feedback improves UX (users see results as they filter)
- Debouncing keyword input prevents excessive API calls
- Controlled state enables "Clear filters" button functionality

**Alternatives Considered:**
- Uncontrolled form with submit button: Rejected due to poor UX (requires extra click)
- URL query params for filter state: Considered but deferred (requires more setup, not critical for v1)
- Client-side filtering: Rejected because backend has indexed search and pagination

**Implementation:**
1. Form state: React useState for each filter (dateRange, repEmail, callType, minScore, keyword)
2. Debounce: Use lodash.debounce (already in dependencies) for keyword input (300ms delay)
3. Submit: Call `searchCalls(filters)` via SWR on any filter change
4. Clear: Reset all state to default values

### 6. Vercel Deployment Configuration

**Decision:** Use Vercel Environment Variables UI for secrets, edge runtime for API routes if needed, standard deployment workflow.

**Rationale:**
- Vercel UI provides secure secret management with preview/production separation
- Edge runtime reduces cold start latency if API routes are added later
- Standard workflow (Git push → auto-deploy) matches team practices

**Alternatives Considered:**
- Vercel KV for session storage: Rejected because Clerk handles sessions
- Self-hosted deployment (AWS, GCP): Rejected due to increased ops burden vs Vercel's managed platform

**Implementation:**
1. Set environment variables in Vercel dashboard:
   - Production: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (pk_live_*), `CLERK_SECRET_KEY` (sk_live_*)
   - Preview: Same as production or separate test keys
2. Configure custom domain: coaching.prefect.io → Vercel production
3. Enable Vercel Analytics for performance monitoring
4. No API routes needed initially (direct MCPClient calls), but edge runtime configured for future use

## Risks / Trade-offs

### Risk: Clerk rate limits during high traffic
**Mitigation:** Clerk free tier supports 10k MAU; Prefect sales team ~50 users. Monitor usage via Clerk dashboard. Upgrade to paid plan if approaching limits.

### Risk: MCP backend downtime blocks entire frontend
**Mitigation:** SWR stale-while-revalidate caching provides graceful degradation. Display cached data with "Trying to reconnect" message. Add backend health check endpoint for monitoring.

### Risk: Large coaching analysis responses cause slow page loads
**Mitigation:** MCPClient implements 30s timeout. Backend already optimizes via caching (60-80% cache hit rate). Lazy-load transcript section on call detail page.

### Risk: Manager users accessing other reps' data creates privacy concerns
**Mitigation:** Document that manager role is intentionally privileged. Ensure only sales leadership gets manager role in Clerk metadata. Log access for audit trail (future enhancement).

### Risk: Recharts bundle size increases initial page load
**Mitigation:** Next.js automatically code-splits Recharts via dynamic imports. Charts only loaded on dashboard pages, not landing/search pages. Monitor bundle size with `npm run analyze`.

### Trade-off: No offline support
Coaching data requires real-time analysis from backend. Offline PWA would need service worker caching strategy, adding complexity. Team decision: online-only acceptable for sales tool used in office/remote with internet.

### Trade-off: No real-time updates
Using polling via SWR revalidation (default 2s) rather than websockets. Coaching analysis is async operation (10-30s), so real-time push not critical. Simplifies architecture and reduces backend complexity.

## Migration Plan

**Phase 1: Authentication Setup** (Blocker - 30 minutes)
1. Create Clerk application at dashboard.clerk.com
2. Enable email/password and Google OAuth providers
3. Copy publishable key (pk_test_*) and secret key (sk_test_*)
4. Update `frontend/.env.local` with real keys
5. Restart Next.js dev server (`npm run dev`)
6. Verify app loads without "Publishable key not valid" error
7. Create first test user, set publicMetadata.role = "manager" in Clerk Dashboard

**Phase 2: Component Implementation** (2-3 days)
1. Build design system components in `frontend/components/coaching/`:
   - ScoreCard.tsx, TrendChart.tsx, InsightCard.tsx, ActionItem.tsx
   - Write unit tests with React Testing Library
   - Verify accessibility with axe-core
2. Complete call analysis viewer page:
   - Implement `useCallAnalysis` SWR hook
   - Build out CallAnalysisViewer component with metadata, transcript, insights, scores
   - Add loading skeletons and error boundaries
3. Complete rep dashboard pages:
   - Implement `useRepInsights` SWR hook
   - Manager dashboard: List all reps with summary cards
   - Individual dashboard: Performance trends, recent calls, metrics
4. Complete search page:
   - Implement `useSearchCalls` SWR hook with debounced keyword filter
   - Build filter UI with date picker, dropdowns, score slider
   - Display results table with pagination

**Phase 3: Integration Testing** (1 day)
1. Test manager role: Verify access to all reps' data
2. Test rep role: Verify access restricted to own data only
3. Test all pages with real coaching data from backend
4. Verify responsive design on mobile/tablet/desktop viewports
5. Run accessibility audit with axe DevTools
6. Fix any bugs identified during testing

**Phase 4: Vercel Deployment** (1 day)
1. Connect GitHub repository to Vercel
2. Configure production environment variables (Clerk keys, MCP backend URL)
3. Deploy to staging URL (automatic preview deployment)
4. Smoke test staging deployment
5. Promote to production (coaching.prefect.io)
6. Monitor Vercel logs and analytics for first 24 hours

**Rollback Strategy:**
- Vercel supports instant rollback to previous deployment via dashboard (1-click, <1 minute)
- If Clerk issues: Revert .env keys to previous working keys
- If backend incompatibility: Frontend gracefully degrades with cached data and error messages

## Open Questions

1. **Manager role assignment process:** Who has authority to assign manager role in Clerk Dashboard? Need documented process for onboarding new managers.

2. **Analytics and monitoring:** What metrics should we track beyond Vercel Analytics? Consider: Page load times, API error rates, coaching tool usage by rep.

3. **Data retention:** How long should frontend cache coaching data via SWR? Current default: revalidate every 2 seconds. Consider longer intervals (5 minutes?) for historical data.

4. **Mobile app:** Is native mobile app (iOS/Android) needed, or is responsive web sufficient? Current design assumes responsive web only.

5. **Coaching notification system:** Should reps receive notifications when new coaching is available? Not in scope for v1, but may need email integration (SendGrid, Resend) in future.
