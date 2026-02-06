# REST API Endpoints Reference

Complete reference for all REST API endpoints with request/response examples.

## Base URL

| Environment | Base URL |
|-------------|----------|
| Local Development | `http://localhost:8000` |
| Vercel Frontend | `https://call-coach.vercel.app` |
| Custom Deployment | `https://your-domain.com` |

## Authentication

### Local Development
No authentication required.

### Production (Horizon)
Requests may require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-domain.com/coaching/analyze-call
```

## Endpoints

### POST /coaching/analyze-call

Analyze a single Gong call for coaching insights across all dimensions.

**URL**: `POST /coaching/analyze-call`

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <api_key> (optional in development)
```

**Request Body**:
```json
{
  "gong_call_id": "1464927526043145564",
  "focus_area": "discovery"
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `gong_call_id` | string | Yes | Unique ID from Gong API |
| `focus_area` | string | No | One of: "discovery", "product", "objections", "engagement" |

**Response** (200 OK):
```json
{
  "call_id": "1464927526043145564",
  "call_duration": 1800,
  "participants": [
    {
      "name": "Sarah Jones",
      "email": "sarah.jones@prefect.io",
      "role": "ae",
      "talk_time_seconds": 720
    },
    {
      "name": "John Smith",
      "email": "john@acme.com",
      "role": "prospect",
      "talk_time_seconds": 1080
    }
  ],
  "dimensions": {
    "discovery": {
      "score": 85,
      "max_score": 100,
      "findings": [
        "Effectively identified customer's pain points",
        "Asked about current solutions in place",
        "Could explore timeline and budget earlier"
      ],
      "recommendations": [
        "Ask qualifying questions about implementation timeline",
        "Clarify budget allocation process before deep product dive",
        "Follow up on their stated pain point about integration complexity"
      ],
      "evidence": [
        {
          "timestamp": 120,
          "quote": "What tools are you currently using for data orchestration?",
          "context": "Discovery phase question"
        }
      ]
    },
    "product_knowledge": {
      "score": 92,
      "max_score": 100,
      "findings": [
        "Comprehensive understanding of Horizon deployment options",
        "Clear explanation of managed agents vs self-hosted",
        "Strong product positioning vs competitors"
      ],
      "recommendations": [],
      "evidence": []
    },
    "objection_handling": {
      "score": 78,
      "max_score": 100,
      "findings": [
        "Handled pricing objection with value-based response",
        "Could have been more proactive with ROI calculation"
      ],
      "recommendations": [
        "Prepare ROI calculator examples before calls",
        "Address budget concerns earlier in conversation",
        "Practice handling technical objections"
      ],
      "evidence": [
        {
          "timestamp": 1320,
          "quote": "The total cost of ownership actually decreases by 40% in year 2",
          "context": "Response to pricing objection"
        }
      ]
    },
    "engagement": {
      "score": 88,
      "max_score": 100,
      "findings": [
        "Built strong rapport with customer",
        "Active listening with frequent confirmation",
        "Good use of customer's language and terminology"
      ],
      "recommendations": [],
      "evidence": []
    }
  },
  "overall_score": 86,
  "summary": "Strong overall performance with particular strength in product knowledge and customer engagement. Focus on discovery depth and proactive objection handling to further improve results.",
  "key_themes": ["discovery", "objection-handling", "product-fit"],
  "next_actions": [
    "Review discovery questioning framework",
    "Practice ROI-based pricing discussions"
  ],
  "call_metadata": {
    "title": "Acme Corp - Discovery Demo",
    "call_type": "discovery",
    "product": "horizon",
    "date": "2026-02-03T14:30:00Z"
  },
  "cached": false,
  "analysis_time_seconds": 34
}
```

**Error Responses**:

*400 Bad Request*:
```json
{
  "error": "Invalid parameter",
  "detail": "focus_area must be one of: discovery, product, objections, engagement"
}
```

*404 Not Found*:
```json
{
  "error": "Call not found",
  "detail": "Call ID 1464927526043145564 not found in database. Ensure the call has been processed by Gong first."
}
```

*500 Internal Server Error*:
```json
{
  "error": "Analysis failed",
  "detail": "Claude API returned an error. Please try again later.",
  "request_id": "req-abc123"
}
```

---

### POST /coaching/rep-insights

Get performance metrics and coaching insights for a specific rep over a time period.

**URL**: `POST /coaching/rep-insights`

**Request Body**:
```json
{
  "rep_email": "sarah.jones@prefect.io",
  "time_period": "month"
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `rep_email` | string | Yes | Email address of the sales rep |
| `time_period` | string | No | One of: "week", "month", "quarter". Default: "month" |

**Response** (200 OK):
```json
{
  "rep_email": "sarah.jones@prefect.io",
  "rep_name": "Sarah Jones",
  "period": {
    "type": "month",
    "start_date": "2026-01-05",
    "end_date": "2026-02-04"
  },
  "statistics": {
    "calls_analyzed": 12,
    "calls_closed_won": 3,
    "close_rate": 0.25,
    "average_call_duration": 1843,
    "average_deal_size": 125000
  },
  "dimension_scores": {
    "discovery": {
      "average": 82,
      "trend": "improving",
      "improvement_since_last_period": 5,
      "scores": [78, 80, 82, 84, 85, 83, 82, 81, 83, 84, 85, 86]
    },
    "product_knowledge": {
      "average": 88,
      "trend": "stable",
      "improvement_since_last_period": 1,
      "scores": [87, 88, 89, 88, 88, 89, 87, 88, 89, 88, 87, 89]
    },
    "objection_handling": {
      "average": 75,
      "trend": "declining",
      "improvement_since_last_period": -3,
      "scores": [78, 77, 76, 75, 74, 73, 74, 75, 76, 75, 74, 75]
    },
    "engagement": {
      "average": 85,
      "trend": "stable",
      "improvement_since_last_period": 2,
      "scores": [84, 84, 85, 85, 86, 85, 85, 86, 85, 86, 85, 86]
    }
  },
  "overall_average": 82.5,
  "performance_tier": "exceeds_expectations",
  "skill_gaps": [
    {
      "dimension": "objection_handling",
      "severity": "high",
      "description": "Objection handling score declining over past 2 weeks",
      "recommendations": [
        "Schedule objection handling role-play session",
        "Review recent calls with focus on pricing objections",
        "Practice technical objection responses"
      ]
    },
    {
      "dimension": "discovery",
      "severity": "medium",
      "description": "Could improve discovery depth and qualification",
      "recommendations": [
        "Review discovery question framework",
        "Focus on budget and timeline earlier in calls"
      ]
    }
  ],
  "coaching_plan": {
    "focus_areas": ["objection_handling", "discovery"],
    "priority_actions": [
      {
        "action": "Attend objection handling workshop",
        "date": "2026-02-12",
        "expected_improvement": "+8 points"
      },
      {
        "action": "Complete discovery questioning module",
        "estimated_time": "2 hours",
        "expected_improvement": "+5 points"
      }
    ],
    "review_date": "2026-03-04"
  },
  "top_calls": [
    {
      "call_id": "1464927526043145564",
      "title": "Acme Corp - Discovery Demo",
      "date": "2026-02-03T14:30:00Z",
      "score": 95,
      "dimensions": {
        "discovery": 92,
        "product_knowledge": 96,
        "objection_handling": 94,
        "engagement": 97
      },
      "outcome": "closed_won"
    },
    {
      "call_id": "1464927526043145565",
      "title": "TechStart Inc - Technical Deep Dive",
      "date": "2026-01-29T10:00:00Z",
      "score": 91,
      "dimensions": {
        "discovery": 88,
        "product_knowledge": 95,
        "objection_handling": 85,
        "engagement": 94
      },
      "outcome": "advanced"
    }
  ],
  "peer_comparison": {
    "percentile": 78,
    "average_team_score": 79,
    "comparison": "Above team average in product knowledge and engagement, below average in objection handling"
  },
  "cached": false,
  "analysis_time_seconds": 52
}
```

**Error Responses**:

*400 Bad Request*:
```json
{
  "error": "Invalid parameter",
  "detail": "time_period must be one of: week, month, quarter"
}
```

*404 Not Found*:
```json
{
  "error": "Rep not found",
  "detail": "No sales rep found with email sarah.jones@prefect.io. Check email spelling."
}
```

---

### POST /coaching/search

Search for calls matching specific criteria.

**URL**: `POST /coaching/search`

**Request Body**:
```json
{
  "query": "discovery pricing",
  "filters": {
    "call_type": "discovery",
    "product": "horizon",
    "min_score": 80,
    "date_from": "2026-01-01T00:00:00Z",
    "date_to": "2026-02-05T23:59:59Z",
    "rep_email": "sarah.jones@prefect.io"
  },
  "limit": 20
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Search keywords (title, participants, topics) |
| `filters` | object | No | Optional filtering criteria |
| `filters.call_type` | string | No | "discovery", "demo", "negotiation", "technical_deep_dive" |
| `filters.product` | string | No | "prefect", "horizon", "both" |
| `filters.min_score` | integer | No | Minimum coaching score (0-100) |
| `filters.date_from` | string | No | Start date in ISO 8601 format |
| `filters.date_to` | string | No | End date in ISO 8601 format |
| `filters.rep_email` | string | No | Filter by specific sales rep |
| `limit` | integer | No | Max results (1-100, default: 20) |

**Response** (200 OK):
```json
{
  "query": "discovery pricing",
  "filters": {
    "call_type": "discovery",
    "product": "horizon",
    "min_score": 80,
    "date_from": "2026-01-01",
    "date_to": "2026-02-05",
    "rep_email": "sarah.jones@prefect.io"
  },
  "total_results": 8,
  "results": [
    {
      "call_id": "1464927526043145564",
      "title": "Acme Corp - Discovery Demo",
      "date": "2026-02-03T14:30:00Z",
      "duration_seconds": 1800,
      "call_type": "discovery",
      "product": "horizon",
      "rep_name": "Sarah Jones",
      "rep_email": "sarah.jones@prefect.io",
      "customer_name": "Acme Corp",
      "customer_industry": "Technology",
      "score": 95,
      "dimensions": {
        "discovery": 92,
        "product_knowledge": 96,
        "objection_handling": 94,
        "engagement": 97
      },
      "key_topics": ["discovery", "pricing", "deployment", "integrations"],
      "summary": "Strong discovery call demonstrating excellent product knowledge and customer engagement. Customer interested in Horizon for workflow orchestration.",
      "outcome": "closed_won"
    },
    {
      "call_id": "1464927526043145565",
      "title": "TechStart Inc - Initial Discovery",
      "date": "2026-01-29T10:00:00Z",
      "duration_seconds": 1500,
      "call_type": "discovery",
      "product": "horizon",
      "rep_name": "Sarah Jones",
      "rep_email": "sarah.jones@prefect.io",
      "customer_name": "TechStart Inc",
      "customer_industry": "FinTech",
      "score": 88,
      "dimensions": {
        "discovery": 85,
        "product_knowledge": 92,
        "objection_handling": 82,
        "engagement": 91
      },
      "key_topics": ["discovery", "use-cases", "feature-request"],
      "summary": "Good discovery call identifying customer's need for data pipeline management.",
      "outcome": "advanced"
    }
  ],
  "facets": {
    "call_types": {
      "discovery": 8,
      "demo": 2,
      "negotiation": 1,
      "technical_deep_dive": 0
    },
    "products": {
      "horizon": 8,
      "prefect": 2
    },
    "outcomes": {
      "closed_won": 3,
      "advanced": 4,
      "stalled": 1
    },
    "score_distribution": {
      "80-85": 2,
      "85-90": 3,
      "90-95": 2,
      "95-100": 1
    }
  },
  "cached": false,
  "query_time_seconds": 2
}
```

**Error Responses**:

*400 Bad Request*:
```json
{
  "error": "Invalid filter",
  "detail": "call_type must be one of: discovery, demo, negotiation, technical_deep_dive"
}
```

*422 Unprocessable Entity*:
```json
{
  "error": "Invalid date format",
  "detail": "date_from must be in ISO 8601 format: 2026-02-05T00:00:00Z"
}
```

---

## Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Check request parameters and format |
| 401 | Unauthorized | Check API key or authentication |
| 404 | Not Found | Resource does not exist |
| 429 | Too Many Requests | Wait before retrying (rate limited) |
| 500 | Internal Error | Retry after 30 seconds, contact support if persistent |
| 503 | Service Unavailable | Service is temporarily down, retry later |

## Pagination

Results are limited by the `limit` parameter:

- Minimum: 1
- Maximum: 100
- Default: 20

For large result sets, paginate by sorting by date and using date filters:

```json
{
  "query": "discovery",
  "filters": {
    "date_from": "2026-01-01T00:00:00Z",
    "date_to": "2026-01-10T23:59:59Z"
  },
  "limit": 100
}
```

Then repeat with next date range:

```json
{
  "query": "discovery",
  "filters": {
    "date_from": "2026-01-11T00:00:00Z",
    "date_to": "2026-01-20T23:59:59Z"
  },
  "limit": 100
}
```

## Rate Limiting

**Local Development**: Unlimited

**Production**:
- 100 requests/minute per API key
- Returns `X-RateLimit-Remaining` header

Example rate limit header:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1670000000
```

If rate limited (429 response):
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "reset_time": "2026-02-05T15:35:00Z"
}
```

## Caching

All endpoints support intelligent caching:

- **Cache hits**: Response includes `"cached": true`
- **Cache misses**: Response includes `"cached": false`
- **TTL**: 30 days
- **Hit rate**: Typically 60-80%

Example cached response:
```json
{
  "call_id": "1464927526043145564",
  ...
  "cached": true,
  "cache_age_seconds": 3600,
  "analysis_time_seconds": 34
}
```

## Examples

### Example 1: Analyze a Discovery Call

```bash
curl -X POST http://localhost:8000/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d '{
    "gong_call_id": "1464927526043145564",
    "focus_area": "discovery"
  }'
```

Response will show discovery dimension is 85/100 with specific findings and recommendations.

### Example 2: Get Monthly Rep Performance

```bash
curl -X POST http://localhost:8000/coaching/rep-insights \
  -H "Content-Type: application/json" \
  -d '{
    "rep_email": "sarah.jones@prefect.io",
    "time_period": "month"
  }'
```

Response includes average scores, trends, skill gaps, and personalized coaching plan.

### Example 3: Find High-Scoring Discovery Calls

```bash
curl -X POST http://localhost:8000/coaching/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "discovery",
    "filters": {
      "call_type": "discovery",
      "min_score": 90,
      "product": "horizon"
    },
    "limit": 10
  }'
```

Response lists top discovery calls with scores 90+ for Horizon.

## OpenAPI Specification

Interactive API docs available when running locally:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Download OpenAPI spec:
- **JSON**: http://localhost:8000/openapi.json
- **YAML**: http://localhost:8000/openapi.yaml

## Next Steps

- [API Overview](./README.md) - Concepts and getting started
- [Error Codes](../troubleshooting/api-errors.md) - Troubleshooting
- [Local Development](../developers/setup.md) - Set up API locally
