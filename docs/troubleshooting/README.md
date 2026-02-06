# Troubleshooting Guide

Solutions to common issues with Call Coach.

## Quick Diagnostics

Before diving into specific issues, run these checks:

```bash
# 1. Backend health check
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy"}

# 2. Database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Expected output:
# (1 row)

# 3. Gong API credentials
curl -H "Authorization: Bearer $GONG_API_SECRET" \
  "$GONG_API_BASE_URL/calls"

# Expected: Returns call list (no 401 error)

# 4. Claude API key
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" | head -20

# Expected: Returns list of models
```

## Backend Issues

### Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'coaching_mcp'`

**Causes**:

- Python environment not activated
- Dependencies not installed
- Wrong working directory

**Solutions**:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Install dependencies
uv pip install -e ".[dev]"

# 3. Check working directory
pwd
# Should be: /Users/gcoyne/src/prefect/call-coach

# 4. Try starting again
uv run mcp-server-dev
```

---

**Error**: `DATABASE_URL must include sslmode=require`

**Causes**:

- Missing `?sslmode=require` in DATABASE_URL
- Neon requires SSL for security

**Solution**:

```bash
# Check your DATABASE_URL
echo $DATABASE_URL

# Should end with: ?sslmode=require
# If not, update .env file:
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Then restart
source .venv/bin/activate
uv run mcp-server-dev
```

---

**Error**: `✗ Database connection failed: could not connect to server`

**Causes**:

- Database is down
- Connection credentials wrong
- Network connectivity issue

**Solutions**:

```bash
# 1. Test database connection
psql $DATABASE_URL

# 2. Check credentials in .env
grep DATABASE_URL .env

# 3. Verify Neon database is running
# Go to https://console.neon.tech and check status

# 4. Check IP allowlist in Neon
# Settings → Project settings → Network access

# 5. Restart database connection
# (Neon has built-in failover, usually resolves itself)
```

---

**Error**: `✗ Gong API authentication failed`

**Causes**:

- Wrong API key or secret
- Wrong tenant URL
- Gong credentials expired

**Solutions**:

```bash
# 1. Verify credentials in .env
grep GONG_API .env

# 2. Check tenant URL format
# Should be: https://us-XXXXX.api.gong.io/v2
# NOT: https://api.gong.io/v2

# 3. Test Gong API manually
curl -H "Authorization: Bearer $GONG_API_SECRET" \
  "$GONG_API_BASE_URL/calls"

# Expected: Returns JSON (no 401 error)

# 4. Get new credentials from Gong
# Go to: https://gong.app.gong.io/settings/api/authentication
# Copy API key and secret
# Update .env file

# 5. Restart server
uv run mcp-server-dev
```

---

**Error**: `✗ Anthropic API key validated [FAILED]`

**Causes**:

- Wrong API key
- API key expired or revoked
- API key doesn't have required permissions

**Solutions**:

```bash
# 1. Check API key
echo $ANTHROPIC_API_KEY

# 2. Get new key from Anthropic Console
# Go to: https://console.anthropic.com/settings/keys
# Create new key
# Update .env file

# 3. Test API key manually
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" | head -20

# 4. Restart server
uv run mcp-server-dev
```

---

### Analysis Taking Too Long

**Symptom**: Call analysis exceeds 2 minutes

**Causes**:

- Very long call (60+ minutes)
- Claude API is slow
- Network latency
- Transcript chunking overhead

**Solutions**:

```bash
# 1. Check call duration
# Calls > 60 minutes may take 2-3 minutes
# This is normal

# 2. Check Claude API status
# https://status.anthropic.com

# 3. Try a shorter call
# Analyze a <30 minute call
# Should complete in <1 minute

# 4. Check network latency
ping api.anthropic.com
# Should show <100ms latency

# 5. Check server logs
# Look for chunking messages
# Verify chunks are reasonable size
```

---

### Call Not Found in Database

**Error**: `404 Not Found - Call ID not found in database`

**Causes**:

- Call hasn't been processed yet
- Wrong call ID format
- Call didn't complete webhook processing
- Call is from different Gong account

**Solutions**:

```bash
# 1. Verify call ID format
# Should be a 18-19 digit number
# Example: 1464927526043145564

# 2. Check if call is in database
psql $DATABASE_URL -c "SELECT * FROM calls WHERE gong_call_id = '1464927526043145564'"

# 3. If not found, wait for webhook processing
# Takes 5-30 seconds after call completes
# Try again in 1 minute

# 4. Check webhook status
psql $DATABASE_URL -c "SELECT * FROM webhook_events ORDER BY received_at DESC LIMIT 1"

# 5. If webhook failed, check error_message column
# May need to reprocess manually

# 6. Verify call exists in Gong
# Log in to https://gong.app.gong.io
# Search for call ID
# Confirm it's from your account
```

---

### Cache Not Working

**Symptom**: Same call analyzed multiple times returns different scores

**Causes**:

- Cache TTL expired (30 days)
- Cache key mismatch
- Rubric version changed
- Cache database cleared

**Solutions**:

```bash
# 1. Check cache entry exists
psql $DATABASE_URL -c "SELECT * FROM cache_keys ORDER BY created_at DESC LIMIT 10"

# 2. Check cache hit rate
psql $DATABASE_URL -c "SELECT COUNT(*) as hits, COUNT(DISTINCT key) as keys FROM cache_keys"

# Expected: hits > keys (multiple hits per key)

# 3. Clear cache if needed
psql $DATABASE_URL -c "TRUNCATE cache_keys"

# 4. Check rubric version
# If you updated rubrics, cache is invalidated
# Run analysis again to rebuild cache

# 5. Monitor cache TTL
# 30 days after analysis, entry expires
# After 30 days, re-analysis will be fresh
```

---

## Frontend Issues

### Frontend Won't Load

**Error**: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not found`

**Causes**:

- Missing `.env.local` file
- Clerk credentials not configured
- Environment variables not loaded

**Solutions**:

```bash
cd frontend

# 1. Create .env.local if missing
cp .env.example .env.local

# 2. Edit with Clerk credentials
# Get from: https://clerk.com
# Look for "Publishable Key" and "Secret Key"

# 3. Add to .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8001

# 4. Restart frontend
npm run dev

# 5. Clear Next.js cache if still failing
rm -rf .next
npm run dev
```

---

**Error**: `API calls returning 404`

**Causes**:

- REST API not running
- Wrong backend URL configured
- Network connectivity issue

**Solutions**:

```bash
# 1. Verify backend is running
curl http://localhost:8001/health

# Expected: {"status": "healthy"}

# 2. Check NEXT_PUBLIC_MCP_BACKEND_URL
cat frontend/.env.local | grep MCP_BACKEND

# Should be: http://localhost:8001

# 3. Check browser DevTools
# Open: http://localhost:3000
# Press F12 (DevTools)
# Go to Network tab
# Make a request
# Check the URL and response

# 4. Check CORS configuration
# If error is CORS related:
# Edit api/rest_server.py
# Verify allow_origins includes your domain

# 5. Restart both frontend and backend
npm run dev  # Frontend
uv run uvicorn api.rest_server:app --port 8001 --reload  # Backend
```

---

**Error**: Port 3000 already in use

**Causes**:

- Another process using port 3000
- Previous Next.js process didn't exit cleanly

**Solutions**:

```bash
# 1. Find process using port 3000
lsof -i :3000

# 2. Kill the process
kill -9 <PID>

# 3. Or use different port
npm run dev -- -p 3001

# 4. Try again
npm run dev
```

---

### Clerk Authentication Not Working

**Symptom**: Can't sign in, always redirected to login page

**Causes**:

- Clerk keys not configured
- Wrong redirect URLs
- Clerk account not set up
- Session cookie issues

**Solutions**:

```bash
# 1. Check Clerk dashboard
# https://dashboard.clerk.com

# 2. Get correct keys
# Settings → API Keys
# Copy "Publishable Key" and "Secret Key"

# 3. Update frontend/.env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# 4. Set redirect URLs in Clerk dashboard
# Settings → URLs
# Add these URLs:
# http://localhost:3000/sign-in
# http://localhost:3000/sign-up
# http://localhost:3000/dashboard

# 5. Create a test user in Clerk
# Go to Users → Create new user
# Set email and password

# 6. Restart frontend
npm run dev

# 7. Clear browser cookies if still failing
# Open DevTools → Application → Cookies
# Delete all cookies for localhost:3000
# Try again
```

---

## API Issues

See [API Error Codes](./api-errors.md) for detailed error code reference.

### 400 Bad Request

**Cause**: Invalid request parameters

**Solution**:

```bash
# Check request format
curl -X POST http://localhost:8001/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d '{"gong_call_id": "abc123"}'

# Verify:
# - All required parameters present
# - Parameters have correct types
# - JSON is valid (no syntax errors)

# Check API docs for required fields
# http://localhost:8001/docs
```

---

### 401 Unauthorized

**Cause**: Missing or invalid API key (if enabled)

**Solution**:

```bash
# In production, requests need Bearer token
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8001/coaching/analyze-call

# For local development, no auth needed
```

---

### 429 Too Many Requests

**Cause**: Rate limit exceeded (production only)

**Solution**:

```bash
# Wait before retrying
# Rate limit: 100 requests/minute

# Check rate limit headers
curl -i http://localhost:8001/health | grep X-RateLimit

# Expected headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 42
# X-RateLimit-Reset: 1670000000

# Wait until X-RateLimit-Reset time
```

---

### 500 Internal Server Error

**Cause**: Server error (database, Claude API, etc.)

**Solution**:

```bash
# 1. Check server logs
# Look for error messages and stack traces

# 2. Check database
psql $DATABASE_URL -c "SELECT 1"

# 3. Check Claude API
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" | head -5

# 4. Restart server
uv run uvicorn api.rest_server:app --port 8001 --reload

# 5. Try request again
```

---

## Database Issues

### Can't Connect to Database

**Error**: `psql: could not connect to server`

**Causes**:

- Database is down
- Wrong connection string
- IP not whitelisted
- Network issue

**Solutions**:

```bash
# 1. Check connection string
echo $DATABASE_URL

# 2. Test connection
psql $DATABASE_URL -c "SELECT 1"

# 3. Check Neon dashboard
# https://console.neon.tech
# Verify database is "Available"

# 4. Check IP allowlist (if using Neon)
# Settings → Project settings → Network access
# Add your IP if not present

# 5. Check credentials
# Connection string format:
# postgresql://user:password@host/db?sslmode=require

# 6. Test with generic connection
psql postgresql://localhost/callcoach
```

---

### Database Tables Missing

**Error**: `✗ Missing required database tables`

**Causes**:

- Migrations not run
- Database not initialized
- Tables accidentally dropped

**Solutions**:

```bash
# 1. Check existing tables
psql $DATABASE_URL -c "\dt"

# 2. Run migrations
psql $DATABASE_URL -f db/migrations/001_initial_schema.sql

# 3. Verify tables created
psql $DATABASE_URL -c "\dt"

# Expected tables:
# - calls
# - speakers
# - transcripts
# - coaching_sessions
# - analysis_runs
# - cache_keys
# - webhook_events
```

---

### Slow Database Queries

**Symptom**: API responses taking >5 seconds

**Causes**:

- Missing indexes
- Large result set
- Database connection pool exhausted
- Network latency

**Solutions**:

```bash
# 1. Check query performance
psql $DATABASE_URL

\timing  # Enable timing
SELECT * FROM coaching_sessions WHERE call_id = 'xxx';

# Should complete in <100ms

# 2. Check indexes
psql $DATABASE_URL -c "\d coaching_sessions"

# Look for indexes (should have many)

# 3. Check connection pool usage
# Neon shows pool usage in dashboard
# Default: 20 max connections

# 4. Optimize slow queries
# Use EXPLAIN to see query plan
EXPLAIN SELECT * FROM coaching_sessions WHERE call_id = 'xxx';

# 5. Contact Neon support if persistent
```

---

## Performance Issues

### High Memory Usage

**Symptom**: Python process using >500MB

**Causes**:

- Large transcripts being loaded into memory
- Memory leak in code
- Tiktoken model loaded multiple times

**Solutions**:

```bash
# 1. Check memory usage
ps aux | grep python

# 2. Check for memory leaks
# Enable Python profiling:
python -m memory_profiler coaching_mcp/server.py

# 3. Optimize memory
# - Stream large results
# - Clear caches periodically
# - Use generators instead of lists

# 4. Restart server periodically
# Kill and restart process after 1-2 hours
```

---

### Slow Analysis

**Symptom**: Analyze call takes >3 minutes

**Causes**:

- Claude API is slow
- Very long transcript (60+ min)
- Network latency
- Server overloaded

**Solutions**:

```bash
# 1. Check call duration
psql $DATABASE_URL -c "SELECT duration_seconds FROM calls WHERE gong_call_id = 'xxx'"

# Convert seconds to minutes
# (seconds / 60) = minutes

# 2. Expected times:
# <30 min call: 30-45 seconds
# 30-60 min call: 60-90 seconds
# >60 min call: 2-3 minutes

# 3. Check Claude API status
# https://status.anthropic.com

# 4. Try with shorter call
# Verify system works with <20 min call

# 5. Check server load
# top
# Look for other processes using CPU/memory
```

---

## Getting Help

1. **Check logs**: Look for error messages and stack traces
2. **Verify configuration**: Check all environment variables
3. **Test connectivity**: Verify database, APIs, and networks
4. **Review architecture**: See [System Architecture](../developers/architecture.md)
5. **Check API docs**: See [API Reference](../api/endpoints.md)
6. **Contact support**: Email with request ID and logs

---

**Still stuck?** See [API Error Codes](./api-errors.md) or contact the team for urgent issues.
