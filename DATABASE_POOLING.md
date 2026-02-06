# Database Connection Pooling for Serverless

This document explains how database connection pooling is configured for Vercel serverless deployment.

## Overview

Serverless functions are stateless and short-lived, which presents challenges for database connections:

1. **Cold Starts**: Functions start from scratch, requiring new connections
2. **Connection Limits**: Traditional connection pools can exhaust database connection limits
3. **Idle Connections**: Connections cannot be reused across function invocations

## Our Solution

We use **Neon Postgres with connection pooling** and configure our pool for serverless constraints.

### 1. Neon Connection Pooler

Neon provides a built-in connection pooler that:
- Manages connections server-side
- Supports many concurrent clients with fewer database connections
- Works seamlessly with serverless functions

**Important**: Use the pooler endpoint:

```bash
# ✅ Pooler endpoint (use this)
postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/callcoach

# ❌ Direct connection (avoid in serverless)
postgresql://user:pass@ep-xxx-pooler.us-east-2.aws.neon.tech/callcoach
```

### 2. Client-Side Pool Configuration

Configuration in `coaching_mcp/shared/config.py`:

```python
database_pool_min_size: int = Field(default=5)
database_pool_max_size: int = Field(default=20)
```

**For Serverless (Vercel)**, use smaller pool sizes:

```bash
DATABASE_POOL_MIN_SIZE=2
DATABASE_POOL_MAX_SIZE=10
```

Why smaller?
- Each serverless function instance gets its own pool
- Many parallel function invocations = many pools
- Smaller pools prevent exhausting Neon connection limits

### 3. Connection Lifecycle

Our connection manager in `db/connection.py`:

```python
@contextmanager
def get_db_connection():
    """Context manager that automatically returns connections to pool."""
    db_pool = get_db_pool()
    conn = db_pool.getconn()
    try:
        # Set per-connection timeout
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '30s'")
        yield conn
    finally:
        db_pool.putconn(conn)  # Always return to pool
```

Key features:
- **Context Manager**: Ensures connections are always returned
- **Statement Timeout**: Prevents long-running queries (30s limit)
- **Per-Connection Settings**: Compatible with Neon pooler

## Configuration by Environment

### Local Development

Use higher pool sizes for better concurrency:

```bash
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=20
```

### Vercel Production

Use lower pool sizes to avoid connection exhaustion:

```bash
DATABASE_POOL_MIN_SIZE=2
DATABASE_POOL_MAX_SIZE=10
```

### Neon Plan Limits

Match pool sizes to your Neon plan:

| Neon Plan | Max Connections | Recommended MAX_SIZE |
|-----------|----------------|---------------------|
| Free      | 10             | 5                   |
| Launch    | 100            | 10                  |
| Scale     | 1000           | 20                  |

## Monitoring Connection Usage

### Via Neon Dashboard

1. Go to [Neon Console](https://console.neon.tech)
2. Select your project
3. View "Connections" tab
4. Monitor current connection count

### Via Database Query

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check connections by state
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;
```

### Via Vercel Logs

Watch for connection errors:

```bash
vercel logs --query="connection"
```

## Troubleshooting

### Error: "too many connections"

**Cause**: Pool size exceeds Neon plan limit

**Solution**:
1. Reduce `DATABASE_POOL_MAX_SIZE`
2. Upgrade Neon plan
3. Add connection retry logic

### Error: "connection timeout"

**Cause**: Slow cold starts or network issues

**Solution**:
1. Verify using pooler endpoint
2. Check Neon dashboard for issues
3. Increase function timeout

### High Connection Count

**Cause**: Many concurrent serverless functions

**Solution**:
1. Each function invocation creates a pool
2. Reduce pool size per function
3. Connections are released when function completes

## Best Practices

1. **Always use context managers**
   ```python
   with get_db_connection() as conn:
       # Use connection
       pass
   # Connection automatically returned
   ```

2. **Keep queries fast**
   - Use indexes
   - Limit result sets
   - Avoid full table scans

3. **Set statement timeouts**
   - Prevents runaway queries
   - Already configured per-connection

4. **Monitor connection usage**
   - Check Neon dashboard regularly
   - Alert on high connection counts

5. **Test cold starts**
   - Verify connections work after idle period
   - Measure cold start latency

## Cold Start Performance

Expected cold start times:

- **First connection**: 2-5 seconds
- **Subsequent queries**: < 500ms
- **Function warmup**: Next.js caches for ~5 minutes

To minimize cold starts:
1. Use Vercel Pro plan (faster infrastructure)
2. Keep pool sizes small
3. Optimize database schema with indexes

## Resources

- [Neon Pooling Guide](https://neon.tech/docs/connect/connection-pooling)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- [psycopg2 Connection Pooling](https://www.psycopg.org/docs/pool.html)

## Summary

| Setting | Local Dev | Vercel Production |
|---------|-----------|------------------|
| `DATABASE_POOL_MIN_SIZE` | 5 | 2 |
| `DATABASE_POOL_MAX_SIZE` | 20 | 10 |
| `statement_timeout` | 30s | 30s |
| Neon Endpoint | Pooler | Pooler |

For serverless: **Smaller pools + Neon pooler = Reliable connections**
