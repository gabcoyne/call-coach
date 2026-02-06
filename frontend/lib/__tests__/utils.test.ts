import { cn } from '../utils'
import { getScoreColor, getPriorityColor, SCORE_COLORS, PRIORITY_COLORS } from '../colors'
import {
  buildApiUrl,
  isSWRError,
  getErrorMessage,
  isAuthError,
  isNotFoundError,
  isServerError,
  isInitialLoading,
  hasData,
  hasError
} from '../swr-config'

describe('utils', () => {
  describe('cn - class name utility', () => {
    it('should merge class names', () => {
      const result = cn('text-red-500', 'bg-blue-500')
      expect(result).toBe('text-red-500 bg-blue-500')
    })

    it('should handle conditional classes', () => {
      const result = cn('base-class', true && 'conditional-class', false && 'not-included')
      expect(result).toBe('base-class conditional-class')
    })

    it('should merge Tailwind classes correctly', () => {
      // Tailwind merge should keep the last conflicting class
      const result = cn('px-2 py-1', 'px-4')
      expect(result).toBe('py-1 px-4')
    })

    it('should handle arrays of classes', () => {
      const result = cn(['text-red-500', 'bg-blue-500'])
      expect(result).toBe('text-red-500 bg-blue-500')
    })

    it('should handle undefined and null values', () => {
      const result = cn('text-red-500', undefined, null, 'bg-blue-500')
      expect(result).toBe('text-red-500 bg-blue-500')
    })

    it('should handle objects with boolean values', () => {
      const result = cn({
        'text-red-500': true,
        'bg-blue-500': false,
        'text-lg': true,
      })
      expect(result).toBe('text-red-500 text-lg')
    })

    it('should handle empty input', () => {
      const result = cn()
      expect(result).toBe('')
    })

    it('should handle nested arrays', () => {
      const result = cn(['text-red-500', ['bg-blue-500', 'p-4']])
      expect(result).toBe('text-red-500 bg-blue-500 p-4')
    })

    it('should handle mixed types', () => {
      const result = cn(
        'base',
        ['array-class'],
        { 'object-class': true },
        undefined,
        'final'
      )
      expect(result).toBe('base array-class object-class final')
    })
  })

  describe('getScoreColor - score color utility', () => {
    it('should return high colors for scores >= 80', () => {
      const result = getScoreColor(80)
      expect(result.base).toBe(SCORE_COLORS.HIGH)
      expect(result.bg).toBe(SCORE_COLORS.HIGH_BG)
      expect(result.text).toBe(SCORE_COLORS.HIGH_TEXT)
      expect(result.label).toBe('Excellent')
    })

    it('should return high colors for scores > 80', () => {
      const result = getScoreColor(95)
      expect(result.base).toBe(SCORE_COLORS.HIGH)
      expect(result.label).toBe('Excellent')
    })

    it('should return high colors for score of 100', () => {
      const result = getScoreColor(100)
      expect(result.base).toBe(SCORE_COLORS.HIGH)
      expect(result.label).toBe('Excellent')
    })

    it('should return medium colors for scores >= 60 and < 80', () => {
      const result = getScoreColor(60)
      expect(result.base).toBe(SCORE_COLORS.MEDIUM)
      expect(result.bg).toBe(SCORE_COLORS.MEDIUM_BG)
      expect(result.text).toBe(SCORE_COLORS.MEDIUM_TEXT)
      expect(result.label).toBe('Good')
    })

    it('should return medium colors for mid-range scores', () => {
      const result = getScoreColor(70)
      expect(result.base).toBe(SCORE_COLORS.MEDIUM)
      expect(result.label).toBe('Good')
    })

    it('should return low colors for scores < 60', () => {
      const result = getScoreColor(59)
      expect(result.base).toBe(SCORE_COLORS.LOW)
      expect(result.bg).toBe(SCORE_COLORS.LOW_BG)
      expect(result.text).toBe(SCORE_COLORS.LOW_TEXT)
      expect(result.label).toBe('Needs Improvement')
    })

    it('should return low colors for score of 0', () => {
      const result = getScoreColor(0)
      expect(result.base).toBe(SCORE_COLORS.LOW)
      expect(result.label).toBe('Needs Improvement')
    })

    it('should handle negative scores', () => {
      const result = getScoreColor(-10)
      expect(result.base).toBe(SCORE_COLORS.LOW)
      expect(result.label).toBe('Needs Improvement')
    })

    it('should handle scores over 100', () => {
      const result = getScoreColor(150)
      expect(result.base).toBe(SCORE_COLORS.HIGH)
      expect(result.label).toBe('Excellent')
    })
  })

  describe('getPriorityColor - priority color utility', () => {
    it('should return high priority colors', () => {
      const result = getPriorityColor('high')
      expect(result).toEqual(PRIORITY_COLORS.HIGH)
      expect(result.bg).toBe('#ef4444')
      expect(result.text).toBe('#ffffff')
    })

    it('should return medium priority colors', () => {
      const result = getPriorityColor('medium')
      expect(result).toEqual(PRIORITY_COLORS.MEDIUM)
      expect(result.bg).toBe('#f59e0b')
    })

    it('should return low priority colors', () => {
      const result = getPriorityColor('low')
      expect(result).toEqual(PRIORITY_COLORS.LOW)
      expect(result.bg).toBe('#3b82f6')
    })

    it('should handle case-insensitive input', () => {
      const resultUpper = getPriorityColor('HIGH' as 'high')
      const resultLower = getPriorityColor('high')
      expect(resultUpper).toEqual(resultLower)
    })
  })

  describe('buildApiUrl - API URL builder', () => {
    beforeAll(() => {
      Object.defineProperty(window, 'location', {
        value: {
          origin: 'http://localhost:3000',
        },
        writable: true,
      })
    })

    it('should build URL without parameters', () => {
      const result = buildApiUrl('/api/calls')
      expect(result).toBe('http://localhost:3000/api/calls')
    })

    it('should build URL with string parameters', () => {
      const result = buildApiUrl('/api/calls', { rep: 'john@example.com' })
      expect(result).toBe('http://localhost:3000/api/calls?rep=john%40example.com')
    })

    it('should build URL with number parameters', () => {
      const result = buildApiUrl('/api/calls', { limit: 10 })
      expect(result).toBe('http://localhost:3000/api/calls?limit=10')
    })

    it('should build URL with boolean parameters', () => {
      const result = buildApiUrl('/api/calls', { active: true })
      expect(result).toBe('http://localhost:3000/api/calls?active=true')
    })

    it('should skip undefined parameters', () => {
      const result = buildApiUrl('/api/calls', { rep: 'john@example.com', filter: undefined })
      expect(result).toBe('http://localhost:3000/api/calls?rep=john%40example.com')
    })

    it('should handle multiple parameters', () => {
      const result = buildApiUrl('/api/calls', {
        rep: 'john@example.com',
        limit: 20,
        active: true
      })
      expect(result).toContain('rep=john%40example.com')
      expect(result).toContain('limit=20')
      expect(result).toContain('active=true')
    })

    it('should handle empty parameters object', () => {
      const result = buildApiUrl('/api/calls', {})
      expect(result).toBe('http://localhost:3000/api/calls')
    })
  })

  describe('isSWRError - error type check', () => {
    it('should return true for error with status', () => {
      const error = new Error('API Error')
      ;(error as any).status = 500
      expect(isSWRError(error)).toBe(true)
    })

    it('should return true for regular error (has message property)', () => {
      // Note: Regular Error objects also pass isSWRError check since they have a message
      const error = new Error('Regular error')
      expect(isSWRError(error)).toBe(true)
    })

    it('should return false for non-error values', () => {
      expect(isSWRError(null)).toBe(false)
      expect(isSWRError(undefined)).toBe(false)
      expect(isSWRError('string')).toBe(false)
      expect(isSWRError(123)).toBe(false)
    })

    it('should return false for objects without message', () => {
      expect(isSWRError({})).toBe(false)
      expect(isSWRError({ status: 404 })).toBe(false)
    })

    it('should return false for objects with non-string message', () => {
      expect(isSWRError({ message: 123 })).toBe(false)
      expect(isSWRError({ message: null })).toBe(false)
    })
  })

  describe('getErrorMessage - error message extraction', () => {
    it('should extract message from SWR error', () => {
      const error = new Error('API Error')
      ;(error as any).status = 500
      expect(getErrorMessage(error)).toBe('API Error')
    })

    it('should extract message from error object (treated as SWRError)', () => {
      // Since isSWRError checks for message property, it extracts directly
      const error = new Error('Error message')
      expect(getErrorMessage(error)).toBe('Error message')
    })

    it('should handle regular error', () => {
      const error = new Error('Regular error')
      expect(getErrorMessage(error)).toBe('Regular error')
    })

    it('should handle non-error values', () => {
      expect(getErrorMessage(null)).toBe('An unknown error occurred')
      expect(getErrorMessage(undefined)).toBe('An unknown error occurred')
    })

    it('should handle string values', () => {
      expect(getErrorMessage('string error')).toBe('An unknown error occurred')
    })

    it('should handle objects without message', () => {
      expect(getErrorMessage({})).toBe('An unknown error occurred')
      expect(getErrorMessage({ status: 500 })).toBe('An unknown error occurred')
    })
  })

  describe('isAuthError - authentication error check', () => {
    it('should return true for 401 status', () => {
      const error = new Error()
      ;(error as any).status = 401
      expect(isAuthError(error)).toBe(true)
    })

    it('should return false for other status codes', () => {
      const error = new Error()
      ;(error as any).status = 404
      expect(isAuthError(error)).toBe(false)
    })

    it('should return false for non-error values', () => {
      expect(isAuthError(null)).toBe(false)
    })
  })

  describe('isNotFoundError - not found error check', () => {
    it('should return true for 404 status', () => {
      const error = new Error()
      ;(error as any).status = 404
      expect(isNotFoundError(error)).toBe(true)
    })

    it('should return false for other status codes', () => {
      const error = new Error()
      ;(error as any).status = 500
      expect(isNotFoundError(error)).toBe(false)
    })
  })

  describe('isServerError - server error check', () => {
    it('should return true for 500 status', () => {
      const error = new Error()
      ;(error as any).status = 500
      expect(isServerError(error)).toBe(true)
    })

    it('should return true for 502 status', () => {
      const error = new Error()
      ;(error as any).status = 502
      expect(isServerError(error)).toBe(true)
    })

    it('should return false for non-server error codes', () => {
      const error = new Error()
      ;(error as any).status = 404
      expect(isServerError(error)).toBe(false)
    })
  })

  describe('Loading state utilities', () => {
    describe('isInitialLoading', () => {
      it('should return true when loading and no data', () => {
        const state = { isLoading: true, data: undefined, error: undefined }
        expect(isInitialLoading(state)).toBe(true)
      })

      it('should return false when not loading', () => {
        const state = { isLoading: false, data: { test: 'data' }, error: undefined }
        expect(isInitialLoading(state)).toBe(false)
      })

      it('should return false when has data', () => {
        const state = { isLoading: true, data: { test: 'data' }, error: undefined }
        expect(isInitialLoading(state)).toBe(false)
      })
    })

    describe('hasData', () => {
      it('should return true when data exists', () => {
        const state = { isLoading: false, data: { test: 'data' }, error: undefined }
        expect(hasData(state)).toBe(true)
      })

      it('should return false when data is undefined', () => {
        const state = { isLoading: false, data: undefined, error: undefined }
        expect(hasData(state)).toBe(false)
      })
    })

    describe('hasError', () => {
      it('should return true when error exists', () => {
        const error = new Error('Test error')
        ;(error as any).status = 500
        const state = { isLoading: false, data: undefined, error }
        expect(hasError(state)).toBe(true)
      })

      it('should return false when no error', () => {
        const state = { isLoading: false, data: { test: 'data' }, error: undefined }
        expect(hasError(state)).toBe(false)
      })
    })
  })
})
