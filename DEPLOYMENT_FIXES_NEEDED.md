# FastMCP Server Deployment Fixes Required

## Current Status

Deployment to Horizon is **FAILING** with module import errors and the code has **critical security vulnerabilities** that must be fixed before production use.

---

## CRITICAL FIXES (Must Do Before Production)

### 1. SQL Injection Vulnerability in search_calls.py

**Location**: `coaching_mcp/tools/search_calls.py` line 100

**Issue**: The objection type filter uses string interpolation in SQL LIKE pattern:

```python
where_clauses.append("transcripts.topics @> ARRAY[%s]::text[]")
args.append(f"%{has_objection_type}%")
```

**Risk**: If `has_objection_type` contains SQL metacharacters, could inject malicious SQL.

**Fix**: Use proper ILIKE with parameterized query:

```python
where_clauses.append("EXISTS (SELECT 1 FROM unnest(transcripts.topics) AS topic WHERE topic ILIKE %s)")
args.append(f"%{has_objection_type}%")
```

### 2. Unsafe Array Type Parameter Handling

**Location**: `coaching_mcp/tools/search_calls.py` line 108

**Issue**: Array overlap operator `&&` with topic list may not be properly handled by psycopg2:

```python
where_clauses.append("transcripts.topics && %s")
args.append(topics)
```

**Risk**: psycopg2 may not properly adapt Python list to PostgreSQL array type, causing query failures.

**Fix**: Use psycopg2's Array adapter explicitly:

```python
from psycopg2.extensions import adapt
where_clauses.append("transcripts.topics && %s::text[]")
args.append(adapt(topics))
```

### 3. Missing Package Dependencies in fastmcp.toml

**Location**: `fastmcp.toml` line 18-19

**Issue**: Only Python version specified, no package dependencies listed.

**Current**:

```toml
[dependencies]
python = ">=3.11"
```

**Fix**: Add required packages:

```toml
[dependencies]
python = ">=3.11"
fastmcp = "==0.3.0"
anthropic = "==0.40.0"
psycopg2-binary = "==2.9.9"
httpx = "==0.27.2"
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"
python-dotenv = ">=1.0.0"
```

---

## HIGH PRIORITY FIXES (Before Production Use)

### 4. Blocking API Calls in Startup Validation

**Location**: `coaching_mcp/server.py` lines 90-101 in `_validate_gong_api()`

**Issue**: Makes live Gong API call with 7-day date range during server startup. If network is slow or API is down, server startup will hang/timeout.

**Impact**: Horizon deployment may timeout during health checks.

**Fix**: Add timeout and make it optional:

```python
def _validate_gong_api() -> None:
    """Test Gong API authentication with minimal request."""
    from datetime import datetime, timedelta
    from gong.client import GongClient, GongAPIError

    try:
        with GongClient() as client:
            # Quick validation - just check auth, don't fetch data
            # Set 1-second timeout for fast failure
            client.client.timeout = 1.0

            # Use minimal date range (yesterday only)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=1)

            calls, _ = client.list_calls(
                from_date=from_date.isoformat() + "Z",
                to_date=to_date.isoformat() + "Z",
            )

            logger.info("✓ Gong API authentication successful")

    except TimeoutError:
        logger.warning("⚠ Gong API validation timed out (non-fatal)")
        # Don't exit - API may be slow but functional

    except GongAPIError as e:
        if "401" in str(e):
            logger.error("✗ Gong API authentication failed - invalid credentials")
            sys.exit(1)
        else:
            logger.warning(f"⚠ Gong API error (non-fatal): {e}")
```

### 5. Database Schema Not Validated

**Location**: `coaching_mcp/server.py` lines 49-76 in `_validate_database_connection()`

**Issue**: Only checks if database is reachable with `SELECT 1`, doesn't verify required tables exist.

**Impact**: Server could start successfully but fail when tools try to query non-existent tables.

**Fix**: Add table existence check:

```python
def _validate_database_connection() -> None:
    """Test database connectivity and schema."""
    from db import fetch_one

    try:
        if "sslmode=require" not in settings.database_url:
            logger.error("✗ DATABASE_URL must include sslmode=require for Neon")
            sys.exit(1)

        # Test connection
        result = fetch_one("SELECT 1 as test")
        if not result or result.get("test") != 1:
            logger.error("✗ Database query returned unexpected result")
            sys.exit(1)

        # Verify critical tables exist
        required_tables = ["calls", "speakers", "transcripts", "coaching_sessions"]
        for table in required_tables:
            result = fetch_one(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                (table,)
            )
            if not result or not result.get("exists"):
                logger.error(f"✗ Required table '{table}' does not exist in database")
                sys.exit(1)

        logger.info("✓ Database connection and schema validated")

    except Exception as e:
        logger.error(f"✗ Database validation failed: {e}")
        sys.exit(1)
```

### 6. Credential Exposure in Logs

**Location**: Multiple files

**Issue**: HTTP errors and connection failures may log full request/response including auth headers.

**Locations**:

- `gong/client.py` line 104 - logs full HTTP error response
- `db/connection.py` line 90 - connection string with password in error messages

**Fix**: Add log sanitization:

```python
# In gong/client.py
except HTTPStatusError as e:
    # Sanitize response before logging
    sanitized_msg = str(e).replace(self.api_key, "***KEY***")
    sanitized_msg = sanitized_msg.replace(self.api_secret, "***SECRET***")
    logger.error(f"Gong API error: {sanitized_msg}")
    raise GongAPIError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")

# In db/connection.py
except Exception as e:
    # Don't log connection string with password
    logger.error(f"Database connection failed: {type(e).__name__}")
    raise
```

---

## MEDIUM PRIORITY FIXES

### 7. Broad Exception Catching in Tools

**Location**: `coaching_mcp/tools/analyze_call.py` lines 96-97

**Issue**: Catches all exceptions and hides them in results:

```python
except Exception as e:
    return {"error": f"Failed to analyze call: {str(e)}"}
```

**Impact**: Hard to debug production failures - errors are silently swallowed.

**Fix**: Catch specific exceptions and re-raise unexpected ones:

```python
except (DatabaseError, GongAPIError) as e:
    return {"error": f"Failed to analyze call: {str(e)}"}
except Exception as e:
    logger.exception(f"Unexpected error analyzing call {call_id}")
    raise  # Re-raise for visibility
```

### 8. API Key Format Validation Too Strict

**Location**: `coaching_mcp/server.py` line 128-131

**Issue**: Hardcoded check for `sk-ant-` prefix will break if Anthropic changes format.

**Fix**: Make it more lenient:

```python
def _validate_anthropic_api() -> None:
    """Validate Anthropic API key format."""
    api_key = settings.anthropic_api_key

    # Basic validation - just check it's a reasonable length
    if not api_key or len(api_key) < 20:
        logger.error("✗ ANTHROPIC_API_KEY appears invalid (too short)")
        sys.exit(1)

    if not api_key.startswith("sk-"):
        logger.warning("⚠ ANTHROPIC_API_KEY format may be invalid (expected sk-* prefix)")
        # Don't exit - format may have changed

    logger.info("✓ Anthropic API key validated")
```

### 9. Missing Timeout on Database Queries

**Location**: All tool implementations

**Issue**: No query timeouts - could hang indefinitely on slow queries.

**Fix**: Add statement timeout in connection pool:

```python
# In db/connection.py
pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=settings.database_pool_min_size,
    maxconn=settings.database_pool_max_size,
    dsn=settings.database_url,
    options="-c statement_timeout=30000"  # 30 second timeout
)
```

---

## LOW PRIORITY IMPROVEMENTS

### 10. Remove Unused Dependency

**Location**: `pyproject.toml`

**Issue**: `asyncpg` is listed but never imported (code uses sync `psycopg2`).

**Fix**: Remove from dependencies or document why it's needed.

### 11. Mixed Dependency Pinning Strategy

**Location**: `pyproject.toml`

**Issue**: Some packages pinned (`fastmcp==0.3.0`), others use `>=` (`prefect>=3.0.0`).

**Fix**: Pin all versions for reproducibility or use `uv.lock` file exclusively.

---

## DEPLOYMENT CHECKLIST

Before attempting another deployment:

- [ ] Fix SQL injection in search_calls.py (CRITICAL)
- [ ] Fix array parameter handling in search_calls.py (CRITICAL)
- [ ] Add package dependencies to fastmcp.toml (CRITICAL)
- [ ] Add timeout to Gong API validation (HIGH)
- [ ] Add database schema validation (HIGH)
- [ ] Sanitize credentials in logs (HIGH)
- [ ] Test locally with `uv run python -m coaching_mcp.server`
- [ ] Verify all 3 tools work without errors
- [ ] Push fixes to GitHub
- [ ] Redeploy to Horizon
- [ ] Check deployment logs for successful validation
- [ ] Test tools via Claude Desktop

---

## Testing Commands

After applying fixes, test locally:

```bash
# 1. Test server starts
uv run python -m coaching_mcp.server

# 2. Test imports work
uv run python -c "from shared import settings; print('✓')"

# 3. Test database connection
uv run python -c "from db import fetch_one; fetch_one('SELECT 1')"

# 4. Test Gong client
uv run python -c "from gong.client import GongClient; print('✓')"

# 5. Run any existing tests
uv run pytest tests/ -v
```

---

## Architecture Strengths (Keep These)

✅ **Clean module structure** - No circular dependencies, proper layering
✅ **Comprehensive error logging** - Good use of logger throughout
✅ **Environment variable management** - Centralized in shared/config.py
✅ **PYTHONPATH handling** - Explicit sys.path setup in server.py
✅ **Tool registration pattern** - Clean FastMCP decorators with delegation
✅ **Validation framework** - Optional, well-structured startup checks

Don't break these during fixes!
