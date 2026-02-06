# Call Coach Documentation

Complete documentation for the Gong Call Coaching Agent - an AI-powered sales coaching system for Prefect teams.

## Getting Started

New to call-coach? Start here:

1. **[Quick Start Guide](../README.md)** - Get up and running in 5 minutes
2. **[User Guide - Getting Started](./user-guide/README.md)** - Overview of key features
3. **[Local Development Setup](./developers/setup.md)** - Set up your development environment

## Documentation Structure

### User Guides

- [Getting Started](./user-guide/README.md) - Introduction to call-coach
- [Using Coaching Insights](./user-guide/coaching.md) - How to interpret and apply coaching recommendations
- [Role Management](./user-guide/role-management.md) - Understanding roles and permissions
- [Weekly Reports](./user-guide/weekly-reports.md) - Interpreting automated weekly summaries

### API Documentation

- [API Overview](./api/README.md) - Architecture and authentication
- [REST Endpoints](./api/endpoints.md) - Complete endpoint reference with examples
- [OpenAPI Specification](./api/openapi.yaml) - Machine-readable API spec

### Developer Guides

- [Local Development](./developers/setup.md) - Environment setup and local testing
- [System Architecture](./developers/architecture.md) - Technical design and components
- [Adding Features](./developers/adding-features.md) - Development workflow and patterns
- [Testing Guide](./developers/testing.md) - How to run and write tests

### Troubleshooting

- [Common Issues](./troubleshooting/README.md) - Quick answers to frequent problems
- [API Error Codes](./troubleshooting/api-errors.md) - Error code reference and solutions
- [Deployment Issues](./troubleshooting/deployment.md) - Troubleshooting production problems
- [Performance Tuning](./troubleshooting/performance.md) - Optimization and monitoring

### Deployment

- [Vercel Deployment](./deployment/vercel.md) - Frontend deployment guide
- [Environment Variables](./deployment/environment.md) - Configuration reference
- [Database Setup](./deployment/database.md) - Neon PostgreSQL configuration
- [Monitoring & Logging](./deployment/monitoring.md) - Production observability

## Key Features

**On-Demand Coaching Tools** - Use MCP protocol to access coaching analysis via Claude Desktop or REST API

**Intelligent Caching** - 60-80% cost reduction through transcript hashing and rubric versioning

**Parallel Analysis** - Concurrent processing across 4 coaching dimensions for 4x speed

**Long Call Support** - Handles 60+ minute calls with sliding window transcript chunking

**Real-Time Ingestion** - Gong webhook integration with <500ms response time and idempotency

**Weekly Reviews** - Automated batch processing and report generation via Prefect flows

## Technology Stack

| Component     | Technology           | Version    |
| ------------- | -------------------- | ---------- |
| Backend       | Python               | 3.11+      |
| API Server    | FastAPI              | 0.115+     |
| MCP Server    | FastMCP              | 2.0+       |
| Orchestration | Prefect              | 3.0+       |
| AI Analysis   | Claude API           | Sonnet 4.5 |
| Database      | PostgreSQL (Neon)    | 15+        |
| Frontend      | Next.js              | 15+        |
| UI Framework  | React with Shadcn/ui | Latest     |

## Project Structure Overview

```
call-coach/
├── docs/                  # This documentation
├── coaching_mcp/          # FastMCP server with MCP tools
├── api/                   # REST API bridge
├── analysis/              # Claude-powered coaching analysis
├── flows/                 # Prefect orchestration flows
├── db/                    # Database schema and models
├── gong/                  # Gong API integration
├── frontend/              # Next.js React application
├── tests/                 # Test suite
└── README.md              # Project overview
```

## Common Tasks

### For Users

- [Analyze a sales call](./user-guide/coaching.md#analyzing-calls)
- [View performance insights](./user-guide/README.md#dashboard)
- [Search for specific calls](./user-guide/README.md#call-search)
- [Understand weekly reports](./user-guide/weekly-reports.md)

### For Developers

- [Set up local environment](./developers/setup.md)
- [Run tests locally](./developers/testing.md)
- [Add a new coaching dimension](./developers/adding-features.md#adding-dimensions)
- [Debug API issues](./troubleshooting/api-errors.md)
- [Deploy to production](./deployment/vercel.md)

### For Operators

- [Monitor production system](./deployment/monitoring.md)
- [Manage environment variables](./deployment/environment.md)
- [Scale the database](./deployment/database.md)
- [Troubleshoot deployment](./troubleshooting/deployment.md)

## Support

For questions or issues:

1. Check the [Troubleshooting Guide](./troubleshooting/README.md)
2. Review [API error codes](./troubleshooting/api-errors.md)
3. See [Common deployment issues](./troubleshooting/deployment.md)
4. Contact the team for urgent production issues

## Latest Updates

- **2026-02-05**: Added comprehensive documentation suite
- **2026-02-04**: Local development guide published
- **2026-01-15**: Neon pooler compatibility fixes
- **2026-01-10**: FastMCP 2.0 integration complete

---

**Ready to get started?** Begin with the [Quick Start Guide](../README.md) or jump to [Local Development Setup](./developers/setup.md).
