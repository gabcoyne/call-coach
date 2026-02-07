/**
 * Staff Roles API
 *
 * GET /api/users/staff-roles - List all staff role assignments
 * PUT /api/users/staff-roles - Create or update staff role
 * DELETE /api/users/staff-roles?email=... - Remove staff role
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";

export async function GET() {
  try {
    const result = await query(`
      SELECT
        email,
        role,
        assigned_by,
        assigned_at,
        updated_at
      FROM staff_roles
      ORDER BY assigned_at DESC
    `);

    return NextResponse.json(result.rows);
  } catch (error) {
    console.error("Error fetching staff roles:", error);
    return NextResponse.json({ error: "Failed to fetch staff roles" }, { status: 500 });
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, role } = body;

    if (!email || !role) {
      return NextResponse.json({ error: "Email and role are required" }, { status: 400 });
    }

    if (!["admin", "manager", "rep"].includes(role)) {
      return NextResponse.json({ error: "Invalid role" }, { status: 400 });
    }

    const assignedBy = request.headers.get("X-User-Email") || "system";

    await query(
      `
      INSERT INTO staff_roles (email, role, assigned_by)
      VALUES ($1, $2, $3)
      ON CONFLICT (email)
      DO UPDATE SET
        role = EXCLUDED.role,
        assigned_by = EXCLUDED.assigned_by,
        updated_at = NOW()
    `,
      [email, role, assignedBy]
    );

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error updating staff role:", error);
    return NextResponse.json({ error: "Failed to update staff role" }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const email = searchParams.get("email");

    if (!email) {
      return NextResponse.json({ error: "Email is required" }, { status: 400 });
    }

    await query("DELETE FROM staff_roles WHERE email = $1", [email]);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error deleting staff role:", error);
    return NextResponse.json({ error: "Failed to delete staff role" }, { status: 500 });
  }
}
