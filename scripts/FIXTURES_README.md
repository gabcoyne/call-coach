# Fixtures Generator

A comprehensive script for generating realistic sample data and fixtures for the call coaching application.

## Overview

The `generate_fixtures.py` script creates realistic sample data that mimics actual Gong data structures. It includes:

- **Prefect Employee Speakers**: Account Executives (AEs), Sales Engineers (SEs), Customer Success Managers (CSMs) with @prefect.io emails
- **Realistic Calls**: Discovery, demo, technical, and negotiation calls with varied durations and dates
- **Call Transcripts**: Realistic dialogue between sales reps and prospects with multiple segments per call
- **Opportunities**: Sales opportunities with various stages, amounts, and health scores
- **Call-Opportunity Links**: Associations between calls and opportunities
- **Coaching Sessions**: Varied coaching feedback across multiple dimensions (product knowledge, discovery, objection handling, engagement)
- **Emails**: Realistic sales email threads linked to opportunities
- **Speaker Participation**: Multiple speakers per call with talk time percentages

## Installation

The script uses only dependencies already installed in the project:

```bash
# Just ensure your environment is set up
uv sync
```

## Usage

### Basic Usage

Generate 20 sample calls (default):

```bash
uv run python scripts/generate_fixtures.py
```

### With Custom Parameters

```bash
# Generate 50 calls spanning last 6 months
uv run python scripts/generate_fixtures.py --num-calls 50 --days-back 180

# Generate with reproducible results (same data each time)
uv run python scripts/generate_fixtures.py --num-calls 30 --seed 42

# Set up a demo account with realistic data for stakeholder presentations
uv run python scripts/generate_fixtures.py --demo-account
```

### Command-Line Options

- `--num-calls N`: Number of calls to generate (default: 20)
- `--days-back N`: Generate calls from the last N days (default: 90)
- `--seed N`: Random seed for reproducible results (default: none)
- `--demo-account`: Generate a larger, more realistic dataset (50 calls, 6 months history)

## Generated Data

### Speakers (Prefect Employees)

- 4 Account Executives (AEs)
- 3 Sales Engineers (SEs)
- 2 Customer Success Managers (CSMs)

All have realistic names and @prefect.io email addresses.

### Calls

Each call includes:

- Realistic title from actual sales call types
- Random date within the lookback period
- Duration between 10-90 minutes
- Call type: discovery, demo, technical deep dive, negotiation, or follow-up
- Product focus: Prefect, Horizon, or both

### Call Participants

Each call has:

- 1-2 Prefect employees (company-side speakers)
- 1-3 prospect/customer participants
- Talk time breakdown and percentages
- Realistic role assignments

### Transcripts

Generated with:

- 10-20 transcript lines per call
- Realistic dialogue based on call type
- Sentiment labels (positive, neutral, negative)
- Extracted topics relevant to sales conversations
- Sequential ordering with timestamps

### Coaching Sessions

For each call, generates 0-3 coaching sessions with:

- One of 4 dimensions: product_knowledge, discovery, objection_handling, engagement
- Score between 0-100 (correlated with dimension)
- 2-3 strength areas specific to the dimension
- 1-2 improvement areas with concrete feedback
- Specific examples with quotes and analysis
- 1-3 action items for continued development
- Full narrative analysis
- Session type: real_time, weekly_review, or on_demand
- Analyst attribution (Claude models)

### Opportunities

Generated with:

- Realistic company names and deal stages
- Random amounts between $50k-$300k
- Health scores from 30-95
- Assigned to Account Executives
- Created 15-90 days ago
- Close dates 7-120 days in the future
- Link to 1-3 calls per opportunity

### Emails

For each opportunity:

- 2-5 realistic sales emails
- Subject lines matching call topics
- Bodies with realistic sales language
- Sender is always a Prefect employee
- Recipients are prospect company domains
- 33% include attachments
- Linked to appropriate opportunities

## Examples

### Quick Demo Setup

```bash
uv run python scripts/generate_fixtures.py --demo-account
```

This generates:

- 50 calls across 6 months of history
- 100+ transcripts
- 30+ coaching sessions
- 20+ opportunities
- 50+ emails
- 30+ speakers and participants

### Development Workflow

```bash
# First time setup
uv run python scripts/generate_fixtures.py --num-calls 20 --seed 42

# Now you have consistent, reproducible data for development
# The seed ensures you get the same data on subsequent runs
```

### Testing Multiple Scenarios

```bash
# Generate with different random seeds for variety
uv run python scripts/generate_fixtures.py --num-calls 15 --seed 1
uv run python scripts/generate_fixtures.py --num-calls 15 --seed 2
uv run python scripts/generate_fixtures.py --num-calls 15 --seed 3
```

## Data Customization

The script includes several template systems for customization:

### Adding More Content

Edit the templates at the top of `generate_fixtures.py`:

- `FIRST_NAMES`, `LAST_NAMES`: Modify speaker names
- `COMPANY_NAMES`: Add more prospects
- `CALL_TITLES`: Vary call titles
- `PAIN_POINTS`: Change problems discussed
- `TRANSCRIPT_TEMPLATES`: Add conversation patterns

### Modifying Generation Parameters

The `FixturesGenerator` class can be imported and used directly:

```python
from scripts.generate_fixtures import FixturesGenerator

generator = FixturesGenerator(
    num_calls=100,
    days_back=365,
    seed=42
)

# Generate individual components
speakers = generator.generate_speakers()
opportunities = generator.generate_opportunities(num_opportunities=10)
calls = generator.generate_calls()

# Or generate everything
counts = generator.generate_all()
```

## Database Requirements

The script requires:

- PostgreSQL database connection (via DATABASE_URL environment variable)
- Database schema already created (from migrations)
- Tables: calls, speakers, transcripts, opportunities, call_opportunities, coaching_sessions, emails

## Logging

All operations are logged to `logs/generate_fixtures.log` with:

- Execution time tracking
- Progress indicators
- Summary statistics of generated data
- Error messages with full stack traces

Check the log file for details about what was generated:

```bash
tail -f logs/generate_fixtures.log
```

## Reproducibility

Use the `--seed` parameter to generate identical data across runs. This is useful for:

- Consistent testing environments
- Reproducible bug reports
- Comparing UI/backend changes without data variance

```bash
# These will generate identical data
uv run python scripts/generate_fixtures.py --num-calls 50 --seed 123
uv run python scripts/generate_fixtures.py --num-calls 50 --seed 123
```

## Notes

- Data is inserted with `ON CONFLICT DO NOTHING` to allow re-running without errors
- All IDs are randomly generated UUIDs for realistic data
- Dates are relative to "now" for fresh data on each run (unless seed is used)
- All Prefect employees use @prefect.io domains
- All prospect emails use realistic domains (e.g., @acme.com)
- Coaching scores are correlated with dimension for realism

## Troubleshooting

### Script doesn't find database

Ensure `DATABASE_URL` environment variable is set:

```bash
export DATABASE_URL="postgresql://user:pass@localhost/callcoach"
uv run python scripts/generate_fixtures.py
```

### Data already exists

The script uses `ON CONFLICT DO NOTHING`, so you can safely re-run it:

```bash
# This will add new data without duplicating existing records
uv run python scripts/generate_fixtures.py --num-calls 100
```

### Large dataset generation takes time

For very large datasets, consider increasing the process:

```bash
# Generate in chunks with different seeds
for i in {1..5}; do
  uv run python scripts/generate_fixtures.py --num-calls 50 --seed $i
done
```

## Performance

Typical generation times:

- 20 calls: ~1-2 seconds
- 50 calls: ~2-3 seconds
- 100 calls: ~5-10 seconds

Database insertion typically adds 2-5 seconds depending on load.

## Testing

Run the test suite:

```bash
uv run pytest tests/test_generate_fixtures.py -v
```

This verifies:

- Data generation functions
- Realistic content in all fields
- Proper structure and relationships
- Reproducibility with seeds
