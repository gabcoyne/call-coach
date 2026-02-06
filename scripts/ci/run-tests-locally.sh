#!/bin/bash

# Local Testing Script
# This script runs the same tests that GitHub Actions runs locally
# Usage: ./run-tests-locally.sh [test-type]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test types
LINT="lint"
TYPE_CHECK="type-check"
UNIT_TESTS="unit"
INTEGRATION_TESTS="integration"
ALL_TESTS="all"
SECURITY="security"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

run_lint() {
    print_header "Running Lint Checks (Ruff & Black)"

    # Check if dependencies are installed
    if ! command -v ruff &> /dev/null || ! command -v black &> /dev/null; then
        print_warning "Installing linting tools..."
        pip install ruff black
    fi

    echo "Running Ruff..."
    if ruff check . --format=github; then
        print_success "Ruff check passed"
    else
        print_error "Ruff check failed"
        return 1
    fi

    echo ""
    echo "Running Black..."
    if black --check .; then
        print_success "Black format check passed"
    else
        print_warning "Files need formatting. Run: black ."
        return 1
    fi
}

run_type_check() {
    print_header "Running Type Checks (MyPy)"

    # Check if mypy is installed
    if ! command -v mypy &> /dev/null; then
        print_warning "Installing mypy..."
        pip install -e ".[dev]" mypy
    fi

    if mypy analysis coaching_mcp api --ignore-missing-imports --show-error-codes; then
        print_success "Type check passed"
    else
        print_error "Type check failed"
        return 1
    fi
}

run_unit_tests() {
    print_header "Running Unit Tests"

    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        print_warning "Installing test dependencies..."
        pip install -e ".[dev]"
    fi

    if pytest tests/ -v --cov=analysis --cov=coaching_mcp --cov=api \
        --cov-report=term-missing -m "not integration and not slow"; then
        print_success "Unit tests passed"
    else
        print_error "Unit tests failed"
        return 1
    fi

    # Check coverage threshold
    echo ""
    echo "Checking coverage threshold (70%)..."
    if pytest tests/ --cov=analysis --cov=coaching_mcp --cov=api \
        --cov-report=term --cov-fail-under=70 -m "not integration and not slow"; then
        print_success "Coverage threshold met (>=70%)"
    else
        print_error "Coverage below 70% threshold"
        return 1
    fi
}

run_integration_tests() {
    print_header "Running Integration Tests"

    if ! command -v pytest &> /dev/null; then
        print_warning "Installing test dependencies..."
        pip install -e ".[dev]"
    fi

    if pytest tests/ -v -m integration; then
        print_success "Integration tests passed"
    else
        print_warning "Integration tests failed (this may be expected if services aren't running)"
        return 1
    fi
}

run_all_tests() {
    print_header "Running All Tests"

    if ! command -v pytest &> /dev/null; then
        print_warning "Installing test dependencies..."
        pip install -e ".[dev]"
    fi

    if pytest tests/ -v --cov=analysis --cov=coaching_mcp --cov=api \
        --cov-report=html --cov-report=term-missing; then
        print_success "All tests passed"
        print_success "HTML coverage report generated in htmlcov/index.html"
    else
        print_error "Some tests failed"
        return 1
    fi
}

run_security_checks() {
    print_header "Running Security Checks"

    # Bandit
    echo "Running Bandit..."
    if command -v bandit &> /dev/null; then
        bandit -r analysis coaching_mcp api -ll || print_warning "Bandit found issues (may be false positives)"
    else
        print_warning "Bandit not installed. Install with: pip install bandit"
    fi

    echo ""

    # pip-audit
    echo "Running pip-audit..."
    if command -v pip-audit &> /dev/null; then
        pip-audit --desc || print_warning "pip-audit found vulnerabilities"
    else
        print_warning "pip-audit not installed. Install with: pip install pip-audit"
    fi

    print_success "Security checks completed"
}

run_docker_build() {
    print_header "Building Docker Images"

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi

    echo "Building MCP image..."
    if docker build -f Dockerfile.mcp -t call-coach-mcp:test .; then
        print_success "MCP image built successfully"
    else
        print_error "Failed to build MCP image"
        return 1
    fi

    echo ""
    echo "Building webhook image..."
    if docker build -f Dockerfile.webhook -t call-coach-webhook:test .; then
        print_success "Webhook image built successfully"
    else
        print_error "Failed to build webhook image"
        return 1
    fi
}

show_help() {
    cat <<EOF
Usage: ./run-tests-locally.sh [test-type]

Test Types:
  lint              Run Ruff and Black format checks
  type-check        Run MyPy type checking
  unit              Run unit tests with coverage
  integration       Run integration tests
  all               Run all tests
  security          Run security checks (Bandit, pip-audit)
  docker            Build Docker images
  help              Show this help message

Examples:
  # Run just linting
  ./run-tests-locally.sh lint

  # Run all tests
  ./run-tests-locally.sh all

  # Run with no arguments (runs all tests)
  ./run-tests-locally.sh

EOF
}

# Main execution
if [ -z "$1" ] || [ "$1" == "--help" ] || [ "$1" == "help" ]; then
    if [ -z "$1" ]; then
        print_header "Running All Tests Locally"
        TEST_TYPE=$ALL_TESTS
    else
        show_help
        exit 0
    fi
else
    TEST_TYPE="$1"
fi

case $TEST_TYPE in
    lint)
        run_lint
        ;;
    type-check)
        run_type_check
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    all)
        run_lint && \
        run_type_check && \
        run_unit_tests && \
        run_integration_tests && \
        run_docker_build
        ;;
    security)
        run_security_checks
        ;;
    docker)
        run_docker_build
        ;;
    help)
        show_help
        exit 0
        ;;
    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo ""
        show_help
        exit 1
        ;;
esac

# Check if the last command succeeded
if [ $? -eq 0 ]; then
    print_success "All selected tests passed!"
    exit 0
else
    print_error "Some tests failed"
    exit 1
fi
