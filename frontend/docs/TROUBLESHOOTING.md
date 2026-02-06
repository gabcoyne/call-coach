# Troubleshooting Guide

Common issues and solutions for the Gong Call Coaching frontend application.

## Table of Contents

- [Authentication Issues](#authentication-issues)
- [API Errors](#api-errors)
- [Build and Development Issues](#build-and-development-issues)
- [UI and Display Issues](#ui-and-display-issues)
- [Performance Issues](#performance-issues)
- [Data Issues](#data-issues)
- [Deployment Issues](#deployment-issues)

## Authentication Issues

### Cannot Sign In

**Symptom**: Sign-in page loads but authentication fails

**Possible Causes**:

1. Incorrect Clerk configuration
2. Missing or invalid Clerk API keys
3. Network issues connecting to Clerk
4. User account not created

**Solutions**:

1. **Verify Clerk API Keys**:

   ```bash
   # Check .env.local (development)
   cat .env.local | grep CLERK

   # Should see:
   # NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
   # CLERK_SECRET_KEY=sk_test_xxxxx
   ```

2. **Check Clerk Dashboard**:

   - Go to [Clerk Dashboard](https://dashboard.clerk.com)
   - Verify API keys match your environment
   - Check that application is active

3. **Clear Browser Cache**:

   - Clear cookies and local storage
   - Try incognito/private mode
   - Try different browser

4. **Check Network Tab**:

   - Open browser DevTools → Network tab
   - Look for failed requests to `clerk.com`
   - Check for CORS errors

5. **Create Test User**:
   - Go to Clerk Dashboard → Users
   - Create test user manually
   - Try signing in with test credentials

### "Unauthorized" After Sign-In

**Symptom**: Successfully sign in but immediately get "Unauthorized" error

**Possible Causes**:

1. User role not set in Clerk
2. Middleware not recognizing session
3. Cookie issues

**Solutions**:

1. **Verify User Role**:

   - Clerk Dashboard → Users → Select user
   - Check `publicMetadata.role` field
   - Should be either `"manager"` or `"rep"`
   - Set if missing:

   ```json
   {
     "role": "rep"
   }
   ```

2. **Check Middleware Configuration**:

   - Verify `middleware.ts` exists in project root
   - Check routes are properly protected
   - Review middleware logs in terminal

3. **Clear Clerk Session**:

   ```javascript
   // In browser console
   localStorage.clear();
   sessionStorage.clear();
   // Then refresh page
   ```

### "Forbidden" When Accessing Data

**Symptom**: Can sign in but get "Forbidden" when trying to view certain pages

**Possible Causes**:

1. RBAC restrictions (rep trying to access manager data)
2. Attempting to view another rep's data
3. Role misconfigured

**Solutions**:

1. **Check Your Role**:

   - Go to Profile page
   - Verify role is correct
   - Contact admin if wrong

2. **Verify Access Permissions**:

   - **Reps**: Can only view own data
   - **Managers**: Can view all data
   - Check URL to ensure you're accessing appropriate data

3. **Test with Manager Account**:
   - Sign in as manager
   - Try accessing the same resource
   - If works, it's an RBAC issue

### Session Expired Errors

**Symptom**: Randomly logged out or "Session expired" messages

**Possible Causes**:

1. Clerk session timeout
2. Token expiration
3. Clock skew

**Solutions**:

1. **Sign Out and Back In**:

   - Click user menu → Sign Out
   - Sign in again
   - Session should refresh

2. **Check System Clock**:

   - Ensure computer clock is accurate
   - Enable automatic time sync

3. **Adjust Clerk Session Settings** (admin):
   - Clerk Dashboard → Sessions
   - Increase session timeout if needed
   - Default: 7 days inactive, 30 days absolute

## API Errors

### "Rate Limit Exceeded" (HTTP 429)

**Symptom**: API requests failing with "Rate limit exceeded"

**Possible Causes**:

1. Too many requests in short time
2. Script or automation hitting API
3. Multiple browser tabs open

**Solutions**:

1. **Wait for Rate Limit Reset**:

   - Check `X-RateLimit-Reset` header
   - Wait until reset time (Unix timestamp)

2. **Reduce Request Frequency**:

   - Close duplicate tabs
   - Stop any scripts hitting API
   - Wait 1 hour and try again

3. **Check Rate Limit Status**:

   ```bash
   # Make API request and check headers
   curl -I http://localhost:3000/api/coaching/analyze-call \
     -H "Cookie: __session=YOUR_SESSION"

   # Look for:
   # X-RateLimit-Limit: 60
   # X-RateLimit-Remaining: 0
   # X-RateLimit-Reset: 1707180000
   ```

### "Internal Server Error" (HTTP 500)

**Symptom**: API requests failing with generic server error

**Possible Causes**:

1. MCP backend unreachable
2. MCP backend error
3. Bug in API route code
4. Invalid data from backend

**Solutions**:

1. **Check API Logs**:

   ```bash
   # Development: Check terminal running `npm run dev`
   # Look for error stack traces

   # Production: Check Vercel function logs
   # Vercel Dashboard → Deployments → Click deployment → Functions
   ```

2. **Verify MCP Backend**:

   ```bash
   # Check if backend is running
   curl http://localhost:8000/health

   # Or production
   curl https://coaching-api.prefect.io/health
   ```

3. **Check Environment Variables**:

   ```bash
   # Verify MCP backend URL is set
   echo $NEXT_PUBLIC_MCP_BACKEND_URL

   # Should output backend URL, not undefined
   ```

4. **Test API Route Directly**:

   ```bash
   # Use curl to isolate issue
   curl -X POST http://localhost:3000/api/coaching/analyze-call \
     -H "Content-Type: application/json" \
     -H "Cookie: __session=YOUR_SESSION" \
     -d '{"call_id": "8123456789012345678"}'
   ```

### "Invalid Request Parameters" (HTTP 400)

**Symptom**: API rejecting request with validation errors

**Possible Causes**:

1. Missing required fields
2. Invalid data format
3. Type mismatch

**Solutions**:

1. **Check Validation Error Details**:

   - Look at response body for specific field errors

   ```json
   {
     "error": "Invalid request parameters",
     "details": {
       "call_id": ["Required"],
       "rep_email": ["Invalid email"]
     }
   }
   ```

2. **Verify Request Format**:

   - Ensure required fields are present
   - Check data types match schema
   - See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

3. **Test with Minimal Request**:

   ```bash
   # Start with minimal valid request
   curl -X POST http://localhost:3000/api/coaching/analyze-call \
     -H "Content-Type: application/json" \
     -d '{"call_id": "8123456789012345678"}'
   ```

### Network Errors

**Symptom**: Requests timing out or failing to connect

**Possible Causes**:

1. MCP backend down
2. Network connectivity issues
3. CORS problems
4. Firewall blocking requests

**Solutions**:

1. **Check Network Connectivity**:

   ```bash
   # Ping backend server
   ping coaching-api.prefect.io

   # Check DNS resolution
   nslookup coaching-api.prefect.io
   ```

2. **Verify Backend Health**:

   ```bash
   # Check if backend is responding
   curl -v http://localhost:8000/
   ```

3. **Check Browser Console**:

   - Open DevTools → Console
   - Look for CORS errors
   - Check Network tab for failed requests

4. **Verify CORS Configuration** (backend issue):
   - Backend must allow frontend origin
   - Check backend CORS settings

## Build and Development Issues

### "Module Not Found" Errors

**Symptom**: Build or dev server fails with module import errors

**Possible Causes**:

1. Missing dependencies
2. Incorrect import paths
3. TypeScript path alias issues

**Solutions**:

1. **Reinstall Dependencies**:

   ```bash
   # Delete node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Import Paths**:

   ```typescript
   // Correct: Use @ alias for project root
   import { Button } from "@/components/ui/button";

   // Incorrect: Relative paths from src
   import { Button } from "../../../components/ui/button";
   ```

3. **Verify tsconfig.json**:

   ```json
   {
     "compilerOptions": {
       "baseUrl": ".",
       "paths": {
         "@/*": ["./*"]
       }
     }
   }
   ```

4. **Clear Next.js Cache**:

   ```bash
   # Delete .next directory
   rm -rf .next

   # Restart dev server
   npm run dev
   ```

### TypeScript Errors

**Symptom**: Type errors preventing compilation

**Possible Causes**:

1. Missing type definitions
2. Type mismatches
3. Strict mode violations

**Solutions**:

1. **Install Type Definitions**:

   ```bash
   # Install missing @types packages
   npm install --save-dev @types/node @types/react @types/react-dom
   ```

2. **Check Type Errors**:

   ```bash
   # Run type checker without building
   npx tsc --noEmit

   # Shows all type errors
   ```

3. **Fix Common Issues**:

   ```typescript
   // Issue: Implicit 'any' type
   // Solution: Add explicit type
   const data: CallAnalysisData = await fetchData();

   // Issue: Possibly undefined
   // Solution: Add optional chaining
   const score = data?.scores?.overall ?? 0;

   // Issue: Type mismatch
   // Solution: Type assertion (use carefully)
   const email = user.email as string;
   ```

### Environment Variables Not Loading

**Symptom**: `process.env.VARIABLE_NAME` is undefined

**Possible Causes**:

1. Missing `.env.local` file
2. Incorrect variable name
3. Dev server not restarted
4. Variables not prefixed with `NEXT_PUBLIC_`

**Solutions**:

1. **Create .env.local**:

   ```bash
   # Copy example file
   cp .env.example .env.local

   # Edit and add your values
   nano .env.local
   ```

2. **Check Variable Names**:

   - Client-side variables MUST start with `NEXT_PUBLIC_`
   - Server-side variables don't need prefix

3. **Restart Dev Server**:

   ```bash
   # Stop dev server (Ctrl+C)
   # Start again
   npm run dev
   ```

4. **Verify Variables Are Set**:

   ```typescript
   // In a server component or API route
   console.log("Backend URL:", process.env.NEXT_PUBLIC_MCP_BACKEND_URL);
   console.log("Clerk Secret:", !!process.env.CLERK_SECRET_KEY); // Don't log actual secret
   ```

### Port Already in Use

**Symptom**: Dev server fails to start with "Port 3000 already in use"

**Solutions**:

1. **Kill Process on Port**:

   ```bash
   # macOS/Linux
   lsof -ti:3000 | xargs kill -9

   # Or use different port
   PORT=3001 npm run dev
   ```

2. **Find and Kill Process**:

   ```bash
   # Find process using port 3000
   lsof -i :3000

   # Kill by PID
   kill -9 <PID>
   ```

## UI and Display Issues

### Styling Not Applied

**Symptom**: Components have no styling or incorrect styling

**Possible Causes**:

1. Tailwind not compiling
2. CSS not imported
3. Class name errors

**Solutions**:

1. **Verify Tailwind Setup**:

   ```bash
   # Check tailwind.config.ts exists
   ls tailwind.config.ts

   # Check postcss.config.js exists
   ls postcss.config.js
   ```

2. **Check Global CSS Import**:

   ```typescript
   // app/layout.tsx should import
   import "@/app/globals.css";
   ```

3. **Clear Build Cache**:

   ```bash
   rm -rf .next
   npm run dev
   ```

4. **Test Tailwind Classes**:

   ```tsx
   // Try simple test component
   <div className="bg-red-500 p-4 text-white">Test - should have red background</div>
   ```

### Components Not Rendering

**Symptom**: Blank page or components not appearing

**Possible Causes**:

1. JavaScript errors preventing render
2. Server component errors
3. Missing data

**Solutions**:

1. **Check Browser Console**:

   - Open DevTools → Console
   - Look for error messages
   - Fix JavaScript errors

2. **Check Server Logs**:

   - Terminal running `npm run dev`
   - Look for server component errors
   - Fix server-side errors

3. **Add Error Boundaries**:

   ```tsx
   // Wrap components in error boundary
   <ErrorBoundary fallback={<div>Error loading</div>}>
     <YourComponent />
   </ErrorBoundary>
   ```

4. **Test with Simple Component**:

   ```tsx
   // Replace complex component with simple one
   export default function TestPage() {
     return <div>Test page rendering</div>;
   }
   ```

### Charts Not Displaying

**Symptom**: Recharts components not rendering

**Possible Causes**:

1. Missing data
2. Invalid data format
3. Recharts import errors

**Solutions**:

1. **Check Data Format**:

   ```typescript
   // Ensure data matches expected format
   console.log("Chart data:", data);

   // Recharts expects array of objects
   const validData = [
     { date: "2024-01-01", score: 75 },
     { date: "2024-01-02", score: 80 },
   ];
   ```

2. **Verify Imports**:

   ```typescript
   // Correct imports
   import {
     LineChart,
     Line,
     XAxis,
     YAxis,
     CartesianGrid,
     Tooltip,
     ResponsiveContainer,
   } from "recharts";
   ```

3. **Add Fallback**:

   ```tsx
   {
     data?.length > 0 ? (
       <ResponsiveContainer width="100%" height={300}>
         <LineChart data={data}>{/* chart components */}</LineChart>
       </ResponsiveContainer>
     ) : (
       <div>No data available</div>
     );
   }
   ```

## Performance Issues

### Slow Page Loads

**Symptom**: Pages take long time to load

**Possible Causes**:

1. Large JavaScript bundles
2. Unoptimized images
3. Slow API requests
4. Too many client components

**Solutions**:

1. **Check Bundle Size**:

   ```bash
   # Analyze bundle
   npm run build

   # Look for large chunks in output
   ```

2. **Optimize Images**:

   ```tsx
   // Use Next.js Image component
   import Image from "next/image";

   <Image
     src="/logo.png"
     alt="Logo"
     width={200}
     height={100}
     priority // For above-fold images
   />;
   ```

3. **Use Server Components**:

   ```tsx
   // Default: Server component (faster)
   export default async function Page() {
     const data = await fetchData();
     return <div>{data}</div>;
   }

   // Only use 'use client' when needed
   ```

4. **Enable Caching**:

   ```typescript
   // Use SWR for client-side caching
   const { data } = useSWR("/api/data", fetcher, {
     revalidateOnFocus: false,
     dedupingInterval: 60000, // Cache for 1 minute
   });
   ```

### High Memory Usage

**Symptom**: Browser or dev server using excessive memory

**Solutions**:

1. **Restart Dev Server**:

   ```bash
   # Stop and restart
   npm run dev
   ```

2. **Clear Browser Cache**:

   - DevTools → Application → Clear storage
   - Restart browser

3. **Check for Memory Leaks**:
   - Use React DevTools Profiler
   - Look for unnecessary re-renders
   - Fix useEffect dependencies

## Data Issues

### Data Not Updating

**Symptom**: UI shows stale data, doesn't reflect changes

**Possible Causes**:

1. SWR cache not invalidating
2. Backend data not updating
3. Browser cache

**Solutions**:

1. **Force Revalidation**:

   ```typescript
   // In your component
   const { data, mutate } = useSWR("/api/data");

   // Force refresh
   mutate();
   ```

2. **Check SWR Config**:

   ```typescript
   // Reduce cache time if data changes frequently
   const { data } = useSWR("/api/data", fetcher, {
     refreshInterval: 30000, // Refresh every 30s
     revalidateOnFocus: true,
   });
   ```

3. **Clear Browser Cache**:
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear all browser data

### Missing or Incorrect Data

**Symptom**: Data is empty, null, or wrong

**Possible Causes**:

1. API returning unexpected format
2. Data transformation errors
3. Backend data issues

**Solutions**:

1. **Check API Response**:

   ```bash
   # Test API directly
   curl http://localhost:3000/api/coaching/analyze-call \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"call_id": "8123456789012345678"}'

   # Verify response format
   ```

2. **Add Data Validation**:

   ```typescript
   // Validate data before using
   if (!data || typeof data !== 'object') {
     console.error('Invalid data format:', data);
     return <div>Error loading data</div>;
   }
   ```

3. **Check Backend Logs**:
   - MCP backend logs
   - Database query results
   - Verify data exists in source system (Gong)

## Deployment Issues

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment troubleshooting.

### Quick Deployment Fixes

**Build Fails in Vercel**:

1. Check build logs in Vercel dashboard
2. Verify environment variables are set
3. Test build locally: `npm run build`
4. Fix errors and redeploy

**Site Not Updating After Deploy**:

1. Clear CDN cache (automatic in Vercel)
2. Hard refresh browser: Ctrl+Shift+R
3. Check deployment status in Vercel
4. Verify correct branch was deployed

**Environment Variables Not Working**:

1. Verify variables in Vercel dashboard
2. Check correct environment (Production vs Preview)
3. Redeploy to apply changes

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Search error message in project documentation
3. Check browser console and network tab
4. Check server logs (terminal or Vercel)
5. Try basic debugging steps (restart, clear cache, etc.)

### Information to Provide

When reporting issues, include:

- **Environment**: Development, preview, or production
- **Browser**: Name and version
- **Error Message**: Exact error text
- **Steps to Reproduce**: How to trigger the issue
- **Screenshots**: If relevant
- **Console Logs**: Browser console and server logs
- **Network Logs**: Failed requests from Network tab

### Contact

- **Technical Issues**: Contact DevOps team
- **User Questions**: See [USER_GUIDE.md](./USER_GUIDE.md)
- **Incidents**: Follow [RUNBOOK.md](./RUNBOOK.md)

## Additional Resources

- [User Guide](./USER_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Environment Variables](./ENVIRONMENT_VARIABLES.md)
- [Runbook](./RUNBOOK.md)
- [Next.js Documentation](https://nextjs.org/docs)
- [Clerk Documentation](https://clerk.com/docs)
