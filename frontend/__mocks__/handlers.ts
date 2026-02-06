/**
 * MSW (Mock Service Worker) handlers for API mocking in tests.
 *
 * This file defines mock handlers for all API endpoints used in the frontend.
 * These handlers intercept network requests during tests and return mock responses.
 */

import { http, HttpResponse } from "msw";

// Base URL for API
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";

// Mock data generators
const createMockCall = (id: string, overrides = {}) => ({
  id,
  rep_id: "rep-123",
  opportunity_id: "opp-456",
  title: "Mock Sales Call",
  duration: 1800,
  call_date: new Date().toISOString(),
  transcript: "This is a mock transcript of a sales call.",
  recording_url: "https://example.com/recording.mp3",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
});

const createMockAnalysis = (id: string, call_id: string, overrides = {}) => ({
  id,
  call_id,
  dimension: "discovery_quality",
  score: 8.5,
  feedback: "Great job on discovery questions!",
  strengths: ["Asked open-ended questions", "Active listening"],
  areas_for_improvement: ["Could probe deeper on pain points"],
  specific_examples: ["Timestamp 5:30 - excellent follow-up question"],
  analyzed_at: new Date().toISOString(),
  created_at: new Date().toISOString(),
  ...overrides,
});

const createMockRepInsight = (id: string, rep_id: string, overrides = {}) => ({
  id,
  rep_id,
  insight_type: "trend",
  title: "Improving Discovery Skills",
  description: "Your discovery question score has improved 15% this month.",
  metric_name: "discovery_quality",
  metric_value: 8.5,
  trend_direction: "up",
  priority: "medium",
  created_at: new Date().toISOString(),
  expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
  ...overrides,
});

const createMockCoachingSession = (id: string, rep_id: string, overrides = {}) => ({
  id,
  rep_id,
  coach_id: "coach-789",
  session_date: new Date().toISOString(),
  duration: 3600,
  topics: ["Discovery", "Objection Handling"],
  goals: ["Improve discovery question quality", "Close more effectively"],
  action_items: ["Practice SPIN questions", "Review objection handling framework"],
  notes: "Great progress on discovery skills.",
  follow_up_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
  status: "completed",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
});

// API handlers
export const handlers = [
  // Calls endpoints
  http.get(`${API_BASE}/api/calls`, () => {
    return HttpResponse.json({
      calls: [
        createMockCall("call-1"),
        createMockCall("call-2", { title: "Follow-up Call" }),
        createMockCall("call-3", { title: "Demo Call" }),
      ],
      total: 3,
      page: 1,
      page_size: 20,
    });
  }),

  http.get(`${API_BASE}/api/calls/:id`, ({ params }) => {
    const { id } = params;
    return HttpResponse.json(createMockCall(id as string));
  }),

  http.post(`${API_BASE}/api/calls`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(createMockCall("call-new", body), { status: 201 });
  }),

  // Analysis endpoints
  http.get(`${API_BASE}/api/calls/:callId/analysis`, ({ params }) => {
    const { callId } = params;
    return HttpResponse.json([
      createMockAnalysis("analysis-1", callId as string),
      createMockAnalysis("analysis-2", callId as string, {
        dimension: "objection_handling",
        score: 7.5,
      }),
    ]);
  }),

  http.post(`${API_BASE}/api/calls/:callId/analysis`, async ({ params, request }) => {
    const { callId } = params;
    const body = await request.json();
    return HttpResponse.json(createMockAnalysis("analysis-new", callId as string, body), {
      status: 201,
    });
  }),

  // Rep insights endpoints
  http.get(`${API_BASE}/api/reps/:repId/insights`, ({ params }) => {
    const { repId } = params;
    return HttpResponse.json({
      insights: [
        createMockRepInsight("insight-1", repId as string),
        createMockRepInsight("insight-2", repId as string, {
          insight_type: "achievement",
          title: "Top Performer This Week",
          trend_direction: "up",
        }),
      ],
      total: 2,
    });
  }),

  http.get(`${API_BASE}/api/reps/:repId/stats`, ({ params }) => {
    return HttpResponse.json({
      rep_id: params.repId,
      total_calls: 42,
      avg_score: 8.2,
      calls_this_week: 12,
      calls_this_month: 42,
      dimensions: {
        discovery_quality: 8.5,
        objection_handling: 7.8,
        product_knowledge: 8.9,
        closing_technique: 7.5,
        rapport_building: 8.3,
      },
      trends: {
        discovery_quality: "up",
        objection_handling: "stable",
        product_knowledge: "up",
        closing_technique: "down",
        rapport_building: "stable",
      },
    });
  }),

  // Coaching sessions endpoints
  http.get(`${API_BASE}/api/coaching-sessions`, ({ request }) => {
    const url = new URL(request.url);
    const repId = url.searchParams.get("rep_id");

    return HttpResponse.json({
      sessions: [
        createMockCoachingSession("session-1", repId || "rep-123"),
        createMockCoachingSession("session-2", repId || "rep-123", {
          status: "scheduled",
          session_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        }),
      ],
      total: 2,
    });
  }),

  http.get(`${API_BASE}/api/coaching-sessions/:id`, ({ params }) => {
    return HttpResponse.json(createMockCoachingSession(params.id as string, "rep-123"));
  }),

  http.post(`${API_BASE}/api/coaching-sessions`, async ({ request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json(
      createMockCoachingSession("session-new", body.rep_id || "rep-123", body),
      { status: 201 }
    );
  }),

  http.put(`${API_BASE}/api/coaching-sessions/:id`, async ({ params, request }) => {
    const body = await request.json();
    return HttpResponse.json(createMockCoachingSession(params.id as string, "rep-123", body));
  }),

  // Opportunities endpoints
  http.get(`${API_BASE}/api/opportunities`, () => {
    return HttpResponse.json({
      opportunities: [
        {
          id: "opp-1",
          rep_id: "rep-123",
          company_name: "Acme Corp",
          amount: 50000,
          stage: "Proposal",
          close_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          probability: 70,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: "opp-2",
          rep_id: "rep-123",
          company_name: "TechStart Inc",
          amount: 75000,
          stage: "Negotiation",
          close_date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(),
          probability: 85,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 2,
    });
  }),

  http.get(`${API_BASE}/api/opportunities/:id/insights`, ({ params }) => {
    return HttpResponse.json({
      opportunity_id: params.id,
      insights: [
        {
          type: "call_frequency",
          message: "3 calls in last 7 days - good momentum",
          score: 8.5,
        },
        {
          type: "discovery_depth",
          message: "Discovery calls scored 8.2/10 on average",
          score: 8.2,
        },
      ],
    });
  }),

  // Search endpoint
  http.get(`${API_BASE}/api/search`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get("q");

    return HttpResponse.json({
      results: [
        { type: "call", id: "call-1", title: `Call matching: ${query}`, score: 0.95 },
        { type: "rep", id: "rep-1", title: `Rep matching: ${query}`, score: 0.87 },
      ],
      total: 2,
      query,
    });
  }),

  // Error simulation handlers (can be activated in specific tests)
  http.get(`${API_BASE}/api/error/500`, () => {
    return HttpResponse.json(
      { error: "Internal Server Error", message: "Something went wrong" },
      { status: 500 }
    );
  }),

  http.get(`${API_BASE}/api/error/404`, () => {
    return HttpResponse.json(
      { error: "Not Found", message: "Resource not found" },
      { status: 404 }
    );
  }),

  http.get(`${API_BASE}/api/error/401`, () => {
    return HttpResponse.json(
      { error: "Unauthorized", message: "Authentication required" },
      { status: 401 }
    );
  }),
];

// Export individual mock data creators for use in tests
export { createMockCall, createMockAnalysis, createMockRepInsight, createMockCoachingSession };
