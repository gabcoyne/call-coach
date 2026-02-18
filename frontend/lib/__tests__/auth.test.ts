import { getCurrentUserRole, getCurrentUserEmail, canViewRepData, getUserSession } from "../auth";
import { UserRole } from "../auth-utils";

// Mock next/headers
const mockHeadersGet = jest.fn();
jest.mock("next/headers", () => ({
  headers: jest.fn(() =>
    Promise.resolve({
      get: mockHeadersGet,
    })
  ),
}));

describe("auth utilities", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockHeadersGet.mockReturnValue(null);
  });

  describe("getCurrentUserRole", () => {
    it("should return manager role when user has manager email", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "george@prefect.io";
        return null;
      });

      const role = await getCurrentUserRole();
      expect(role).toBe(UserRole.MANAGER);
    });

    it("should return rep role for non-manager email", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "rep@prefect.io";
        return null;
      });

      const role = await getCurrentUserRole();
      expect(role).toBe(UserRole.REP);
    });

    it("should return null when no email header", async () => {
      mockHeadersGet.mockReturnValue(null);

      const role = await getCurrentUserRole();
      expect(role).toBeNull();
    });

    it("should parse raw IAP header format", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-goog-authenticated-user-email")
          return "accounts.google.com:george@prefect.io";
        return null;
      });

      const role = await getCurrentUserRole();
      expect(role).toBe(UserRole.MANAGER);
    });
  });

  describe("getCurrentUserEmail", () => {
    it("should return user email from normalized header", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "test@example.com";
        return null;
      });

      const email = await getCurrentUserEmail();
      expect(email).toBe("test@example.com");
    });

    it("should return user email from raw IAP header", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-goog-authenticated-user-email")
          return "accounts.google.com:test@example.com";
        return null;
      });

      const email = await getCurrentUserEmail();
      expect(email).toBe("test@example.com");
    });

    it("should return null when no header present", async () => {
      mockHeadersGet.mockReturnValue(null);

      const email = await getCurrentUserEmail();
      expect(email).toBeNull();
    });
  });

  describe("canViewRepData", () => {
    it("should allow managers to view any rep data", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "george@prefect.io";
        return null;
      });

      const canView = await canViewRepData("rep@example.com");
      expect(canView).toBe(true);
    });

    it("should allow reps to view their own data", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "rep@example.com";
        return null;
      });

      const canView = await canViewRepData("rep@example.com");
      expect(canView).toBe(true);
    });

    it("should allow reps to view their own data (case insensitive)", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "Rep@Example.com";
        return null;
      });

      const canView = await canViewRepData("rep@example.com");
      expect(canView).toBe(true);
    });

    it("should not allow reps to view other rep data", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "rep1@example.com";
        return null;
      });

      const canView = await canViewRepData("rep2@example.com");
      expect(canView).toBe(false);
    });

    it("should return false when user is not authenticated", async () => {
      mockHeadersGet.mockReturnValue(null);

      const canView = await canViewRepData("rep@example.com");
      expect(canView).toBe(false);
    });
  });

  describe("getUserSession", () => {
    it("should return complete session information", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "george@prefect.io";
        if (header === "x-iap-user-id") return "user-123";
        return null;
      });

      const session = await getUserSession();

      expect(session.userId).toBe("user-123");
      expect(session.email).toBe("george@prefect.io");
      expect(session.role).toBe(UserRole.MANAGER);
    });

    it("should parse raw IAP user ID format", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-goog-authenticated-user-email")
          return "accounts.google.com:test@example.com";
        if (header === "x-goog-authenticated-user-id") return "accounts.google.com:12345";
        return null;
      });

      const session = await getUserSession();

      expect(session.userId).toBe("12345");
      expect(session.email).toBe("test@example.com");
    });
  });

  describe("edge cases and error handling", () => {
    it("should handle unauthenticated requests consistently", async () => {
      mockHeadersGet.mockReturnValue(null);

      const role = await getCurrentUserRole();
      const email = await getCurrentUserEmail();
      const canView = await canViewRepData("test@example.com");

      expect(role).toBeNull();
      expect(email).toBeNull();
      expect(canView).toBe(false);
    });

    it("should handle manager email case insensitively", async () => {
      mockHeadersGet.mockImplementation((header: string) => {
        if (header === "x-iap-user-email") return "GEORGE@PREFECT.IO";
        return null;
      });

      const role = await getCurrentUserRole();
      expect(role).toBe(UserRole.MANAGER);
    });
  });
});
