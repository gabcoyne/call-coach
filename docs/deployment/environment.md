# Environment Variables Reference

Complete reference for all environment variables used by Call Coach.

## Overview

Environment variables configure the application for different environments (local, staging, production). All sensitive values should be stored securely, never committed to git.

## Required Variables

These must be set for the application to start.

### ANTHROPIC_API_KEY

**Description**: Claude API authentication key

**Format**: `sk-ant-v7-...` (usually 50+ characters)

**Where to Get**:

1. Go to <https://console.anthropic.com/settings/keys>
2. Click "Create new key"
3. Copy the full key

**Example**:

```
ANTHROPIC_API_KEY=sk-ant-api03-v7-...
```

**Used By**: Analysis engine for coaching generation

---

### DATABASE_URL

**Description**: PostgreSQL connection string for Neon cloud database

**Format**: `postgresql://[user]:[password]@[host]/[database]?sslmode=require`

**Components**:

- `user`: Database username
- `password`: Database password
- `host`: Database hostname (Neon)
- `database`: Database name
- `sslmode=require`: Required for Neon

**Where to Get**:

1. Go to <https://console.neon.tech>
2. Select your project
3. Click "Connection" button
4. Choose "Connection string"
5. Copy the full string (must include `?sslmode=require`)

**Example**:

```
DATABASE_URL=postgresql://neondb_owner:abc123@ep-cool-cloud-a1b2c3d4.us-east-2.aws.neon.tech/callcoach?sslmode=require
```

**Important**: Must include `?sslmode=require` suffix for security.

**Used By**: All database operations

---

### GONG_API_KEY

**Description**: Gong API access key for authentication

**Format**: alphanumeric (12-20 characters)

**Where to Get**:

1. Log in to Gong: <https://gong.app.gong.io>
2. Go to Settings → Integrations → API
3. Copy "Access Key ID"

**Example**:

```
GONG_API_KEY=UQ4SK2LPUPBCFN7Q
```

**Used By**: Gong API calls (fetching calls, transcripts)

---

### GONG_API_SECRET

**Description**: Gong API secret key for JWT signing

**Format**: JWT-like string (starts with `eyJ...`)

**Where to Get**:

1. Same location as GONG_API_KEY
2. Copy "Access Key Secret"

**Example**:

```
GONG_API_SECRET=eyJhbGciOiJIUzI1NiJ9...
```

**Important**: Keep secret, never expose in logs or public URLs

**Used By**: Gong API authentication

---

### GONG_API_BASE_URL

**Description**: Gong API base URL (tenant-specific)

**Format**: `https://us-[number].api.gong.io/v2`

**Important**: Must use your tenant-specific URL, not generic `api.gong.io`

**Where to Get**:

1. Log in to Gong
2. Look at URL: `https://us-[NUMBER].gong.io`
3. Use that number in API URL

**Example**:

```
GONG_API_BASE_URL=https://us-79647.api.gong.io/v2
```

**Used By**: All Gong API requests

---

## Optional Variables

These configure specific features or override defaults.

### GONG_WEBHOOK_SECRET

**Description**: Secret for verifying incoming Gong webhooks

**Format**: Any string you choose (recommended: 32+ random characters)

**Usage**:

1. Set in .env
2. Copy same value to Gong dashboard → Webhooks
3. Used to verify HMAC signatures

**Example**:

```
GONG_WEBHOOK_SECRET=your_super_secret_webhook_key_12345678
```

**Default**: Optional (webhooks work without it, but less secure)

**Used By**: Webhook signature verification

---

### LOG_LEVEL

**Description**: Logging verbosity level

**Valid Values**:

- `DEBUG` - Very verbose, shows all details
- `INFO` - Normal level, shows important info
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors
- `CRITICAL` - Only critical errors

**Example**:

```
LOG_LEVEL=INFO
```

**Default**: `INFO`

**Used By**: All logging throughout application

---

### CACHE_TTL_SECONDS

**Description**: How long to cache analysis results (seconds)

**Valid Range**: 3600 (1 hour) to 2592000 (30 days)

**Example**:

```
CACHE_TTL_SECONDS=2592000  # 30 days
```

**Default**: 2592000 (30 days)

**Used By**: Cache expiration logic

---

### PREFECT_API_URL

**Description**: Prefect Cloud API URL for flow orchestration

**Format**: `https://api.prefect.cloud/api/accounts/...`

**Only Used For**: Cloud Prefect deployments

**Example**:

```
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/abc123/workspaces/xyz789
```

**Default**: Not set (uses local Prefect server)

---

### PREFECT_API_KEY

**Description**: Prefect Cloud API authentication key

**Format**: Long alphanumeric string

**Only Used For**: Cloud Prefect deployments

**Example**:

```
PREFECT_API_KEY=pnu_abc123xyz789...
```

**Default**: Not set

---

## By Environment

### Local Development

Minimal setup in `.env`:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...?sslmode=require
GONG_API_KEY=...
GONG_API_SECRET=...
GONG_API_BASE_URL=https://us-XXXXX.api.gong.io/v2

# Optional but recommended
LOG_LEVEL=DEBUG
GONG_WEBHOOK_SECRET=dev_webhook_secret
```

### Staging/Testing

Add monitoring and security:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...?sslmode=require
GONG_API_KEY=...
GONG_API_SECRET=...
GONG_API_BASE_URL=https://us-XXXXX.api.gong.io/v2

# Security
GONG_WEBHOOK_SECRET=staging_webhook_secret_strong_value

# Monitoring
LOG_LEVEL=INFO

# Prefect (if using Horizon)
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/...
PREFECT_API_KEY=pnu_...
```

### Production

Full security and monitoring:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...  # Production key
DATABASE_URL=postgresql://...?sslmode=require  # Production DB
GONG_API_KEY=...  # Production credentials
GONG_API_SECRET=...
GONG_API_BASE_URL=https://us-XXXXX.api.gong.io/v2

# Security
GONG_WEBHOOK_SECRET=<strong_random_value>

# Monitoring
LOG_LEVEL=WARNING  # Less verbose in production

# Prefect
PREFECT_API_URL=https://api.prefect.cloud/...
PREFECT_API_KEY=pnu_...

# Cache
CACHE_TTL_SECONDS=2592000  # 30 days
```

## Setting Environment Variables

### Local Development (`.env` file)

```bash
# 1. Create .env in project root
cp .env.example .env

# 2. Edit .env with your values
nano .env

# 3. Source environment when needed
source .venv/bin/activate

# (activated shell will load .env automatically)

# 4. Verify
echo $ANTHROPIC_API_KEY  # Should print your key
```

### Vercel Deployment

```bash
# 1. Go to Vercel dashboard
# https://vercel.com/dashboard

# 2. Select project → Settings → Environment Variables

# 3. Add each variable:
# - Name: ANTHROPIC_API_KEY
# - Value: sk-ant-...
# - Environments: Production, Preview, Development

# 4. Add for all required variables

# 5. Redeploy for changes to take effect
# Vercel → Deployments → Redeploy
```

### Prefect Horizon

```bash
# 1. Go to Prefect Horizon dashboard
# https://horizon.prefect.io

# 2. Select workspace → MCP Servers

# 3. Create new server or edit existing

# 4. Go to Environment Variables section

# 5. Add each variable:
# Name: ANTHROPIC_API_KEY
# Value: sk-ant-...
# Is secret: ✓ (check this for sensitive values)

# 6. Save and deploy
```

### Docker / Docker Compose

```bash
# 1. Create .env file in project root
cp .env.example .env

# 2. Edit with values
nano .env

# 3. Docker Compose will load automatically
docker-compose up

# Or pass individual variables
docker run -e ANTHROPIC_API_KEY=sk-ant-... image_name
```

## Validating Configuration

### Quick Validation Script

```bash
#!/bin/bash
# validate_env.sh

echo "Checking environment variables..."

check_var() {
  if [ -z "${!1}" ]; then
    echo "✗ Missing: $1"
    return 1
  else
    echo "✓ Found: $1"
    return 0
  fi
}

all_good=true

check_var ANTHROPIC_API_KEY || all_good=false
check_var DATABASE_URL || all_good=false
check_var GONG_API_KEY || all_good=false
check_var GONG_API_SECRET || all_good=false
check_var GONG_API_BASE_URL || all_good=false

if [ "$all_good" = true ]; then
  echo ""
  echo "✓ All required variables present!"
else
  echo ""
  echo "✗ Some variables missing!"
  exit 1
fi
```

Run with:

```bash
bash validate_env.sh
```

### Server Startup Validation

The server validates all variables on startup:

```bash
uv run mcp-server-dev

# Output should show:
# ✓ All required environment variables present
# ✓ Database connection successful
# ✓ Gong API authentication successful
# ✓ Anthropic API key validated
# 🚀 MCP server ready - 3 tools registered
```

If any validation fails, check:

1. Variable name is spelled correctly
2. Variable value is valid
3. Variable is in correct environment scope

## Secrets Management

### Best Practices

1. **Never commit `.env` to git**

   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use `.env.example`** for template

   ```bash
   # Show which variables are needed
   cat .env.example
   ```

3. **Rotate credentials regularly** (quarterly recommended)

4. **Use different keys for different environments**

   - Dev: Personal API keys
   - Staging: Separate test keys
   - Production: Dedicated prod keys

5. **Log rotation: Never log secrets**

   ```python
   # Bad:
   logger.info(f"Connecting with key: {api_key}")

   # Good:
   logger.info("Connecting to API")
   ```

### Rotating Credentials

**When to Rotate**:

- Quarterly or on schedule
- If key is compromised
- After team member leaves
- Before major security update

**How to Rotate**:

1. **Generate new credentials** in source service:

   - Anthropic: <https://console.anthropic.com/settings/keys>
   - Gong: <https://gong.app.gong.io/settings/api/authentication>

2. **Update all copies** of credential:

   - Development: Update `.env`
   - Staging: Update in deployment system
   - Production: Update in Vercel/Horizon

3. **Deploy with new key**: Restart application

4. **Verify new key works**: Test API calls

5. **Revoke old key** in source service:

   - After confirming new key works
   - Prevents accidental use of old key

6. **Document rotation**: Update security log

## Troubleshooting

### "Environment variable not found"

**Causes**:

- Typo in variable name
- Variable not in active environment
- Shell not sourced `.env`

**Solutions**:

```bash
# 1. Check spelling
echo $ANTHROPIC_API_KEY  # Match exactly, case-sensitive

# 2. Check .env exists
ls -la .env

# 3. Reload environment
source .venv/bin/activate

# 4. Check it's there
echo $ANTHROPIC_API_KEY
```

---

### "Variable is empty"

**Causes**:

- Variable set but value is empty
- Variable set to wrong file

**Solutions**:

```bash
# 1. Check .env file content
grep ANTHROPIC_API_KEY .env

# Should show: ANTHROPIC_API_KEY=sk-ant-...
# NOT: ANTHROPIC_API_KEY=

# 2. Check for quoted empty string
# Wrong:
ANTHROPIC_API_KEY=""

# Right:
ANTHROPIC_API_KEY=sk-ant-...

# 3. Fix and reload
source .venv/bin/activate
```

---

### "SSL certificate error"

**Cause**: DATABASE_URL missing `?sslmode=require`

**Solution**:

```bash
# 1. Check DATABASE_URL
echo $DATABASE_URL

# Should end with: ?sslmode=require

# 2. Edit .env
nano .env

# 3. Add ?sslmode=require if missing
DATABASE_URL=postgresql://...?sslmode=require

# 4. Reload and test
source .venv/bin/activate
psql $DATABASE_URL -c "SELECT 1"
```

---

## See Also

- [Local Development Setup](../developers/setup.md) - How to set up locally
- [Deployment Guide](./vercel.md) - How to deploy
- [Troubleshooting](../troubleshooting/README.md) - Common issues
