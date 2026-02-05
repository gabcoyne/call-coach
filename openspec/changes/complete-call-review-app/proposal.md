## Why

The Gong Call Coaching Agent has a fully functional MCP backend (database, Gong API integration, Claude analysis engine, 3 coaching tools), but the Next.js frontend is blocked by invalid Clerk authentication keys and missing implementation of core user-facing features. Users cannot access the coaching app because authentication fails on page load, and even with valid keys, critical features like call analysis viewing, rep dashboards, and search are incomplete. This change completes the frontend to deliver a production-ready call coaching application.

## What Changes

- **Fix Authentication**: Replace placeholder Clerk keys with valid credentials, configure Clerk application with email/password/Google auth, and set up manager/rep role metadata
- **Complete Call Analysis Viewer**: Implement full call detail page with transcript viewer, coaching insights display, dimension scores, and action items
- **Build Rep Dashboard**: Create performance overview with trend charts, recent calls list, coaching metrics, and role-based access (managers see all reps, reps see only themselves)
- **Implement Search & Filters**: Add call search with filters for date range, rep, call type, performance scores, and keyword search
- **Integrate MCP Backend**: Connect all frontend pages to FastMCP backend API endpoints for analyze_call, get_rep_insights, and search_calls tools
- **Complete Design System**: Finalize component library with coaching-specific UI elements (score cards, trend charts, insight cards, action items)
- **Prepare Vercel Deployment**: Configure environment variables, API routes, edge runtime settings, and deployment pipeline

## Capabilities

### New Capabilities
- `clerk-authentication`: Clerk-based authentication with email/password/Google OAuth and manager/rep RBAC using publicMetadata
- `call-analysis-viewer`: Full-featured call detail page displaying transcript, coaching insights, dimension scores, and actionable recommendations
- `rep-dashboard`: Performance dashboard with trend visualization, recent calls, metrics aggregation, and role-based data access
- `call-search`: Advanced search and filtering for calls by date, rep, type, performance, and keywords
- `mcp-backend-integration`: Frontend API client for FastMCP backend tools (analyze_call, get_rep_insights, search_calls)
- `coaching-design-system`: Reusable UI components for coaching data (score cards, charts, insights, action items)
- `vercel-deployment`: Production deployment configuration with environment management and API routing

### Modified Capabilities
<!-- No existing spec requirements are changing -->

## Impact

**Affected Code:**
- `frontend/.env.local`: Add valid Clerk keys (pk_test_*, sk_test_*)
- `frontend/app/layout.tsx`: Already has ClerkProvider, verify middleware config
- `frontend/app/calls/[callId]/page.tsx`: Complete call analysis viewer implementation
- `frontend/app/calls/[callId]/CallAnalysisViewer.tsx`: Build out full component with API integration
- `frontend/app/dashboard/page.tsx`: Manager dashboard with all reps
- `frontend/app/dashboard/[repEmail]/page.tsx`: Individual rep performance view
- `frontend/app/search/page.tsx`: Search interface with filters
- `frontend/lib/api/`: New directory for MCP backend API client
- `frontend/components/coaching/`: New coaching-specific components (ScoreCard, TrendChart, InsightCard, ActionItem)

**Dependencies:**
- Clerk Dashboard: Create application, get API keys, configure metadata schema
- MCP Backend: Must remain running on localhost:8000 (or deployed URL)
- Neon Database: Contains call data, coaching results, rubrics

**APIs:**
- New API routes: `/api/calls/[callId]`, `/api/reps/[email]/insights`, `/api/calls/search`
- MCP Backend Tools: `analyze_call`, `get_rep_insights`, `search_calls`

**Systems:**
- Vercel: Deployment target with environment variable configuration
- Clerk: Third-party auth service
