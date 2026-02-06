# Local Development Setup

Get the Call Coach backend and frontend running locally for development.

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** - Check with `python3 --version`
- **Node.js 20+** - Check with `node --version`
- **PostgreSQL 15+** (optional: use Neon cloud database)
- **uv** - Python package manager ([install](https://github.com/astral-sh/uv))
- **Git** - For version control
- **Clerk account** - For authentication ([create free account](https://clerk.com))

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/prefect-teams/call-coach.git
cd call-coach

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install uv (recommended Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Claude API (get from https://console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-...

# Gong API (get from Gong dashboard)
GONG_API_KEY=your_gong_access_key
GONG_API_SECRET=your_gong_secret_key
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2  # Replace with your tenant URL

# Database (create free instance at https://console.neon.tech)
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/callcoach?sslmode=require

# Optional: Gong webhook verification
GONG_WEBHOOK_SECRET=optional_webhook_secret

# Logging
LOG_LEVEL=INFO
```

### Getting Credentials

**Anthropic API Key:**

1. Go to <https://console.anthropic.com/settings/keys>
2. Create new API key
3. Copy and paste into `.env`

**Gong API Credentials:**

1. Log in to Gong (<https://gong.app.gong.io>)
2. Go to Settings → Integrations → API
3. Copy API key and secret
4. Find your tenant URL (usually `https://us-XXXXX.api.gong.io/v2`)

**Neon Database:**

1. Create account at <https://console.neon.tech>
2. Create new project
3. Copy connection string (must include `?sslmode=require`)
4. Example: `postgresql://user:pass@ep-abc123.us-east-2.aws.neon.tech/callcoach?sslmode=require`

## Step 3: Initialize Database

Create tables and schema:

```bash
# Install psql if needed
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql-client
# Windows: Download PostgreSQL installer

# Run migrations
psql $DATABASE_URL -f db/migrations/001_initial_schema.sql

# Verify tables created
psql $DATABASE_URL -c "\dt"

# Expected output:
#  public | calls               | table
#  public | speakers            | table
#  public | transcripts         | table
#  public | coaching_sessions   | table
#  ...
```

## Step 4: Start Backend Services

**Terminal 1 - FastMCP Server (MCP tools)**:

```bash
# Navigate to project root
cd /Users/gcoyne/src/prefect/call-coach

# Development mode (fast startup, relaxed validation)
uv run mcp-server-dev

# Expected output:
# ✓ All required environment variables present
# ✓ Database connection successful
# ✓ Gong API authentication successful
# ✓ Anthropic API key validated
# 🚀 MCP server ready - 3 tools registered
# Server running on http://localhost:8000
```

**Terminal 2 - REST API Server** (for frontend integration):

```bash
cd /Users/gcoyne/src/prefect/call-coach

# Start REST API (rebuilds on changes)
uv run uvicorn api.rest_server:app --host 0.0.0.0 --port 8001 --reload

# Expected output:
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8001
```

## Step 5: Setup Frontend

**Terminal 3 - Next.js Frontend**:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with Clerk credentials
```

Configure `frontend/.env.local`:

```bash
# Clerk Authentication (create at https://clerk.com)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# MCP Backend URL
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8001

# Optional Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

**Start the frontend:**

```bash
npm run dev

# Expected output:
# ▲ Next.js 15.1.6
# - Local:    http://localhost:3000
# ✓ Ready in 1.5s
```

## Step 6: Verify Everything Works

Open your browser and test:

1. **Frontend**: <http://localhost:3000>

   - Should show landing page
   - Try signing in with Clerk

2. **API Docs**: <http://localhost:8001/docs>

   - Interactive Swagger UI
   - Can test API endpoints

3. **API ReDoc**: <http://localhost:8001/redoc>

   - Alternative API documentation

4. **Health Check**:

   ```bash
   curl http://localhost:8001/coaching/health
   # Expected: {"status": "healthy"}
   ```

## Development Workflow

### Backend Development

**Make changes to Python code:**

```bash
# Edit files in:
# - coaching_mcp/
# - analysis/
# - db/
# - gong/

# Server auto-reloads on save
# Check logs for errors
```

**Run tests:**

```bash
pytest tests/ -v

# Run specific test file:
pytest tests/test_chunking.py -v

# Run with coverage:
pytest tests/ --cov=coaching_mcp --cov-report=html
```

**Check code quality:**

```bash
# Format code
black coaching_mcp/ analysis/ db/

# Lint
ruff check coaching_mcp/ analysis/

# Type checking
mypy coaching_mcp/
```

### Frontend Development

**Make changes to React code:**

```bash
# Edit files in:
# - frontend/app/
# - frontend/components/
# - frontend/lib/

# Next.js auto-reloads on save
# Check browser console for errors
```

**Run tests:**

```bash
cd frontend

# Run tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

**Format and lint:**

```bash
cd frontend

# Format code
npm run format

# Lint
npm run lint
```

### Database Changes

**Create a new migration:**

```bash
# Create migration file
touch db/migrations/002_add_new_table.sql

# Edit migration with SQL
# Example: CREATE TABLE new_table (...)

# Run migration
psql $DATABASE_URL -f db/migrations/002_add_new_table.sql

# Verify
psql $DATABASE_URL -c "\dt"
```

## Common Development Tasks

### Test Analysis of a Call

**Using REST API:**

```bash
# Get a real Gong call ID from your account first
CALL_ID="1464927526043145564"

curl -X POST http://localhost:8001/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d "{\"gong_call_id\": \"$CALL_ID\"}"
```

**Using Python:**

```python
from coaching_mcp.tools.analyze_call import analyze_call_tool

result = analyze_call_tool(
    gong_call_id="1464927526043145564",
    focus_area="discovery"
)

print(result)
```

### Query Database

```bash
# Connect to database
psql $DATABASE_URL

# Common queries
SELECT * FROM calls LIMIT 5;
SELECT COUNT(*) FROM coaching_sessions;
SELECT * FROM calls WHERE gong_call_id = '123456';
```

### Debug MCP Tools

Add logging to understand what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your tool and see detailed logs
```

### Check Dependencies

```bash
# Python dependencies
uv tree

# Check for outdated packages
uv pip list --outdated

# Frontend dependencies
cd frontend
npm outdated
npm update
```

## Troubleshooting

### Backend Won't Start

**Error: `ModuleNotFoundError`**

```bash
# Install missing dependencies
uv pip install -e .

# Or reinstall everything
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Error: `Database connection failed`**

```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Common issue: missing sslmode=require
# Should be: postgresql://user:pass@host/db?sslmode=require
```

**Error: `401 Unauthorized` on Gong API**

```bash
# Verify credentials
echo $GONG_API_KEY
echo $GONG_API_SECRET

# Test Gong API manually
curl -H "Authorization: Bearer $GONG_API_SECRET" \
  "$GONG_API_BASE_URL/calls"

# Check tenant URL is correct (not generic api.gong.io)
```

### Frontend Won't Start

**Error: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not found`**

```bash
# Check .env.local exists in frontend/
ls frontend/.env.local

# Recreate if needed
cp frontend/.env.example frontend/.env.local
# Then edit with your Clerk keys
```

**Error: `Port 3000 already in use`**

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
npm run dev -- -p 3001
```

**Error: `API calls returning 404`**

```bash
# Check NEXT_PUBLIC_MCP_BACKEND_URL in .env.local
cat frontend/.env.local | grep MCP_BACKEND

# Verify backend is running
curl http://localhost:8001/health

# Check frontend is using correct URL
# Open DevTools → Network → Check request URLs
```

### Tests Failing

**Python tests fail:**

```bash
# Run with verbose output
pytest tests/ -vv

# Run specific test
pytest tests/test_chunking.py::test_chunk_transcript -vv

# Run without database (unit tests only)
pytest tests/test_analysis.py -v -m "not integration"
```

**Frontend tests fail:**

```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Run tests with verbose output
npm run test -- --verbose

# Update snapshots if intentional
npm run test -- -u
```

## Advanced Setup

### Using Local PostgreSQL

Instead of Neon cloud:

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15

# Start service
brew services start postgresql@15

# Create database
createdb callcoach

# Get connection string
DATABASE_URL=postgresql://localhost/callcoach

# Run migrations
psql $DATABASE_URL -f db/migrations/001_initial_schema.sql
```

### Using Docker Compose

Run everything in containers:

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### IDE Setup

**VS Code:**

```bash
# Install extensions
- Python
- Pylance
- FastAPI
- ESLint
- Prettier

# Create .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  }
}
```

**PyCharm:**

- Open project
- Go to Settings → Project → Python Interpreter
- Click gear icon → Add → Existing Environment
- Select `.venv/bin/python`

## Next Steps

1. **Make a small change** - Edit a Python file, see it reload
2. **Run tests** - `pytest tests/ -v`
3. **Create a PR** - Make a feature branch and test
4. **Read architecture** - See [System Architecture](./architecture.md)
5. **Check contributing guide** - How to submit changes

## Getting Help

- **Backend issues**: Check `coaching_mcp/server.py` logs
- **Frontend issues**: Check browser DevTools
- **Database issues**: Test with `psql $DATABASE_URL`
- **API issues**: Try `curl` directly against REST API
- **Documentation**: See [Troubleshooting Guide](../troubleshooting/README.md)

---

**Your local environment is ready!** Start developing at <http://localhost:3000>
