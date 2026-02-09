# Implementation Tasks

## 1. Investigation with Chrome DevTools

- [x] 1.1 Start Chrome DevTools MCP server and connect to browser
- [x] 1.2 Navigate to call detail page and take snapshot of page state
- [x] 1.3 Inspect network tab to confirm no request to /api/coaching/analyze-call
- [x] 1.4 Inspect CallAnalysisViewer component props and state
- [x] 1.5 Verify Clerk authentication cookies present in browser
- [x] 1.6 Check console for React hydration errors or warnings
- [x] 1.7 Document findings in investigation notes

## 2. Authentication Flow Analysis

- [ ] 2.1 Test API route directly with curl (unauthenticated baseline)
- [ ] 2.2 Test API route from browser console with fetch (authenticated)
- [ ] 2.3 Verify withAuth middleware is working correctly
- [ ] 2.4 Check Clerk middleware.ts configuration for App Router compatibility
- [ ] 2.5 Trace authentication context from SSR through client hydration
- [ ] 2.6 Document authentication boundary where context is lost

## 3. SWR Hook Pattern Comparison

- [x] 3.1 Read use-current-user.ts (known working example)
- [x] 3.2 Read useCallAnalysis.ts (broken hook)
- [x] 3.3 Compare line-by-line for differences in configuration
- [x] 3.4 Identify why use-current-user works but useCallAnalysis doesn't
- [x] 3.5 Document specific pattern differences

## 4. Fix SWR Hook Configuration

- [x] 4.1 Apply working pattern from use-current-user to useCallAnalysis
- [x] 4.2 Ensure fetcher function includes credentials: "include"
- [x] 4.3 Verify buildApiUrl returns correct URL format
- [x] 4.4 Add error handling for fetch failures
- [x] 4.5 Test hook in isolation with manual invocation

## 5. Fix Server Component Integration

- [ ] 5.1 Review page.tsx server component for authentication passing
- [ ] 5.2 Ensure callId is correctly passed as prop to client component
- [ ] 5.3 Verify no SSR/CSR hydration mismatches
- [ ] 5.4 Add error boundaries around client component
- [ ] 5.5 Test page load with Chrome DevTools monitoring

## 6. Fix UUID Type Issue in Coaching Sessions

- [ ] 6.1 Review coaching_sessions table schema for call_id column type
- [ ] 6.2 Create database migration to change call_id from UUID to TEXT or BIGINT
- [ ] 6.3 Update TypeScript types in db/models.py to match schema change
- [ ] 6.4 Modify coaching-sessions API route to remove UUID casting
- [ ] 6.5 Test endpoint with numeric Gong call ID (e.g., "1545043197760013510")
- [ ] 6.6 Verify query returns results without type errors

## 7. Add Comprehensive Error States

- [ ] 7.1 Add error state UI to CallAnalysisViewer for network failures
- [ ] 7.2 Add retry button for transient errors
- [ ] 7.3 Add 401 handling with redirect to login
- [ ] 7.4 Add 403 handling with permission explanation
- [ ] 7.5 Add 404 handling with link back to calls list
- [ ] 7.6 Test each error state with Chrome DevTools network throttling

## 8. Add Error Logging and Debugging

- [ ] 8.1 Add structured logging to useCallAnalysis hook
- [ ] 8.2 Add console.log for SWR state changes during debugging
- [ ] 8.3 Add error logging to API route with full context
- [ ] 8.4 Add React error boundary logging with component state
- [ ] 8.5 Document common error patterns in troubleshooting guide

## 9. Testing and Validation

- [ ] 9.1 Run frontend test suite (61 tests must pass)
- [ ] 9.2 Update useCallAnalysis.test.tsx for new error states
- [ ] 9.3 Manual smoke test: calls list → call detail → analysis loads
- [ ] 9.4 Test with different call IDs (analyzed, unanalyzed, invalid)
- [ ] 9.5 Test authentication edge cases (expired session, logout)
- [ ] 9.6 Test on different browsers (Chrome, Firefox, Safari)
- [ ] 9.7 Verify other SWR hooks still work (user profile, calls list)

## 10. Cleanup and Documentation

- [ ] 10.1 Remove debug logging added during investigation
- [ ] 10.2 Remove unused SWR hook rewrites from previous attempts
- [ ] 10.3 Update CLAUDE.md with debugging patterns learned
- [ ] 10.4 Document authentication flow in architecture docs
- [ ] 10.5 Close beads issue bd-9p8 with resolution notes
- [ ] 10.6 Commit changes with detailed commit message
- [ ] 10.7 Push to remote and verify CI passes
