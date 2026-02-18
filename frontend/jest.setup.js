// Polyfill Web APIs BEFORE any imports (required for Next.js API routes)
const { TextEncoder, TextDecoder } = require("util");
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Polyfill Request/Response for Next.js API routes (minimal implementation for tests)
if (typeof global.Request === "undefined") {
  global.Request = class Request {
    constructor(input, init) {
      const url = typeof input === "string" ? input : input.url;
      const method = init?.method || "GET";
      const headers = new Map(Object.entries(init?.headers || {}));
      const body = init?.body;

      // Use Object.defineProperty for read-only properties
      Object.defineProperty(this, "url", { value: url, writable: false });
      Object.defineProperty(this, "method", { value: method, writable: false });
      Object.defineProperty(this, "headers", { value: headers, writable: false });
      Object.defineProperty(this, "_body", { value: body, writable: false });
      Object.defineProperty(this, "nextUrl", { value: { pathname: url }, writable: false });
    }
    async json() {
      return JSON.parse(this._body);
    }
    async text() {
      return this._body;
    }
  };
}

if (typeof global.Response === "undefined") {
  global.Response = class Response {
    constructor(body, init) {
      this.body = body;
      this.status = init?.status || 200;
      this.ok = this.status >= 200 && this.status < 300;
      this.headers = new Map(Object.entries(init?.headers || {}));
    }
    async json() {
      return typeof this.body === "string" ? JSON.parse(this.body) : this.body;
    }
    async text() {
      return typeof this.body === "string" ? this.body : JSON.stringify(this.body);
    }
    static json(data, init) {
      return new Response(JSON.stringify(data), {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(init?.headers || {}),
        },
      });
    }
  };
}

if (typeof global.Headers === "undefined") {
  global.Headers = class Headers extends Map {
    constructor(init) {
      super(Object.entries(init || {}));
    }
  };
}

// Learn more: https://github.com/testing-library/jest-dom
require("@testing-library/jest-dom");

// Set up MSW (Mock Service Worker) for API mocking
// Note: MSW v2 uses a different module structure
let server;
try {
  const { setupServer } = require("msw/node");
  const { handlers } = require("./__mocks__/handlers");

  // Create MSW server instance with handlers
  server = setupServer(...handlers);

  // Start server before all tests
  beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));

  // Reset handlers after each test
  afterEach(() => server.resetHandlers());

  // Clean up after all tests
  afterAll(() => server.close());
} catch (error) {
  // MSW not installed or handlers not configured - skip MSW setup
  console.warn("MSW setup skipped:", error.message);
}

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      pathname: "/",
      query: {},
      asPath: "/",
    };
  },
  usePathname() {
    return "/";
  },
  useSearchParams() {
    return new URLSearchParams();
  },
  useParams() {
    return {};
  },
}));

// Mock IAP auth context
jest.mock("@/lib/auth-context", () => ({
  useAuthContext: jest.fn(() => ({
    user: {
      id: "test-user-id",
      email: "test@example.com",
      name: "Test User",
      role: "rep",
    },
    isLoading: false,
    isAuthenticated: true,
    signOut: jest.fn(),
  })),
  AuthProvider: ({ children }) => children,
}));

// Mock IAP auth middleware
jest.mock("@/lib/auth-middleware", () => ({
  getAuthContext: jest.fn(() => ({
    userId: "test-user-id",
    email: "test@example.com",
    name: "Test User",
    role: "rep",
  })),
}));

// Mock fetch globally
global.fetch = jest.fn();

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};

// Mock ResizeObserver for Recharts
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {
    // Trigger callback with mock entry
    this.callback([{ contentRect: { width: 800, height: 600 } }]);
  }
  unobserve() {}
  disconnect() {}
};

// Reset mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
});
