# Prefect MCP Server Integration

## Problem

The Call Coach application could benefit from direct access to Prefect documentation and API knowledge during coaching analysis. When analyzing calls about Prefect Cloud, the coaching system needs accurate, up-to-date information about:

- Product capabilities and features
- Pricing tiers and what's included
- Technical architecture and best practices
- Common objections and how to address them

Currently, this knowledge is statically embedded in prompts. The Prefect MCP server provides a docs proxy that could keep this knowledge current.

## Proposed Solution

Integrate the [Prefect MCP server](https://docs.prefect.io/v3/how-to-guides/ai/use-prefect-mcp-server) as an MCP client in the Call Coach backend to provide:

1. **Real-time documentation access** during call analysis
2. **Product knowledge validation** - verify claims made in calls against actual documentation
3. **Feature accuracy checking** - ensure coaching feedback references correct capabilities

## Integration Approach

### Option A: Server-side MCP Client (Recommended)

Add the Prefect MCP server as a dependency in the coaching analysis pipeline:

```python
# In analysis/engine.py or similar
from prefect_mcp import PrefectMCPClient

async def get_product_context(topic: str) -> str:
    """Query Prefect docs for relevant product information."""
    client = PrefectMCPClient()
    docs = await client.search_docs(topic)
    return docs
```

**Pros:**
- Single point of integration
- Can cache responses
- Doesn't require end-user credentials

**Cons:**
- Adds latency to analysis
- Requires managing MCP connection lifecycle

### Option B: Knowledge Base Sync

Periodically sync Prefect documentation into the existing knowledge base:

```bash
# Cron job or scheduled task
python scripts/sync_prefect_docs.py
```

**Pros:**
- No runtime dependency on external MCP server
- Faster analysis (local data)

**Cons:**
- Documentation can become stale
- More complex sync logic

## Configuration

Add to `.env`:

```bash
# Prefect MCP Server (for product knowledge)
PREFECT_MCP_ENABLED=true
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/[ACCOUNT_ID]/workspaces/[WORKSPACE_ID]
PREFECT_API_KEY=pnu_xxxx  # Read-only key for docs access
```

## MCP Server Capabilities

The Prefect MCP server provides:

### Tools
- **Dashboard overview** - System health and statistics
- **Query deployments** - Deployment configurations and status
- **Query flow runs** - Execution history and logs
- **Query work pools** - Infrastructure status
- **Search docs** - Documentation proxy for current API syntax and best practices

### Resources
- Deployment configurations
- Flow run logs
- Work pool status
- Event history

## Use Cases for Call Coach

### 1. Product Knowledge Validation

When analyzing a call where a rep describes Prefect features:

```python
# Example: Rep claims "Prefect has automatic retries"
docs = await prefect_mcp.search_docs("automatic retries task configuration")
# Returns current documentation on retry configuration
# Coaching can validate if rep's explanation was accurate
```

### 2. Objection Response Enhancement

When a prospect raises a technical objection:

```python
# Example: Prospect asks about Kubernetes support
docs = await prefect_mcp.search_docs("kubernetes worker infrastructure")
# Coaching can suggest accurate technical responses
```

### 3. Competitive Positioning

When Airflow/Dagster/etc. are mentioned:

```python
# Example: Prospect mentions they're evaluating Airflow
docs = await prefect_mcp.search_docs("migration from airflow")
# Returns migration guides and comparison points
```

## Implementation Steps

1. **Add prefect-mcp dependency**
   ```bash
   uv add prefect-mcp
   ```

2. **Create MCP client wrapper** in `services/prefect_mcp.py`

3. **Integrate into analysis engine** - Add optional product context enrichment

4. **Update prompts** - Reference MCP-sourced documentation instead of static content

5. **Add caching layer** - Cache doc queries to reduce latency

## Security Considerations

- Use read-only API key with minimal permissions
- MCP server provides read-only access by design
- No sensitive customer data flows to Prefect API

## Sources

- [Prefect MCP Server Documentation](https://docs.prefect.io/v3/how-to-guides/ai/use-prefect-mcp-server)
- [GitHub: PrefectHQ/prefect-mcp-server](https://github.com/PrefectHQ/prefect-mcp-server)
- [Prefect Blog: Introducing the MCP Server](https://www.prefect.io/blog/a-prefect-mcp-server)
