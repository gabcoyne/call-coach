# Call Coach Application Error Report

**Date**: 2026-02-05
**Environment**: Local Development (<http://localhost:3000>)
**User**: <george@prefect.io>

## Executive Summary

Navigation testing of the Call Coach application revealed **three categories of errors**:

1. **Critical Infrastructure Issue**: MCP backend server not running (ERR_CONNECTION_REFUSED)
2. **Application Component Errors**: Search and Feed pages have runtime errors
3. **React State Management Issues**: setState() calls during render on Dashboard

## Error Categories

### 1. MCP Backend Connection Failures (CRITICAL)

**Impact**: All pages that depend on MCP data fail to load properly.

**Error Pattern**:

```
Failed to load resource: net::ERR_CONNECTION_REFUSED
MCP request failed (attempt 1/4), retrying in 1000ms
MCP request failed (attempt 2/4), retrying in 2000ms
...continues through 4 attempts...
```

**Affected Pages**:

- Dashboard (`/dashboard/george%40prefect.io`)
- Opportunities (`/opportunities`)

**Root Cause**: The MCP backend server is not running. The frontend is configured to connect to the MCP server but cannot establish a connection.

**Resolution Required**: Start the MCP backend server before using the application.

---

### 2. Search Page Error (HIGH PRIORITY)

**Location**: `/search`

**Error Message**:

```
A <Select.Item /> must have a value prop that is not an empty string.
This is because the Select value can be set to an empty string to clear
the selection and show the placeholder.
```

**User Impact**: Search page displays error boundary instead of search interface.

**Component**: SearchPage component (likely in filter controls)

**Root Cause**: A Select component (probably Radix UI or similar) has an item with an empty string value, which is not allowed.

**Location in Code**: `frontend/app/search/page.tsx` or related component

**Fix Required**: Find Select.Item components in the search page and ensure all have non-empty value props.

---

### 3. Feed Page Error (HIGH PRIORITY)

**Location**: `/feed`

**Error Message**:

```
Cannot read properties of undefined (reading 'items')
```

**Component Stack**:

```
at FeedPage (webpack-internal:///(app-pages-browser)/./app/feed/page.tsx:29:76)
```

**User Impact**: Feed page displays error boundary instead of feed content.

**Root Cause**: Attempting to access `.items` property on an undefined object. Likely missing null check or data not loaded before render.

**Location in Code**: `frontend/app/feed/page.tsx:29:76`

**Fix Required**: Add null/undefined checks before accessing `.items` property, or ensure data is loaded before component renders.

---

### 4. Dashboard React State Warning (MEDIUM PRIORITY)

**Location**: `/dashboard/george%40prefect.io`

**Error Message**:

```
Cannot update a component (Router) while rendering a different component (DashboardPage).
To locate the bad setState() call inside DashboardPage, follow the stack trace.
```

**User Impact**: Dashboard displays but has state management issues that could cause re-render loops or performance problems.

**Root Cause**: DashboardPage component is calling setState during render phase, likely in useEffect without proper dependencies or direct state updates in render.

**Fix Required**: Move state updates to useEffect hooks or event handlers. Avoid calling setState directly during component render.

---

## Page Status Summary

| Page          | URL                 | Status     | Error Type                                         |
| ------------- | ------------------- | ---------- | -------------------------------------------------- |
| Dashboard     | `/dashboard/:email` | ⚠️ Partial | MCP connection failure + React state warning       |
| Search        | `/search`           | ❌ Broken  | Select.Item empty value                            |
| Feed          | `/feed`             | ❌ Broken  | Cannot read 'items' of undefined                   |
| Calls         | `/calls`            | ✅ Working | Shows "Coming Soon" placeholder                    |
| Opportunities | `/opportunities`    | ⚠️ Partial | MCP connection failure - shows filters but no data |
| Profile       | `/profile`          | ✅ Working | Shows "Coming Soon" placeholder                    |
| Settings      | `/settings`         | ✅ Working | Shows settings navigation                          |

**Legend**:

- ✅ Working: Page loads and displays as expected
- ⚠️ Partial: Page loads but has functionality issues
- ❌ Broken: Error boundary triggered, page unusable

---

## Console Error Details

### Feed Page Full Error Stack

```
TypeError: Cannot read properties of undefined (reading 'items')
    at FeedPage (webpack-internal:///(app-pages-browser)/./app/feed/page.tsx:29:76)
    at ClientPageRoot
    at InnerLayoutRouter
    at RedirectErrorBoundary
    at RedirectBoundary
    at HTTPAccessFallbackBoundary
    at LoadingBoundary
    at ErrorBoundary
    [... full React component stack ...]
```

**Component Location**: `frontend/app/feed/page.tsx` line 29, column 76

### MCP Connection Error Details

**Frequency**: Continuous retries every 1-4 seconds when on pages requiring MCP data
**Retry Strategy**: Exponential backoff (1000ms, 2000ms, 4000ms, 8000ms)
**Final Behavior**: After 4 failed attempts, displays "MCP backend request failed after retries"

---

## Recommendations

### Immediate Actions (Before Demo/Production)

1. **Start MCP Backend Server**

   - Command: `cd /Users/gcoyne/src/prefect/call-coach && uv run python -m coaching_mcp.server`
   - Verify server is running before starting frontend
   - Add startup script to documentation

2. **Fix Search Page Select Error**

   - File: `frontend/app/search/page.tsx`
   - Find all `<Select.Item value="" />` instances
   - Change to valid non-empty values or add placeholder option differently

3. **Fix Feed Page Undefined Access**

   - File: `frontend/app/feed/page.tsx:29`
   - Add null check: `data?.items?.map(...)` or conditional render
   - Ensure data is loaded before accessing properties

4. **Fix Dashboard State Updates**
   - File: `frontend/app/dashboard/[email]/page.tsx`
   - Move setState calls into useEffect hooks
   - Review dependency arrays

### Future Improvements

1. **Better Error Handling**

   - Add loading states while MCP backend is connecting
   - Display user-friendly messages instead of technical errors
   - Add retry buttons on error boundaries

2. **Development Experience**

   - Add health check endpoint to MCP backend
   - Frontend should detect if backend is unavailable on startup
   - Add dev environment checks/warnings

3. **Monitoring**
   - Add error tracking (Sentry, LogRocket, etc.)
   - Monitor MCP connection failures
   - Track page load success rates

---

## Test Coverage Note

The test suite has **600+ tests with 88% passing** (as of TDD Parallel Wave 2 completion). However, these component errors suggest:

1. Integration tests may not cover all user navigation paths
2. E2E tests might not be running against a live MCP backend
3. Tests may be mocking data that hides undefined property access

**Recommendation**: Add E2E tests that navigate through all pages with MCP backend running to catch these integration issues.

---

## Environment Information

- **Node.js Version**: (not captured)
- **Next.js**: Using App Router
- **Frontend Port**: 3000
- **MCP Backend**: Not running (should be on default port)
- **Database**: Neon PostgreSQL (connection status unknown)

---

## Next Steps

1. Start MCP backend server
2. Re-test all pages with backend running
3. Fix Search page Select.Item error
4. Fix Feed page undefined access
5. Fix Dashboard setState warning
6. Add E2E tests covering full navigation flow
7. Update local development documentation with proper startup sequence
