// Polyfill Web APIs BEFORE any imports (required for Next.js API routes)
const { TextEncoder, TextDecoder } = require("util");
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Polyfill Request/Response for Next.js API routes (minimal implementation for tests)
if (typeof global.Request === "undefined") {
  global.Request = class Request {
    constructor(input, init) {
      this.url = typeof input === "string" ? input : input.url;
      this.method = init?.method || "GET";
      this.headers = new Map(Object.entries(init?.headers || {}));
      this._body = init?.body;
      this.nextUrl = { pathname: this.url };
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

// Mock Clerk authentication
jest.mock("@clerk/nextjs/server", () => ({
  auth: jest.fn(() => ({
    userId: "test-user-id",
    sessionId: "test-session-id",
  })),
  currentUser: jest.fn(() => ({
    id: "test-user-id",
    emailAddresses: [{ emailAddress: "test@example.com" }],
    publicMetadata: { role: "rep" },
  })),
  ClerkProvider: ({ children }) => children,
}));

jest.mock("@clerk/nextjs", () => ({
  useUser: jest.fn(() => ({
    isSignedIn: true,
    user: {
      id: "test-user-id",
      emailAddresses: [{ emailAddress: "test@example.com" }],
      publicMetadata: { role: "rep" },
    },
  })),
  useAuth: jest.fn(() => ({
    isSignedIn: true,
    userId: "test-user-id",
    sessionId: "test-session-id",
  })),
  SignIn: () => <div>Sign In</div>,
  SignUp: () => <div>Sign Up</div>,
  UserButton: () => <div>User Button</div>,
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
