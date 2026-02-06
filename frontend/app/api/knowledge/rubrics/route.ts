/**
 * Coaching Rubrics API
 *
 * Endpoints:
 * GET /api/knowledge/rubrics - List coaching rubrics
 * POST /api/knowledge/rubrics - Create new rubric version
 * PATCH /api/knowledge/rubrics - Update rubric metadata
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const category = searchParams.get("category");
    const activeOnly = searchParams.get("active_only") !== "false";
    const allVersions = searchParams.get("all_versions") === "true";

    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (allVersions) params.append("all_versions", "true");
    params.append("active_only", String(activeOnly));

    const response = await fetch(`${API_BASE}/knowledge/rubrics?${params.toString()}`, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching rubrics:", error);
    return NextResponse.json({ error: "Failed to fetch rubrics" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();

    // Validate required fields
    const required = ["name", "version", "category", "criteria", "scoring_guide"];
    const missing = required.filter((field) => !body[field]);

    if (missing.length > 0) {
      return NextResponse.json(
        { error: `Missing required fields: ${missing.join(", ")}` },
        { status: 400 }
      );
    }

    const response = await fetch(`${API_BASE}/knowledge/rubrics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...body,
        created_by: userId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error creating rubric:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to create rubric",
      },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const rubricId = searchParams.get("id");

    if (!rubricId) {
      return NextResponse.json({ error: "Missing required parameter: id" }, { status: 400 });
    }

    const body = await request.json();

    const response = await fetch(`${API_BASE}/knowledge/rubrics/${rubricId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...body,
        updated_by: userId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error updating rubric:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to update rubric",
      },
      { status: 500 }
    );
  }
}
