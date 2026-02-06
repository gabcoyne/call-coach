# CI/CD Quick Reference

Quick commands and cheat sheet for working with the CI/CD pipeline.

## Quick Commands

### Run Tests Locally

```bash
# Backend - All tests
pytest tests/ --cov --cov-report=term-missing

# Backend - Fast tests only
pytest tests/ -m "not slow and not integration and not e2e"

# Backend - Integration tests
pytest tests/ -m integration

# Backend - With parallel execution
pytest tests/ -n auto

# Frontend - All tests
cd frontend && npm test

# Frontend - With coverage
cd frontend && npm run test:coverage

# Frontend - Watch mode
cd frontend && npm run test:watch
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run pytest-quick

# Bypass hooks (use sparingly)
git commit --no-verify
```

### Setup and Verification

```bash
# Initial setup
./scripts/setup-ci-cd.sh

# Verify everything is configured
./scripts/verify-ci-cd.sh
```

## Coverage Commands

```bash
# Generate HTML coverage report (backend)
pytest --cov --cov-report=html
open htmlcov/index.html

# Generate HTML coverage report (frontend)
cd frontend
npm run test:coverage
open coverage/lcov-report/index.html

# Check coverage threshold
pytest --cov --cov-fail-under=70
```

## Workflow Status

Check workflow status:

- GitHub: Repository > Actions tab
- Codecov: <https://codecov.io/gh/gabcoyne/call-coach>

## Required Status Checks

For merge approval, these must pass:

- ✅ Backend Tests Summary
- ✅ Frontend Tests Summary
- ✅ Enforce Test Quality
- ✅ codecov/project (70% min)
- ✅ codecov/patch (70% min)

## Common Issues

### Workflows not triggering

```bash
# Check file paths
git diff --name-only origin/develop

# Manually trigger workflow
# Go to: Actions > Select workflow > Run workflow
```

### Coverage threshold not met

```bash
# Find uncovered lines
pytest --cov --cov-report=term-missing | grep -A 5 "TOTAL"

# Generate detailed report
pytest --cov --cov-report=html
open htmlcov/index.html
```

### Pre-commit hooks failing

```bash
# See what failed
pre-commit run --all-files

# Fix and retry
git add .
git commit -m "your message"
```

### Tests pass locally but fail in CI

```bash
# Check environment differences
cat .github/workflows/test-backend.yml | grep -A 10 "env:"

# Run tests in same Python version as CI
pyenv local 3.11
pytest tests/
```

## File Locations

| Purpose                 | File                                  |
| ----------------------- | ------------------------------------- |
| Backend workflow        | `.github/workflows/test-backend.yml`  |
| Frontend workflow       | `.github/workflows/test-frontend.yml` |
| Merge blocking          | `.github/workflows/enforce-tests.yml` |
| Coverage config         | `.codecov.yml`                        |
| Pre-commit hooks        | `.pre-commit-config.yaml`             |
| Setup script            | `scripts/setup-ci-cd.sh`              |
| Verification script     | `scripts/verify-ci-cd.sh`             |
| Branch protection guide | `docs/BRANCH_PROTECTION.md`           |
| Full CI/CD docs         | `docs/CI_CD_INTEGRATION.md`           |

## Environment Variables

### Local Development

```bash
# Required for backend tests
export DATABASE_URL="postgresql://..."
export GONG_API_KEY="..."
export GONG_API_SECRET="..."
export ANTHROPIC_API_KEY="..."

# Required for frontend tests
cd frontend
cp .env.local.example .env.local
# Edit .env.local with your values
```

### GitHub Secrets (Required)

```
CODECOV_TOKEN=<from-codecov-dashboard>
```

### GitHub Secrets (Optional)

```
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=test-password
TEST_CALL_ID=1234567890
TEST_REP_EMAIL=sarah@example.com
```

## Bypassing Checks (Emergency Only)

### Skip CI entirely

```bash
git commit -m "docs: Update README [skip ci]"
```

### Skip pre-commit hooks

```bash
git commit --no-verify
```

### Override branch protection

- Requires admin privileges
- Go to: PR > Merge button > Override
- **Must** file follow-up issue

## Coverage Targets

| Component | Minimum | Target | Blocks Merge |
| --------- | ------- | ------ | ------------ |
| Backend   | 70%     | 80%    | Yes if < 70% |
| Frontend  | 70%     | 75%    | Yes if < 70% |
| Overall   | 70%     | 80%    | Yes if < 70% |

## Test Markers (Backend)

```python
@pytest.mark.integration   # Integration tests
@pytest.mark.slow         # Slow tests (> 5s)
@pytest.mark.e2e          # End-to-end tests
@pytest.mark.performance  # Performance tests
@pytest.mark.asyncio      # Async tests
```

Run specific markers:

```bash
pytest tests/ -m integration
pytest tests/ -m "not slow and not integration"
```

## Workflow Timeouts

| Workflow            | Timeout | Expected Duration |
| ------------------- | ------- | ----------------- |
| Backend lint        | 15 min  | 2-3 min           |
| Backend type-check  | 15 min  | 3-4 min           |
| Backend unit tests  | 30 min  | 5-10 min          |
| Backend integration | 30 min  | 5-10 min          |
| Frontend lint       | 15 min  | 1-2 min           |
| Frontend unit tests | 30 min  | 3-5 min           |
| Frontend build      | 20 min  | 2-3 min           |

## Getting Help

1. Check this quick reference
2. Review full docs: `docs/CI_CD_INTEGRATION.md`
3. Check workflow logs: Repository > Actions
4. Review Codecov dashboard
5. See branch protection guide: `docs/BRANCH_PROTECTION.md`

## Useful Links

- Workflows: <https://github.com/gabcoyne/call-coach/actions>
- Coverage: <https://codecov.io/gh/gabcoyne/call-coach>
- Branch Rules: <https://github.com/gabcoyne/call-coach/settings/branches>
- Secrets: <https://github.com/gabcoyne/call-coach/settings/secrets/actions>

## Version

**Last Updated**: 2026-02-05
**CI/CD Version**: 1.0
**Maintained by**: DevOps Team
