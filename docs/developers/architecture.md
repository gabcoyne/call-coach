# System Architecture

High-level overview of the Call Coach system design, components, and data flow.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Call Coach Architecture                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Gong Webhooks │
│   & API         │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Webhook Server (Port 8000)                             │
│  - Receives Gong webhooks                                        │
│  - HMAC signature verification                                   │
│  - Idempotency check (via gong_webhook_id)                       │
│  - Triggers Prefect flow                                         │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Prefect Flow: process_new_call                                  │
│  - Fetch call metadata from Gong                                 │
│  - Fetch transcript from Gong                                    │
│  - Extract speakers and metadata                                 │
│  - Store in PostgreSQL                                           │
│  - Queue for analysis                                            │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Analysis Engine (Claude API)                                    │
│  - Chunk long transcripts                                        │
│  - Check cache for previous analysis                             │
│  - Call Claude API for analysis                                  │
│  - Extract coaching insights                                     │
│  - Store results in database                                     │
│  - Update cache                                                  │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Data Layer: PostgreSQL (Neon)                                   │
│  - Calls, transcripts, speakers                                  │
│  - Coaching sessions and analysis runs                           │
│  - Cache entries                                                 │
│  - Webhook events (audit trail)                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
┌───────────────────────────────┐   ┌──────────────────────────┐
│  REST API (Port 8001)         │   │  FastMCP Server (Port8000)│
│  - analyze_call               │   │  - MCP protocol endpoint  │
│  - get_rep_insights           │   │  - Claude Desktop support │
│  - search_calls               │   │  - Same tools as REST API │
└───────────────────────────────┘   └──────────────────────────┘
         │                                     │
         └──────────────┬──────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Next.js Frontend           │
         │   - React components         │
         │   - Clerk authentication     │
         │   - Dashboard, search, feed  │
         │   - Port 3000                │
         └──────────────────────────────┘
```

## Components

### 1. Gong Integration

**Location**: `gong/`

**Responsibility**: Integrate with Gong API

**Key Files**:
- `client.py` - Gong API client with retry logic
- `webhook.py` - Webhook receiver with HMAC verification
- `types.py` - Type definitions (Call, Transcript, Speaker)

**Features**:
- Get call metadata (title, participants, duration)
- Fetch full transcript with speaker turns
- Verify webhook signatures
- Handle authentication

**Example Usage**:
```python
from gong.client import GongClient

with GongClient() as client:
    call = client.get_call("gong_call_id")
    transcript = client.get_transcript("gong_call_id")
```

### 2. Webhook Server

**Location**: Root level (webhook handling in FastAPI)

**Port**: 8000

**Responsibility**: Receive and validate Gong webhooks

**Flow**:
1. Receive webhook from Gong
2. Verify HMAC signature
3. Check idempotency (gong_webhook_id)
4. Trigger Prefect flow for processing
5. Return 200 OK immediately

**Response Time**: <500ms (critical SLA)

### 3. Prefect Flows

**Location**: `flows/`

**Responsibility**: Orchestrate call processing pipeline

**Key Flows**:

**process_new_call.py**
- Triggered by webhook
- Tasks:
  1. Fetch call metadata from Gong
  2. Fetch transcript from Gong
  3. Store call in database
  4. Store speakers and transcripts
  5. Queue for analysis
- Retries on failure
- Logs all steps

**weekly_review.py**
- Scheduled weekly (Monday 6 AM PT)
- Tasks:
  1. Query calls from past week
  2. Aggregate analysis results
  3. Calculate team metrics
  4. Generate reports
  5. Send notifications

### 4. Analysis Engine

**Location**: `analysis/`

**Responsibility**: Generate coaching insights using Claude

**Key Components**:

**engine.py** - Main orchestration
```
Input: Transcript
  ↓
Chunk transcript (if > 4K tokens)
  ↓
Check cache (by transcript_hash)
  ↓
Analyze 4 dimensions in parallel:
  ├─ Discovery (using prompt)
  ├─ Product Knowledge (using prompt)
  ├─ Objection Handling (using prompt)
  └─ Engagement (using prompt)
  ↓
Combine results
  ↓
Output: Coaching insights for each dimension
```

**chunking.py** - Handle long transcripts
- Sliding window with 20% overlap
- Token counting with tiktoken
- Handles 60+ minute calls (>80K tokens)
- Preserves context in chunks

**cache.py** - Intelligent result caching
- Key: `hash(transcript + dimension + rubric_version)`
- TTL: 30 days
- Hit rate: 60-80%
- Cost savings: 60-80%

**learning_insights.py** - Extract learning points
- Identify key themes
- Extract evidence with timestamps
- Generate recommendations

**opportunity_coaching.py** - Analyze patterns
- Recurring themes
- Opportunity identification
- Trend analysis

### 5. Database Layer

**Location**: `db/`

**Type**: PostgreSQL 15+

**Responsibility**: Persist all application data

**Key Tables**:

```
calls
├─ gong_call_id (unique)
├─ title, duration_seconds
├─ scheduled_at, created_at
├─ metadata (JSONB)
└─ processed_at

speakers (per call)
├─ name, email, role
├─ company_side (bool)
├─ talk_time_seconds
└─ call_id (FK)

transcripts (per call)
├─ speaker_id, sequence_number
├─ text, sentiment
├─ timestamp_seconds
├─ topics (array)
├─ chunk_metadata (JSONB)
└─ full_text_search (tsvector)

coaching_sessions
├─ call_id (FK)
├─ dimensions (JSONB)
├─ overall_score
├─ summary, key_themes
└─ created_at

analysis_runs
├─ call_id (FK)
├─ dimension, status
├─ score, findings
├─ recommendations
└─ timestamp

cache_keys
├─ key (unique)
├─ result (JSONB)
├─ ttl, created_at
└─ hits

webhook_events
├─ gong_webhook_id (unique, idempotency key)
├─ event_type, payload
├─ signature_valid, status
└─ timestamps
```

**Key Features**:
- Partitioned `coaching_sessions` table (quarterly)
- Indexes on critical queries
- Full-text search on transcripts
- JSONB for flexible metadata
- Audit trail via webhook_events

### 6. REST API

**Location**: `api/rest_server.py`

**Port**: 8001

**Framework**: FastAPI

**Endpoints**:
- `POST /coaching/analyze-call` - Analyze single call
- `POST /coaching/rep-insights` - Get rep performance
- `POST /coaching/search` - Search calls
- `GET /docs` - Swagger UI
- `GET /health` - Health check

**Features**:
- CORS middleware for frontend
- Request validation (Pydantic)
- Error handling and logging
- Rate limiting (production)

### 7. FastMCP Server

**Location**: `coaching_mcp/server.py`

**Port**: 8000

**Protocol**: Model Context Protocol (MCP)

**Tools Registered**:
1. `analyze_call` - Analyze call for coaching
2. `get_rep_insights` - Get rep performance
3. `search_calls` - Search calls

**Features**:
- Environment validation on startup
- Database connectivity check
- Gong API credential validation
- Claude API key validation
- Graceful error handling

**MCP Tools**:

**tools/analyze_call.py**
- Input: Gong call ID, focus area
- Output: Coaching analysis
- Calls: Gong API, Claude API, Database

**tools/get_rep_insights.py**
- Input: Rep email, time period
- Output: Performance metrics, trends
- Calls: Database, Claude API

**tools/search_calls.py**
- Input: Query, filters
- Output: Call results
- Calls: Database, full-text search

### 8. Frontend

**Location**: `frontend/`

**Framework**: Next.js 15 + React

**Port**: 3000

**Key Pages**:
- `/dashboard` - Rep performance dashboard
- `/calls/[callId]` - Call analysis viewer
- `/search` - Call search interface
- `/feed` - Coaching insights feed
- `/settings` - User settings

**Authentication**: Clerk

**Components**:
- SWR for data fetching
- Recharts for visualizations
- Shadcn/ui for components
- Tailwind CSS for styling

**API Integration**:
- Calls REST API at `$NEXT_PUBLIC_MCP_BACKEND_URL`
- Role-based UI (Manager vs Rep)
- Real-time updates

## Data Flow

### Call Processing Flow

```
1. Gong Call Completed
   ↓
2. Gong Sends Webhook
   ├─ URL: http://localhost:8000/webhooks/gong
   ├─ Method: POST
   └─ Headers: X-Gong-Signature (HMAC-SHA256)
   ↓
3. Webhook Server
   ├─ Verify HMAC signature
   ├─ Check gong_webhook_id for idempotency
   ├─ Store event in webhook_events table
   └─ Trigger Prefect flow
   ↓
4. Prefect Flow: process_new_call
   ├─ Task 1: fetch_call_from_gong
   │   └─ Get metadata (title, participants, duration)
   │
   ├─ Task 2: fetch_transcript_from_gong
   │   └─ Get full transcript with timestamps
   │
   ├─ Task 3: store_call_metadata
   │   └─ Create calls table entry
   │
   ├─ Task 4: store_speakers
   │   └─ Create speakers table entries
   │
   ├─ Task 5: store_transcripts
   │   └─ Create transcripts table entries
   │
   └─ Task 6: queue_for_analysis
       └─ Mark as ready for analysis
   ↓
5. Analysis Engine
   ├─ Fetch call and transcript from DB
   ├─ Check cache (transcript_hash)
   │
   ├─ If cache miss:
   │   ├─ Chunk transcript if needed
   │   ├─ Analyze 4 dimensions in parallel
   │   ├─ Call Claude API for each dimension
   │   ├─ Store results in coaching_sessions
   │   ├─ Store cache entry
   │   └─ Update webhook_events status
   │
   └─ If cache hit:
       └─ Return cached results
   ↓
6. Results Available
   ├─ coaching_sessions table updated
   ├─ Cache hit metrics recorded
   └─ Frontend can query results
```

### User Query Flow

```
1. Frontend User
   └─ "Analyze call 1464927526043145564"
   ↓
2. Next.js API Route
   └─ POST /api/coaching/analyze-call
   ↓
3. REST API Server
   └─ POST http://localhost:8001/coaching/analyze-call
   ↓
4. analyze_call Tool
   ├─ Fetch call from database
   ├─ Check cache
   ├─ If miss: Call analysis engine
   └─ Return results
   ↓
5. REST API Response
   └─ JSON with dimensions, scores, recommendations
   ↓
6. Next.js Response
   └─ Send to frontend
   ↓
7. Frontend Render
   └─ Display analysis with scores, findings, recommendations
```

## Key Design Decisions

### 1. Intelligent Caching

**Why**: Claude API calls are expensive (~$15 per 1M tokens)

**How**:
- Cache key: `hash(transcript + dimension + rubric_version)`
- TTL: 30 days
- Invalidated only when rubric version changes

**Result**: 60-80% cache hit rate, 80% cost reduction

### 2. Parallel Analysis

**Why**: 4 dimensions analyzed independently

**How**:
- Use Prefect's `ConcurrentTaskRunner`
- Each dimension analyzed in parallel
- Results combined after all complete

**Result**: 4x faster analysis, same cost

### 3. Transcript Chunking

**Why**: Claude has context limits (long calls > 4K tokens)

**How**:
- Sliding window with 20% overlap
- Token counting with tiktoken
- Analyze chunks separately
- Combine results

**Result**: Support for 60+ minute calls

### 4. Idempotency

**Why**: Gong webhooks might be retried

**How**:
- Use `gong_webhook_id` as unique key
- Check before processing
- Return success even if already processed

**Result**: Safe webhook handling, no duplicates

### 5. Real-Time Response

**Why**: Webhook must return <500ms

**How**:
- Webhook server immediately returns 200 OK
- Queue processing in Prefect flow
- Analysis happens asynchronously
- Results available when ready

**Result**: Fast webhook response, async analysis

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Webhook response | <500ms | Target SLA |
| Analyze call (cold) | 30-45s | Claude API call |
| Analyze call (cached) | <1s | From database |
| Get rep insights | 45-120s | Analyzes multiple calls |
| Search calls | 1-5s | Database query |
| Parse transcript | <2s | Chunking + storage |

## Scalability

### Horizontal Scaling

**Webhook Server**: Stateless, can scale horizontally
- Multiple instances behind load balancer
- Share PostgreSQL database
- No session state

**Analysis Engine**: Can handle 100+ calls/week
- Bottleneck: Claude API rate limits
- Could queue longer with Prefect
- Would need API rate increase

**REST API**: Handles 100+ concurrent users
- Neon connection pool (20 max)
- Stateless design

### Vertical Scaling

**Database**: PostgreSQL with partitioning
- Quarterly partitions for coaching_sessions
- Indexes on critical queries
- Full-text search for transcripts

**Memory**: Python processes use ~200MB each
- Efficient token counting with tiktoken
- Streaming responses when possible

## Security

### API Security

- HMAC-SHA256 webhook signature verification
- Gong API credentials never exposed in logs
- Claude API key validated but not logged
- Database credentials from environment only

### Database Security

- SSL required for Neon connections
- Parameterized queries (no SQL injection)
- Connection pooling with limits
- Row-level audit trail via webhook_events

### Frontend Security

- Clerk authentication on all pages
- JWT tokens validated
- Role-based access control (Manager vs Rep)
- CORS configured for trusted origins

## Monitoring & Observability

### Logging

- Python logging configured at INFO level
- Structured logs from Prefect flows
- Request logging in FastAPI
- Error tracking with stack traces

### Metrics

- Cache hit rate percentage
- Analysis latency (p50, p95, p99)
- API response times
- Database query performance
- Error rates by type

### Debugging

- Webhook events stored in database (audit trail)
- Analysis runs logged with status
- Full error messages in responses
- Request IDs for tracing

## Future Improvements

1. **Prompt Caching** - Cache knowledge base/rubrics with Claude
2. **Real-time Transcription** - Analyze calls as they happen
3. **Video Analysis** - Include visual cues from recordings
4. **Custom Rubrics** - Allow teams to define coaching dimensions
5. **ML Scoring** - Use ML models instead of Claude for speed
6. **Mobile App** - Native iOS/Android clients
7. **Slack Integration** - Share insights in Slack

---

**See also**: [Local Development Setup](./setup.md) | [API Reference](../api/endpoints.md) | [Troubleshooting](../troubleshooting/README.md)
