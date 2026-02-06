/**
 * API route for managing staff role assignments.
 *
 * GET /api/settings/roles - List all Prefect staff with their assigned roles
 *
 * Authorization: Requires manager role (Clerk publicMetadata.role === 'manager')
 */
import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";
import * as db from "@/lib/db";

/**
 * GET handler - List all Prefect staff with their role assignments
 *
 * Returns a merged list of:
 * - All Prefect staff from speakers table (unique @prefect.io emails)
 * - Their role assignments from staff_roles table (if any)
 *
 * Authorization: Manager only
 */
export async function GET(request: NextRequest) {
  try {
    // Check authentication
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized - please sign in" }, { status: 401 });
    }

    // Check manager authorization
    const user = await currentUser();
    const userRole = user?.publicMetadata?.role;

    if (userRole !== "manager") {
      return NextResponse.json({ error: "Forbidden - manager access required" }, { status: 403 });
    }

    // Get all Prefect staff emails from speakers table
    const prefectStaff = await db.get_prefect_staff();

    // Get all role assignments
    const roleAssignments = await db.list_all_staff_roles();

    // Create a map of email -> role assignment
    const roleMap = new Map(roleAssignments.map((r: any) => [r.email, r]));

    // Merge staff with their role assignments
    const staffWithRoles = prefectStaff.map((staff: any) => {
      const roleAssignment = roleMap.get(staff.email);

      return {
        email: staff.email,
        name: staff.name || staff.email.split("@")[0], // Fallback to email prefix if no name
        role: roleAssignment?.role || null,
        assigned_by: roleAssignment?.assigned_by || null,
        assigned_at: roleAssignment?.assigned_at || null,
        updated_at: roleAssignment?.updated_at || null,
      };
    });

    // Sort by name
    staffWithRoles.sort((a: any, b: any) => {
      const nameA = a.name.toLowerCase();
      const nameB = b.name.toLowerCase();
      return nameA < nameB ? -1 : nameA > nameB ? 1 : 0;
    });

    return NextResponse.json({
      staff: staffWithRoles,
      total: staffWithRoles.length,
      with_roles: roleAssignments.length,
    });
  } catch (error: any) {
    console.error("Failed to list staff roles:", error);
    return NextResponse.json(
      { error: "Failed to retrieve staff roles", details: error.message },
      { status: 500 }
    );
  }
}
