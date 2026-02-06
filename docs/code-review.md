# Code Review Checklist

A comprehensive checklist for reviewing code changes in the Gong Call Coaching application, with special emphasis on test quality and test-driven development practices.

## Quick Reference

Before approving any pull request, verify:

- [ ] Tests were written before implementation (TDD followed)
- [ ] All tests pass in CI
- [ ] Coverage thresholds are met (85% backend, 75% frontend)
- [ ] Code follows project conventions
- [ ] Changes are well-documented

---

## Table of Contents

1. [Test Quality](#test-quality)
2. [Code Quality](#code-quality)
3. [Architecture & Design](#architecture--design)
4. [Performance](#performance)
5. [Security](#security)
6. [Documentation](#documentation)
7. [CI/CD](#cicd)
8. [Review Process](#review-process)

---

## Test Quality

### Test-Driven Development (TDD)

**Critical:** Verify tests were written BEFORE implementation.

- [ ] **Git history shows tests committed first**

  - Check: `git log --oneline --follow path/to/test_file.py`
  - Test file should have earlier or same commit timestamp as implementation
  - Exception: Bug fixes may have test and fix in same commit

- [ ] **Tests fail without implementation**

  - Ask: "Did you verify the test failed before implementing?"
  - Red-Green-Refactor cycle should be evident

- [ ] **Test describes requirements clearly**
  - Test name explains what feature does
  - Test can serve as documentation

**Red flags:**

- Implementation file committed before test file
- Author says "I'll add tests later"
- Tests added in separate PR after feature merge

### Test Coverage

**Quantitative checks:**

- [ ] **Backend coverage ≥ 85%**

  - View coverage report in CI artifacts
  - Check `htmlcov/index.html` locally
  - Identify uncovered lines and branches

- [ ] **Frontend coverage ≥ 75%**

  - View coverage report in CI artifacts
  - Check `coverage/lcov-report/index.html` locally

- [ ] **New code is tested**

  - Run: `pytest tests/ --cov=module --cov-report=term-missing`
  - Focus on changed files, not overall percentage
  - Critical paths should have 95%+ coverage

- [ ] **Coverage didn't decrease**
  - Compare before/after coverage percentages
  - Small decreases acceptable for refactoring
  - Large decreases (>5%) need justification

**What should be covered:**

- ✅ Business logic
- ✅ API endpoints
- ✅ Database operations
- ✅ Error handling
- ✅ Edge cases
- ✅ Critical paths

**What doesn't need coverage:**

- ❌ Simple getters/setters
- ❌ Third-party library code
- ❌ Generated code
- ❌ Obvious pass-throughs

### Test Types & Structure

**Unit tests:**

- [ ] **Tests are isolated**

  - No dependencies between tests
  - Tests can run in any order
  - Each test has its own setup

- [ ] **Tests are fast**

  - Unit tests: < 100ms each
  - Integration tests: < 2s each
  - Total suite: < 2 minutes

- [ ] **External dependencies are mocked**

  - Claude API calls mocked
  - Gong API calls mocked
  - Clerk auth mocked
  - Database used real (for integration tests only)

- [ ] **Tests follow Arrange-Act-Assert**

  ```python
  def test_example():
      # ARRANGE: Set up test data
      data = create_test_data()

      # ACT: Perform action
      result = function_under_test(data)

      # ASSERT: Verify outcome
      assert result == expected
  ```

**Integration tests:**

- [ ] **Tests use real database**

  - Database fixtures create test schema
  - Transactions rolled back after test
  - No pollution between tests

- [ ] **Tests verify component interactions**

  - API → Service → Database
  - Multiple modules working together
  - Data flows correctly

- [ ] **External APIs still mocked**
  - Only internal components use real implementations

**End-to-end tests:**

- [ ] **Tests simulate user workflows**

  - Complete user journey tested
  - Multiple steps in sequence
  - Real-world scenarios

- [ ] **Tests are deterministic**
  - No random failures
  - No timing dependencies
  - Repeatable results

### Test Quality

**Naming:**

- [ ] **Test names are descriptive**

  - Format: `test_<action>_<condition>_<expected_result>`
  - Examples:
    - ✅ `test_cache_hit_prevents_api_call`
    - ✅ `test_missing_call_id_raises_value_error`
    - ❌ `test_cache` (too vague)
    - ❌ `test_1` (meaningless)

- [ ] **Docstrings explain purpose**

  ```python
  def test_cache_hit_prevents_api_call():
      """Verify cached results skip Claude API call."""
  ```

**Assertions:**

- [ ] **Tests verify behavior, not implementation**

  ```python
  # ✅ Good: Tests what it does
  assert result.status == "completed"
  assert len(result.insights) > 0

  # ❌ Bad: Tests how it works
  assert result._internal_cache is not None
  assert result._api_client.called
  ```

- [ ] **Error messages are clear**

  ```python
  # ✅ Good
  assert score >= 0, f"Score {score} should be non-negative"

  # ❌ Bad
  assert score >= 0  # No context if it fails
  ```

- [ ] **Assertions are specific**

  ```python
  # ✅ Good
  assert result["scores"]["discovery"] == 85
  assert "strengths" in result
  assert len(result["action_items"]) == 3

  # ❌ Bad
  assert result  # Too broad
  ```

**Test Data:**

- [ ] **Uses fixtures or factories**

  ```python
  # ✅ Good: Reusable fixture
  @pytest.fixture
  def sample_call():
      return CallFactory.create()

  def test_analyze_call(sample_call):
      result = analyze(sample_call)
      assert result

  # ❌ Bad: Inline data
  def test_analyze_call():
      call = {"id": "123", "title": "Call", ...}  # Repetitive
      result = analyze(call)
      assert result
  ```

- [ ] **Test data is realistic**

  - Valid UUIDs for IDs
  - Proper timestamps
  - Realistic string lengths
  - Valid enum values

- [ ] **Test data doesn't duplicate production data**
  - No real customer data
  - No real API keys
  - No real email addresses

**Mocking:**

- [ ] **Mocks are used appropriately**

  - Patch where used, not where defined
  - Mock external services only
  - Verify mock was called

- [ ] **Mock responses are realistic**

  ```python
  # ✅ Good: Realistic Claude response
  mock_response = {
      "scores": {"discovery": 85},
      "strengths": ["Asked open-ended questions"],
      "areas_for_improvement": ["Better discovery"]
  }

  # ❌ Bad: Minimal/unrealistic
  mock_response = {}  # Won't catch real issues
  ```

- [ ] **Mocks don't hide bugs**
  - Test verifies important behavior
  - Not just "does it run without errors"

### Error Testing

- [ ] **Tests cover error scenarios**

  - Invalid inputs
  - Missing data
  - Network failures
  - API errors
  - Database errors

- [ ] **Error handling is explicit**

  ```python
  # ✅ Good: Explicit error check
  def test_missing_call_id_raises_error():
      with pytest.raises(ValueError, match="call_id is required"):
          analyze_call_tool(call_id=None)

  # ❌ Bad: Implicit
  def test_missing_call_id():
      try:
          analyze_call_tool(call_id=None)
      except:
          pass  # Catches any error, even wrong ones
  ```

- [ ] **Error messages are tested**
  - Verify error message text
  - Helps detect breaking changes

### Test Maintenance

- [ ] **No skipped tests without explanation**

  ```python
  # ✅ Acceptable
  @pytest.mark.skip(reason="Waiting for Gong API v2 support - TICKET-123")
  def test_gong_v2_feature():
      pass

  # ❌ Not acceptable
  @pytest.mark.skip
  def test_something():
      pass
  ```

- [ ] **No commented-out tests**

  - Delete or fix them
  - Git history preserves old code

- [ ] **Tests are maintainable**
  - Not overly complex
  - Not duplicating logic
  - Clear and readable

---

## Code Quality

### General

- [ ] **Code follows style guide**

  - Backend: PEP 8 (enforced by ruff/black)
  - Frontend: Prettier + ESLint rules
  - Consistent naming conventions

- [ ] **No linting errors**

  - Run: `ruff check .` (backend)
  - Run: `npm run lint` (frontend)
  - Fix all warnings/errors

- [ ] **Type hints are used (Python)**

  ```python
  # ✅ Good
  def analyze_call(call_id: str, dimension: str) -> dict[str, Any]:
      ...

  # ❌ Bad
  def analyze_call(call_id, dimension):
      ...
  ```

- [ ] **TypeScript types are explicit (Frontend)**

  ```typescript
  // ✅ Good
  interface CallAnalysis {
    callId: string;
    scores: Record<string, number>;
  }

  // ❌ Bad
  const analysis: any = ...
  ```

### Functions & Methods

- [ ] **Functions do one thing**

  - Single responsibility
  - < 50 lines of code
  - Can be understood in < 1 minute

- [ ] **Functions have clear names**

  - Verbs for actions: `analyze_call`, `fetch_transcript`
  - Nouns for getters: `get_score`, `find_rep`
  - Booleans start with is/has: `is_valid`, `has_cache`

- [ ] **Function signatures are clear**

  - Required parameters first
  - Optional parameters last
  - Reasonable number of parameters (< 5)

- [ ] **No code duplication**
  - DRY principle followed
  - Shared logic extracted to utilities
  - Similar code refactored

### Error Handling

- [ ] **Errors are handled appropriately**

  - Don't swallow exceptions silently
  - Log errors with context
  - Return meaningful error messages

- [ ] **Error types are specific**

  ```python
  # ✅ Good
  raise ValueError(f"Invalid call_id: {call_id}")

  # ❌ Bad
  raise Exception("Error")  # Too generic
  ```

- [ ] **User-facing errors are clear**
  - No stack traces to end users
  - Actionable error messages
  - Include suggestions to fix

### Complexity

- [ ] **Cyclomatic complexity is reasonable**

  - Limit nested ifs/loops
  - Extract complex conditionals to functions
  - Use early returns

- [ ] **Code is readable**
  - Clear variable names
  - Comments explain "why" not "what"
  - No clever/obscure tricks

---

## Architecture & Design

### API Design

- [ ] **Endpoints follow REST conventions**

  - POST for creating resources
  - GET for retrieving
  - PUT/PATCH for updates
  - DELETE for removal

- [ ] **Request/response schemas are validated**

  - Pydantic models (backend)
  - Zod schemas (frontend)
  - Clear error messages for invalid data

- [ ] **Responses are consistent**
  - Standard format across endpoints
  - Consistent error structure
  - Include relevant metadata

### Database

- [ ] **Queries are efficient**

  - No N+1 queries
  - Proper indexes used
  - Pagination for large results

- [ ] **Migrations are safe**

  - No data loss
  - Backwards compatible
  - Tested before deployment

- [ ] **Transactions are used correctly**
  - Atomic operations
  - Rollback on errors
  - No partial state

### Caching

- [ ] **Cache keys are deterministic**

  - Same input = same key
  - Include version in key
  - Clear invalidation strategy

- [ ] **Cache misses are handled**
  - Fallback to source
  - Refresh cache
  - Don't block on cache

### Dependencies

- [ ] **No unnecessary dependencies**

  - Justify new packages
  - Check licensing
  - Review security advisories

- [ ] **Dependencies are pinned**
  - Exact versions in lock files
  - Regular updates scheduled

---

## Performance

### Response Times

- [ ] **API endpoints respond quickly**

  - < 2s for most requests
  - < 5s for complex analysis
  - Use async where appropriate

- [ ] **Database queries are fast**

  - < 100ms for simple queries
  - < 500ms for complex queries
  - Indexes on frequently queried columns

- [ ] **No blocking operations**
  - Long operations are async
  - Background jobs for heavy work
  - Progress indicators for users

### Resource Usage

- [ ] **Memory usage is reasonable**

  - No memory leaks
  - Large datasets streamed
  - Connection pools configured

- [ ] **No expensive operations in loops**
  - Batch database operations
  - Cache repeated calculations
  - Use iterators for large datasets

---

## Security

### Authentication & Authorization

- [ ] **Authentication is required**

  - Protected endpoints have auth checks
  - JWT tokens validated
  - Session management secure

- [ ] **Authorization is enforced**
  - Users can only access their data
  - Role-based access control (RBAC)
  - Manager vs. rep permissions

### Data Protection

- [ ] **No secrets in code**

  - Environment variables used
  - No API keys in source
  - Secrets not logged

- [ ] **Input is validated**

  - SQL injection prevented
  - XSS prevented
  - CSRF tokens used

- [ ] **Sensitive data is protected**
  - PII is encrypted
  - Audit logs for access
  - Data retention policies followed

---

## Documentation

### Code Documentation

- [ ] **Public APIs have docstrings**

  ```python
  def analyze_call(call_id: str, dimension: str) -> dict[str, Any]:
      """
      Analyze a Gong call for a specific coaching dimension.

      Args:
          call_id: Gong call identifier
          dimension: Coaching dimension to analyze

      Returns:
          Dictionary containing scores, strengths, and recommendations

      Raises:
          ValueError: If call_id is invalid
          NotFoundError: If call not found
      """
  ```

- [ ] **Complex logic is explained**
  - Comments explain "why"
  - Non-obvious algorithms documented
  - Edge cases noted

### User Documentation

- [ ] **README is updated**

  - New features documented
  - Setup instructions current
  - Examples provided

- [ ] **API changes documented**
  - Breaking changes highlighted
  - Migration guide provided
  - Deprecation warnings added

### Change Documentation

- [ ] **PR description is complete**

  - What changed and why
  - Testing performed
  - Screenshots for UI changes
  - Links to related tickets

- [ ] **Commit messages are clear**
  - Descriptive, not vague
  - Reference ticket numbers
  - Explain context

---

## CI/CD

### Continuous Integration

- [ ] **All CI checks pass**

  - Tests pass
  - Coverage thresholds met
  - Linting passes
  - Type checking passes

- [ ] **No skipped CI checks**
  - All jobs completed
  - No "will fix later"

### Deployment

- [ ] **Changes are backwards compatible**

  - Database migrations safe
  - API changes versioned
  - Gradual rollout plan

- [ ] **Rollback plan exists**
  - Can revert quickly
  - Data not lost
  - Users not impacted

---

## Review Process

### For Reviewers

**Before starting:**

1. Pull branch locally
2. Run tests: `pytest tests/` and `npm test`
3. Check coverage reports
4. Review git diff

**During review:**

1. Read PR description thoroughly
2. Verify TDD was followed (check git history)
3. Check tests before implementation code
4. Verify all checklist items
5. Test locally if possible
6. Leave specific, actionable feedback

**Feedback guidelines:**

- Be respectful and constructive
- Explain the "why" behind suggestions
- Distinguish between "must fix" and "nice to have"
- Praise good work

**Types of feedback:**

- 🔴 **Blocking:** Must be fixed before merge (security, bugs, missing tests)
- 🟡 **Important:** Should be fixed (code quality, maintainability)
- 🟢 **Nice to have:** Optional improvements (refactoring, style)
- 💬 **Question:** Asking for clarification

**Example feedback:**

```markdown
🔴 **Blocking:** Missing tests for error case

The function `analyze_call` can raise ValueError but there's no test for this scenario.
Please add:
\`\`\`python
def test_analyze_call_invalid_id_raises_error():
with pytest.raises(ValueError):
analyze_call(call_id="invalid")
\`\`\`

🟡 **Important:** Consider extracting this logic

Lines 45-60 duplicate the logic from `cache.py:generate_key()`. Consider extracting
to a shared utility function.

🟢 **Nice to have:** Variable naming

`x` and `y` on line 32 could be more descriptive. Consider `score` and `threshold`.

💬 **Question:** Why async here?

Is this function called in an async context? If not, making it async adds unnecessary
complexity.
```

**Approval criteria:**

- [ ] All tests pass
- [ ] Coverage thresholds met
- [ ] TDD followed
- [ ] No blocking feedback unresolved
- [ ] Code quality acceptable
- [ ] Documentation complete

### For Authors

**Before requesting review:**

1. Self-review your changes
2. Run full test suite locally
3. Check coverage report
4. Run linting/formatting
5. Update documentation
6. Write clear PR description

**Responding to feedback:**

- Thank reviewers for their time
- Address all feedback (or explain why not)
- Ask questions if unclear
- Mark conversations resolved after fixing
- Request re-review after changes

**What to do with feedback:**

- 🔴 Blocking → Must fix before merge
- 🟡 Important → Fix now or create follow-up ticket
- 🟢 Nice to have → Fix if quick, otherwise create ticket
- 💬 Question → Answer clearly

---

## Common Issues

### Tests Added After Implementation

**Problem:** Tests were written after code, not before (violates TDD).

**How to detect:**

- Check git log timestamps
- Test file committed later than implementation
- Author admits tests added later

**Action:**

- 🔴 Block merge
- Request rewrite following TDD process
- Explain importance of TDD

### Low Test Coverage

**Problem:** Coverage below thresholds or new code not tested.

**How to detect:**

- Coverage report in CI
- Changed lines highlighted in coverage report

**Action:**

- 🔴 Block merge if below threshold
- Request specific tests for uncovered lines
- Help identify what needs testing

### Flaky Tests

**Problem:** Tests pass/fail randomly.

**How to detect:**

- Re-run CI multiple times
- Check for timing dependencies
- Look for shared state

**Action:**

- 🔴 Block merge
- Request fix for flakiness
- Suggest debugging techniques

### Tests That Don't Test

**Problem:** Tests exist but don't verify behavior.

**Example:**

```python
def test_analyze_call():
    result = analyze_call("call-123")
    assert result  # Too broad, always passes
```

**Action:**

- 🟡 Request specific assertions
- Explain what should be verified
- Provide examples

### Missing Error Tests

**Problem:** Only happy path tested, errors not covered.

**How to detect:**

- Check for `pytest.raises`
- Review error handling code
- Look for validation logic

**Action:**

- 🟡 Request error tests
- Suggest specific scenarios
- Reference test examples

---

## Quick Reference

**Checklist summary:**

```markdown
## Test Quality

- [ ] TDD followed (tests before implementation)
- [ ] All tests pass
- [ ] Coverage ≥ 85% (backend) / 75% (frontend)
- [ ] Tests are isolated and deterministic
- [ ] External APIs mocked
- [ ] Error cases tested
- [ ] Test names descriptive

## Code Quality

- [ ] No linting errors
- [ ] Type hints/types used
- [ ] No code duplication
- [ ] Error handling appropriate
- [ ] Code readable and maintainable

## Documentation

- [ ] Docstrings for public APIs
- [ ] PR description complete
- [ ] README updated if needed
- [ ] Breaking changes documented

## CI/CD

- [ ] All CI checks pass
- [ ] No skipped checks
- [ ] Backwards compatible
```

---

## References

- [Testing Guide](testing-guide.md) - Comprehensive testing documentation
- [README.md](../README.md) - Running tests locally
- [pytest documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)

---

## Questions?

If you're unsure about any aspect of code review:

1. Check this guide and the Testing Guide
2. Look at recent PRs for examples
3. Ask in #engineering Slack
4. When in doubt, ask the author to clarify

**Remember:** Code review is about improving code quality and sharing knowledge, not finding fault. Be respectful, constructive, and collaborative.
