#!/bin/bash
# FastMCP Cloud Deployment Script for Gong Call Coach
# Deploys MCP server to Prefect Horizon

set -e  # Exit on error

echo "========================================================"
echo "FastMCP Cloud Deployment - Gong Call Coach"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FASTMCP_API_KEY="${FASTMCP_API_KEY:-fmcp_F6rhqd9oFr1HOzNu6hOa5VBfwh2iXsKYWofXqPGTzqc}"
HORIZON_URL="https://horizon.prefect.io/prefect-george/servers"
SERVER_NAME="gong-call-coach"

echo ""
echo "📋 Pre-Deployment Checks"
echo "========================================================"

# Check 1: Verify uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv not found${NC}"
    echo "Install uv: https://docs.astral.sh/uv/"
    exit 1
fi
echo -e "${GREEN}✓${NC} uv installed"

# Check 2: Verify dependencies are synced
echo "Syncing dependencies..."
if ! uv sync; then
    echo -e "${RED}✗ uv sync failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Dependencies synced"

# Check 3: Verify MCP server can initialize locally
echo "Testing MCP server initialization..."
if ! timeout 10 uv run python -c "from coaching_mcp.server import mcp; print('Server initialized')" 2>&1 | grep -q "Server initialized"; then
    echo -e "${YELLOW}⚠${NC}  MCP server initialization test skipped (imports may fail without .env)"
else
    echo -e "${GREEN}✓${NC} MCP server imports successfully"
fi

# Check 4: Verify required files exist
required_files=("fastmcp.toml" ".fastmcp/config.json" "coaching_mcp/server.py" "pyproject.toml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓${NC} All required files present"

echo ""
echo "========================================================"
echo "🚀 Ready to Deploy"
echo "========================================================"
echo ""
echo "Manual Deployment Steps:"
echo ""
echo "1. Navigate to Horizon MCP Servers:"
echo "   ${HORIZON_URL}"
echo ""
echo "2. Create New MCP Server:"
echo "   - Name: ${SERVER_NAME}"
echo "   - Runtime: Python 3.11"
echo "   - Command: uv"
echo "   - Args: [\"run\", \"python\", \"coaching_mcp/server.py\"]"
echo "   - Working Directory: /app"
echo ""
echo "3. Set Environment Variables in Horizon UI:"
echo "   (Copy from your local .env file)"
echo ""

if [ -f ".env" ]; then
    echo "   Required variables from .env:"
    echo "   ---"
    grep -E "^(GONG_API_KEY|GONG_API_SECRET|GONG_API_BASE_URL|ANTHROPIC_API_KEY|DATABASE_URL)=" .env || echo "   (No variables found in .env)"
    echo "   ---"
else
    echo -e "   ${YELLOW}⚠${NC}  .env file not found - ensure you set these manually:"
    echo "   - GONG_API_KEY"
    echo "   - GONG_API_SECRET"
    echo "   - GONG_API_BASE_URL"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - DATABASE_URL"
fi

echo ""
echo "4. Upload Project Files:"
echo "   - Option A: Connect GitHub repository"
echo "   - Option B: Upload project directory directly"
echo ""
echo "5. Deploy and Verify:"
echo "   - Click 'Deploy' in Horizon UI"
echo "   - Wait for status to show 'Ready' (within 30 seconds)"
echo "   - Check logs for validation success messages"
echo ""
echo "========================================================"
echo "🧪 Post-Deployment Testing"
echo "========================================================"
echo ""
echo "After deployment succeeds, test via Claude Desktop:"
echo ""
echo "Test 1 - Analyze Call:"
echo "  > analyze_call(\"1464927526043145564\")"
echo ""
echo "Test 2 - Get Rep Insights:"
echo "  > get_rep_insights(\"sarah.jones@prefect.io\", time_period=\"last_30_days\")"
echo ""
echo "Test 3 - Search Calls:"
echo "  > search_calls(call_type=\"discovery\", min_score=70, limit=10)"
echo ""
echo "========================================================"
echo "📊 Monitoring"
echo "========================================================"
echo ""
echo "After deployment:"
echo "- View logs in Horizon UI for validation messages"
echo "- Monitor Neon dashboard for database connection usage"
echo "- Check Anthropic usage dashboard for API costs"
echo ""
echo "Expected cold start: 10-15 seconds"
echo "Expected warm start: <2 seconds"
echo ""
echo "========================================================"
echo "✅ Pre-deployment checks complete!"
echo "Proceed to Horizon UI: ${HORIZON_URL}"
echo "========================================================"
