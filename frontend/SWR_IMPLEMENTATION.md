# SWR Data Fetching Implementation

## Overview

This document describes the SWR (Stale-While-Revalidate) data fetching implementation for the Gong Call Coaching frontend. SWR provides efficient data fetching with automatic caching, revalidation, and optimistic updates.

## Architecture

### Core Components

1. **Global SWR Configuration** (`lib/swr-config.ts`)

   - Default fetcher with authentication
   - Revalidation settings
   - Error retry logic with exponential backoff
   - Utility functions for API URL building and error handling

2. **SWR Provider** (`lib/swr-provider.tsx`)

   - Wraps the application with global SWR configuration
   - Should be added to root layout.tsx

3. **Custom Hooks** (`lib/hooks/`)

   - `useCallAnalysis` - Fetch call analysis data
   - `useRepInsights` - Fetch rep performance insights
   - `useSearchCalls` - Search calls with filters
   - Mutation variants for on-demand operations

4. **Utility Hooks** (`lib/hooks/`)
   - `useOptimistic` - Optimistic UI updates
   - `useErrorHandling` - Error state management
   - `useLoadingState` - Loading state patterns
   - `useDataFreshness` - Data freshness tracking

## Installation

SWR has been added to package.json:

```json
{
  "dependencies": {
    "swr": "^2.2.5"
  }
}
```

Run `npm install` to install the package.

## Configuration

### Global Configuration

The global SWR configuration is defined in `lib/swr-config.ts`:

```typescript
export const swrConfig: SWRConfiguration = {
  fetcher,
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  revalidateIfStale: true,
  dedupingInterval: 2000,
  focusThrottleInterval: 5000,
  shouldRetryOnError: true,
  errorRetryInterval: 5000,
  errorRetryCount: 3,
  loadingTimeout: 30000,
  keepPreviousData: true,
};
```

### Error Retry with Exponential Backoff

The configuration includes custom error retry logic:

- Don't retry on 404 (not found)
- Don't retry on 401/403 (authentication/authorization errors)
- Max 3 retries with exponential backoff: 5s, 10s, 20s

## Usage

### 1. Add SWR Provider to Layout

Add the SWR provider to your root layout:

```tsx
// app/layout.tsx
import { SWRProvider } from "@/lib/swr-provider";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ClerkProvider>
          <SWRProvider>{children}</SWRProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
```

### 2. Use Call Analysis Hook

Fetch call analysis data:

```tsx
import { useCallAnalysis } from "@/lib/hooks";

function CallAnalysisView({ callId }: { callId: string }) {
  const { data, error, isLoading } = useCallAnalysis(callId, {
    dimensions: ["product_knowledge", "discovery"],
    use_cache: true,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  return (
    <div>
      <h1>{data.call_metadata.title}</h1>
      <p>Overall Score: {data.scores.overall}</p>
    </div>
  );
}
```

### 3. Use Rep Insights Hook

Fetch rep performance insights:

```tsx
import { useRepInsights } from "@/lib/hooks";

function RepDashboard({ repEmail }: { repEmail: string }) {
  const { data, error, isLoading } = useRepInsights(repEmail, {
    time_period: "last_30_days",
    product_filter: "prefect",
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  return (
    <div>
      <h2>{data.rep_info.name}</h2>
      <p>Calls Analyzed: {data.rep_info.calls_analyzed}</p>
      {/* Render charts, trends, etc. */}
    </div>
  );
}
```

### 4. Use Search Calls Hook

Search calls with filters:

```tsx
import { useSearchCalls } from "@/lib/hooks";
import { useState } from "react";

function CallSearch() {
  const [filters, setFilters] = useState({
    min_score: 70,
    limit: 20,
  });

  const { data, error, isLoading } = useSearchCalls(filters);

  if (isLoading) return <div>Searching...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{data?.map((call) => <CallCard key={call.call_id} call={call} />)}</div>;
}
```

### 5. Optimistic Updates

Implement optimistic UI updates for better UX:

```tsx
import { useCallAnalysis, useOptimistic } from "@/lib/hooks";

function UpdateScoreButton({ callId, newScore }: Props) {
  const { data, mutate } = useCallAnalysis(callId);
  const { performOptimisticUpdate, isOptimistic } = useOptimistic();

  const handleUpdate = async () => {
    await performOptimisticUpdate(
      `/api/coaching/analyze-call?call_id=${callId}`,
      async () => {
        const response = await fetch("/api/coaching/update-score", {
          method: "POST",
          body: JSON.stringify({ callId, newScore }),
        });
        return response.json();
      },
      {
        optimisticData: (current) => ({
          ...current!,
          scores: { ...current!.scores, overall: newScore },
        }),
      }
    );
  };

  return (
    <button onClick={handleUpdate} disabled={isOptimistic}>
      Update Score {isOptimistic && "(saving...)"}
    </button>
  );
}
```

### 6. Error Handling

Use error handling utilities:

```tsx
import { useCallAnalysis, useErrorHandling } from "@/lib/hooks";

function CallAnalysisView({ callId }: { callId: string }) {
  const { data, error: swrError } = useCallAnalysis(callId);
  const { errorMessage, isAuthError, clearError } = useErrorHandling(swrError, {
    onAuthError: () => {
      window.location.href = "/sign-in";
    },
    autoClear: true,
    autoClearTimeout: 5000,
  });

  if (isAuthError) {
    return <div>Please sign in to view this analysis.</div>;
  }

  if (errorMessage) {
    return (
      <div className="error-banner">
        {errorMessage}
        <button onClick={clearError}>Dismiss</button>
      </div>
    );
  }

  return <div>{data && <AnalysisContent data={data} />}</div>;
}
```

### 7. Loading State Management

Use loading state utilities:

```tsx
import { useCallAnalysis, useDebouncedLoading } from "@/lib/hooks";

function SearchResults({ query }: { query: string }) {
  const { data, isValidating } = useSearchCalls({ query });
  const debouncedLoading = useDebouncedLoading(isValidating, 300);

  // Only show loading spinner after 300ms (prevents flickering)
  if (debouncedLoading) return <LoadingSpinner />;

  return <ResultsList results={data} />;
}
```

## Advanced Features

### Multiple Rep Insights (Manager View)

Fetch insights for multiple reps simultaneously:

```tsx
import { useMultipleRepInsights } from "@/lib/hooks";

function TeamDashboard({ repEmails }: { repEmails: string[] }) {
  const { data, error, isLoading } = useMultipleRepInsights(repEmails, {
    time_period: "last_30_days",
  });

  if (isLoading) return <div>Loading team data...</div>;
  if (error) return <div>Error loading team data</div>;

  return (
    <div>
      {Object.entries(data).map(([email, insights]) => (
        <RepCard key={email} insights={insights} />
      ))}
    </div>
  );
}
```

### Manual Mutations

Use mutation hooks for manual triggering:

```tsx
import { useCallAnalysisMutation } from "@/lib/hooks";

function AnalyzeCallButton({ callId }: { callId: string }) {
  const { trigger, isMutating, data } = useCallAnalysisMutation({
    onSuccess: (data) => console.log("Analysis complete:", data),
    onError: (error) => console.error("Analysis failed:", error),
  });

  const handleAnalyze = async () => {
    await trigger({
      call_id: callId,
      force_reanalysis: true,
    });
  };

  return (
    <button onClick={handleAnalyze} disabled={isMutating}>
      {isMutating ? "Analyzing..." : "Analyze Call"}
    </button>
  );
}
```

### Data Freshness Tracking

Track data freshness and show refresh UI:

```tsx
import { useRepInsights, useDataFreshness } from "@/lib/hooks";

function RepDashboard({ email }: { email: string }) {
  const { data, mutate } = useRepInsights(email);
  const { lastUpdated, isStale, refresh } = useDataFreshness({
    onRefresh: mutate,
    staleTime: 60000, // 1 minute
  });

  return (
    <div>
      <p>Last updated: {lastUpdated?.toLocaleTimeString()}</p>
      {isStale && <button onClick={refresh}>Refresh</button>}
      {/* Dashboard content */}
    </div>
  );
}
```

## API Integration

All hooks are designed to work seamlessly with the backend API routes:

- `/api/coaching/analyze-call` - Call analysis endpoint
- `/api/coaching/rep-insights` - Rep insights endpoint
- `/api/coaching/search-calls` - Call search endpoint

The hooks automatically:

- Include credentials (Clerk session cookies)
- Set appropriate headers
- Handle authentication errors
- Parse JSON responses
- Provide TypeScript types from `@/types/coaching`

## Benefits

1. **Automatic Caching**: SWR caches data by key, reducing unnecessary network requests
2. **Background Revalidation**: Keeps data fresh without blocking the UI
3. **Optimistic Updates**: Update UI immediately before server confirmation
4. **Error Retry**: Automatic retry with exponential backoff
5. **Type Safety**: Full TypeScript support with typed responses
6. **Authentication**: Seamless integration with Clerk authentication
7. **Performance**: Deduplication, focus revalidation, and keep previous data

## Next Steps

1. **Add SWR Provider to Layout**: Add `<SWRProvider>` to `app/layout.tsx`
2. **Implement UI Components**: Use hooks in Call Analysis Viewer, Rep Dashboard, and Search pages
3. **Add Loading Skeletons**: Use loading state hooks to create skeleton loaders
4. **Error Boundaries**: Create error boundary components using error handling hooks
5. **Testing**: Write unit tests for hooks and integration tests for data fetching

## Files Created

- `lib/swr-config.ts` - Global SWR configuration
- `lib/swr-provider.tsx` - SWR provider component
- `lib/hooks/useCallAnalysis.ts` - Call analysis hook
- `lib/hooks/useRepInsights.ts` - Rep insights hook
- `lib/hooks/use-search-calls.ts` - Call search hook
- `lib/hooks/use-optimistic.ts` - Optimistic update utilities
- `lib/hooks/use-error-handling.ts` - Error handling utilities
- `lib/hooks/use-loading-state.ts` - Loading state utilities
- `lib/hooks/index.ts` - Barrel exports for all hooks

## Dependencies

- `swr@^2.2.5` - SWR library
- `swr/mutation` - SWR mutation utilities (included with SWR)

## Related Documentation

- [SWR Documentation](https://swr.vercel.app/)
- [Backend Integration Complete](./BACKEND_INTEGRATION_COMPLETE.md)
- [API Testing Guide](./API_TESTING.md)
- [Clerk Authentication](./CLERK_SETUP.md)
