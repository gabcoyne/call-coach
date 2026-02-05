# Gong Call Coaching - Frontend

Next.js 15 frontend application for AI-powered sales coaching with Clerk authentication.

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- A Clerk account (see [CLERK_SETUP.md](./CLERK_SETUP.md) for setup instructions)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables template
cp .env.example .env.local

# Add your Clerk API keys to .env.local
# Get keys from: https://dashboard.clerk.com
```

### Development

```bash
# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
# Build for production
npm run build

# Run production build
npm start
```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with Clerk provider
│   ├── page.tsx             # Home page
│   ├── sign-in/             # Sign-in route
│   │   └── [[...sign-in]]/
│   │       └── page.tsx
│   └── sign-up/             # Sign-up route
│       └── [[...sign-up]]/
│           └── page.tsx
├── lib/                      # Shared utilities
│   └── auth.ts              # RBAC utilities and role management
├── middleware.ts             # Route protection middleware
├── .env.example             # Environment variables template
└── CLERK_SETUP.md           # Clerk authentication setup guide
```

## Authentication

This application uses [Clerk](https://clerk.com) for authentication and user management.

### User Roles

- **Manager**: Can view all reps' data and team insights
- **Rep**: Can only view their own data

Roles are stored in Clerk's `publicMetadata.role` field.

### Protected Routes

All routes except `/sign-in` and `/sign-up` require authentication. The middleware in `middleware.ts` handles route protection automatically.

### RBAC Utilities

The `lib/auth.ts` module provides utilities for role-based access control:

```typescript
import { getCurrentUserRole, isManager, canViewRepData } from "@/lib/auth";

// Get current user's role
const role = await getCurrentUserRole();

// Check if user is a manager
const hasManagerAccess = await isManager();

// Check if user can view specific rep's data
const canView = await canViewRepData("rep@example.com");
```

## Environment Variables

See [.env.example](./.env.example) for required environment variables.

### Clerk Configuration

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
- `CLERK_SECRET_KEY`: Your Clerk secret key
- `NEXT_PUBLIC_CLERK_SIGN_IN_URL`: Sign-in page URL (default: `/sign-in`)
- `NEXT_PUBLIC_CLERK_SIGN_UP_URL`: Sign-up page URL (default: `/sign-up`)
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL`: Redirect after sign-in (default: `/dashboard`)
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL`: Redirect after sign-up (default: `/dashboard`)

### Backend Configuration

- `NEXT_PUBLIC_MCP_BACKEND_URL`: MCP backend API URL (for future API integration)

## Testing

Manual testing steps are documented in [CLERK_SETUP.md](./CLERK_SETUP.md#task-39-testing-authentication-flow).

Automated testing will be added in Phase 12 (Testing and Quality Assurance).

## Development Workflow

1. Create a feature branch from `develop`
2. Make your changes
3. Test locally
4. Commit with clear messages
5. Create a PR to `develop` (not `main`)

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Clerk Documentation](https://clerk.com/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [TypeScript](https://www.typescriptlang.org/)

## Support

For questions or issues, refer to:
- [CLERK_SETUP.md](./CLERK_SETUP.md) for authentication troubleshooting
- [OpenSpec tasks](../openspec/changes/nextjs-coaching-frontend/tasks.md) for project roadmap
