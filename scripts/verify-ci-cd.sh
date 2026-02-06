#!/bin/bash
#
# Verify CI/CD Integration
# Quick check that all CI/CD files are in place and properly configured
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=================================="
echo "CI/CD Integration Verification"
echo -e "==================================${NC}"
echo ""

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_string_in_file() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $1 contains '$2'"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 missing '$2'"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# 1. Check workflow files
echo "Checking GitHub Actions workflows..."
check_file ".github/workflows/test-backend.yml"
check_file ".github/workflows/test-frontend.yml"
check_file ".github/workflows/enforce-tests.yml"
echo ""

# 2. Check codecov config
echo "Checking Codecov configuration..."
check_file ".codecov.yml"
if [ -f ".codecov.yml" ]; then
    check_string_in_file ".codecov.yml" "target: 70%"
    check_string_in_file ".codecov.yml" "backend:"
    check_string_in_file ".codecov.yml" "frontend:"
fi
echo ""

# 3. Check pre-commit config
echo "Checking pre-commit configuration..."
check_file ".pre-commit-config.yaml"
if [ -f ".pre-commit-config.yaml" ]; then
    check_string_in_file ".pre-commit-config.yaml" "pytest-quick"
    check_string_in_file ".pre-commit-config.yaml" "jest-quick"
fi
echo ""

# 4. Check documentation
echo "Checking documentation..."
check_file "docs/BRANCH_PROTECTION.md"
check_file "docs/CI_CD_INTEGRATION.md"
check_file "docs/CI_CD_IMPLEMENTATION_SUMMARY.md"
echo ""

# 5. Check scripts
echo "Checking setup scripts..."
check_file "scripts/setup-ci-cd.sh"
if [ -f "scripts/setup-ci-cd.sh" ]; then
    if [ -x "scripts/setup-ci-cd.sh" ]; then
        echo -e "${GREEN}✓${NC} scripts/setup-ci-cd.sh is executable"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} scripts/setup-ci-cd.sh not executable"
        ((CHECKS_FAILED++))
    fi
fi
echo ""

# 6. Check README updates
echo "Checking README.md updates..."
check_file "README.md"
if [ -f "README.md" ]; then
    check_string_in_file "README.md" "codecov"
    check_string_in_file "README.md" "Backend Tests"
    check_string_in_file "README.md" "Frontend Tests"
    check_string_in_file "README.md" "## Testing"
fi
echo ""

# 7. Check workflow syntax (basic)
echo "Checking workflow YAML syntax..."
for workflow in .github/workflows/test-backend.yml .github/workflows/test-frontend.yml .github/workflows/enforce-tests.yml; do
    if [ -f "$workflow" ]; then
        if grep -q "jobs:" "$workflow" && grep -q "runs-on:" "$workflow"; then
            echo -e "${GREEN}✓${NC} $workflow has required structure"
            ((CHECKS_PASSED++))
        else
            echo -e "${RED}✗${NC} $workflow missing required structure"
            ((CHECKS_FAILED++))
        fi
    fi
done
echo ""

# 8. Summary
echo -e "${BLUE}=================================="
echo "Verification Summary"
echo -e "==================================${NC}"
echo ""
echo -e "Checks passed: ${GREEN}${CHECKS_PASSED}${NC}"
echo -e "Checks failed: ${RED}${CHECKS_FAILED}${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Commit and push changes to GitHub"
    echo "2. Add CODECOV_TOKEN to GitHub secrets"
    echo "3. Configure branch protection rules (see docs/BRANCH_PROTECTION.md)"
    echo "4. Create a test PR to verify workflows"
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Please review the failures above and fix any issues."
    exit 1
fi
