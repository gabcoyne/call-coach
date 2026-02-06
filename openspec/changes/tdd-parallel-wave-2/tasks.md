# TDD Parallel Wave 2 Tasks

## 1. Test Infrastructure Setup

- [x] 1.1 Install backend test dependencies (pytest, pytest-asyncio,
      pytest-xdist, pytest-mock, pytest-cov, faker)
- [x] 1.2 Install frontend test dependencies (@testing-library/react,
      @testing-library/jest-dom, @testing-library/user-event, msw)
- [x] 1.3 Configure pytest.ini with parallel execution and coverage settings
- [x] 1.4 Update jest.config.js with coverage thresholds and test patterns
- [x] 1.5 Create Docker Compose file for test database (Postgres)
- [x] 1.6 Create pytest fixtures for database connection and cleanup (tests/fixtures/conftest.py)
- [x] 1.7 Create test data factories (tests/fixtures/factories.py)
- [x] 1.8 Set up MSW handlers for mocking external APIs (frontend/**mocks**/handlers.ts)

## 2. Backend Unit Tests - Analysis Engine

- [x] 2.1 Write test for prompt generation (test_analysis_engine.py::test_generate_prompt_for_dimension)
- [x] 2.2 Write test for Claude API call with mocked response (test_analysis_engine.py::test_run_claude_analysis_mocked)
- [x] 2.3 Write test for cache hit scenario (test_analysis_engine.py::test_cache_hit_prevents_api_call)
- [x] 2.4 Write test for cache miss scenario (test_analysis_engine.py::test_cache_miss_triggers_api_call)
- [x] 2.5 Write test for malformed Claude response error handling (test_analysis_engine.py::test_malformed_response_error)

## 3. Backend Unit Tests - Cache Module

- [x] 3.1 Write test for Redis available scenario (test_cache.py::test_redis_available_operations)
- [x] 3.2 Write test for Redis unavailable graceful degradation (test_cache.py::test_redis_unavailable_fallback)
- [x] 3.3 Write test for cache key generation consistency (test_cache.py::test_cache_key_deterministic)
- [x] 3.4 Write test for cache invalidation by dimension (test_cache.py::test_invalidate_dimension)

## 4. Backend Unit Tests - Database Module

- [x] 4.1 Write test for connection pool initialization (test_database.py::test_connection_pool_init)
- [x] 4.2 Write test for parameterized query execution (test_database.py::test_query_execution_with_params)
- [x] 4.3 Write test for transaction rollback on error (test_database.py::test_transaction_rollback)
- [x] 4.4 Write test for connection timeout handling (test_database.py::test_connection_timeout_retry)

## 5. Backend Unit Tests - MCP Tools

- [ ] 5.1 Write test for analyze_call with valid parameters (test_mcp_tools.py::test_analyze_call_valid)
- [ ] 5.2 Write test for get_rep_insights with time filtering (test_mcp_tools.py::test_rep_insights_time_filter)
- [ ] 5.3 Write test for search_calls with complex filters (test_mcp_tools.py::test_search_calls_complex_filters)
- [ ] 5.4 Write test for tool parameter validation (test_mcp_tools.py::test_tool_validation_error)

## 6. Middleware Fixes and Tests

- [ ] 6.1 Refactor RateLimitMiddleware to use FastAPI dependency injection
- [ ] 6.2 Write test for rate limit enforcement (test_rate_limit.py::test_rate_limit_enforced)
- [ ] 6.3 Write test for rate limit headers (test_rate_limit.py::test_rate_limit_headers)
- [ ] 6.4 Write test for per-endpoint rate limits (test_rate_limit.py::test_per_endpoint_limits)
- [ ] 6.5 Write test for per-user rate limiting (test_rate_limit.py::test_per_user_limits)
- [ ] 6.6 Write test for rate limit reset (test_rate_limit.py::test_rate_limit_reset)
- [ ] 6.7 Refactor CompressionMiddleware to use dependency injection
- [ ] 6.8 Write test for compression above threshold (test_compression.py::test_large_response_compressed)
- [ ] 6.9 Write test for no compression below threshold (test_compression.py::test_small_response_not_compressed)
- [ ] 6.10 Write test for compression with client support check (test_compression.py::test_client_without_gzip)

## 7. Backend Integration Tests

- [ ] 7.1 Write integration test for POST endpoint creates DB record (test_api_integration.py::test_post_creates_record)
- [ ] 7.2 Write integration test for GET endpoint retrieves record (test_api_integration.py::test_get_retrieves_record)
- [ ] 7.3 Write integration test for auth required (test_api_integration.py::test_auth_required)
- [ ] 7.4 Write integration test for transaction commit (test_database_integration.py::test_transaction_commit)
- [ ] 7.5 Write integration test for transaction rollback (test_database_integration.py::test_transaction_rollback)
- [ ] 7.6 Write integration test for connection pool under load (test_database_integration.py::test_connection_pool_load)

## 8. Frontend Unit Tests - Components

- [ ] 8.1 Write test for ScoreTrendChart renders with data (ScoreTrendChart.test.tsx::test_renders_with_props)
- [ ] 8.2 Write test for SkillGapRadar user interaction (SkillGapRadar.test.tsx::test_user_interaction)
- [ ] 8.3 Write test for TeamComparisonBar async data loading (TeamComparisonBar.test.tsx::test_async_loading)
- [ ] 8.4 Write test for ActivityTimeline component (ActivityTimeline.test.tsx::test_activity_timeline)
- [ ] 8.5 Write test for ObjectionBreakdown component (ObjectionBreakdown.test.tsx::test_objection_breakdown)
- [ ] 8.6 Write test for CallAnalysisViewer component (CallAnalysisViewer.test.tsx::test_call_analysis_viewer)

## 9. Frontend Unit Tests - Hooks

- [ ] 9.1 Write test for useRepInsights hook initial state (useRepInsights.test.tsx::test_initial_state)
- [ ] 9.2 Write test for useRepInsights hook updates (useRepInsights.test.tsx::test_state_updates)
- [ ] 9.3 Write test for useCallAnalysis hook (useCallAnalysis.test.tsx::test_call_analysis_hook)
- [ ] 9.4 Write test for custom hooks error handling (useRepInsights.test.tsx::test_error_handling)

## 10. Frontend Unit Tests - Utilities

- [ ] 10.1 Write test for utility functions with valid input (utils.test.ts::test_utils_valid_input)
- [ ] 10.2 Write test for utility functions with edge cases (utils.test.ts::test_utils_edge_cases)
- [ ] 10.3 Write test for auth utilities (auth.test.ts::test_auth_utilities)

## 11. Frontend Integration Tests

- [ ] 11.1 Write integration test for API route handler success (api-routes.test.ts::test_route_handler_success)
- [ ] 11.2 Write integration test for API route validation error (api-routes.test.ts::test_route_validation_error)
- [ ] 11.3 Write integration test for API route DB interaction (api-routes.test.ts::test_route_database_query)
- [ ] 11.4 Write integration test for login to dashboard workflow (user-workflows.test.tsx::test_login_dashboard)
- [ ] 11.5 Write integration test for create coaching session workflow (user-workflows.test.tsx::test_create_session)

## 12. End-to-End API Tests

- [ ] 12.1 Write E2E test for complete coaching analysis flow (test_e2e_coaching.py::test_coaching_analysis_flow)
- [ ] 12.2 Write E2E test for error propagation (test_e2e_coaching.py::test_error_propagation)
- [ ] 12.3 Write performance test for API response time under load (test_performance.py::test_api_load)
- [ ] 12.4 Write performance test for database query optimization (test_performance.py::test_database_query_performance)

## 13. CI/CD Integration

- [ ] 13.1 Update GitHub Actions workflow with backend test job (.github/workflows/test-backend.yml)
- [ ] 13.2 Update GitHub Actions workflow with frontend test job (.github/workflows/test-frontend.yml)
- [ ] 13.3 Add coverage reporting to CI (codecov or coveralls integration)
- [ ] 13.4 Configure CI to block merges on test failure
- [ ] 13.5 Add coverage badge to README.md
- [ ] 13.6 Update pre-commit hooks to run test suite (.pre-commit-config.yaml)

## 14. Documentation

- [ ] 14.1 Write testing guide explaining TDD workflow (docs/testing-guide.md)
- [ ] 14.2 Add test examples for each test type to documentation
- [ ] 14.3 Document how to run tests locally (README.md section)
- [ ] 14.4 Document how to debug failing tests (docs/testing-guide.md)
- [ ] 14.5 Create code review checklist including test quality criteria (docs/code-review.md)

## 15. Verification and Cleanup

- [ ] 15.1 Run full backend test suite and verify 85%+ coverage
- [ ] 15.2 Run full frontend test suite and verify 75%+ coverage
- [ ] 15.3 Verify all middleware works correctly in dev environment
- [ ] 15.4 Verify CI pipeline executes tests successfully
- [ ] 15.5 Verify pre-commit hooks block commits on test failure
- [ ] 15.6 Clean up any skipped or disabled tests
- [ ] 15.7 Run performance tests and document baseline metrics
