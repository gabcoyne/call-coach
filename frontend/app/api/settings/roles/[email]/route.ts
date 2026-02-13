/**
 * API route for managing individual staff role assignments.
 *
 * PUT /api/settings/roles/[email] - Update role for a staff member
 * DELETE /api/settings/roles/[email] - Remove role assignment
 *
 * Authorization: Requires manager role
 */
import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";
import * as db from "@/lib/db";
import { z } from "zod";

// Validation schema for role update
const UpdateRoleSchema = z.object({
  role: z.enum(["ae", "se", "csm"], {
    errorMap: () => ({ message: "Role must be one of: ae, se, csm" }),
  }),
});

/**
 * PUT handler - Update role assignment for a staff member
 *
 * Request body:
 * {
 *   "role": "ae" | "se" | "csm"
 * }
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ email: string }> }
) {
  const { email } = await params;

  try {
    // Check authentication
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized - please sign in" }, { status: 401 });
    }

    // Check manager authorization
    const user = await currentUser();
    const userRole = user?.publicMetadata?.role;
    const managerEmail = user?.emailAddresses?.[0]?.emailAddress;

    if (userRole !== "manager") {
      return NextResponse.json({ error: "Forbidden - manager access required" }, { status: 403 });
    }

    if (!managerEmail) {
      return NextResponse.json({ error: "Manager email not found" }, { status: 400 });
    }

    // Decode and validate email from URL
    const staffEmail = decodeURIComponent(email);

    // Validate that email is a Prefect email
    if (!staffEmail.endsWith("@prefect.io")) {
      return NextResponse.json(
        { error: "Invalid email - must be a @prefect.io address" },
        { status: 400 }
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const validation = UpdateRoleSchema.safeParse(body);

    if (!validation.success) {
      return NextResponse.json(
        {
          error: "Invalid request body",
          details: validation.error.errors,
        },
        { status: 400 }
      );
    }

    const { role } = validation.data;

    // Update role assignment in database
    await db.upsert_staff_role(staffEmail, role, managerEmail);

    return NextResponse.json({
      success: true,
      email: staffEmail,
      role: role,
      assigned_by: managerEmail,
      message: `Role updated to ${role.toUpperCase()} for ${staffEmail}`,
    });
  } catch (error: any) {
    console.error("Failed to update staff role:", error);
    return NextResponse.json(
      { error: "Failed to update role", details: error.message },
      { status: 500 }
    );
  }
}

/**
 * DELETE handler - Remove role assignment for a staff member
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ email: string }> }
) {
  const { email } = await params;

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

    // Decode email from URL
    const staffEmail = decodeURIComponent(email);

    // Validate that email is a Prefect email
    if (!staffEmail.endsWith("@prefect.io")) {
      return NextResponse.json(
        { error: "Invalid email - must be a @prefect.io address" },
        { status: 400 }
      );
    }

    // Delete role assignment from database
    await db.delete_staff_role(staffEmail);

    return NextResponse.json({
      success: true,
      email: staffEmail,
      message: `Role assignment removed for ${staffEmail}`,
    });
  } catch (error: any) {
    console.error("Failed to delete staff role:", error);
    return NextResponse.json(
      { error: "Failed to delete role", details: error.message },
      { status: 500 }
    );
  }
}
