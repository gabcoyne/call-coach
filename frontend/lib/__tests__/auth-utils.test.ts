/**
 * Tests for client-side auth utilities (auth-utils.ts)
 * These utilities work with Clerk's UserResource on the client side
 */

import {
  getUserRole,
  isManager,
  isRep,
  getUserEmail,
  canViewRepData,
  hasManagerAccess,
  getRoleDisplayName,
  UserRole,
} from '../auth-utils'
import type { UserResource } from '@clerk/types'

// Helper to create mock user objects
function createMockUser(
  overrides: Partial<UserResource> = {}
): UserResource {
  return {
    id: 'user-123',
    emailAddresses: [
      { emailAddress: 'test@example.com', id: 'email-1' } as any,
    ],
    publicMetadata: { role: 'rep' },
    ...overrides,
  } as UserResource
}

describe('auth-utils - client-side utilities', () => {
  describe('getUserRole', () => {
    it('should return manager role when user has manager metadata', () => {
      const user = createMockUser({
        publicMetadata: { role: 'manager' },
      })

      const role = getUserRole(user)
      expect(role).toBe(UserRole.MANAGER)
    })

    it('should return rep role when user has rep metadata', () => {
      const user = createMockUser({
        publicMetadata: { role: 'rep' },
      })

      const role = getUserRole(user)
      expect(role).toBe(UserRole.REP)
    })

    it('should default to rep when no role is set', () => {
      const user = createMockUser({
        publicMetadata: {},
      })

      const role = getUserRole(user)
      expect(role).toBe(UserRole.REP)
    })

    it('should default to rep when publicMetadata is undefined', () => {
      const user = createMockUser({
        publicMetadata: undefined,
      })

      const role = getUserRole(user)
      expect(role).toBe(UserRole.REP)
    })

    it('should return rep for null user', () => {
      const role = getUserRole(null)
      expect(role).toBe(UserRole.REP)
    })

    it('should return rep for undefined user', () => {
      const role = getUserRole(undefined)
      expect(role).toBe(UserRole.REP)
    })

    it('should handle invalid role values', () => {
      const user = createMockUser({
        publicMetadata: { role: 'admin' },
      })

      const role = getUserRole(user)
      expect(role).toBe(UserRole.REP) // Should default to rep
    })

    it('should handle non-string role values', () => {
      const user = createMockUser({
        publicMetadata: { role: 123 as any },
      })

      const role = getUserRole(user)
      expect(role).toBe(UserRole.REP)
    })
  })

  describe('isManager', () => {
    it('should return true for managers', () => {
      const user = createMockUser({
        publicMetadata: { role: 'manager' },
      })

      expect(isManager(user)).toBe(true)
    })

    it('should return false for reps', () => {
      const user = createMockUser({
        publicMetadata: { role: 'rep' },
      })

      expect(isManager(user)).toBe(false)
    })

    it('should return false for null user', () => {
      expect(isManager(null)).toBe(false)
    })

    it('should return false for undefined user', () => {
      expect(isManager(undefined)).toBe(false)
    })

    it('should return false when no role is set', () => {
      const user = createMockUser({
        publicMetadata: {},
      })

      expect(isManager(user)).toBe(false)
    })
  })

  describe('isRep', () => {
    it('should return true for reps', () => {
      const user = createMockUser({
        publicMetadata: { role: 'rep' },
      })

      expect(isRep(user)).toBe(true)
    })

    it('should return false for managers', () => {
      const user = createMockUser({
        publicMetadata: { role: 'manager' },
      })

      expect(isRep(user)).toBe(false)
    })

    it('should return true for null user (default)', () => {
      expect(isRep(null)).toBe(true)
    })

    it('should return true for undefined user (default)', () => {
      expect(isRep(undefined)).toBe(true)
    })

    it('should return true when no role is set', () => {
      const user = createMockUser({
        publicMetadata: {},
      })

      expect(isRep(user)).toBe(true)
    })
  })

  describe('getUserEmail', () => {
    it('should return user email', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'test@example.com', id: 'email-1' } as any],
      })

      const email = getUserEmail(user)
      expect(email).toBe('test@example.com')
    })

    it('should return null for null user', () => {
      expect(getUserEmail(null)).toBeNull()
    })

    it('should return null for undefined user', () => {
      expect(getUserEmail(undefined)).toBeNull()
    })

    it('should return null when user has no email addresses', () => {
      const user = createMockUser({
        emailAddresses: [],
      })

      const email = getUserEmail(user)
      expect(email).toBeNull()
    })

    it('should throw when emailAddresses is undefined', () => {
      // Note: The implementation doesn't handle undefined emailAddresses
      // This test documents the current behavior
      const user = createMockUser({
        emailAddresses: undefined as any,
      })

      expect(() => getUserEmail(user)).toThrow()
    })

    it('should return first email when multiple exist', () => {
      const user = createMockUser({
        emailAddresses: [
          { emailAddress: 'first@example.com', id: 'email-1' } as any,
          { emailAddress: 'second@example.com', id: 'email-2' } as any,
        ],
      })

      const email = getUserEmail(user)
      expect(email).toBe('first@example.com')
    })
  })

  describe('canViewRepData', () => {
    it('should allow managers to view any rep data', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'manager@example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'manager' },
      })

      const canView = canViewRepData(user, 'rep@example.com')
      expect(canView).toBe(true)
    })

    it('should allow reps to view their own data', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'rep@example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      const canView = canViewRepData(user, 'rep@example.com')
      expect(canView).toBe(true)
    })

    it('should allow reps to view their own data (case insensitive)', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'Rep@Example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      const canView = canViewRepData(user, 'rep@example.com')
      expect(canView).toBe(true)
    })

    it('should not allow reps to view other rep data', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'rep1@example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      const canView = canViewRepData(user, 'rep2@example.com')
      expect(canView).toBe(false)
    })

    it('should return false when user is null', () => {
      const canView = canViewRepData(null, 'rep@example.com')
      expect(canView).toBe(false)
    })

    it('should return false when user is undefined', () => {
      const canView = canViewRepData(undefined, 'rep@example.com')
      expect(canView).toBe(false)
    })

    it('should return false when user has no email', () => {
      const user = createMockUser({
        emailAddresses: [],
        publicMetadata: { role: 'rep' },
      })

      const canView = canViewRepData(user, 'rep@example.com')
      expect(canView).toBe(false)
    })

    it('should handle email comparison with different cases', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'REP@EXAMPLE.COM', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      expect(canViewRepData(user, 'rep@example.com')).toBe(true)
      expect(canViewRepData(user, 'Rep@Example.Com')).toBe(true)
      expect(canViewRepData(user, 'REP@EXAMPLE.COM')).toBe(true)
    })

    it('should handle whitespace in emails', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'rep@example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      // Note: in real scenario, emails should be trimmed by the caller
      const canView = canViewRepData(user, 'rep@example.com ')
      expect(canView).toBe(false) // Should not match due to whitespace
    })
  })

  describe('hasManagerAccess', () => {
    it('should return true for managers', () => {
      const user = createMockUser({
        publicMetadata: { role: 'manager' },
      })

      expect(hasManagerAccess(user)).toBe(true)
    })

    it('should return false for reps', () => {
      const user = createMockUser({
        publicMetadata: { role: 'rep' },
      })

      expect(hasManagerAccess(user)).toBe(false)
    })

    it('should return false for null user', () => {
      expect(hasManagerAccess(null)).toBe(false)
    })

    it('should return false for undefined user', () => {
      expect(hasManagerAccess(undefined)).toBe(false)
    })
  })

  describe('getRoleDisplayName', () => {
    it('should return "Manager" for managers', () => {
      const user = createMockUser({
        publicMetadata: { role: 'manager' },
      })

      expect(getRoleDisplayName(user)).toBe('Manager')
    })

    it('should return "Sales Rep" for reps', () => {
      const user = createMockUser({
        publicMetadata: { role: 'rep' },
      })

      expect(getRoleDisplayName(user)).toBe('Sales Rep')
    })

    it('should return "Sales Rep" for null user', () => {
      expect(getRoleDisplayName(null)).toBe('Sales Rep')
    })

    it('should return "Sales Rep" for undefined user', () => {
      expect(getRoleDisplayName(undefined)).toBe('Sales Rep')
    })

    it('should return "Sales Rep" when no role is set', () => {
      const user = createMockUser({
        publicMetadata: {},
      })

      expect(getRoleDisplayName(user)).toBe('Sales Rep')
    })
  })

  describe('edge cases and security', () => {
    it('should handle malformed user objects', () => {
      const malformedUser = {} as UserResource

      expect(getUserRole(malformedUser)).toBe(UserRole.REP)
      expect(isManager(malformedUser)).toBe(false)
      expect(isRep(malformedUser)).toBe(true)
      // getUserEmail will throw with undefined emailAddresses
      expect(() => getUserEmail(malformedUser)).toThrow()
      expect(hasManagerAccess(malformedUser)).toBe(false)
      expect(getRoleDisplayName(malformedUser)).toBe('Sales Rep')
    })

    it('should not allow role escalation through email matching', () => {
      const repUser = createMockUser({
        emailAddresses: [{ emailAddress: 'rep@example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      // Rep trying to access manager's data
      expect(canViewRepData(repUser, 'manager@example.com')).toBe(false)
    })

    it('should handle users with multiple email addresses correctly', () => {
      const user = createMockUser({
        emailAddresses: [
          { emailAddress: 'primary@example.com', id: 'email-1' } as any,
          { emailAddress: 'secondary@example.com', id: 'email-2' } as any,
        ],
        publicMetadata: { role: 'rep' },
      })

      // Should only use first email for comparison
      expect(canViewRepData(user, 'primary@example.com')).toBe(true)
      expect(canViewRepData(user, 'secondary@example.com')).toBe(false)
    })

    it('should handle special characters in emails', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: 'user+test@example.com', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      expect(canViewRepData(user, 'user+test@example.com')).toBe(true)
      expect(canViewRepData(user, 'user@example.com')).toBe(false)
    })

    it('should handle empty strings', () => {
      const user = createMockUser({
        emailAddresses: [{ emailAddress: '', id: 'email-1' } as any],
        publicMetadata: { role: 'rep' },
      })

      expect(getUserEmail(user)).toBe('')
      // Empty string is falsy, so canViewRepData returns false (line 100-102)
      expect(canViewRepData(user, '')).toBe(false)
      expect(canViewRepData(user, 'test@example.com')).toBe(false)
    })
  })

  describe('UserRole enum', () => {
    it('should have correct enum values', () => {
      expect(UserRole.MANAGER).toBe('manager')
      expect(UserRole.REP).toBe('rep')
    })

    it('should only have two roles', () => {
      const roles = Object.values(UserRole)
      expect(roles).toHaveLength(2)
      expect(roles).toContain('manager')
      expect(roles).toContain('rep')
    })
  })
})
