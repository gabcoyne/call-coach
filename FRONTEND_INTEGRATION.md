# Frontend Integration Guide

This guide explains how the Next.js frontend connects to the FastMCP backend tools.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Next.js App    │  HTTP   │  REST API Bridge │  Python │  MCP Tools       │
│  (Port 3000)    ├────────>│  (Port 8000)     ├────────>│  (Backend Logic) │
│                 │  POST   │  FastAPI Server  │  Calls  │  analyze_call    │
│  React + SWR    │         │  CORS enabled    │         │  get_rep_insights│
└─────────────────┘         └──────────────────┘         │  search_calls    │
                                                          └──────────────────┘
```

## Components

### 1. REST API Bridge (`/api/rest_server.py`)

FastAPI server that exposes MCP tools as REST HTTP endpoints:

- **Endpoint Pattern**: `POST /tools/{tool_name}`
- **CORS**: Configured for Next.js (localhost:3000, Vercel)
- **Error Handling**: Consistent JSON error responses
- **Type Safety**: Pydantic models for request/response validation

Available endpoints:

- `POST /tools/analyze_call` - Analyze a specific call
- `POST /tools/get_rep_insights` - Get rep performance trends
- `POST /tools/search_calls` - Search calls with filters
- `POST /tools/analyze_opportunity` - Analyze opportunity patterns
- `POST /tools/get_learning_insights` - Compare to top performers

### 2. MCP Client (`/frontend/lib/mcp-client.ts`)

TypeScript HTTP client for calling the REST API:

```typescript
const mcpClient = new MCPClient("http://localhost:8000");

// Example usage
const analysis = await mcpClient.analyzeCall({
  call_id: "call-123",
  use_cache: true,
  include_transcript_snippets: true,
});
```

Features:

- **Retry Logic**: Exponential backoff for network errors
- **Type Safety**: Full TypeScript interfaces
- **Error Handling**: MCPClientError with status codes

### 3. React Hooks (`/frontend/lib/hooks/`)

SWR-based hooks for data fetching with caching:

- `useCallAnalysis(callId)` - Fetch call analysis
- `useRepInsights(email, options)` - Fetch rep performance
- `useSearchCalls(filters)` - Search calls with debouncing

Features:

- **Automatic Caching**: SWR handles cache invalidation
- **Loading States**: Built-in loading/error states
- **Revalidation**: Background data refresh
- **Optimistic Updates**: UI updates before server response

### 4. UI Pages

#### Call Analysis Page (`/frontend/app/calls/[callId]/page.tsx`)

Displays comprehensive call analysis with:

- Call metadata (date, duration, participants)
- Dimension scores (product knowledge, discovery, etc.)
- Strengths and areas for improvement
- Specific examples from transcript
- Action items with priorities

#### Rep Dashboard (`/frontend/app/dashboard/[repEmail]/page.tsx`)

Shows rep performance trends:

- Overall score and call count
- Score trends over time (line chart)
- Dimension breakdown (score cards)
- Recent calls list

#### Search Page (`/frontend/app/search/page.tsx`)

Filter and search calls:

- Date range filter
- Rep email filter (managers only)
- Call type multi-select
- Minimum score slider
- Keyword search (debounced)
- Paginated results table

## Setup Instructions

### 1. Start the REST API Server

```bash
# Option 1: Using the startup script
./scripts/start-rest-api.sh

# Option 2: Manually with uvicorn
uv run uvicorn api.rest_server:app --host 0.0.0.0 --port 8000 --reload

# The server will be available at http://localhost:8000
# Health check: curl http://localhost:8000/health
```

### 2. Configure Environment Variables

Create `/frontend/.env.local`:

```bash
# MCP Backend
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000

# Clerk Auth (for user authentication)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:3000
```

## Testing the Integration

### 1. Test REST API Directly

```bash
# Health check
curl http://localhost:8000/health

# Analyze a call
curl -X POST http://localhost:8000/tools/analyze_call \
  -H "Content-Type: application/json" \
  -d '{"call_id": "1464927526043145564", "use_cache": true}'

# Get rep insights
curl -X POST http://localhost:8000/tools/get_rep_insights \
  -H "Content-Type: application/json" \
  -d '{"rep_email": "sarah.jones@prefect.io", "time_period": "last_30_days"}'

# Search calls
curl -X POST http://localhost:8000/tools/search_calls \
  -H "Content-Type: application/json" \
  -d '{"min_score": 70, "limit": 10}'
```

### 2. Test Frontend Pages

1. **Call Analysis**: Navigate to `http://localhost:3000/calls/{call_id}`

   - Should show loading skeleton
   - Then display full analysis with scores
   - Error handling with retry button

2. **Rep Dashboard**: Navigate to `http://localhost:3000/dashboard/{email}`

   - Shows performance trends
   - Score charts render correctly
   - Recent calls are listed

3. **Search**: Navigate to `http://localhost:3000/search`
   - Filter controls work
   - Results update on filter change
   - Pagination works

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:

```
Access to fetch at 'http://localhost:8000/tools/analyze_call' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution**: Verify CORS is configured in `/api/rest_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection Refused

If frontend can't connect to backend:

```
Failed to fetch: net::ERR_CONNECTION_REFUSED
```

**Solution**: Ensure REST API server is running on port 8000:

```bash
# Check if server is running
curl http://localhost:8000/health

# If not running, start it
./scripts/start-rest-api.sh
```

### Database Connection Errors

If you see database errors in REST API logs:

```
psycopg2.OperationalError: connection to server failed
```

**Solution**: Verify `DATABASE_URL` in `.env`:

```bash
# Must include sslmode=require for Neon
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Import Errors

If REST API fails to import modules:

```
ModuleNotFoundError: No module named 'coaching_mcp'
```

**Solution**: Install dependencies with uv:

```bash
uv sync
```

## Data Flow Example

Here's how a call analysis request flows through the system:

1. **User Action**: User navigates to `/calls/call-123`
2. **React Component**: `CallAnalysisViewer` renders
3. **SWR Hook**: `useCallAnalysis('call-123')` is called
4. **HTTP Request**: MCP client sends `POST /tools/analyze_call`
5. **REST API**: FastAPI receives request, validates with Pydantic
6. **MCP Tool**: `analyze_call_tool()` is called with parameters
7. **Backend Logic**: Analysis runs (database queries, Claude API calls)
8. **Response**: JSON response sent back through chain
9. **UI Update**: React component renders analysis data
10. **Cache**: SWR caches result for 5 minutes

## Performance Considerations

### Caching Strategy

- **Backend Cache**: Analysis results cached in database (60-80% cost reduction)
- **HTTP Cache**: SWR caches responses in browser (5-minute TTL)
- **Debouncing**: Search input debounced (300ms delay)

### Loading States

- **Skeleton Screens**: Shown during initial load
- **Keep Previous Data**: SWR shows stale data while revalidating
- **Progressive Loading**: Charts render as data arrives

### Error Recovery

- **Exponential Backoff**: Automatic retries with increasing delays
- **Error Boundaries**: React error boundaries catch render errors
- **Retry Buttons**: Manual retry option for failed requests

## Deployment Notes

### Production Deployment

For production, update environment variables:

```bash
# Frontend .env.production
NEXT_PUBLIC_MCP_BACKEND_URL=https://api.yourcompany.com

# Backend deployment
# Deploy REST API to Vercel/Railway/Fly.io
# Ensure CORS includes production domain
```

### Monitoring

Monitor these metrics in production:

- **API Response Times**: Track `/tools/*` endpoint latency
- **Error Rates**: Monitor 4xx/5xx responses
- **Cache Hit Rates**: Track cache effectiveness
- **Database Connections**: Monitor connection pool usage

## API Reference

See `/api/rest_server.py` for complete API documentation with Pydantic models.

FastAPI automatically generates interactive docs at:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
