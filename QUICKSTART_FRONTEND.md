# Frontend Quick Start Guide

Get the call coaching UI running in 5 minutes.

## Prerequisites

- Python 3.11+ with `uv` installed
- Node.js 18+ with `npm` installed
- Neon database with `DATABASE_URL` configured
- API keys in `.env` file

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Verify Environment Variables

Check your `.env` file has:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Gong API (optional for testing)
GONG_API_KEY=...
GONG_API_SECRET=...
GONG_API_BASE_URL=https://api.gong.io
```

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

### 3. Start the Backend API

Option 1 - Using Make:

```bash
make rest-api
```

Option 2 - Using Script:

```bash
./scripts/start-rest-api.sh
```

Option 3 - Manually:

```bash
uv run uvicorn api.rest_server:app --host 0.0.0.0 --port 8000 --reload
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

### 4. Test the Backend

In a new terminal:

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"ok","service":"call-coaching-api","tools":5}
```

### 5. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

You should see:

```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in 2.5s
```

### 6. Open the App

Navigate to: <http://localhost:3000>

You should see the Call Coach dashboard.

## Test with Sample Data

### View a Call Analysis

1. Navigate to: <http://localhost:3000/calls/1464927526043145564>
2. You should see:
   - Call metadata (date, duration, participants)
   - Performance scores (overall, dimensions)
   - Strengths and improvement areas
   - Specific examples from the call
   - Action items

### View Rep Dashboard

1. Navigate to: <http://localhost:3000/dashboard/sarah.jones@prefect.io>
2. You should see:
   - Performance overview
   - Score trends over time
   - Dimension breakdown
   - Recent calls list

### Search Calls

1. Navigate to: <http://localhost:3000/search>
2. Try filtering by:
   - Date range
   - Minimum score (use slider)
   - Keyword search

## Troubleshooting

### Backend Not Starting

**Error**: `ModuleNotFoundError: No module named 'api'`

**Fix**: Make sure you're in the project root directory:

```bash
cd /Users/gcoyne/src/prefect/call-coach
uv run uvicorn api.rest_server:app --reload
```

### Frontend Can't Connect

**Error**: Browser console shows `Failed to fetch`

**Fix**: Ensure backend is running on port 8000:

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
make rest-api
```

### CORS Errors

**Error**: Browser console shows `CORS policy blocked`

**Fix**: Verify CORS settings in `/api/rest_server.py` include your frontend URL.

### Database Connection Failed

**Error**: Backend logs show `psycopg2.OperationalError`

**Fix**: Verify DATABASE_URL in `.env`:

```bash
# Must include sslmode=require
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### No Calls Found

**Error**: Empty data in UI

**Fix**: Load sample data:

```bash
# Run Gong sync to populate database
uv run python flows/daily_gong_sync.py
```

## Development Workflow

### Making Changes

1. **Backend Changes**: REST API auto-reloads on file save
2. **Frontend Changes**: Next.js auto-reloads on file save
3. **Database Changes**: Restart backend after migrations

### Viewing Logs

Backend logs appear in terminal where you ran `make rest-api`:

```bash
INFO:     127.0.0.1:54321 - "POST /tools/analyze_call HTTP/1.1" 200 OK
```

Frontend logs appear in terminal where you ran `npm run dev`:

```bash
○ Compiling /calls/[callId]/page ...
✓ Compiled in 1.2s
```

Browser console shows client-side errors.

### Testing API Endpoints Directly

Use curl or Postman to test endpoints:

```bash
# Analyze call
curl -X POST http://localhost:8000/tools/analyze_call \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "1464927526043145564",
    "use_cache": true,
    "include_transcript_snippets": true
  }'

# Get rep insights
curl -X POST http://localhost:8000/tools/get_rep_insights \
  -H "Content-Type: application/json" \
  -d '{
    "rep_email": "sarah.jones@prefect.io",
    "time_period": "last_30_days"
  }'

# Search calls
curl -X POST http://localhost:8000/tools/search_calls \
  -H "Content-Type: application/json" \
  -d '{
    "min_score": 70,
    "limit": 10
  }'
```

## Next Steps

- **Add Authentication**: Configure Clerk for user authentication
- **Deploy to Production**: See FRONTEND_INTEGRATION.md for deployment guide
- **Customize UI**: Edit components in `frontend/components/`
- **Add Features**: Create new MCP tools and expose via REST API

## Common Commands

```bash
# Start backend
make rest-api

# Start frontend
make frontend

# Start both (experimental)
make dev-full

# Run tests
uv run pytest tests/

# Format code
uv run black .

# Check database
psql $DATABASE_URL
```

## Getting Help

- **Backend Issues**: Check `api/rest_server.py` logs
- **Frontend Issues**: Check browser console and Next.js logs
- **Database Issues**: Check `db/` directory for schema
- **Integration Guide**: See `FRONTEND_INTEGRATION.md` for detailed architecture

## Architecture Overview

```
┌─────────────────────┐
│   Next.js Frontend  │  http://localhost:3000
│   - React + SWR     │
│   - TypeScript      │
└──────────┬──────────┘
           │ HTTP POST /tools/*
           ▼
┌─────────────────────┐
│   REST API Bridge   │  http://localhost:8000
│   - FastAPI         │
│   - CORS enabled    │
└──────────┬──────────┘
           │ Python calls
           ▼
┌─────────────────────┐
│   MCP Tools         │
│   - analyze_call    │
│   - get_rep_insights│
│   - search_calls    │
└──────────┬──────────┘
           │ SQL queries
           ▼
┌─────────────────────┐
│   Neon Database     │
│   - calls           │
│   - coaching_sessions│
│   - opportunities   │
└─────────────────────┘
```

Happy coding!
