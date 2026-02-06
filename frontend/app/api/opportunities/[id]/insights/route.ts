/**
 * GET /api/opportunities/[id]/insights
 *
 * Generate holistic coaching insights for an opportunity using the analyze_opportunity MCP tool.
 * This calls the Python backend to run analysis across all calls/emails.
 */
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;

    // Call the MCP tool via Python backend
    // This is a placeholder - in production, this would call the actual MCP server
    // For now, return mock insights to demonstrate the UI
    const mockInsights = {
      insights: {
        themes: ["Budget constraints", "Technical integration concerns", "Timeline pressure"],
        objections: [
          {
            objection: "Pricing is higher than competitors",
            frequency: 3,
            status: "partially_resolved",
          },
          {
            objection: "Integration complexity with existing systems",
            frequency: 2,
            status: "unresolved",
          },
        ],
        relationship_strength: {
          score: 65,
          trend: "improving",
          notes:
            "Engagement has increased over the last two weeks. Key decision maker is now more responsive.",
        },
        recommendations: [
          "Address integration concerns with a detailed technical demo focusing on API compatibility",
          "Schedule a call with the CFO to discuss ROI and present case studies from similar customers",
          "Follow up on pricing objection with a custom quote that highlights value-add features",
          "Maintain momentum by scheduling next steps within 48 hours",
          "Consider involving a solutions engineer for the next technical discussion",
        ],
      },
      generated_at: new Date().toISOString(),
    };

    // TODO: Replace with actual MCP tool call
    // Example:
    // const response = await fetch('http://localhost:8000/mcp/analyze_opportunity', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ opportunity_id: id }),
    // });
    // const insights = await response.json();

    return NextResponse.json(mockInsights);
  } catch (error) {
    console.error(`Error generating insights for opportunity ${id}:`, error);
    return NextResponse.json({ error: "Failed to generate insights" }, { status: 500 });
  }
}
