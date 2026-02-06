#!/bin/bash
#
# Apply Performance Optimizations
#
# Applies database indexes, query optimizations, and verifies setup.
# Safe to run multiple times (uses IF NOT EXISTS).
#
# Usage:
#   ./scripts/apply_performance_optimizations.sh
#   ./scripts/apply_performance_optimizations.sh --verify-only
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}Loading .env file...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL not set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}=== Call Coach Performance Optimization ===${NC}\n"

# Parse arguments
VERIFY_ONLY=false
if [ "$1" = "--verify-only" ]; then
    VERIFY_ONLY=true
fi

# Function to run SQL and check for errors
run_sql() {
    local sql_file=$1
    local description=$2

    echo -e "${YELLOW}$description...${NC}"

    if psql "$DATABASE_URL" -f "$sql_file" > /tmp/sql_output.log 2>&1; then
        echo -e "${GREEN}✓ Success${NC}"
        # Show key output
        tail -n 5 /tmp/sql_output.log
        echo ""
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "Error output:"
        cat /tmp/sql_output.log
        return 1
    fi
}

# Function to run SQL command
run_sql_command() {
    local command=$1
    local description=$2

    echo -e "${YELLOW}$description...${NC}"

    if psql "$DATABASE_URL" -c "$command" > /tmp/sql_output.log 2>&1; then
        echo -e "${GREEN}✓ Success${NC}"
        cat /tmp/sql_output.log
        echo ""
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        cat /tmp/sql_output.log
        return 1
    fi
}

# Verify database connection
echo -e "${YELLOW}Verifying database connection...${NC}"
if psql "$DATABASE_URL" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connected to database${NC}\n"
else
    echo -e "${RED}✗ Failed to connect to database${NC}"
    exit 1
fi

if [ "$VERIFY_ONLY" = true ]; then
    echo -e "${YELLOW}=== Verification Mode ===${NC}\n"

    # Check if indexes exist
    echo -e "${YELLOW}Checking indexes...${NC}"
    run_sql_command "
        SELECT
            schemaname,
            tablename,
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) as size
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        AND indexname LIKE 'idx_%'
        ORDER BY pg_relation_size(indexrelid) DESC
        LIMIT 20;
    " "Top 20 indexes by size"

    # Check index usage
    echo -e "${YELLOW}Checking index usage...${NC}"
    run_sql_command "SELECT * FROM get_index_usage_stats() LIMIT 10;" "Index usage statistics"

    # Check cache statistics
    echo -e "${YELLOW}Checking cache statistics...${NC}"
    run_sql_command "SELECT * FROM get_cache_statistics(7);" "Cache stats (last 7 days)"

    # Check materialized view
    echo -e "${YELLOW}Checking materialized view...${NC}"
    run_sql_command "
        SELECT COUNT(*) as rep_count, MAX(last_refreshed) as last_refresh
        FROM mv_rep_performance;
    " "Rep performance view status"

    echo -e "${GREEN}=== Verification Complete ===${NC}"
    exit 0
fi

# Apply optimizations
echo -e "${YELLOW}=== Applying Performance Optimizations ===${NC}\n"

# Step 1: Apply indexes
if [ -f "db/performance/indexes.sql" ]; then
    run_sql "db/performance/indexes.sql" "Step 1: Creating performance indexes"
else
    echo -e "${RED}✗ indexes.sql not found${NC}"
    exit 1
fi

# Step 2: Apply query optimizations
if [ -f "db/performance/query_optimization.sql" ]; then
    run_sql "db/performance/query_optimization.sql" "Step 2: Creating optimized query functions"
else
    echo -e "${RED}✗ query_optimization.sql not found${NC}"
    exit 1
fi

# Step 3: Analyze tables
echo -e "${YELLOW}Step 3: Updating table statistics...${NC}"
run_sql_command "SELECT analyze_coaching_tables();" "Analyzing tables"

# Step 4: Refresh materialized views
echo -e "${YELLOW}Step 4: Refreshing materialized views...${NC}"
run_sql_command "SELECT refresh_rep_performance_view();" "Refreshing rep performance view"

# Step 5: Verify optimizations
echo -e "${YELLOW}=== Verification ===${NC}\n"

# Check index count
run_sql_command "
    SELECT COUNT(*) as index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%';
" "Total performance indexes"

# Check function creation
run_sql_command "
    SELECT COUNT(*) as function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN (
        'get_cached_coaching_session',
        'get_rep_performance_summary',
        'search_calls_optimized',
        'get_call_with_details',
        'get_cache_statistics'
    );
" "Optimized functions created"

# Performance summary
echo -e "\n${GREEN}=== Performance Optimization Complete ===${NC}\n"
echo -e "Summary:"
echo -e "  ✓ Performance indexes applied"
echo -e "  ✓ Optimized query functions created"
echo -e "  ✓ Table statistics updated"
echo -e "  ✓ Materialized views refreshed"
echo -e ""
echo -e "Next steps:"
echo -e "  1. Run cache warming: ${YELLOW}python -m cache.warming --days 30${NC}"
echo -e "  2. Verify Redis: ${YELLOW}redis-cli ping${NC}"
echo -e "  3. Monitor performance: ${YELLOW}python -m monitoring.cache_stats${NC}"
echo -e ""
echo -e "For verification, run: ${YELLOW}./scripts/apply_performance_optimizations.sh --verify-only${NC}"
