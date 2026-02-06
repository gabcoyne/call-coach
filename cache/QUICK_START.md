## Quick Start: Caching Layer

5-minute guide to using the caching system in call-coach.

### Installation

```bash
# Install dependencies
pip install redis>=5.0.0

# Start Redis (local development)
brew install redis  # macOS
brew services start redis

# Verify Redis is running
redis-cli ping
# Expected: PONG
```

### Configuration

Add to `.env`:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
ENABLE_CACHING=true
CACHE_TTL_DAYS=90
```

### Basic Usage

#### 1. Use Redis Cache Directly

```python
from cache import get_redis_cache
from db.models import CoachingDimension

# Get cache instance
redis_cache = get_redis_cache()

# Store session
redis_cache.set(
    dimension=CoachingDimension.DISCOVERY,
    transcript_hash="abc123",
    rubric_version="1.0.0",
    session_data={
        "score": 85,
        "strengths": ["Good discovery"],
    }
)

# Retrieve session
cached = redis_cache.get(
    dimension=CoachingDimension.DISCOVERY,
    transcript_hash="abc123",
    rubric_version="1.0.0"
)
```

#### 2. Use Existing Analysis Engine (Automatic Caching)

```python
from analysis.engine import get_or_create_coaching_session

# This automatically checks cache before analysis
session = get_or_create_coaching_session(
    call_id=call_id,
    rep_id=rep_id,
    dimension=CoachingDimension.DISCOVERY,
    transcript=transcript,
    force_reanalysis=False  # True to bypass cache
)
```

#### 3. Use Prompt Caching with Claude

```python
from cache.prompt_cache import PromptCacheManager

prompt_cache = PromptCacheManager()

# Build cached messages (rubrics, KB cached)
messages = prompt_cache.format_cached_messages(
    dimension=dimension,
    transcript=transcript,
    rubric=rubric,
    knowledge_base=kb_content
)

# Use with Claude API (caching automatic)
response = anthropic_client.messages.create(
    model="claude-sonnet-4-5-20250929",
    messages=messages
)
```

### Common Operations

#### Warm Cache

```bash
# Warm all caches (last 30 days)
python -m cache.warming --days 30

# Warm specific dimension
python -m cache.warming --dimension discovery --days 7
```

#### Check Cache Statistics

```bash
# Get comprehensive stats
python -m monitoring.cache_stats --days 7

# Dimension breakdown
python -m monitoring.cache_stats --dimension-breakdown
```

#### Invalidate Cache

```python
from cache import get_redis_cache
from db.models import CoachingDimension

redis_cache = get_redis_cache()

# Invalidate all for dimension
redis_cache.invalidate_dimension(
    dimension=CoachingDimension.DISCOVERY,
    rubric_version="1.0.0"  # or None for all versions
)
```

### Database Setup

```bash
# Apply performance indexes (one time)
./scripts/apply_performance_optimizations.sh

# Verify indexes
./scripts/apply_performance_optimizations.sh --verify-only
```

### Monitoring

#### Check Cache Health

```python
from monitoring.cache_stats import get_cache_metrics

stats = get_cache_metrics(days_back=7)
print(f"Cache hit rate: {stats['database']['cache_hit_rate']}%")
print(f"Cost savings: ${stats['cost_savings']['cost_savings_usd']}")
```

#### Prometheus Metrics

```bash
# Export metrics
python -m monitoring.cache_stats --format prometheus
```

### Troubleshooting

#### Redis Not Available

```bash
# Check if Redis is running
redis-cli ping

# Check connection
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# View Redis info
redis-cli INFO stats
```

#### Low Cache Hit Rate

```bash
# Check cache stats
python -m monitoring.cache_stats

# Warm cache
python -m cache.warming --days 30

# Verify TTL
echo $CACHE_TTL_DAYS
```

#### Slow Queries

```sql
-- Check index usage
SELECT * FROM get_index_usage_stats();

-- Refresh materialized views
SELECT refresh_rep_performance_view();

-- Check query plans
SELECT analyze_query_plan('YOUR QUERY');
```

### Production Deployment

```bash
# 1. Install Redis
apt-get install redis-server

# 2. Apply DB optimizations
./scripts/apply_performance_optimizations.sh

# 3. Warm cache
python -m cache.warming --days 30

# 4. Schedule maintenance (crontab)
0 2 * * * python -m cache.warming --days 30
0 3 * * * psql $DATABASE_URL -c "SELECT refresh_rep_performance_view();"

# 5. Monitor
python -m monitoring.cache_stats
```

### Key Metrics

**Target**: 60-80% cache hit rate
**Cost Savings**: ~$197/month for 20 calls/day
**Query Performance**: 10x improvement

### Need Help?

1. Check `cache/README.md` for detailed docs
2. Review `CACHING_PERFORMANCE_IMPLEMENTATION.md` for architecture
3. Run tests: `pytest tests/cache/`
