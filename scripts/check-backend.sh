#!/bin/bash
#
# Check MCP Backend Server Health
#
# Usage: ./scripts/check-backend.sh [URL]
#
# Default URL: http://localhost:8000
# Custom URL: ./scripts/check-backend.sh https://mcp.prefect.io
#
# Exit codes:
#   0 - Server is healthy (status: ok)
#   1 - Server is starting (status: starting)
#   2 - Server is unreachable or error
#

set -e

# Configuration
BACKEND_URL="${1:-http://localhost:8000}"
HEALTH_ENDPOINT="${BACKEND_URL}/health"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Checking MCP backend health..."
echo "URL: ${HEALTH_ENDPOINT}"
echo ""

# Make request with timeout
if ! response=$(curl -s -w "\n%{http_code}" --connect-timeout 5 --max-time 10 "${HEALTH_ENDPOINT}" 2>&1); then
    echo -e "${RED}✗ Failed to connect to backend${NC}"
    echo "Error: ${response}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify backend is running: ps aux | grep mcp-server"
    echo "  2. Check if port 8000 is in use: lsof -ti:8000"
    echo "  3. Try starting backend: uv run mcp-server-dev"
    exit 2
fi

# Parse response (last line is status code)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

# Check HTTP status code
if [ "$http_code" -eq 200 ]; then
    # Parse JSON response
    status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    tools=$(echo "$body" | grep -o '"tools":[0-9]*' | cut -d':' -f2)

    if [ "$status" = "ok" ]; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        echo "  Status: ${status}"
        echo "  Tools: ${tools}"
        echo ""
        echo -e "${GREEN}MCP server is ready to accept requests${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ Backend returned unexpected status${NC}"
        echo "  Status: ${status}"
        echo "  Expected: ok"
        echo ""
        echo "Response: ${body}"
        exit 2
    fi
elif [ "$http_code" -eq 503 ]; then
    echo -e "${YELLOW}⚠ Backend is starting${NC}"
    echo "  HTTP Status: 503 Service Unavailable"
    echo ""
    echo "The server is initializing. This usually takes 2-10 seconds."
    echo "Wait a moment and try again."
    exit 1
else
    echo -e "${RED}✗ Backend returned error${NC}"
    echo "  HTTP Status: ${http_code}"
    echo "  Response: ${body}"
    exit 2
fi
