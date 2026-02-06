# CI/CD Integration Summary

## Overview

This document summarizes the CI/CD integration for the call-coach project, implementing comprehensive automated testing and quality gates.

## Implemented Components

### 1. GitHub Actions Workflows

#### Backend Test Workflow (`.github/workflows/test-backend.yml`)

**Purpose**: Run all Python backend tests on push/PR

**Jobs**:

- **lint**: Ruff, Black, and isort checks
- **type-check**: MyPy static type analysis
- **unit-tests**: pytest unit tests with coverage (Python 3.11 & 3.12)
  - Coverage threshold: 70% minimum
  - Runs on matrix: Python 3.11 and 3.12
  - Uploads to Codecov with flags: `backend,python-{version}`
- **integration-tests**: Integration tests (requires unit tests to pass)
- **security-scan**: Bandit security scanning and dependency vulnerability checks
- **backend-tests-summary**: Aggregates all job results

**Triggers**:

- Push to `main` or `develop` branches (Python files only)
- Pull requests to `main` or `develop` (Python files only)

**Features**:

- Parallel execution for faster feedback
- Fail-fast disabled to see all failures
- Comprehensive error reporting
- Coverage reporting to Codecov

#### Frontend Test Workflow (`.github/workflows/test-frontend.yml`)

**Purpose**: Run all TypeScript/React frontend tests on push/PR

**Jobs**:

- **lint**: ESLint and TypeScript compilation checks
- **unit-tests**: Jest unit tests with coverage
  - Coverage threshold: 70% minimum
  - Uploads to Codecov with flag: `frontend`
- **accessibility-tests**: Jest-axe accessibility tests
- **build-check**: Next.js production build verification
- **frontend-tests-summary**: Aggregates all job results

**Triggers**:

- Push to `main` or `develop` branches (frontend files only)
- Pull requests to `main` or `develop` (frontend files only)

**Features**:

- Separate accessibility testing job
- Build verification to catch production issues early
- Bundle size analysis

#### Test Enforcement Workflow (`.github/workflows/enforce-tests.yml`)

**Purpose**: Block PRs that don't meet quality standards

**Jobs**:

- **block-on-test-failure**: Validates all required checks passed
  - Checks backend test status
  - Checks frontend test status
  - Checks coverage status

**Triggers**:

- Pull requests to `main` or `develop`

**Features**:

- Uses GitHub API to query check status
- Fails the PR if any required check fails
- Provides clear error messages

### 2. Codecov Integration (`.codecov.yml`)

**Configuration**:

- Project coverage target: 70% minimum
- Patch coverage target: 70% minimum
- Separate flags for backend and frontend
- Ignores test files and vendored code

**Features**:

- Automatic coverage comments on PRs
- Coverage diff visualization
- Flag-based coverage tracking
- GitHub checks integration

**Coverage Paths**:

- Backend: `analysis/`, `coaching_mcp/`, `api/`, `gong/`, `db/`
- Frontend: `frontend/`

### 3. Pre-commit Hooks (`.pre-commit-config.yaml`)

**Added Tests Hooks**:

- **pytest-quick**: Runs fast backend tests on Python file changes
  - Excludes slow, integration, and e2e tests
  - Fails fast after 3 failures
  - Only runs if Python files changed
- **jest-quick**: Runs related frontend tests on TypeScript file changes
  - Uses Jest's `--findRelatedTests` for fast feedback
  - Passes with no tests if no test files found
  - Only runs if frontend files changed

**Other Hooks** (existing):

- Black, Ruff, isort for Python
- Prettier for TypeScript/JavaScript
- MyPy for type checking
- Bandit for security scanning
- General file checks (YAML, JSON, TOML)

### 4. Documentation

#### README.md Updates

- Added coverage badge
- Added backend and frontend test workflow badges
- Added comprehensive Testing section with:
  - Running tests locally
  - CI/CD pipeline overview
  - Coverage report access
  - Coverage targets

#### Branch Protection Guide (`docs/BRANCH_PROTECTION.md`)

- Step-by-step instructions for GitHub settings
- Required status checks list
- Configuration for `main` and `develop` branches
- Troubleshooting guide
- Emergency override procedures

#### Setup Script (`scripts/setup-ci-cd.sh`)

- Automated local CI/CD setup
- Validates required tools
- Installs pre-commit hooks
- Checks workflow files
- Provides next-steps guidance
- Tests backend and frontend setup

## Required GitHub Configuration

### Secrets

Add these secrets in GitHub repository settings (`Settings > Secrets and variables > Actions`):

```
CODECOV_TOKEN=<token-from-codecov-dashboard>
```

### Branch Protection Rules

Configure for both `main` and `develop` branches (`Settings > Branches > Add rule`):

**Required Status Checks**:

- ✅ `Backend Tests Summary`
- ✅ `Frontend Tests Summary`
- ✅ `Enforce Test Quality / Block Merge on Test Failures`
- ✅ `codecov/project`
- ✅ `codecov/patch`

**Other Settings**:

- ✅ Require pull request reviews: 1 approval
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Include administrators

See [docs/BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) for detailed instructions.

## Testing Standards

### Coverage Requirements

| Component | Minimum | Target |
| --------- | ------- | ------ |
| Backend   | 70%     | 80%    |
| Frontend  | 70%     | 75%    |
| Overall   | 70%     | 80%    |

### Test Types

**Backend**:

- Unit tests: Fast, isolated tests (< 1s each)
- Integration tests: Database, API, external service tests
- E2E tests: Full flow tests with Playwright

**Frontend**:

- Unit tests: Component and hook tests
- Accessibility tests: Jest-axe checks
- Build tests: Production build verification

### Test Markers

Use pytest markers to categorize tests:

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (> 5s)
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.asyncio` - Async tests

## Workflow Execution

### Local Development

```bash
# Install pre-commit hooks
./scripts/setup-ci-cd.sh

# Run tests before commit
pytest tests/ -m "not slow and not integration"
cd frontend && npm test

# Or let pre-commit run automatically
git commit -m "your message"
```

### Pull Request Flow

1. Developer pushes branch
2. GitHub Actions triggers:
   - Backend tests (if Python files changed)
   - Frontend tests (if frontend files changed)
3. Tests run in parallel
4. Coverage uploaded to Codecov
5. Codecov comments on PR with coverage diff
6. All required checks must pass (green ✓)
7. Merge button enabled only if:
   - All tests passed
   - Coverage threshold met
   - Approvals received
   - Branch is up-to-date

### Merge Protection

PRs **cannot** be merged if:

- Any backend test fails
- Any frontend test fails
- Coverage drops below 70%
- Build fails
- Security scan finds critical issues

## Performance Characteristics

### Workflow Duration

| Workflow             | Duration      | Timeout |
| -------------------- | ------------- | ------- |
| Backend Lint         | 2-3 min       | 15 min  |
| Backend Type Check   | 3-4 min       | 15 min  |
| Backend Unit Tests   | 5-10 min      | 30 min  |
| Backend Integration  | 5-10 min      | 30 min  |
| Frontend Lint        | 1-2 min       | 15 min  |
| Frontend Unit Tests  | 3-5 min       | 30 min  |
| Frontend Build       | 2-3 min       | 20 min  |
| **Total (parallel)** | **10-15 min** | N/A     |

### Resource Usage

- **Concurrent workflows**: Up to 5 (GitHub Actions default)
- **Matrix builds**: Python 3.11 and 3.12 in parallel
- **Caching**: pip and npm caches enabled
- **Artifacts**: Coverage reports stored for 90 days

## Monitoring and Alerts

### Codecov Dashboard

Monitor at: `https://codecov.io/gh/gabcoyne/call-coach`

**Alerts**:

- Coverage drops below 70%
- Patch coverage below 70%
- Large uncovered changes

### GitHub Actions

Monitor at: Repository > Actions tab

**Alerts**:

- Workflow failures
- Timeout issues
- Dependency vulnerabilities

## Troubleshooting

### Common Issues

**Tests pass locally but fail in CI**:

- Check environment variables
- Verify Python/Node versions match
- Check for timing-dependent tests
- Review CI logs for specific error

**Coverage threshold not met**:

- Run locally: `pytest --cov --cov-report=term-missing`
- Identify uncovered lines
- Add tests for uncovered code
- Or update threshold if reasonable

**Pre-commit hooks failing**:

- Run: `pre-commit run --all-files`
- Fix issues identified
- Commit again

**Status checks not appearing**:

- Ensure workflows ran at least once
- Check workflow file syntax
- Verify triggers match changed files

## Maintenance

### Weekly Tasks

- Review failed workflows and fix root causes
- Monitor coverage trends
- Update dependencies in workflows

### Monthly Tasks

- Review and update coverage thresholds
- Audit branch protection rules
- Update documentation as needed

### Quarterly Tasks

- Upgrade GitHub Actions versions
- Review test performance and optimize
- Evaluate new testing tools

## Related Documentation

- [Branch Protection Setup](BRANCH_PROTECTION.md)
- [Testing Guide](testing-guide.md) (if exists)
- [Code Review Checklist](code-review.md) (if exists)
- [Setup Script](../scripts/setup-ci-cd.sh)

## Change Log

| Date       | Change                    | Author                  |
| ---------- | ------------------------- | ----------------------- |
| 2026-02-05 | Initial CI/CD integration | ci-cd-integration agent |

## Questions or Issues

For questions or issues with CI/CD:

1. Check this documentation
2. Review [docs/BRANCH_PROTECTION.md](BRANCH_PROTECTION.md)
3. Check workflow logs in GitHub Actions
4. Review Codecov dashboard
5. Contact DevOps team
