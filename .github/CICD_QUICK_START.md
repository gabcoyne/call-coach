# CI/CD Quick Start Guide

This guide helps you get the call-coach CI/CD pipeline up and running in minutes.

## Overview

The call-coach project now has a comprehensive CI/CD pipeline with:

- **7 GitHub Actions workflows** for testing, building, deploying, and releasing
- **Automated security scanning** for dependencies and code
- **Database migration management** with rollback support
- **Multi-environment deployment** (staging → production)
- **Automated release process** with version bumping

## Quick Setup (5 minutes)

### Step 1: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click "Enable GitHub Actions"

### Step 2: Configure Secrets

GitHub Actions workflows need environment secrets. Use the helper script:

```bash
# Make the script executable
chmod +x scripts/ci/setup-secrets.sh

# Run interactive setup
scripts/ci/setup-secrets.sh

# Or with GitHub CLI if you have it installed
gh secret list --repo gabcoyne/call-coach
```

**Minimum required secrets:**

```
# Staging
STAGING_DATABASE_URL
STAGING_API_URL
STAGING_WEB_URL

# Vercel (for frontend)
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
VERCEL_PROJECT_ID_STAGING

# Production
PRODUCTION_DATABASE_URL
PRODUCTION_API_URL
PRODUCTION_DEPLOYMENT_TOKEN
```

See `scripts/ci/README.md` for the complete list.

### Step 3: Set Up Branch Protection

```bash
# Make the script executable
chmod +x scripts/ci/setup-branch-protection.sh

# Run setup
scripts/ci/setup-branch-protection.sh YOUR_GITHUB_TOKEN
```

This configures:
- Required status checks before merging
- PR review requirements
- Automatic enforcement of CI/CD rules

### Step 4: Test Locally

```bash
# Run all tests like CI does
scripts/ci/run-tests-locally.sh all

# Or run specific checks
scripts/ci/run-tests-locally.sh lint        # Formatting
scripts/ci/run-tests-locally.sh type-check  # Type checking
scripts/ci/run-tests-locally.sh unit        # Unit tests
scripts/ci/run-tests-locally.sh security    # Security scans
```

## Workflow Reference

### Test Suite (`.github/workflows/tests.yml`)

Runs on: Every push to main/develop and PRs
- Lint & format checking
- Type checking
- Unit and integration tests
- Coverage reporting (70% minimum)

### Build (`.github/workflows/build.yml`)

Runs on: Code changes on main/develop
- Builds Docker images for MCP and webhook servers
- Pushes to GitHub Container Registry

### Deploy Staging (`.github/workflows/deploy-staging.yml`)

Runs on: Push to develop branch
- Runs database migrations
- Deploys backend to staging
- Deploys frontend to Vercel staging
- Runs smoke tests

### Deploy Production (`.github/workflows/deploy-production.yml`)

Runs on: Version tags (v1.0.0, v1.1.0, etc.)
- Full test suite (80% coverage enforced)
- Builds production Docker images
- Runs migrations with backup
- Deploys to production
- Creates GitHub release

### Database Migration (`.github/workflows/migrate.yml`)

Trigger manually: `gh workflow run migrate.yml -f environment=staging`
- Validates migrations
- Creates database backup
- Runs migrations with verification
- Automatic rollback on failure

### Security (`.github/workflows/security.yml`)

Runs on: Every push, PRs, and weekly schedule
- Dependency vulnerability scanning
- Python/JavaScript security analysis
- Container image scanning
- License compliance checking
- Secret detection

### Release (`.github/workflows/release.yml`)

Trigger manually via GitHub Actions UI:
1. Go to "Actions" tab
2. Select "Release" workflow
3. Click "Run workflow"
4. Choose version bump type: major/minor/patch

This will:
- Calculate next version
- Generate changelog
- Run full test suite
- Create git tag and GitHub release
- Publish to PyPI
- Merge to main and develop

## Common Tasks

### Deploy to Staging

1. Make changes on `develop` branch
2. Create a PR with `main`
3. Get approved and merge
4. Changes automatically deploy to staging

### Deploy to Production

```bash
# On your local machine
git checkout main
git pull origin main

# Tag a new release
git tag v1.2.3
git push origin v1.2.3

# Or via GitHub UI:
# - Go to Actions → Release workflow
# - Click "Run workflow"
# - Select version type (patch/minor/major)
```

### Run Database Migrations

```bash
# Via GitHub CLI
gh workflow run migrate.yml -f environment=staging

# Or via GitHub UI:
# - Actions → Database Migration
# - Run workflow
# - Select environment and (optional) target version
```

### Check Test Results

1. Go to "Actions" tab in GitHub
2. Click on the workflow run
3. Expand job details for specific failures
4. View logs or artifacts

### View Security Findings

1. Go to "Security" tab
2. Click "Code scanning alerts"
3. Review findings by severity
4. Dismiss false positives or create issues

## Troubleshooting

### Tests fail with "coverage below 70%"

```bash
# Check coverage locally
pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api --cov-report=term-missing

# Write tests for uncovered lines
# Re-run to verify

# Coverage must be >= 70% (80% for production)
```

### Docker build fails

```bash
# Debug locally
docker build -f Dockerfile.mcp -t test:mcp .
docker build -f Dockerfile.webhook -t test:webhook .

# Check for syntax errors or missing files
```

### Deployment fails

1. Check the workflow log in GitHub Actions
2. Verify all secrets are set correctly
3. Ensure deployment target is accessible
4. Review application logs on the target

### Secret or environment variable not found

```bash
# Verify secrets are set
gh secret list --repo gabcoyne/call-coach

# Add missing secret
gh secret set SECRET_NAME --repo gabcoyne/call-coach

# Or via GitHub UI: Settings → Secrets → New repository secret
```

## Best Practices

1. **Always test locally first**
   ```bash
   scripts/ci/run-tests-locally.sh all
   ```

2. **Keep commits clean**
   - One feature per PR
   - Clear commit messages
   - Run linter before committing

3. **Use semantic versioning**
   ```
   v1.2.3 = v[major].[minor].[patch]
   ```

4. **Review before merging**
   - Check CI status (green ✅)
   - Get at least 1 approval
   - Resolve conflicts

5. **Monitor deployments**
   - Check GitHub Actions logs
   - Monitor production errors
   - Set up alerts if available

## Files Created

```
.github/
├── workflows/
│   ├── tests.yml                 # Lint, type-check, test, coverage
│   ├── build.yml                 # Build Docker images
│   ├── deploy-staging.yml        # Deploy to staging
│   ├── deploy-production.yml     # Deploy to production
│   ├── migrate.yml               # Database migrations
│   ├── security.yml              # Security scanning
│   └── release.yml               # Automated release process
├── CODEOWNERS                    # Code review requirements
└── CICD_QUICK_START.md          # This file

scripts/ci/
├── README.md                     # Comprehensive documentation
├── setup-secrets.sh              # Configure GitHub secrets
├── setup-branch-protection.sh    # Configure branch rules
└── run-tests-locally.sh          # Run tests locally
```

## Next Steps

1. ✅ Configure secrets (see Step 2 above)
2. ✅ Set up branch protection (see Step 3 above)
3. ✅ Test locally (see Step 4 above)
4. Create a PR to verify CI runs
5. Monitor deployments as you release

## Documentation

- **Full documentation**: See `scripts/ci/README.md`
- **Workflow definitions**: See `.github/workflows/`
- **Local testing**: Run `scripts/ci/run-tests-locally.sh help`

## Support

For issues or questions:

1. Check workflow logs in GitHub Actions
2. Review `scripts/ci/README.md` for detailed info
3. Check the workflow YAML files for configuration options
4. Review GitHub Actions documentation at https://docs.github.com/actions

---

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Status**: Ready for Production
