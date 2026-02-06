/**
 * GET /api/calls/[id]/coaching-sessions
 *
 * Get all coaching sessions for a call.
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: callId } = await params;

    const result = await query(
      `
      SELECT
        id, call_id, coaching_dimension, session_type, score, created_at
      FROM coaching_sessions
      WHERE call_id = $1
      ORDER BY created_at DESC
      `,
      [callId]
    );

    return NextResponse.json({
      coaching_sessions: result.rows,
      count: result.rows.length,
    });
  } catch (error) {
    const { id: callId } = await params;
    console.error(`Error fetching coaching sessions for call ${callId}:`, error);
    return NextResponse.json({ error: "Failed to fetch coaching sessions" }, { status: 500 });
  }
}
