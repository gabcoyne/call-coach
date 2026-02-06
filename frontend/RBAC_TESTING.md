# Role-Based Access Control (RBAC) Testing Guide

This document provides testing procedures to verify that role-based access control is working correctly in the Gong Call Coaching application.

## Prerequisites

Before testing, ensure you have:

1. Two test users in Clerk Dashboard:
   - **Manager test user** with `publicMetadata.role = "manager"`
   - **Rep test user** with `publicMetadata.role = "rep"` (or no role set)

## Test Scenarios

### Test 1: Manager Role - Full Access

**Objective:** Verify managers can access all reps' data

**Steps:**

1. Sign in as the manager test user
2. Navigate to `/dashboard`
3. Verify you see a list of all reps (manager view)
4. Click on a rep to view their dashboard
5. Navigate to `/dashboard/[any-rep-email]`
6. Verify you can view the rep's data and insights

**Expected Results:**

- Manager sees team overview on `/dashboard`
- Manager can access any rep's individual dashboard
- Manager-only features are visible (e.g., Rep Selector, team analytics)
- No access denied errors

**Acceptance Criteria:**

- [ ] Manager dashboard shows all reps
- [ ] Can navigate to any rep's dashboard
- [ ] Manager-only UI elements are visible
- [ ] No 403 errors when viewing rep data

---

### Test 2: Rep Role - Restricted Access

**Objective:** Verify reps can only access their own data

**Steps:**

1. Sign in as the rep test user
2. Navigate to `/dashboard`
3. Verify you are automatically directed to your own dashboard
4. Try to navigate to `/dashboard/[another-rep-email]`
5. Verify you are redirected to your own dashboard or see a 403 error

**Expected Results:**

- Rep only sees their own dashboard
- Attempting to view another rep's data results in redirect or 403 error
- Manager-only features are hidden
- Rep can view their own calls and insights

**Acceptance Criteria:**

- [ ] Rep sees only their own dashboard
- [ ] Cannot access other reps' dashboards
- [ ] Manager-only features are hidden
- [ ] Own data loads correctly

---

### Test 3: Manager-Only Features Visibility

**Objective:** Verify manager-only features are properly hidden from reps

**Features to Check:**

| Feature                       | Manager (Visible) | Rep (Hidden) |
| ----------------------------- | ----------------- | ------------ |
| Team overview on `/dashboard` | ✅                | ❌           |
| Rep selector dropdown         | ✅                | ❌           |
| Team analytics                | ✅                | ❌           |
| All reps' call history        | ✅                | ❌           |
| Team-wide search filters      | ✅                | ❌           |

**Steps:**

1. Sign in as manager and note which features are visible
2. Sign out
3. Sign in as rep
4. Verify those same features are hidden

**Acceptance Criteria:**

- [ ] Rep selector is visible to managers only
- [ ] Team overview is manager-only
- [ ] Search page filters show "All Reps" for managers, disabled for reps
- [ ] No manager-only buttons/links visible to reps

---

### Test 4: 403 Forbidden Page

**Objective:** Verify 403 error page displays for unauthorized access

**Steps:**

1. Sign in as rep
2. Note your email address (e.g., `rep@test.com`)
3. Try to navigate to `/dashboard/another-rep@test.com`
4. Verify 403 page or redirect occurs

**Expected Results:**

- 403 error page is displayed, OR
- Automatic redirect to own dashboard
- Clear error message explaining lack of permission
- "Go back" and "Go to dashboard" buttons work

**Acceptance Criteria:**

- [ ] 403 page displays with clear message
- [ ] Error message is user-friendly
- [ ] Navigation buttons work correctly
- [ ] Page is styled consistently with app

---

### Test 5: Role Utilities Functionality

**Objective:** Verify client-side auth utility functions work correctly

**Test Cases:**

```typescript
// Test with manager user object
import { isManager, isRep, canViewRepData, getUserRole } from "@/lib/auth-utils";

// Manager tests
const managerUser = { publicMetadata: { role: "manager" } };
console.assert(isManager(managerUser) === true);
console.assert(isRep(managerUser) === false);
console.assert(getUserRole(managerUser) === "manager");
console.assert(canViewRepData(managerUser, "any@email.com") === true);

// Rep tests
const repUser = {
  publicMetadata: { role: "rep" },
  emailAddresses: [{ emailAddress: "rep@test.com" }],
};
console.assert(isManager(repUser) === false);
console.assert(isRep(repUser) === true);
console.assert(getUserRole(repUser) === "rep");
console.assert(canViewRepData(repUser, "rep@test.com") === true);
console.assert(canViewRepData(repUser, "other@test.com") === false);

// Default to rep when no role is set
const noRoleUser = { publicMetadata: {} };
console.assert(isRep(noRoleUser) === true);
console.assert(isManager(noRoleUser) === false);
```

**Acceptance Criteria:**

- [ ] `isManager()` returns correct boolean
- [ ] `isRep()` returns correct boolean
- [ ] `canViewRepData()` enforces access rules
- [ ] `getUserRole()` returns correct role enum
- [ ] Default role is "rep" when not set

---

### Test 6: Backend Authorization

**Objective:** Verify backend API enforces role-based access

**Steps:**

1. Sign in as rep
2. Open browser DevTools Network tab
3. Navigate to your own dashboard
4. Check API request to `/api/rep-insights`
5. Note the Authorization header contains Clerk token
6. Try to manually fetch another rep's insights (if possible)
7. Verify backend returns 403 or filters data

**Expected Results:**

- Backend validates Clerk token
- Rep can only fetch their own data via API
- Manager can fetch any rep's data via API
- 403 or empty response for unauthorized requests

**Acceptance Criteria:**

- [ ] API requests include Clerk auth token
- [ ] Backend enforces role-based data access
- [ ] Reps cannot access other reps' data via API
- [ ] Managers can access all data via API

---

### Test 7: Role Assignment and Changes

**Objective:** Verify role changes take effect properly

**Steps:**

1. Sign in as rep
2. Note current access level
3. Have admin change role to "manager" in Clerk Dashboard
4. Sign out and sign back in
5. Verify new manager access is active

**Expected Results:**

- Role change requires sign-out/sign-in to take effect
- New role is immediately active after re-authentication
- All manager features become accessible

**Acceptance Criteria:**

- [ ] Role changes require re-authentication
- [ ] New role takes effect immediately after sign-in
- [ ] No cached old role data

---

### Test 8: Search Page Role Filtering

**Objective:** Verify search results respect role-based access

**Steps:**

1. Sign in as manager
2. Navigate to `/search`
3. Verify "Rep Filter" dropdown is visible
4. Search for calls across all reps
5. Sign out and sign in as rep
6. Navigate to `/search`
7. Verify "Rep Filter" is hidden or disabled
8. Verify search results only show your own calls

**Expected Results:**

- Managers see all reps' calls in search results
- Reps only see their own calls
- Rep filter is manager-only

**Acceptance Criteria:**

- [ ] Rep filter visible to managers
- [ ] Rep filter hidden/disabled for reps
- [ ] Search results filtered by role
- [ ] No other reps' calls appear for rep users

---

## Automated Testing

For automated testing, use the following approach:

```typescript
// __tests__/rbac/auth-utils.test.ts
import { isManager, canViewRepData } from "@/lib/auth-utils";

describe("RBAC Utilities", () => {
  it("correctly identifies manager role", () => {
    const manager = { publicMetadata: { role: "manager" } };
    expect(isManager(manager)).toBe(true);
  });

  it("correctly identifies rep role", () => {
    const rep = { publicMetadata: { role: "rep" } };
    expect(isManager(rep)).toBe(false);
  });

  it("managers can view all rep data", () => {
    const manager = { publicMetadata: { role: "manager" } };
    expect(canViewRepData(manager, "any@email.com")).toBe(true);
  });

  it("reps can only view own data", () => {
    const rep = {
      publicMetadata: { role: "rep" },
      emailAddresses: [{ emailAddress: "rep@test.com" }],
    };
    expect(canViewRepData(rep, "rep@test.com")).toBe(true);
    expect(canViewRepData(rep, "other@test.com")).toBe(false);
  });
});
```

---

## Common Issues and Troubleshooting

### Issue: Role not taking effect after assignment

**Solution:**

- Sign out completely
- Clear browser cookies and localStorage
- Sign back in
- Verify role in Clerk Dashboard

### Issue: 403 page not displaying

**Solution:**

- Check that `/app/403.tsx` exists
- Verify redirect logic in page components
- Check browser console for errors

### Issue: Manager sees rep view

**Solution:**

- Verify `publicMetadata.role = "manager"` in Clerk Dashboard
- Check that role is exactly "manager" (lowercase)
- Ensure no extra spaces in role value

### Issue: Rep can access other reps' data

**Solution:**

- Check that backend API enforces authorization
- Verify `canViewRepData()` is being used
- Review component-level access checks

---

## Security Checklist

Before deploying to production, ensure:

- [ ] All manager-only routes enforce role checks
- [ ] Backend API validates roles via Clerk token
- [ ] 403 page exists for unauthorized access
- [ ] Client-side checks prevent UI exposure
- [ ] Server-side checks prevent data access
- [ ] Role assignment process is documented
- [ ] Only authorized personnel can assign manager role
- [ ] Audit trail exists for role changes

---

## Testing Completion Checklist

Mark each test scenario as complete:

- [ ] Test 1: Manager full access verified
- [ ] Test 2: Rep restricted access verified
- [ ] Test 3: Manager-only features properly hidden
- [ ] Test 4: 403 page displays correctly
- [ ] Test 5: Role utility functions work
- [ ] Test 6: Backend authorization enforced
- [ ] Test 7: Role changes take effect
- [ ] Test 8: Search filtering respects roles

**Testing completed by:** **\*\***\_\_\_**\*\***
**Date:** **\*\***\_\_\_**\*\***
**Verified by:** **\*\***\_\_\_**\*\***
