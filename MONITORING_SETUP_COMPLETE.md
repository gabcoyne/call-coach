# Monitoring and Observability Infrastructure - Complete

## Overview

Comprehensive monitoring and observability infrastructure has been successfully implemented for the Call Coach application. This includes error tracking, metrics collection, structured logging, performance profiling, and alerting capabilities.

## Implementation Summary

### 1. Sentry Error Tracking

**File**: `/Users/gcoyne/src/prefect/call-coach/monitoring/sentry.py`

Complete Sentry integration with:

- Exception capture with rich context (user ID, email, call_id, rep_id, opportunity_id, correlation_id)
- Message capturing for logging
- Breadcrumb tracking for request chains
- User context setting for error grouping
- Tag support for filtering and grouping errors
- Configurable error sampling rates for production
- Automatic integration with FastAPI and Starlette
- Performance profiling optional support

**Key Classes**:

- `SentryConfig` - Configuration and initialization
- Global functions: `capture_exception()`, `capture_message()`, `add_breadcrumb()`, `set_user_context()`, `set_tags()`

### 2. Prometheus Metrics

**File**: `/Users/gcoyne/src/prefect/call-coach/monitoring/metrics.py`

Comprehensive metrics collection tracking:

**API Metrics**:

- `api_requests_total` - Total requests by method, endpoint, status
- `api_request_duration_seconds` - Request latency with percentiles (p50, p95, p99)

**Claude API Metrics**:

- `claude_api_calls_total` - Total API calls by model and status
- `claude_input_tokens_total` - Input tokens sent
- `claude_output_tokens_total` - Output tokens received
- `claude_api_duration_seconds` - API call latency

**Cache Metrics**:

- `cache_hits_total` - Cache hits by type
- `cache_misses_total` - Cache misses by type
- `cache_size_bytes` - Current cache size
- Helper method: `get_cache_hit_rate()`

**Database Metrics**:

- `db_queries_total` - Total queries by operation and table
- `db_query_duration_seconds` - Query latency with percentiles
- `db_connections_active` - Active database connections

**Business Metrics**:

- `calls_analyzed_total` - Coaching analyses completed (by status)
- `coaching_sessions_created_total` - Sessions created
- `coaching_session_duration_seconds` - Session duration distribution

**Error Metrics**:

- `errors_total` - Total errors by type and source
- `gong_api_errors_total` - Gong API errors by type

**System Metrics**:

- `background_tasks_running` - Active background tasks

**Key Classes**:

- `MetricsCollector` - Main metrics collector with context managers
- Global functions: `get_metrics()`, `initialize_metrics()`, `track_api_call()` decorator

### 3. Structured Logging

**File**: `/Users/gcoyne/src/prefect/call-coach/instrumentation/logger.py`

JSON-formatted logging with full request tracing:

**Features**:

- Correlation ID generation and tracking via context variables
- Call ID, rep ID, user ID tracking across requests
- JSON output for log aggregation (ELK, DataDog, etc.)
- Structured extra fields for metadata
- Context filters for automatic field injection
- Specialized logging methods for coaching scenarios

**Log Types**:

- `log_api_request()` - API endpoint calls with duration and status
- `log_call_analysis()` - Coaching analysis with dimensions and tokens
- `log_coaching_session()` - Session creation with score and metadata
- `log_database_query()` - Query execution with timing
- `log_cache_operation()` - Cache hit/miss tracking
- `log_external_api_call()` - Third-party API calls (Gong, Claude, etc.)

**Key Classes**:

- `StructuredLogger` - Logger instance with context management
- `JSONFormatter` - JSON log formatting
- `CorrelationIdFilter` - Automatic field injection
- Global functions: `setup_structured_logging()`, `get_logger()`, `get_correlation_id()`, `set_correlation_id()`

### 4. Alerting Rules

**File**: `/Users/gcoyne/src/prefect/call-coach/monitoring/alerts.yml`

Prometheus alerting rules organized by category:

**Error Alerts**:

- High error rate (>5%) - Critical, 5m threshold
- Sentry error spike (>10 in 15m) - Warning, 5m threshold
- Gong API errors occurring - Warning, 2m threshold
- Claude API error rate (>5%) - Warning, 5m threshold

**Performance Alerts**:

- Slow API responses (p95 > 2s) - Warning, 5m threshold
- High Claude API latency (p95 > 30s) - Warning, 5m threshold
- Slow database queries (p95 > 1s) - Warning, 5m threshold
- Long call analysis duration (p95 > 60s) - Info, 10m threshold

**Resource Alerts**:

- High memory usage (>85%) - Warning, 5m threshold
- High CPU usage (>80%) - Warning, 5m threshold
- Disk critically full (<15% available) - Critical, 5m threshold
- Database connection pool near full (>80%) - Warning, 5m threshold

**Business Alerts**:

- Zero coaching sessions in 1 hour - Warning, 2h threshold
- Zero calls analyzed in 1 hour - Warning, 2h threshold
- Low cache hit rate (<30%) - Info, 10m threshold

**Dependency Alerts**:

- PostgreSQL database down - Critical, 1m threshold
- Redis cache down - Critical, 1m threshold
- Gong API experiencing issues - Critical, 5m threshold

**Token Usage Alerts**:

- High token usage (>1M tokens/hour) - Warning, 30m threshold
- Daily token cost above threshold (>$100) - Info, 1h threshold

### 5. Health Check Endpoint

**File**: `/Users/gcoyne/src/prefect/call-coach/frontend/app/api/health/route.ts`

Comprehensive health check API endpoint (`GET /api/health`):

**Checks Performed**:

- Database connectivity and response time
- Redis cache connectivity (with degradation if not configured)
- Claude API availability (auth validation)
- Backend API availability

**Response Format**:

```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "ISO8601",
  "uptime": "milliseconds",
  "checks": {
    "database": { "status": "up|down|degraded", "latency_ms": 5 },
    "redis": { "status": "up|down|degraded", "latency_ms": 2 },
    "claude_api": { "status": "up|down|degraded", "latency_ms": 150 },
    "backend_api": { "status": "up|down|degraded", "latency_ms": 10 }
  },
  "version": "1.0.0",
  "environment": "production"
}
```

**Status Codes**:

- 200 - Healthy (all checks up)
- 503 - Degraded or Unhealthy (one or more checks down)

### 6. Performance Profiling

**File**: `/Users/gcoyne/src/prefect/call-coach/instrumentation/profiler.py`

Multi-level performance profiling for bottleneck identification:

**PerformanceProfiler**:

- Block-level profiling with context manager
- Function-level profiling with decorator
- Memory tracking alongside timing
- Statistical analysis (min, max, avg, percentiles)
- Report generation and file persistence
- Slowest calls tracking

**CPUProfiler**:

- cProfile-based function-level CPU profiling
- Statistical output generation
- Profile data persistence for post-analysis
- Top-20 functions report generation

**SlowRequestDetector**:

- Configurable threshold detection
- Slow request logging with metadata
- Request history tracking
- Slow request reporting with sorting

**Key Classes**:

- `PerformanceProfiler` - Block and function profiling
- `CPUProfiler` - CPU-level profiling
- `SlowRequestDetector` - Request threshold monitoring
- Global functions: `get_performance_profiler()`, `get_cpu_profiler()`, `get_slow_request_detector()`, `initialize_profiling()`, `profile_request()` decorator

### 7. Grafana Dashboard

**File**: `/Users/gcoyne/src/prefect/call-coach/monitoring/dashboards/call_coach.json`

Pre-built comprehensive dashboard with 8 panels:

**Panels**:

1. Application Status (gauge)
2. API Request Rate (timeseries, by method/endpoint)
3. API Response Time Percentiles (p50, p95, p99)
4. Claude API Token Usage (stacked area, input/output)
5. Cache Hit Rate (gauge)
6. Database Query Performance (p95 by operation/table)
7. Error Rate (stacked area by error type)
8. Business Metrics (calls analyzed, sessions created)

**Configuration**:

- 10-second refresh rate
- 6-hour time range
- Dark theme with semantic colors
- Threshold indicators
- Legend tables with statistics

## Integration Points

### FastAPI REST Server Integration

```python
from monitoring.sentry import initialize_sentry
from monitoring.metrics import get_metrics
from instrumentation.logger import setup_structured_logging, set_correlation_id

# Startup
initialize_sentry(environment="production")
setup_structured_logging(log_level="INFO", json_format=True)

# Middleware for metrics
@app.middleware("http")
async def track_api_metrics(request, call_next):
    metrics = get_metrics()
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    metrics.record_api_request(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        duration=duration,
    )
    return response

# Middleware for correlation ID
@app.middleware("http")
async def add_correlation(request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID")
    set_correlation_id(correlation_id)
    return await call_next(request)
```

### FastMCP Server Integration

```python
from monitoring.sentry import initialize_sentry, capture_exception
from instrumentation.logger import get_logger

# Startup
initialize_sentry(environment="production")

# Tool wrapper
@mcp.tool()
def analyze_call(call_id: str):
    logger = get_logger(__name__)
    try:
        logger.info(f"Analyzing call {call_id}")
        result = analyze_call_tool(call_id)
        logger.log_call_analysis(
            call_id=call_id,
            rep_id=result["rep_id"],
            duration=result["duration"],
            dimensions=result["dimensions"],
            tokens_used=result["tokens_used"],
        )
        return result
    except Exception as e:
        capture_exception(e, context={"call_id": call_id})
        raise
```

## Files Created

### Monitoring Module

- `/Users/gcoyne/src/prefect/call-coach/monitoring/__init__.py` - Module exports
- `/Users/gcoyne/src/prefect/call-coach/monitoring/sentry.py` - Sentry integration
- `/Users/gcoyne/src/prefect/call-coach/monitoring/metrics.py` - Prometheus metrics
- `/Users/gcoyne/src/prefect/call-coach/monitoring/alerts.yml` - Alert definitions
- `/Users/gcoyne/src/prefect/call-coach/monitoring/dashboards/call_coach.json` - Grafana dashboard
- `/Users/gcoyne/src/prefect/call-coach/monitoring/README.md` - Complete setup guide

### Instrumentation Module

- `/Users/gcoyne/src/prefect/call-coach/instrumentation/__init__.py` - Module exports
- `/Users/gcoyne/src/prefect/call-coach/instrumentation/logger.py` - Structured logging
- `/Users/gcoyne/src/prefect/call-coach/instrumentation/profiler.py` - Performance profiling

### Frontend Health Check

- `/Users/gcoyne/src/prefect/call-coach/frontend/app/api/health/route.ts` - Health check endpoint

### Configuration

- Updated `/Users/gcoyne/src/prefect/call-coach/pyproject.toml` - Added monitoring dependencies

## Dependencies Added

```toml
# In pyproject.toml
"sentry-sdk[fastapi]>=1.40.0",
"prometheus-client>=0.19.0",
```

Optional for enhanced profiling:

- `psutil>=5.9.0` - For memory usage tracking in profiler

## Environment Variables

```bash
# Sentry Configuration
SENTRY_DSN=https://key@sentry.io/project-id
ENVIRONMENT=production|staging|development

# Application Metadata
APP_VERSION=1.0.0
ANTHROPIC_API_KEY=sk-...
DATABASE_URL=postgresql://...

# Monitoring Endpoints
COACHING_API_URL=http://localhost:8000  # For health checks
REDIS_URL=redis://localhost:6379        # For Redis health checks
```

## Quick Start

### 1. Initialize Monitoring

```python
# In your main FastAPI app
from monitoring import initialize_sentry, initialize_metrics
from instrumentation import setup_structured_logging, initialize_profiling

# At startup
initialize_sentry(dsn=os.getenv("SENTRY_DSN"))
initialize_metrics()
setup_structured_logging(log_level="INFO", json_format=True)
initialize_profiling(output_dir="./profiling_results")
```

### 2. Use in Endpoints

```python
from monitoring.metrics import get_metrics
from instrumentation.logger import get_logger

@app.post("/api/calls/{call_id}/analyze")
async def analyze_call(call_id: str):
    logger = get_logger(__name__)
    metrics = get_metrics()

    start_time = time.time()
    try:
        result = analyze_call_tool(call_id)
        duration = time.time() - start_time

        logger.log_call_analysis(
            call_id=call_id,
            rep_id=result["rep_id"],
            duration=duration,
            dimensions=result["dimensions"],
            tokens_used=result["tokens_used"],
        )

        metrics.record_call_analyzed(status="success")
        return result

    except Exception as e:
        duration = time.time() - start_time
        metrics.record_call_analyzed(status="error")
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise
```

### 3. Deploy Monitoring Stack

```bash
# Start Docker Compose stack
docker-compose -f monitoring/docker-compose.yml up -d

# Access dashboards
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# Alertmanager: http://localhost:9093
```

## Testing Monitoring Setup

```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Test metrics endpoint (after adding Prometheus middleware)
curl http://localhost:8000/metrics

# Test error tracking
curl -X POST http://localhost:8000/test-error

# Check logs
docker logs call-coach-api | grep "correlation_id"
```

## Dashboard Usage

1. **Import Dashboard** - Go to Grafana > Dashboards > Import
2. **Load JSON** - Upload `monitoring/dashboards/call_coach.json`
3. **Select Data Source** - Choose Prometheus
4. **View Metrics** - All 8 panels should populate within minutes

## Alerting Setup

1. **Configure Alertmanager** - Update `alerts.yml` notification channels
2. **Set Slack Webhook** - For alert notifications
3. **Configure PagerDuty** - For critical alerts
4. **Set Up Email** - For team notifications

## Best Practices

1. **Always include correlation IDs** in requests for end-to-end tracing
2. **Use context variables** for call_id, rep_id, user_id
3. **Sample errors appropriately** (100% in dev, 10-50% in production)
4. **Monitor token usage** closely for cost management
5. **Set up meaningful alerts** that warrant action
6. **Review dashboards daily** during operational hours
7. **Use structured fields** instead of string interpolation in logs

## Cost Considerations

- **Sentry**: Free tier covers many errors; pricing scales with volume
- **Prometheus**: Free (self-hosted); retention consumes disk space
- **Grafana**: Free tier available; cloud hosting available
- **Token Usage**: Monitor Claude API tokens closely via metrics dashboard

## Next Steps

1. Set SENTRY_DSN environment variable
2. Deploy monitoring stack with Docker Compose
3. Configure alert notification channels
4. Import Grafana dashboard
5. Add monitoring initialization to FastAPI server startup
6. Test end-to-end flow with sample requests
7. Review alerts and adjust thresholds based on baseline metrics

## Documentation

Full documentation available in `/Users/gcoyne/src/prefect/call-coach/monitoring/README.md`

- Setup instructions for each component
- Configuration examples
- Usage patterns
- Troubleshooting guide
- Integration examples
- Best practices

## Support

For questions or issues:

1. Review the comprehensive README.md
2. Check Grafana dashboard for current metrics
3. Review Sentry for recent errors
4. Check structured logs for correlation IDs
5. Use health endpoint to verify dependencies
