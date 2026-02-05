## Why

The Gong Call Coaching Agent's MCP server is currently only runnable locally, limiting accessibility to sales managers and coaches who need on-demand insights. Deploying to FastMCP Cloud (integrated with Prefect Horizon) will make the three coaching tools (analyze_call, get_rep_insights, search_calls) accessible to the entire team via Claude Desktop without local setup, while maintaining secure access to production databases and Gong API credentials.

## What Changes

- Add FastMCP Cloud deployment configuration files (`fastmcp.toml`, `.fastmcp/config.json`)
- Create Prefect Horizon deployment manifest with proper environment variable handling
- Add deployment script (`.fastmcp/deploy.sh`) with pre-deployment validation
- Update README with cloud deployment instructions and Horizon integration steps
- Add production readiness checks (database connectivity, API key validation, MCP tool testing)
- Configure secure environment variable management for cloud deployment

## Capabilities

### New Capabilities
- `fastmcp-cloud-config`: FastMCP Cloud deployment configuration including runtime, dependencies, and environment variable specifications
- `horizon-integration`: Prefect Horizon MCP server integration with proper authentication and working directory setup
- `cloud-env-management`: Secure environment variable configuration for cloud deployments with validation
- `deployment-validation`: Pre-deployment health checks for database, Gong API, and Claude API connectivity

### Modified Capabilities
<!-- No existing specs are being modified - this is net new cloud deployment capability -->

## Impact

**New Files**:
- `fastmcp.toml` - FastMCP project configuration
- `.fastmcp/config.json` - Cloud deployment metadata
- `.fastmcp/deploy.sh` - Deployment automation script
- `openspec/changes/fastmcp-cloud-deployment/` - OpenSpec artifacts

**Modified Files**:
- `README.md` - Add cloud deployment section with Horizon integration
- `mcp/server.py` - Add startup validation logging for cloud environment
- `pyproject.toml` - Ensure all FastMCP Cloud dependencies are pinned

**External Systems**:
- **Prefect Horizon**: New MCP server at `https://horizon.prefect.io/prefect-george/servers`
- **FastMCP Cloud**: Server authentication via `fmcp_F6rhqd9oFr1HOzNu6hOa5VBfwh2iXsKYWofXqPGTzqc`
- **Neon Database**: Cloud server needs production database access (already configured)
- **Gong API**: Cloud server needs tenant-specific URL (`https://us-79647.api.gong.io/v2`)
- **Anthropic API**: Cloud server needs Claude API access for analysis

**No Breaking Changes**: Existing local development workflow remains unchanged.
