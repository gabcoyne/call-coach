# Horizon Deployment Configuration

## Current Issue

The deployment is failing with "No module named 'coaching_mcp'" because Horizon is trying to run the server as a Python module instead of importing it as a file.

## Correct Horizon Configuration

When configuring the server in the Horizon UI, use these settings:

### Server Entrypoint
```
launcher.py:mcp
```

**Alternative (if launcher doesn't work)**: Add `--with-editable .` flag to install the package first

The launcher script handles installing the `coaching_mcp` package before importing the server.

### Explanation

According to FastMCP documentation, Horizon expects:
- **Format**: `path/to/file.py:variable_name`
- **Our server**: The FastMCP instance is created at line 216 of `coaching_mcp/server.py` as `mcp = FastMCP("Gong Call Coaching Agent")`
- **Therefore**: Use `coaching_mcp/server.py:mcp`

Horizon will:
1. Clone the GitHub repository
2. Install dependencies from `requirements.txt` or `pyproject.toml`
3. Import the file directly: `from coaching_mcp.server import mcp`
4. Run the FastMCP instance

## Dependencies

Horizon will auto-detect dependencies. Ensure we have either:

### Option 1: requirements.txt (Recommended)
Create a `requirements.txt` with:
```
fastmcp==0.3.0
anthropic==0.40.0
psycopg2-binary==2.9.9
httpx==0.27.2
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

### Option 2: pyproject.toml
Horizon can also read from `pyproject.toml` if it exists.

## Environment Variables

Configure these in Horizon UI under "Environment Variables":

```bash
GONG_API_KEY=<your-gong-api-key>
GONG_API_SECRET=<your-gong-api-secret>
GONG_API_BASE_URL=https://api.gong.io
ANTHROPIC_API_KEY=<your-anthropic-api-key>
DATABASE_URL=<your-neon-postgres-url>
GONG_WEBHOOK_SECRET=<your-webhook-secret>
LOG_LEVEL=INFO
SKIP_VALIDATION=false  # Set to true to skip startup validation
```

## Testing the Fix

1. **Go to Horizon UI** → Your call-coach server
2. **Click "Settings" or "Configuration"**
3. **Update the entrypoint to**: `coaching_mcp/server.py:mcp`
4. **Save and redeploy**

The server should now start successfully!

## Verification

Once deployed, you should see in the logs:
```
🚀 MCP server ready - 3 tools registered
```

And in Claude Desktop, you should see 3 tools available:
- `analyze_call`
- `get_rep_insights`
- `search_calls`
