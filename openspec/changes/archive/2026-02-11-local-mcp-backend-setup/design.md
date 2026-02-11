# Design

## Context

**Current State:**

- FastMCP backend server exists at `coaching_mcp/server.py` with 3 tools (analyze_call, get_rep_insights, search_calls)
- Configuration uses Pydantic Settings in `coaching_mcp/shared/config.py` with `env_file=".env"`
- `.env` file exists in project root with all required credentials (Gong, Anthropic, Database)
- Server validation requires all env vars and validates database connectivity on startup
- No local development workflow - server was designed for Horizon deployment only

**Problem:**

- Pydantic Settings `env_file=".env"` looks for `.env` relative to the module location (`coaching_mcp/shared/`), not project root
- Server fails with "Missing required environment variables" even though `.env` exists
- Strict validation (Gong API check, database table verification) blocks local dev if APIs are slow or unavailable

**Constraints:**

- Must use `uv` for all Python operations (per project standards)
- Cannot modify database schema or backend tool implementations
- Must maintain compatibility with Horizon deployment
- Frontend expects backend at localhost:8000 (hardcoded in frontend/.env.local as NEXT_PUBLIC_MCP_BACKEND_URL)

## Goals / Non-Goals

**Goals:**

- Enable local FastMCP server development with single `uv` command
- Fix `.env` file loading to work from project root
- Add optional `--dev` mode that relaxes validation for faster iteration
- Create comprehensive backend documentation (CLAUDE.md) covering architecture, development, and testing
- Document full-stack local workflow (frontend + backend + database)
- Make it easy for new contributors to get started in <5 minutes

**Non-Goals:**

- Changing backend tool implementations or adding new tools
- Modifying database schema or migration strategy
- Setting up Docker/containerization (local database uses existing Neon connection)
- Creating mock/stub services (use real Gong API, real database)
- Hot-reload during development (restart server manually - simple enough)

## Decisions

### Decision 1: Fix `.env` Loading with Explicit Path Resolution

**Choice:** Modify `coaching_mcp/shared/config.py` to explicitly find project root and load `.env` from there.

**Alternatives Considered:**

1. **Symlink `.env` into `coaching_mcp/shared/`** - Brittle, doesn't work cross-platform, easy to forget
2. **Use `python-dotenv` explicitly before Settings** - Redundant with Pydantic Settings, but might be needed
3. **Set `env_file` to absolute path** - Requires finding project root dynamically

**Rationale:**
Use `pathlib` to walk up from `__file__` until finding project root (has `.git` or `pyproject.toml`), then construct absolute path to `.env`. This works in both local dev and Horizon deployment.

```python
from pathlib import Path

def find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current.parent  # Fallback to parent of this file

PROJECT_ROOT = find_project_root()
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        # ... rest of config
    )
```

**Trade-off:** Adds ~10 lines of code, but solves the problem reliably across environments.

### Decision 2: Add `--dev` Flag for Relaxed Validation

**Choice:** Add `--dev` command-line flag that skips expensive validations (Gong API check, relaxes database table checks).

**Alternatives Considered:**

1. **Environment variable `DEV_MODE=true`** - Less discoverable, requires changing `.env`
2. **Separate `dev_server.py` script** - Code duplication, harder to maintain
3. **No relaxed mode** - Forces slow startups during iteration

**Rationale:**
CLI flag is most explicit and discoverable. Keep all validation code but wrap in `if not dev_mode:` checks. For dev mode:

- Skip Gong API connectivity check (uses real API, but don't validate at startup)
- Only check database connection, not table existence (assumes migrations ran)
- Log warnings instead of errors for missing optional env vars

**Implementation:**

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dev", action="store_true", help="Development mode with relaxed validation")
args = parser.parse_args()

if not args.dev:
    _validate_gong_api()
    _validate_database_tables()
else:
    logger.info("🏗️  Dev mode: skipping expensive validations")
    _validate_database_connection_only()
```

### Decision 3: Use `pyproject.toml` Scripts for uv Integration

**Choice:** Add `[project.scripts]` entries in `pyproject.toml` for easy invocation:

```toml
[project.scripts]
mcp-server = "coaching_mcp.server:main"
mcp-server-dev = "coaching_mcp.server:main_dev"  # Wrapper that adds --dev
```

**Alternatives Considered:**

1. **Shell script `run-mcp-server.sh`** - Works, but less integrated with Python tooling
2. **Makefile targets** - Another tool to learn, not Python-native
3. **Just `uv run python -m`** - Verbose, easy to forget flags

**Rationale:**
`uv run mcp-server-dev` is clearest and shortest. Shell script as fallback for those who prefer it. Both approaches documented in CLAUDE.md.

### Decision 4: Frontend Backend URL Configuration

**Choice:** Add `NEXT_PUBLIC_MCP_BACKEND_URL` to `frontend/.env.local` with default `http://localhost:8000`.

**Current State:** Frontend MCP client likely hardcodes or uses build-time env var.

**Change Needed:** Update `frontend/lib/mcp-client.ts` to read from env var with fallback:

```typescript
const MCP_BACKEND_URL = process.env.NEXT_PUBLIC_MCP_BACKEND_URL || "http://localhost:8000";
```

This allows production to override (e.g., `https://mcp.prefect.io`) without code changes.

### Decision 5: CLAUDE.md Structure

**Choice:** Create comprehensive `CLAUDE.md` at project root covering:

1. **Quick Start** - Get server running in <5 min
2. **Architecture** - How backend is structured
3. **Development Workflow** - Edit → Test → Debug cycle
4. **Testing** - Unit tests, integration tests, manual tool testing
5. **Troubleshooting** - Common errors and fixes
6. **Deployment** - Differences between local and Horizon

**Rationale:**
Single source of truth for backend development. Agents and humans can reference it. Reduces "how do I..." questions.

## Risks / Trade-offs

**Risk:** Finding project root could fail in unusual setups (e.g., symlinked checkouts, Docker without `.git`)

- **Mitigation:** Fallback to `Path(__file__).parent.parent.parent` (3 levels up from `coaching_mcp/shared/config.py`)

**Risk:** Dev mode skips validations that could catch real issues

- **Mitigation:** Document clearly that `--dev` is for LOCAL ONLY, always test without --dev before pushing

**Risk:** Database migrations might not be current when using --dev

- **Mitigation:** Add note to run `prefect db upgrade` if seeing missing table errors

**Trade-off:** Two ways to run server (`uv run mcp-server-dev` vs `uv run python -m coaching_mcp.server --dev`) could confuse users

- **Decision:** Document both, recommend `mcp-server-dev` for simplicity

**Risk:** Frontend still shows errors if backend starts but tools fail

- **Mitigation:** Add health check endpoint that frontend can poll

## Migration Plan

**Phase 1: Fix Config (No Breaking Changes)**

1. Update `coaching_mcp/shared/config.py` with project root finding logic
2. Test that `.env` loads correctly: `uv run python -c "from coaching_mcp.shared import settings; print(settings.gong_api_key[:10])"`
3. Verify server starts with full validation: `uv run python -m coaching_mcp.server`

**Phase 2: Add Dev Mode**

1. Add `--dev` argument parsing to `coaching_mcp/server.py`
2. Wrap validation calls in `if not dev_mode:` blocks
3. Add dev-specific logging
4. Test dev mode startup: `uv run python -m coaching_mcp.server --dev`

**Phase 3: Add Scripts & Documentation**

1. Add `[project.scripts]` to `pyproject.toml`
2. Create `CLAUDE.md` with all sections
3. Update root `README.md` with Quick Start section pointing to CLAUDE.md
4. Create `scripts/check-backend.sh` health check script

**Phase 4: Frontend Integration**

1. Add `NEXT_PUBLIC_MCP_BACKEND_URL` to `frontend/.env.example`
2. Update `frontend/lib/mcp-client.ts` to use env var
3. Test full-stack: start backend, start frontend, verify tools work

**Rollback:**

- Phase 1-2 are backwards compatible (no breaking changes)
- Phase 3-4 are additive only (docs and scripts)
- No rollback needed - changes are all improvements

## Open Questions

**Q1:** Should we add a health check endpoint (`GET /health`) that frontend can poll?

- **Answer:** Yes, add simple endpoint that returns `{"status": "ok", "tools": 3}` - useful for monitoring

**Q2:** Should dev mode automatically mock Gong API calls to avoid rate limits?

- **Answer:** No, use real APIs. Rate limits are high enough for dev. Mocking adds complexity.

**Q3:** Do we need hot-reload with `watchfiles` or similar?

- **Answer:** No, manual restart is fine for now. Can add later if needed. Keep simple.

**Q4:** Should we support multiple environments (.env.development, .env.production)?

- **Answer:** No, single `.env` for now. Horizon uses environment variables, not files. Local = .env, Horizon = UI config.
