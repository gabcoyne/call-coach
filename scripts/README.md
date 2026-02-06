# Batch Processing Scripts

This directory contains scripts for batch processing Gong calls with AI coaching analysis.

## Overview

The batch processing workflow has two main steps:

1. **Load Transcripts** (`load_transcripts.py`) - Fetches call transcripts from Gong API
2. **Analyze Calls** (`batch_analyze_calls.py`) - Runs AI coaching analysis on all calls

## Prerequisites

- Database with calls loaded (run Gong sync first)
- Gong API credentials configured in `.env`
- Anthropic API key configured in `.env`

## Usage

### Step 1: Load Transcripts

This script fetches transcripts from Gong for all calls that don't have transcripts yet.

```bash
# Load transcripts for all calls (takes ~50 seconds per call)
uv run python scripts/load_transcripts.py

# For 100 calls, expect ~80-90 minutes runtime
# Uses 3 concurrent workers to respect Gong API rate limits
```

**What it does:**

- Queries database for calls without transcripts
- Fetches call metadata and transcripts from Gong API
- Stores transcript sentences in database
- Creates default speaker records if Gong doesn't return participants
- Logs progress to `logs/load_transcripts.log`

**Output:**

```
Starting batch transcript loading from Gong
================================================================================
Found 100 calls needing transcripts
Loading transcripts for 100 calls with 3 concurrent workers

[1/100] ✓ 6478583504175344664: 420 sentences, 1 speakers (48.06s)
[2/100] ✓ 5658057227506738128: 512 sentences, 1 speakers (51.23s)
...

Batch transcript loading complete!
================================================================================
Total calls processed: 100
Successful: 98
Failed: 2
Total transcript sentences: 42,315
Total duration: 82.5 minutes
```

### Step 2: Batch Analyze Calls

This script runs AI coaching analysis on all calls with transcripts.

```bash
# Analyze all calls across 4 dimensions
uv run python scripts/batch_analyze_calls.py

# For 100 calls × 4 dimensions = 400 analyses
# With 5 concurrent workers, expect ~60-90 minutes runtime
# Cost: ~$15-25 (depends on transcript length and caching)
```

**What it does:**

- Queries database for calls without coaching sessions
- For each call, analyzes across 4 dimensions:
  - `discovery` - Discovery methodology (SPICED, Challenger, Sandler)
  - `objection_handling` - Objection handling skills
  - `product_knowledge` - Technical accuracy and expertise
  - `engagement` - Talk ratio, listening, rapport
- Stores coaching sessions with scores, strengths, improvements, examples
- Uses caching to avoid re-analyzing identical transcripts
- Logs progress to `logs/batch_analyze.log`

**Output:**

```
Starting batch analysis of calls
================================================================================
Found 100 calls needing analysis
Analyzing 100 calls with 5 concurrent workers

[1/100] ✓ 6478583504175344664: 4/4 dimensions completed (32.5s)
[2/100] ✓ 5658057227506738128: 4/4 dimensions completed (28.1s)
...

Batch analysis complete!
================================================================================
Total calls processed: 100
Successful: 98
Failed: 2
Total dimensions analyzed: 392
Total duration: 68.3 minutes

Coaching sessions in database: 392
Calls with coaching sessions: 98
```

## Architecture

### Concurrency

- **Transcript loading**: 3 concurrent workers (respects Gong API rate limits)
- **Coaching analysis**: 5 concurrent workers (Claude API is more forgiving)

### Error Handling

- Each call is processed independently
- Failures don't block other calls
- Errors are logged with full stack traces
- Summary includes success/failure counts

### Caching

The analysis engine uses intelligent caching based on:

- Transcript hash (SHA256 of full transcript text)
- Rubric version (semantic version of evaluation criteria)
- Coaching dimension

This means:

- Identical transcripts analyzed with same rubric = instant cache hit
- Updated rubrics automatically invalidate cache for new insights
- Costs are minimized through cache reuse

### Performance

Typical timings:

- Load transcript: 40-60 seconds per call
- Analyze one dimension: 6-10 seconds per call
- Analyze all 4 dimensions: 25-35 seconds per call

For 100 calls:

- Transcript loading: ~80 minutes (sequential bottleneck is Gong API)
- Coaching analysis: ~60 minutes (parallelized across 5 workers)
- **Total: ~2.5 hours end-to-end**

## Monitoring

### Logs

All scripts write detailed logs to `logs/` directory:

- `logs/load_transcripts.log` - Transcript loading progress and errors
- `logs/batch_analyze.log` - Analysis progress and errors

### Database Queries

Check progress in real-time:

```sql
-- Calls with transcripts
SELECT COUNT(DISTINCT call_id) FROM transcripts;

-- Calls with coaching sessions
SELECT COUNT(DISTINCT call_id) FROM coaching_sessions;

-- Coaching sessions by dimension
SELECT
    coaching_dimension,
    COUNT(*) as sessions,
    AVG(score) as avg_score
FROM coaching_sessions
GROUP BY coaching_dimension;

-- Recent coaching sessions
SELECT
    c.title,
    cs.coaching_dimension,
    cs.score,
    cs.created_at
FROM coaching_sessions cs
JOIN calls c ON cs.call_id = c.id
ORDER BY cs.created_at DESC
LIMIT 10;
```

## Troubleshooting

### Missing speakers

If Gong doesn't return participant data, the script creates a default "Unknown Rep" speaker with `company_side = true`. This allows analysis to proceed.

### Failed transcript loads

Common causes:

- Gong API rate limits (429 errors) - script automatically retries with backoff
- Call doesn't have transcript yet in Gong - skip and retry later
- Network timeouts - increase timeout in `gong/client.py`

### Failed analyses

Common causes:

- No transcript for call - run `load_transcripts.py` first
- No company rep found - check speaker creation logic
- Claude API errors - check `ANTHROPIC_API_KEY` in `.env`
- Malformed analysis response - check prompt templates in `analysis/prompts.py`

### JSONB serialization errors

If you see `can't adapt type 'dict'` errors, make sure JSONB fields are being serialized:

- Use `json.dumps()` for dict values
- Cast to `::jsonb` in SQL query
- Check `flows/process_new_call.py` and `analysis/cache.py` for examples

## Cost Estimation

For 100 calls with average transcript length:

**Gong API:**

- Free (included in Gong subscription)

**Claude API (Sonnet 4.5):**

- Input tokens: ~4000 per dimension
- Output tokens: ~4500 per dimension
- Cache creation: ~3000 tokens first analysis
- Cache hits: Nearly free for subsequent analyses
- **Cost per call**: ~$0.15-0.25 (4 dimensions)
- **Total for 100 calls**: ~$15-25

With intelligent caching, subsequent runs on similar transcripts are much cheaper.

## Next Steps

After batch analysis completes:

1. **Verify data**: Check coaching_sessions table has expected records
2. **Test MCP tools**: Use `analyze_call` and `get_rep_insights` tools
3. **Build UI**: Frontend can query coaching_sessions for dashboards
4. **Set up automation**: Run daily via Prefect flows on new calls

## Development

To test on a subset of calls:

```python
# Test with just 5 calls
uv run python -c "
from scripts.batch_analyze_calls import batch_analyze_calls
from db import fetch_all, fetch_one

# Get 5 calls
calls = fetch_all('''
    SELECT c.id, c.gong_call_id, c.title
    FROM calls c
    LEFT JOIN coaching_sessions cs ON c.id = cs.call_id
    WHERE cs.id IS NULL
    LIMIT 5
''')

from concurrent.futures import ThreadPoolExecutor
from scripts.batch_analyze_calls import analyze_single_call

results = []
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(analyze_single_call, call) for call in calls]
    for future in futures:
        results.append(future.result())

for r in results:
    print(f'{r[\"gong_call_id\"]}: {len(r[\"dimensions_completed\"])}/4 dimensions')
"
```
