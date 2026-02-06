# Branch Protection Configuration

This document provides step-by-step instructions for configuring GitHub branch protection rules to enforce test quality standards.

## Overview

Branch protection rules ensure that:

1. All tests pass before code can be merged
2. Code coverage meets minimum thresholds (70%)
3. Code reviews are completed
4. Branches are up-to-date with the base branch

## Configuration Steps

### 1. Navigate to Branch Protection Settings

1. Go to your repository: `https://github.com/gabcoyne/call-coach`
2. Click **Settings** > **Branches**
3. Under "Branch protection rules", click **Add rule**

### 2. Configure Protection for `main` Branch

**Branch name pattern**: `main`

**Required Settings**:

#### Require a pull request before merging

- ✅ Enable
- Require approvals: `1`
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (if CODEOWNERS file exists)

#### Require status checks to pass before merging

- ✅ Enable
- ✅ Require branches to be up to date before merging

**Required status checks** (add these):

```
Backend Tests Summary
Frontend Tests Summary
Enforce Test Quality / Block Merge on Test Failures
codecov/project
codecov/patch
```

#### Additional Settings

- ✅ Require conversation resolution before merging
- ✅ Require signed commits (optional but recommended)
- ✅ Require linear history (optional)
- ✅ Include administrators (enforce rules for admins too)
- ✅ Allow force pushes: **Disable**
- ✅ Allow deletions: **Disable**

### 3. Configure Protection for `develop` Branch

Repeat the same configuration as `main` with these differences:

**Branch name pattern**: `develop`

**Required Settings**: Same as `main` but optionally:

- Reduce required approvals to `0` or `1` for faster iteration
- Keep status checks the same

### 4. Verify Configuration

After saving, test the configuration:

1. Create a new branch from `develop`
2. Make a change that would fail tests
3. Create a pull request
4. Verify that:
   - Status checks run automatically
   - Merge button is disabled until checks pass
   - Coverage badge shows on PR

## Required Status Checks Explained

### Backend Tests Summary

- Runs: Python linting, type checking, unit tests, integration tests
- Coverage: Must maintain 70% minimum coverage
- Blocks merge if: Any backend test fails or coverage drops below threshold

### Frontend Tests Summary

- Runs: TypeScript linting, unit tests, build check, accessibility tests
- Coverage: Must maintain 70% minimum coverage
- Blocks merge if: Any frontend test fails, build fails, or coverage drops below threshold

### Enforce Test Quality

- Runs: Validates that all test workflows completed successfully
- Blocks merge if: Backend or frontend test suites failed

### codecov/project

- Runs: Validates overall project coverage meets target (70%)
- Blocks merge if: Total project coverage drops below threshold

### codecov/patch

- Runs: Validates that new code (patch) has adequate coverage
- Blocks merge if: New code has less than 70% coverage

## Exemptions and Overrides

### Emergency Hotfixes

For critical production issues that need immediate deployment:

1. Create a branch with prefix `hotfix/`
2. Admins can override branch protection with "Administrator override"
3. **Must** file a follow-up issue to add missing tests
4. Review changes in next team sync

### Skipping CI Checks

To skip CI checks for documentation-only changes:

```bash
git commit -m "docs: Update README [skip ci]"
```

**Warning**: This bypasses all checks. Use sparingly.

## Monitoring and Maintenance

### Weekly Review

- Check branch protection rules are still enabled
- Review any bypassed checks in the past week
- Update required status checks if workflow names change

### Quarterly Review

- Evaluate if coverage thresholds should be increased
- Review bypass requests and patterns
- Update this documentation if process changes

## Troubleshooting

### "Required status check is not present"

**Cause**: Status check hasn't run yet or workflow name changed

**Solution**:

1. Trigger workflows manually via "Actions" tab
2. Wait for all checks to register
3. Refresh branch protection settings

### "Merge button enabled despite failing tests"

**Cause**: Status check not marked as required or wrong name

**Solution**:

1. Verify exact status check name in Actions > Recent runs
2. Update branch protection to use exact name
3. May need to re-create PR to trigger checks

### "Cannot add status check as required"

**Cause**: Status check must run at least once to be selectable

**Solution**:

1. Create a test PR on the protected branch
2. Wait for all workflows to complete
3. Status checks will appear in branch protection settings

## Related Documentation

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Test Backend Workflow](../.github/workflows/test-backend.yml)
- [Test Frontend Workflow](../.github/workflows/test-frontend.yml)
- [Codecov Configuration](../.codecov.yml)
- [Pre-commit Hooks](../.pre-commit-config.yaml)
