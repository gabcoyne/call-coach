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

## Role Assignment Process

### Manager Role Assignment Authority

Only **Sales Leadership** and **Engineering Admins** have authority to assign the manager role in Clerk Dashboard.

**Current authorized personnel:**
- VP of Sales
- Sales Operations Manager
- Engineering team leads

**Process for assigning manager role:**

1. **Request**: New manager sends email to sales-ops@prefect.io with:
   - Full name
   - Email address used for Clerk sign-up
   - Justification for manager access

2. **Approval**: Sales Ops Manager reviews request and approves within 1 business day

3. **Assignment**: Authorized personnel:
   - Log into Clerk Dashboard (https://dashboard.clerk.com)
   - Navigate to "Users" section
   - Search for user by email
   - Click on user → "Metadata" tab
   - Under "Public metadata", add or update:
     ```json
     {
       "role": "manager"
     }
     ```
   - Click "Save"

4. **Verification**: User signs out and signs back in to receive manager role

5. **Audit**: Log assignment in #sales-ops Slack channel:
   ```
   Assigned manager role to [Name] ([email]) - approved by [Approver]
   ```

### Rep Role (Default)

All users default to "rep" role if no role is specified in publicMetadata. No action required.

### Role Revocation

To remove manager access:
1. Navigate to user in Clerk Dashboard
2. Go to "Metadata" tab
3. Under "Public metadata", either:
   - Change `"role": "manager"` to `"role": "rep"`
   - Or remove the role field entirely (defaults to rep)
4. Click "Save"
5. User's access changes immediately on next page load

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

### Understanding Roles

The Gong Call Coaching app has two roles:

1. **Manager (`manager`)**: Full access to all features
   - View all sales reps' dashboards and data
   - Access team-wide analytics and insights
   - Search and filter across all calls
   - View manager-only features

2. **Sales Rep (`rep`)**: Limited access to own data
   - View only their own dashboard and call data
   - Cannot access other reps' information
   - Restricted search results to own calls
   - No access to manager-only features

### Setting Roles via Clerk Dashboard

#### For Individual Users:

1. **Navigate to Users**
   - Go to [Clerk Dashboard](https://dashboard.clerk.com)
   - Click on "Users" in the sidebar
   - Find the user you want to assign a role to

2. **Edit User Metadata**
   - Click on the user to open their profile
   - Navigate to the "Metadata" tab
   - Under "Public metadata", click "Edit"

3. **Set Role**

   **For Managers:**
   ```json
   {
     "role": "manager"
   }
   ```

   **For Sales Reps:**
   ```json
   {
     "role": "rep"
   }
   ```

   Note: If no role is set, users default to "rep" role.

4. **Save Changes**
   - Click "Save" to apply the changes
   - The user will need to sign out and sign back in for the role to take effect

#### Quick Setup for Testing:

For development and testing, create at least two test users:

1. **Manager Test User:**
   - Email: `manager@test.com`
   - Public Metadata: `{ "role": "manager" }`

2. **Rep Test User:**
   - Email: `rep@test.com`
   - Public Metadata: `{ "role": "rep" }`

### Verifying Role Assignment

After setting roles, verify they're working correctly:

1. **Sign in as Manager:**
   - Should see all reps in the dashboard
   - Can navigate to any rep's individual dashboard
   - See manager-only UI elements (e.g., Rep Selector)

2. **Sign in as Rep:**
   - Should only see own dashboard
   - Attempting to view another rep's dashboard redirects to own dashboard
   - Manager-only features are hidden

### Role-Based Access Control Implementation

The app implements RBAC at multiple layers:

1. **Client-Side Utilities** (`lib/auth-utils.ts`):
   - `isManager(user)`: Check if user is a manager
   - `canViewRepData(user, repEmail)`: Check if user can view specific rep's data
   - `hasManagerAccess(user)`: Check for manager-only features

2. **Server-Side Utilities** (`lib/auth.ts`):
   - `getCurrentUserRole()`: Get role from session
   - `requireManager()`: Enforce manager-only access
   - `canViewRepData(repEmail)`: Server-side authorization check

3. **Component-Level Protection:**
   ```tsx
   import { useUser } from "@clerk/nextjs";
   import { isManager } from "@/lib/auth-utils";

   const { user } = useUser();

   {isManager(user) && (
     <ManagerOnlyFeature />
   )}
   ```

4. **Page-Level Protection:**
   - Automatic redirects for unauthorized access attempts
   - 403 error page for forbidden access
   - Backend API validates roles via Clerk token

### Bulk Role Assignment (Future Enhancement)

For production deployment with many users, consider:

1. **Webhook-Based Auto-Assignment:**
   - Set up Clerk webhook for `user.created` events
   - Auto-assign roles based on email domain (e.g., `*@sales.prefect.io` = rep)
   - Example: Managers from `*@management.prefect.io`

2. **Organization-Based Roles:**
   - Use Clerk Organizations feature
   - Create "Sales Team" and "Management" organizations
   - Assign roles based on organization membership

3. **External System Integration:**
   - Sync roles from HR/CRM systems via API
   - Use Clerk Management API to bulk update `publicMetadata`
   - Automate role updates on employee status changes

4. **CSV Import Script:**
   ```bash
   # Example script structure
   # Import users from CSV and set roles
   node scripts/import-users.js users.csv
   ```

### Role Migration and Updates

If you need to update roles for existing users:

1. **Individual Update:** Use Clerk Dashboard (method above)
2. **Bulk Update:** Use Clerk Management API
3. **After Role Changes:** Users must sign out and sign back in

### Common Role Assignment Scenarios

**Scenario 1: New Manager Onboarding**
1. Create user account via sign-up flow
2. Set `publicMetadata.role = "manager"` in Clerk Dashboard
3. User signs in and has full manager access

**Scenario 2: Rep Promotion to Manager**
1. Navigate to user in Clerk Dashboard
2. Update `publicMetadata.role` from `"rep"` to `"manager"`
3. User signs out and back in
4. Now has manager access to all data

**Scenario 3: Manager Demotion to Rep**
1. Update `publicMetadata.role` from `"manager"` to `"rep"`
2. User signs out and back in
3. Access restricted to own data only

**Scenario 4: Bulk Department Role Assignment**
- Use Clerk Management API with script
- Filter users by email domain
- Set roles in batch operation

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
