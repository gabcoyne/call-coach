# Vercel Deployment Guide

Deploy the Next.js frontend to Vercel and connect to backend services.

## Prerequisites

- Vercel account (create free at <https://vercel.com>)
- GitHub repository with code
- Backend API running (REST API on port 8001)
- Clerk account for authentication

## Step 1: Prepare Frontend for Deployment

**Update Environment Variables**:

```bash
# frontend/.env.production
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...  # Clerk production key
CLERK_SECRET_KEY=sk_live_...  # Clerk production secret
NEXT_PUBLIC_MCP_BACKEND_URL=https://your-api-domain.com  # Production backend URL
```

**Test Locally**:

```bash
# Build production bundle
npm run build

# Start production server
npm start

# Test at http://localhost:3000
```

---

## Step 2: Connect GitHub Repository

**Option A: Existing Vercel Account**

1. Go to <https://vercel.com/dashboard>
2. Click "Add New..." → "Project"
3. Select GitHub repository
4. Choose `call-coach` project
5. Vercel auto-detects Next.js configuration

**Option B: New Vercel Account**

1. Go to <https://vercel.com>
2. Click "Start Deploying"
3. Choose "Continue with GitHub"
4. Authorize Vercel to access your repositories
5. Select `call-coach` repository
6. Proceed with configuration

---

## Step 3: Configure Vercel Project

### Project Settings

1. After connecting repo, configure build settings:

```
Framework: Next.js 15
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

2. Configure environment variables:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk_live_...
CLERK_SECRET_KEY: sk_live_... (mark as secret ✓)
NEXT_PUBLIC_MCP_BACKEND_URL: https://your-api.com
```

3. Configure production domain:

```
Domain: call-coach.vercel.app (default)
Or custom: coach.your-company.com
```

### Deployment Options

**Auto-Deploy on Push**:

- Automatic: Every push to main → production
- Enable: Vercel → Project Settings → Git
- Check: "Deploy on push" is enabled

**Preview Deployments**:

- Automatic: Every PR gets preview URL
- Share preview URL with team
- Test before merging to main

---

## Step 4: Configure Clerk for Production

### Update Clerk URLs

1. Go to Clerk Dashboard: <https://dashboard.clerk.com>
2. Select your application
3. Go to Settings → URLs
4. Update URLs for production:

```
Sign In: https://call-coach.vercel.app/sign-in
Sign Up: https://call-coach.vercel.app/sign-up
After Sign In: https://call-coach.vercel.app/dashboard
After Sign Up: https://call-coach.vercel.app/dashboard
```

### Update Allowed Origins

1. Settings → CORS & Origins
2. Add your production domain:

```
https://call-coach.vercel.app
https://coach.your-company.com (if using custom domain)
```

### Configure Custom Domain (Optional)

1. Go to Clerk Dashboard → Settings → Domains
2. Add custom domain: `auth.your-company.com`
3. Add DNS records (Clerk provides instructions)
4. Update frontend environment to use custom domain

---

## Step 5: Set Up Backend API

The frontend needs a working REST API backend.

### Option A: Deploy Backend to Vercel (Recommended)

Backend can run as Vercel Serverless Function:

1. Create `api/handler.py` in project root:

```python
from api.rest_server import app
from vercel_python_wsgi import asgi_to_wsgi

asgi = asgi_to_wsgi(app)

def handler(request):
    return asgi(request)
```

2. Add to `vercel.json`:

```json
{
  "functions": {
    "api/handler.py": {
      "runtime": "python3.11"
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/handler.py"
    }
  ]
}
```

3. Set environment variables in Vercel:

```
ANTHROPIC_API_KEY: sk-ant-...
DATABASE_URL: postgresql://...?sslmode=require
GONG_API_KEY: ...
GONG_API_SECRET: ...
GONG_API_BASE_URL: https://us-XXXXX.api.gong.io/v2
```

4. Deploy: Push to GitHub, Vercel auto-deploys

5. Update frontend `.env.production`:

```
NEXT_PUBLIC_MCP_BACKEND_URL=https://call-coach.vercel.app/api
```

### Option B: Keep Backend Separate

Backend runs on different server (recommended for larger deployments):

1. Deploy backend to:

   - AWS EC2, Lambda, or similar
   - Google Cloud, Azure
   - Heroku, Railway, Render
   - Your own servers

2. Ensure backend is publicly accessible:

   ```
   https://api.your-company.com
   ```

3. Update frontend environment:

```
NEXT_PUBLIC_MCP_BACKEND_URL=https://api.your-company.com
```

4. Configure CORS in backend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://call-coach.vercel.app",
        "https://coach.your-company.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 6: Deploy

### First Deployment

1. Push code to GitHub main branch
2. Vercel automatically starts build
3. Monitor build progress at <https://vercel.com/dashboard>
4. Build takes 2-5 minutes
5. Once done, app is live at `call-coach.vercel.app`

### Subsequent Deployments

**Automatic** (recommended):

- Just push to main
- Vercel builds and deploys automatically
- Takes ~2-5 minutes

**Manual**:

1. Go to Vercel Dashboard
2. Select project
3. Click "Deploy" button
4. Choose branch to deploy

---

## Step 7: Verify Deployment

### Test Frontend

```bash
# Open app
https://call-coach.vercel.app

# Test login
1. Click "Sign In"
2. Create account or sign in
3. Should redirect to dashboard
4. Should show "Loading..." then dashboard
```

### Test Backend Connection

```bash
# In browser console (F12)
fetch('https://call-coach.vercel.app/api/health')
  .then(r => r.json())
  .then(d => console.log(d))

# Expected:
# {status: "healthy"}

# Or if separate backend:
fetch('https://api.your-company.com/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

### Test API Calls

1. Open dashboard
2. Go to Search page
3. Try searching for calls
4. Should get results from backend

If fails, check:

- Backend URL in environment variables
- Backend is running
- CORS is configured
- Network in DevTools shows requests to correct URL

---

## Monitoring & Maintenance

### View Logs

**Vercel Frontend Logs**:

1. Go to <https://vercel.com/dashboard>
2. Select project
3. Go to "Deployments"
4. Click deployment
5. Scroll to "Logs"
6. View build and runtime logs

**Backend Logs**:
Depends on backend hosting platform.

### Performance Monitoring

**Vercel Analytics**:

1. Go to project → "Analytics"
2. View:
   - Page load times
   - Visitor counts
   - Error rates
   - Top pages

**Monitor Key Metrics**:

- Page load time: Target <3 seconds
- Time to interactive: Target <5 seconds
- Error rate: Target <0.1%
- Uptime: Target 99.9%

### Update Dependencies

```bash
# Check for updates
npm outdated

# Update packages
npm update

# Or upgrade major versions
npm install react@latest next@latest

# Test locally
npm run dev
npm run build

# Commit and push
git add package.json package-lock.json
git commit -m "chore: update dependencies"
git push origin main

# Vercel auto-deploys
```

---

## Troubleshooting

### "Build Failed"

**Check logs in Vercel**:

1. Go to Deployments → Failed deployment
2. Scroll to "Build Log"
3. Look for error message

**Common causes**:

- Missing environment variable
- TypeScript error
- Import error
- Dependency not installed

**Solution**:

```bash
# Test locally
npm run build

# Fix any errors
# Commit
git add .
git commit -m "fix: build errors"
git push

# Vercel auto-rebuilds
```

---

### "App Shows 404"

**Causes**:

- Build failed (check logs)
- Wrong framework detected
- Next.js output directory missing

**Solution**:

```bash
# Verify vercel.json doesn't have conflicting config
cat vercel.json

# Should not override next.js defaults

# Rebuild
git push origin main

# Or manually redeploy in Vercel dashboard
```

---

### "API Calls Failing (404)"

**Check CORS and backend URL**:

```bash
# In browser console
fetch('https://api.your-backend.com/health')
  .then(r => r.json())
  .then(d => console.log(d))

# Check environment variable in Vercel
# Go to Settings → Environment Variables
# Verify NEXT_PUBLIC_MCP_BACKEND_URL is correct
```

**Solutions**:

1. Update environment variable in Vercel
2. Redeploy: Go to Deployments → Redeploy
3. Clear browser cache: Ctrl+Shift+Delete
4. Test in incognito window

---

### "Clerk Authentication Not Working"

**Check Clerk configuration**:

1. Go to Clerk Dashboard
2. Settings → URLs
3. Verify sign-in/sign-up URLs match your domain
4. Verify allowed origins include your domain
5. Check API keys are correct

**In Vercel**:

1. Go to Settings → Environment Variables
2. Verify Clerk keys:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (public)
   - `CLERK_SECRET_KEY` (secret)
3. Keys should be "Live" keys, not "Development"
4. Redeploy

**Redeploy after Clerk changes**:

```bash
# In Vercel: Deployments → Redeploy
# Or push new commit
git add .
git commit -m "chore: clerk config update"
git push
```

---

### "Slow Page Loads"

**Optimize performance**:

1. **Enable Next.js Image Optimization**:

   ```
   Settings → Image Optimization: Enabled
   ```

2. **Use Vercel Analytics**:

   ```
   Project → Analytics
   Check which pages are slow
   ```

3. **Optimize Clerk**:

   - Reduce calls to Clerk API
   - Cache authentication state
   - Use SWR for data fetching

4. **Database Optimization**:
   - Add database indexes
   - Optimize queries
   - Check connection pool

---

## Production Checklist

Before going live, verify:

- [ ] Frontend deployed to Vercel
- [ ] Custom domain configured (optional but recommended)
- [ ] Clerk configured for production
- [ ] Backend API deployed and accessible
- [ ] Environment variables set in Vercel
- [ ] Tested login flow
- [ ] Tested call analysis
- [ ] Tested search functionality
- [ ] Verified CORS headers
- [ ] Set up monitoring/alerts
- [ ] Documented access credentials
- [ ] Team trained on access

---

## Monitoring & Support

### Health Checks

**Weekly**:

```bash
# Monitor API
curl https://call-coach.vercel.app/api/health

# Monitor Gong integration
curl https://call-coach.vercel.app/api/gong-status

# Check logs in Vercel dashboard
```

**Monthly**:

- Review analytics
- Check error rates
- Update dependencies
- Audit access logs

### Get Help

- **Vercel Docs**: <https://vercel.com/docs>
- **Next.js Docs**: <https://nextjs.org>
- **Clerk Docs**: <https://clerk.com/docs>

---

**Deployment complete!** Your app is now live at <https://call-coach.vercel.app>
