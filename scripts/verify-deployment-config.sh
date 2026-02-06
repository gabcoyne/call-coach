#!/bin/bash

# Verify Vercel Deployment Configuration
# This script checks that all required environment variables and configurations
# are in place before deploying to Vercel.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Vercel Deployment Configuration Verification${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check for required files
echo -e "${YELLOW}Checking required configuration files...${NC}"
errors=0
warnings=0

check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
    else
        echo -e "${RED}✗${NC} $description: $file ${RED}(MISSING)${NC}"
        ((errors++))
    fi
}

check_file "vercel.json" "Vercel configuration"
check_file "frontend/package.json" "Frontend package.json"
check_file ".env.production.example" "Production env example"
check_file "DEPLOYMENT.md" "Deployment documentation"
check_file "frontend/app/api/cron/daily-sync/route.ts" "Cron job endpoint"

echo ""

# Check vercel.json structure
echo -e "${YELLOW}Validating vercel.json structure...${NC}"

if [ -f "vercel.json" ]; then
    # Check for required keys
    if grep -q '"buildCommand"' vercel.json; then
        echo -e "${GREEN}✓${NC} buildCommand configured"
    else
        echo -e "${RED}✗${NC} buildCommand missing"
        ((errors++))
    fi

    if grep -q '"crons"' vercel.json; then
        echo -e "${GREEN}✓${NC} Cron jobs configured"
    else
        echo -e "${YELLOW}⚠${NC} No cron jobs configured"
        ((warnings++))
    fi

    if grep -q '"functions"' vercel.json; then
        echo -e "${GREEN}✓${NC} Function settings configured"
    else
        echo -e "${YELLOW}⚠${NC} No function settings"
        ((warnings++))
    fi
fi

echo ""

# Check environment variable documentation
echo -e "${YELLOW}Checking environment variable documentation...${NC}"

required_vars=(
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"
    "CLERK_SECRET_KEY"
    "DATABASE_URL"
    "GONG_API_KEY"
    "GONG_API_SECRET"
    "ANTHROPIC_API_KEY"
    "CRON_SECRET"
    "NEXT_PUBLIC_APP_URL"
)

if [ -f ".env.production.example" ]; then
    for var in "${required_vars[@]}"; do
        if grep -q "$var" .env.production.example; then
            echo -e "${GREEN}✓${NC} $var documented"
        else
            echo -e "${RED}✗${NC} $var not documented"
            ((errors++))
        fi
    done
else
    echo -e "${RED}✗${NC} .env.production.example not found"
    ((errors++))
fi

echo ""

# Check frontend build
echo -e "${YELLOW}Verifying frontend can build...${NC}"

if [ -d "frontend" ]; then
    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠${NC} node_modules not found, run 'npm install'"
        ((warnings++))
    else
        echo -e "${GREEN}✓${NC} node_modules present"
    fi

    # Check if TypeScript compiles
    if command -v npm &> /dev/null; then
        echo -e "${BLUE}Running type check...${NC}"
        if npm run lint &> /dev/null; then
            echo -e "${GREEN}✓${NC} TypeScript types valid"
        else
            echo -e "${RED}✗${NC} TypeScript errors found (run 'npm run lint')"
            ((errors++))
        fi
    fi

    cd ..
fi

echo ""

# Check database connection configuration
echo -e "${YELLOW}Checking database configuration...${NC}"

if [ -f "db/connection.py" ]; then
    echo -e "${GREEN}✓${NC} Database connection module exists"

    # Check for connection pooling
    if grep -q "ThreadedConnectionPool" db/connection.py; then
        echo -e "${GREEN}✓${NC} Connection pooling configured"
    else
        echo -e "${YELLOW}⚠${NC} Connection pooling may not be configured"
        ((warnings++))
    fi

    # Check for statement timeout
    if grep -q "statement_timeout" db/connection.py; then
        echo -e "${GREEN}✓${NC} Statement timeout configured"
    else
        echo -e "${YELLOW}⚠${NC} Statement timeout not found"
        ((warnings++))
    fi
fi

echo ""

# Check Python dependencies
echo -e "${YELLOW}Checking Python configuration...${NC}"

if [ -f "pyproject.toml" ]; then
    echo -e "${GREEN}✓${NC} pyproject.toml exists"

    # Check for FastMCP
    if grep -q "fastmcp" pyproject.toml; then
        echo -e "${GREEN}✓${NC} FastMCP dependency present"
    else
        echo -e "${RED}✗${NC} FastMCP dependency missing"
        ((errors++))
    fi

    # Check for required packages
    required_packages=("anthropic" "psycopg2-binary" "pydantic" "fastapi")
    for pkg in "${required_packages[@]}"; do
        if grep -q "$pkg" pyproject.toml; then
            echo -e "${GREEN}✓${NC} $pkg dependency present"
        else
            echo -e "${RED}✗${NC} $pkg dependency missing"
            ((errors++))
        fi
    done
fi

echo ""

# Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo -e "${GREEN}Configuration is ready for Vercel deployment.${NC}"
    exit 0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠ Configuration is mostly ready with $warnings warning(s).${NC}"
    echo -e "${YELLOW}Review warnings above before deploying.${NC}"
    exit 0
else
    echo -e "${RED}✗ Configuration has $errors error(s) and $warnings warning(s).${NC}"
    echo -e "${RED}Fix errors before deploying to Vercel.${NC}"
    exit 1
fi
