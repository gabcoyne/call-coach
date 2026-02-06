# API Optimization Summary

## Overview

This document summarizes the API performance optimizations and production features added to the Call Coaching API.

## Implementation Date

February 5, 2026

## Changes Made

### 1. Database Query Optimization

**Location**: `/Users/gcoyne/src/prefect/call-coach/db/performance/slow_queries.sql`

**Features**:

- EXPLAIN ANALYZE queries for common patterns
- Composite index recommendations:
  - `idx_calls_product_scheduled` - Call filtering by product and date
  - `idx_coaching_rep_created` - Rep performance queries
  - `idx_coaching_dimension_created` - Dimension-specific queries
  - `idx_call_opportunities_opp_id` - Opportunity timeline queries
  - `idx_emails_opportunity_sent` - Email lookups
  - `idx_speakers_email_company` - Rep email searches
  - `idx_transcripts_fts` - Full-text search optimization
  - `idx_transcripts_call_sequence` - Transcript retrieval
- Table statistics and maintenance queries
- Connection pooling monitoring
- Query performance analysis tools

**Benefits**:

- Faster query execution for filtered searches (2-10x improvement expected)
- Reduced database load from repeated queries
- Better query planner decisions with updated statistics

### 2. API Response Optimization

**Location**: `/Users/gcoyne/src/prefect/call-coach/middleware/compression.py`

**Features**:

- Automatic gzip compression for responses > 500 bytes
- Content-Type aware compression (JSON, HTML, XML, etc.)
- Configurable compression level (default: 6)
- Client negotiation via Accept-Encoding header
- Proper Vary and Content-Encoding headers

**Benefits**:

- 60-80% reduction in response size for JSON payloads
- Faster page loads and API responses
- Reduced bandwidth costs

### 3. Pagination Support

**Location**: `/Users/gcoyne/src/prefect/call-coach/db/pagination.py`

**Features**:

- Offset-based pagination with page/page_size parameters
- Cursor-based pagination for infinite scrolling
- Generic PaginatedResult type with metadata (total, has_next, etc.)
- Helper functions for adding pagination to queries

**Benefits**:

- Reduced memory usage for large result sets
- Faster initial page loads
- Better user experience with progressive loading

### 4. Rate Limiting

**Location**: `/Users/gcoyne/src/prefect/call-coach/middleware/rate_limit.py`

**Features**:

- Token bucket algorithm with configurable rates
- Per-user rate limits (identified by email, API key, or IP)
- Per-endpoint rate limits with different tiers:
  - General endpoints: 100 req/min (burst: 150)
  - Expensive endpoints: 20 req/min (burst: 30)
- Standard rate limit headers (X-RateLimit-\*)
- Automatic bucket cleanup for inactive users

**Expensive Endpoints**:

- `/tools/analyze_call`
- `/tools/analyze_opportunity`
- `/tools/get_learning_insights`

**Benefits**:

- Protection against abuse and DoS attacks
- Fair resource allocation across users
- Predictable API behavior under load

### 5. API Versioning

**Location**: `/Users/gcoyne/src/prefect/call-coach/api/v1/`

**Features**:

- Versioned endpoints under `/api/v1/` prefix
- Separate request/response schemas per version
- Version field in all responses
- Backward compatibility guarantees
- Deprecation warning support

**Endpoints Versioned**:

- `POST /api/v1/tools/analyze_call`
- `POST /api/v1/tools/get_rep_insights`
- `POST /api/v1/tools/search_calls` (with pagination)
- `POST /api/v1/tools/analyze_opportunity`
- `POST /api/v1/tools/get_learning_insights`

**Benefits**:

- Safe API evolution without breaking clients
- Clear migration path for frontend
- Ability to test new features alongside stable API

### 6. Error Handling

**Location**: `/Users/gcoyne/src/prefect/call-coach/api/error_handlers.py`

**Features**:

- Standardized error response format:

  ```json
  {
    "error": "error_code",
    "message": "Human-readable message",
    "details": {...},
    "request_id": "uuid"
  }
  ```

- Specialized handlers for:
  - HTTP exceptions (4xx/5xx)
  - Validation errors (422)
  - Database errors (503 for transient, 500 for permanent)
  - General exceptions (500)
- Retry logic for transient errors (exponential backoff)
- Error tracking integration hooks (ready for Sentry)
- Request ID tracking through error chain

**Benefits**:

- Consistent error experience for frontend
- Easier debugging with request IDs
- Automatic retry for transient failures
- Better error visibility and tracking

### 7. Performance Monitoring

**Location**: `/Users/gcoyne/src/prefect/call-coach/api/monitoring.py`

**Features**:

- Real-time metrics collection:
  - Request counts per endpoint
  - Response time percentiles (p50, p95, p99)
  - Error rates by status code
  - Rate limit hits by endpoint
- Monitoring endpoints:
  - `GET /monitoring/health` - Health check for load balancers
  - `GET /monitoring/metrics` - Comprehensive metrics
  - `GET /monitoring/metrics/endpoint/{path}` - Endpoint-specific metrics
  - `GET /monitoring/metrics/database` - Database performance
  - `GET /monitoring/metrics/rate-limits` - Rate limiting stats
- Thread-safe metrics collector
- Configurable sample size for percentile calculations

**Benefits**:

- Real-time visibility into API performance
- Early detection of performance degradation
- Data-driven optimization decisions
- Integration with monitoring tools (Prometheus, Datadog, etc.)

### 8. Enhanced REST Server

**Location**: `/Users/gcoyne/src/prefect/call-coach/api/rest_server.py`

**Changes**:

- Integrated all middleware components
- Added request ID generation and propagation
- Added response time tracking
- Structured logging with context
- Exposed rate limit headers
- Integrated error handlers
- Included v1 versioned API routes

**New Headers**:

- `X-Request-ID` - Unique request identifier
- `X-Response-Time` - Response time in milliseconds
- `X-RateLimit-Limit` - Rate limit capacity
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp
- `Content-Encoding: gzip` - Compression indicator

## Performance Impact

### Expected Improvements

1. **Database Queries**: 2-10x faster for filtered queries with indexes
2. **Response Size**: 60-80% reduction with gzip compression
3. **API Latency**: 20-40% reduction from compression and pagination
4. **Error Recovery**: Automatic retry reduces failed requests by 50-70%

### Resource Usage

1. **Memory**: +10-20 MB for rate limit buckets and metrics
2. **CPU**: +5-10% for compression (offset by reduced network I/O)
3. **Database**: Reduced query load from indexes and pagination

## Migration Guide

### For Frontend Developers

1. **Use Versioned Endpoints**:

   ```typescript
   // Old (still works)
   POST / tools / analyze_call;

   // New (recommended)
   POST / api / v1 / tools / analyze_call;
   ```

2. **Handle Rate Limits**:

   ```typescript
   if (response.status === 429) {
     const retryAfter = response.headers.get("Retry-After");
     // Wait and retry
   }
   ```

3. **Use Pagination**:

   ```typescript
   // Search calls with pagination
   POST /api/v1/tools/search_calls
   {
     "limit": 20,
     "offset": 0
   }

   // Response includes pagination metadata
   {
     "api_version": "v1",
     "data": {
       "items": [...],
       "total": 100,
       "page": 0,
       "page_size": 20,
       "has_next": true
     }
   }
   ```

4. **Handle Errors Consistently**:

   ```typescript
   try {
     const response = await fetch('/api/v1/tools/analyze_call', ...);
     const data = await response.json();

     if (!response.ok) {
       // All errors have consistent format
       console.error(`Error ${data.error}: ${data.message}`);
       console.error('Request ID:', data.request_id);
     }
   } catch (error) {
     // Network errors
   }
   ```

### For DevOps/Deployment

1. **Database Indexes**:

   ```bash
   # Run index creation (CONCURRENTLY to avoid locks)
   psql $DATABASE_URL -f db/performance/slow_queries.sql
   ```

2. **Monitoring Setup**:

   ```bash
   # Health check for load balancer
   curl http://api:8000/monitoring/health

   # Prometheus metrics endpoint (TODO: add /metrics export)
   curl http://api:8000/monitoring/metrics
   ```

3. **Rate Limit Configuration**:

   ```python
   # In rest_server.py, adjust as needed:
   app.add_middleware(
       RateLimitMiddleware,
       default_rate_limit=100,  # requests per minute
       expensive_rate_limit=20,
   )
   ```

## Testing

### Manual Testing

1. **Rate Limiting**:

   ```bash
   # Send 100+ requests quickly
   for i in {1..110}; do
     curl -w "\n" http://localhost:8000/tools/analyze_call \
       -H "Content-Type: application/json" \
       -d '{"call_id": "test"}' &
   done
   wait

   # Should see 429 responses after limit
   ```

2. **Compression**:

   ```bash
   # Request with gzip support
   curl -H "Accept-Encoding: gzip" \
     http://localhost:8000/tools/search_calls \
     -d '{"limit": 50}' --compressed -v

   # Should see Content-Encoding: gzip header
   ```

3. **Monitoring**:

   ```bash
   # Check metrics
   curl http://localhost:8000/monitoring/metrics | jq

   # Check database health
   curl http://localhost:8000/monitoring/metrics/database | jq
   ```

### Automated Tests

TODO: Add test suite covering:

- Rate limit enforcement
- Compression for different content types
- Pagination edge cases
- Error response format consistency
- Database index usage (EXPLAIN output)

## Future Enhancements

1. **Response Caching**:

   - Add ETag support for conditional requests
   - Cache-Control headers for static responses
   - Redis-backed response cache

2. **Request Tracing**:

   - Distributed tracing with OpenTelemetry
   - Correlation IDs across services
   - Trace context propagation

3. **Advanced Rate Limiting**:

   - Redis-backed rate limiter for multi-instance deployment
   - Rate limit by API key tier (free/premium)
   - Dynamic rate limits based on load

4. **Metrics Export**:

   - Prometheus /metrics endpoint
   - StatsD integration
   - Custom metrics for business logic

5. **Query Optimization**:
   - Query result caching
   - Database read replicas
   - Materialized views for analytics

## Contact

For questions or issues related to these optimizations, contact the api-optimization-agent or review the implementation in:

- `/Users/gcoyne/src/prefect/call-coach/middleware/`
- `/Users/gcoyne/src/prefect/call-coach/api/v1/`
- `/Users/gcoyne/src/prefect/call-coach/db/performance/`
