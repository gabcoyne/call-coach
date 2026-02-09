/**
 * Example usage of auth-utils.ts for Role-Based Access Control
 *
 * This file demonstrates how to use the client-side auth utilities
 * in React components for role-based feature rendering.
 */

import { useUser } from "@clerk/nextjs";
import {
  isManager,
  isRep,
  canViewRepData,
  getUserRole,
  getUserEmail,
  hasManagerAccess,
  getRoleDisplayName,
  UserRole
} from "@/lib/auth-utils";

// Example 1: Conditional rendering based on manager role
export function ManagerOnlyFeature() {
  const { user } = useUser();

  // Only render for managers
  if (!isManager(user)) {
    return null;
  }

  return (
    <div>
      <h2>Manager Dashboard</h2>
      <p>This feature is only visible to managers</p>
    </div>
  );
}

// Example 2: Different UI for managers vs reps
export function DashboardHeader() {
  const { user } = useUser();
  const role = getUserRole(user);
  const displayName = getRoleDisplayName(user);

  return (
    <header>
      <h1>Dashboard - {displayName}</h1>
      {role === UserRole.MANAGER ? (
        <p>View all team members' performance</p>
      ) : (
        <p>View your personal performance</p>
      )}
    </header>
  );
}

// Example 3: Checking access to specific rep's data
export function RepDataViewer({ repEmail }: { repEmail: string }) {
  const { user } = useUser();
  const canView = canViewRepData(user, repEmail);

  if (!canView) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <h3 className="text-red-800">Access Denied</h3>
        <p>You don't have permission to view this rep's data</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Rep Performance: {repEmail}</h2>
      {/* Rep data here */}
    </div>
  );
}

// Example 4: Using hasManagerAccess for feature flags
export function NavigationMenu() {
  const { user } = useUser();

  return (
    <nav>
      <ul>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/calls">My Calls</a></li>

        {hasManagerAccess(user) && (
          <>
            <li><a href="/team">Team Overview</a></li>
            <li><a href="/analytics">Team Analytics</a></li>
            <li><a href="/admin">Admin Settings</a></li>
          </>
        )}
      </ul>
    </nav>
  );
}

// Example 5: Page-level authorization check
export function RepDashboardPage({ repEmail }: { repEmail: string }) {
  const { user, isLoaded } = useUser();
  const userEmail = getUserEmail(user);

  // Wait for user to load
  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  // Check if user can view this rep's data
  const canView = canViewRepData(user, repEmail);

  if (!canView) {
    // Redirect to 403 page or show error
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-4">
            You don't have permission to view this page.
          </p>
          {userEmail && (
            <a
              href={`/dashboard/${encodeURIComponent(userEmail)}`}
              className="text-blue-600 hover:underline"
            >
              Go to your dashboard
            </a>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1>Dashboard for {repEmail}</h1>
      {/* Dashboard content */}
    </div>
  );
}

// Example 6: Using role in data fetching hooks
export function RepInsightsComponent({ repEmail }: { repEmail: string }) {
  const { user } = useUser();
  const canView = canViewRepData(user, repEmail);

  // Fetch data for this rep
  // const { data } = useRepInsights(canView ? repEmail : null);
  // Note: Pass null to skip fetching if user can't view the data

  if (!canView) {
    return <div>You don't have access to this data</div>;
  }

  return (
    <div>
      {/* Display insights */}
    </div>
  );
}

// Example 7: Role-based button rendering
export function ActionButtons() {
  const { user } = useUser();

  return (
    <div className="flex gap-2">
      <button className="btn-primary">View My Calls</button>

      {isManager(user) ? (
        <>
          <button className="btn-secondary">Export Team Report</button>
          <button className="btn-secondary">Manage Team</button>
        </>
      ) : (
        <button className="btn-secondary">Request Coaching</button>
      )}
    </div>
  );
}

// Example 8: Server-side role check (use lib/auth.ts instead)
// Note: For server components and API routes, use the server-side utilities:
//
// import { getCurrentUserRole, canViewRepData, requireManager } from "@/lib/auth";
//
// export default async function ServerComponent() {
//   const role = await getCurrentUserRole();
//   // ... use role
// }
