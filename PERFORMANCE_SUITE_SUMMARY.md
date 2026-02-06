# Performance Testing Suite - Implementation Summary

## Overview

A comprehensive performance testing and benchmarking suite has been created for the Call Coaching API. This suite provides load testing, stress testing, detailed benchmarking, and real-world performance scenarios with automated CI/CD integration.

## Deliverables

### 1. Load Testing System

**File:** `/Users/gcoyne/src/prefect/call-coach/tests/performance/load_test.py`

A Locust-based load testing system that simulates realistic user load:

- **Concurrent Users:** 100 simultaneous users
- **Test Coverage:** 1000+ coaching analyses, multiple search patterns
- **Measured Endpoints:**

  - `/tools/analyze_call` - Call analysis with caching
  - `/tools/get_rep_insights` - Rep performance insights
  - `/tools/search_calls` - Complex search with filters
  - `/tools/analyze_opportunity` - Opportunity analysis
  - `/health` - API health check

- **Statistics Tracking:**
  - Response time percentiles (P50, P95, P99)
  - Throughput (requests/second)
  - Error rates and success counts
  - Per-endpoint metrics

**Usage:**

```bash
locust -f tests/performance/load_test.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=5 \
  --run-time=5m
```

### 2. Stress Testing System

**File:** `/Users/gcoyne/src/prefect/call-coach/tests/performance/stress_test.py`

An async-based stress testing framework that identifies system breaking points:

- **Ramp-up Strategy:** Gradual increase from 10 to 1000 concurrent users
- **Breaking Point Detection:** Automatic identification when error rate >10% or P99 >10s
- **Metrics Collection:**
  - Concurrent user levels
  - Success/failure counts
  - Response time percentiles
  - Throughput under stress
  - Recovery behavior

**Usage:**

```bash
python tests/performance/stress_test.py
```

### 3. Benchmarking Suite

#### 3.1 API Benchmarks

**File:** `/Users/gcoyne/src/prefect/call-coach/benchmarks/api_benchmarks.py`

Pytest-benchmark based endpoint performance measurement:

- **13 Benchmark Tests:**

  - Health check
  - Analyze call (cached, uncached, with transcript)
  - Rep insights (7/30/90 days, with product filters)
  - Search calls (simple, by product, date range, complex)
  - Opportunity analysis

- **Features:**
  - Automatic baseline comparison
  - Regression detection (>10% threshold)
  - JSON output for trending
  - Per-operation metrics

**Usage:**

```bash
pytest benchmarks/api_benchmarks.py -v
```

#### 3.2 Database Benchmarks

**File:** `/Users/gcoyne/src/prefect/call-coach/benchmarks/db_benchmarks.py`

Database query performance measurement:

- **14 Query Benchmarks:**

  - Call metadata and transcript retrieval
  - Rep-based and product-based searches
  - Date range searches with complex filters
  - Rep statistics calculation
  - Opportunity call retrieval
  - Dashboard statistics
  - Batch operations

- **Optimization Focus:**
  - Index usage verification
  - Connection pool performance
  - Query plan analysis

**Usage:**

```bash
pytest benchmarks/db_benchmarks.py -v
```

#### 3.3 Cache Benchmarks

**File:** `/Users/gcoyne/src/prefect/call-coach/benchmarks/cache_benchmarks.py`

Redis cache performance measurement:

- **18 Cache Benchmarks:**

  - GET/SET operations
  - Cache hit/miss scenarios
  - Batch operations
  - Pattern-based invalidation
  - Serialization/deserialization
  - Compression overhead
  - Memory management
  - Cache warming strategies

- **Features:**
  - Hit rate measurement
  - TTL verification
  - Memory usage tracking
  - Eviction performance

**Usage:**

```bash
pytest benchmarks/cache_benchmarks.py -v
```

### 4. Performance Scenarios

Real-world usage patterns combining multiple API calls:

#### 4.1 Coaching Analysis Scenario

**File:** `/Users/gcoyne/src/prefect/call-coach/tests/performance/scenarios/coaching_analysis.py`

Tests analyzing 100 coaching calls:

- **5 Scenario Tests:**

  - Sequential analysis of 100 calls
  - Different dimension configurations
  - Cache effectiveness measurement
  - Large transcript analysis
  - Rapid sequential analysis patterns

- **Metrics:**
  - Time per call
  - Dimension impact on performance
  - Cache speedup (typical: 10-50x)
  - Throughput under various conditions

**Usage:**

```bash
pytest tests/performance/scenarios/coaching_analysis.py -v -m performance
```

#### 4.2 Dashboard Load Scenario

**File:** `/Users/gcoyne/src/prefect/call-coach/tests/performance/scenarios/dashboard_load.py`

Tests rep dashboard loading performance:

- **7 Scenario Tests:**

  - Single rep dashboard load
  - All 50 reps dashboard load
  - Time period variations (7/30/90 days)
  - Concurrent rep views
  - Product filtering impact
  - Metrics calculation performance
  - Caching benefits

- **Metrics:**
  - Total load time
  - Component load success rate
  - Throughput (reps/second)
  - Filter performance impact

**Usage:**

```bash
pytest tests/performance/scenarios/dashboard_load.py -v -m performance
```

#### 4.3 Search Scenario

**File:** `/Users/gcoyne/src/prefect/call-coach/tests/performance/scenarios/search.py`

Tests complex search query performance:

- **7 Scenario Tests:**

  - Simple searches
  - Product-filtered searches
  - Rep-based searches
  - Date range searches
  - Score filter searches
  - Complex multi-filter searches
  - Result pagination and sorting

- **Metrics:**
  - Query execution time
  - Filter impact analysis
  - Result size impact
  - Sorting performance

**Usage:**

```bash
pytest tests/performance/scenarios/search.py -v -m performance
```

### 5. Report Generation

**File:** `/Users/gcoyne/src/prefect/call-coach/benchmarks/report.py`

HTML report generator with performance visualization:

- **Report Sections:**

  - Executive summary metrics
  - Endpoint performance table
  - Database query analysis
  - Cache performance metrics
  - Trend analysis
  - Regression detection results

- **Features:**
  - Percentile calculation (P50, P95, P99)
  - Status indicators (✓/⚠)
  - Responsive design
  - Printable format

**Usage:**

```bash
python benchmarks/report.py
```

Output: `benchmarks/reports/performance_report.html`

### 6. CI/CD Pipeline

**File:** `/Users/gcoyne/src/prefect/call-coach/.github/workflows/performance.yml`

Automated performance testing on every PR and push:

**Triggers:**

- Every PR to main/develop
- Every push to main/develop
- Daily schedule (2 AM UTC)

**Pipeline Steps:**

1. Set up PostgreSQL and Redis services
2. Install dependencies (pytest, pytest-benchmark, locust)
3. Set up test database
4. Start API server
5. Run API benchmarks with regression detection
6. Run database benchmarks
7. Run cache benchmarks
8. Run performance scenarios
9. Generate HTML report
10. Upload results as artifacts
11. Post results comment on PRs
12. Check performance thresholds
13. Run load test on main branch
14. Run stress test
15. Upload load test results

**Regression Detection:**

- Fails if mean response time increases >10%
- Compares against stored baseline
- Posts warning comments on failing PRs

**Performance Targets:**
| Endpoint | P50 | P95 | P99 |
|----------|-----|-----|-----|
| `/health` | <50ms | <100ms | <200ms |
| `/tools/analyze_call` | <1000ms | <3000ms | <5000ms |
| `/tools/get_rep_insights` | <500ms | <2000ms | <4000ms |
| `/tools/search_calls` | <300ms | <1000ms | <2000ms |
| `/tools/analyze_opportunity` | <2000ms | <5000ms | <8000ms |

### 7. Documentation

**File:** `/Users/gcoyne/src/prefect/call-coach/PERFORMANCE_TESTING.md`

Comprehensive documentation including:

- Overview of all testing components
- Detailed usage instructions for each test
- Performance targets and thresholds
- Troubleshooting guide
- Best practices
- Further reading resources

## File Structure

```
/Users/gcoyne/src/prefect/call-coach/
├── tests/performance/
│   ├── __init__.py
│   ├── load_test.py               # Locust load testing (100 users)
│   ├── stress_test.py             # Async stress testing (ramp-up)
│   └── scenarios/
│       ├── __init__.py
│       ├── coaching_analysis.py   # 100-call analysis scenario
│       ├── dashboard_load.py      # Rep dashboard scenario
│       └── search.py              # Search query scenario
├── benchmarks/
│   ├── __init__.py
│   ├── api_benchmarks.py          # 13 endpoint benchmarks
│   ├── db_benchmarks.py           # 14 query benchmarks
│   ├── cache_benchmarks.py        # 18 cache benchmarks
│   └── report.py                  # HTML report generator
├── .github/workflows/
│   └── performance.yml            # CI/CD pipeline
├── pyproject.toml                 # Updated with pytest-benchmark
├── PERFORMANCE_TESTING.md         # Complete documentation
└── PERFORMANCE_SUITE_SUMMARY.md   # This file
```

## Dependencies

Added to `pyproject.toml`:

```
pytest-benchmark>=4.0.0  # For microbenchmarking
locust>=2.17.0          # For load testing
```

Already included:

```
pytest>=8.0.0           # Testing framework
pytest-asyncio>=0.23.0  # Async testing
pytest-cov>=4.1.0       # Coverage reporting
httpx>=0.27.0           # HTTP client for API testing
```

## Quick Start

### Local Testing

```bash
# Install dependencies
pip install -e ".[dev]"

# Start API server in one terminal
python -m uvicorn api.rest_server:app --host 127.0.0.1 --port 8000

# In another terminal, run load test
locust -f tests/performance/load_test.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=5 \
  --run-time=5m

# Or run benchmarks
pytest benchmarks/api_benchmarks.py -v

# Or run scenarios
pytest tests/performance/scenarios/ -v -m performance

# Generate report
python benchmarks/report.py
```

### CI/CD Testing

The pipeline will automatically:

1. Run all benchmarks on every PR
2. Compare to baseline and flag regressions
3. Run load/stress tests on push to main
4. Generate detailed reports
5. Comment on PRs with results

## Performance Metrics Collected

### Load Testing

- Response time percentiles (P50, P95, P99)
- Throughput (requests/second)
- Error rate percentage
- Per-endpoint metrics

### Stress Testing

- Breaking point (users at failure)
- Error rates under increasing load
- Response time degradation
- Recovery behavior

### Benchmarks

- Execution time per operation
- Mean/min/max/stdev
- Baseline comparison
- Regression detection

### Scenarios

- End-to-end operation time
- Component success rates
- Cache effectiveness
- Filter performance impact

## Integration Points

The performance suite integrates with:

1. **GitHub Actions** - Automated CI/CD pipeline
2. **PostgreSQL** - Database performance testing
3. **Redis** - Cache performance testing
4. **FastAPI** - REST API endpoint testing
5. **Locust** - Load testing framework
6. **pytest-benchmark** - Microbenchmarking

## Future Enhancements

Potential improvements:

- Add tracing/profiling integration (Jaeger, Opentelemetry)
- Database query analysis with EXPLAIN PLAN
- Memory profiling with tracemalloc
- Network simulation for latency testing
- Historical trend visualization
- Automated baseline storage in S3/GCS
- Integration with performance monitoring tools

## Notes

- All tests are designed to run against mock/test data to avoid side effects
- The stress test automatically detects breaking points
- Load test can be run in headless mode for CI/CD
- Benchmarks are stored as JSON for trending
- CI/CD pipeline fails on >10% performance regression
- Reports include comparison to baseline

## Support

For detailed instructions, see `/Users/gcoyne/src/prefect/call-coach/PERFORMANCE_TESTING.md`

## Summary

A complete, production-ready performance testing suite has been created with:

- ✅ 6 load/stress test configurations
- ✅ 45+ individual benchmarks
- ✅ 19 real-world scenario tests
- ✅ Automated CI/CD pipeline
- ✅ HTML report generation
- ✅ Regression detection
- ✅ Complete documentation

The suite is ready for immediate use and will provide continuous performance monitoring throughout the development lifecycle.
