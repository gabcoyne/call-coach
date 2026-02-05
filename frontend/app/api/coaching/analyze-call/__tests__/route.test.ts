import { NextRequest } from 'next/server'
import { POST } from '../route'
import { mcpClient } from '@/lib/mcp-client'

// Mock dependencies
jest.mock('@/lib/mcp-client')
jest.mock('@/lib/auth-middleware', () => ({
  withAuth: (handler: any) => handler,
  apiError: (message: string, status: number) => ({
    json: jest.fn(),
    status,
    message,
  }),
  canAccessRepData: jest.fn(() => true),
}))
jest.mock('@/lib/rate-limit', () => ({
  checkRateLimit: jest.fn(() => ({
    allowed: true,
    limit: 100,
    remaining: 99,
    reset: Date.now() + 60000,
  })),
  rateLimitHeaders: jest.fn(() => ({})),
}))
jest.mock('@/lib/api-logger', () => ({
  logRequest: jest.fn(),
  logResponse: jest.fn(),
  logError: jest.fn(),
}))

const mockMcpClient = mcpClient as jest.Mocked<typeof mcpClient>

describe('POST /api/coaching/analyze-call', () => {
  const mockAuthContext = {
    userId: 'test-user-id',
    role: 'rep',
    email: 'test@example.com',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should analyze call successfully', async () => {
    const mockAnalysisResponse = {
      call_id: 'call-123',
      rep_analyzed: {
        email: 'test@example.com',
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
      strengths: ['Strong opening'],
      areas_for_improvement: ['Better close'],
      coaching_notes: 'Great job',
      transcript_snippets: [],
      action_items: ['Follow up'],
      analyzed_at: '2024-01-15T10:00:00Z',
    }

    mockMcpClient.analyzeCall.mockResolvedValue(mockAnalysisResponse)

    const request = new NextRequest('http://localhost/api/coaching/analyze-call', {
      method: 'POST',
      body: JSON.stringify({
        call_id: 'call-123',
        dimensions: ['Discovery', 'Value Proposition'],
      }),
    })

    const response = await POST(request, mockAuthContext)

    expect(response.status).toBe(200)
    const data = await response.json()
    expect(data).toEqual(mockAnalysisResponse)
    expect(mockMcpClient.analyzeCall).toHaveBeenCalledWith({
      call_id: 'call-123',
      dimensions: ['Discovery', 'Value Proposition'],
    })
  })

  it('should return 400 for invalid request body', async () => {
    const request = new NextRequest('http://localhost/api/coaching/analyze-call', {
      method: 'POST',
      body: JSON.stringify({
        // Missing call_id
        dimensions: ['Discovery'],
      }),
    })

    const response = await POST(request, mockAuthContext)

    expect(response.status).toBe(400)
  })

  it('should handle MCP client errors', async () => {
    mockMcpClient.analyzeCall.mockRejectedValue(new Error('MCP backend error'))

    const request = new NextRequest('http://localhost/api/coaching/analyze-call', {
      method: 'POST',
      body: JSON.stringify({
        call_id: 'call-123',
      }),
    })

    const response = await POST(request, mockAuthContext)

    expect(response.status).toBe(500)
  })
})
