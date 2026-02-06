## Why

The call coaching application has grown to include multiple backend services (FastAPI REST API, FastMCP server) and a complex Next.js frontend, but lacks comprehensive test coverage. Critical middleware components (rate limiting, compression) are currently disabled due to initialization errors, and many features remain untested. We need a systematic TDD approach executed in parallel by multiple agents to establish robust test coverage, fix broken middleware, and ensure production readiness.

## What Changes

- Implement comprehensive pytest suite for Python backend (API routes, MCP tools, analysis engine, caching)
- Create Jest/React Testing Library suite for Next.js frontend (components, hooks, API routes)
- Fix and test middleware components (rate limiting, compression, authentication)
- Add end-to-end API integration tests with mock data
- Establish TDD workflow with pre-commit hooks and CI/CD integration
- Achieve 80%+ code coverage across backend and frontend
- Add performance and load testing for critical paths
- Create test fixtures and factories for consistent test data

## Capabilities

### New Capabilities

- `backend-unit-tests`: Unit tests for all Python modules (analysis engine, cache, database, MCP tools)
- `backend-integration-tests`: Integration tests for API endpoints and database operations
- `frontend-unit-tests`: Unit tests for React components, hooks, and utility functions
- `frontend-integration-tests`: Integration tests for Next.js API routes and user workflows
- `middleware-testing`: Tests for rate limiting, compression, and auth middleware with fixes
- `e2e-api-tests`: End-to-end API testing with realistic scenarios
- `test-infrastructure`: Pytest/Jest configuration, fixtures, factories, and CI integration
- `tdd-workflow-process`: Documentation and tooling for test-first development

### Modified Capabilities

- `api-middleware`: Fix rate limiting and compression middleware initialization issues (requirements changing to support proper FastAPI/Starlette integration)

## Impact

**Backend Impact**:

- All Python modules in `analysis/`, `api/`, `coaching_mcp/`, `middleware/`, `cache/`, `db/` will have test files
- `pytest.ini` and test configuration updated
- CI/CD pipeline extended with test runs and coverage reporting

**Frontend Impact**:

- All components in `frontend/components/`, `frontend/lib/`, `frontend/app/api/` will have test files
- `jest.config.js` updated with coverage thresholds
- Test utilities and mocking helpers added

**Development Workflow Impact**:

- Pre-commit hooks enforce tests pass before commit
- CI blocks merges if coverage drops below 80%
- New features require tests written first (TDD)

**Dependencies**:

- Add `pytest-asyncio`, `pytest-mock`, `faker` for Python testing
- Add `@testing-library/jest-dom`, `@testing-library/user-event`, `msw` for frontend testing
- Add `pytest-cov` and `jest coverage` reporters

**Systems Affected**:

- GitHub Actions workflows (add test and coverage jobs)
- Development environment setup (test dependencies)
- Documentation (testing guide, TDD workflow)
