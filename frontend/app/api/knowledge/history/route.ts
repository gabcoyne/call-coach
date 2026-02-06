/**
 * Knowledge Base History API
 *
 * GET /api/knowledge/history - Get version history for an entry
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
    const product = searchParams.get("product");
    const category = searchParams.get("category");

    if (!product || !category) {
      return NextResponse.json(
        { error: "Missing required parameters: product, category" },
        { status: 400 }
      );
    }

    const response = await fetch(
      `${API_BASE}/knowledge/history?product=${product}&category=${category}`,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching knowledge history:", error);
    return NextResponse.json(
      { error: "Failed to fetch knowledge history" },
      { status: 500 }
    );
  }
}
