# CI/CD Workflow Architecture Diagram

## High-Level Pipeline Flow

```
                          CODE PUSH/PR
                              |
                ______________|______________
               |                             |
          PULL REQUEST                    PUSH TO BRANCH
               |                             |
               |                    (main or develop)
               |                             |
               v                             v
          TEST SUITE                    TEST SUITE
          (All Checks)                  (All Checks)
               |                             |
               |                    _________|_________
               |                   |                   |
               v                   v                   v
          (Success)           BUILD                 DEPLOY
                            (Docker)               (Staging)
                              (Push)


                          PRODUCTION RELEASE
                              (Tag: v1.0.0)
                                  |
                                  v
                             TEST SUITE
                           (80% Coverage)
                                  |
                                  v
                              BUILD & PUSH
                            (Docker Images)
                                  |
                                  v
                             DATABASE
                            MIGRATIONS
                                  |
                                  v
                            DEPLOY PROD
                           (Frontend+Backend)
                                  |
                                  v
                          CREATE RELEASE
                         (GitHub + PyPI)
```

## Detailed Workflow Breakdown

### 1. Test Suite Workflow (Always Runs)

```
┌─────────────────────────────────────────────────────┐
│  TEST SUITE WORKFLOW (tests.yml)                     │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │ LINT & FORMAT    │  │  TYPE CHECK      │         │
│  │  (Ruff, Black)   │  │  (MyPy)          │         │
│  └──────────────────┘  └──────────────────┘         │
│          ↓                      ↓                    │
│          └──────────┬───────────┘                    │
│                     ↓                                │
│  ┌─────────────────────────────────────┐            │
│  │ PYTHON TESTS (Matrix: 3.11, 3.12)   │            │
│  ├─────────────────────────────────────┤            │
│  │ • Unit Tests                        │            │
│  │ • Integration Tests                 │            │
│  │ • Coverage: 70% minimum (enforced)  │            │
│  │ • Codecov upload                    │            │
│  └─────────────────────────────────────┘            │
│                     ↓                                │
│  ┌──────────────────────────────────────┐           │
│  │ PASS ✓ or FAIL ✗                     │           │
│  │ (Blocks merge if fails)              │           │
│  └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘

Triggers: Every push, every PR
Time: ~15 minutes
Required: All checks must pass
```

### 2. Build Workflow (Main/Develop Branch)

```
┌─────────────────────────────────────────────────────┐
│  BUILD WORKFLOW (build.yml)                          │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐ │
│  │ BUILD MCP IMAGE      │  │ BUILD WEBHOOK IMAGE  │ │
│  │ (Dockerfile.mcp)     │  │ (Dockerfile.webhook) │ │
│  └──────────────────────┘  └──────────────────────┘ │
│           ↓                          ↓              │
│  ┌──────────────────────────────────────────────┐  │
│  │ PUSH TO GITHUB CONTAINER REGISTRY (ghcr.io)  │  │
│  ├──────────────────────────────────────────────┤  │
│  │ Tags:                                        │  │
│  │  • branch name: develop, main                │  │
│  │  • commit SHA: develop-abc123def             │  │
│  │  • semantic version: v1.0.0                  │  │
│  └──────────────────────────────────────────────┘  │
│                      ↓                              │
│  ┌──────────────────────────────────────────────┐  │
│  │ VERIFY IMAGES                                │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

Triggers: Push to main/develop (code changes)
Time: ~10-15 minutes
Produces: Docker images in GHCR
```

### 3. Staging Deployment (Develop Branch)

```
┌─────────────────────────────────────────────────────┐
│  STAGING DEPLOYMENT (deploy-staging.yml)             │
├─────────────────────────────────────────────────────┤
│                                                       │
│  1. DATABASE MIGRATION                              │
│     ├─ Validate migrations                         │
│     ├─ Create backup                               │
│     ├─ Run migrations                              │
│     └─ Verify success                              │
│           ↓                                         │
│  2. BUILD & PUSH DOCKER IMAGES                      │
│     └─ Tag: staging-latest                         │
│           ↓                                         │
│  3. DEPLOY FRONTEND                                 │
│     └─ Vercel (staging project)                    │
│           ↓                                         │
│  4. DEPLOY BACKEND                                  │
│     └─ Staging infrastructure                      │
│           ↓                                         │
│  5. SMOKE TESTS                                     │
│     ├─ Health checks                               │
│     ├─ Critical path tests                         │
│     └─ Verify deployment                           │
│                                                       │
└─────────────────────────────────────────────────────┘

Triggers: Push to develop branch
Time: ~20-30 minutes
Requires: Test suite passes
Database: Staging PostgreSQL
Frontend: Vercel staging
Backend: Staging infrastructure
```

### 4. Production Deployment (Version Tags)

```
┌──────────────────────────────────────────────────────────┐
│  PRODUCTION DEPLOYMENT (deploy-production.yml)            │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. PREPARE RELEASE                                      │
│     ├─ Extract version from tag                         │
│     ├─ Generate changelog from commits                  │
│     └─ Prepare release artifacts                        │
│           ↓                                              │
│  2. RUN FULL TEST SUITE                                  │
│     ├─ All tests must pass                              │
│     ├─ Coverage: 80% minimum (enforced)                │
│     └─ Security scans complete                          │
│           ↓                                              │
│  3. BUILD PRODUCTION IMAGES                              │
│     ├─ Docker MCP image (prod tag)                      │
│     ├─ Docker webhook image (prod tag)                  │
│     └─ Push to GHCR                                     │
│           ↓                                              │
│  4. DATABASE MIGRATION                                   │
│     ├─ Create backup                                    │
│     ├─ Validate migrations                              │
│     ├─ Run migrations                                   │
│     ├─ Verify success                                   │
│     └─ Rollback on failure                              │
│           ↓                                              │
│  5. DEPLOY FRONTEND                                      │
│     └─ Vercel (production project)                      │
│           ↓                                              │
│  6. DEPLOY BACKEND                                       │
│     └─ Production infrastructure                        │
│           ↓                                              │
│  7. CREATE RELEASE                                       │
│     ├─ GitHub release with changelog                    │
│     └─ Publish to PyPI                                  │
│                                                            │
└──────────────────────────────────────────────────────────┘

Triggers: Git tag (v1.0.0, v1.1.0, etc.)
Time: ~30-45 minutes
Requires: All checks + 80% coverage
Database: Production PostgreSQL
Frontend: Vercel production
Backend: Production infrastructure
Produces: GitHub release + PyPI package
```

### 5. Database Migration Workflow

```
┌─────────────────────────────────────────────────────┐
│  DATABASE MIGRATION (migrate.yml)                    │
├─────────────────────────────────────────────────────┤
│                                                       │
│  START                                              │
│    ↓                                                │
│  VALIDATE MIGRATIONS                                │
│    ├─ Check syntax                                 │
│    ├─ List pending migrations                      │
│    └─ Verify dependencies                          │
│    ↓                                                │
│  SELECT TARGET                                      │
│    ├─ Environment: staging or production           │
│    ├─ Target version: (optional, default: latest)  │
│    └─ Get connection string from secrets           │
│    ↓                                                │
│  BACKUP DATABASE                                    │
│    └─ pg_dump or equivalent                        │
│    ↓                                                │
│  RUN MIGRATIONS                                     │
│    ├─ Execute migration SQL/scripts                │
│    └─ Log execution details                        │
│    ↓                                                │
│  SUCCESS?                                           │
│    ├─ YES → VERIFY & DONE ✓                        │
│    └─ NO  → ROLLBACK & NOTIFY ✗                    │
│                                                       │
└─────────────────────────────────────────────────────┘

Triggers: Manual workflow_dispatch or migration file changes
Time: ~10-20 minutes
Requires: Environment-specific secrets
Produces: Migration audit log
Safety: Automatic backup + rollback
```

### 6. Security Scanning Workflow

```
┌──────────────────────────────────────────────────────────┐
│  SECURITY SCANNING (security.yml)                         │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────┐  ┌─────────────────────┐        │
│  │ DEPENDENCY SCAN     │  │ CODE SECURITY       │        │
│  ├─────────────────────┤  ├─────────────────────┤        │
│  │ • pip-audit (Python)│  │ • Bandit (Python)   │        │
│  │ • npm audit (Node)  │  │ • Semgrep (Patterns)│        │
│  │ • SBOM generation   │  │ • CodeQL (Advanced) │        │
│  └─────────────────────┘  └─────────────────────┘        │
│           ↓                        ↓                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │ CONTAINER SECURITY                              │   │
│  ├──────────────────────────────────────────────────┤   │
│  │ • Trivy: MCP image scan                         │   │
│  │ • Trivy: Webhook image scan                     │   │
│  │ • Severity reporting                            │   │
│  └──────────────────────────────────────────────────┘   │
│           ↓                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ COMPLIANCE CHECKS                                │   │
│  ├──────────────────────────────────────────────────┤   │
│  │ • pip-licenses: License compliance              │   │
│  │ • TruffleHog: Secret detection                  │   │
│  └──────────────────────────────────────────────────┘   │
│           ↓                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ GENERATE REPORTS                                │   │
│  ├──────────────────────────────────────────────────┤   │
│  │ • SARIF → GitHub Security tab                  │   │
│  │ • Artifacts → Manual review                    │   │
│  │ • Summary → PR comments                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                            │
└──────────────────────────────────────────────────────────┘

Triggers: Every push, every PR, weekly schedule
Time: ~15-20 minutes
Produces: SARIF reports + artifacts
Integration: GitHub Security tab + PR comments
Tools: 9 security scanners
```

### 7. Release Workflow

```
┌──────────────────────────────────────────────────────────┐
│  RELEASE WORKFLOW (release.yml)                           │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  START (Manual Trigger)                                  │
│    ├─ Version Type: major/minor/patch/prerelease        │
│    └─ Prerelease Suffix: alpha/beta/rc (optional)       │
│    ↓                                                     │
│  CALCULATE VERSION                                       │
│    ├─ Get previous version from tags                    │
│    ├─ Apply version bump                                │
│    └─ Output: v1.2.3                                    │
│    ↓                                                     │
│  GENERATE CHANGELOG                                      │
│    ├─ Commits since last tag                            │
│    ├─ Categorize: feat, fix, docs, etc.                │
│    └─ Output: CHANGELOG.md                              │
│    ↓                                                     │
│  UPDATE VERSION                                          │
│    ├─ Modify pyproject.toml                            │
│    ├─ Create release branch                             │
│    └─ Commit version update                             │
│    ↓                                                     │
│  TEST                                                    │
│    ├─ Full test suite (80% coverage)                   │
│    ├─ Build verification                                │
│    └─ All checks pass?                                  │
│    ↓                                                     │
│  CREATE TAG & MERGE                                      │
│    ├─ Create annotated git tag                          │
│    ├─ Merge to main                                     │
│    ├─ Merge to develop                                  │
│    └─ Push all changes                                  │
│    ↓                                                     │
│  CREATE GITHUB RELEASE                                   │
│    ├─ Tag: v1.2.3                                       │
│    ├─ Title: "Release v1.2.3"                           │
│    ├─ Body: Full changelog + details                    │
│    └─ Publish release                                   │
│    ↓                                                     │
│  PUBLISH TO PyPI                                         │
│    ├─ Build wheel distribution                          │
│    ├─ Upload to PyPI                                    │
│    └─ Make available via pip                            │
│    ↓                                                     │
│  CLEANUP                                                 │
│    └─ Delete release branch                             │
│                                                            │
└──────────────────────────────────────────────────────────┘

Triggers: Manual workflow_dispatch
Time: ~15-20 minutes
Produces: Version tag + GitHub release + PyPI package
Automation: Handles all release coordination
```

## Environment Matrix

```
┌─────────────────┬──────────┬────────────┬─────────────────┐
│ Environment     │ Trigger  │ Database   │ Frontend        │
├─────────────────┼──────────┼────────────┼─────────────────┤
│ Testing         │ PR/Push  │ Test DB    │ Unit/E2E tests  │
│ Staging         │ develop  │ Staging    │ Vercel staging  │
│ Production      │ v*.*.* tag│ Production│ Vercel prod     │
│ PyPI            │ Release  │ N/A        │ N/A             │
└─────────────────┴──────────┴────────────┴─────────────────┘
```

## Status Check Requirements

```
┌─────────────────────────────────────────┐
│ REQUIRED STATUS CHECKS (Main/Develop)   │
├─────────────────────────────────────────┤
│ ✓ lint                                  │
│ ✓ type-check                            │
│ ✓ python-tests (3.11, 3.12)             │
│ ✓ build-mcp                             │
│ ✓ build-webhook                         │
│ ✓ security (all checks pass)            │
├─────────────────────────────────────────┤
│ Requirement: All must pass before merge │
│ Auto-dismiss: Stale PR reviews          │
│ Enforce: Admins & code owners           │
└─────────────────────────────────────────┘
```

## Data Flow Diagram

```
Source Code
    ↓
GitHub Repository
    ├─→ Test Suite ────→ Pass/Fail
    ├─→ Build ─────────→ Docker Images (GHCR)
    ├─→ Security ──────→ Vulnerability Reports
    ├─→ Deploy Staging→ Staging Environment
    └─→ Deploy Prod ──→ Production + Release
         + Migration ──→ Database
         + Release ────→ GitHub + PyPI
```

---

**Last Updated**: February 5, 2026
**Pipeline Status**: Production Ready
