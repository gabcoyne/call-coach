# Quick Start - Gong Call Coaching Agent

Get up and running in 5 minutes.

## What This Does

Analyzes sales calls from Gong using Claude AI to provide coaching insights on:
- **Product Knowledge**: Technical accuracy and positioning
- **Discovery**: Question quality and listening skills
- **Objection Handling**: Response effectiveness
- **Engagement**: Talk ratios and rapport building

## Architecture at a Glance

```
Gong → Webhook → Prefect Flow → Postgres → Claude API → MCP Tools
```

## Installation

```bash
# Clone and setup
git clone <repo-url>
cd call-coach
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Start local environment
make dev
```

## Quick Test

```bash
# Run tests
make test

# Test webhook endpoint
curl http://localhost:8000/webhooks/health

# Check database
psql $DATABASE_URL -c "\dt"
```

## Next Steps

1. **Phase 1 (Complete):** Foundation and webhook handling ✅
2. **Phase 2 (Next):** Load coaching rubrics and product knowledge
3. **Phase 3:** Implement Claude API analysis
4. **Phase 4:** Build MCP tools for on-demand coaching
5. **Phase 5:** Add automated weekly reviews
6. **Phase 6:** Production hardening

See [STATUS.md](STATUS.md) for detailed progress.

## Key Files

- `webhook_server.py` - Webhook endpoint
- `flows/process_new_call.py` - Prefect flow for ingestion
- `analysis/engine.py` - Coaching analysis engine
- `db/migrations/001_initial_schema.sql` - Database schema
- `SETUP.md` - Detailed setup instructions

## Cost Estimates

- **Without optimization:** $1,787/month (100 calls/week)
- **With caching:** $317/month (82% reduction)
- **Per call:** $3.17

## Need Help?

Check [SETUP.md](SETUP.md) for detailed instructions and troubleshooting.
