# Fix Call Detail Page Loading

## Why

The call detail page (`/calls/[callId]`) shows skeleton loaders indefinitely instead of displaying call analysis data. Manual API testing confirms the backend endpoint works correctly (returns 200 with valid JSON), but the React component's SWR hook never triggers the fetch request. This blocks managers from viewing coaching insights for individual calls, which is the core value proposition of the application.

## What Changes

- Fix SWR data fetching in call detail page client component
- Ensure proper authentication flow for API routes accessed via SWR
- Fix UUID type mismatch in coaching-sessions endpoint (separate issue found during investigation)
- Validate SSR/CSR boundary handling for authenticated data fetching
- Add comprehensive error states and logging for debugging similar issues

## Capabilities

### New Capabilities

- `call-detail-debugging`: Structured approach to debugging data fetching issues in call detail pages, including authentication flow validation, SWR configuration verification, and SSR/CSR boundary analysis.

### Modified Capabilities

- `call-analysis-display`: Current implementation shows infinite loading state. Requirements change to include proper loading states, error handling, and authentication boundary management.

## Impact

**Affected Components:**

- `frontend/app/calls/[callId]/page.tsx` - Server component wrapper
- `frontend/app/calls/[callId]/CallAnalysisViewer.tsx` - Client component with SWR hooks
- `frontend/lib/hooks/useCallAnalysis.ts` - SWR hook implementation
- `frontend/app/api/coaching/analyze-call/route.ts` - API route handler
- `frontend/app/api/calls/[id]/coaching-sessions/route.ts` - UUID type issue

**Authentication Flow:**

- Clerk authentication middleware integration with Next.js App Router
- Cookie-based session handling across SSR and client-side fetching
- API route protection via `withAuth` wrapper

**Dependencies:**

- SWR v2.x data fetching patterns
- Next.js 14 App Router SSR/CSR boundaries
- Clerk authentication SDK

**Database:**

- Fix UUID parsing in coaching_sessions query (call_id from Gong is numeric string, not UUID)
