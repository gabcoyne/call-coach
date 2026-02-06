# Database Performance Optimization

This directory contains tools and scripts for database performance analysis and optimization.

## Files

### slow_queries.sql

Comprehensive SQL script for analyzing database performance:

1. **Slow Query Identification**
   - Queries by average execution time
   - Long-running query detection
   - Query statistics from pg_stat_statements

2. **Index Analysis**
   - EXPLAIN ANALYZE for common query patterns
   - Index usage statistics
   - Unused index detection
   - Index size analysis

3. **Index Recommendations**
   - Composite indexes for call filtering
   - Indexes for coaching session lookups
   - Full-text search optimization
   - Opportunity timeline query optimization

4. **Table Statistics**
   - Table sizes and row counts
   - Dead tuple analysis (VACUUM recommendations)
   - Last VACUUM/ANALYZE timestamps

5. **Connection Pooling**
   - Current connection counts
   - Connection state breakdown (active/idle/idle in transaction)
   - Long-running transaction detection

## Usage

### Initial Setup

Run the index creation queries to optimize database performance:

```bash
# Connect to database
psql $DATABASE_URL

# Enable query statistics (if not already enabled)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

# Run index creation queries (CONCURRENTLY to avoid locks)
\i db/performance/slow_queries.sql
```

### Regular Monitoring

Run the analysis queries periodically to identify performance issues:

```bash
# Analyze slow queries
psql $DATABASE_URL -c "
SELECT calls, mean_exec_time, query
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Check for unused indexes
psql $DATABASE_URL -c "
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;
"

# Check table bloat (VACUUM needed)
psql $DATABASE_URL -c "
SELECT schemaname, tablename,
       n_dead_tup,
       ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
"
```

### Performance Testing

Before and after adding indexes, run EXPLAIN ANALYZE on common queries:

```bash
# Test call filtering query
psql $DATABASE_URL -c "
EXPLAIN ANALYZE
SELECT * FROM calls
WHERE product = 'Prefect Cloud'
AND scheduled_at > '2024-01-01'
ORDER BY scheduled_at DESC
LIMIT 50;
"

# Test rep performance query
psql $DATABASE_URL -c "
EXPLAIN ANALYZE
SELECT cs.*
FROM coaching_sessions cs
JOIN speakers s ON cs.rep_id = s.id
WHERE s.email = 'test@example.com'
AND cs.created_at >= NOW() - INTERVAL '30 days'
ORDER BY cs.created_at DESC;
"
```

## Index Recommendations

### Critical Indexes (High Impact)

1. **idx_calls_product_scheduled**
   - Speeds up call filtering by product and date
   - Used by dashboard and analytics queries
   - Expected improvement: 5-10x

2. **idx_coaching_rep_created**
   - Optimizes rep performance queries
   - Used by insights and coaching endpoints
   - Expected improvement: 3-8x

3. **idx_transcripts_fts**
   - Full-text search optimization
   - Used by search and topic queries
   - Expected improvement: 10-50x

### Secondary Indexes (Medium Impact)

1. **idx_speakers_email_company**
   - Rep email lookups
   - Expected improvement: 2-5x

2. **idx_emails_opportunity_sent**
   - Opportunity timeline queries
   - Expected improvement: 2-4x

## Maintenance

### VACUUM and ANALYZE

Run VACUUM and ANALYZE regularly to maintain query planner statistics:

```bash
# Manual VACUUM (for urgent bloat issues)
psql $DATABASE_URL -c "VACUUM VERBOSE ANALYZE calls;"

# Check autovacuum settings
psql $DATABASE_URL -c "
SHOW autovacuum_vacuum_scale_factor;
SHOW autovacuum_analyze_scale_factor;
"
```

### Index Maintenance

Monitor index health and rebuild if needed:

```bash
# Check index bloat
psql $DATABASE_URL -c "
SELECT
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
"

# Rebuild bloated index (CONCURRENTLY to avoid locks)
psql $DATABASE_URL -c "
REINDEX INDEX CONCURRENTLY idx_name;
"
```

## Troubleshooting

### High CPU Usage

1. Check for missing indexes on frequently queried columns
2. Look for sequential scans in EXPLAIN output
3. Verify autovacuum is running

### High Memory Usage

1. Check connection pool size
2. Look for idle transactions holding locks
3. Monitor work_mem settings

### Slow Queries

1. Run EXPLAIN ANALYZE to see query plan
2. Check if indexes are being used
3. Look for type casts preventing index usage
4. Consider query rewriting for better performance

## Resources

- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Understanding EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [Index Maintenance](https://www.postgresql.org/docs/current/routine-reindex.html)
