/**
 * API route for managing user preferences.
 *
 * GET /api/user/preferences - Get user's preferences
 * PUT /api/user/preferences - Update user's preferences
 *
 * Preferences include:
 * - Notification settings (email, Slack integration)
 * - Display preferences (theme, layout)
 * - Coaching dimension defaults
 * - Data retention settings
 */
import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";

// In-memory store for demo purposes
// In production, this would be stored in the database
const userPreferencesStore = new Map<string, any>();

export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const preferences = userPreferencesStore.get(userId) || {
      // Default preferences
      theme: "system",
      compactMode: false,
      autoRefreshEnabled: true,
      dashboardLayout: "grid",
      defaultCoachingDimensions: ["opening", "discovery", "pitch"],
      weeklyReports: true,
      coachingUpdates: true,
      callAnalysis: true,
      opportunityInsights: true,
      slackIntegration: false,
      notificationFrequency: "weekly",
      dataRetentionDays: 180,
    };

    return NextResponse.json(preferences);
  } catch (error: any) {
    console.error("Failed to get preferences:", error);
    return NextResponse.json(
      { error: "Failed to retrieve preferences", details: error.message },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const body = await request.json();

    // Validate incoming preferences
    const validatedPreferences = {
      theme: body.theme || "system",
      compactMode: body.compactMode ?? false,
      autoRefreshEnabled: body.autoRefreshEnabled ?? true,
      dashboardLayout: body.dashboardLayout || "grid",
      defaultCoachingDimensions: body.defaultCoachingDimensions || ["opening", "discovery", "pitch"],
      weeklyReports: body.weeklyReports ?? true,
      coachingUpdates: body.coachingUpdates ?? true,
      callAnalysis: body.callAnalysis ?? true,
      opportunityInsights: body.opportunityInsights ?? true,
      slackIntegration: body.slackIntegration ?? false,
      notificationFrequency: body.notificationFrequency || "weekly",
      dataRetentionDays: body.dataRetentionDays ?? 180,
    };

    // Validate coaching dimensions are not empty
    if (!Array.isArray(validatedPreferences.defaultCoachingDimensions) ||
        validatedPreferences.defaultCoachingDimensions.length === 0) {
      return NextResponse.json(
        { error: "At least one coaching dimension must be selected" },
        { status: 400 }
      );
    }

    // Validate notification frequency
    const validFrequencies = ["daily", "weekly", "monthly"];
    if (!validFrequencies.includes(validatedPreferences.notificationFrequency)) {
      return NextResponse.json(
        { error: "Invalid notification frequency" },
        { status: 400 }
      );
    }

    // Validate theme
    const validThemes = ["light", "dark", "system"];
    if (!validThemes.includes(validatedPreferences.theme)) {
      return NextResponse.json(
        { error: "Invalid theme" },
        { status: 400 }
      );
    }

    // Store preferences
    userPreferencesStore.set(userId, validatedPreferences);

    return NextResponse.json({
      success: true,
      message: "Preferences updated successfully",
      preferences: validatedPreferences,
    });
  } catch (error: any) {
    console.error("Failed to update preferences:", error);
    return NextResponse.json(
      { error: "Failed to update preferences", details: error.message },
      { status: 500 }
    );
  }
}
