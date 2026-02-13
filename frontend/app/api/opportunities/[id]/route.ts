/**
 * GET /api/opportunities/[id]
 *
 * Get opportunity detail with call/email counts.
 */
import { NextRequest, NextResponse } from "next/server";
import { getOpportunity } from "@/lib/db/opportunities";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  try {
    // Fetch opportunity
    const opportunity = await getOpportunity(id);

    if (!opportunity) {
      return NextResponse.json({ error: "Opportunity not found" }, { status: 404 });
    }

    return NextResponse.json({ opportunity });
  } catch (error) {
    console.error(`Error fetching opportunity ${id}:`, error);
    return NextResponse.json({ error: "Failed to fetch opportunity" }, { status: 500 });
  }
}
