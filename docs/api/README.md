# API Documentation

Complete reference for the Call Coach REST API and MCP tools.

## Overview

The Call Coach system provides two API interfaces:

1. **MCP Protocol** - For Claude Desktop and AI assistants (recommended)
2. **REST API** - For web frontends and custom integrations

Both interfaces provide access to the same coaching analysis tools.

## Quick Start

### Using MCP (Claude Desktop)

The easiest way to get started is using Claude Desktop with the MCP server:

```
To analyze call abc-123 and focus on discovery quality
To show me Sarah's performance trends this month
To find all discovery calls from last month with pricing objections
```

### Using REST API

For web application integration:

```bash
curl -X POST http://localhost:8000/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d '{
    "gong_call_id": "1464927526043145564",
    "focus_area": "discovery"
  }'
```

## Authentication

### Local Development
No authentication required when running locally.

### Production (Horizon Deployment)
- MCP tools use Horizon's built-in authentication
- REST API requests should include Bearer token (if enabled)

### Environment Variables

```bash
# Required for all deployments
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...?sslmode=require
GONG_API_KEY=your_key
GONG_API_SECRET=your_secret

# Optional for custom deployments
LOG_LEVEL=INFO
GONG_WEBHOOK_SECRET=optional_secret
```

See [Environment Variables](../deployment/environment.md) for complete reference.

## Core Concepts

### Coaching Dimensions

The system analyzes calls across four coaching dimensions:

1. **Discovery** - Understanding customer needs and pain points
2. **Product Knowledge** - Demonstrating deep product expertise
3. **Objection Handling** - Addressing and overcoming customer concerns
4. **Engagement** - Building rapport and customer relationships

Each dimension generates:
- Dimension-specific scores (0-100)
- Key findings and observations
- Actionable coaching recommendations

### Call Analysis

The system processes Gong call data to:
1. Fetch transcript from Gong API
2. Extract speakers and their roles
3. Chunk long transcripts for analysis
4. Analyze across 4 coaching dimensions
5. Generate recommendations
6. Cache results for future queries

Typical analysis time: 15-45 seconds per call

### Performance Insights

Rep performance tracking includes:
- Weekly coaching scores across dimensions
- Performance trends over time
- Skill gap identification
- Personalized development plans

## API Tools

### 1. Analyze Call

Analyze a single call transcript for coaching insights.

**Tool Name**: `analyze_call`

**Parameters**:
- `gong_call_id` (string, required): The Gong call ID to analyze
- `focus_area` (string, optional): Specific dimension to focus on
  - Valid values: "discovery", "product", "objections", "engagement"
  - If not specified, all dimensions analyzed

**Response**:
```json
{
  "call_id": "1464927526043145564",
  "call_duration": 1800,
  "dimensions": {
    "discovery": {
      "score": 85,
      "findings": [
        "Rep effectively asked about customer's current tools",
        "Could dig deeper into timeline and budget"
      ],
      "recommendations": [
        "Ask about implementation timeline earlier",
        "Clarify budget allocation process"
      ]
    },
    "product_knowledge": {
      "score": 92,
      "findings": ["Strong understanding of Horizon features"],
      "recommendations": []
    },
    "objection_handling": {
      "score": 78,
      "findings": ["Good response to pricing objection"],
      "recommendations": ["Practice scaling objections"]
    },
    "engagement": {
      "score": 88,
      "findings": ["Strong rapport with customer"],
      "recommendations": []
    }
  },
  "overall_score": 86,
  "summary": "Strong discovery call with solid product knowledge...",
  "key_themes": ["discovery", "relationship-building"]
}
```

### 2. Get Rep Insights

Retrieve performance metrics and trends for a specific rep.

**Tool Name**: `get_rep_insights`

**Parameters**:
- `rep_email` (string, required): The rep's email address
- `time_period` (string, optional): Analysis period
  - Valid values: "week", "month", "quarter"
  - Default: "month"

**Response**:
```json
{
  "rep_email": "sarah.jones@prefect.io",
  "period": "month",
  "calls_analyzed": 12,
  "average_scores": {
    "discovery": 82,
    "product_knowledge": 88,
    "objection_handling": 75,
    "engagement": 85
  },
  "trend": "improving",
  "skill_gaps": [
    "Objection handling - practice overcoming price concerns",
    "Discovery - ask more qualifying questions"
  ],
  "coaching_plan": [
    {
      "dimension": "objection_handling",
      "priority": "high",
      "recommendation": "Role-play pricing objection scenarios",
      "target_improvement": "+10 points"
    }
  ],
  "top_calls": [
    {
      "call_id": "123456",
      "call_type": "demo",
      "score": 95,
      "date": "2026-02-03"
    }
  ]
}
```

### 3. Search Calls

Find calls matching specific criteria.

**Tool Name**: `search_calls`

**Parameters**:
- `query` (string, required): Search query
  - Searches: title, product, call type, participant names
  - Examples: "discovery", "pricing objection", "Sarah", "Horizon"
- `filters` (object, optional):
  - `call_type`: "discovery", "demo", "negotiation", "technical_deep_dive"
  - `product`: "prefect", "horizon", "both"
  - `min_score`: Minimum coaching score (0-100)
  - `date_from`: Start date (ISO 8601)
  - `date_to`: End date (ISO 8601)
  - `rep_email`: Filter by specific rep
- `limit` (integer, optional): Max results to return (default: 10, max: 100)

**Response**:
```json
{
  "query": "discovery pricing",
  "total_results": 24,
  "results": [
    {
      "call_id": "1464927526043145564",
      "title": "Acme Corp - Discovery Call",
      "date": "2026-02-03T14:30:00Z",
      "duration": 1800,
      "call_type": "discovery",
      "product": "horizon",
      "rep_name": "Sarah Jones",
      "rep_email": "sarah.jones@prefect.io",
      "score": 92,
      "key_topics": ["pricing", "discovery", "feature-request"],
      "summary": "Strong discovery call with clear pricing discussion..."
    }
  ],
  "filters_applied": {
    "call_type": null,
    "product": null,
    "min_score": 0
  }
}
```

## Error Handling

### Common Errors

**400 Bad Request**
- Missing required parameters
- Invalid parameter values
- Malformed JSON

**401 Unauthorized**
- Missing or invalid API credentials
- Session expired

**404 Not Found**
- Call ID not found in database
- Rep email not found

**429 Too Many Requests**
- Rate limit exceeded
- Wait before retrying

**500 Internal Server Error**
- Database connection failure
- Claude API unavailable
- Unexpected service error

See [API Error Codes](../troubleshooting/api-errors.md) for detailed error handling.

## Rate Limiting

**MCP Tools**: No rate limits (local or Horizon deployment)

**REST API**:
- Local development: Unlimited
- Production (Horizon): 100 requests/minute per API key

When rate limited, the API returns `429 Too Many Requests` with:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## Caching & Performance

### Smart Caching

Results are cached based on:
```
cache_key = hash(transcript + dimension + rubric_version)
```

**Cache hits**: Typically achieve 60-80% hit rate
**Cache TTL**: 30 days (configurable)
**Cost savings**: 60-80% reduction vs. uncached baseline

### Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Analyze call (cold) | 30-45s | First analysis, no cache |
| Analyze call (hit) | <1s | From cache |
| Rep insights (cold) | 45-120s | Analyzes multiple calls |
| Rep insights (hit) | 2-5s | From cache |
| Search calls | 1-5s | Database query |

## API Versions

Current version: **1.0.0**

### Changelog

**v1.0.0** (2026-02-05)
- Initial API release
- 3 core tools: analyze_call, get_rep_insights, search_calls
- MCP and REST interfaces
- Intelligent caching

### Backwards Compatibility

The API maintains backwards compatibility with previous versions. Deprecated features will be marked and provided 6 months notice before removal.

## Integration Examples

### Python

```python
import requests
import json

# Analyze a call
response = requests.post(
    "http://localhost:8000/coaching/analyze-call",
    json={
        "gong_call_id": "1464927526043145564",
        "focus_area": "discovery"
    }
)

analysis = response.json()
print(f"Overall Score: {analysis['overall_score']}")
for dim, data in analysis['dimensions'].items():
    print(f"  {dim}: {data['score']}")
```

### JavaScript/TypeScript

```typescript
// Using fetch API
const response = await fetch('http://localhost:8000/coaching/analyze-call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    gong_call_id: '1464927526043145564',
    focus_area: 'discovery'
  })
});

const analysis = await response.json();
console.log(`Overall Score: ${analysis.overall_score}`);
```

### cURL

```bash
# Analyze call
curl -X POST http://localhost:8000/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d '{
    "gong_call_id": "1464927526043145564",
    "focus_area": "discovery"
  }'

# Get rep insights
curl -X POST http://localhost:8000/coaching/rep-insights \
  -H "Content-Type: application/json" \
  -d '{
    "rep_email": "sarah.jones@prefect.io",
    "time_period": "month"
  }'

# Search calls
curl -X POST http://localhost:8000/coaching/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "discovery pricing",
    "filters": {
      "product": "horizon",
      "min_score": 80
    }
  }'
```

## Interactive API Documentation

When running locally, view interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces let you test API calls directly from your browser.

## Next Steps

- [Detailed Endpoint Reference](./endpoints.md) - All parameters and responses
- [Error Code Reference](../troubleshooting/api-errors.md) - Troubleshooting
- [Integration Guide](../developers/adding-features.md) - Custom integrations
- [REST Endpoints](./endpoints.md) - Complete endpoint documentation
