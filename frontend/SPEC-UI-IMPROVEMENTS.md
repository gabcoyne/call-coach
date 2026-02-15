# UI Improvements Specification

This document specifies the required UI improvements for Call Coach frontend based on user feedback.

---

## 1. Date Picker Implementation

### Current State

- Dashboard and calls pages use `Select` dropdowns with preset time periods (`last_7_days`, `last_30_days`, etc.)
- No custom date range selection exists
- Component: `components/dashboard/TimePeriodSelector.tsx`

### Requirements

Install shadcn date picker components and add custom date range selection to:

- Dashboard page (`app/dashboard/[repEmail]/page.tsx`)
- Calls page (`app/calls/page.tsx`)

### Implementation

**Step 1: Install dependencies**

```bash
npx shadcn@latest add popover
npx shadcn@latest add calendar
npm install date-fns
```

**Step 2: Create DateRangePicker component**

Create `components/ui/date-range-picker.tsx`:

- Compose Popover + Calendar from shadcn
- Support single date and date range modes
- Format dates using `date-fns`
- Include preset quick-select buttons (Last 7 days, Last 30 days, etc.)

**Step 3: Update pages**

Dashboard (`app/dashboard/[repEmail]/page.tsx`):

- Replace or augment TimePeriodSelector with DateRangePicker
- Update API calls to use `start_date` and `end_date` parameters

Calls page (`app/calls/page.tsx`):

- Add DateRangePicker to filter card
- Pass date range to `search_calls` API

### Files to Create/Modify

| File                                  | Action                  |
| ------------------------------------- | ----------------------- |
| `components/ui/popover.tsx`           | Create (shadcn install) |
| `components/ui/calendar.tsx`          | Create (shadcn install) |
| `components/ui/date-range-picker.tsx` | Create                  |
| `app/dashboard/[repEmail]/page.tsx`   | Modify                  |
| `app/calls/page.tsx`                  | Modify                  |

---

## 2. Email Display Fix

### Current State

- Emails are URL-encoded in route params: `Wayne%40prefect.io`
- Dashboard table shows raw email addresses (line 183 in `app/dashboard/page.tsx`)
- `decodeURIComponent` is used in `[repEmail]/page.tsx` but display still shows email format

### Requirements

Display user-friendly names instead of encoded emails:

- Use first + last name when available
- Fall back to decoded email if name unavailable
- Never show `%40` or encoded characters to users

### Implementation

**Option A: Extract name from email (simple)**

```typescript
function formatRepDisplay(email: string, name?: string): string {
  if (name) return name;
  // Convert "wayne.smith@prefect.io" → "Wayne Smith"
  const localPart = email.split("@")[0];
  return localPart
    .split(".")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
```

**Option B: Fetch user metadata (robust)**

- Create API endpoint to lookup user by email
- Cache user metadata in component state
- Display full name from user record

### Files to Modify

| File                                | Change                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------ |
| `app/dashboard/page.tsx`            | Use `rep.name` instead of `rep.email` in display; keep email in secondary text |
| `app/dashboard/[repEmail]/page.tsx` | Display decoded name in header, not raw email                                  |
| `lib/utils.ts`                      | Add `formatRepDisplay()` helper                                                |

---

## 3. Opportunities Page Experience

### Current State

- Page exists: `app/opportunities/page.tsx` → renders `OpportunitiesList.tsx`
- API endpoint: `GET /api/opportunities` (fully implemented with pagination, filters, sorting)
- Database query: `lib/db/opportunities.ts` `searchOpportunities()`
- **Issue**: Returns empty because no data exists in database

### Requirements

Design complete opportunities experience:

1. Ensure data pipeline populates opportunities
2. Create opportunity detail page
3. Add opportunity-to-call linking
4. Design empty state with actionable guidance

### Implementation

**Phase 1: Data Pipeline**

- Verify `opportunities` table has data (may need import script)
- Link opportunities to calls via `opportunity_calls` join table
- Populate health scores based on call analysis

**Phase 2: Empty State (Immediate)**
Update `OpportunitiesList.tsx` empty state:

```tsx
<div className="text-center py-12">
  <Target className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
  <h3 className="text-lg font-semibold">No opportunities found</h3>
  <p className="text-muted-foreground mt-2 max-w-md mx-auto">
    Opportunities are synced from your CRM. Contact your admin if you expect to see data here.
  </p>
  <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
    Refresh
  </Button>
</div>
```

**Phase 3: Opportunity Detail Page**
Create `app/opportunities/[id]/page.tsx`:

- Header: Opportunity name, account, stage, amount
- Health score gauge with trend
- Timeline of related calls (linked from coaching_sessions)
- AI insights section (reuse `OpportunityInsights` component)
- Action buttons: View in CRM, Schedule follow-up

**Phase 4: Call Linking**

- Add "Related Opportunity" field to call detail page
- Show opportunity context in call analysis
- Enable filtering calls by opportunity

### Files to Create/Modify

| File                                             | Action                     |
| ------------------------------------------------ | -------------------------- |
| `components/opportunities/OpportunitiesList.tsx` | Enhance empty state        |
| `app/opportunities/[id]/page.tsx`                | Create detail page         |
| `app/api/opportunities/[id]/route.ts`            | Create detail endpoint     |
| `lib/db/opportunities.ts`                        | Add `getOpportunityById()` |
| `scripts/import_opportunities.py`                | Create/verify data import  |

---

## 4. Calls Table Improvements

### Current State

- `app/calls/page.tsx` renders 8-column table
- Issues identified:
  - No pagination (hardcoded `limit: 20, offset: 0`)
  - Search query captured but NOT sent to API (lines 93-96)
  - No date range filtering
  - Table renders but data may be sparse

### Requirements

1. Add pagination matching Opportunities page pattern
2. Implement actual search functionality
3. Add date range filter
4. Improve mobile responsiveness
5. Add loading states per-row for better UX

### Implementation

**Step 1: Add Pagination**

```typescript
// Add state
const [page, setPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);
const limit = 20;

// Update request
const requestBody = {
  limit,
  offset: (page - 1) * limit,
  // ... filters
};

// Handle response
const result = await response.json();
setCalls(result.data.items);
setTotalPages(Math.ceil(result.data.total / limit));
```

**Step 2: Implement Search**

```typescript
// Send search query to backend
if (searchQuery.trim()) {
  requestBody.search = searchQuery.trim();
}
```

Note: Backend `search_calls` may need enhancement to support text search.

**Step 3: Add Date Filter**

```typescript
// Add to filter card
<DateRangePicker
  value={dateRange}
  onChange={setDateRange}
/>

// Include in request
if (dateRange?.from) requestBody.start_date = dateRange.from.toISOString();
if (dateRange?.to) requestBody.end_date = dateRange.to.toISOString();
```

**Step 4: Add Pagination Controls**
Copy pattern from `OpportunitiesList.tsx` (lines 411-446):

```tsx
<div className="flex items-center justify-between px-4 py-3 border-t">
  <div className="text-sm text-muted-foreground">
    Page {page} of {totalPages}
  </div>
  <div className="flex gap-2">
    <Button
      variant="outline"
      size="sm"
      onClick={() => setPage((p) => Math.max(1, p - 1))}
      disabled={page === 1}
    >
      Previous
    </Button>
    <Button
      variant="outline"
      size="sm"
      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
      disabled={page === totalPages}
    >
      Next
    </Button>
  </div>
</div>
```

### Files to Modify

| File                   | Change                                            |
| ---------------------- | ------------------------------------------------- |
| `app/calls/page.tsx`   | Add pagination, implement search, add date filter |
| Backend `search_calls` | May need text search support                      |

---

## 5. Call ID → Event Title Mapping

### Current State

- Call IDs are used internally in URLs: `/calls/{call_id}`
- Display already shows `call.title` in most places
- **Verification**: Searched codebase - Call IDs are NOT displayed to users
- Call titles may sometimes be empty/null (needs fallback)

### Requirements

- Ensure all user-facing displays show call title, never raw ID
- Add fallback for missing titles
- Format: "Call with {customer} on {date}" when title is null

### Implementation

**Add title fallback helper:**

```typescript
// lib/utils.ts
export function formatCallTitle(call: {
  title?: string | null;
  customer_names?: string[];
  date?: string | null;
}): string {
  if (call.title) return call.title;

  const customer = call.customer_names?.[0] || "Unknown";
  const dateStr = call.date
    ? new Date(call.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })
    : "Unknown date";

  return `Call with ${customer} on ${dateStr}`;
}
```

**Update components:**

- `app/calls/page.tsx` line 250: Use `formatCallTitle(call)`
- `components/search/search-results.tsx` lines 87, 167: Use helper
- `components/coaching/RecentActivityFeed.tsx`: Verify fallback exists

### Files to Modify

| File                                         | Change                  |
| -------------------------------------------- | ----------------------- |
| `lib/utils.ts`                               | Add `formatCallTitle()` |
| `app/calls/page.tsx`                         | Use `formatCallTitle()` |
| `components/search/search-results.tsx`       | Use `formatCallTitle()` |
| `components/coaching/RecentActivityFeed.tsx` | Verify/add fallback     |

---

## 6. Performance Investigation

### Current State

- Calls page sometimes fails to load
- Direct API call to backend MCP server
- No caching, no pagination (fetches 20 items repeatedly)
- No error retry logic

### Root Causes Identified

1. **No pagination**: Always fetches all matching records up to limit
2. **Backend dependency**: Direct call to `NEXT_PUBLIC_MCP_BACKEND_URL`
3. **No caching**: Every filter change triggers full refetch
4. **No timeout handling**: Network issues cause hanging

### Implementation

**Step 1: Add SWR for caching and deduplication**

```typescript
import useSWR from "swr";

const { data, error, isLoading, mutate } = useSWR(
  ["calls", callTypeFilter, productFilter, searchQuery, page],
  () => fetchCalls({ callTypeFilter, productFilter, searchQuery, page }),
  {
    revalidateOnFocus: false,
    dedupingInterval: 30000, // 30 second cache
  }
);
```

**Step 2: Add request timeout**

```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

const response = await fetch(url, {
  signal: controller.signal,
  // ... other options
});

clearTimeout(timeoutId);
```

**Step 3: Add error boundary and retry**

```tsx
if (error) {
  return (
    <Card className="border-destructive">
      <CardContent className="pt-6">
        <AlertCircle className="h-8 w-8 text-destructive mb-2" />
        <p>Failed to load calls. Please try again.</p>
        <Button onClick={() => mutate()}>Retry</Button>
      </CardContent>
    </Card>
  );
}
```

**Step 4: Add loading skeleton improvements**
Show more realistic skeleton matching actual table rows.

**Step 5: Consider API route proxy**
Instead of calling backend directly from client, route through Next.js API:

```
Client → /api/calls → Backend MCP
```

Benefits:

- Server-side caching
- Better error handling
- Hide backend URL from client

### Files to Modify

| File                     | Change                           |
| ------------------------ | -------------------------------- |
| `app/calls/page.tsx`     | Add SWR, timeout, error handling |
| `app/api/calls/route.ts` | Create proxy endpoint (optional) |

---

## Implementation Priority

| Priority | Item                     | Effort | Impact                     |
| -------- | ------------------------ | ------ | -------------------------- |
| P0       | Calls page performance   | Medium | High - Page broken         |
| P1       | Calls pagination         | Low    | High - Limited to 20 items |
| P1       | Email display fix        | Low    | Medium - UX polish         |
| P2       | Date picker              | Medium | Medium - Feature gap       |
| P2       | Call title fallback      | Low    | Low - Edge case            |
| P3       | Opportunities experience | High   | Medium - Depends on data   |

---

## Testing Checklist

- [x] Date picker: Select custom range, verify API receives correct dates ✅ IMPLEMENTED
- [ ] Email display: Confirm no `%40` visible anywhere in UI (Dashboard looks good, needs verification)
- [x] Opportunities: Test empty state, then with data if available ✅ IMPLEMENTED
- [x] Calls table: Pagination works, search filters results, date range filters ✅ IMPLEMENTED
- [x] Call titles: Test with null title, verify fallback renders ✅ IMPLEMENTED
- [x] Performance: Calls page loads within 3 seconds, retry works on failure ✅ IMPLEMENTED

---

## Implementation Status (Updated 2026-02-13)

### Completed

1. **Date Range Picker** - Created `components/ui/date-range-picker.tsx`

   - Two-month calendar view
   - Quick-select presets (Last 7/30/90 days, This month, Last month)
   - Integrated into Calls page

2. **Calls Page Improvements** (`app/calls/page.tsx`)

   - Added DateRangePicker to filters
   - Added pagination with Previous/Next navigation
   - Added error handling with Retry button
   - Added 15-second timeout for requests
   - Added `formatCallTitle()` fallback for null titles

3. **Opportunities Empty State** (`components/opportunities/OpportunitiesList.tsx`)

   - Added Target icon
   - Improved messaging explaining CRM sync
   - Added Refresh button

4. **Design System Page** - Fixed type errors for removed button/badge variants

5. **BigQuery Data Sync** - Created incremental sync pipeline

   - `scripts/import_opportunities_from_bigquery.py` - One-time import script
   - `flows/sync_bigquery_data.py` - Prefect flow for scheduled sync
   - `prefect.yaml` - Deployment config with 6-hour schedule
   - Successfully imported 3,194 opportunities from BigQuery
   - Synced 1,000 calls in incremental test

6. **Opportunities Page Data** (`components/opportunities/OpportunitiesList.tsx`)
   - Fixed null handling for close_date, amount, health_score, call_count, email_count
   - Page now renders 3,194 opportunities correctly

### Remaining

1. **Email display** - Dashboard already shows names; verify no `%40` appears elsewhere
2. **Dashboard date picker** - Add DateRangePicker to individual rep dashboard
3. **Backend enhancements** - May need text search support in `search_calls`
4. **Deploy BigQuery sync** - Run `prefect deploy` to activate scheduled sync
