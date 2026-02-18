/**
 * GET /api/auth/me
 *
 * Returns the current user's information from IAP headers.
 * Used by the client-side auth context to get user info.
 */

import { NextResponse } from "next/server";
import { getAuthContext } from "@/lib/auth-middleware";

export async function GET() {
  try {
    const authContext = await getAuthContext();

    return NextResponse.json({
      user: {
        id: authContext.userId,
        email: authContext.email,
        name: authContext.name,
        role: authContext.role,
      },
    });
  } catch (error) {
    // Not authenticated
    return NextResponse.json({ user: null }, { status: 401 });
  }
}
