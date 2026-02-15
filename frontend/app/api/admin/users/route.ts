/**
 * API route for listing users with their activity metrics.
 *
 * GET /api/admin/users - List all users with roles and activity metrics
 *
 * Authorization: Requires manager role (Clerk publicMetadata.role === 'manager')
 */
import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";
import * as db from "@/lib/db";

// Check if auth bypass is enabled (for development)
const bypassAuth = process.env.BYPASS_AUTH === "true";

export async function GET(request: NextRequest) {
  try {
    // In bypass mode, skip auth checks
    if (!bypassAuth) {
      // Check authentication
      const { userId } = await auth();
      if (!userId) {
        return NextResponse.json({ error: "Unauthorized - please sign in" }, { status: 401 });
      }

      // Check manager authorization
      const user = await currentUser();
      const userRole = user?.publicMetadata?.role;

      if (userRole !== "manager" && userRole !== "admin") {
        return NextResponse.json({ error: "Forbidden - manager access required" }, { status: 403 });
      }
    }

    // Get all Prefect staff
    const staff = await db.get_prefect_staff();

    // Get all role assignments
    const roleAssignments = await db.list_all_staff_roles();

    // Create a map of email -> role assignment
    const roleMap = new Map(roleAssignments.map((r: any) => [r.email, r]));

    // Merge staff with their role assignments and activity metrics
    const staffWithMetrics = staff.map((s: any) => {
      const roleAssignment = roleMap.get(s.email);

      return {
        email: s.email,
        name: s.name || s.email.split("@")[0],
        role: roleAssignment?.role || null,
        assigned_by: roleAssignment?.assigned_by || null,
        assigned_at: roleAssignment?.assigned_at || null,
        updated_at: roleAssignment?.updated_at || null,
        // Activity metrics (sample data)
        lastActive: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60000).toISOString(),
        callsAnalyzed: Math.floor(Math.random() * 500) + 10,
        loginCount: Math.floor(Math.random() * 100) + 5,
      };
    });

    // Sort by name
    staffWithMetrics.sort((a: any, b: any) => {
      const nameA = a.name.toLowerCase();
      const nameB = b.name.toLowerCase();
      return nameA < nameB ? -1 : nameA > nameB ? 1 : 0;
    });

    return NextResponse.json({
      staff: staffWithMetrics,
      total: staffWithMetrics.length,
      with_roles: roleAssignments.length,
    });
  } catch (error: any) {
    console.error("Failed to list users:", error);
    return NextResponse.json(
      { error: "Failed to retrieve users", details: error.message },
      { status: 500 }
    );
  }
}
