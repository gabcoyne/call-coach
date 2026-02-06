# Frontend Integration Testing Checklist

Use this checklist to verify the frontend-backend integration is working correctly.

## Prerequisites

- [ ] Database populated with call data
- [ ] `.env` file configured with all required variables
- [ ] `frontend/.env.local` configured with Clerk keys
- [ ] Python dependencies installed (`uv sync`)
- [ ] Frontend dependencies installed (`cd frontend && npm install`)

## Backend Testing

### 1. REST API Server Startup

```bash
./scripts/start-rest-api.sh
```

**Expected Output**:

```
Starting Call Coaching REST API...
Endpoints will be available at http://localhost:8000

INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

- [ ] Server starts without errors
- [ ] Listening on port 8000

### 2. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Output**:

```json
{ "status": "ok", "service": "call-coaching-api", "tools": 5 }
```

- [ ] Returns 200 status
- [ ] Shows 5 tools registered

### 3. OpenAPI Documentation

Open in browser: <http://localhost:8000/docs>

- [ ] Swagger UI loads
- [ ] Shows all 5 tool endpoints:
  - POST /tools/analyze_call
  - POST /tools/get_rep_insights
  - POST /tools/search_calls
  - POST /tools/analyze_opportunity
  - POST /tools/get_learning_insights
- [ ] "Try it out" functionality works

### 4. Analyze Call Endpoint

```bash
curl -X POST http://localhost:8000/tools/analyze_call \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "YOUR_CALL_ID",
    "use_cache": true,
    "include_transcript_snippets": true
  }'
```

Replace `YOUR_CALL_ID` with an actual call ID from your database.

**Expected Output**: JSON with:

- [ ] `call_metadata` object
- [ ] `scores` object with dimension scores
- [ ] `strengths` array
- [ ] `areas_for_improvement` array
- [ ] `action_items` array

### 5. Rep Insights Endpoint

```bash
curl -X POST http://localhost:8000/tools/get_rep_insights \
  -H "Content-Type: application/json" \
  -d '{
    "rep_email": "YOUR_REP_EMAIL",
    "time_period": "last_30_days"
  }'
```

Replace `YOUR_REP_EMAIL` with an actual rep email from your database.

**Expected Output**: JSON with:

- [ ] `rep_info` object
- [ ] `score_trends` object
- [ ] `skill_gaps` array
- [ ] `improvement_areas` array
- [ ] `coaching_plan` string

### 6. Search Calls Endpoint

```bash
curl -X POST http://localhost:8000/tools/search_calls \
  -H "Content-Type: application/json" \
  -d '{
    "min_score": 70,
    "limit": 10
  }'
```

**Expected Output**: JSON array with:

- [ ] Array of call objects
- [ ] Each call has `call_id`, `title`, `date`, `overall_score`
- [ ] Results limited to 10 items

## Frontend Testing

### 1. Frontend Startup

```bash
cd frontend
npm run dev
```

**Expected Output**:

```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in 2.5s
```

- [ ] Server starts without errors
- [ ] Listening on port 3000

### 2. Homepage

Navigate to: <http://localhost:3000>

- [ ] Page loads without errors
- [ ] No console errors in browser
- [ ] Layout renders correctly

### 3. Call Analysis Page

Navigate to: <http://localhost:3000/calls/{CALL_ID}>

Replace `{CALL_ID}` with an actual call ID.

**Page Elements**:

- [ ] Loading skeleton appears first
- [ ] Call metadata displays:
  - [ ] Title
  - [ ] Date
  - [ ] Duration
  - [ ] Participants count
- [ ] Performance scores display:
  - [ ] Overall score card
  - [ ] Dimension score cards (product knowledge, discovery, etc.)
  - [ ] Color-coded by score (green/yellow/red)
- [ ] Insights display:
  - [ ] Strengths list
  - [ ] Areas for improvement list
- [ ] Transcript examples display:
  - [ ] Good examples (green background)
  - [ ] Needs work examples (amber background)
- [ ] Action items display:
  - [ ] Prioritized items
  - [ ] Check icons

**Interactions**:

- [ ] Back button navigates to dashboard
- [ ] Refresh button reloads data
- [ ] No console errors

### 4. Rep Dashboard Page

Navigate to: <http://localhost:3000/dashboard/{REP_EMAIL}>

Replace `{REP_EMAIL}` with an actual rep email.

**Page Elements**:

- [ ] Loading skeleton appears first
- [ ] Header displays:
  - [ ] Rep name
  - [ ] Rep email
  - [ ] Time range selector
- [ ] Performance overview displays:
  - [ ] Overall average score
  - [ ] Total calls count
  - [ ] Date range info
- [ ] Score trends chart displays:
  - [ ] Line chart with multiple dimensions
  - [ ] Legend with color coding
  - [ ] X-axis (dates) and Y-axis (scores)
- [ ] Dimension breakdown displays:
  - [ ] Score cards for each dimension
  - [ ] Color-coded scores
- [ ] Recent calls list displays:
  - [ ] Call date
  - [ ] Call type
  - [ ] Overall score
  - [ ] "View Details" link

**Interactions**:

- [ ] Time range selector changes data
- [ ] Back button navigates
- [ ] "View Details" links work
- [ ] No console errors

### 5. Search Page

Navigate to: <http://localhost:3000/search>

**Filter Controls**:

- [ ] Start date input
- [ ] End date input
- [ ] Rep email input (if manager role)
- [ ] Call type checkboxes
- [ ] Minimum score slider
- [ ] Keyword search input
- [ ] Clear filters button

**Interactions**:

- [ ] Filters update results automatically
- [ ] Date validation works (end > start)
- [ ] Keyword search is debounced (300ms)
- [ ] Clear filters resets all inputs

**Results**:

- [ ] Loading skeleton appears during fetch
- [ ] Results table displays:
  - [ ] Date column
  - [ ] Rep column
  - [ ] Type column
  - [ ] Score column (color-coded badge)
  - [ ] Actions column (View Details button)
- [ ] Pagination controls display:
  - [ ] Page counter
  - [ ] Previous/Next buttons
  - [ ] Buttons disabled when appropriate
- [ ] Empty state shows when no results
- [ ] Error state shows with retry button on error

### 6. Error Handling

**Test error scenarios**:

1. **Backend Down**: Stop REST API server, try to load a page

   - [ ] Error message displays
   - [ ] Retry button appears
   - [ ] Retry button reloads data

2. **Invalid Call ID**: Navigate to `/calls/invalid-id`

   - [ ] Error message displays
   - [ ] No console errors crash the app

3. **Network Error**: Disconnect network, try to load data
   - [ ] Error message displays
   - [ ] Automatic retry with exponential backoff

### 7. Loading States

**Test loading indicators**:

1. **Initial Load**:

   - [ ] Skeleton screens display
   - [ ] Smooth transition to actual content

2. **Background Refresh**:

   - [ ] Previous data stays visible
   - [ ] Updates seamlessly when new data arrives

3. **Filter Changes**:
   - [ ] Loading state appears
   - [ ] Results update correctly

### 8. Browser Console

Open browser DevTools console (F12).

**Check for**:

- [ ] No error messages (red)
- [ ] No warning messages (yellow)
- [ ] Network requests complete successfully
- [ ] No CORS errors

**Network Tab**:

- [ ] POST requests to `http://localhost:8000/tools/*` succeed (200 status)
- [ ] Response times are reasonable (<5s for analysis)
- [ ] No failed requests (4xx, 5xx)

## Performance Testing

### 1. Response Times

Measure endpoint response times:

```bash
time curl -X POST http://localhost:8000/tools/analyze_call \
  -H "Content-Type: application/json" \
  -d '{"call_id": "YOUR_CALL_ID", "use_cache": true}'
```

**Expected Times** (with caching enabled):

- [ ] Analyze call: <2s (cached), <10s (uncached)
- [ ] Rep insights: <3s
- [ ] Search calls: <1s

### 2. Frontend Performance

Use Chrome DevTools Lighthouse:

1. Navigate to a page
2. Open DevTools > Lighthouse
3. Run audit

**Expected Scores**:

- [ ] Performance: >80
- [ ] Accessibility: >90
- [ ] Best Practices: >80
- [ ] SEO: >80

### 3. Cache Verification

1. Load call analysis page
2. Note loading time
3. Refresh page
4. Note loading time again

- [ ] Second load is faster (SWR cache hit)

## Integration Testing

### 1. End-to-End Flow

Complete user journey:

1. Start on homepage
2. Navigate to search page
3. Filter for high-scoring calls (>80)
4. Click "View Details" on a result
5. Review call analysis
6. Navigate to rep dashboard from call page
7. Review rep performance trends

- [ ] All pages load correctly
- [ ] Data is consistent across pages
- [ ] No errors in console
- [ ] Navigation works smoothly

### 2. Data Consistency

Compare data from API and UI:

1. Call `/tools/analyze_call` directly via curl
2. Load same call in UI
3. Verify scores match

- [ ] Overall score matches
- [ ] Dimension scores match
- [ ] Strengths/improvements match

### 3. Multiple Users

If authentication is enabled:

1. Sign in as Rep A
2. View Rep A's dashboard
3. Sign out
4. Sign in as Manager
5. View Rep A's dashboard

- [ ] Rep sees only their own data
- [ ] Manager sees any rep's data
- [ ] Authorization enforced correctly

## Troubleshooting Steps

If any test fails, check:

1. **Backend Logs**: Check terminal where REST API is running
2. **Frontend Logs**: Check terminal where Next.js is running
3. **Browser Console**: Check for JavaScript errors
4. **Network Tab**: Check for failed HTTP requests
5. **Database**: Verify data exists in tables
6. **Environment Variables**: Verify all .env files are configured

Common fixes:

- **CORS Error**: Verify CORS settings in `api/rest_server.py`
- **404 Not Found**: Verify REST API is running on port 8000
- **500 Server Error**: Check backend logs for Python errors
- **Empty Data**: Verify database is populated
- **Auth Error**: Check Clerk configuration

## Sign-Off

Once all tests pass:

- [ ] Backend tests: \_\_\_/6 passed
- [ ] Frontend tests: \_\_\_/8 passed
- [ ] Performance tests: \_\_\_/3 passed
- [ ] Integration tests: \_\_\_/3 passed

**Total**: \_\_\_/20 passed

**Tested by**: **\*\***\_\_\_\_**\*\***

**Date**: **\*\***\_\_\_\_**\*\***

**Notes**:

```
[Add any issues or observations here]
```

## Next Steps After Testing

Once all tests pass:

1. [ ] Document any issues found
2. [ ] Deploy to staging environment
3. [ ] Run tests again in staging
4. [ ] Deploy to production
5. [ ] Monitor production metrics
6. [ ] Gather user feedback

## Resources

- **Troubleshooting Guide**: See `FRONTEND_INTEGRATION.md`
- **Quick Start**: See `QUICKSTART_FRONTEND.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
