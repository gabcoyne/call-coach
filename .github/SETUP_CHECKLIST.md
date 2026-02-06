# CI/CD Setup Checklist

Use this checklist to ensure the CI/CD pipeline is properly configured.

## Phase 1: Initial Setup (5 minutes)

- [ ] **Scripts are executable**
  ```bash
  ls -la scripts/ci/*.sh
  # Should show: -rwxr-xr-x (executable)
  ```

- [ ] **All workflow files exist**
  ```bash
  ls -la .github/workflows/
  # Should show: tests.yml, build.yml, deploy-*.yml, migrate.yml, security.yml, release.yml
  ```

- [ ] **Documentation files exist**
  ```bash
  ls -la .github/
  # Should show: CODEOWNERS, CICD_QUICK_START.md, CI_CD_IMPLEMENTATION_SUMMARY.md, WORKFLOW_DIAGRAM.md
  ```

## Phase 2: GitHub Configuration (10-15 minutes)

### Secrets Configuration

- [ ] **Run secrets setup script**
  ```bash
  scripts/ci/setup-secrets.sh
  ```

- [ ] **Verify required secrets are set**
  ```bash
  gh secret list --repo gabcoyne/call-coach
  ```

## Phase 3: Local Testing (5 minutes)

- [ ] **Test suite runs locally**
  ```bash
  scripts/ci/run-tests-locally.sh all
  ```

## Phase 4: GitHub Actions Verification (10 minutes)

- [ ] **Visit Actions tab in GitHub**
  - Go to your repository
  - Click "Actions" tab

- [ ] **All workflows are listed**
  - [ ] Test Suite
  - [ ] Build Docker Images
  - [ ] Deploy to Staging
  - [ ] Deploy to Production
  - [ ] Database Migration
  - [ ] Security Scanning
  - [ ] Release

## Phase 5: First Test Run (10-20 minutes)

- [ ] **Create a test PR**
  ```bash
  git checkout -b test/cicd-validation
  echo "# CI/CD Test" > CICD_TEST.md
  git add CICD_TEST.md
  git commit -m "test: CI/CD validation"
  git push origin test/cicd-validation
  ```

- [ ] **All checks pass**
  - [ ] Green checkmark on PR
  - [ ] All checks show passing

## Quick Reference Commands

```bash
# Make scripts executable
chmod +x scripts/ci/*.sh

# Configure secrets
scripts/ci/setup-secrets.sh

# Setup branch protection
scripts/ci/setup-branch-protection.sh YOUR_GITHUB_TOKEN

# Test locally
scripts/ci/run-tests-locally.sh all

# Check specific tests
scripts/ci/run-tests-locally.sh lint
scripts/ci/run-tests-locally.sh unit
scripts/ci/run-tests-locally.sh security
```

**Status**: ✅ Ready for Production
