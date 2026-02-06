# Horizon Deployment Configuration - FastMCP Best Practices

## The Right Way: fastmcp.json

According to FastMCP documentation, the best practice for Horizon deployment is to use a `fastmcp.json` configuration file. This file is now included in the repository.

### What fastmcp.json does

```json
{
  "source": {
    "path": "coaching_mcp/server.py", // Path to the server file
    "entrypoint": "mcp" // Variable name of the FastMCP instance
  },
  "environment": {
    "type": "uv",
    "project": ".", // Use pyproject.toml in current directory
    "editable": ["."] // Install current directory as editable package
  }
}
```

The **`"editable": ["."]`** is the key - it tells Horizon to install the current directory as an editable Python package before importing the server. This makes all `from coaching_mcp.*` imports work correctly.

## Horizon UI Configuration

### Entrypoint

```
coaching_mcp/server.py:mcp
```

This means:

- **File**: `coaching_mcp/server.py`
- **Variable**: `mcp` (the FastMCP instance at line 216 in that file)

### How Horizon Will Build It

1. Clone GitHub repository
2. Read `fastmcp.json` configuration
3. Install dependencies from `pyproject.toml` (detected via `"project": "."`)
4. Install current directory as editable package (via `"editable": ["."]`)
5. Import: `from coaching_mcp.server import mcp`
6. Run the server

### Environment Variables

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

## Why Previous Approaches Failed

1. **`python -m coaching_mcp.server`** - Requires parent directory in PYTHONPATH
2. **`coaching_mcp/server.py:mcp` alone** - Package not installed, imports fail
3. **`launcher.py`** - Workaround, not best practice

## Best Practice (Current Approach)

Use `fastmcp.json` with `"editable": ["."]` to install the local package properly. This follows FastMCP's documented pattern for projects with local packages.

## Verification

Once deployed, check logs for:

```
🚀 MCP server ready - 3 tools registered
```

And in Claude Desktop, verify 3 tools are available:

- `analyze_call`
- `get_rep_insights`
- `search_calls`

## References

- [FastMCP Environment Configuration](https://gofastmcp.com/deployment/server-configuration#environment-configuration)
- [FastMCP Horizon Deployment](https://gofastmcp.com/deployment/prefect-horizon)
