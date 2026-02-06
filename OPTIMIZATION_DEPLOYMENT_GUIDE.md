# API Optimization Deployment Guide

## Overview

This guide covers deploying the API optimization features to production environments.

## Prerequisites

- PostgreSQL 12+ with pg_stat_statements extension
- Python 3.11+
- Access to production database
- Deployment access (Vercel, cloud provider, etc.)

## Step-by-Step Deployment

### 1. Database Optimization

#### Enable Required Extensions

```bash
# Connect to production database
psql $DATABASE_URL

# Enable pg_stat_statements for query analysis
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

# Verify extension is loaded
\dx
```

#### Create Performance Indexes

**Important**: Run with CONCURRENTLY to avoid locking tables in production.

```bash
# Run index creation script
psql $DATABASE_URL -f db/performance/slow_queries.sql

# Or run specific indexes:
psql $DATABASE_URL -c "
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_calls_product_scheduled
ON calls(product, scheduled_at DESC) WHERE product IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_coaching_rep_created
ON coaching_sessions(rep_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transcripts_fts
ON transcripts USING GIN (full_text_search);
"
```

#### Verify Index Creation

```bash
# Check index status
psql $DATABASE_URL -c "
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE indexname LIKE 'idx_%'
ORDER BY indexname;
"
```

### 2. Environment Configuration

#### Update Environment Variables

Add or verify these settings in your `.env` or deployment config:

```bash
# Database connection pooling
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=20

# Logging
LOG_LEVEL=INFO  # Use DEBUG for troubleshooting

# Optional: Error tracking
# SENTRY_DSN=https://...
```

#### Vercel Deployment

Update `vercel.json`:

```json
{
  "env": {
    "DATABASE_POOL_MIN_SIZE": "5",
    "DATABASE_POOL_MAX_SIZE": "20"
  }
}
```

### 3. Code Deployment

#### Install Dependencies

```bash
# No new dependencies required!
# All optimizations use built-in Python libraries
pip install -e .
```

#### Test Locally

```bash
# Start server with optimizations
python -m api.rest_server

# In another terminal, test endpoints
curl http://localhost:8000/monitoring/health
curl http://localhost:8000/monitoring/metrics

# Test rate limiting (should see 429 after ~150 requests)
for i in {1..160}; do
  curl -w "\n%{http_code}\n" http://localhost:8000/health
done
```

#### Deploy to Production

```bash
# Vercel
vercel deploy --prod

# Or your deployment method
git push origin main  # If using CI/CD
```

### 4. Post-Deployment Verification

#### Health Check

```bash
# Check API health
curl https://your-api.vercel.app/monitoring/health

# Should return:
# {
#   "status": "healthy",
#   "timestamp": "...",
#   "uptime_seconds": 123,
#   "database": "connected"
# }
```

#### Verify Rate Limiting

```bash
# Check rate limit headers
curl -I https://your-api.vercel.app/health

# Should see:
# X-RateLimit-Limit: 150
# X-RateLimit-Remaining: 149
# X-RateLimit-Reset: 1234567890
```

#### Verify Compression

```bash
# Request with gzip support
curl -H "Accept-Encoding: gzip" \
  https://your-api.vercel.app/api/v1/tools/search_calls \
  -d '{"limit": 50}' \
  -H "Content-Type: application/json" \
  --compressed -v

# Should see:
# Content-Encoding: gzip
```

#### Check Metrics

```bash
# Get comprehensive metrics
curl https://your-api.vercel.app/monitoring/metrics | jq

# Check database metrics
curl https://your-api.vercel.app/monitoring/metrics/database | jq
```

### 5. Monitoring Setup

#### Health Check for Load Balancer

Configure your load balancer or monitoring service:

- **Endpoint**: `GET /monitoring/health`
- **Expected Status**: 200
- **Expected Response**: `{"status": "healthy"}`
- **Check Interval**: 30 seconds
- **Timeout**: 5 seconds

#### Metrics Collection

Set up periodic metrics collection:

```bash
# Cron job to log metrics every 5 minutes
*/5 * * * * curl https://your-api.vercel.app/monitoring/metrics >> /var/log/api-metrics.log
```

Or integrate with monitoring service:

```python
# Example: Send metrics to Datadog
import requests
import time

def collect_metrics():
    metrics = requests.get("https://your-api.vercel.app/monitoring/metrics").json()

    # Send to Datadog, Prometheus, etc.
    # datadog.statsd.gauge('api.total_requests', metrics['total_requests'])
    # datadog.statsd.gauge('api.error_rate', metrics['error_rate'])
```

#### Alert Configuration

Set up alerts for:

1. **High Error Rate**

   - Metric: `error_rate > 0.05` (5%)
   - Action: Page on-call, investigate logs

2. **Rate Limit Hits**

   - Metric: `rate_limit_hits > 100/hour`
   - Action: Notify team, review user patterns

3. **Slow Response Times**

   - Metric: `response_time_ms.p95 > 1000`
   - Action: Check database performance, review logs

4. **Database Issues**
   - Metric: `database != "connected"`
   - Action: Immediate page, check database health

### 6. Performance Testing

#### Load Testing

Use tools like `locust` or `k6` to test under load:

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def search_calls(self):
        self.client.post("/api/v1/tools/search_calls", json={
            "limit": 20,
            "offset": 0
        })

# Run load test
# locust -f locustfile.py --host https://your-api.vercel.app
```

#### Database Query Performance

```bash
# Check query performance after deployment
psql $DATABASE_URL -c "
SELECT
    calls,
    mean_exec_time,
    max_exec_time,
    query
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Should see improved execution times for indexed queries
```

### 7. Rollback Plan

If issues occur, rollback procedure:

#### Emergency Rollback

```bash
# Revert to previous deployment
vercel rollback

# Or git revert
git revert HEAD
git push origin main
```

#### Database Rollback

If indexes cause issues:

```bash
# Drop specific index
psql $DATABASE_URL -c "DROP INDEX CONCURRENTLY idx_name;"

# Indexes can be dropped without data loss
# They can be recreated later once issues are resolved
```

## Troubleshooting

### Issue: Rate Limiting Too Aggressive

**Symptoms**: Legitimate users getting 429 responses

**Solution**: Adjust rate limits in `api/rest_server.py`:

```python
app.add_middleware(
    RateLimitMiddleware,
    default_rate_limit=200,  # Increase from 100
    expensive_rate_limit=40,  # Increase from 20
)
```

### Issue: High Memory Usage

**Symptoms**: Server OOM errors, high memory metrics

**Solution**: Reduce connection pool size:

```bash
# In .env
DATABASE_POOL_MAX_SIZE=10  # Reduce from 20
```

### Issue: Slow Queries Still Occurring

**Symptoms**: High p95 response times, database metrics show slow queries

**Solution**:

1. Check if indexes are being used:

   ```bash
   psql $DATABASE_URL -c "
   EXPLAIN ANALYZE
   SELECT * FROM calls WHERE product = 'Prefect Cloud' LIMIT 50;
   "
   ```

2. Verify index exists and is valid:

   ```bash
   psql $DATABASE_URL -c "
   SELECT indexname, indexdef
   FROM pg_indexes
   WHERE tablename = 'calls';
   "
   ```

3. Run ANALYZE to update statistics:

   ```bash
   psql $DATABASE_URL -c "ANALYZE calls;"
   ```

### Issue: Compression Not Working

**Symptoms**: No Content-Encoding header, large response sizes

**Solution**: Verify client sends Accept-Encoding header:

```bash
# Test with curl
curl -H "Accept-Encoding: gzip" \
  https://your-api.vercel.app/api/v1/tools/search_calls \
  --compressed -v

# Should see Content-Encoding: gzip in response headers
```

## Maintenance

### Weekly Tasks

1. Check metrics dashboard for trends
2. Review error logs for patterns
3. Monitor rate limit hits for abuse

### Monthly Tasks

1. Run database performance analysis
2. Review and optimize slow queries
3. Check index usage and remove unused indexes
4. Update alert thresholds based on actual usage

### Quarterly Tasks

1. Review rate limit configuration
2. Analyze API usage patterns
3. Plan capacity upgrades if needed
4. Update optimization strategies

## Support

For issues or questions:

1. Check metrics: `GET /monitoring/metrics`
2. Review logs with request ID
3. Check database performance: `db/performance/slow_queries.sql`
4. Contact: api-optimization-agent

## Additional Resources

- [API Optimization Summary](./API_OPTIMIZATION_SUMMARY.md)
- [Database Performance README](./db/performance/README.md)
- [Test Suite](./tests/api/test_optimizations.py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Performance](https://wiki.postgresql.org/wiki/Performance_Optimization)
