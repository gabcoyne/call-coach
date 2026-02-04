# Gong Call Coaching Agent for Prefect Sales Teams

AI-powered sales coaching system that analyzes Gong calls for SEs, AEs, and CSMs across Prefect and Horizon products.

## Architecture

- **FastMCP Server**: On-demand coaching tools via MCP protocol
- **Prefect Flows on Horizon**: Webhook processing and scheduled batch reviews
- **Claude API**: AI-powered call analysis and coaching generation
- **Neon Postgres**: Coaching data, metrics, and knowledge base
- **Gong Integration**: Webhooks and API for call data

## Key Features

- **Intelligent Caching**: 60-80% cost reduction through transcript hashing and rubric versioning
- **Parallel Analysis**: 4x faster processing with concurrent dimension analysis
- **Long Call Support**: Sliding window chunking for 60+ minute calls
- **Real-time Ingestion**: Async webhook handling with <3s response time
- **Trend Analysis**: Performance tracking across reps and time periods

## Project Structure

```
call-coach/
├── db/                 # Database schema and migrations
├── gong/               # Gong API client and webhook handling
├── analysis/           # Claude-powered coaching analysis engine
├── knowledge/          # Coaching rubrics and product documentation
├── mcp/                # FastMCP server and tools
├── flows/              # Prefect flows for automation
├── reports/            # Report generation and templates
└── tests/              # Test suite
```

## Setup

1. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Initialize database**:
   ```bash
   psql $DATABASE_URL -f db/migrations/001_initial_schema.sql
   ```

4. **Load knowledge base**:
   ```bash
   python -m knowledge.loader
   ```

5. **Run FastMCP server**:
   ```bash
   python -m mcp.server
   ```

6. **Deploy Prefect flows**:
   ```bash
   prefect deploy flows/process_new_call.py
   prefect deploy flows/weekly_review.py
   ```

## Usage

### On-Demand Coaching (MCP Tools)

Use with Claude Desktop or API:

```
"Analyze call abc-123 and focus on discovery quality"
"Show me Sarah's performance trends this month"
"Compare calls xyz-456 and xyz-789 for objection handling"
```

### Weekly Reviews (Automated)

Scheduled every Monday at 6am PT:
- Analyzes all calls from previous week
- Generates rep-specific coaching reports
- Sends team-wide insights to sales leadership

## Development

### Run tests
```bash
pytest tests/
```

### Local development with Docker Compose
```bash
docker-compose up
```

### Check cost metrics
```bash
python -m analysis.metrics
```

## Cost Optimization

- **Baseline**: ~$1,787/month (100 calls/week, no optimization)
- **Optimized**: ~$317/month (82% reduction)
- **Per call**: $3.17 (vs. $17.87 baseline)

Key optimizations:
1. Intelligent caching (60-80% cache hit rate)
2. Prompt caching (50% input token reduction)
3. Parallel execution (4x faster, same cost)

## Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [MCP Tools Reference](docs/MCP_TOOLS.md)
- [Coaching Rubrics](docs/COACHING_RUBRICS.md)

## License

Proprietary - Prefect Technologies, Inc.
