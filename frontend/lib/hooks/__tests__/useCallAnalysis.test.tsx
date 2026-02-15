import { renderHook, waitFor, act } from "@testing-library/react";
import { SWRConfig } from "swr";
import { useCallAnalysis, useCallAnalysisMutation } from "../useCallAnalysis";
import type { AnalyzeCallResponse } from "@/types/coaching";

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

// Custom fetcher for tests
async function testFetcher(url: string) {
  const response = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error: any = new Error("An error occurred while fetching the data.");
    error.status = response.status;

    try {
      const errorData = await response.json();
      error.info = errorData;
      error.message = errorData.error || errorData.message || error.message;
    } catch {
      // If error response is not JSON, use default message
    }

    throw error;
  }

  return response.json();
}

// Test data
const mockAnalysisResponse: AnalyzeCallResponse = {
  call_metadata: {
    id: "call-123",
    title: "Discovery Call - Acme Corp",
    date: "2024-01-15T10:00:00Z",
    duration_seconds: 1800,
    call_type: "discovery",
    product: "prefect",
    participants: [
      {
        name: "Test Rep",
        email: "rep@example.com",
        role: "AE",
        is_internal: true,
        talk_time_seconds: 900,
      },
    ],
    gong_url: "https://gong.io/call/123",
    recording_url: null,
  },
  rep_analyzed: {
    email: "rep@example.com",
    name: "Test Rep",
    role: "AE",
  },
  scores: {
    overall: 85,
    discovery: 80,
    product_knowledge: 90,
    objection_handling: 85,
    engagement: 80,
  },
  strengths: ["Strong opening", "Clear value prop"],
  areas_for_improvement: ["Better discovery questions", "More confident close"],
  specific_examples: {
    good: ["Great product demo", "Strong objection handling"],
    needs_work: ["Discovery questions need more depth"],
  },
  action_items: ["Follow up on pricing questions"],
  dimension_details: {
    discovery: {
      score: 80,
      strengths: ["Asked good qualifying questions"],
      areas_for_improvement: ["Could dig deeper on pain points"],
    },
  },
  comparison_to_average: [
    {
      metric: "overall",
      rep_score: 85,
      team_average: 78,
      difference: 7,
      percentile: 75,
      sample_size: 50,
    },
  ],
  transcript: null,
};

// Wrapper component for SWR provider
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0, fetcher: testFetcher }}>
    {children}
  </SWRConfig>
);

// Mock window.location for URL building
Object.defineProperty(window, "location", {
  value: {
    origin: "http://localhost:3000",
  },
  writable: true,
});

describe("useCallAnalysis", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
  });

  it("should fetch call analysis successfully", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response);

    const { result } = renderHook(() => useCallAnalysis("call-123"), { wrapper });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();

    await waitFor(() => {
      expect(result.current.data).toEqual(mockAnalysisResponse);
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeUndefined();
  });

  it("should handle null callId gracefully", () => {
    const { result } = renderHook(() => useCallAnalysis(null), { wrapper });

    // When callId is null, the query is disabled - isLoading is false
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
  });

  it("should handle undefined callId gracefully", () => {
    const { result } = renderHook(() => useCallAnalysis(undefined), { wrapper });

    // When callId is undefined, the query is disabled - isLoading is false
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
  });

  it("should not fetch when enabled is false", () => {
    const { result } = renderHook(() => useCallAnalysis("call-123", { enabled: false }), {
      wrapper,
    });

    expect(result.current.isLoading).toBe(false);
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it("should build correct URL with options", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response);

    renderHook(
      () =>
        useCallAnalysis("call-123", {
          dimensions: ["Discovery", "Value Proposition"],
          use_cache: false,
          include_transcript_snippets: false,
          force_reanalysis: true,
        }),
      { wrapper }
    );

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("call_id=call-123"),
        expect.any(Object)
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("dimensions=Discovery%2CValue+Proposition"),
        expect.any(Object)
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("use_cache=false"),
        expect.any(Object)
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("include_transcript_snippets=false"),
        expect.any(Object)
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("force_reanalysis=true"),
        expect.any(Object)
      );
    });
  });

  it("should handle fetch errors", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useCallAnalysis("call-123"), { wrapper });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
  });
});

describe("useCallAnalysisMutation", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
  });

  it("should trigger analysis successfully", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response);

    const { result } = renderHook(() => useCallAnalysisMutation(), { wrapper });

    expect(result.current.isMutating).toBe(false);

    let data;
    await act(async () => {
      data = await result.current.trigger({
        call_id: "call-123",
        force_reanalysis: true,
      });
    });

    expect(result.current.isMutating).toBe(false);
    expect(data).toEqual(mockAnalysisResponse);
    expect(result.current.data).toEqual(mockAnalysisResponse);
  });

  it("should call onSuccess callback", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response);

    const onSuccess = jest.fn();
    const { result } = renderHook(() => useCallAnalysisMutation({ onSuccess }), { wrapper });

    await act(async () => {
      await result.current.trigger({ call_id: "call-123" });
    });

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });

    // Verify onSuccess was called with the response data as first argument
    expect(onSuccess.mock.calls[0][0]).toEqual(mockAnalysisResponse);
  });

  it("should call onError callback", async () => {
    const errorResponse = {
      error: "Analysis failed",
      message: "Invalid call ID",
    };

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => errorResponse,
    } as Response);

    const onError = jest.fn();
    const { result } = renderHook(() => useCallAnalysisMutation({ onError }), { wrapper });

    await act(async () => {
      try {
        await result.current.trigger({ call_id: "invalid-id" });
      } catch (error) {
        // Expected to throw
      }
    });

    await waitFor(() => {
      expect(onError).toHaveBeenCalled();
    });

    const errorArg = onError.mock.calls[0][0];
    // The error message comes from the error response's error field or message field
    expect(errorArg.message).toMatch(/Analysis failed|Invalid call ID/);
  });

  it("should handle non-JSON error responses", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("Not JSON");
      },
    } as Response);

    const { result } = renderHook(() => useCallAnalysisMutation(), { wrapper });

    await act(async () => {
      try {
        await result.current.trigger({ call_id: "call-123" });
      } catch (error) {
        expect((error as Error).message).toBe("Failed to analyze call");
      }
    });
  });

  it("should reset mutation state", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response);

    const { result } = renderHook(() => useCallAnalysisMutation(), { wrapper });

    await act(async () => {
      await result.current.trigger({ call_id: "call-123" });
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockAnalysisResponse);
    });

    act(() => {
      result.current.reset();
    });

    await waitFor(() => {
      expect(result.current.data).toBeUndefined();
    });
    expect(result.current.error).toBeUndefined();
  });
});
