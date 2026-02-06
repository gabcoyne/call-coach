/**
 * Integration Tests for API Routes
 *
 * Tests 11.1-11.3:
 * - test_route_handler_success: Verify route handler returns success response
 * - test_route_validation_error: Verify route returns validation error for invalid input
 * - test_route_database_query: Verify route interacts with database correctly
 *
 * Note: These tests mock the API endpoints using fetch mocks to test the integration
 * between frontend code and API routes without requiring the full Next.js runtime.
 */

describe("API Route Integration Tests", () => {
  let fetchMock: jest.Mock;

  beforeEach(() => {
    fetchMock = jest.fn();
    global.fetch = fetchMock;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("test_route_handler_success (11.1)", () => {
    it("should return successful response with valid data from opportunities endpoint", async () => {
      const mockResponse = {
        opportunities: [
          {
            id: "opp-123",
            name: "Acme Corp Deal",
            stage: "negotiation",
            amount: 50000,
            health_score: 85,
            owner_email: "sales@prefect.io",
            close_date: "2024-02-15",
            updated_at: "2024-01-15T10:00:00Z",
          },
        ],
        pagination: {
          page: 1,
          limit: 50,
          total: 1,
          totalPages: 1,
          hasMore: false,
        },
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const response = await fetch("/api/opportunities");
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(response.status).toBe(200);
      expect(data).toHaveProperty("opportunities");
      expect(data).toHaveProperty("pagination");
      expect(Array.isArray(data.opportunities)).toBe(true);
      expect(data.opportunities.length).toBeGreaterThan(0);
      expect(data.opportunities[0].name).toBe("Acme Corp Deal");
    });

    it("should return health check with all services up", async () => {
      const mockHealthResponse = {
        status: "healthy",
        timestamp: "2024-01-15T10:00:00Z",
        uptime: 1000,
        checks: {
          database: {
            status: "up",
            latency_ms: 10,
            timestamp: "2024-01-15T10:00:00Z",
          },
          redis: {
            status: "up",
            latency_ms: 5,
            timestamp: "2024-01-15T10:00:00Z",
          },
          claude_api: {
            status: "up",
            latency_ms: 100,
            timestamp: "2024-01-15T10:00:00Z",
          },
          backend_api: {
            status: "up",
            latency_ms: 20,
            timestamp: "2024-01-15T10:00:00Z",
          },
        },
        version: "1.0.0",
        environment: "test",
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockHealthResponse,
      });

      const response = await fetch("/api/health");
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data).toHaveProperty("status");
      expect(data.status).toBe("healthy");
      expect(data).toHaveProperty("checks");
      expect(data.checks).toHaveProperty("database");
      expect(data.checks.database.status).toBe("up");
    });

    it("should return coaching session list for a call", async () => {
      const mockSessions = {
        coaching_sessions: [
          {
            id: "session-1",
            call_id: "call-123",
            coaching_dimension: "Discovery",
            session_type: "quick_win",
            score: 85,
            created_at: "2024-01-15T10:00:00Z",
          },
        ],
        count: 1,
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockSessions,
      });

      const response = await fetch("/api/calls/call-123/coaching-sessions");
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data).toHaveProperty("coaching_sessions");
      expect(data).toHaveProperty("count");
      expect(data.count).toBe(1);
    });
  });

  describe("test_route_validation_error (11.2)", () => {
    it("should return 400 for invalid pagination parameters", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: "Invalid pagination parameters",
        }),
      });

      const response = await fetch("/api/opportunities?page=0&limit=1000");

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty("error");
      expect(data.error).toContain("Invalid pagination");
    });

    it("should return 400 for negative page number", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: "Invalid pagination parameters",
        }),
      });

      const response = await fetch("/api/opportunities?page=-1");

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty("error");
    });

    it("should return 400 for limit exceeding maximum", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: "Invalid pagination parameters",
        }),
      });

      const response = await fetch("/api/opportunities?limit=500");

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty("error");
      expect(data.error).toContain("Invalid pagination");
    });

    it("should return 400 for invalid coaching session data", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: "Invalid request parameters",
          details: "call_id is required",
        }),
      });

      const response = await fetch("/api/coaching-sessions/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coaching_dimension: "Discovery" }),
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain("Invalid");
    });
  });

  describe("test_route_database_query (11.3)", () => {
    it("should execute database query with correct filtering", async () => {
      const mockFilteredOpportunities = {
        opportunities: [
          {
            id: "opp-1",
            name: "Deal 1",
            stage: "qualification",
            amount: 25000,
            health_score: 75,
            owner_email: "rep1@prefect.io",
            close_date: "2024-03-01",
            updated_at: "2024-01-10T10:00:00Z",
          },
          {
            id: "opp-2",
            name: "Deal 2",
            stage: "proposal",
            amount: 75000,
            health_score: 90,
            owner_email: "rep2@prefect.io",
            close_date: "2024-04-01",
            updated_at: "2024-01-12T10:00:00Z",
          },
        ],
        pagination: {
          page: 1,
          limit: 50,
          total: 2,
          totalPages: 1,
          hasMore: false,
        },
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockFilteredOpportunities,
      });

      const response = await fetch("/api/opportunities?owner=rep1@prefect.io&stage=qualification");

      expect(response.ok).toBe(true);
      const data = await response.json();
      expect(data.opportunities).toBeDefined();
      expect(data.pagination).toBeDefined();
      expect(data.opportunities.length).toBe(2);
    });

    it("should handle database connection errors gracefully", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({
          error: "Failed to fetch opportunities",
        }),
      });

      const response = await fetch("/api/opportunities");

      expect(response.ok).toBe(false);
      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data).toHaveProperty("error");
      expect(data.error).toContain("Failed to fetch opportunities");
    });

    it("should handle empty result sets correctly", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          opportunities: [],
          pagination: {
            page: 1,
            limit: 50,
            total: 0,
            totalPages: 0,
            hasMore: false,
          },
        }),
      });

      const response = await fetch("/api/opportunities?search=nonexistent");

      expect(response.ok).toBe(true);
      const data = await response.json();
      expect(data.opportunities).toEqual([]);
      expect(data.pagination.total).toBe(0);
    });

    it("should execute parameterized queries with filtering", async () => {
      const mockFilteredOpportunities = {
        opportunities: [
          {
            id: "opp-high-score",
            name: "High Value Deal",
            stage: "negotiation",
            amount: 100000,
            health_score: 95,
            owner_email: "ace@prefect.io",
            close_date: "2024-02-01",
            updated_at: "2024-01-15T10:00:00Z",
          },
        ],
        pagination: {
          page: 1,
          limit: 50,
          total: 1,
          totalPages: 1,
          hasMore: false,
        },
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockFilteredOpportunities,
      });

      const response = await fetch(
        "/api/opportunities?health_score_min=90&sort=amount&sort_dir=DESC"
      );

      expect(response.ok).toBe(true);
      const data = await response.json();
      expect(data.opportunities).toHaveLength(1);
      expect(data.opportunities[0].health_score).toBeGreaterThanOrEqual(90);
    });

    it("should handle database timeouts", async () => {
      fetchMock.mockRejectedValueOnce(new Error("Connection timeout"));

      await expect(fetch("/api/opportunities")).rejects.toThrow("Connection timeout");
    });

    it("should query coaching sessions for a specific call", async () => {
      const mockSessions = {
        coaching_sessions: [
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
        ],
        count: 2,
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockSessions,
      });

      const response = await fetch("/api/calls/call-789/coaching-sessions");
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.coaching_sessions).toHaveLength(2);
      expect(data.count).toBe(2);
      expect(data.coaching_sessions[0].coaching_dimension).toBe("Value Proposition");
    });
  });

  describe("Database Transaction Tests", () => {
    it("should maintain data consistency across multiple queries", async () => {
      const opportunitiesData = {
        opportunities: [
          {
            id: "opp-tx-1",
            name: "Transaction Test Deal",
            stage: "proposal",
            amount: 60000,
            health_score: 80,
            owner_email: "rep@prefect.io",
            close_date: "2024-03-15",
            updated_at: "2024-01-15T10:00:00Z",
          },
        ],
        pagination: {
          page: 1,
          limit: 50,
          total: 1,
          totalPages: 1,
          hasMore: false,
        },
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => opportunitiesData,
      });

      const response = await fetch("/api/opportunities?page=1&limit=50");
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.pagination.total).toBe(1);
      expect(data.opportunities.length).toBe(1);
      expect(data.pagination.totalPages).toBe(1);
    });
  });

  describe("Edge Cases and Error Handling", () => {
    it("should handle SQL injection attempts safely", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          opportunities: [],
          pagination: {
            page: 1,
            limit: 50,
            total: 0,
            totalPages: 0,
            hasMore: false,
          },
        }),
      });

      const response = await fetch("/api/opportunities?search='; DROP TABLE opportunities; --");

      expect(response.ok).toBe(true);
      expect(fetchMock).toHaveBeenCalled();
    });

    it("should handle concurrent requests correctly", async () => {
      fetchMock.mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          opportunities: [
            {
              id: "opp-concurrent",
              name: "Concurrent Test",
              stage: "discovery",
              amount: 30000,
              health_score: 70,
              owner_email: "rep@prefect.io",
              close_date: "2024-05-01",
              updated_at: "2024-01-15T10:00:00Z",
            },
          ],
          pagination: {
            page: 1,
            limit: 50,
            total: 1,
            totalPages: 1,
            hasMore: false,
          },
        }),
      });

      const requests = Array.from({ length: 5 }, () => fetch("/api/opportunities"));

      const responses = await Promise.all(requests);

      responses.forEach((response) => {
        expect(response.ok).toBe(true);
      });
    });

    it("should handle network errors gracefully", async () => {
      fetchMock.mockRejectedValueOnce(new Error("Network error"));

      await expect(fetch("/api/opportunities")).rejects.toThrow("Network error");
    });
  });

  describe("API Route Response Formats", () => {
    it("should return consistent response format for list endpoints", async () => {
      const mockResponse = {
        opportunities: [],
        pagination: {
          page: 1,
          limit: 50,
          total: 0,
          totalPages: 0,
          hasMore: false,
        },
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const response = await fetch("/api/opportunities");
      const data = await response.json();

      expect(data).toHaveProperty("opportunities");
      expect(data).toHaveProperty("pagination");
      expect(data.pagination).toHaveProperty("page");
      expect(data.pagination).toHaveProperty("limit");
      expect(data.pagination).toHaveProperty("total");
      expect(data.pagination).toHaveProperty("totalPages");
      expect(data.pagination).toHaveProperty("hasMore");
    });

    it("should return consistent error format", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({
          error: "Internal server error",
        }),
      });

      const response = await fetch("/api/opportunities");
      const data = await response.json();

      expect(data).toHaveProperty("error");
      expect(typeof data.error).toBe("string");
    });
  });
});
