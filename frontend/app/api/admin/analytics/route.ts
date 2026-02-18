/**
 * API route for analytics and performance insights.
 *
 * GET /api/admin/analytics - Get coaching dimension scores, top performers, and skill gaps
 *
 * Authorization: Requires manager role
 */
import { NextRequest, NextResponse } from "next/server";
import { getAuthContext } from "@/lib/auth-middleware";

export async function GET(request: NextRequest) {
  try {
    // Check authentication and authorization
    const authContext = await getAuthContext();

    if (authContext.role !== "manager") {
      return NextResponse.json({ error: "Forbidden - manager access required" }, { status: 403 });
    }

    // Coaching dimensions with score distributions
    const coachingDimensions = [
      { dimension: "Objection Handling", score: 78, count: 45 },
      { dimension: "Discovery", score: 82, count: 42 },
      { dimension: "Pitch Quality", score: 75, count: 48 },
      { dimension: "Closing", score: 71, count: 39 },
      { dimension: "Rapport Building", score: 88, count: 52 },
    ];

    // Top performers leaderboard
    const topPerformers = [
      {
        name: "Alice Johnson",
        email: "alice.johnson@prefect.io",
        avgScore: 89.5,
        callsAnalyzed: 128,
        rank: 1,
      },
      {
        name: "Bob Smith",
        email: "bob.smith@prefect.io",
        avgScore: 87.2,
        callsAnalyzed: 115,
        rank: 2,
      },
      {
        name: "Carol White",
        email: "carol.white@prefect.io",
        avgScore: 85.8,
        callsAnalyzed: 98,
        rank: 3,
      },
      {
        name: "David Brown",
        email: "david.brown@prefect.io",
        avgScore: 84.1,
        callsAnalyzed: 92,
        rank: 4,
      },
      {
        name: "Emma Davis",
        email: "emma.davis@prefect.io",
        avgScore: 82.6,
        callsAnalyzed: 87,
        rank: 5,
      },
    ];

    // Skill gap analysis
    const skillGaps = [
      {
        skill: "Advanced Negotiation",
        averageScore: 68.5,
        targetScore: 85.0,
        gap: 16.5,
        teamMembers: 24,
      },
      {
        skill: "Product Deep Dive",
        averageScore: 72.3,
        targetScore: 85.0,
        gap: 12.7,
        teamMembers: 24,
      },
      {
        skill: "Competitive Positioning",
        averageScore: 75.1,
        targetScore: 85.0,
        gap: 9.9,
        teamMembers: 22,
      },
      {
        skill: "Executive Communication",
        averageScore: 78.4,
        targetScore: 85.0,
        gap: 6.6,
        teamMembers: 18,
      },
      {
        skill: "ROI Articulation",
        averageScore: 79.8,
        targetScore: 85.0,
        gap: 5.2,
        teamMembers: 20,
      },
    ];

    return NextResponse.json({
      coachingDimensions,
      topPerformers,
      skillGaps,
    });
  } catch (error: any) {
    // If auth fails, return 401
    if (error.message?.includes("authenticated") || error.message?.includes("Unauthorized")) {
      return NextResponse.json({ error: "Unauthorized - please sign in" }, { status: 401 });
    }
    console.error("Failed to retrieve analytics:", error);
    return NextResponse.json(
      { error: "Failed to retrieve analytics", details: error.message },
      { status: 500 }
    );
  }
}
