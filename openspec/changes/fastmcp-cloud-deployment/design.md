## Context

The Gong Call Coaching Agent MCP server currently runs locally with `uv run python mcp/server.py`. Three coaching tools (analyze_call, get_rep_insights, search_calls) require direct database access to Neon PostgreSQL and authenticated API calls to Gong and Anthropic.

**Current State:**

- MCP server defined in `mcp/server.py` using FastMCP framework
- Dependencies managed via `pyproject.toml` with uv
- Environment variables loaded from `.env` file (DATABASE_URL, GONG_API_KEY, GONG_API_SECRET, ANTHROPIC_API_KEY)
- Tools query production database directly (no caching layer)

**Deployment Target:**

- Prefect Horizon MCP server registry at `https://horizon.prefect.io/prefect-george/servers`
- FastMCP Cloud authentication via API key: `fmcp_F6rhqd9oFr1HOzNu6hOa5VBfwh2iXsKYWofXqPGTzqc`
- Must support secure environment variable injection
- Multi-user access via Claude Desktop

**Constraints:**

- Cannot bundle credentials in code or config files
- Database connections must use SSL (Neon requirement: `?sslmode=require`)
- Gong API requires tenant-specific base URL (`https://us-79647.api.gong.io/v2`)
- MCP server must start within 30 seconds (Horizon timeout)

## Goals / Non-Goals

**Goals:**

- Deploy MCP server to FastMCP Cloud accessible via Prefect Horizon
- Securely manage production credentials (no secrets in repo)
- Maintain 100% feature parity with local development
- Enable team-wide access to coaching tools via Claude Desktop
- Add pre-deployment validation (DB connectivity, API key testing)

**Non-Goals:**

- Modifying MCP tool implementations (they work as-is)
- Adding authentication/authorization layer (Horizon handles this)
- Caching or performance optimization (defer to Phase 6)
- Multi-tenant support (single Prefect workspace deployment)

## Decisions

### Decision 1: FastMCP Cloud + Prefect Horizon Integration

**Choice:** Deploy to FastMCP Cloud via Prefect Horizon MCP server registry

**Rationale:**

- User already has Horizon workspace (`prefect-george`)
- FastMCP Cloud provides managed hosting with zero infra overhead
- Native integration with Claude Desktop via Horizon
- Automatic SSL/TLS and credential management

**Alternatives Considered:**

- ❌ Self-hosted Docker container: Requires infrastructure management, monitoring, updates
- ❌ AWS Lambda: Cold start times exceed 30s due to psycopg2 binary, TikToken model loading
- ❌ Modal: Great for ML but overkill for 3 simple tools, adds vendor dependency

### Decision 2: Environment Variable Management

**Choice:** Use Horizon UI for credential injection, `fastmcp.toml` for variable names only

**Rationale:**

- Horizon UI provides secure secret storage with encryption at rest
- Variables injected at runtime (never logged or exposed)
- `fastmcp.toml` serves as documentation of required vars
- No secrets committed to git

**Implementation:**

```toml
[server.env]
GONG_API_KEY = "${GONG_API_KEY}"          # Placeholder syntax
GONG_API_SECRET = "${GONG_API_SECRET}"
DATABASE_URL = "${DATABASE_URL}"
```

Actual values set in Horizon UI during deployment.

### Decision 3: Deployment Validation Strategy

**Choice:** Add startup validation in `mcp/server.py` with fail-fast behavior

**Rationale:**

- Catch configuration errors before tools are invoked
- Provide clear error messages for missing credentials
- Validate connectivity to external services (DB, Gong, Anthropic)

**Validation Sequence:**

1. Check all required env vars present
2. Test database connection with simple query (`SELECT 1`)
3. Validate Gong API credentials (`GET /calls` with date range)
4. Verify Anthropic API key (lightweight endpoint check)
5. Log success or fail with specific error

**Trade-off:** Adds 2-3s to startup time, but prevents silent failures.

### Decision 4: Dependency Pinning

**Choice:** Pin exact versions in `pyproject.toml` for cloud deployment

**Rationale:**

- Avoid surprise breakage from transitive dependency updates
- FastMCP Cloud caches built environments per dependency hash
- Local dev can use looser constraints (`>=`) for flexibility

**Pinned Dependencies:**

```toml
dependencies = [
    "fastmcp==0.3.0",
    "anthropic==0.40.0",
    "psycopg2-binary==2.9.9",
    "httpx==0.27.2",
]
```

## Risks / Trade-offs

### Risk 1: Database Connection Exhaustion

**Risk:** Cloud MCP server may exhaust Neon connection pool (5-20 connections) if multiple users invoke tools simultaneously.

**Mitigation:**

- Connection pooling already configured in `db/connection.py`
- Monitor Neon dashboard for connection spikes
- Phase 6 (Production Hardening) will add connection limits per user

### Risk 2: Cold Start Latency

**Risk:** First tool invocation after idle period may take 10-15s as FastMCP Cloud provisions container.

**Mitigation:**

- Acceptable for coaching use case (not real-time)
- Horizon provides warmup configuration if needed
- Document expected latency in README

### Risk 3: Credential Rotation

**Risk:** If Gong/Anthropic keys rotate, cloud deployment breaks until manually updated in Horizon UI.

**Mitigation:**

- Document credential update process in README
- Set calendar reminder for quarterly key rotation
- Future: Add Prefect Secret Block integration for automated rotation

### Risk 4: Cost Overrun

**Risk:** Unlimited Claude API calls could spike costs if users run expensive analyses.

**Mitigation:**

- Existing cache layer (SHA256 transcript hash + rubric version) reduces duplicate analyses
- Phase 6 will add per-user rate limiting
- Monitor Anthropic usage dashboard weekly

## Migration Plan

**Deployment Steps:**

1. Push code with `fastmcp.toml` and `.fastmcp/config.json`
2. Navigate to <https://horizon.prefect.io/prefect-george/servers>
3. Create new MCP server:
   - Name: `gong-call-coach`
   - Runtime: Python 3.11
   - Command: `uv run python mcp/server.py`
   - Working Directory: `/app`
4. Set environment variables in Horizon UI (copy from local `.env`)
5. Deploy and wait for "Ready" status
6. Test with Claude Desktop:
   - `analyze_call("1464927526043145564")`
   - `get_rep_insights("sarah.jones@prefect.io")`
   - `search_calls(call_type="discovery", min_score=70)`

**Rollback Strategy:**

- If deployment fails validation: Fix locally, redeploy
- If tools error in production: Disable server in Horizon UI, investigate with logs
- Users can continue with local MCP server (no downtime for development)

**No Data Migration:** Database schema unchanged, no data transformation needed.

## Open Questions

1. **What is the FastMCP Cloud `fmcp_*` key used for?** Assumed to be server authentication to FastMCP registry. Need to confirm if it's passed as env var or CLI flag during deployment.

2. **Does Horizon support file-based config upload?** If yes, can bundle `fastmcp.toml` and `.fastmcp/config.json` in deployment. If no, need to manually configure in UI.

3. **What is the observability story?** How do we access logs for debugging? Does Horizon provide metrics dashboard for tool invocation counts, latency, errors?

**Resolution Path:** Test deployment to staging environment first, document actual behavior, update design doc accordingly.
