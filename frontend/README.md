# Gong Call Coaching - Frontend

A Next.js 15 application providing AI-powered sales coaching insights with Clerk authentication and MCP backend integration.

## Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Support](#support)

## Quick Start

### Prerequisites

- Node.js 20.x LTS or higher
- npm or yarn
- A Clerk account for authentication
- Access to the MCP backend server

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables template
cp .env.example .env.local

# Configure your environment variables (see docs/ENVIRONMENT_VARIABLES.md)
# At minimum, add your Clerk API keys:
# - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# - CLERK_SECRET_KEY
```

### Running Locally

```bash
# Start the development server
npm run dev

# The app will be available at http://localhost:3000
```

### First-Time Setup

1. Follow the Clerk setup guide: [CLERK_SETUP.md](./CLERK_SETUP.md)
2. Configure environment variables: [docs/ENVIRONMENT_VARIABLES.md](./docs/ENVIRONMENT_VARIABLES.md)
3. Ensure the MCP backend is running (see root project README)
4. Create test users in Clerk dashboard with appropriate roles
5. Test authentication flows

## Project Overview

This frontend application provides a modern UI for sales coaching powered by AI analysis of Gong sales calls. Key features include:

- **Call Analysis Viewer**: Deep-dive analysis of individual calls with coaching insights across multiple dimensions
- **Rep Performance Dashboard**: Performance trends, skill gaps, and personalized coaching plans
- **Call Search & Filter**: Advanced search with multiple criteria and saved searches
- **Coaching Insights Feed**: Chronological activity feed with team insights and highlights
- **Role-Based Access Control**: Managers can view all data, reps see only their own

### User Roles

- **Manager**: Full access to all reps' data, team insights, and performance comparisons
- **Rep**: Access restricted to their own call analyses and performance data

## Architecture

### Tech Stack

- **Framework**: Next.js 15 with App Router
- **UI Components**: Shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS with custom Prefect brand theme
- **Authentication**: Clerk (user management and RBAC)
- **Data Fetching**: SWR for client-side data fetching with caching
- **Charts**: Recharts for data visualization
- **Validation**: Zod for runtime type validation
- **Backend**: FastMCP Python server (MCP protocol)

### Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with navigation
│   ├── page.tsx                 # Landing page
│   ├── api/                     # API routes (backend bridge)
│   │   └── coaching/
│   │       ├── analyze-call/    # Call analysis endpoint
│   │       ├── rep-insights/    # Rep performance endpoint
│   │       └── search-calls/    # Search endpoint
│   ├── calls/[callId]/          # Call analysis viewer
│   ├── dashboard/[repEmail]/    # Rep performance dashboard
│   ├── search/                  # Call search page
│   ├── feed/                    # Coaching insights feed
│   ├── profile/                 # User profile page
│   ├── sign-in/                 # Clerk sign-in
│   └── sign-up/                 # Clerk sign-up
├── components/                   # Reusable UI components
│   └── ui/                      # Shadcn/ui components
├── lib/                          # Shared utilities
│   ├── mcp-client.ts            # MCP backend HTTP client
│   ├── auth.ts                  # RBAC utilities
│   ├── auth-middleware.ts       # API route auth middleware
│   ├── rate-limit.ts            # Rate limiting
│   ├── api-logger.ts            # API logging
│   ├── hooks/                   # Custom React hooks
│   └── utils.ts                 # Utility functions
├── types/                        # TypeScript types and Zod schemas
│   └── coaching.ts              # Coaching API types
├── public/                       # Static assets
│   └── logos/                   # Brand assets
├── docs/                         # Documentation
├── middleware.ts                 # Route protection middleware
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
└── package.json                 # Dependencies
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Environment Variables](./docs/ENVIRONMENT_VARIABLES.md)**: Configuration reference for all environment variables
- **[API Documentation](./docs/API_DOCUMENTATION.md)**: Complete API reference for `/api/coaching/*` endpoints
- **[User Guide](./docs/USER_GUIDE.md)**: Role-specific guides for managers and sales reps
- **[Deployment Guide](./docs/DEPLOYMENT.md)**: Vercel deployment and rollback procedures
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Runbook](./docs/RUNBOOK.md)**: Monitoring and incident response procedures

### Additional Guides

- **[Clerk Setup](./CLERK_SETUP.md)**: Authentication setup and configuration
- **[API Testing](./API_TESTING.md)**: Testing API endpoints locally
- **[Design System](./DESIGN_SYSTEM.md)**: Component library and theming guide

## Development

### Commands

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Run production build locally
npm start

# Lint code
npm run lint

# Type checking
npx tsc --noEmit
```

### Development Workflow

1. **Branch from develop**: All feature branches start from `develop`, not `main`
2. **Make your changes**: Follow TypeScript strict mode and ESLint rules
3. **Test locally**: Verify changes work with local MCP backend
4. **Commit with clear messages**: Use conventional commit format
5. **Create PR to develop**: PRs should target `develop` branch

### Adding New Features

1. Define TypeScript types in `types/coaching.ts`
2. Add Zod validation schemas for request/response
3. Create API route in `app/api/coaching/` if needed
4. Implement UI components in `app/` or `components/`
5. Add SWR hooks in `lib/hooks/` for data fetching
6. Update documentation

### Code Style

- Use TypeScript strict mode
- Follow ESLint and Prettier configurations
- Use functional components with hooks
- Prefer server components over client components
- Use async/await over promises
- Add JSDoc comments for complex functions

## Testing

### Manual Testing

See [CLERK_SETUP.md](./CLERK_SETUP.md#testing-authentication-flow) for authentication testing steps.

### Automated Testing (Future)

Automated testing will be added in Phase 12:

- Unit tests with Jest and React Testing Library
- Integration tests for API routes
- E2E tests with Playwright
- Accessibility testing with axe-core

## Deployment

The application is configured for deployment on Vercel. See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed instructions.

### Quick Deploy to Vercel

1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend/`
3. Configure environment variables in Vercel dashboard
4. Deploy!

### Preview Deployments

Every pull request automatically gets a preview deployment with a unique URL. The preview URL is posted as a comment on the PR.

### Production Deployment

Merging to `main` branch automatically deploys to production. Vercel provides instant rollback capability through the dashboard.

## Support

### Getting Help

- **Authentication Issues**: See [CLERK_SETUP.md](./CLERK_SETUP.md)
- **API Errors**: See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
- **Build Failures**: Check [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)
- **Incident Response**: Follow [docs/RUNBOOK.md](./docs/RUNBOOK.md)

### Useful Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Clerk Documentation](https://clerk.com/docs)
- [Shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [SWR Documentation](https://swr.vercel.app)
- [Zod Documentation](https://zod.dev)

### Project Links

- [OpenSpec Tasks](../openspec/changes/nextjs-coaching-frontend/tasks.md) - Project roadmap
- [Root Project README](../README.md) - Overall project documentation

## Contributing

This is an internal Prefect project. For questions or issues, please contact the engineering team.

## License

Proprietary - Prefect Technologies, Inc.
