/**
 * GET /api/emails/[id]
 *
 * Get email detail with body.
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  try {
    // Fetch email details
    const result = await query(
      `
      SELECT
        id,
        gong_email_id,
        subject,
        sender_email,
        recipients,
        sent_at,
        body_snippet,
        metadata
      FROM emails
      WHERE id = $1
      `,
      [id]
    );

    if (result.rows.length === 0) {
      return NextResponse.json({ error: "Email not found" }, { status: 404 });
    }

    return NextResponse.json({ email: result.rows[0] });
  } catch (error) {
    console.error(`Error fetching email ${id}:`, error);
    return NextResponse.json({ error: "Failed to fetch email" }, { status: 500 });
  }
}
