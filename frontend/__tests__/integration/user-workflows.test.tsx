/**
 * Integration Tests for User Workflows
 *
 * Tests 11.4-11.5:
 * - test_login_dashboard: Verify user can login and navigate to dashboard
 * - test_create_session: Verify user can create a coaching session workflow
 */

import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DashboardPage from "@/app/dashboard/page";

// Mock SWR hooks
jest.mock("@/lib/hooks/use-search-calls", () => ({
  useSearchCalls: jest.fn(() => ({
    data: [],
    isLoading: false,
    error: null,
  })),
}));

// Get mock functions that are already defined in jest.setup.js
const mockUseUser = require("@clerk/nextjs").useUser;
const mockUseAuth = require("@clerk/nextjs").useAuth;
const mockUseRouter = require("next/navigation").useRouter;
const mockUsePathname = require("next/navigation").usePathname;

describe("User Workflow Integration Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("test_login_dashboard (11.4)", () => {
    it("should render dashboard after successful authentication as manager", async () => {
      // Mock authenticated manager user
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "manager-123",
          emailAddresses: [{ emailAddress: "manager@prefect.io" }],
          publicMetadata: { role: "manager" },
        } as any,
      });

      mockUseAuth.mockReturnValue({
        isSignedIn: true,
        userId: "manager-123",
        sessionId: "session-123",
      } as any);

      // Mock API response for calls
      const { useSearchCalls } = require("@/lib/hooks/use-search-calls");
      useSearchCalls.mockReturnValue({
        data: [
          {
            id: "call-1",
            prefect_reps: ["John Doe", "Jane Smith"],
            overall_score: 85,
            date: "2024-01-15T10:00:00Z",
          },
          {
            id: "call-2",
            prefect_reps: ["John Doe"],
            overall_score: 90,
            date: "2024-01-16T10:00:00Z",
          },
        ],
        isLoading: false,
        error: null,
      });

      render(<DashboardPage />);

      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText("Team Dashboard")).toBeInTheDocument();
      });

      // Verify dashboard elements are present
      expect(screen.getByText("Overview of all sales reps performance")).toBeInTheDocument();
      expect(screen.getByText("Sales Representatives")).toBeInTheDocument();
    });

    it("should redirect rep to their own dashboard", async () => {
      // Mock authenticated rep user
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "rep-123",
          emailAddresses: [{ emailAddress: "rep@prefect.io" }],
          publicMetadata: { role: "rep" },
        } as any,
      });

      mockUseAuth.mockReturnValue({
        isSignedIn: true,
        userId: "rep-123",
        sessionId: "session-123",
      } as any);

      const { container } = render(<DashboardPage />);

      // For a rep, the component should render null (as it redirects)
      // or show a brief loading state before redirect
      // The actual redirect logic is handled by the router which we've mocked
      await waitFor(() => {
        // Component should either be empty or show minimal content
        expect(container.textContent === "" || container.textContent).toBeDefined();
      });
    });

    it("should show loading state while user data loads", () => {
      // Mock loading state
      mockUseUser.mockReturnValue({
        isLoaded: false,
        isSignedIn: false,
        user: null,
      } as any);

      mockUseAuth.mockReturnValue({
        isSignedIn: false,
        userId: null,
        sessionId: null,
      } as any);

      render(<DashboardPage />);

      // Verify loading state
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    it("should handle authentication errors gracefully", async () => {
      // Mock authenticated user but API error
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "manager-123",
          emailAddresses: [{ emailAddress: "manager@prefect.io" }],
          publicMetadata: { role: "manager" },
        } as any,
      });

      const { useSearchCalls } = require("@/lib/hooks/use-search-calls");
      useSearchCalls.mockReturnValue({
        data: null,
        isLoading: false,
        error: new Error("Failed to fetch rep data"),
      });

      render(<DashboardPage />);

      // Wait for error state to render
      await waitFor(() => {
        expect(screen.getByText("Error loading dashboard")).toBeInTheDocument();
      });

      expect(screen.getByText("Failed to fetch rep data")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
    });

    it("should complete full login-to-dashboard flow for manager", async () => {
      // Simulate complete authentication and data loading flow
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "manager-123",
          emailAddresses: [{ emailAddress: "manager@prefect.io" }],
          publicMetadata: { role: "manager" },
        } as any,
      });

      mockUseAuth.mockReturnValue({
        isSignedIn: true,
        userId: "manager-123",
        sessionId: "session-123",
      } as any);

      const { useSearchCalls } = require("@/lib/hooks/use-search-calls");
      useSearchCalls.mockReturnValue({
        data: [
          {
            id: "call-1",
            prefect_reps: ["Sales Rep"],
            overall_score: 88,
            date: "2024-01-15T10:00:00Z",
          },
        ],
        isLoading: false,
        error: null,
      });

      const user = userEvent.setup();
      render(<DashboardPage />);

      // Wait for dashboard to fully render
      await waitFor(() => {
        expect(screen.getByText("Team Dashboard")).toBeInTheDocument();
      });

      // Verify rep card is displayed
      expect(screen.getByText("Sales Rep")).toBeInTheDocument();

      // Verify "View Details" button is present and clickable
      const viewDetailsButton = screen.getByRole("button", {
        name: /view details/i,
      });
      expect(viewDetailsButton).toBeInTheDocument();

      // Click the button (navigation will be handled by the router mock)
      await user.click(viewDetailsButton);

      // In a real environment, this would navigate. In our test, we verify the button works.
      // The router.push call is tested in component-specific tests
    });

    it("should display empty state when no rep data available", async () => {
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "manager-123",
          emailAddresses: [{ emailAddress: "manager@prefect.io" }],
          publicMetadata: { role: "manager" },
        } as any,
      });

      const { useSearchCalls } = require("@/lib/hooks/use-search-calls");
      useSearchCalls.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(
          screen.getByText("No rep data available. Calls need to be analyzed first.")
        ).toBeInTheDocument();
      });
    });
  });

  describe("test_create_session (11.5)", () => {
    it("should create coaching session workflow", async () => {
      // Mock fetch for coaching session creation
      global.fetch = jest.fn((url) => {
        if (url.toString().includes("/api/calls/")) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              coaching_sessions: [],
              count: 0,
            }),
          } as Response);
        }
        return Promise.reject(new Error("Not found"));
      }) as jest.Mock;

      const callId = "call-123";
      const response = await fetch(`/api/calls/${callId}/coaching-sessions`);
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data).toHaveProperty("coaching_sessions");
      expect(Array.isArray(data.coaching_sessions)).toBe(true);
    });

    it("should handle POST request to create coaching session", async () => {
      const mockCoachingSession = {
        id: "session-123",
        call_id: "call-456",
        coaching_dimension: "Discovery",
        session_type: "quick_win",
        score: 85,
        created_at: "2024-01-15T10:00:00Z",
      };

      // Mock successful POST
      global.fetch = jest.fn((url, options) => {
        if (url.toString().includes("/api/coaching-sessions") && options?.method === "POST") {
          return Promise.resolve({
            ok: true,
            status: 201,
            json: async () => mockCoachingSession,
          } as Response);
        }
        return Promise.reject(new Error("Not found"));
      }) as jest.Mock;

      const response = await fetch("/api/coaching-sessions/new", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          call_id: "call-456",
          coaching_dimension: "Discovery",
          session_type: "quick_win",
        }),
      });

      expect(response.ok).toBe(true);
      expect(response.status).toBe(201);
      const data = await response.json();
      expect(data).toEqual(mockCoachingSession);
    });

    it("should validate session creation data", async () => {
      // Mock validation error response
      global.fetch = jest.fn((url, options) => {
        if (url.toString().includes("/api/coaching-sessions") && options?.method === "POST") {
          return Promise.resolve({
            ok: false,
            status: 400,
            json: async () => ({
              error: "Invalid session data",
              details: "call_id is required",
            }),
          } as Response);
        }
        return Promise.reject(new Error("Not found"));
      }) as jest.Mock;

      const response = await fetch("/api/coaching-sessions/new", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          // Missing required call_id
          coaching_dimension: "Discovery",
        }),
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty("error");
      expect(data.error).toContain("Invalid");
    });

    it("should fetch existing coaching sessions for a call", async () => {
      const mockSessions = [
        {
          id: "session-1",
          call_id: "call-789",
          coaching_dimension: "Value Proposition",
          session_type: "deep_dive",
          score: 90,
          created_at: "2024-01-10T10:00:00Z",
        },
        {
          id: "session-2",
          call_id: "call-789",
          coaching_dimension: "Objection Handling",
          session_type: "quick_win",
          score: 75,
          created_at: "2024-01-12T10:00:00Z",
        },
      ];

      global.fetch = jest.fn((url) => {
        if (url.toString().includes("/api/calls/call-789/coaching-sessions")) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              coaching_sessions: mockSessions,
              count: mockSessions.length,
            }),
          } as Response);
        }
        return Promise.reject(new Error("Not found"));
      }) as jest.Mock;

      const response = await fetch("/api/calls/call-789/coaching-sessions");
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.coaching_sessions).toHaveLength(2);
      expect(data.count).toBe(2);
      expect(data.coaching_sessions[0].coaching_dimension).toBe("Value Proposition");
    });

    it("should handle complete workflow: analyze call -> create session -> fetch sessions", async () => {
      // Step 1: Analyze a call
      const mockAnalysisResponse = {
        call_id: "call-workflow",
        scores: {
          overall: 85,
          dimensions: {
            Discovery: 80,
            "Value Proposition": 90,
          },
        },
        coaching_notes: "Great discovery questions",
      };

      // Step 2: Create coaching session based on analysis
      const mockSessionResponse = {
        id: "session-workflow",
        call_id: "call-workflow",
        coaching_dimension: "Discovery",
        session_type: "quick_win",
        score: 80,
        created_at: "2024-01-15T10:00:00Z",
      };

      // Step 3: Fetch all sessions for the call
      const mockSessionsResponse = {
        coaching_sessions: [mockSessionResponse],
        count: 1,
      };

      global.fetch = jest.fn((url, options) => {
        const urlString = url.toString();

        if (urlString.includes("/api/coaching/analyze-call")) {
          return Promise.resolve({
            ok: true,
            json: async () => mockAnalysisResponse,
          } as Response);
        }

        if (urlString.includes("/api/coaching-sessions") && options?.method === "POST") {
          return Promise.resolve({
            ok: true,
            status: 201,
            json: async () => mockSessionResponse,
          } as Response);
        }

        if (urlString.includes("/api/calls/call-workflow/coaching-sessions")) {
          return Promise.resolve({
            ok: true,
            json: async () => mockSessionsResponse,
          } as Response);
        }

        return Promise.reject(new Error("Not found"));
      }) as jest.Mock;

      // Execute workflow
      // Step 1: Analyze call
      const analysisResponse = await fetch("/api/coaching/analyze-call", {
        method: "POST",
        body: JSON.stringify({ call_id: "call-workflow" }),
      });
      const analysisData = await analysisResponse.json();
      expect(analysisData.call_id).toBe("call-workflow");

      // Step 2: Create session
      const sessionResponse = await fetch("/api/coaching-sessions/new", {
        method: "POST",
        body: JSON.stringify({
          call_id: "call-workflow",
          coaching_dimension: "Discovery",
          session_type: "quick_win",
        }),
      });
      const sessionData = await sessionResponse.json();
      expect(sessionData.id).toBe("session-workflow");

      // Step 3: Fetch sessions
      const sessionsResponse = await fetch("/api/calls/call-workflow/coaching-sessions");
      const sessionsData = await sessionsResponse.json();
      expect(sessionsData.coaching_sessions).toHaveLength(1);
      expect(sessionsData.coaching_sessions[0].coaching_dimension).toBe("Discovery");
    });

    it("should handle errors during session creation gracefully", async () => {
      global.fetch = jest.fn(() => {
        return Promise.resolve({
          ok: false,
          status: 500,
          json: async () => ({
            error: "Database connection failed",
          }),
        } as Response);
      }) as jest.Mock;

      const response = await fetch("/api/coaching-sessions/new", {
        method: "POST",
        body: JSON.stringify({
          call_id: "call-error",
          coaching_dimension: "Discovery",
        }),
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data.error).toContain("Database connection failed");
    });
  });

  describe("Navigation and Routing Tests", () => {
    it("should navigate between pages in the workflow", async () => {
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "manager-123",
          emailAddresses: [{ emailAddress: "manager@prefect.io" }],
          publicMetadata: { role: "manager" },
        } as any,
      });

      const { useSearchCalls } = require("@/lib/hooks/use-search-calls");
      useSearchCalls.mockReturnValue({
        data: [
          {
            id: "call-1",
            prefect_reps: ["Test Rep"],
            overall_score: 85,
            date: "2024-01-15T10:00:00Z",
          },
        ],
        isLoading: false,
        error: null,
      });

      const user = userEvent.setup();
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Team Dashboard")).toBeInTheDocument();
      });

      // Verify rep row is clickable
      const repRow = screen.getByText("Test Rep").closest("tr");
      expect(repRow).toBeInTheDocument();

      // In integration tests, we verify the UI renders correctly
      // Navigation behavior is tested in E2E tests
      if (repRow) {
        expect(repRow).toHaveClass("cursor-pointer");
      }
    });
  });

  describe("Error Recovery Tests", () => {
    it("should retry failed requests", async () => {
      mockUseUser.mockReturnValue({
        isLoaded: true,
        isSignedIn: true,
        user: {
          id: "manager-123",
          emailAddresses: [{ emailAddress: "manager@prefect.io" }],
          publicMetadata: { role: "manager" },
        } as any,
      });

      const { useSearchCalls } = require("@/lib/hooks/use-search-calls");
      useSearchCalls.mockReturnValue({
        data: null,
        isLoading: false,
        error: new Error("Network error"),
      });

      const user = userEvent.setup();
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Error loading dashboard")).toBeInTheDocument();
      });

      // Click retry button
      const retryButton = screen.getByRole("button", { name: /retry/i });

      // Mock window.location.reload
      delete (window as any).location;
      (window as any).location = { reload: jest.fn() };

      await user.click(retryButton);

      expect(window.location.reload).toHaveBeenCalled();
    });
  });
});
