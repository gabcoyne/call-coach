/**
 * Role Assignment Management Page
 *
 * Manager-only page for assigning coaching roles (AE, SE, CSM) to Prefect staff.
 * Displays all staff members with their current role assignments and allows bulk updates.
 *
 * Authorization: Requires manager role (Clerk publicMetadata.role === 'manager')
 */
import { Suspense } from "react";
import { currentUser } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { RoleAssignmentTable } from "@/components/RoleAssignmentTable";

export default async function RoleAssignmentPage() {
  const user = await currentUser();

  // Check authentication
  if (!user) {
    redirect("/sign-in");
  }

  // Check manager authorization
  const userRole = user.publicMetadata?.role;
  if (userRole !== "manager") {
    redirect("/403");
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Role Assignment</h1>
          <p className="mt-2 text-gray-600">
            Assign coaching roles to staff members to customize evaluation criteria.
            Each role has a specialized rubric focused on relevant skills.
          </p>
        </div>

        {/* Role Descriptions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
            <h3 className="font-semibold text-blue-900">Account Executive (AE)</h3>
            <p className="text-sm text-blue-700 mt-1">
              Discovery, objection handling, product positioning, relationship building
            </p>
          </div>
          <div className="border rounded-lg p-4 bg-green-50 border-green-200">
            <h3 className="font-semibold text-green-900">Sales Engineer (SE)</h3>
            <p className="text-sm text-green-700 mt-1">
              Technical accuracy, architecture fit, problem-solution mapping
            </p>
          </div>
          <div className="border rounded-lg p-4 bg-purple-50 border-purple-200">
            <h3 className="font-semibold text-purple-900">Customer Success Manager (CSM)</h3>
            <p className="text-sm text-purple-700 mt-1">
              Value realization, risk identification, relationship depth, expansion
            </p>
          </div>
        </div>

        {/* Role Assignment Table */}
        <Suspense
          fallback={
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center space-y-2">
                <div className="animate-spin h-8 w-8 border-4 border-prefect-blue-500 border-t-transparent rounded-full mx-auto" />
                <p className="text-sm text-muted-foreground">
                  Loading staff members...
                </p>
              </div>
            </div>
          }
        >
          <RoleAssignmentTable />
        </Suspense>
      </div>
    </div>
  );
}

export const metadata = {
  title: "Role Assignment - Call Coach",
  description: "Assign coaching roles to staff members for tailored evaluation",
};
