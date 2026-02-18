/**
 * POST /api/coaching-sessions/[id]/feedback
 *
 * Submit feedback on a coaching session.
 *
 * Request body:
 * {
 *   feedback_type: 'accurate' | 'inaccurate' | 'missing_context' | 'helpful' | 'not_helpful',
 *   feedback_text?: string
 * }
 */
import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db/connection";
import { getAuthContext } from "@/lib/auth-middleware";
import { z } from "zod";

// Validation schema for feedback submission
const feedbackSchema = z.object({
  feedback_type: z.enum(["accurate", "inaccurate", "missing_context", "helpful", "not_helpful"]),
  feedback_text: z.string().max(1000).optional(),
});

type FeedbackRequest = z.infer<typeof feedbackSchema>;

export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id: coachingSessionId } = await params;

  try {
    // Check authentication
    const authContext = await getAuthContext();

    // Parse and validate request body
    const body = await request.json();
    const validatedData = feedbackSchema.parse(body);

    // Get the coaching session to extract rep_id
    const sessionResult = await query(
      `
      SELECT id, rep_id, call_id FROM coaching_sessions
      WHERE id = $1
      `,
      [coachingSessionId]
    );

    if (sessionResult.rows.length === 0) {
      return NextResponse.json({ error: "Coaching session not found" }, { status: 404 });
    }

    const session = sessionResult.rows[0];

    // Get rep information to use as rep_id in feedback table
    // (rep_id is the speaker_id from the coaching_sessions table)
    const repId = session.rep_id;

    // Insert feedback record
    const feedbackResult = await query(
      `
      INSERT INTO coaching_feedback (
        coaching_session_id, rep_id, feedback_type, feedback_text, created_at
      )
      VALUES ($1, $2, $3, $4, NOW())
      RETURNING id, coaching_session_id, feedback_type, feedback_text, created_at
      `,
      [coachingSessionId, repId, validatedData.feedback_type, validatedData.feedback_text || null]
    );

    if (feedbackResult.rows.length === 0) {
      return NextResponse.json({ error: "Failed to record feedback" }, { status: 500 });
    }

    const feedback = feedbackResult.rows[0];

    return NextResponse.json(
      {
        success: true,
        feedback: {
          id: feedback.id,
          coaching_session_id: feedback.coaching_session_id,
          feedback_type: feedback.feedback_type,
          feedback_text: feedback.feedback_text,
          created_at: feedback.created_at,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: "Invalid request body",
          details: error.errors,
        },
        { status: 400 }
      );
    }

    // If auth fails, return 401
    if (
      error instanceof Error &&
      (error.message?.includes("authenticated") || error.message?.includes("Unauthorized"))
    ) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    console.error(`Error submitting feedback for session ${coachingSessionId}:`, error);
    return NextResponse.json({ error: "Failed to submit feedback" }, { status: 500 });
  }
}

/**
 * GET /api/coaching-sessions/[id]/feedback
 *
 * Get feedback for a coaching session.
 */
export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id: coachingSessionId } = await params;

  try {
    const result = await query(
      `
      SELECT
        id, coaching_session_id, rep_id, feedback_type, feedback_text, created_at
      FROM coaching_feedback
      WHERE coaching_session_id = $1
      ORDER BY created_at DESC
      `,
      [coachingSessionId]
    );

    return NextResponse.json({
      feedback: result.rows,
      count: result.rows.length,
    });
  } catch (error) {
    console.error(`Error fetching feedback for session ${coachingSessionId}:`, error);
    return NextResponse.json({ error: "Failed to fetch feedback" }, { status: 500 });
  }
}
