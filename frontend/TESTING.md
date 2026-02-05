# Testing Guide for Call Coach Frontend

This document outlines the testing strategy, setup, and best practices for the Next.js coaching frontend application.

## Table of Contents

- [Test Infrastructure](#test-infrastructure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Code Coverage](#code-coverage)
- [Accessibility Testing](#accessibility-testing)
- [Performance Testing](#performance-testing)
- [CI/CD Integration](#cicd-integration)

## Test Infrastructure

### Testing Stack

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/jest-dom**: Custom DOM matchers
- **@axe-core/react**: Accessibility testing
- **@next/bundle-analyzer**: Bundle size analysis

### Configuration Files

- **jest.config.js**: Jest configuration for Next.js 15 with App Router
- **jest.setup.js**: Global test setup, mocks, and utilities
- **tsconfig.json**: TypeScript configuration with test paths

### Mocks

The following are automatically mocked in `jest.setup.js`:

- Next.js navigation (`next/navigation`)
- Clerk authentication (`@clerk/nextjs`, `@clerk/nextjs/server`)
- Global `fetch` API
- `window.matchMedia`
- `IntersectionObserver`

## Running Tests

### Basic Commands

```bash
# Run all tests
npm test

# Run tests in watch mode (development)
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode (optimized for CI/CD)
npm run test:ci
```

### Running Specific Tests

```bash
# Run tests for a specific file
npm test -- button.test.tsx

# Run tests matching a pattern
npm test -- --testNamePattern="should render"

# Run only changed tests (watch mode)
npm run test:watch -- --onlyChanged

# Update snapshots
npm test -- --updateSnapshot
```

## Test Categories

### 1. Unit Tests

**Location**: `lib/__tests__/`

Tests for utility functions, helpers, and pure logic.

**Example**:
```typescript
// lib/__tests__/utils.test.ts
import { cn } from '../utils'

describe('cn utility', () => {
  it('should merge class names', () => {
    expect(cn('px-2', 'py-1')).toBe('px-2 py-1')
  })
})
```

**Coverage**: Utility functions in `lib/`

### 2. Hook Tests

**Location**: `lib/hooks/__tests__/`

Tests for custom React hooks, especially SWR hooks.

**Example**:
```typescript
// lib/hooks/__tests__/useCallAnalysis.test.tsx
import { renderHook, waitFor } from '@testing-library/react'
import { useCallAnalysis } from '../useCallAnalysis'

describe('useCallAnalysis', () => {
  it('should fetch call analysis', async () => {
    const { result } = renderHook(() => useCallAnalysis('call-123'))

    await waitFor(() => {
      expect(result.current.data).toBeDefined()
    })
  })
})
```

**Coverage**: All hooks in `lib/hooks/`

### 3. Component Tests

**Location**: `components/**/__tests__/`

Tests for UI components focusing on rendering and user interactions.

**Example**:
```typescript
// components/ui/__tests__/button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../button'

describe('Button', () => {
  it('should handle clicks', async () => {
    const onClick = jest.fn()
    const user = userEvent.setup()

    render(<Button onClick={onClick}>Click me</Button>)
    await user.click(screen.getByRole('button'))

    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
```

**Coverage**: All components in `components/`

### 4. Integration Tests

**Location**: `app/api/**/__tests__/`

Tests for API routes with mocked MCP backend.

**Example**:
```typescript
// app/api/coaching/analyze-call/__tests__/route.test.ts
import { POST } from '../route'
import { mcpClient } from '@/lib/mcp-client'

jest.mock('@/lib/mcp-client')

describe('POST /api/coaching/analyze-call', () => {
  it('should analyze call successfully', async () => {
    mcpClient.analyzeCall.mockResolvedValue(mockResponse)

    const request = new NextRequest('http://localhost', {
      method: 'POST',
      body: JSON.stringify({ call_id: 'call-123' }),
    })

    const response = await POST(request, mockAuthContext)

    expect(response.status).toBe(200)
  })
})
```

**Coverage**: API routes in `app/api/`

### 5. Authentication Tests

Tests for authentication flows, RBAC, and Clerk integration.

**Scenarios**:
- Sign up flow
- Sign in flow
- Role assignment (manager vs. rep)
- RBAC enforcement (reps see own data only)
- Unauthorized access handling

### 6. Responsive Design Tests

Tests for mobile, tablet, and desktop viewports.

**Example**:
```typescript
describe('Mobile responsiveness', () => {
  beforeEach(() => {
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(max-width: 768px)',
      media: query,
      // ...
    }))
  })

  it('should show mobile menu on small screens', () => {
    // Test mobile-specific behavior
  })
})
```

## Writing Tests

### Best Practices

1. **Test Behavior, Not Implementation**
   ```typescript
   // Good: Test what user sees
   expect(screen.getByText('Analysis complete')).toBeInTheDocument()

   // Bad: Test internal state
   expect(component.state.isLoading).toBe(false)
   ```

2. **Use Semantic Queries**
   ```typescript
   // Prefer (in order):
   screen.getByRole('button', { name: /submit/i })
   screen.getByLabelText('Email')
   screen.getByText('Welcome')

   // Avoid:
   screen.getByTestId('submit-button')
   ```

3. **Async Testing**
   ```typescript
   // Use waitFor for async assertions
   await waitFor(() => {
     expect(screen.getByText('Loaded')).toBeInTheDocument()
   })

   // Use findBy for elements that appear asynchronously
   const element = await screen.findByText('Loaded')
   ```

4. **User Event Simulation**
   ```typescript
   // Use user-event for realistic interactions
   const user = userEvent.setup()
   await user.click(button)
   await user.type(input, 'test@example.com')
   ```

5. **Mocking API Calls**
   ```typescript
   // Mock fetch for API tests
   global.fetch = jest.fn(() =>
     Promise.resolve({
       ok: true,
       json: () => Promise.resolve({ data: 'mock' }),
     })
   ) as jest.Mock
   ```

### Test Structure

```typescript
describe('ComponentName', () => {
  beforeEach(() => {
    // Setup before each test
    jest.clearAllMocks()
  })

  afterEach(() => {
    // Cleanup after each test
  })

  describe('feature/scenario', () => {
    it('should behave in expected way', () => {
      // Arrange
      const props = { /* ... */ }

      // Act
      render(<Component {...props} />)

      // Assert
      expect(screen.getByText('Expected')).toBeInTheDocument()
    })
  })
})
```

## Code Coverage

### Coverage Goals

- **Statements**: 70%
- **Branches**: 60%
- **Functions**: 70%
- **Lines**: 70%

### Coverage Report

```bash
# Generate coverage report
npm run test:coverage

# View HTML report
open coverage/lcov-report/index.html
```

### Coverage by Category

- **lib/utils**: 90%+ (critical utilities)
- **lib/hooks**: 80%+ (data fetching logic)
- **components/ui**: 70%+ (design system)
- **app/api**: 80%+ (API routes with business logic)

### Excluded from Coverage

- Type definition files (`*.d.ts`)
- Configuration files
- Build artifacts (`.next/`, `coverage/`)

## Accessibility Testing

### Automated Testing

Use `@axe-core/react` for automated accessibility audits.

```typescript
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

describe('Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Component />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

### Manual Testing Checklist

- [ ] Keyboard navigation works (Tab, Enter, Space, Escape)
- [ ] Screen reader announces content correctly
- [ ] Color contrast meets WCAG AA standards (4.5:1)
- [ ] Focus indicators are visible
- [ ] Form labels are associated with inputs
- [ ] Error messages are announced
- [ ] Modal dialogs trap focus

### Lighthouse Audit

```bash
# Run Lighthouse in CI
npx lighthouse http://localhost:3000 --only-categories=accessibility
```

**Target Scores**:
- Accessibility: 95+
- Best Practices: 90+
- Performance: 85+
- SEO: 90+

## Performance Testing

### Bundle Analysis

```bash
# Analyze bundle size
npm run analyze

# This opens a visual treemap of the bundle
```

**Bundle Size Targets**:
- First Load JS: < 200 KB
- Total Page Size: < 500 KB
- Time to Interactive (TTI): < 3s

### Load Testing API Routes

Use `k6` or `artillery` for load testing:

```bash
# Install k6
brew install k6

# Run load test (50 concurrent users)
k6 run load-test.js
```

**Example k6 script**:
```javascript
import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  vus: 50, // 50 virtual users
  duration: '30s',
}

export default function () {
  const res = http.get('http://localhost:3000/api/coaching/analyze-call')
  check(res, { 'status is 200': (r) => r.status === 200 })
  sleep(1)
}
```

**Performance Targets**:
- API response time (p95): < 500ms
- API response time (p99): < 1s
- Throughput: > 100 req/s
- Error rate: < 0.1%

## CI/CD Integration

### GitHub Actions

Example workflow for running tests in CI:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test:ci

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### Pre-commit Hooks

Use Husky to run tests before commits:

```bash
# Install Husky
npm install --save-dev husky

# Setup pre-commit hook
npx husky add .husky/pre-commit "npm test -- --onlyChanged"
```

## Troubleshooting

### Common Issues

1. **Tests timing out**
   ```typescript
   // Increase timeout for slow tests
   it('should complete', async () => {
     // ...
   }, 10000) // 10 second timeout
   ```

2. **Mock not working**
   ```typescript
   // Clear mocks between tests
   beforeEach(() => {
     jest.clearAllMocks()
   })
   ```

3. **Act warnings**
   ```typescript
   // Wrap state updates in act
   await waitFor(() => {
     expect(screen.getByText('Updated')).toBeInTheDocument()
   })
   ```

4. **Module resolution errors**
   - Check `jest.config.js` moduleNameMapper
   - Ensure tsconfig paths match

### Debug Mode

```bash
# Run Jest in debug mode
node --inspect-brk node_modules/.bin/jest --runInBand

# Then open chrome://inspect in Chrome
```

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Next.js Testing](https://nextjs.org/docs/testing)
- [Accessibility Testing](https://www.w3.org/WAI/test-evaluate/)
