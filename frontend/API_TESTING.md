# API Bridge Testing Guide

This document provides step-by-step instructions for testing the Next.js API routes that bridge to the MCP backend.

## Prerequisites

1. **MCP Backend Running**: Ensure the FastMCP coaching backend is running locally

   ```bash
   # From project root
   fastmcp dev
   # Or use the configured command
   uv run python -m coaching_mcp.server
   ```

2. **Environment Variables**: Ensure `.env.local` has the correct MCP backend URL

   ```bash
   NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000
   ```

3. **Database**: Ensure Neon database has processed calls and coaching sessions

   ```bash
   # Verify with psql or database client
   SELECT COUNT(*) FROM calls WHERE processed_at IS NOT NULL;
   SELECT COUNT(*) FROM coaching_sessions;
   ```

4. **Authentication**: Ensure you have a valid Clerk session (sign in first)

## Test Cases

### 1. Analyze Call Endpoint

**Endpoint**: `POST /api/coaching/analyze-call`

**Test Case 1.1: Successful Analysis**

```bash
curl -X POST http://localhost:3000/api/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-clerk-session-cookie>" \
  -d '{
    "call_id": "1464927526043145564",
    "dimensions": ["discovery", "engagement"],
    "use_cache": true,
    "include_transcript_snippets": true
  }'
```

**Expected Response**: 200 OK with analysis data

```json
{
  "call_metadata": {
    "id": "1464927526043145564",
    "title": "Discovery Call - Acme Corp",
    "date": "2025-01-15T10:00:00Z",
    ...
  },
  "scores": {
    "discovery": 85,
    "engagement": 78,
    "overall": 81
  },
  "strengths": [...],
  "areas_for_improvement": [...],
  ...
}
```

**Test Case 1.2: Invalid Call ID**

```bash
curl -X POST http://localhost:3000/api/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-clerk-session-cookie>" \
  -d '{
    "call_id": "invalid-id"
  }'
```

**Expected Response**: 400 Bad Request or 404 Not Found

**Test Case 1.3: Rate Limit Exceeded**

```bash
# Make 11+ requests in rapid succession
for i in {1..15}; do
  curl -X POST http://localhost:3000/api/coaching/analyze-call \
    -H "Content-Type: application/json" \
    -H "Cookie: <your-clerk-session-cookie>" \
    -d '{"call_id": "1464927526043145564"}'
done
```

**Expected Response**: After 10 requests, 429 Too Many Requests

```json
{
  "error": "Rate limit exceeded"
}
```

**Headers**:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: <timestamp>
```

### 2. Rep Insights Endpoint

**Endpoint**: `POST /api/coaching/rep-insights`

**Test Case 2.1: Successful Insights (Manager)**

```bash
curl -X POST http://localhost:3000/api/coaching/rep-insights \
  -H "Content-Type: application/json" \
  -H "Cookie: <manager-clerk-session-cookie>" \
  -d '{
    "rep_email": "john.doe@prefect.io",
    "time_period": "last_30_days",
    "product_filter": "prefect"
  }'
```

**Expected Response**: 200 OK with rep insights

```json
{
  "rep_info": {
    "name": "John Doe",
    "email": "john.doe@prefect.io",
    "calls_analyzed": 15,
    ...
  },
  "score_trends": {
    "discovery": {
      "dates": ["2025-01-01", "2025-01-08", ...],
      "scores": [75, 78, 82, ...],
      ...
    }
  },
  "skill_gaps": [...],
  ...
}
```

**Test Case 2.2: Rep Accessing Own Data**

```bash
curl -X POST http://localhost:3000/api/coaching/rep-insights \
  -H "Content-Type: application/json" \
  -H "Cookie: <rep-clerk-session-cookie>" \
  -d '{
    "rep_email": "jane.smith@prefect.io"
  }'
```

**Expected Response**: 200 OK if email matches authenticated user, 403 Forbidden otherwise

**Test Case 2.3: Invalid Email**

```bash
curl -X POST http://localhost:3000/api/coaching/rep-insights \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-clerk-session-cookie>" \
  -d '{
    "rep_email": "invalid-email"
  }'
```

**Expected Response**: 400 Bad Request

```json
{
  "error": "Invalid request parameters",
  "details": {
    "rep_email": {
      "_errors": ["Valid email address required"]
    }
  }
}
```

### 3. Search Calls Endpoint

**Endpoint**: `POST /api/coaching/search-calls`

**Test Case 3.1: Basic Search**

```bash
curl -X POST http://localhost:3000/api/coaching/search-calls \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-clerk-session-cookie>" \
  -d '{
    "product": "prefect",
    "call_type": "discovery",
    "limit": 10
  }'
```

**Expected Response**: 200 OK with array of calls

```json
[
  {
    "call_id": "1464927526043145564",
    "title": "Discovery Call - Acme Corp",
    "date": "2025-01-15T10:00:00Z",
    "overall_score": 85,
    ...
  },
  ...
]
```

**Test Case 3.2: Search with Score Filter**

```bash
curl -X POST http://localhost:3000/api/coaching/search-calls \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-clerk-session-cookie>" \
  -d '{
    "min_score": 80,
    "max_score": 95,
    "limit": 20
  }'
```

**Test Case 3.3: Search with Date Range**

```bash
curl -X POST http://localhost:3000/api/coaching/search-calls \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-clerk-session-cookie>" \
  -d '{
    "date_range": {
      "start": "2025-01-01T00:00:00Z",
      "end": "2025-01-31T23:59:59Z"
    },
    "limit": 15
  }'
```

**Test Case 3.4: Rep Auto-Filtering**

```bash
# As a rep (not manager), search should auto-filter to own calls
curl -X POST http://localhost:3000/api/coaching/search-calls \
  -H "Content-Type: application/json" \
  -H "Cookie: <rep-clerk-session-cookie>" \
  -d '{
    "limit": 20
  }'
```

**Expected Response**: Only returns calls where the authenticated rep participated

## Manual Testing with Browser

### Using Browser DevTools

1. **Sign in to the application** at `http://localhost:3000`
2. **Open DevTools** (F12) and go to Network tab
3. **Open Console** and run:

```javascript
// Test analyze-call
fetch("/api/coaching/analyze-call", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    call_id: "1464927526043145564",
    dimensions: ["discovery"],
  }),
})
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);

// Test rep-insights
fetch("/api/coaching/rep-insights", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    rep_email: "your-email@prefect.io",
    time_period: "last_30_days",
  }),
})
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);

// Test search-calls
fetch("/api/coaching/search-calls", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    product: "prefect",
    limit: 10,
  }),
})
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);
```

## Observability and Logging

### Check Logs

All API requests are logged to the console. Look for:

```json
{
  "timestamp": "2025-02-05T18:45:00.000Z",
  "level": "info",
  "endpoint": "/api/coaching/analyze-call",
  "method": "POST",
  "userId": "user_xyz123",
  "statusCode": 200,
  "duration": 1234,
  "metadata": {
    "call_id": "1464927526043145564",
    "overall_score": 85
  }
}
```

### Monitor Rate Limits

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1738782360000
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**

   - Ensure you're signed in via Clerk
   - Check that Clerk environment variables are set correctly

2. **403 Forbidden**

   - Verify RBAC rules (reps can only access own data)
   - Check user role in Clerk metadata

3. **429 Rate Limit Exceeded**

   - Wait for rate limit window to reset
   - Check `X-RateLimit-Reset` header for reset time

4. **500 Internal Server Error**

   - Check that MCP backend is running
   - Verify `NEXT_PUBLIC_MCP_BACKEND_URL` environment variable
   - Check backend logs for errors
   - Ensure database connection is working

5. **MCP Backend Connection Failed**
   - Verify MCP server is running: `curl http://localhost:8000/health`
   - Check network connectivity
   - Verify backend URL configuration

## Performance Testing

### Load Testing with Apache Bench

```bash
# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -p test-payload.json -T application/json \
  -H "Cookie: <your-session-cookie>" \
  http://localhost:3000/api/coaching/search-calls
```

### Expected Performance

- **Analyze Call**: 1-5 seconds (depending on cache)
- **Rep Insights**: 500ms-2 seconds
- **Search Calls**: 100ms-1 second

## Success Criteria

All tests should pass with:

- ✅ Correct HTTP status codes
- ✅ Valid JSON responses matching TypeScript types
- ✅ Proper authentication enforcement
- ✅ RBAC rules enforced
- ✅ Rate limiting working
- ✅ Request/response logging visible
- ✅ Error handling graceful
