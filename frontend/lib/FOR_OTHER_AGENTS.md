# For Other Agents: Using RBAC Utilities

## Quick Start

If you're implementing pages or components that need role-based access control, use these utilities:

### Client Components (use `auth-utils.ts`)

```typescript
"use client";

import { useUser } from "@clerk/nextjs";
import { isManager, canViewRepData } from "@/lib/auth-utils";

export function MyClientComponent({ repEmail }: { repEmail: string }) {
  const { user } = useUser();

  // Check if current user can view this rep's data
  if (!canViewRepData(user, repEmail)) {
    return <div>Access Denied</div>;
  }

  return <div>Your component here</div>;
}
```

### Server Components (use `auth.ts`)

```typescript
import { canViewRepData } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function MyServerComponent({ params }: { params: { repEmail: string } }) {
  // Server-side authorization check
  const hasAccess = await canViewRepData(params.repEmail);

  if (!hasAccess) {
    redirect('/403');
  }

  return <div>Your component here</div>;
}
```

## Common Patterns

### Pattern 1: Manager-Only Feature

```typescript
import { useUser } from "@clerk/nextjs";
import { isManager } from "@/lib/auth-utils";

export function FeatureWithManagerOnly() {
  const { user } = useUser();

  return (
    <div>
      {/* Everyone sees this */}
      <CommonFeature />

      {/* Only managers see this */}
      {isManager(user) && (
        <ManagerOnlySection />
      )}
    </div>
  );
}
```

### Pattern 2: Different UI for Manager vs Rep

```typescript
import { useUser } from "@clerk/nextjs";
import { isManager } from "@/lib/auth-utils";

export function Dashboard() {
  const { user } = useUser();

  return isManager(user) ? (
    <ManagerDashboard />
  ) : (
    <RepDashboard />
  );
}
```

### Pattern 3: Page-Level Authorization

```typescript
import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { canViewRepData, getUserEmail } from "@/lib/auth-utils";

export default function RepPage({ repEmail }: { repEmail: string }) {
  const { user, isLoaded } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && !canViewRepData(user, repEmail)) {
      // Redirect unauthorized users to their own page
      const userEmail = getUserEmail(user);
      if (userEmail) {
        router.push(`/dashboard/${encodeURIComponent(userEmail)}`);
      }
    }
  }, [isLoaded, user, repEmail, router]);

  if (!isLoaded || !canViewRepData(user, repEmail)) {
    return null; // Will redirect
  }

  return <div>Your page content</div>;
}
```

### Pattern 4: Conditional Data Fetching

```typescript
import { useUser } from "@clerk/nextjs";
import { canViewRepData } from "@/lib/auth-utils";
import { useRepInsights } from "@/lib/hooks";

export function RepInsights({ repEmail }: { repEmail: string }) {
  const { user } = useUser();
  const canView = canViewRepData(user, repEmail);

  // Only fetch if user has access (pass null to skip)
  const { data, error } = useRepInsights(canView ? repEmail : null);

  if (!canView) {
    return <div>You don't have access to this data</div>;
  }

  if (error) return <div>Error loading data</div>;
  if (!data) return <div>Loading...</div>;

  return <div>{/* Display data */}</div>;
}
```

## Available Functions

### Client-Side (`lib/auth-utils.ts`)

Import from `@/lib/auth-utils`:

- **`isManager(user)`**: Returns `true` if user is a manager
- **`isRep(user)`**: Returns `true` if user is a rep
- **`canViewRepData(user, repEmail)`**: Returns `true` if user can view the rep's data
- **`getUserRole(user)`**: Returns `UserRole.MANAGER` or `UserRole.REP`
- **`getUserEmail(user)`**: Returns user's email address or `null`
- **`hasManagerAccess(user)`**: Same as `isManager()` (alias)
- **`getRoleDisplayName(user)`**: Returns "Manager" or "Sales Rep"

### Server-Side (`lib/auth.ts`)

Import from `@/lib/auth`:

- **`getCurrentUserRole()`**: Returns current user's role (async)
- **`isManager()`**: Returns `true` if current user is manager (async)
- **`isRep()`**: Returns `true` if current user is rep (async)
- **`getCurrentUserEmail()`**: Returns current user's email (async)
- **`canViewRepData(repEmail)`**: Returns `true` if current user can view the rep (async)
- **`requireManager()`**: Throws error if current user is not a manager (async)
- **`getUserSession()`**: Returns complete session info (async)

## When to Use Which

| Scenario | Use |
|----------|-----|
| Hiding UI elements | `auth-utils.ts` (client) |
| "use client" components | `auth-utils.ts` (client) |
| Server components | `auth.ts` (server) |
| API routes | `auth.ts` (server) |
| Page-level authorization | Both (client for UI, server for data) |
| Data fetching hooks | `auth-utils.ts` (client) to pass correct params |

## Examples for Specific Tasks

### Task: Hide "View All Reps" Button from Reps

```typescript
import { useUser } from "@clerk/nextjs";
import { isManager } from "@/lib/auth-utils";

export function Navigation() {
  const { user } = useUser();

  return (
    <nav>
      <a href="/dashboard">My Dashboard</a>
      {isManager(user) && (
        <a href="/team">View All Reps</a>
      )}
    </nav>
  );
}
```

### Task: Show Rep Selector Only to Managers

```typescript
import { useUser } from "@clerk/nextjs";
import { isManager } from "@/lib/auth-utils";

export function DashboardFilters() {
  const { user } = useUser();

  return (
    <div>
      {/* Time period filter - everyone sees this */}
      <TimePeriodFilter />

      {/* Rep selector - managers only */}
      {isManager(user) && (
        <RepSelector />
      )}
    </div>
  );
}
```

### Task: Restrict Search Results by Role

```typescript
import { useUser } from "@clerk/nextjs";
import { isManager, getUserEmail } from "@/lib/auth-utils";
import { useSearchCalls } from "@/lib/hooks";

export function SearchPage() {
  const { user } = useUser();
  const [filters, setFilters] = useState({});

  // For reps, automatically filter to own email
  const effectiveFilters = {
    ...filters,
    rep_email: isManager(user) ? filters.rep_email : getUserEmail(user)
  };

  const { data } = useSearchCalls(effectiveFilters);

  return (
    <div>
      {/* Rep filter only for managers */}
      {isManager(user) && (
        <RepFilter value={filters.rep_email} onChange={(email) => setFilters({ ...filters, rep_email: email })} />
      )}

      <SearchResults results={data} />
    </div>
  );
}
```

## Error Handling

### Show 403 Page for Unauthorized Access

```typescript
import { redirect } from "next/navigation";
import { canViewRepData } from "@/lib/auth";

export default async function RepDashboard({ params }: { params: { repEmail: string } }) {
  if (!await canViewRepData(params.repEmail)) {
    redirect('/403');
  }

  return <div>Dashboard content</div>;
}
```

### Custom Unauthorized Message

```typescript
import { useUser } from "@clerk/nextjs";
import { canViewRepData } from "@/lib/auth-utils";

export function RepData({ repEmail }: { repEmail: string }) {
  const { user } = useUser();

  if (!canViewRepData(user, repEmail)) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <h3>Access Denied</h3>
        <p>You don't have permission to view this rep's data.</p>
      </div>
    );
  }

  return <div>Rep data here</div>;
}
```

## Testing Your Implementation

1. Test as manager: Should see all features and data
2. Test as rep: Should only see own data, manager features hidden
3. Try accessing another rep's URL: Should redirect or show 403
4. Check that no console errors appear
5. Verify data fetching respects role (check Network tab)

## Questions?

- See `RBAC_IMPLEMENTATION.md` for full architecture
- See `auth-utils.example.tsx` for more examples
- See `RBAC_TESTING.md` for testing procedures
- See `CLERK_SETUP.md` for role assignment

## Common Mistakes to Avoid

1. **Don't use client utilities on server**: `auth-utils.ts` is for client components only
2. **Don't use server utilities on client**: `auth.ts` is async and requires server context
3. **Don't trust client checks alone**: Always validate on server for security
4. **Don't forget to check `isLoaded`**: Wait for Clerk to load user data
5. **Don't hardcode roles**: Use the utility functions, not `user.publicMetadata.role === 'manager'`

## Implementation Checklist

When implementing a new feature with RBAC:

- [ ] Import correct utilities (client vs server)
- [ ] Check role before rendering manager-only UI
- [ ] Check role before fetching sensitive data
- [ ] Handle unauthorized access (403 or redirect)
- [ ] Test as both manager and rep
- [ ] Verify backend also enforces authorization
- [ ] Add loading state while checking auth
- [ ] Handle case where user is not loaded yet

---

**Happy coding!** If you need help, check the example files or ask for clarification.
