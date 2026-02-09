import { renderHook, waitFor, act } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { useRepInsights, useMultipleRepInsights } from '../useRepInsights'
import type { RepInsightsResponse } from '@/types/coaching'

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

// Custom fetcher for tests
async function testFetcher(url: string) {
  const response = await fetch(url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const error: any = new Error('An error occurred while fetching the data.')
    error.status = response.status

    try {
      const errorData = await response.json()
      error.info = errorData
      error.message = errorData.error || errorData.message || error.message
    } catch {
      // If error response is not JSON, use default message
    }

    throw error
  }

  return response.json()
}

// Test data
const mockRepInsightsResponse: RepInsightsResponse = {
  rep_info: {
    name: 'Test Rep',
    email: 'rep@example.com',
    role: 'AE',
    calls_analyzed: 25,
    date_range: {
      start: '2024-01-01',
      end: '2024-01-31',
      period: 'last_30_days',
    },
    product_filter: null,
  },
  score_trends: {
    overall: {
      dates: ['2024-01-01', '2024-01-15', '2024-01-31'],
      scores: [75, 80, 85],
      call_counts: [5, 10, 10],
    },
    product_knowledge: {
      dates: ['2024-01-01', '2024-01-15', '2024-01-31'],
      scores: [70, 75, 80],
      call_counts: [5, 10, 10],
    },
  },
  skill_gaps: [
    {
      area: 'Discovery',
      current_score: 65,
      target_score: 85,
      gap: 20,
      sample_size: 15,
      priority: 'high',
    },
    {
      area: 'Objection Handling',
      current_score: 75,
      target_score: 85,
      gap: 10,
      sample_size: 20,
      priority: 'medium',
    },
  ],
  improvement_areas: [
    {
      area: 'Product Knowledge',
      recent_score: 80,
      older_score: 70,
      change: 10,
      trend: 'improving',
    },
  ],
  recent_wins: [
    'Closed deal with Fortune 500 client',
    'Perfect discovery call score',
  ],
  coaching_plan: 'Focus on discovery questions and active listening techniques',
}

// Wrapper component for SWR provider
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0, fetcher: testFetcher }}>
    {children}
  </SWRConfig>
)

// Mock window.location for URL building
Object.defineProperty(window, 'location', {
  value: {
    origin: 'http://localhost:3000',
  },
  writable: true,
})

describe('useRepInsights', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  describe('Task 9.1: Initial State', () => {
    it('should return correct initial state with valid email', () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      const { result } = renderHook(
        () => useRepInsights('rep@example.com'),
        { wrapper }
      )

      // Initial state before data loads
      expect(result.current.isLoading).toBe(true)
      expect(result.current.data).toBeUndefined()
      expect(result.current.error).toBeUndefined()
      expect(result.current.mutate).toBeInstanceOf(Function)
    })

    it('should not fetch when repEmail is null', () => {
      const { result } = renderHook(() => useRepInsights(null), { wrapper })

      // Note: isLoading will be true because enabled defaults to true,
      // but no fetch will actually happen because url is null
      expect(result.current.isLoading).toBe(true)
      expect(result.current.data).toBeUndefined()
      expect(result.current.error).toBeUndefined()
      expect(mockFetch).not.toHaveBeenCalled()
    })

    it('should not fetch when repEmail is undefined', () => {
      const { result } = renderHook(() => useRepInsights(undefined), { wrapper })

      // Note: isLoading will be true because enabled defaults to true,
      // but no fetch will actually happen because url is null
      expect(result.current.isLoading).toBe(true)
      expect(result.current.data).toBeUndefined()
      expect(result.current.error).toBeUndefined()
      expect(mockFetch).not.toHaveBeenCalled()
    })

    it('should not load when enabled is false', () => {
      const { result } = renderHook(
        () => useRepInsights('rep@example.com', { enabled: false }),
        { wrapper }
      )

      expect(result.current.isLoading).toBe(false)
      expect(result.current.data).toBeUndefined()
      expect(mockFetch).not.toHaveBeenCalled()
    })
  })

  describe('Task 9.2: State Updates', () => {
    it('should fetch and update state with rep insights successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      const { result } = renderHook(
        () => useRepInsights('rep@example.com'),
        { wrapper }
      )

      expect(result.current.isLoading).toBe(true)

      await waitFor(() => {
        expect(result.current.data).toEqual(mockRepInsightsResponse)
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeUndefined()
      expect(result.current.data?.rep_info.email).toBe('rep@example.com')
      expect(result.current.data?.skill_gaps).toHaveLength(2)
    })

    it('should update when options change', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      const { result, rerender } = renderHook(
        ({ options }) => useRepInsights('rep@example.com', options),
        {
          wrapper,
          initialProps: { options: { time_period: 'last_30_days' as const } },
        }
      )

      await waitFor(() => {
        expect(result.current.data).toEqual(mockRepInsightsResponse)
      })

      // Clear mock and change time period
      mockFetch.mockClear()
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ...mockRepInsightsResponse,
          rep_info: {
            ...mockRepInsightsResponse.rep_info,
            date_range: {
              ...mockRepInsightsResponse.rep_info.date_range,
              period: 'last_7_days',
            },
          },
        }),
      } as Response)

      rerender({ options: { time_period: 'last_7_days' as const } })

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled()
      })
    })

    it('should call mutate to refresh data', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      const { result } = renderHook(
        () => useRepInsights('rep@example.com'),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.data).toEqual(mockRepInsightsResponse)
      })

      mockFetch.mockClear()
      const updatedResponse = {
        ...mockRepInsightsResponse,
        rep_info: {
          ...mockRepInsightsResponse.rep_info,
          calls_analyzed: 30,
        },
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => updatedResponse,
      } as Response)

      await act(async () => {
        await result.current.mutate()
      })

      await waitFor(() => {
        expect(result.current.data?.rep_info.calls_analyzed).toBe(30)
      })
    })
  })

  describe('Task 9.4: Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(
        () => useRepInsights('rep@example.com'),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.error).toBeDefined()
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.data).toBeUndefined()
      expect(result.current.error?.message).toBe('Network error')
    })

    it('should handle API error responses', async () => {
      const errorResponse = {
        error: 'Rep not found',
        message: 'No data available for this rep',
      }

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => errorResponse,
      } as Response)

      const { result } = renderHook(
        () => useRepInsights('unknown@example.com'),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.error).toBeDefined()
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.data).toBeUndefined()
    })

    it('should handle malformed JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON')
        },
      } as Response)

      const { result } = renderHook(
        () => useRepInsights('rep@example.com'),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.error).toBeDefined()
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.data).toBeUndefined()
    })

    it('should recover from error on retry', async () => {
      // First call fails
      mockFetch.mockRejectedValueOnce(new Error('Temporary error'))

      const { result } = renderHook(
        () => useRepInsights('rep@example.com'),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.error).toBeDefined()
      })

      // Retry with successful response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      await act(async () => {
        await result.current.mutate()
      })

      await waitFor(() => {
        expect(result.current.data).toEqual(mockRepInsightsResponse)
      })

      expect(result.current.error).toBeUndefined()
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('URL Building and Options', () => {
    it('should build correct URL with default options', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      renderHook(() => useRepInsights('rep@example.com'), { wrapper })

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('rep_email=rep%40example.com'),
          expect.any(Object)
        )
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('time_period=last_30_days'),
          expect.any(Object)
        )
      })
    })

    it('should build URL with custom time period', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      renderHook(
        () => useRepInsights('rep@example.com', { time_period: 'last_7_days' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('time_period=last_7_days'),
          expect.any(Object)
        )
      })
    })

    it('should build URL with product filter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      renderHook(
        () =>
          useRepInsights('rep@example.com', { product_filter: 'prefect' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('product_filter=prefect'),
          expect.any(Object)
        )
      })
    })

    it('should build URL with all options', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRepInsightsResponse,
      } as Response)

      renderHook(
        () =>
          useRepInsights('rep@example.com', {
            time_period: 'last_quarter',
            product_filter: 'horizon',
          }),
        { wrapper }
      )

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('rep_email=rep%40example.com'),
          expect.any(Object)
        )
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('time_period=last_quarter'),
          expect.any(Object)
        )
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('product_filter=horizon'),
          expect.any(Object)
        )
      })
    })
  })
})

describe('useMultipleRepInsights', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('should fetch insights for multiple reps', async () => {
    const rep1Response = { ...mockRepInsightsResponse }
    const rep2Response = {
      ...mockRepInsightsResponse,
      rep_info: {
        ...mockRepInsightsResponse.rep_info,
        email: 'rep2@example.com',
        name: 'Test Rep 2',
      },
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => rep1Response,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => rep2Response,
      } as Response)

    const { result } = renderHook(
      () => useMultipleRepInsights(['rep1@example.com', 'rep2@example.com']),
      { wrapper }
    )

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.data).toBeDefined()
    })

    expect(result.current.isLoading).toBe(false)
    expect(Object.keys(result.current.data)).toHaveLength(2)
    expect(result.current.data['rep1@example.com']).toEqual(rep1Response)
    expect(result.current.data['rep2@example.com']).toEqual(rep2Response)
  })

  it('should handle empty rep emails array', () => {
    const { result } = renderHook(() => useMultipleRepInsights([]), { wrapper })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toEqual({})
    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('should handle error when fetching multiple reps', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Server error' }),
    } as Response)

    const { result } = renderHook(
      () => useMultipleRepInsights(['rep1@example.com', 'rep2@example.com']),
      { wrapper }
    )

    await waitFor(() => {
      expect(result.current.error).toBeDefined()
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toEqual({})
  })

  it('should call mutate to refresh all reps data', async () => {
    const rep1Response = { ...mockRepInsightsResponse }
    const rep2Response = {
      ...mockRepInsightsResponse,
      rep_info: {
        ...mockRepInsightsResponse.rep_info,
        email: 'rep2@example.com',
      },
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => rep1Response,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => rep2Response,
      } as Response)

    const { result } = renderHook(
      () => useMultipleRepInsights(['rep1@example.com', 'rep2@example.com']),
      { wrapper }
    )

    await waitFor(() => {
      expect(result.current.data).toBeDefined()
    })

    mockFetch.mockClear()
    const updatedRep1 = {
      ...rep1Response,
      rep_info: { ...rep1Response.rep_info, calls_analyzed: 50 },
    }
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => updatedRep1,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => rep2Response,
      } as Response)

    await act(async () => {
      await result.current.mutate()
    })

    await waitFor(() => {
      expect(result.current.data['rep1@example.com'].rep_info.calls_analyzed).toBe(
        50
      )
    })
  })
})
