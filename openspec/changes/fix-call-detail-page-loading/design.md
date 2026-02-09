# Design: Fix Call Detail Page Loading

## Context

The call detail page uses Next.js 14 App Router with a server component wrapper (`page.tsx`) that renders a client component (`CallAnalysisViewer.tsx`). The client component uses SWR hooks to fetch call analysis data from `/api/coaching/analyze-call`.

**Current State:**

- API route handler exists with both GET and POST methods
- Backend MCP server returns valid data when tested directly
- Frontend shows infinite loading (skeleton loaders)
- SWR hook instantiates but never triggers fetch
- Authentication via Clerk with cookie-based sessions

**Investigation Findings:**

- Manual curl to API returns HTML (not authenticated)
- Browser DevTools shows no network request to analyze-call endpoint
- Multiple SWR hook rewrites attempted (inline fetcher, config fetcher, etc.)
- Database has separate UUID type issue in coaching-sessions endpoint

**Constraints:**

- Must maintain Clerk authentication flow
- Cannot break existing working pages (calls list, dashboard)
- Must work with SSR/CSR boundaries in Next.js App Router
- SWR patterns must match working examples (e.g., use-current-user.ts)

## Goals / Non-Goals

**Goals:**

- Call detail page loads and displays analysis data from backend
- Proper loading states and error handling for users
- Authentication works correctly for API routes accessed via SWR
- Fix UUID type mismatch in coaching-sessions endpoint
- Establish debugging patterns for similar issues

**Non-Goals:**

- Rewrite entire authentication system
- Change SWR library or data fetching strategy
- Modify backend MCP tool implementations
- Add real-time updates or WebSocket connections
- Optimize performance (focus on correctness first)

## Decisions

### Decision 1: Investigate Authentication Flow First

**Choice:** Focus on authentication boundary between SSR and client-side SWR fetching.

**Rationale:** The symptom (no network request) suggests SWR hook is blocked before attempting fetch, possibly by authentication state. Curl returning HTML indicates unauthenticated request hits Next.js's default behavior.

**Alternatives Considered:**

- Rewrite SWR hook again → Already attempted multiple times without success
- Use different data fetching library → Would require extensive refactoring
- Server-side data fetching only → Loses benefits of SWR caching and revalidation

**Why this approach:** Authentication mismatch is the most likely root cause given curl vs browser behavior difference.

### Decision 2: Use Chrome DevTools MCP for Debugging

**Choice:** Leverage Chrome DevTools MCP server to inspect actual browser state, network activity, and React component lifecycle.

**Rationale:** We have Chrome DevTools MCP available and integrated. Can programmatically inspect:

- Network requests (or lack thereof)
- React component state and props
- Clerk authentication state in browser
- Console errors and warnings

**Alternatives Considered:**

- Manual browser debugging → Time-consuming, hard to document
- Add extensive logging to code → Pollutes codebase with debug code

**Why this approach:** MCP tools provide systematic, repeatable investigation that can be documented in specs.

### Decision 3: Separate Concerns - Fix UUID Issue Independently

**Choice:** Fix coaching-sessions UUID type error as a separate, atomic change.

**Rationale:** The UUID issue is unrelated to SWR fetching problem. Call IDs from Gong are numeric strings, but database schema expects UUID type.

**Solution:** Add type conversion or change schema to use TEXT/BIGINT for call_id column.

**Alternatives Considered:**

- Fix both issues together → Increases complexity and risk
- Ignore UUID issue → Blocks coaching sessions feature

**Why this approach:** Atomic changes are easier to test and revert if needed.

### Decision 4: Match Working SWR Pattern Exactly

**Choice:** Compare byte-for-byte with use-current-user.ts (known working example) and identify any differences.

**Rationale:** If another hook works with same authentication setup, the pattern difference is the bug.

**Alternatives Considered:**

- Keep trying random SWR configurations → Already failed multiple times
- Use fetch directly without SWR → Loses caching benefits

**Why this approach:** Working code is the best specification.

## Risks / Trade-offs

**Risk 1: Authentication Architecture Issues**

- If Clerk integration has fundamental SSR/CSR boundary issues, fix may require extensive refactoring
- **Mitigation:** Test with Chrome DevTools to confirm auth state before making changes. If deep issue found, escalate to architectural review.

**Risk 2: SWR Version Incompatibility**

- SWR v2.x may have breaking changes or bugs with Next.js 14 App Router
- **Mitigation:** Check SWR GitHub issues for similar problems. Consider downgrading or upgrading if pattern issue found.

**Risk 3: Database Schema Change Impact**

- Changing call_id from UUID to BIGINT affects all queries and foreign keys
- **Mitigation:** Use database migration with rollback plan. Test on staging database first.

**Risk 4: Breaking Other Pages**

- Changes to authentication flow or SWR config could break working pages
- **Mitigation:** Run full test suite before committing. Manual smoke test of calls list, dashboard, and other SWR-using pages.

## Migration Plan

**Phase 1: Investigation (Chrome DevTools)**

1. Start browser with Chrome DevTools MCP connected
2. Navigate to call detail page
3. Inspect network tab for missing requests
4. Check React component state and props
5. Verify Clerk authentication cookies present
6. Document findings in investigation notes

**Phase 2: Fix Authentication Boundary**

1. Compare useCallAnalysis with use-current-user.ts line-by-line
2. Identify pattern differences
3. Apply working pattern to useCallAnalysis
4. Test in browser with DevTools monitoring
5. Verify network request appears and returns data

**Phase 3: Fix UUID Type Issue**

1. Create database migration to change call_id column type
2. Update TypeScript types to match
3. Test coaching-sessions endpoint with numeric call ID
4. Verify query returns results without type errors

**Phase 4: Validation**

1. Run frontend test suite (61 tests must pass)
2. Manual smoke test: calls list → call detail → analysis loads
3. Check error states: invalid call ID, network error, etc.
4. Verify other SWR hooks still work (user profile, calls list)

**Rollback Strategy:**

- Database migration has down() function to revert schema change
- Git revert commits if authentication changes break other pages
- Feature flag to serve old page version if needed (add if high risk)

## Open Questions

1. **Why does curl return HTML instead of 401/403?**

   - Expected: Unauthenticated API request should return JSON error
   - Actual: Returns full HTML page (Next.js default behavior)
   - Investigation needed: Check withAuth middleware implementation

2. **Why does SWR hook not trigger fetch at all?**

   - SWR should attempt fetch and fail, not silently do nothing
   - Possible: Hook is disabled by some condition we're not seeing
   - Possible: URL is null or malformed, causing SWR to skip fetch
   - Investigation: Add console.log to hook to trace execution

3. **Are there other pages with UUID type issues?**

   - Only coaching-sessions found so far
   - Should audit all API routes for similar assumptions
   - May need systematic fix if pattern is widespread

4. **Is Clerk SSR setup correct?**
   - Clerk docs have specific Next.js 14 App Router guidance
   - May need to verify middleware.ts configuration
   - Check if other apps using Clerk + SWR + App Router have solved this
