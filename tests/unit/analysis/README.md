# Analysis Engine Unit Tests - TDD Wave 2

This directory contains comprehensive TDD unit tests for the analysis engine, covering tasks 2.1-2.5 of the TDD Parallel Wave 2 project.

## Test Coverage

### File: `test_analysis_engine.py`

The test file contains 17 comprehensive tests organized into 5 test classes:

#### 1. TestGeneratePromptForDimension (6 tests) - Task 2.1

Tests prompt generation for each coaching dimension:

- ✅ `test_generate_prompt_discovery` - Validates discovery prompt structure and content
- ✅ `test_generate_prompt_engagement` - Validates engagement prompt structure
- ✅ `test_generate_prompt_objection_handling` - Validates objection handling prompt
- ✅ `test_generate_prompt_product_knowledge_requires_kb` - Tests knowledge base inclusion
- ✅ `test_generate_prompt_product_knowledge_without_kb_raises_error` - Tests error on missing KB
- ✅ `test_generate_prompt_includes_role_context` - Validates role-specific context inclusion

#### 2. TestRunClaudeAnalysisMocked (3 tests) - Task 2.2

Tests Claude API integration with mocked responses:

- ✅ `test_run_claude_analysis_returns_parsed_json` - Tests API call and JSON parsing
- ✅ `test_run_claude_analysis_handles_json_in_markdown` - Tests markdown extraction
- ✅ `test_run_claude_analysis_tracks_cache_tokens` - Tests usage metrics tracking

#### 3. TestCacheHitPreventsApiCall (2 tests) - Task 2.3

Tests cache hit scenarios:

- ✅ `test_cache_hit_returns_cached_result_without_api_call` - Validates cache retrieval
- ✅ `test_cache_disabled_always_runs_analysis` - Tests cache disable functionality

#### 4. TestCacheMissTriggersApiCall (2 tests) - Task 2.4

Tests cache miss scenarios:

- ✅ `test_cache_miss_calls_api_and_stores_result` - Validates API call on cache miss
- ✅ `test_force_reanalysis_bypasses_cache` - Tests force reanalysis flag

#### 5. TestMalformedResponseError (4 tests) - Task 2.5

Tests error handling for malformed responses:

- ✅ `test_malformed_json_raises_value_error` - Tests invalid JSON error handling
- ✅ `test_non_json_response_without_code_block_raises_error` - Tests non-JSON response
- ✅ `test_malformed_json_in_markdown_raises_error` - Tests malformed markdown JSON
- ✅ `test_api_error_is_propagated` - Tests API error propagation

## Running the Tests

To run these tests:

```bash
# Run all tests in the file
.venv/bin/python -m pytest tests/unit/analysis/test_analysis_engine.py -v -p no:xdist

# Run a specific test class
.venv/bin/python -m pytest tests/unit/analysis/test_analysis_engine.py::TestGeneratePromptForDimension -v -p no:xdist

# Run a specific test
.venv/bin/python -m pytest tests/unit/analysis/test_analysis_engine.py::TestGeneratePromptForDimension::test_generate_prompt_discovery -v -p no:xdist
```

**Note**: The `-p no:xdist` flag is required to disable parallel execution which can cause import issues with the current project setup.

## Test Results

**Status**: ✅ ALL TESTS PASSING (17/17)

All tests passed on first run, indicating that the existing implementation of the analysis engine already satisfies all TDD requirements for:

- Prompt generation across all coaching dimensions
- Claude API integration with proper mocking
- Cache hit/miss logic
- Error handling for malformed responses

## Test Strategy

These tests follow TDD best practices:

1. **Comprehensive Mocking**: All external dependencies (Claude API, database, cache) are mocked
2. **Isolated Testing**: Each test is independent and doesn't depend on external state
3. **Clear Assertions**: Tests verify specific behaviors with descriptive assertions
4. **Error Path Testing**: Includes tests for both happy path and error scenarios
5. **Fixture Usage**: Common test data is provided via pytest fixtures for reusability

## Dependencies

The tests require the following to be properly set up:

- Package installed in editable mode: `uv pip install -e .`
- All dev dependencies from pyproject.toml
- pytest plugins: pytest-mock for mocking support

## TDD Workflow Followed

1. **Write Test First**: Tests were written based on the specifications in OpenSpec
2. **Run Tests**: Verified tests pass against existing implementation
3. **Refactor if Needed**: Tests validate that implementation meets all requirements

This ensures the analysis engine behavior is documented and protected against regressions.
