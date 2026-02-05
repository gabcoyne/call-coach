# Running Gong Call Coaching Locally

Complete guide to running both the MCP backend and Next.js frontend for local development.

## Prerequisites

- **Python 3.11+** with `uv` package manager
- **Node.js 20+** with `npm`
- **Neon PostgreSQL** database (cloud-hosted)
- **Gong API** credentials
- **Anthropic API** key
- **Clerk** account for authentication

## Quick Start (2 Terminals)

### Terminal 1: MCP Backend (Port 8000)

```bash
# Navigate to project root
cd /Users/gcoyne/src/prefect/call-coach

# Ensure .env file exists with required variables
cat .env  # Should show GONG_API_KEY, DATABASE_URL, ANTHROPIC_API_KEY, etc.

# Start MCP server using python-dotenv to load env vars
python3 -c "
from dotenv import load_dotenv
import subprocess
load_dotenv()
subprocess.run(['uv', 'run', 'python', 'coaching_mcp/server.py'])
"

# You should see:
# ✓ Database connection successful
# ✓ Gong API authentication successful
# ✓ Anthropic API key validated
# 🚀 MCP server ready - 3 tools registered
```

### Terminal 2: Next.js Frontend (Port 3000)

```bash
# Navigate to frontend directory
cd /Users/gcoyne/src/prefect/call-coach/frontend

# Ensure environment variables are set
cat .env.local  # Should show Clerk keys and MCP_BACKEND_URL

# Start development server
npm run dev

# You should see:
# ▲ Next.js 15.1.6
# - Local:    http://localhost:3000
# ✓ Ready in 1.5s
```

## Access the Application

1. **Open browser**: http://localhost:3000
2. **Sign in**: You'll be redirected to Clerk authentication
3. **Create test user**: Sign up with email or use test credentials
4. **Explore features**:
   - Dashboard: View rep performance metrics
   - Search: Filter and search calls
   - Feed: Activity feed with coaching insights
   - Call Viewer: Detailed call analysis

## Environment Variables

### Backend (.env in project root)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
GONG_API_KEY=UQ4SK2L...
GONG_API_SECRET=eyJhbGciOiJ...
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2

# Optional
GONG_WEBHOOK_SECRET=your_webhook_secret
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=20
LOG_LEVEL=INFO
```

### Frontend (frontend/.env.local)

```bash
# Required - Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Required - MCP Backend URL
NEXT_PUBLIC_MCP_BACKEND_URL=http://localhost:8000

# Optional - Clerk URLs (defaults)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

## Troubleshooting

### Backend Issues

**"Missing required environment variables"**
- Ensure `.env` file exists in project root
- Verify all required variables are set (see above)
- Try loading manually: `source .env` (won't work with special chars)
- Use the python-dotenv approach shown above

**"Database connection failed"**
- Check DATABASE_URL is correct and includes `?sslmode=require`
- Verify Neon database is running: `psql $DATABASE_URL -c "SELECT 1"`
- Check IP allowlist in Neon dashboard
- Confirm database schema is applied (see root README)

**"Gong API authentication failed"**
- Verify GONG_API_KEY and GONG_API_SECRET are correct
- Check GONG_API_BASE_URL uses your tenant-specific URL
- Test credentials: `python tests/test_gong_client_live.py`

**"statement_timeout parameter error"**
- This should be fixed in latest version (e4cf57c)
- If still seeing it, ensure you've pulled latest changes
- The fix moves statement_timeout from pool init to per-connection SET

### Frontend Issues

**"Cannot find module" or import errors**
- Run `npm install` in frontend directory
- Clear Next.js cache: `rm -rf .next`
- Restart dev server

**"Clerk authentication failed"**
- Verify Clerk API keys in `.env.local`
- Check Clerk dashboard: https://dashboard.clerk.com
- Ensure test keys (pk_test_/sk_test_) for development
- Create test users in Clerk dashboard if needed

**"API calls failing" (Network errors)**
- Ensure MCP backend is running on http://localhost:8000
- Check `NEXT_PUBLIC_MCP_BACKEND_URL` in `.env.local`
- Open browser DevTools → Network tab to inspect requests
- Verify CORS settings if seeing CORS errors

**Port already in use**
- Frontend: `lsof -ti:3000 | xargs kill -9`
- Backend: `lsof -ti:8000 | xargs kill -9`

## Development Workflow

### Making Backend Changes

1. Edit files in `coaching_mcp/`, `analysis/`, `gong/`, or `db/`
2. Server will auto-reload (if using uvicorn --reload)
3. Test changes: `pytest tests/`
4. Check logs in Terminal 1 for errors

### Making Frontend Changes

1. Edit files in `frontend/app/`, `frontend/components/`, or `frontend/lib/`
2. Next.js hot-reloads automatically
3. Test changes in browser (auto-refreshes)
4. Run tests: `cd frontend && npm test`

### Testing Full Flow

1. Ensure both servers are running
2. Open browser to http://localhost:3000
3. Sign in with Clerk test credentials
4. Navigate through Dashboard, Search, Feed
5. Check Network tab for API calls to http://localhost:8000
6. Verify data flows through correctly

## Stopping Servers

**Graceful shutdown**:
- Press `Ctrl+C` in each terminal

**Force kill**:
```bash
# Kill MCP backend
pkill -f "python coaching_mcp/server.py"

# Kill Next.js frontend
pkill -f "next dev"
```

## Next Steps

- Read [frontend/README.md](frontend/README.md) for frontend architecture
- See [README.md](README.md) for backend architecture and deployment
- Review [frontend/docs/](frontend/docs/) for comprehensive documentation
- Check [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for production deployment

## Getting Help

- Frontend issues: Check `frontend/docs/TROUBLESHOOTING.md`
- Backend issues: Check root `README.md` troubleshooting section
- Database issues: Review `db/migrations/` for schema
- API integration: See `frontend/docs/API_DOCUMENTATION.md`
