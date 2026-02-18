/**
 * API route for exporting user data (GDPR compliant).
 *
 * POST /api/user/data/export - Export user's personal data
 *
 * Request body:
 * {
 *   "format": "csv" | "json",
 *   "includeCallRecordings": boolean,
 *   "includeTranscripts": boolean,
 *   "includeCoachingFeedback": boolean
 * }
 *
 * Returns: File stream (CSV or JSON)
 */
import { NextRequest, NextResponse } from "next/server";
import { getAuthContext } from "@/lib/auth-middleware";

// Mock data for demo
const mockCoachingData = {
  user: {
    id: "user123",
    email: "user@example.com",
    firstName: "John",
    lastName: "Doe",
    createdAt: new Date().toISOString(),
  },
  sessions: [
    {
      id: "session1",
      date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 45,
      callId: "call123",
      dimensions: {
        opening: 8,
        discovery: 7,
        pitch: 8,
        objectionHandling: 6,
        closing: 7,
      },
      feedback: "Strong opening and discovery questions. Could improve objection handling.",
    },
    {
      id: "session2",
      date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 35,
      callId: "call124",
      dimensions: {
        opening: 7,
        discovery: 8,
        pitch: 7,
        objectionHandling: 7,
        closing: 8,
      },
      feedback: "Excellent discovery process and closing technique. Great improvement!",
    },
  ],
  transcripts: [
    {
      id: "transcript1",
      sessionId: "session1",
      date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      content: "[Sample transcript content would go here]",
    },
  ],
};

function convertToCSV(data: any): string {
  // Convert coaching sessions to CSV format
  let csv = "ID,Date,Duration (mins),Opening,Discovery,Pitch,Objection Handling,Closing,Feedback\n";

  data.sessions.forEach((session: any) => {
    const row = [
      session.id,
      session.date,
      session.duration,
      session.dimensions.opening,
      session.dimensions.discovery,
      session.dimensions.pitch,
      session.dimensions.objectionHandling,
      session.dimensions.closing,
      `"${session.feedback}"`,
    ];
    csv += row.join(",") + "\n";
  });

  return csv;
}

function convertToJSON(data: any): string {
  return JSON.stringify(data, null, 2);
}

export async function POST(request: NextRequest) {
  try {
    const authContext = await getAuthContext();
    const body = await request.json();

    const { format = "csv", includeTranscripts = true } = body;

    // Validate format
    if (!["csv", "json"].includes(format)) {
      return NextResponse.json(
        { error: "Invalid format. Must be 'csv' or 'json'" },
        { status: 400 }
      );
    }

    // Build export data
    const exportData = {
      exportDate: new Date().toISOString(),
      user: {
        id: authContext.userId,
        email: authContext.email,
        name: authContext.name,
      },
      sessions: mockCoachingData.sessions,
      ...(includeTranscripts && { transcripts: mockCoachingData.transcripts }),
    };

    // Convert to requested format
    let content: string;
    let contentType: string;
    let filename: string;

    if (format === "json") {
      content = convertToJSON(exportData);
      contentType = "application/json";
      filename = `call-coach-data-export-${new Date().toISOString().split("T")[0]}.json`;
    } else {
      content = convertToCSV(exportData);
      contentType = "text/csv";
      filename = `call-coach-data-export-${new Date().toISOString().split("T")[0]}.csv`;
    }

    // Log export for audit trail
    console.log(
      `Data export for user ${authContext.userId}: ${format} format, includes transcripts: ${includeTranscripts}`
    );

    return new NextResponse(content, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename="${filename}"`,
      },
    });
  } catch (error: any) {
    // If auth fails, return 401
    if (error.message?.includes("authenticated") || error.message?.includes("Unauthorized")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    console.error("Failed to export data:", error);
    return NextResponse.json(
      { error: "Failed to export data", details: error.message },
      { status: 500 }
    );
  }
}
