import { cn } from '../utils'

describe('utils', () => {
  describe('cn', () => {
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
  })
})
