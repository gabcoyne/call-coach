# Call-Coach CI/CD Pipeline

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Date**: February 5, 2026

This directory contains the complete CI/CD pipeline for the call-coach project using GitHub Actions.

## Quick Links

### 📖 Documentation

1. **[CICD Quick Start](./CICD_QUICK_START.md)** ⭐ START HERE

   - 5-minute setup guide
   - Quick reference for common tasks
   - Basic troubleshooting

2. **[Setup Checklist](./SETUP_CHECKLIST.md)**

   - Step-by-step verification checklist
   - Ensures everything is configured correctly

3. **[CI/CD Implementation Summary](./CI_CD_IMPLEMENTATION_SUMMARY.md)**

   - Technical architecture details
   - Integration points and dependencies
   - Complete specification reference

4. **[Workflow Diagrams](./WORKFLOW_DIAGRAM.md)**
   - Visual workflow architecture
   - Data flow diagrams
   - Status check requirements

### 🔧 Helper Scripts

Located in `scripts/ci/`:

- **[run-tests-locally.sh](../scripts/ci/run-tests-locally.sh)**

  - Run tests like CI does locally
  - Usage: `./scripts/ci/run-tests-locally.sh all`

- **[setup-secrets.sh](../scripts/ci/setup-secrets.sh)**

  - Interactive GitHub secrets configuration
  - Usage: `./scripts/ci/setup-secrets.sh`

- **[setup-branch-protection.sh](../scripts/ci/setup-branch-protection.sh)**

  - Automated branch protection setup
  - Usage: `./scripts/ci/setup-branch-protection.sh TOKEN`

- **[README.md](../scripts/ci/README.md)**
  - Comprehensive 500+ line reference guide
  - All environment variables and secrets
  - Complete setup instructions

### 📋 Configuration Files

- **[CODEOWNERS](./CODEOWNERS)** - Code ownership and PR requirements
- **[workflows/](./workflows/)** - All workflow definitions (7 total)

## Workflows Overview

| Workflow                                                   | Trigger          | Purpose                          |
| ---------------------------------------------------------- | ---------------- | -------------------------------- |
| [tests.yml](./workflows/tests.yml)                         | Push/PR          | Lint, type-check, test, coverage |
| [build.yml](./workflows/build.yml)                         | Code changes     | Build Docker images              |
| [deploy-staging.yml](./workflows/deploy-staging.yml)       | develop push     | Deploy to staging                |
| [deploy-production.yml](./workflows/deploy-production.yml) | Version tags     | Deploy to production             |
| [migrate.yml](./workflows/migrate.yml)                     | Manual trigger   | Database migrations              |
| [security.yml](./workflows/security.yml)                   | Push/PR/Schedule | 9 security tools                 |
| [release.yml](./workflows/release.yml)                     | Manual trigger   | Automated releases               |

## Quick Start

### 1. Configure Secrets (5 minutes)

```bash
scripts/ci/setup-secrets.sh
```

Or manually via GitHub Settings → Secrets → New repository secret

### 2. Set Up Branch Protection

```bash
scripts/ci/setup-branch-protection.sh YOUR_GITHUB_TOKEN
```

Or manually via GitHub Settings → Branches

### 3. Test Locally

```bash
scripts/ci/run-tests-locally.sh all
```

### 4. Create a Test PR

Push a test branch and create a PR to verify workflows run.

## Common Operations

### Deploy to Staging

```bash
git push origin develop
# Automatically deploys to staging
```

### Deploy to Production

```bash
git tag v1.2.3
git push origin v1.2.3
# Automatically deploys to production
```

### Run Database Migrations

```bash
gh workflow run migrate.yml -f environment=staging
```

### Create a Release

```bash
gh workflow run release.yml -f version_type=minor
```

### Run Tests Locally

```bash
scripts/ci/run-tests-locally.sh [lint|type-check|unit|integration|security|all]
```

## Required Secrets

23 secrets must be configured in GitHub Settings → Secrets:

**Database**: STAGING/PRODUCTION_DATABASE_URL
**API**: STAGING/PRODUCTION_API_URL, STAGING/PRODUCTION_API_ENDPOINT
**Frontend**: STAGING/PRODUCTION_WEB_URL
**Vercel**: VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID, VERCEL_PROJECT_ID_STAGING
**Testing**: TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_CALL_ID, TEST_REP_EMAIL, etc.
**Deployment**: STAGING/PRODUCTION_DEPLOYMENT_TOKEN

See [scripts/ci/README.md](../scripts/ci/README.md) for complete list.

## Coverage Requirements

- **Unit Tests**: 70% minimum (enforced)
- **Production Deployments**: 80% minimum (enforced)

Verified with coverage reports uploaded to Codecov.

## Security

9 security scanning tools:

- pip-audit (Python dependencies)
- npm audit (Node.js dependencies)
- Bandit (Python code)
- Semgrep (Code patterns)
- CodeQL (Advanced analysis)
- Trivy (Container images)
- License compliance checking
- TruffleHog (Secret detection)
- SBOM generation

Results integrated into GitHub Security tab.

## Status Checks (Branch Protection)

**Required to pass before merge**:

- lint
- type-check
- python-tests
- build-mcp
- build-webhook
- security

## Monitoring

- **Coverage**: Codecov integration
- **Builds**: GitHub Actions logs (90-day retention)
- **Security**: GitHub Security tab
- **Deployments**: GitHub Actions logs + monitoring

## Support

1. **Quick questions**: See [CICD_QUICK_START.md](./CICD_QUICK_START.md)
2. **Setup help**: See [scripts/ci/README.md](../scripts/ci/README.md)
3. **Technical details**: See [CI_CD_IMPLEMENTATION_SUMMARY.md](./CI_CD_IMPLEMENTATION_SUMMARY.md)
4. **Visual guides**: See [WORKFLOW_DIAGRAM.md](./WORKFLOW_DIAGRAM.md)
5. **Troubleshooting**: See [scripts/ci/README.md](../scripts/ci/README.md#troubleshooting)

## Files & Documentation

```
.github/
├── README.md                              (this file)
├── SETUP_CHECKLIST.md                    (verification checklist)
├── CICD_QUICK_START.md                   (5-min setup guide)
├── CI_CD_IMPLEMENTATION_SUMMARY.md       (technical details)
├── WORKFLOW_DIAGRAM.md                   (architecture diagrams)
├── CODEOWNERS                            (code ownership)
└── workflows/
    ├── tests.yml                         (test pipeline)
    ├── build.yml                         (docker build)
    ├── deploy-staging.yml                (staging deployment)
    ├── deploy-production.yml             (production deployment)
    ├── migrate.yml                       (database migrations)
    ├── security.yml                      (security scanning)
    ├── release.yml                       (automated releases)
    ├── vercel-preview.yml                (vercel preview)
    └── performance.yml                   (performance tests)

scripts/ci/
├── README.md                             (comprehensive guide)
├── run-tests-locally.sh                  (local test execution)
├── setup-secrets.sh                      (secrets configuration)
└── setup-branch-protection.sh            (branch protection setup)
```

## Next Steps

1. ✅ Read [CICD_QUICK_START.md](./CICD_QUICK_START.md)
2. ✅ Run setup scripts
3. ✅ Test locally with `scripts/ci/run-tests-locally.sh all`
4. ✅ Create a test PR to verify workflows
5. ✅ Review [CI_CD_IMPLEMENTATION_SUMMARY.md](./CI_CD_IMPLEMENTATION_SUMMARY.md) for details

## Key Features

✅ **7 GitHub Actions Workflows**
✅ **9 Security Scanning Tools**
✅ **Multi-Environment Deployment** (staging → production)
✅ **Database Migration Safety** (backup + rollback)
✅ **Automated Release Process** (versioning + publishing)
✅ **Coverage Enforcement** (70% minimum)
✅ **Branch Protection Rules**
✅ **Comprehensive Documentation**
✅ **Helper Scripts** (setup + testing)
✅ **Production Ready**

## Statistics

- **Total Workflows**: 7
- **Total Jobs**: 32
- **Security Tools**: 9
- **Required Secrets**: 23
- **Documentation**: ~65 KB
- **Code**: ~3,000+ lines
- **Setup Time**: ~5 minutes
- **Coverage Requirement**: 70% (unit), 80% (production)

---

**Status**: ✅ READY FOR PRODUCTION

For detailed information, see the individual documentation files listed above.
