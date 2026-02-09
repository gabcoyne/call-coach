# Role-Based Access Control (RBAC) Implementation

## Overview

This document describes the Role-Based Access Control implementation for the Gong Call Coaching application. The system uses Clerk authentication with custom roles stored in user metadata.

## Architecture

### Two-Tier RBAC System

1. **Client-Side** (`lib/auth-utils.ts`): For UI rendering and component visibility
2. **Server-Side** (`lib/auth.ts`): For data access authorization and API protection

This dual-layer approach ensures both a good user experience (no flashing of unauthorized content) and strong security (server-side enforcement).

## Roles

### Manager (`manager`)
- Full access to all features
- Can view all sales reps' data and dashboards
- Has access to team-wide analytics and insights
- Can search and filter across all calls
- Sees manager-only UI components

### Sales Rep (`rep`)
- Limited access to own data only
- Cannot access other reps' information
- Search results filtered to own calls
- Manager-only features are hidden from UI

**Default Role:** If no role is set in `publicMetadata`, users default to `rep`.

## Files Created

### Core Implementation Files

1. **`/lib/auth-utils.ts`** (Client-side utilities)
   - `isManager(user)`: Check if user is a manager
   - `isRep(user)`: Check if user is a rep
   - `getUserRole(user)`: Get the user's role enum
   - `getUserEmail(user)`: Get the user's email address
   - `canViewRepData(user, repEmail)`: Check if user can view specific rep's data
   - `hasManagerAccess(user)`: Check for manager-only features
   - `getRoleDisplayName(user)`: Get user-friendly role name

2. **`/lib/auth.ts`** (Server-side utilities)
   - `getCurrentUserRole()`: Get role from Clerk session (async)
   - `isManager()`: Server-side manager check (async)
   - `isRep()`: Server-side rep check (async)
   - `getCurrentUserEmail()`: Get email from session (async)
   - `canViewRepData(repEmail)`: Server-side authorization (async)
   - `requireManager()`: Throws error if not manager (async)
   - `getUserSession()`: Complete session info (async)

3. **`/app/403.tsx`** (Forbidden error page)
   - Custom error page for unauthorized access attempts
   - User-friendly messaging
   - Navigation options to return to authorized pages

### Documentation Files

4. **`CLERK_SETUP.md`** (Updated with RBAC documentation)
   - Role assignment process
   - Manager role assignment authority
   - Bulk role assignment strategies
   - Role verification procedures

5. **`/lib/auth-utils.example.tsx`** (Usage examples)
   - Comprehensive examples for all auth utility functions
   - Common patterns for component-level access control
   - Best practices for client-side authorization

6. **`RBAC_TESTING.md`** (Testing guide)
   - Complete testing procedures
   - Test scenarios for both roles
   - Security checklist
   - Troubleshooting guide

## Usage Patterns

### Client-Side Components

```typescript
import { useUser } from "@clerk/nextjs";
import { isManager, canViewRepData } from "@/lib/auth-utils";

export function MyComponent() {
  const { user } = useUser();

  // Conditional rendering based on role
  if (!isManager(user)) {
    return null; // Hide from non-managers
  }

  return <ManagerOnlyFeature />;
}
```

### Server-Side Pages (App Router)

```typescript
import { getCurrentUserRole, canViewRepData } from "@/lib/auth";

export default async function RepDashboard({ params }: { params: { repEmail: string } }) {
  // Server-side authorization
  const hasAccess = await canViewRepData(params.repEmail);

  if (!hasAccess) {
    redirect('/403');
  }

  // Fetch and display data
  return <Dashboard repEmail={params.repEmail} />;
}
```

### API Routes

```typescript
import { requireManager } from "@/lib/auth";

export async function GET() {
  try {
    // Enforce manager-only access
    await requireManager();

    // Process manager-only request
    return Response.json({ data: teamData });
  } catch (error) {
    return Response.json({ error: 'Unauthorized' }, { status: 403 });
  }
}
```

## Integration with Existing Components

### Already Implemented

The following pages/components already use role-based access control:

1. **`/app/dashboard/[repEmail]/page.tsx`**
   - Checks `user?.publicMetadata?.role === 'manager'`
   - Redirects unauthorized users to their own dashboard
   - Shows manager-only features (Rep Selector)

2. **`/lib/hooks/use-rep-insights.ts`**
   - Backend enforces role-based access via Clerk token
   - Reps can only fetch their own data

3. **`/app/search/page.tsx`**
   - Rep filter is conditionally rendered for managers
   - Search results filtered by role on backend

### Migration to New Utilities

Other developers can migrate existing code to use the new utilities:

**Before:**
```typescript
const isManager = user?.publicMetadata?.role === 'manager';
```

**After:**
```typescript
import { isManager } from '@/lib/auth-utils';
const managerAccess = isManager(user);
```

## Security Considerations

### Defense in Depth

1. **Client-Side**: Hide UI elements from unauthorized users (better UX)
2. **Server-Side**: Enforce authorization on all data access (security)
3. **API Layer**: Backend validates Clerk tokens and roles
4. **Database**: No direct database access from frontend

### Best Practices

1. **Never trust client-side checks alone**: Always validate on server
2. **Use server-side utilities for data access**: Use `lib/auth.ts` in server components and API routes
3. **Use client-side utilities for UI**: Use `lib/auth-utils.ts` in client components
4. **Validate on every request**: Don't cache authorization decisions
5. **Fail securely**: Default to denying access when in doubt

### Role Assignment Security

- Only authorized personnel can assign manager role
- Role changes are audited in Slack
- Approval process required for manager role
- See `CLERK_SETUP.md` for full role assignment process

## Testing

Comprehensive testing procedures are documented in `RBAC_TESTING.md`. Key test areas:

1. Manager can access all reps' data
2. Reps can only access their own data
3. 403 page displays for unauthorized access
4. Manager-only features are hidden from reps
5. Backend API enforces authorization
6. Role changes take effect after re-authentication

## Future Enhancements

### Potential Improvements

1. **Organization-based roles**: Use Clerk Organizations for team management
2. **Webhook automation**: Auto-assign roles based on email domain
3. **Role hierarchy**: Add "Team Lead" role with subset of manager permissions
4. **Audit logging**: Track all role assignments and changes
5. **Permission granularity**: Fine-grained permissions beyond just manager/rep

### Scalability Considerations

For large deployments (>100 users):
- Implement bulk role import/export via Clerk Management API
- Add caching layer for role lookups (with short TTL)
- Consider external RBAC system integration (e.g., WorkOS)
- Implement role-based rate limiting

## Troubleshooting

### Common Issues

**Issue**: Role not taking effect
- **Solution**: Sign out and back in (Clerk caches metadata)

**Issue**: 403 page not displaying
- **Solution**: Check redirect logic and route protection

**Issue**: Manager sees rep view
- **Solution**: Verify role is exactly "manager" (lowercase) in Clerk Dashboard

**Issue**: TypeScript errors with user object
- **Solution**: Import `UserResource` type from `@clerk/types`

See `RBAC_TESTING.md` for complete troubleshooting guide.

## Support and Maintenance

### Contacts

- **Technical Owner**: Engineering team leads
- **Role Administration**: Sales Operations Manager
- **Security Questions**: Security team

### Documentation Updates

When making changes to RBAC:
1. Update this document
2. Update `CLERK_SETUP.md` with role assignment changes
3. Update `RBAC_TESTING.md` with new test scenarios
4. Update code examples in `auth-utils.example.tsx`

---

**Last Updated**: 2026-02-05
**Version**: 1.0
**Status**: Implemented and Ready for Testing
