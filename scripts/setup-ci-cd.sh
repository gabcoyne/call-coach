#!/bin/bash
#
# Setup CI/CD Integration
# This script helps configure the testing infrastructure for the call-coach project
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "Call Coach CI/CD Setup"
echo "=================================="
echo ""

# 1. Check if required tools are installed
echo "Checking required tools..."

if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ git is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ git${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ python3${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ node is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ node${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm${NC}"

echo ""

# 2. Install pre-commit hooks
echo "Installing pre-commit hooks..."

if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

pre-commit install
echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
echo ""

# 3. Check GitHub repository configuration
echo "Checking GitHub repository configuration..."

if git remote -v | grep -q "github.com"; then
    REPO_URL=$(git remote get-url origin | sed 's/git@github.com://' | sed 's/.git$//')
    echo -e "${GREEN}✓ GitHub remote configured: ${REPO_URL}${NC}"

    echo ""
    echo -e "${YELLOW}Next steps for GitHub configuration:${NC}"
    echo ""
    echo "1. Configure Codecov:"
    echo "   - Visit: https://codecov.io/gh/${REPO_URL}"
    echo "   - Add CODECOV_TOKEN secret to GitHub repository"
    echo "   - Go to: https://github.com/${REPO_URL}/settings/secrets/actions"
    echo ""
    echo "2. Configure Branch Protection (main branch):"
    echo "   - Visit: https://github.com/${REPO_URL}/settings/branches"
    echo "   - Add rule for 'main' branch"
    echo "   - Enable: 'Require status checks to pass before merging'"
    echo "   - Required checks: Backend Tests Summary, Frontend Tests Summary, codecov/project"
    echo "   - See docs/BRANCH_PROTECTION.md for full instructions"
    echo ""
    echo "3. Configure Branch Protection (develop branch):"
    echo "   - Same as main branch"
    echo "   - See docs/BRANCH_PROTECTION.md for full instructions"
    echo ""
else
    echo -e "${RED}✗ No GitHub remote found${NC}"
    echo "Run: git remote add origin git@github.com:username/call-coach.git"
fi

# 4. Verify workflow files
echo "Verifying GitHub Actions workflows..."

WORKFLOW_DIR=".github/workflows"
REQUIRED_WORKFLOWS=(
    "test-backend.yml"
    "test-frontend.yml"
    "enforce-tests.yml"
)

for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "${WORKFLOW_DIR}/${workflow}" ]; then
        echo -e "${GREEN}✓ ${workflow}${NC}"
    else
        echo -e "${RED}✗ ${workflow} not found${NC}"
    fi
done
echo ""

# 5. Verify codecov configuration
if [ -f ".codecov.yml" ]; then
    echo -e "${GREEN}✓ .codecov.yml configured${NC}"
else
    echo -e "${RED}✗ .codecov.yml not found${NC}"
fi
echo ""

# 6. Test backend setup
echo "Testing backend test setup..."

if [ -f "pyproject.toml" ]; then
    echo -e "${GREEN}✓ pyproject.toml exists${NC}"

    if grep -q "pytest" pyproject.toml; then
        echo -e "${GREEN}✓ pytest configured${NC}"
    else
        echo -e "${YELLOW}⚠ pytest not found in pyproject.toml${NC}"
    fi

    if grep -q "pytest-cov" pyproject.toml; then
        echo -e "${GREEN}✓ pytest-cov configured${NC}"
    else
        echo -e "${YELLOW}⚠ pytest-cov not found in pyproject.toml${NC}"
    fi
else
    echo -e "${RED}✗ pyproject.toml not found${NC}"
fi
echo ""

# 7. Test frontend setup
echo "Testing frontend test setup..."

if [ -f "frontend/package.json" ]; then
    echo -e "${GREEN}✓ frontend/package.json exists${NC}"

    if grep -q "\"test\":" frontend/package.json; then
        echo -e "${GREEN}✓ test script configured${NC}"
    else
        echo -e "${YELLOW}⚠ test script not found in package.json${NC}"
    fi

    if grep -q "jest" frontend/package.json; then
        echo -e "${GREEN}✓ jest configured${NC}"
    else
        echo -e "${YELLOW}⚠ jest not found in package.json${NC}"
    fi
else
    echo -e "${RED}✗ frontend/package.json not found${NC}"
fi
echo ""

# 8. Run test validation
echo "Running quick test validation..."

echo "Backend tests (quick check)..."
if pytest tests/ -m "not slow and not integration and not e2e" --collect-only &> /dev/null; then
    TEST_COUNT=$(pytest tests/ -m "not slow and not integration and not e2e" --collect-only -q | tail -1)
    echo -e "${GREEN}✓ Backend tests discovered: ${TEST_COUNT}${NC}"
else
    echo -e "${YELLOW}⚠ Could not discover backend tests (this is ok if venv not set up)${NC}"
fi

echo "Frontend tests (quick check)..."
if [ -d "frontend/node_modules" ]; then
    cd frontend
    if npm test -- --listTests &> /dev/null; then
        TEST_COUNT=$(npm test -- --listTests 2>/dev/null | wc -l)
        echo -e "${GREEN}✓ Frontend tests discovered: ${TEST_COUNT} test files${NC}"
    else
        echo -e "${YELLOW}⚠ Could not discover frontend tests${NC}"
    fi
    cd ..
else
    echo -e "${YELLOW}⚠ Frontend dependencies not installed (run: cd frontend && npm install)${NC}"
fi
echo ""

# 9. Summary
echo "=================================="
echo "Setup Summary"
echo "=================================="
echo ""
echo -e "${GREEN}✓ Local setup complete${NC}"
echo ""
echo "To complete CI/CD integration:"
echo "1. Push changes to GitHub"
echo "2. Configure Codecov token in GitHub secrets"
echo "3. Set up branch protection rules (see docs/BRANCH_PROTECTION.md)"
echo "4. Create a test PR to verify workflows run correctly"
echo ""
echo "To run tests locally:"
echo "  Backend:  pytest tests/ --cov --cov-report=term-missing"
echo "  Frontend: cd frontend && npm run test:coverage"
echo ""
echo "To test pre-commit hooks:"
echo "  pre-commit run --all-files"
echo ""
