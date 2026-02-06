/**
 * GET /api/calls/[id]
 *
 * Get call detail with transcript.
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    // Fetch call details
    const result = await query(
      `
      SELECT
        id,
        gong_call_id,
        title,
        scheduled_at,
        duration,
        participants,
        transcript,
        summary,
        metadata
      FROM calls
      WHERE id = $1
      `,
      [id]
    );

    if (result.rows.length === 0) {
      return NextResponse.json({ error: "Call not found" }, { status: 404 });
    }

    return NextResponse.json({ call: result.rows[0] });
  } catch (error) {
    console.error(`Error fetching call ${params.id}:`, error);
    return NextResponse.json(
      { error: "Failed to fetch call" },
      { status: 500 }
    );
  }
}
