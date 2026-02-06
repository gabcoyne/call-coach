## Context

The Gong Call Coaching Agent currently provides powerful AI-powered coaching insights through an MCP backend with 3 tools: `analyze_call`, `get_rep_insights`, and `search_calls`. Access is limited to Claude Desktop or direct API calls, creating a barrier for sales teams who need self-service access to coaching data.

**Current State:**

- MCP backend deployed on FastMCP Cloud via Prefect Horizon
- Data stored in Neon PostgreSQL with coaching sessions, metrics, transcripts
- No web frontend - all access through MCP protocol
- Prefect branding assets available at prefect.io

**Constraints:**

- Must deploy to Vercel (specified requirement)
- Must use Prefect brand identity (colors, typography, assets)
- Must support role-based access (managers see all, reps see own data)
- Backend MCP server is Python-based, frontend will be TypeScript/React

**Stakeholders:**

- Sales managers: Primary users, need coaching insights for team
- Sales reps: Secondary users, want to see own performance
- Engineering team: Maintain both frontend and backend

## Goals / Non-Goals

**Goals:**

- Provide modern, elegant web UI for coaching insights with Prefect branding
- Enable self-service access to call analyses and rep performance data
- Support mobile-responsive design for access anywhere
- Deploy to Vercel with preview environments for PR-based workflow
- Integrate securely with MCP backend
- Launch MVP in 2-3 weeks with core features

**Non-Goals:**

- Real-time call analysis (use existing async processing)
- Mobile native apps (web responsive is sufficient)
- Video/audio playback of calls (link to Gong instead)
- Admin panel for managing users (use existing auth provider)
- White-labeling or multi-tenant support
- Offline-first functionality

## Decisions

### 1. Next.js 15 with App Router (Server Components)

**Decision**: Use Next.js 15 with App Router and React Server Components.

**Rationale**:

- Server Components reduce client bundle size for data-heavy coaching views
- Built-in API routes simplify backend integration without separate BFF
- Vercel-optimized (hosting platform requirement)
- App Router provides modern patterns (layouts, loading states, error boundaries)

**Alternatives Considered**:

- **Remix**: Strong data loading, but less Vercel-optimized, smaller ecosystem
- **Vite + React SPA**: Simpler but loses SSR benefits, SEO, and initial load performance
- **Next.js Pages Router**: Mature but older pattern, missing Server Components benefits

### 2. MCP Backend Integration via REST API Bridge

**Decision**: Create REST API endpoints in Next.js `/app/api/` that proxy to MCP backend using `@modelcontextprotocol/sdk`.

**Rationale**:

- Web browsers can't natively speak MCP protocol (requires stdio/SSE transports)
- Next.js API routes provide secure server-side bridge
- Keeps auth tokens and MCP credentials server-side (never exposed to browser)
- Simplifies client code (standard fetch/SWR instead of MCP client)

**Architecture**:

```
Browser → Next.js API Routes → MCP SDK Client → FastMCP Server
   (fetch)     (proxies)           (MCP protocol)    (tools)
```

**Alternatives Considered**:

- **Direct MCP from Browser**: Not feasible - MCP requires stdio/SSE, browsers can't connect
- **Separate BFF Service**: Overengineering for MVP, adds deployment complexity
- **GraphQL Gateway**: Overkill for simple CRUD operations, adds learning curve

### 3. Monorepo Structure with Turborepo

**Decision**: Create `frontend/` directory within existing `call-coach` repo, use Turborepo for monorepo management.

**Rationale**:

- Keeps frontend and backend code colocated for easier cross-team changes
- Turborepo provides fast builds, caching, and task orchestration
- Single repo simplifies deployment coordination (shared types, OpenSpec changes)
- Existing repo already has beads, OpenSpec, knowledge base

**Structure**:

```
call-coach/
├── frontend/              # Next.js app (this change)
│   ├── app/               # Next.js 15 App Router
│   ├── components/        # React components
│   ├── lib/               # Utilities, MCP client
│   └── package.json
├── coaching_mcp/          # MCP backend (existing)
├── db/                    # Database schema (existing)
├── package.json           # Root package.json with workspaces
└── turbo.json             # Turborepo config
```

**Alternatives Considered**:

- **Separate Git Repo**: Harder to coordinate changes, duplicate OpenSpec/beads setup
- **No Monorepo Tool**: Manual dependency management, slower builds, no caching

### 4. Prefect Design System with Tailwind CSS + Shadcn/ui

**Decision**: Build custom Prefect design system using Tailwind CSS + Shadcn/ui components.

**Rationale**:

- Tailwind provides utility-first styling, easy to customize with Prefect colors
- Shadcn/ui gives accessible, unstyled components we can brand
- Prefect.io uses similar stack (easy to extract colors/typography)
- No dependency on external UI library updates/breaking changes

**Prefect Brand Integration**:

- Colors: Extract from prefect.io CSS (primary blue, accent colors)
- Typography: Use Prefect's font stack (likely Inter or similar)
- Components: Build on Shadcn/ui, style with Prefect aesthetics
- Logos/assets: Download from prefect.io or use Prefect brand kit

**Alternatives Considered**:

- **Material UI**: Heavy, opinionated styles, hard to customize to Prefect brand
- **Ant Design**: Enterprise-focused, not modern enough aesthetic
- **Chakra UI**: Good but adds runtime overhead vs. compile-time Tailwind

### 5. Clerk for Authentication

**Decision**: Use Clerk for authentication and user management.

**Rationale**:

- Handles sign-up, login, session management, password reset out-of-box
- Built-in role-based access control (managers vs. reps)
- Next.js middleware integration for route protection
- Vercel-optimized, scales automatically
- Free tier sufficient for MVP (up to 5K monthly active users)

**User Roles**:

- `manager`: Can view all reps, all calls, team-wide insights
- `rep`: Can view only own calls and performance data

**Alternatives Considered**:

- **NextAuth.js**: More setup required, need to manage user DB, no built-in RBAC
- **Auth0**: More expensive, heavier integration, overkill for use case
- **Custom JWT Auth**: Significant engineering effort, security risk, slow MVP

### 6. SWR for Data Fetching and Caching

**Decision**: Use SWR (stale-while-revalidate) for client-side data fetching and caching.

**Rationale**:

- Optimistic UI updates with automatic revalidation
- Built-in loading/error states, retry logic
- Request deduplication (avoids redundant API calls)
- Prefetch and mutation patterns for smooth UX
- Lightweight, well-maintained by Vercel

**Alternatives Considered**:

- **React Query**: Feature-rich but heavier, SWR sufficient for needs
- **Apollo Client**: GraphQL-specific, we're using REST API bridge
- **Native fetch**: No caching, loading states, or revalidation logic

### 7. Recharts for Data Visualization

**Decision**: Use Recharts for performance trend charts and metrics visualization.

**Rationale**:

- React-native, composable API (easy to customize)
- Good TypeScript support
- Covers all chart types needed (line, bar, radar for multi-dimensional scores)
- Lightweight compared to D3.js, easier learning curve

**Chart Types**:

- Line charts: Rep score trends over time
- Bar charts: Dimension comparisons (product knowledge, discovery, objections)
- Radar charts: Multi-dimensional skill assessments

**Alternatives Considered**:

- **Chart.js**: Imperative API, harder to integrate with React
- **D3.js**: Powerful but overkill, steep learning curve, large bundle
- **Nivo**: Beautiful but heavier, slower render for large datasets

## Risks / Trade-offs

### [Risk] MCP protocol changes break API bridge

**Mitigation**: Pin `@modelcontextprotocol/sdk` version, write adapter layer to isolate MCP client logic. Version bumps require testing.

### [Risk] Vercel cold starts delay API responses (>2s)

**Mitigation**: Use Vercel Edge Functions for API routes if latency is critical. Monitor p95 latency, add Vercel warm-up cron if needed.

### [Risk] Clerk free tier limits (5K MAU) exceeded

**Mitigation**: Monitor usage in Clerk dashboard. Budget for Clerk Pro ($25/mo) if team grows past 5K users. Unlikely for internal sales tool.

### [Risk] Prefect brand assets (logos, colors) not publicly available

**Mitigation**: Contact Prefect design team for brand kit. If unavailable, manually extract colors from prefect.io CSS and use placeholder logos until official assets provided.

### [Risk] Backend MCP server lacks CORS configuration for web clients

**Mitigation**: API bridge in Next.js handles all backend communication server-side, so CORS not needed. Browser never directly calls MCP server.

### [Risk] Large coaching datasets cause slow page loads

**Mitigation**: Implement pagination (20 calls per page), virtualized lists for large result sets, lazy load transcript snippets. Cache aggressively with SWR.

### [Trade-off] Server Components vs. Client Components

Server Components reduce bundle size but require more server round-trips. Use Server Components for data fetching, Client Components for interactive UI (filters, charts). Optimize with React Suspense boundaries.

### [Trade-off] Monorepo complexity

Monorepo adds Turborepo learning curve and workspace management. Benefit is colocated code and shared tooling. If friction increases, can extract frontend to separate repo later.

## Migration Plan

### Phase 1: Bootstrap (Week 1)

1. Add Turborepo to root `package.json`, create `turbo.json`
2. Create `frontend/` directory with Next.js 15 initialized
3. Install dependencies: Tailwind, Shadcn/ui, SWR, Recharts, Clerk
4. Extract Prefect brand colors/typography from prefect.io
5. Set up Vercel project and connect GitHub repo
6. Create development, preview, and production environments

### Phase 2: Core Features (Week 2)

1. Implement authentication with Clerk (sign up, login, RBAC)
2. Build MCP API bridge in `/app/api/coaching/*` routes
3. Create design system components (buttons, cards, layouts)
4. Implement call analysis viewer (fetch + display call details)
5. Implement rep performance dashboard (trends, charts)
6. Implement call search and filter UI

### Phase 3: Polish & Deploy (Week 3)

1. Mobile responsive design testing
2. Error handling and loading states
3. Performance optimization (bundle analysis, image optimization)
4. Security audit (auth flows, API validation)
5. Deploy to production Vercel environment
6. User acceptance testing with sales team

### Rollback Strategy

- Vercel instant rollbacks to previous deployment via dashboard
- Feature flags for gradual rollout (if needed)
- Backend MCP server unchanged, so frontend rollback has no backend impact

## Open Questions

1. **Auth Provider Integration**: Should we sync Clerk users with Prefect's existing auth system, or is Clerk independent? Need to clarify if reps/managers already have Prefect accounts.

2. **Domain Configuration**: What domain/subdomain should frontend use? Options: `coaching.prefect.io`, `calls.prefect.io`, or separate domain?

3. **Analytics/Monitoring**: Should we add PostHog, Mixpanel, or similar for usage analytics? Or rely on Vercel Analytics?

4. **Database Access**: Should frontend directly query Neon PostgreSQL for better performance, or always go through MCP backend? Direct DB access would reduce latency but bypasses backend caching.

5. **Prefect Brand Assets**: Who owns Prefect brand kit? Need contact for official logos, color palette, typography specs.
