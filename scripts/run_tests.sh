#!/bin/bash
# Test runner script for Call Coaching application

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE=${1:-"unit"}
COVERAGE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: ./scripts/run_tests.sh [TEST_TYPE] [OPTIONS]"
            echo ""
            echo "TEST_TYPE:"
            echo "  unit       - Run unit tests (default)"
            echo "  analysis   - Run analysis module tests"
            echo "  mcp        - Run MCP tool tests"
            echo "  api        - Run API endpoint tests"
            echo "  e2e        - Run end-to-end tests"
            echo "  load       - Run load tests"
            echo "  all        - Run all tests (except load)"
            echo "  quick      - Run fast unit tests only"
            echo ""
            echo "OPTIONS:"
            echo "  --coverage - Generate coverage report"
            echo "  --verbose  - Verbose output"
            echo "  --help     - Show this help"
            exit 0
            ;;
        *)
            TEST_TYPE=$1
            shift
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"
PYTEST_ARGS="-v"

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -vv -s"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=analysis --cov=coaching_mcp --cov=api --cov-report=html --cov-report=term-missing"
fi

# Run tests based on type
case $TEST_TYPE in
    unit)
        echo -e "${BLUE}Running unit tests...${NC}"
        $PYTEST_CMD tests/ $PYTEST_ARGS -m "not integration and not e2e"
        ;;
    analysis)
        echo -e "${BLUE}Running analysis module tests...${NC}"
        $PYTEST_CMD tests/analysis/ $PYTEST_ARGS
        ;;
    mcp)
        echo -e "${BLUE}Running MCP tool tests...${NC}"
        $PYTEST_CMD tests/mcp/ $PYTEST_ARGS
        ;;
    api)
        echo -e "${BLUE}Running API endpoint tests...${NC}"
        $PYTEST_CMD tests/api/ $PYTEST_ARGS
        ;;
    e2e)
        echo -e "${BLUE}Running end-to-end tests...${NC}"
        if [ -z "$BASE_URL" ]; then
            BASE_URL="http://localhost:3000"
        fi
        echo -e "${YELLOW}Using BASE_URL: $BASE_URL${NC}"
        $PYTEST_CMD e2e/ $PYTEST_ARGS -m e2e
        ;;
    load)
        echo -e "${BLUE}Running load tests...${NC}"
        echo -e "${YELLOW}Make sure API is running on http://localhost:8000${NC}"
        python scripts/load_test.py
        ;;
    quick)
        echo -e "${BLUE}Running quick unit tests (no slow, no integration)...${NC}"
        $PYTEST_CMD tests/ $PYTEST_ARGS -m "not slow and not integration and not e2e"
        ;;
    all)
        echo -e "${BLUE}Running all tests...${NC}"
        $PYTEST_CMD tests/ e2e/ $PYTEST_ARGS -m "not e2e"
        ;;
    *)
        echo -e "${YELLOW}Unknown test type: $TEST_TYPE${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

# Show results
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Tests passed!${NC}"
    if [ "$COVERAGE" = true ]; then
        echo -e "${GREEN}✓ Coverage report generated: htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Tests failed!${NC}"
    exit 1
fi
