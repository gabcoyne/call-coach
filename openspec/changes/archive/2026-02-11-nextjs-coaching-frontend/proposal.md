# Proposal

## Why

Sales managers and coaches currently lack a modern, intuitive interface to interact with AI-powered coaching insights from the Gong Call Coaching Agent. While the MCP backend provides powerful analysis tools, accessing them requires Claude Desktop or API calls, limiting adoption and usability. A dedicated web frontend with Prefect branding will make coaching insights accessible to the entire sales team through an elegant, self-service interface deployed on Vercel.

## What Changes

- New Next.js 15 (App Router) web application with Prefect brand identity
- Modern UI for viewing call analyses, rep performance dashboards, and coaching insights
- Real-time search and filtering across analyzed calls
- Interactive data visualizations for performance trends and metrics
- Responsive design supporting desktop, tablet, and mobile devices
- Integration with MCP backend via REST API or direct MCP protocol bridge
- Vercel deployment pipeline with preview environments for PR-based workflows
- Authentication and role-based access control (managers vs. reps)

## Capabilities

### New Capabilities

- `ui-design-system`: Prefect-branded design system with colors, typography, components, and assets from prefect.io
- `call-analysis-viewer`: Display detailed call analysis with scores, strengths, areas for improvement, transcript snippets, and coaching recommendations
- `rep-performance-dashboard`: Interactive dashboard showing rep performance trends, skill gaps, improvement areas, and coaching history across time periods
- `call-search-and-filter`: Search and filter calls by rep, date range, product, call type, score thresholds, objection types, and topics
- `coaching-insights-feed`: Chronological feed of recent analyses, team-wide insights, and coaching highlights
- `mcp-backend-integration`: API client and data layer for communicating with FastMCP coaching tools (analyze_call, get_rep_insights, search_calls)
- `vercel-deployment`: Production deployment configuration, environment variables, preview environments, and CI/CD pipeline

### Modified Capabilities

<!-- No existing capabilities are being modified - this is a new frontend -->

## Impact

**New Codebase:**

- New `frontend/` directory with Next.js application
- Separate git repository or monorepo structure (to be decided in design phase)

**Backend Dependencies:**

- Requires MCP backend to expose REST API endpoints or WebSocket bridge for web clients
- May need to add CORS configuration to FastMCP server
- Authentication layer needed (JWT tokens, API keys, or session-based auth)

**Infrastructure:**

- Vercel project and deployment pipeline
- Environment variables for MCP backend URL, auth credentials, and feature flags
- Domain/subdomain configuration (e.g., coaching.prefect.io)

**User Impact:**

- Sales managers get self-service access to coaching insights
- Reps can view their own performance data and coaching recommendations
- Reduces dependency on Claude Desktop for accessing coaching features
- Enables mobile access to coaching data

**Security Considerations:**

- Authentication required to prevent unauthorized access to coaching data
- Role-based access control (managers see all reps, reps see only their own data)
- Secure communication with backend (HTTPS, API key validation)
- PII and sensitive call data protection
