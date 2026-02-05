import { renderHook, waitFor } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { useCallAnalysis, useCallAnalysisMutation } from '../useCallAnalysis'
import type { AnalyzeCallResponse } from '@/types/coaching'

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

// Test data
const mockAnalysisResponse: AnalyzeCallResponse = {
  call_id: 'call-123',
  rep_analyzed: {
    email: 'rep@example.com',
    name: 'Test Rep',
  },
  scores: {
    overall: 85,
    dimensions: {
      Discovery: 80,
      'Value Proposition': 90,
      'Objection Handling': 85,
      'Call to Action': 80,
    },
  },
  strengths: ['Strong opening', 'Clear value prop'],
  areas_for_improvement: ['Better discovery questions', 'More confident close'],
  coaching_notes: 'Great overall performance',
  transcript_snippets: [],
  action_items: ['Follow up on pricing questions'],
  analyzed_at: '2024-01-15T10:00:00Z',
}

// Wrapper component for SWR provider
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
    {children}
  </SWRConfig>
)

describe('useCallAnalysis', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('should fetch call analysis successfully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response)

    const { result } = renderHook(() => useCallAnalysis('call-123'), { wrapper })

    expect(result.current.isLoading).toBe(true)
    expect(result.current.data).toBeUndefined()

    await waitFor(() => {
      expect(result.current.data).toEqual(mockAnalysisResponse)
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeUndefined()
  })

  it('should handle null callId gracefully', () => {
    const { result } = renderHook(() => useCallAnalysis(null), { wrapper })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeUndefined()
    expect(result.current.error).toBeUndefined()
  })

  it('should handle undefined callId gracefully', () => {
    const { result } = renderHook(() => useCallAnalysis(undefined), { wrapper })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeUndefined()
    expect(result.current.error).toBeUndefined()
  })

  it('should not fetch when enabled is false', () => {
    const { result } = renderHook(
      () => useCallAnalysis('call-123', { enabled: false }),
      { wrapper }
    )

    expect(result.current.isLoading).toBe(false)
    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('should build correct URL with options', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response)

    renderHook(
      () =>
        useCallAnalysis('call-123', {
          dimensions: ['Discovery', 'Value Proposition'],
          use_cache: false,
          include_transcript_snippets: false,
          force_reanalysis: true,
        }),
      { wrapper }
    )

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('call_id=call-123'),
        expect.any(Object)
      )
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('dimensions=Discovery%2CValue+Proposition'),
        expect.any(Object)
      )
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('use_cache=false'),
        expect.any(Object)
      )
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('include_transcript_snippets=false'),
        expect.any(Object)
      )
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('force_reanalysis=true'),
        expect.any(Object)
      )
    })
  })

  it('should handle fetch errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useCallAnalysis('call-123'), { wrapper })

    await waitFor(() => {
      expect(result.current.error).toBeDefined()
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.data).toBeUndefined()
  })
})

describe('useCallAnalysisMutation', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('should trigger analysis successfully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response)

    const { result } = renderHook(() => useCallAnalysisMutation(), { wrapper })

    expect(result.current.isMutating).toBe(false)

    const promise = result.current.trigger({
      call_id: 'call-123',
      force_reanalysis: true,
    })

    expect(result.current.isMutating).toBe(true)

    const data = await promise

    await waitFor(() => {
      expect(result.current.isMutating).toBe(false)
    })

    expect(data).toEqual(mockAnalysisResponse)
    expect(result.current.data).toEqual(mockAnalysisResponse)
  })

  it('should call onSuccess callback', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response)

    const onSuccess = jest.fn()
    const { result } = renderHook(() => useCallAnalysisMutation({ onSuccess }), { wrapper })

    await result.current.trigger({ call_id: 'call-123' })

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(mockAnalysisResponse)
    })
  })

  it('should call onError callback', async () => {
    const errorResponse = {
      error: 'Analysis failed',
      message: 'Invalid call ID',
    }

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => errorResponse,
    } as Response)

    const onError = jest.fn()
    const { result } = renderHook(() => useCallAnalysisMutation({ onError }), { wrapper })

    try {
      await result.current.trigger({ call_id: 'invalid-id' })
    } catch (error) {
      // Expected to throw
    }

    await waitFor(() => {
      expect(onError).toHaveBeenCalled()
    })

    const errorArg = onError.mock.calls[0][0]
    expect(errorArg.message).toBe('Invalid call ID')
  })

  it('should handle non-JSON error responses', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error('Not JSON')
      },
    } as Response)

    const { result } = renderHook(() => useCallAnalysisMutation(), { wrapper })

    try {
      await result.current.trigger({ call_id: 'call-123' })
    } catch (error) {
      expect((error as Error).message).toBe('Failed to analyze call')
    }
  })

  it('should reset mutation state', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalysisResponse,
    } as Response)

    const { result } = renderHook(() => useCallAnalysisMutation(), { wrapper })

    await result.current.trigger({ call_id: 'call-123' })

    await waitFor(() => {
      expect(result.current.data).toEqual(mockAnalysisResponse)
    })

    result.current.reset()

    expect(result.current.data).toBeUndefined()
    expect(result.current.error).toBeUndefined()
  })
})
