# FastMCP Cloud Deployment Checklist

## ✅ Pre-Deployment (Complete)

- [x] `fastmcp.toml` configured with correct server path
- [x] `.fastmcp/config.json` with tool metadata
- [x] `pyproject.toml` with pinned dependencies
- [x] Startup validation functions in `coaching_mcp/server.py`
- [x] Deployment script `.fastmcp/deploy.sh` tested
- [x] All 3 MCP tools implemented (analyze_call, get_rep_insights, search_calls)
- [x] Environment variables documented in `.env.example`
- [x] README with deployment documentation

## 🚀 Deployment Steps

### Option 1: GitHub Integration (Recommended)

1. **Push to GitHub** (if not already done):
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Navigate to Horizon**:
   - Go to: https://horizon.prefect.io/prefect-george/servers
   - Click "Create New MCP Server"

3. **Connect GitHub**:
   - Select repository: `call-coach`
   - Branch: `main`
   - Entrypoint: `coaching_mcp/server.py:mcp`

4. **Configure Server**:
   - **Name**: `gong-call-coach`
   - **Description**: "AI-powered sales coaching system analyzing Gong calls"
   - **Runtime**: Python 3.11
   - **Dependencies**: Auto-detected from `pyproject.toml`

5. **Set Environment Variables** (mark as secrets):

   Copy values from your local `.env` file:
   ```
   GONG_API_KEY=<your_gong_access_key>
   GONG_API_SECRET=<your_gong_secret_key_jwt>
   GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
   ANTHROPIC_API_KEY=<your_anthropic_api_key>
   DATABASE_URL=<your_neon_postgres_url>?sslmode=require
   ```

6. **Deploy**:
   - Click "Deploy Server"
   - Wait 60 seconds for deployment
   - Server will be available at: `https://gong-call-coach.fastmcp.app/mcp`

### Option 2: Direct Upload

1. **Create deployment package**:
   ```bash
   tar -czf gong-call-coach-deployment.tar.gz \
     coaching_mcp/ \
     db/ \
     gong/ \
     analysis/ \
     knowledge/ \
     flows/ \
     reports/ \
     config.py \
     fastmcp.toml \
     pyproject.toml \
     uv.lock
   ```

2. **Navigate to Horizon**:
   - Go to: https://horizon.prefect.io/prefect-george/servers
   - Click "Create New MCP Server"
   - Choose "Upload Files"

3. **Upload & Configure**:
   - Upload `gong-call-coach-deployment.tar.gz`
   - Set entrypoint: `coaching_mcp/server.py:mcp`
   - Configure environment variables (same as Option 1)

4. **Deploy**:
   - Click "Deploy Server"

## ✅ Post-Deployment Verification

### 1. Check Deployment Logs

Expected successful startup messages:
```
========================================================
Starting Gong Call Coaching MCP Server
========================================================

🔍 Running pre-flight validation checks...
✓ All required environment variables present
✓ Database connection successful
✓ Gong API authentication successful
✓ Anthropic API key validated

✅ All validation checks passed!
========================================================
🚀 MCP server ready - 3 tools registered
========================================================
```

### 2. Test via Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gong-call-coach": {
      "url": "https://gong-call-coach.fastmcp.app/mcp",
      "apiKey": "fmcp_F6rhqd9oFr1HOzNu6hOa5VBfwh2iXsKYWofXqPGTzqc"
    }
  }
}
```

Restart Claude Desktop and test:

**Test 1 - Analyze Call**:
```
Can you analyze Gong call 1464927526043145564?
```

Expected: Detailed coaching analysis with scores, strengths, improvement areas

**Test 2 - Get Rep Insights**:
```
Show me performance insights for sarah.jones@prefect.io over the last 30 days
```

Expected: Score trends, skill gaps, coaching plan

**Test 3 - Search Calls**:
```
Find discovery calls from last month with pricing objections scored above 70
```

Expected: List of matching calls with metadata

### 3. Monitor Performance

- **Cold start**: First invocation after idle (expect 10-15s)
- **Warm start**: Subsequent invocations (expect <2s)
- **Validation time**: Startup checks (expect 5-8s)

### 4. Check Dashboards

- **Horizon Logs**: Verify no errors, check validation messages
- **Neon Dashboard**: Monitor connection pool usage (target <50%)
- **Anthropic Usage**: Track token usage and costs (expect $10-15/day)

## 🔧 Troubleshooting

### 401 Authentication Error
- Verify `GONG_API_KEY` and `GONG_API_SECRET` are correct
- Confirm tenant-specific URL in `GONG_API_BASE_URL`
- Check credentials haven't expired

### Database Connection Timeout
- Verify `?sslmode=require` in `DATABASE_URL`
- Check Neon IP allowlist includes Horizon IPs
- Test locally: `psql $DATABASE_URL -c "SELECT 1"`

### Cold Start >30s
- Check Horizon logs for bottleneck
- Verify dependency sizes are reasonable
- Consider pre-warming strategy

### Tools Not Appearing
- Restart Claude Desktop completely
- Verify Horizon server status is "Ready"
- Check FastMCP API key is valid

## 📋 Success Criteria

- [ ] Server deployed and status shows "Ready"
- [ ] All validation checks pass in logs
- [ ] Three tools visible in Claude Desktop
- [ ] Test call analysis completes successfully
- [ ] Cold start <15s, warm start <2s
- [ ] No credential leaks in logs

## 🔄 Credential Rotation (Quarterly)

1. Generate new keys:
   - Gong: https://gong.app.gong.io/settings/api/authentication
   - Anthropic: https://console.anthropic.com/settings/keys

2. Update in Horizon:
   - Navigate to server settings
   - Edit environment variables
   - Save and redeploy

3. Verify with test calls

---

**Current Status**: Ready for deployment! All configuration complete.

**Next Action**: Choose deployment option and follow steps above.
