/**
 * Tests for client-side auth utilities (auth-utils.ts)
 * These utilities work with IAP authentication
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
} from "../auth-utils";
import type { AuthUser } from "../auth-context";

// Helper to create mock user objects
function createMockUser(overrides: Partial<AuthUser> = {}): AuthUser {
  return {
    id: "user-123",
    email: "test@example.com",
    name: "Test User",
    role: "rep",
    ...overrides,
  } as AuthUser;
}

describe("auth-utils - client-side utilities", () => {
  describe("getUserRole", () => {
    it("should return manager role when user has manager role", () => {
      const user = createMockUser({ role: "manager" });

      const role = getUserRole(user);
      expect(role).toBe(UserRole.MANAGER);
    });

    it("should return rep role when user has rep role", () => {
      const user = createMockUser({ role: "rep" });

      const role = getUserRole(user);
      expect(role).toBe(UserRole.REP);
    });

    it("should return rep for null user", () => {
      const role = getUserRole(null);
      expect(role).toBe(UserRole.REP);
    });

    it("should return rep for undefined user", () => {
      const role = getUserRole(undefined);
      expect(role).toBe(UserRole.REP);
    });
  });

  describe("isManager", () => {
    it("should return true for managers", () => {
      const user = createMockUser({ role: "manager" });

      expect(isManager(user)).toBe(true);
    });

    it("should return false for reps", () => {
      const user = createMockUser({ role: "rep" });

      expect(isManager(user)).toBe(false);
    });

    it("should return false for null user", () => {
      expect(isManager(null)).toBe(false);
    });

    it("should return false for undefined user", () => {
      expect(isManager(undefined)).toBe(false);
    });
  });

  describe("isRep", () => {
    it("should return true for reps", () => {
      const user = createMockUser({ role: "rep" });

      expect(isRep(user)).toBe(true);
    });

    it("should return false for managers", () => {
      const user = createMockUser({ role: "manager" });

      expect(isRep(user)).toBe(false);
    });

    it("should return true for null user (default)", () => {
      expect(isRep(null)).toBe(true);
    });

    it("should return true for undefined user (default)", () => {
      expect(isRep(undefined)).toBe(true);
    });
  });

  describe("getUserEmail", () => {
    it("should return user email", () => {
      const user = createMockUser({ email: "test@example.com" });

      const email = getUserEmail(user);
      expect(email).toBe("test@example.com");
    });

    it("should return null for null user", () => {
      expect(getUserEmail(null)).toBeNull();
    });

    it("should return null for undefined user", () => {
      expect(getUserEmail(undefined)).toBeNull();
    });
  });

  describe("canViewRepData", () => {
    it("should allow managers to view any rep data", () => {
      const user = createMockUser({
        email: "manager@example.com",
        role: "manager",
      });

      const canView = canViewRepData(user, "rep@example.com");
      expect(canView).toBe(true);
    });

    it("should allow reps to view their own data", () => {
      const user = createMockUser({
        email: "rep@example.com",
        role: "rep",
      });

      const canView = canViewRepData(user, "rep@example.com");
      expect(canView).toBe(true);
    });

    it("should allow reps to view their own data (case insensitive)", () => {
      const user = createMockUser({
        email: "Rep@Example.com",
        role: "rep",
      });

      const canView = canViewRepData(user, "rep@example.com");
      expect(canView).toBe(true);
    });

    it("should not allow reps to view other rep data", () => {
      const user = createMockUser({
        email: "rep1@example.com",
        role: "rep",
      });

      const canView = canViewRepData(user, "rep2@example.com");
      expect(canView).toBe(false);
    });

    it("should return false when user is null", () => {
      const canView = canViewRepData(null, "rep@example.com");
      expect(canView).toBe(false);
    });

    it("should return false when user is undefined", () => {
      const canView = canViewRepData(undefined, "rep@example.com");
      expect(canView).toBe(false);
    });

    it("should handle email comparison with different cases", () => {
      const user = createMockUser({
        email: "REP@EXAMPLE.COM",
        role: "rep",
      });

      expect(canViewRepData(user, "rep@example.com")).toBe(true);
      expect(canViewRepData(user, "Rep@Example.Com")).toBe(true);
      expect(canViewRepData(user, "REP@EXAMPLE.COM")).toBe(true);
    });
  });

  describe("hasManagerAccess", () => {
    it("should return true for managers", () => {
      const user = createMockUser({ role: "manager" });

      expect(hasManagerAccess(user)).toBe(true);
    });

    it("should return false for reps", () => {
      const user = createMockUser({ role: "rep" });

      expect(hasManagerAccess(user)).toBe(false);
    });

    it("should return false for null user", () => {
      expect(hasManagerAccess(null)).toBe(false);
    });

    it("should return false for undefined user", () => {
      expect(hasManagerAccess(undefined)).toBe(false);
    });
  });

  describe("getRoleDisplayName", () => {
    it('should return "Manager" for managers', () => {
      const user = createMockUser({ role: "manager" });

      expect(getRoleDisplayName(user)).toBe("Manager");
    });

    it('should return "Sales Rep" for reps', () => {
      const user = createMockUser({ role: "rep" });

      expect(getRoleDisplayName(user)).toBe("Sales Rep");
    });

    it('should return "Sales Rep" for null user', () => {
      expect(getRoleDisplayName(null)).toBe("Sales Rep");
    });

    it('should return "Sales Rep" for undefined user', () => {
      expect(getRoleDisplayName(undefined)).toBe("Sales Rep");
    });
  });

  describe("UserRole enum", () => {
    it("should have correct enum values", () => {
      expect(UserRole.MANAGER).toBe("manager");
      expect(UserRole.REP).toBe("rep");
    });

    it("should only have two roles", () => {
      const roles = Object.values(UserRole);
      expect(roles).toHaveLength(2);
      expect(roles).toContain("manager");
      expect(roles).toContain("rep");
    });
  });
});
