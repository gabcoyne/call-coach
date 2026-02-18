/**
 * API route for updating a user's role.
 *
 * PUT /api/admin/users/[email]/role - Update user role
 *
 * Authorization: Requires manager role
 *
 * Request body:
 * {
 *   "role": "manager" | "ae" | "se" | "csm" | null
 * }
 */
import { NextRequest, NextResponse } from "next/server";
import { getAuthContext } from "@/lib/auth-middleware";
import * as db from "@/lib/db";

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ email: string }> }
) {
  try {
    // Check authentication and authorization
    const authContext = await getAuthContext();

    if (authContext.role !== "manager") {
      return NextResponse.json({ error: "Forbidden - manager access required" }, { status: 403 });
    }

    const managerEmail = authContext.email;

    const { email } = await params;
    const body = await request.json();
    const { role } = body;

    // Validate role
    const validRoles = ["manager", "ae", "se", "csm"];
    if (role && !validRoles.includes(role)) {
      return NextResponse.json(
        { error: "Invalid role. Must be one of: manager, ae, se, csm, or null" },
        { status: 400 }
      );
    }

    // Validate email format
    if (!email.includes("@")) {
      return NextResponse.json({ error: "Invalid email format" }, { status: 400 });
    }

    // Update or delete role
    if (role) {
      await db.upsert_staff_role(email, role, managerEmail);
    } else {
      await db.delete_staff_role(email);
    }

    return NextResponse.json({
      success: true,
      email,
      role: role || null,
      updated_by: managerEmail,
      updated_at: new Date().toISOString(),
    });
  } catch (error: any) {
    // If auth fails, return 401
    if (error.message?.includes("authenticated") || error.message?.includes("Unauthorized")) {
      return NextResponse.json({ error: "Unauthorized - please sign in" }, { status: 401 });
    }
    console.error("Failed to update user role:", error);
    return NextResponse.json(
      { error: "Failed to update user role", details: error.message },
      { status: 500 }
    );
  }
}
