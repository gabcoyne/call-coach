# CI/CD Pipeline Setup Guide

This directory contains CI/CD pipeline configuration and utilities for the call-coach project.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and includes:

1. **Test Suite** - Linting, type checking, unit tests, integration tests
2. **Build** - Docker image building and pushing to GitHub Container Registry
3. **Deployment** - Staging and production deployments with database migrations
4. **Security** - Vulnerability scanning, SAST, container scanning, license compliance
5. **Release** - Automated version bumping, changelog generation, GitHub releases
6. **Database Migrations** - Safe migration execution with rollback capabilities

## Workflows

### Test Suite (`.github/workflows/tests.yml`)

Runs on every push to main/develop and on pull requests.

**Jobs:**

- **Lint & Format** - Ruff and Black checks
- **Type Check** - MyPy type checking
- **Unit & Integration Tests** - Pytest with coverage reporting
  - Coverage threshold: 70% minimum
  - Coverage uploaded to Codecov
  - Tests run on Python 3.11 and 3.12

**Triggering:**

```bash
# Automatic on push to main/develop
# Automatic on PR to main/develop
# Only on changes to Python/TypeScript files
```

### Build Workflow (`.github/workflows/build.yml`)

Builds Docker images for MCP server and webhook server.

**Images:**

- `ghcr.io/<owner>/call-coach-mcp:tag`
- `ghcr.io/<owner>/call-coach-webhook:tag`

**Tags:**

- Branch name (e.g., `develop`, `main`)
- Commit SHA with branch prefix (e.g., `develop-abc123def`)
- Semantic version tags for releases

**Permissions Required:**

```
packages: write
contents: read
```

### Staging Deployment (`.github/workflows/deploy-staging.yml`)

Automatically deploys to staging on push to develop branch.

**Steps:**

1. Run database migrations
2. Build Docker images
3. Deploy frontend to Vercel (staging project)
4. Deploy backend to staging infrastructure
5. Run smoke tests

**Required Secrets:**

- `STAGING_DATABASE_URL` - PostgreSQL connection string
- `STAGING_API_URL` - API endpoint for frontend config
- `STAGING_API_ENDPOINT` - Backend health check URL
- `STAGING_WEB_URL` - Frontend URL for testing
- `VERCEL_TOKEN` - Vercel deployment token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID_STAGING` - Vercel project ID for staging
- `STAGING_TEST_USER_EMAIL` - Test credentials
- `STAGING_TEST_USER_PASSWORD` - Test credentials

### Production Deployment (`.github/workflows/deploy-production.yml`)

Triggers on version tags (e.g., `v1.0.0`).

**Steps:**

1. Run full test suite (70% coverage minimum, with 80% enforced for production)
2. Build and push production Docker images
3. Run database migrations with backup
4. Deploy frontend to production
5. Deploy backend to production
6. Create GitHub release with changelog

**Tags:** Must follow semantic versioning: `v[MAJOR].[MINOR].[PATCH]`

Example:

```bash
git tag v1.2.3
git push origin v1.2.3
```

**Required Secrets:**

- `PRODUCTION_DATABASE_URL`
- `PRODUCTION_API_URL`
- `PRODUCTION_API_ENDPOINT`
- `PRODUCTION_DEPLOYMENT_TOKEN`
- All staging secrets

### Database Migration Workflow (`.github/workflows/migrate.yml`)

Safely runs database migrations with rollback capabilities.

**Triggers:**

- Manual trigger via `workflow_dispatch` (specify environment and target version)
- Automatic on changes to migration files in develop/main

**Features:**

- Pre-migration backup creation
- Migration validation
- Post-migration verification
- Automatic rollback on failure
- Migration logging

**Usage:**

Manual trigger via GitHub Actions UI:

```
Workflow: Database Migration
Inputs:
  - environment: staging or production
  - target_version: (optional, defaults to latest)
```

Or via GitHub CLI:

```bash
gh workflow run migrate.yml -f environment=staging
```

### Security Scanning (`.github/workflows/security.yml`)

Comprehensive security checks running on every push and scheduled weekly.

**Checks:**

1. **pip-audit** - Python dependency vulnerability scanning
2. **npm audit** - Node.js dependency vulnerability scanning
3. **Bandit** - Python code security scanning
4. **Semgrep** - Semantic code pattern matching
5. **CodeQL** - GitHub's code analysis (language: Python)
6. **Trivy** - Container image vulnerability scanning
7. **License Compliance** - Check for problematic licenses
8. **Secret Scanning** - TruffleHog secret detection

**Results:**

- SARIF reports uploaded to GitHub Security tab
- Artifacts uploaded for manual review
- Summaries posted in PR comments

### Release Workflow (`.github/workflows/release.yml`)

Automated release process with version bumping and changelog generation.

**Triggers:**

- Manual via `workflow_dispatch` with inputs:
  - Version type: `major`, `minor`, `patch`, or `prerelease`
  - Prerelease suffix (for prerelease versions): `alpha`, `beta`, `rc`

**Steps:**

1. Calculate next version based on type
2. Generate changelog from commits
3. Update version in `pyproject.toml`
4. Create release branch
5. Run full test suite
6. Create git tag
7. Merge to main and develop
8. Create GitHub release
9. Publish to PyPI

**Usage:**

```bash
# Trigger via GitHub CLI
gh workflow run release.yml -f version_type=minor

# Or via Actions UI:
# - Go to Actions
# - Select "Release" workflow
# - Click "Run workflow"
# - Select version type and (optionally) prerelease suffix
```

## Environment Variables

### GitHub Secrets Required

Store these as repository secrets in GitHub Settings:

**Database:**

- `STAGING_DATABASE_URL` - PostgreSQL URL for staging
- `PRODUCTION_DATABASE_URL` - PostgreSQL URL for production

**API Endpoints:**

- `STAGING_API_URL` - Staging API base URL
- `STAGING_API_ENDPOINT` - Health check endpoint
- `PRODUCTION_API_URL` - Production API base URL
- `PRODUCTION_API_ENDPOINT` - Production health check

**Frontend URLs:**

- `STAGING_WEB_URL` - Staging web application URL
- `PRODUCTION_WEB_URL` - Production web application URL

**Vercel:**

- `VERCEL_TOKEN` - Vercel authentication token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Production project ID
- `VERCEL_PROJECT_ID_STAGING` - Staging project ID

**Test Credentials:**

- `STAGING_TEST_USER_EMAIL` - Test user email
- `STAGING_TEST_USER_PASSWORD` - Test user password
- `TEST_USER_EMAIL` - Test user email for CI
- `TEST_USER_PASSWORD` - Test user password for CI
- `TEST_CALL_ID` - Sample call ID for testing
- `TEST_REP_EMAIL` - Sample representative email

**Deployment:**

- `STAGING_DEPLOYMENT_TOKEN` - Token for staging deployments
- `PRODUCTION_DEPLOYMENT_TOKEN` - Token for production deployments

### Local Development

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your local configuration
```

## Running Tests Locally

### Python Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run unit tests only
pytest tests/ -m "not integration and not slow"

# Run with coverage
pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api --cov-report=html

# Run specific test file
pytest tests/test_analysis.py -v

# Run with markers
pytest tests/ -m integration  # Integration tests only
pytest tests/ -m slow        # Slow tests
pytest tests/ -m "not slow"  # Exclude slow tests
```

### Linting and Format Checking

```bash
# Lint with ruff
ruff check .

# Format check with black
black --check .

# Auto-format with black
black .

# Type checking
mypy analysis coaching_mcp api --ignore-missing-imports
```

### Frontend Tests

```bash
cd frontend
npm ci
npm test
npm run lint
```

### Security Scanning Locally

```bash
# Python security (bandit)
pip install bandit
bandit -r analysis coaching_mcp api

# Dependency audit
pip-audit
npm audit --production
```

## Branch Protection Rules

### Main Branch

The `main` branch has the following protection rules:

- ✅ Require pull request reviews before merging (1+ approval)
- ✅ Require status checks to pass:
  - `lint` - Ruff and Black formatting
  - `type-check` - MyPy type checking
  - `python-tests` - Unit and integration tests with coverage
  - `build` - Docker image builds
  - `security` - All security scans
- ✅ Require branches to be up to date before merging
- ✅ Require code owner reviews
- ✅ Dismiss stale PR approvals when new commits are pushed

### Develop Branch

The `develop` branch has similar protections:

- ✅ Require pull request reviews (1+ approval)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Auto-delete head branches after PR merge

## GitHub Actions Configuration

### Concurrency

Build and deployment workflows use concurrency to prevent duplicate runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This ensures only one workflow runs per branch at a time.

### Caching

Workflows use GitHub's built-in caching:

- **pip** - Python package cache (auto)
- **npm** - Node package cache (auto)
- **Docker buildx** - Layer caching between builds

Cache hit rate significantly speeds up CI times.

## Troubleshooting

### Coverage Threshold Failures

If tests fail due to coverage < 70%:

```bash
# Check local coverage
pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api --cov-report=term-missing

# Identify uncovered lines
# Add tests for those lines

# Re-run coverage check
pytest tests/ --cov-fail-under=70
```

### Docker Build Failures

If Docker builds fail:

```bash
# Build locally to debug
docker build -f Dockerfile.mcp -t test:mcp .
docker build -f Dockerfile.webhook -t test:webhook .

# Check for build issues
docker build -f Dockerfile.mcp -t test:mcp . --progress=plain
```

### Deployment Failures

1. Check the workflow run details in GitHub Actions
2. Review the deployment logs
3. Verify environment variables/secrets are set
4. Check database connectivity
5. Review application logs on the deployment target

### Security Scan False Positives

For CodeQL/Semgrep false positives:

1. Review the finding in GitHub Security tab
2. Add suppression if it's a false positive
3. Update SARIF metadata

## Setting Up Status Checks

### Enable Branch Protection

1. Go to Settings → Branches
2. Click "Add rule"
3. Pattern: `main`
4. Enable "Require pull request reviews"
5. Enable "Require status checks to pass before merging"
6. Select required checks:
   - lint
   - type-check
   - python-tests
   - build
   - security

### Required Status Checks

The following workflows must pass before merging to main:

1. **Test Suite** (`tests.yml`)

   - All matrix configurations must pass
   - Coverage must be >= 70%

2. **Build** (`build.yml`)

   - Docker images must build successfully

3. **Security** (`security.yml`)
   - No critical vulnerabilities
   - No secrets detected

## Monitoring and Alerts

### GitHub Notifications

Watch for:

- Red X on PRs = check failed
- Yellow indicator = check running
- Green check = all passed

### Action Item Notifications

Failures automatically post PR comments highlighting issues.

### GitHub Security Advisories

Monitor the Security tab for:

- Secret scanning alerts
- Dependabot alerts
- Code scanning alerts

## CI/CD Best Practices

1. **Keep CI Fast** - Run expensive tests only when needed
2. **Fail Fast** - Run quick checks (lint, type) before slow tests
3. **Use Caching** - Docker layer cache, pip/npm cache
4. **Clear Logs** - Keep logs readable with good formatting
5. **Secure Secrets** - Use GitHub Secrets, never commit credentials
6. **Test in Containers** - Tests run in containers similar to production
7. **Monitor Trends** - Track build times, failure rates, security issues

## Support

For questions or issues:

1. Check GitHub Actions logs for detailed error messages
2. Review workflow file comments for configuration options
3. Consult GitHub Actions documentation
4. Check project-specific documentation

---

**Last Updated:** 2026-02-05
