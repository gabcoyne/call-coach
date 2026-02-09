# Call Detail Page Loading Investigation

## Problem Statement

Call detail page showed skeleton loaders indefinitely. SWR hook `useCallAnalysis` was instantiated but never triggered fetch requests.

## Investigation Process

### Tools Used

- Chrome DevTools MCP for systematic browser inspection
- Network tab analysis
- Console logging for hook lifecycle tracking
- Direct fetch testing from browser console

### Key Findings

1. **API Endpoint Working**: Manual tests confirmed `/api/coaching/analyze-call` returned 200 with valid data (overall_score: 68)
2. **Authentication Working**: Clerk cookies present, `/api/v1/users/me` requests successful
3. **No Network Requests**: Zero requests to analyze-call endpoint despite hook being called 6+ times per render
4. **No Errors**: Console showed no React errors, hydration mismatches, or JavaScript exceptions

### Root Cause

**SWR options object caused fetcher to never execute.**

The problematic configuration:

```typescript
const { data, error } = useSWR<AnalyzeCallResponse>(
  url, // URL string as key
  async (url) => {
    /* fetcher */
  },
  {
    revalidateOnFocus: true,
    revalidateOnMount: force_reanalysis,
    keepPreviousData: true,
    dedupingInterval: 0,
  }
);
```

Specific issues:

1. Using URL string as key with inline fetcher created conflict
2. SWR options (`revalidateOnMount`, `keepPreviousData`, etc.) prevented initial fetch
3. Pattern didn't match working example (`use-current-user.ts`)

## Solution

Adopted the working pattern from `use-current-user.ts`:

```typescript
const { data, error } = useSWR<AnalyzeCallResponse>(
  callId && enabled ? ["analyze-call", callId] : null,
  async () => {
    const url = buildApiUrl("/api/coaching/analyze-call", {
      call_id: callId!,
      // ... params
    });

    const response = await fetch(url, {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    // error handling

    return response.json();
  }
  // NO OPTIONS - use SWR defaults
);
```

### Key Changes

1. **Array key**: `['analyze-call', callId]` instead of full URL string
2. **URL built inside fetcher**: Not passed as parameter
3. **No SWR options**: Removed all custom options, rely on defaults
4. **Fetcher takes no params**: Closure captures variables from hook scope

## Results

✅ Page now loads call analysis data successfully
✅ Shows real metadata: title, date, duration, participants
✅ SWR fetcher executes on mount
✅ Network request to `/api/coaching/analyze-call` appears in DevTools
✅ Data renders in component within ~3 seconds

## Lessons Learned

1. **Match working patterns exactly**: Don't assume SWR configurations are interchangeable
2. **Array keys preferred**: More flexible than URL strings, better for React deps
3. **SWR defaults are good**: Custom options should be added incrementally with testing
4. **Chrome DevTools MCP invaluable**: Systematic browser inspection caught what manual debugging missed
5. **Direct fetch testing isolates issues**: Confirmed API/auth worked, isolated problem to SWR config

## Related Issues

- Beads issue bd-9p8 (can now be closed)
- Original symptom: Infinite skeleton loaders
- Secondary issue discovered: UUID type mismatch in coaching-sessions endpoint (separate fix needed)
