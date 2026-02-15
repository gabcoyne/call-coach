import { NextRequest } from "next/server";

// Create mock for execAsync
const mockExecAsync = jest.fn();

// Mock util.promisify to return our mock
jest.mock("util", () => ({
  ...jest.requireActual("util"),
  promisify: () => mockExecAsync,
}));

// Import after mocking
import { POST, GET } from "../route";

describe("GET /api/cron/daily-sync", () => {
  it("should return cron job configuration", async () => {
    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "GET",
    });

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toMatchObject({
      job: "daily-gong-sync",
      schedule: "0 6 * * *",
      description: expect.any(String),
    });
  });
});

describe("POST /api/cron/daily-sync", () => {
  const mockCronSecret = "test-cron-secret-123";

  beforeEach(() => {
    jest.clearAllMocks();
    process.env.CRON_SECRET = mockCronSecret;
  });

  afterEach(() => {
    delete process.env.CRON_SECRET;
  });

  it("should reject unauthorized requests", async () => {
    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
      headers: {
        Authorization: "Bearer wrong-secret",
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(401);
    const data = await response.json();
    expect(data).toEqual({ error: "Unauthorized" });
  });

  it("should reject requests without authorization header", async () => {
    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
    });

    const response = await POST(request);

    expect(response.status).toBe(401);
  });

  it("should execute sync successfully with valid authorization", async () => {
    const mockStdout = JSON.stringify({
      status: "success",
      opportunities: { synced: 10, errors: 0 },
    });

    mockExecAsync.mockResolvedValue({ stdout: mockStdout, stderr: "" });

    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${mockCronSecret}`,
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toMatchObject({
      job: "daily-gong-sync",
      status: "success",
      output: expect.any(String),
    });
  });

  it("should handle sync failures gracefully", async () => {
    const mockError = new Error("Python script failed") as any;
    mockError.stdout = "Partial output";
    mockError.stderr = "Error details";

    mockExecAsync.mockRejectedValue(mockError);

    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${mockCronSecret}`,
      },
    });

    const response = await POST(request);

    // Should return 200 even on sync failure (job executed, sync failed)
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toMatchObject({
      job: "daily-gong-sync",
      status: "failed",
      error: expect.any(String),
    });
  });

  it("should allow requests in development without CRON_SECRET", async () => {
    delete process.env.CRON_SECRET;

    mockExecAsync.mockResolvedValue({ stdout: "Success", stderr: "" });

    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
    });

    const response = await POST(request);

    // Should allow in development (no CRON_SECRET configured)
    expect(response.status).toBe(200);
  });

  it("should execute with correct Python command", async () => {
    mockExecAsync.mockResolvedValue({ stdout: "Success", stderr: "" });

    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${mockCronSecret}`,
      },
    });

    await POST(request);

    expect(mockExecAsync).toHaveBeenCalledWith(
      expect.stringContaining("uv run python -m flows.daily_gong_sync"),
      expect.objectContaining({
        timeout: 280000,
        maxBuffer: 10 * 1024 * 1024,
      })
    );
  });

  it("should handle timeout errors", async () => {
    const timeoutError = new Error("Execution timed out") as any;
    timeoutError.code = "ETIMEDOUT";

    mockExecAsync.mockRejectedValue(timeoutError);

    const request = new NextRequest("http://localhost/api/cron/daily-sync", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${mockCronSecret}`,
      },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.status).toBe("failed");
    expect(data.error).toContain("timed out");
  });
});
