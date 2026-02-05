# Clerk Authentication Setup Guide

## Task 3.1: Create Clerk Account and Application

### Steps to Complete:

1. **Create a Clerk Account**
   - Go to [https://dashboard.clerk.com/sign-up](https://dashboard.clerk.com/sign-up)
   - Sign up with your email or GitHub account

2. **Create a New Application**
   - Click "Add application" in the Clerk dashboard
   - Name: `Gong Call Coaching` (or `Call Coach - Dev` for development)
   - Choose authentication methods:
     - ✅ Email
     - ✅ Password
     - ✅ Google (optional, recommended)
   - Click "Create application"

3. **Get API Keys**
   - After creating the app, you'll see your API keys
   - Copy the `Publishable Key` (starts with `pk_test_...`)
   - Copy the `Secret Key` (starts with `sk_test_...`)
   - Create a `.env.local` file in the `frontend/` directory:
     ```bash
     cd frontend
     cp .env.example .env.local
     ```
   - Paste your keys into `.env.local`:
     ```
     NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
     CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE
     ```

4. **Configure User Metadata for Roles**
   - In Clerk Dashboard, go to "Users & Authentication" → "Metadata"
   - We use `publicMetadata.role` to store user roles
   - Roles: `manager` or `rep`

5. **Set First User as Manager**
   - After signing up your first user, go to Clerk Dashboard → "Users"
   - Click on your user
   - Go to "Metadata" tab
   - Under "Public metadata", add:
     ```json
     {
       "role": "manager"
     }
     ```
   - Click "Save"

## Task 3.2: Install Dependencies

```bash
cd frontend
npm install @clerk/nextjs
```

This has been added to `package.json`. Run `npm install` to install it.

## Task 3.9: Testing Authentication Flow

### Manual Testing Steps:

1. **Start the Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test Sign-Up Flow**
   - Navigate to [http://localhost:3000](http://localhost:3000)
   - You should be redirected to `/sign-in` (protected route)
   - Click "Don't have an account? Sign up"
   - Complete the sign-up form
   - Verify email if required
   - Check that you're redirected to `/dashboard` after sign-up

3. **Test Sign-In Flow**
   - Sign out (if signed in)
   - Navigate to `/sign-in`
   - Enter credentials
   - Verify successful login and redirect to `/dashboard`

4. **Test Route Protection**
   - Sign out
   - Try to navigate to `/dashboard` or any protected route
   - Verify you're redirected to `/sign-in`
   - Sign in and verify you can access protected routes

5. **Test Role-Based Access Control (RBAC)**
   - Create two test users in Clerk Dashboard:
     - User 1: Set `publicMetadata.role` to `"manager"`
     - User 2: Set `publicMetadata.role` to `"rep"` (or leave empty, defaults to rep)
   - Test manager access:
     - Sign in as manager
     - Should see manager-only features (to be implemented in later tasks)
   - Test rep access:
     - Sign in as rep
     - Should only see own data (to be implemented in later tasks)

6. **Test Logout Flow**
   - Click logout (once implemented in UI)
   - Verify session is cleared
   - Verify redirect to sign-in page

### Automated Testing (Future)

Once Jest and React Testing Library are set up (Task 12.5), add tests:

```typescript
// __tests__/auth/sign-in.test.tsx
describe("Sign-In Flow", () => {
  it("redirects unauthenticated users to /sign-in", () => {
    // Test implementation
  });

  it("allows authenticated users to access protected routes", () => {
    // Test implementation
  });
});

// __tests__/auth/rbac.test.ts
describe("RBAC Utilities", () => {
  it("correctly identifies manager role", () => {
    // Test implementation
  });

  it("restricts rep access to own data only", () => {
    // Test implementation
  });
});
```

## Role Configuration in Clerk

### Setting Roles via Clerk Dashboard

For each user, set their role in public metadata:

**Manager:**
```json
{
  "role": "manager"
}
```

**Sales Rep:**
```json
{
  "role": "rep"
}
```

### Bulk Role Assignment (Future Enhancement)

For production, consider:
- Using Clerk webhooks to auto-assign roles based on email domain
- Using Clerk Organizations to manage teams
- Syncing roles from an external HR system via API

## Security Considerations

1. **Environment Variables**
   - Never commit `.env.local` to git
   - Use Vercel environment variables for production
   - Rotate keys if they're ever exposed

2. **Role Validation**
   - Always validate roles server-side using `lib/auth.ts` utilities
   - Never trust client-side role checks
   - Use middleware for route-level protection

3. **Session Management**
   - Clerk handles session tokens automatically
   - Sessions expire after inactivity (configurable in Clerk Dashboard)
   - Use `auth()` or `currentUser()` server-side to validate sessions

## Troubleshooting

### "Clerk: Missing publishableKey"
- Ensure `.env.local` exists with correct keys
- Restart dev server after adding environment variables
- Check that keys don't have extra spaces or quotes

### "Clerk: Invalid session token"
- Clear browser cookies and localStorage
- Sign out and sign in again
- Check that CLERK_SECRET_KEY is correct

### Users not getting redirected after sign-in
- Check `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` in `.env.local`
- Verify middleware configuration in `middleware.ts`
- Check browser console for errors

## Next Steps

After authentication is working:
- Implement user profile UI (Section 10)
- Add role-based UI elements
- Implement manager/rep dashboards with proper access control
- Set up Clerk webhooks for user lifecycle events
