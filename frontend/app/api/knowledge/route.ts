/**
 * Knowledge Base Management API
 *
 * Endpoints:
 * GET /api/knowledge - List all knowledge base entries
 * POST /api/knowledge - Create/update knowledge base entry
 * DELETE /api/knowledge - Delete knowledge base entry
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

    // Get query parameters
    const { searchParams } = new URL(request.url);
    const product = searchParams.get("product");
    const category = searchParams.get("category");

    // Build query string
    const params = new URLSearchParams();
    if (product) params.append("product", product);
    if (category) params.append("category", category);

    const response = await fetch(`${API_BASE}/knowledge?${params.toString()}`, {
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
    console.error("Error fetching knowledge entries:", error);
    return NextResponse.json({ error: "Failed to fetch knowledge entries" }, { status: 500 });
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
    if (!body.product || !body.category || !body.content) {
      return NextResponse.json(
        { error: "Missing required fields: product, category, content" },
        { status: 400 }
      );
    }

    // Add user metadata
    body.metadata = {
      ...body.metadata,
      updated_by: userId,
      updated_at: new Date().toISOString(),
    };

    const response = await fetch(`${API_BASE}/knowledge`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error creating/updating knowledge entry:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to create/update knowledge entry",
      },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
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

    const response = await fetch(`${API_BASE}/knowledge?product=${product}&category=${category}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error deleting knowledge entry:", error);
    return NextResponse.json({ error: "Failed to delete knowledge entry" }, { status: 500 });
  }
}
