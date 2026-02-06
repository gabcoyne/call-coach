# Performance Testing and Benchmarking Suite

Comprehensive performance testing suite for the Call Coaching API. Includes load testing, stress testing, benchmarking, and performance scenarios.

## Overview

The performance suite is organized into four main components:

### 1. Load Testing (`tests/performance/load_test.py`)

Simulates realistic user load on the API using Locust.

**Features:**

- 100 concurrent users simulation
- 1000+ coaching analyses
- Multiple search query patterns
- Measures response times, throughput, and error rates
- Tests all major API endpoints

**Usage:**

```bash
# Run load test locally
locust -f tests/performance/load_test.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=5 \
  --run-time=5m

# Run load test headless
locust -f tests/performance/load_test.py \
  --headless \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=5 \
  --run-time=5m \
  --csv=load_test_results
```

**Metrics Collected:**

- Response time percentiles (P50, P95, P99)
- Throughput (requests/second)
- Error rate percentage
- Success/failure counts

### 2. Stress Testing (`tests/performance/stress_test.py`)

Pushes the system to its limits to identify breaking points.

**Features:**

- Gradual ramp-up from 10 to 1000 concurrent users
- Automatic detection of breaking points
- Tests recovery after failures
- Resource utilization monitoring

**Usage:**

```bash
# Run stress test
python tests/performance/stress_test.py

# With custom parameters
python -c "
from tests.performance.stress_test import StressTestRunner
import asyncio

runner = StressTestRunner(
    base_url='http://localhost:8000',
    initial_users=10,
    max_users=500,
    ramp_up_interval=30,
    requests_per_user=50
)
metrics = asyncio.run(runner.run())
runner.print_summary()
"
```

**Key Metrics:**

- Breaking point identification (users at which system fails)
- Error rates under load
- Response times at different concurrency levels
- Recovery behavior

### 3. Benchmarking Suite

#### API Benchmarks (`benchmarks/api_benchmarks.py`)

Measures performance of individual API endpoints using pytest-benchmark.

**Features:**

- Endpoint-specific performance measurement
- Cache vs. non-cache comparison
- Complex query benchmarking
- Regression detection

**Usage:**

```bash
# Run API benchmarks
pytest benchmarks/api_benchmarks.py -v

# With baseline comparison
pytest benchmarks/api_benchmarks.py \
  --benchmark-json=results.json \
  --benchmark-compare=baseline.json \
  --benchmark-compare-fail=mean:10%

# Run specific benchmark
pytest benchmarks/api_benchmarks.py::TestAPIBenchmarks::test_analyze_call_cached -v
```

**Benchmarked Endpoints:**

- `/health` - Health check
- `/tools/analyze_call` - Call analysis (cached/uncached/with transcript)
- `/tools/get_rep_insights` - Rep insights (7/30/90 days, with product filter)
- `/tools/search_calls` - Search (simple, product filter, date range, complex)
- `/tools/analyze_opportunity` - Opportunity analysis

#### Database Benchmarks (`benchmarks/db_benchmarks.py`)

Measures database query performance and identifies optimization opportunities.

**Features:**

- Query execution time tracking
- Index usage verification
- Connection pool performance
- Batch operation optimization

**Usage:**

```bash
# Run database benchmarks
pytest benchmarks/db_benchmarks.py -v

# Focus on slow queries
pytest benchmarks/db_benchmarks.py -k "complex_filters" -v
```

**Measured Queries:**

- Call metadata retrieval
- Transcript fetching
- Rep-based searches
- Product-based searches
- Date range queries
- Rep statistics
- Opportunity analysis

#### Cache Benchmarks (`benchmarks/cache_benchmarks.py`)

Measures Redis cache performance.

**Features:**

- GET/SET operation latency
- Cache hit/miss scenarios
- Serialization/deserialization overhead
- Memory usage patterns
- Eviction and invalidation performance

**Usage:**

```bash
# Run cache benchmarks
pytest benchmarks/cache_benchmarks.py -v

# Run specific test
pytest benchmarks/cache_benchmarks.py::TestCacheBenchmarks::test_cache_hit_scenario -v
```

**Measured Operations:**

- Cache read/write latency
- Batch operations
- Pattern-based invalidation
- Compression overhead
- Memory management

### 4. Performance Scenarios

Real-world usage patterns that combine multiple operations.

#### Coaching Analysis Scenario (`tests/performance/scenarios/coaching_analysis.py`)

Analyzes 100 coaching calls in sequence.

```bash
pytest tests/performance/scenarios/coaching_analysis.py -v -m performance
```

**Tests:**

- Sequential analysis of 100 calls
- Different dimension configurations
- Cache effectiveness measurement
- Analysis with transcript snippets
- Parallel analysis patterns

#### Dashboard Load Scenario (`tests/performance/scenarios/dashboard_load.py`)

Tests dashboard loading performance for sales reps.

```bash
pytest tests/performance/scenarios/dashboard_load.py -v -m performance
```

**Tests:**

- Single rep dashboard load
- Multi-rep dashboard load
- Different time periods (7/30/90 days)
- Concurrent rep views
- Product filtering impact
- Caching benefits

#### Search Scenario (`tests/performance/scenarios/search.py`)

Tests complex search query performance.

```bash
pytest tests/performance/scenarios/search.py -v -m performance
```

**Tests:**

- Simple searches
- Product-filtered searches
- Date range searches
- Complex multi-filter searches
- Result pagination
- Result sorting

## Performance Report Generation

The suite includes an HTML report generator (`benchmarks/report.py`) that creates detailed performance reports.

**Usage:**

```bash
# Generate sample report
python benchmarks/report.py

# Report includes:
# - Response time metrics (P50, P95, P99)
# - Endpoint performance comparison
# - Database query analysis
# - Cache hit rates and performance
# - Historical trend data
```

Report is saved to: `benchmarks/reports/performance_report.html`

## CI/CD Integration

The performance test pipeline (`.github/workflows/performance.yml`) runs automatically on:

- Every pull request
- Every push to main/develop
- Daily schedule (2 AM UTC)

**Pipeline Steps:**

1. Set up test environment (PostgreSQL, Redis)
2. Start API server
3. Run API benchmarks (with regression detection)
4. Run database benchmarks
5. Run cache benchmarks
6. Run performance scenarios
7. Generate HTML report
8. Upload results as artifacts
9. Comment on PR with results

**Regression Detection:**

- Fails if mean response time increases >10%
- Compares against baseline results
- Posts warning comments on PRs

## Setting Up Baselines

To establish performance baselines:

```bash
# Generate initial baselines
pytest benchmarks/api_benchmarks.py \
  --benchmark-json=benchmarks/.benchmarks/api_baseline.json

pytest benchmarks/db_benchmarks.py \
  --benchmark-json=benchmarks/.benchmarks/db_baseline.json

pytest benchmarks/cache_benchmarks.py \
  --benchmark-json=benchmarks/.benchmarks/cache_baseline.json

# Store these files in version control for future comparisons
```

## Performance Targets

Recommended response time targets:

| Endpoint                     | P50     | P95     | P99     |
| ---------------------------- | ------- | ------- | ------- |
| `/health`                    | <50ms   | <100ms  | <200ms  |
| `/tools/analyze_call`        | <1000ms | <3000ms | <5000ms |
| `/tools/get_rep_insights`    | <500ms  | <2000ms | <4000ms |
| `/tools/search_calls`        | <300ms  | <1000ms | <2000ms |
| `/tools/analyze_opportunity` | <2000ms | <5000ms | <8000ms |

**System Targets:**

- Error rate: <1%
- Throughput: >50 req/s (100 concurrent users)
- Breaking point: >500 concurrent users
- Cache hit rate: >80%

## Troubleshooting

### API Server Not Responding

```bash
# Ensure API is running
curl http://localhost:8000/health

# Start the server if needed
python -m uvicorn api.rest_server:app --host 127.0.0.1 --port 8000
```

### Database Connection Issues

```bash
# Check database is running
psql postgresql://postgres:postgres@localhost:5432/call_coaching -c "SELECT 1"

# Check connection string
echo $DATABASE_URL
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping

# Check connection string
echo $REDIS_URL
```

### Benchmark Regression Detected

```bash
# Review the detailed report
open benchmarks/reports/performance_report.html

# Profile the slow endpoint
python -m cProfile -s cumtime api/rest_server.py

# Check database query plans
# SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

## Best Practices

1. **Run benchmarks consistently**: Always use the same hardware for baseline comparisons
2. **Isolate variables**: Test one change at a time
3. **Warm up before measuring**: Let the system reach steady state before collecting metrics
4. **Monitor resources**: Check CPU, memory, and I/O during tests
5. **Test realistic scenarios**: Use patterns that match real user behavior
6. **Store baselines**: Keep historical benchmarks to track improvements

## Further Reading

- [Locust Documentation](https://docs.locust.io/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance.html)
- [Redis Benchmarking](https://redis.io/docs/management/optimization/benchmarks/)
