# Role Management & Access Control

Understanding user roles and permissions in Call Coach.

## User Roles

Call Coach has two primary user roles with different capabilities:

### Sales Rep

**Who**: Individual sales representatives (AE, SE, CSM)

**What They Can Do**:
- View their own call analyses
- See their personal performance dashboard
- Create their own coaching plans
- Search their own calls
- View weekly reports for themselves
- Compare their scores to team averages (anonymized)

**What They Cannot Do**:
- View other reps' call data
- View other reps' performance dashboards
- Download team reports
- Export data
- Manage system settings

**Access Pattern**:
```
Rep Sarah logs in
├─ Can see Sarah's calls
├─ Can see Sarah's dashboard
├─ Can create Sarah's coaching plan
└─ Cannot see John's calls or dashboard
```

**Primary Use Cases**:
- Review my recent calls
- Understand my strengths and gaps
- Track my improvement over time
- Find calls to learn from

---

### Manager

**Who**: Sales managers, directors, team leads

**What They Can Do**:
- View all team members' call analyses
- Compare rep performance
- View aggregate team insights
- Generate team reports
- Create team coaching plans
- Access analytics and trends
- Export data for analysis
- Monitor team progress

**What They Cannot Do**:
- Edit call analyses
- Delete historical data
- Change system-level settings
- Access data outside their scope

**Access Pattern**:
```
Manager John logs in
├─ Can see all team members' calls
├─ Can see all team dashboards
├─ Can compare Sarah vs Tom scores
├─ Can create team coaching plan
└─ Can generate team report
```

**Primary Use Cases**:
- Monitor team performance
- Identify coaching opportunities
- Track team trends
- Report to leadership
- Develop team skills

---

## Setting Up Roles

### In Clerk (Authentication)

Roles are managed through Clerk's role/permission system.

**Step 1: Create Roles in Clerk**

1. Go to Clerk Dashboard: https://dashboard.clerk.com
2. Navigate to: Users & Authentication → Roles
3. Create two roles:
   - **Rep** (with permissions: view_own_data, analyze_own_calls)
   - **Manager** (with permissions: view_all_data, generate_reports)

**Step 2: Assign Roles to Users**

1. Go to: Users & Authentication → Users
2. Select a user
3. Go to "Roles" section
4. Assign either "Rep" or "Manager"

**Step 3: Sync Roles to Application**

The frontend automatically checks role on login:

```typescript
// In Next.js component
const { sessionClaims } = useAuth();
const userRole = sessionClaims?.role;  // 'rep' or 'manager'

if (userRole === 'manager') {
  // Show manager features
} else {
  // Show rep features
}
```

---

## Role-Based Features

### Rep Dashboard

**Shows**:
- Personal performance metrics
- Trend graphs (Discovery, Product, Objections, Engagement)
- Recent analyzed calls (5 most recent)
- Personal coaching plan
- Weekly report (self only)

**UI Elements**:
- "My Dashboard" in navigation
- Can only view own data
- Restricted search (only own calls)

**Example**:
```
Sarah's Dashboard
├─ This Month: 82 average score
├─ Trend: Improving (+5)
├─ Recent Calls:
│  ├─ Acme Corp: 95
│  ├─ TechStart: 88
│  └─ FinCorp: 82
└─ Coaching Plan:
   └─ Focus: Objection handling
```

---

### Manager Dashboard

**Shows**:
- Team member performance metrics
- Peer comparison matrix
- Team trend analysis
- Team coaching opportunities
- Team reports

**UI Elements**:
- "Team Dashboard" in navigation
- Can select individual team members
- Advanced filtering and sorting
- Export to CSV/PDF

**Example**:
```
Manager Dashboard
├─ Team Performance:
│  ├─ Sarah: 82 avg (↑ improving)
│  ├─ Tom: 76 avg (→ stable)
│  └─ Lisa: 85 avg (→ stable)
├─ Skill Gaps (Team):
│  └─ Objection Handling: Team avg 76 (below target 80)
└─ Reports:
   └─ Generate Team Weekly Report
```

---

## Data Visibility Rules

### What Reps See

**Can See**:
- Their own call list
- Their own analysis details
- Their own scores and trends
- Their own coaching plan
- Team average scores (no names)
- Top performers (anonymized, top 3)

**Cannot See**:
- Other reps' call details
- Specific peer performance
- Other reps' names in comparisons
- Team reports

### What Managers See

**Can See**:
- All team members' calls
- All analysis details
- Individual and team scores
- All coaching plans
- Team reports
- Trend analysis
- Performance comparisons

**Rules**:
- Manager sees only their team (from Clerk org structure)
- Cannot see calls from other departments
- Cannot see leadership dashboard (if applicable)

---

## Implementing Role Checks

### Frontend (React/Next.js)

```typescript
import { useAuth } from "@clerk/nextjs";

function Dashboard() {
  const { sessionClaims, isLoaded } = useAuth();

  if (!isLoaded) return <div>Loading...</div>;

  const userRole = sessionClaims?.role;

  if (userRole === "manager") {
    return <ManagerDashboard />;
  } else if (userRole === "rep") {
    return <RepDashboard />;
  } else {
    return <div>Unknown role</div>;
  }
}
```

### API (Python/FastAPI)

```python
from fastapi import HTTPException
from coaching_mcp.shared import get_current_user

@app.get("/coaching/rep-insights")
async def get_insights(rep_email: str, current_user = Depends(get_current_user)):
    user_role = current_user.get("role")

    if user_role == "manager":
        # Allow viewing any rep's data
        pass
    elif user_role == "rep":
        # Allow viewing only own data
        if rep_email != current_user.get("email"):
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=403, detail="Unknown role")

    # Continue with analysis...
```

---

## Common Access Scenarios

### Scenario 1: Rep Reviews Own Call

```
Sarah logs in
├─ ✓ Can see dashboard (her own)
├─ ✓ Can analyze call (her own)
├─ ✓ Can view analysis results
├─ ✓ Can create coaching plan
└─ ✗ Cannot view John's dashboard
```

**Result**: Works fine - no restrictions needed.

---

### Scenario 2: Manager Reviews Team Performance

```
Manager John logs in
├─ ✓ Can see team dashboard
├─ ✓ Can view Sarah's calls
├─ ✓ Can view Tom's analysis
├─ ✓ Can generate team report
└─ ✓ Can export data
```

**Result**: Works fine - manager permissions active.

---

### Scenario 3: Rep Tries to View Peer Data

```
Rep Sarah tries to view Tom's dashboard
├─ Clerk checks: Is Sarah a manager?
├─ Answer: No, Sarah is a rep
├─ Clerk checks: Is Tom Sarah?
├─ Answer: No
└─ Result: 403 Forbidden - redirected to own dashboard
```

**Result**: Access denied - security working correctly.

---

### Scenario 4: Admin Manages Roles

```
Clerk Admin in Clerk Dashboard
├─ Go to Users section
├─ Select a user
├─ Change role from "rep" to "manager"
├─ Confirm change
└─ User sees updated permissions on next login
```

**Result**: Role change takes effect immediately on next login.

---

## Team Structure

### How Teams are Defined

Teams in Call Coach are based on Clerk's organization structure:

**Option 1: Clerk Organizations**
```
Organization: Sales Team
├─ John (Manager)
│  └─ Role: manager
├─ Sarah (Sales Rep)
│  └─ Role: rep
├─ Tom (Sales Rep)
│  └─ Role: rep
└─ Lisa (Sales Rep)
    └─ Role: rep
```

John (manager) sees Sarah, Tom, and Lisa's data.

**Option 2: Custom Team Assignment**
If not using Clerk orgs:
1. Store team assignments in database
2. Add team_id to user claims
3. Check team_id when viewing data

---

## Troubleshooting Access Issues

### "I Can't See Other Reps' Data" (as Manager)

**Cause**: Role not set to "manager" or not in same team

**Solution**:
```bash
1. Go to Clerk Dashboard
2. Select your user account
3. Go to "Roles" section
4. Verify role is set to "manager"
5. Log out and log back in
6. Try again
```

---

### "I Can See Reps' Data" (as Rep)

**Cause**: Role set incorrectly

**Solution**:
```bash
1. Go to Clerk Dashboard
2. Find your user
3. Check role in "Roles" section
4. Should be "rep", not "manager"
5. Fix if needed
6. Log out and log back in
```

---

### "Role Didn't Update" (after Change)

**Cause**: Clerk cache or not logged out

**Solution**:
```bash
1. Log out completely
2. Clear browser cookies (for Clerk)
3. Close browser
4. Open browser
5. Log back in
6. Verify new role
```

---

## Best Practices

1. **Regular Access Audits**
   - Monthly: Check role assignments
   - Quarterly: Audit data access logs
   - Remove roles for departed team members

2. **Principle of Least Privilege**
   - Assign minimal required role
   - Rep: Default role for new hires
   - Manager: Only for managers, directors

3. **Clear Role Definitions**
   - Communicate role capabilities
   - Document access policies
   - Train managers on features

4. **Secure Transitions**
   - When rep becomes manager: Upgrade role
   - When manager leaves: Downgrade to rep
   - Immediate revocation: Remove all access

5. **Monitor Access**
   - Log who accessed what, when
   - Review logs for suspicious activity
   - Alert on privilege escalation

---

## Related Topics

- [Getting Started](./README.md) - User guide overview
- [Using Coaching Insights](./coaching.md) - How to apply coaching
- [Weekly Reports](./weekly-reports.md) - Understanding reports
- [Deployment](../deployment/) - Setting up production

---

**Questions about access?** Contact your manager or system administrator.
