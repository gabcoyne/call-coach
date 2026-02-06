import {
  getCurrentUserRole,
  isManager,
  isRep,
  getCurrentUserEmail,
  canViewRepData,
  requireManager,
  getUserSession,
} from '../auth'
import { UserRole } from '../auth-utils'
import { auth, currentUser } from '@clerk/nextjs/server'

// Mock Clerk
jest.mock('@clerk/nextjs/server')

describe('auth utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('getCurrentUserRole', () => {
    it('should return manager role when user has manager metadata', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: { role: 'manager' },
      })

      const role = await getCurrentUserRole()
      expect(role).toBe(UserRole.MANAGER)
    })

    it('should return rep role when user has rep metadata', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: { role: 'rep' },
      })

      const role = await getCurrentUserRole()
      expect(role).toBe(UserRole.REP)
    })

    it('should default to rep when no role is set', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: {},
      })

      const role = await getCurrentUserRole()
      expect(role).toBe(UserRole.REP)
    })

    it('should return null when user is not authenticated', async () => {
      (currentUser as jest.Mock).mockResolvedValue(null)

      const role = await getCurrentUserRole()
      expect(role).toBeNull()
    })
  })

  describe('isManager', () => {
    it('should return true for managers', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: { role: 'manager' },
      })

      const result = await isManager()
      expect(result).toBe(true)
    })

    it('should return false for reps', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: { role: 'rep' },
      })

      const result = await isManager()
      expect(result).toBe(false)
    })
  })

  describe('isRep', () => {
    it('should return true for reps', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: { role: 'rep' },
      })

      const result = await isRep()
      expect(result).toBe(true)
    })

    it('should return false for managers', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        publicMetadata: { role: 'manager' },
      })

      const result = await isRep()
      expect(result).toBe(false)
    })
  })

  describe('getCurrentUserEmail', () => {
    it('should return user email', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        emailAddresses: [{ emailAddress: 'test@example.com' }],
      })

      const email = await getCurrentUserEmail()
      expect(email).toBe('test@example.com')
    })

    it('should return null when user is not authenticated', async () => {
      (currentUser as jest.Mock).mockResolvedValue(null)

      const email = await getCurrentUserEmail()
      expect(email).toBeNull()
    })

    it('should return null when user has no email addresses', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        emailAddresses: [],
      })

      const email = await getCurrentUserEmail()
      expect(email).toBeNull()
    })
  })

  describe('canViewRepData', () => {
    it('should allow managers to view any rep data', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'manager-123',
        emailAddresses: [{ emailAddress: 'manager@example.com' }],
        publicMetadata: { role: 'manager' },
      })

      const canView = await canViewRepData('rep@example.com')
      expect(canView).toBe(true)
    })

    it('should allow reps to view their own data', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'rep-123',
        emailAddresses: [{ emailAddress: 'rep@example.com' }],
        publicMetadata: { role: 'rep' },
      })

      const canView = await canViewRepData('rep@example.com')
      expect(canView).toBe(true)
    })

    it('should allow reps to view their own data (case insensitive)', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'rep-123',
        emailAddresses: [{ emailAddress: 'Rep@Example.com' }],
        publicMetadata: { role: 'rep' },
      })

      const canView = await canViewRepData('rep@example.com')
      expect(canView).toBe(true)
    })

    it('should not allow reps to view other rep data', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'rep-123',
        emailAddresses: [{ emailAddress: 'rep1@example.com' }],
        publicMetadata: { role: 'rep' },
      })

      const canView = await canViewRepData('rep2@example.com')
      expect(canView).toBe(false)
    })

    it('should return false when user is not authenticated', async () => {
      (currentUser as jest.Mock).mockResolvedValue(null)

      const canView = await canViewRepData('rep@example.com')
      expect(canView).toBe(false)
    })
  })

  describe('requireManager', () => {
    it('should not throw for managers', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'manager-123',
        publicMetadata: { role: 'manager' },
      })

      await expect(requireManager()).resolves.not.toThrow()
    })

    it('should throw for non-managers', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'rep-123',
        publicMetadata: { role: 'rep' },
      })

      await expect(requireManager()).rejects.toThrow('Unauthorized: Manager access required')
    })
  })

  describe('getUserSession', () => {
    it('should return complete session information', async () => {
      const mockAuth = {
        userId: 'user-123',
        sessionId: 'session-456',
      };
      const mockUser = {
        id: 'user-123',
        emailAddresses: [{ emailAddress: 'test@example.com' }],
        publicMetadata: { role: 'manager' },
      };

      (auth as jest.Mock).mockResolvedValue(mockAuth);
      (currentUser as jest.Mock).mockResolvedValue(mockUser)

      const session = await getUserSession()

      expect(session.userId).toBe('user-123')
      expect(session.sessionId).toBe('session-456')
      expect(session.user).toEqual(mockUser)
      expect(session.role).toBe(UserRole.MANAGER)
      expect(session.email).toBe('test@example.com')
    })
  })

  describe('edge cases and error handling', () => {
    it('should handle unauthenticated requests consistently', async () => {
      (currentUser as jest.Mock).mockResolvedValue(null)

      const role = await getCurrentUserRole()
      const email = await getCurrentUserEmail()
      const isManagerResult = await isManager()
      const isRepResult = await isRep()
      const canView = await canViewRepData('test@example.com')

      expect(role).toBeNull()
      expect(email).toBeNull()
      expect(isManagerResult).toBe(false)
      expect(isRepResult).toBe(false)
      expect(canView).toBe(false)
    })

    it('should handle invalid role values gracefully', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        emailAddresses: [{ emailAddress: 'test@example.com' }],
        publicMetadata: { role: 'invalid-role' },
      })

      const role = await getCurrentUserRole()
      expect(role).toBe(UserRole.REP) // Should default to rep
    })

    it('should handle missing publicMetadata', async () => {
      (currentUser as jest.Mock).mockResolvedValue({
        id: 'user-123',
        emailAddresses: [{ emailAddress: 'test@example.com' }],
      })

      const role = await getCurrentUserRole()
      expect(role).toBe(UserRole.REP) // Should default to rep
    })
  })
})
