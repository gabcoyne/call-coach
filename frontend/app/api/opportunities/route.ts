/**
 * GET /api/opportunities
 *
 * List opportunities with filtering, sorting, and pagination.
 *
 * Query params:
 * - owner: Filter by owner email
 * - stage: Filter by stage (can be comma-separated list)
 * - health_score_min: Minimum health score
 * - health_score_max: Maximum health score
 * - search: Text search on name/account
 * - sort: Sort field (updated_at, close_date, health_score, amount)
 * - sort_dir: Sort direction (ASC, DESC)
 * - page: Page number (1-based)
 * - limit: Items per page
 */
import { NextRequest, NextResponse } from "next/server";
import { searchOpportunities } from "@/lib/db/opportunities";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Parse filters
    const filters: Record<string, any> = {};

    const owner = searchParams.get("owner");
    if (owner) {
      filters.owner = owner;
    }

    const stage = searchParams.get("stage");
    if (stage) {
      // Support comma-separated list
      filters.stage = stage.includes(",") ? stage.split(",") : stage;
    }

    const healthScoreMin = searchParams.get("health_score_min");
    if (healthScoreMin) {
      filters.health_score_min = parseFloat(healthScoreMin);
    }

    const healthScoreMax = searchParams.get("health_score_max");
    if (healthScoreMax) {
      filters.health_score_max = parseFloat(healthScoreMax);
    }

    const search = searchParams.get("search");
    if (search) {
      filters.search = search;
    }

    // Parse sorting
    const sort = searchParams.get("sort") || "updated_at";
    const sortDir = searchParams.get("sort_dir") || "DESC";

    // Parse pagination
    const page = parseInt(searchParams.get("page") || "1", 10);
    const limit = parseInt(searchParams.get("limit") || "50", 10);

    // Validate pagination
    if (page < 1 || limit < 1 || limit > 200) {
      return NextResponse.json(
        { error: "Invalid pagination parameters" },
        { status: 400 }
      );
    }

    const offset = (page - 1) * limit;

    // Query database
    const { opportunities, total } = await searchOpportunities({
      filters,
      sort,
      sortDir,
      limit,
      offset,
    });

    // Return response with pagination metadata
    return NextResponse.json({
      opportunities,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
        hasMore: offset + opportunities.length < total,
      },
    });
  } catch (error) {
    console.error("Error fetching opportunities:", error);
    return NextResponse.json(
      { error: "Failed to fetch opportunities" },
      { status: 500 }
    );
  }
}
