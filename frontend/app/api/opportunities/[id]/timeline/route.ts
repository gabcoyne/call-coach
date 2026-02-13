/**
 * GET /api/opportunities/[id]/timeline
 *
 * Get chronological timeline of calls and emails for an opportunity.
 *
 * Query params:
 * - page: Page number (1-based, default: 1)
 * - limit: Items per page (default: 20, max: 100)
 */
import { NextRequest, NextResponse } from "next/server";
import { getOpportunityTimeline } from "@/lib/db/opportunities";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const searchParams = request.nextUrl.searchParams;

  try {
    // Parse pagination
    const page = parseInt(searchParams.get("page") || "1", 10);
    const limit = Math.min(parseInt(searchParams.get("limit") || "20", 10), 100);

    if (page < 1 || limit < 1) {
      return NextResponse.json({ error: "Invalid pagination parameters" }, { status: 400 });
    }

    const offset = (page - 1) * limit;

    // Fetch timeline items
    const { items, total } = await getOpportunityTimeline({
      opportunityId: id,
      limit,
      offset,
    });

    // Return timeline with pagination metadata
    return NextResponse.json({
      items,
      pagination: {
        page,
        limit,
        total,
        hasMore: offset + items.length < total,
      },
    });
  } catch (error) {
    console.error(`Error fetching timeline for opportunity ${id}:`, error);
    return NextResponse.json({ error: "Failed to fetch timeline" }, { status: 500 });
  }
}
