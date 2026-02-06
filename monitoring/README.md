# Monitoring and Observability Infrastructure

Comprehensive monitoring and observability setup for the Call Coach application, including error tracking, metrics collection, structured logging, and performance profiling.

## Architecture

The monitoring infrastructure consists of five main components:

1. **Sentry** - Error tracking and exception reporting with rich context
2. **Prometheus** - Metrics collection and time-series data storage
3. **Structured Logging** - JSON-formatted logs with correlation IDs for request tracing
4. **Grafana** - Visualization and dashboarding for metrics
5. **Performance Profiling** - Identification of bottlenecks and slow requests

## Components

### 1. Sentry Error Tracking (`monitoring/sentry.py`)

Captures exceptions with rich context including user information, call IDs, and request correlation IDs.

#### Configuration

Set up Sentry DSN in environment variables:

```bash
export SENTRY_DSN="https://your-key@sentry.io/your-project"
export ENVIRONMENT="production"  # or staging, development
```

#### Usage

```python
from monitoring.sentry import initialize_sentry, capture_exception, set_user_context

# Initialize at startup
initialize_sentry(dsn="your-sentry-dsn", environment="production")

# Capture exceptions with context
try:
    analyze_call(call_id)
except Exception as e:
    capture_exception(
        e,
        context={
            "call_id": call_id,
            "rep_id": rep_id,
            "correlation_id": request.correlation_id,
        }
    )

# Set user context for tracking
set_user_context(user_id="123", email="user@example.com")
```

### 2. Prometheus Metrics (`monitoring/metrics.py`)

Tracks application performance metrics including API response times, token usage, cache hit rates, and database performance.

#### Key Metrics

- **API Metrics**

  - `api_requests_total` - Total requests by method, endpoint, and status
  - `api_request_duration_seconds` - Request latency with percentiles

- **Claude API Metrics**

  - `claude_api_calls_total` - Total API calls by model and status
  - `claude_input_tokens_total` - Input tokens sent
  - `claude_output_tokens_total` - Output tokens received
  - `claude_api_duration_seconds` - API call latency

- **Cache Metrics**

  - `cache_hits_total` - Cache hits by cache type
  - `cache_misses_total` - Cache misses by cache type
  - `cache_size_bytes` - Current cache size

- **Database Metrics**

  - `db_queries_total` - Total queries by operation and table
  - `db_query_duration_seconds` - Query latency
  - `db_connections_active` - Active database connections

- **Business Metrics**
  - `calls_analyzed_total` - Coaching analyses completed
  - `coaching_sessions_created_total` - Sessions created
  - `coaching_session_duration_seconds` - Session duration

#### Usage

```python
from monitoring.metrics import get_metrics, track_api_call

metrics = get_metrics()

# Record API request
metrics.record_api_request("GET", "/api/calls/123", status=200, duration=0.25)

# Track Claude API usage
metrics.record_claude_call(
    model="claude-opus-4-5",
    input_tokens=500,
    output_tokens=300,
    duration=2.5,
)

# Record cache operation
metrics.record_cache_hit("call_analysis")
metrics.record_cache_miss("rep_insights")

# Track database query
with metrics.track_db_query("SELECT", "calls"):
    result = db.query("SELECT * FROM calls WHERE id = ?", [call_id])
```

### 3. Structured Logging (`instrumentation/logger.py`)

JSON-formatted logging with correlation ID support for request tracing across the application.

#### Configuration

```python
from instrumentation.logger import setup_structured_logging, get_logger

# Initialize at startup
setup_structured_logging(log_level="INFO", json_format=True)

# Get logger instance
logger = get_logger(__name__)
```

#### Features

- **Correlation IDs** - Automatic request tracing
- **Context Variables** - Call ID, rep ID, user ID tracking
- **Structured Output** - JSON-formatted logs for log aggregation
- **Extra Fields** - Custom metadata in every log entry

#### Usage

```python
from instrumentation.logger import get_logger, set_correlation_id

logger = get_logger(__name__)

# Set correlation ID for request
correlation_id = set_correlation_id()
logger.info("Processing request", extra={"endpoint": "/api/calls"})

# Log coaching session with metadata
logger.log_coaching_session(
    session_id="session-123",
    call_id="call-456",
    rep_id="rep-789",
    dimension="discovery",
    score=85.5,
    tokens_used=1500,
)

# Log database queries
logger.log_database_query(
    operation="SELECT",
    table="calls",
    duration=0.05,
    rows_affected=1,
)
```

### 4. Alerting Rules (`monitoring/alerts.yml`)

Alert definitions for Prometheus Alertmanager covering:

- **Error Alerts**

  - High error rate (>5%)
  - Sentry error spike
  - Gong API errors
  - Claude API errors

- **Performance Alerts**

  - Slow API responses (p95 > 2s)
  - High Claude API latency (p95 > 30s)
  - Slow database queries (p95 > 1s)

- **Resource Alerts**

  - High memory usage (>85%)
  - High CPU usage (>80%)
  - High disk usage (<15% available)

- **Business Alerts**
  - Zero coaching sessions created
  - Zero calls analyzed
  - Low cache hit rate (<30%)

#### Configuration

Update `alerts.yml` with your notification channels:

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - "alertmanager:9093"
```

### 5. Performance Profiling (`instrumentation/profiler.py`)

Identifies bottlenecks and slow requests with detailed profiling data.

#### Features

- **Block Profiling** - Time specific code blocks
- **Function Profiling** - Profile function execution
- **CPU Profiling** - cProfile-based detailed analysis
- **Slow Request Detection** - Identify requests exceeding thresholds

#### Usage

```python
from instrumentation.profiler import (
    get_performance_profiler,
    get_slow_request_detector,
    profile_request,
)

profiler = get_performance_profiler()

# Profile a code block
with profiler.profile_block("call_analysis"):
    result = analyze_call(call_id)

# Profile a function
@profiler.profile_function
def analyze_opportunity(opp_id):
    # implementation
    pass

# Detect slow requests
detector = get_slow_request_detector()
detector.check_request(
    request_id="req-123",
    endpoint="/api/calls/123/analyze",
    duration=3.5,
)

# Get profiling report
report = profiler.get_report()
profiler.save_report()
```

## Grafana Dashboard

A pre-built dashboard (`monitoring/dashboards/call_coach.json`) provides comprehensive visualization:

- Application status
- API request rate and latency
- Claude API token usage and latency
- Cache hit rate
- Database query performance
- Error rate
- Business metrics (calls analyzed, sessions created)

### Import Dashboard

1. Open Grafana
2. Go to Dashboards > New > Import
3. Upload or paste `monitoring/dashboards/call_coach.json`
4. Select Prometheus data source
5. Click Import

## Health Check Endpoint

The `/api/health` endpoint provides comprehensive health status:

```bash
curl http://localhost:3000/api/health

{
  "status": "healthy",
  "timestamp": "2025-02-05T19:35:00.000Z",
  "uptime": 3600000,
  "checks": {
    "database": {
      "status": "up",
      "latency_ms": 5,
      "timestamp": "2025-02-05T19:35:00.000Z"
    },
    "redis": {
      "status": "up",
      "latency_ms": 2,
      "timestamp": "2025-02-05T19:35:00.000Z"
    },
    "claude_api": {
      "status": "up",
      "latency_ms": 150,
      "timestamp": "2025-02-05T19:35:00.000Z"
    },
    "backend_api": {
      "status": "up",
      "latency_ms": 10,
      "timestamp": "2025-02-05T19:35:00.000Z"
    }
  },
  "version": "1.0.0",
  "environment": "production"
}
```

## Integration with FastAPI/REST Server

### Setup Sentry in API Server

```python
# api/rest_server.py
from fastapi import FastAPI
from monitoring.sentry import initialize_sentry

app = FastAPI()

# Initialize Sentry
initialize_sentry()

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    from instrumentation.logger import set_correlation_id
    correlation_id = request.headers.get("X-Correlation-ID")
    set_correlation_id(correlation_id)
    response = await call_next(request)
    return response
```

### Add Metrics Middleware

```python
from monitoring.metrics import get_metrics
import time

@app.middleware("http")
async def track_metrics(request: Request, call_next):
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
```

## Integration with FastMCP Server

### Add Sentry and Logging

```python
# coaching_mcp/server.py
from monitoring.sentry import initialize_sentry
from instrumentation.logger import setup_structured_logging

# Initialize monitoring
initialize_sentry(environment="production")
setup_structured_logging(log_level="INFO", json_format=True)

# Wrap tool execution with error handling
@mcp.tool()
def analyze_call(call_id: str, ...):
    try:
        from instrumentation.logger import get_logger
        logger = get_logger(__name__)
        logger.info(f"Analyzing call {call_id}")

        # Call implementation
        result = analyze_call_tool(call_id, ...)

        logger.info(f"Call analysis completed", extra={
            "call_id": call_id,
            "tokens_used": result.get("tokens_used"),
        })
        return result
    except Exception as e:
        from monitoring.sentry import capture_exception
        capture_exception(e, context={"call_id": call_id})
        raise
```

## Dependencies

Add these to `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...
    "sentry-sdk[fastapi]>=1.40.0",
    "prometheus-client>=0.19.0",
]
```

Install:

```bash
pip install -e ".[monitoring]"
```

Or manually:

```bash
pip install sentry-sdk prometheus-client
```

## Docker Compose Setup

Example `docker-compose.yml` for monitoring stack:

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus_data:
  grafana_data:
```

## Environment Variables

```bash
# Sentry
SENTRY_DSN=https://key@sentry.io/project
ENVIRONMENT=production

# Prometheus
PROMETHEUS_SCRAPE_INTERVAL=15s

# Health checks
COACHING_API_URL=http://localhost:8000
REDIS_URL=redis://localhost:6379

# Application
APP_VERSION=1.0.0
ANTHROPIC_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

## Monitoring Best Practices

1. **Correlation IDs** - Always use correlation IDs for end-to-end request tracing
2. **Context** - Include call_id, rep_id, and user_id in all logs and errors
3. **Sampling** - Use error sampling (1.0 in prod, 0.1 in dev) for high-volume operations
4. **Alerts** - Set up meaningful alerts that trigger actionable responses
5. **Dashboards** - Review dashboards daily during production operations
6. **Retention** - Configure appropriate retention for logs and metrics

## Troubleshooting

### Sentry not capturing errors

1. Check `SENTRY_DSN` is set correctly
2. Verify Sentry integration is initialized before app starts
3. Check error sampling rate (`error_sample_rate`)

### Missing metrics

1. Verify Prometheus scrape job is configured
2. Check metrics are being recorded in code
3. Ensure Prometheus retention period is sufficient

### Slow logs

1. Check if JSON formatting is enabled
2. Consider log sampling in high-volume scenarios
3. Use structured fields instead of string interpolation

### Health check failures

1. Verify dependencies (database, Redis, Claude API) are accessible
2. Check environment variables are set
3. Review individual check latencies to identify slow dependency

## Additional Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Structured Logging Guide](https://www.kartar.net/2015/12/structured-logging/)
- [Performance Profiling Best Practices](https://www.python.org/dev/peps/pep-0409/)
