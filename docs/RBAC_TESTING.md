# RBAC Testing Guide

## Prerequisites

1. API server must be running: `python api/rest_server.py`
2. Database migration 006 must be applied
3. Test users must exist in the database

## Test Users

Based on current database:

- **Admin**: `admin@prefect.io`
- **Manager**: `ann@prefect.io`
- **Reps**: `trent@prefect.io`, `wayne@prefect.io`, `shane@prefect.io`, etc.

## Manual Testing

### Test 1: Get Current User (All Roles)

```bash
# As Rep
curl -H "X-User-Email: trent@prefect.io" http://localhost:8000/api/v1/users/me

# As Manager
curl -H "X-User-Email: ann@prefect.io" http://localhost:8000/api/v1/users/me

# As Admin
curl -H "X-User-Email: admin@prefect.io" http://localhost:8000/api/v1/users/me
```

**Expected Results:**
- All should return 200 with user profile
- Each user should have the correct role

---

### Test 2: Get Team Reps (Managers/Admins Only)

```bash
# As Manager (should work)
curl -H "X-User-Email: ann@prefect.io" http://localhost:8000/api/v1/team/reps

# As Rep (should fail with 403)
curl -H "X-User-Email: trent@prefect.io" http://localhost:8000/api/v1/team/reps

# As Admin (should work)
curl -H "X-User-Email: admin@prefect.io" http://localhost:8000/api/v1/team/reps
```

**Expected Results:**
- Manager: 200 with list of managed reps
- Rep: 403 Forbidden
- Admin: 200 with list of managed reps

---

### Test 3: Get Team Calls (Managers/Admins Only)

```bash
# As Manager (should work)
curl -H "X-User-Email: ann@prefect.io" "http://localhost:8000/api/v1/team/calls?limit=5"

# As Rep (should fail with 403)
curl -H "X-User-Email: trent@prefect.io" "http://localhost:8000/api/v1/team/calls?limit=5"

# As Admin (should work)
curl -H "X-User-Email: admin@prefect.io" "http://localhost:8000/api/v1/team/calls?limit=5"
```

**Expected Results:**
- Manager: 200 with team's calls
- Rep: 403 Forbidden
- Admin: 200 with all calls

---

### Test 4: Get Calls (Role-Based Filtering)

```bash
# As Rep (only sees own calls)
curl -H "X-User-Email: trent@prefect.io" "http://localhost:8000/api/v1/calls?limit=5"

# As Manager (sees team calls)
curl -H "X-User-Email: ann@prefect.io" "http://localhost:8000/api/v1/calls?limit=5"

# As Admin (sees all calls)
curl -H "X-User-Email: admin@prefect.io" "http://localhost:8000/api/v1/calls?limit=5"
```

**Expected Results:**
- Rep: 200 with only their calls
- Manager: 200 with team's calls
- Admin: 200 with all calls

---

### Test 5: No Authentication (Should Fail)

```bash
# Missing X-User-Email header
curl http://localhost:8000/api/v1/users/me
```

**Expected Result:**
- 401 Unauthorized with error message

---

### Test 6: Invalid User (Should Fail)

```bash
# Non-existent user
curl -H "X-User-Email: nonexistent@prefect.io" http://localhost:8000/api/v1/users/me
```

**Expected Result:**
- 404 Not Found with error message

---

## Automated Testing

Run the automated test suite:

```bash
# Create a test script
cat > test_rbac_live.sh << 'EOF'
#!/bin/bash

API_URL="http://localhost:8000"
PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local email="$2"
    local endpoint="$3"
    local expected_status="$4"

    echo -n "Testing: $name... "

    if [ -z "$email" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$endpoint")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -H "X-User-Email: $email" "$API_URL$endpoint")
    fi

    if [ "$status" = "$expected_status" ]; then
        echo "✓ PASS (got $status)"
        ((PASS++))
    else
        echo "✗ FAIL (expected $expected_status, got $status)"
        ((FAIL++))
    fi
}

echo "========================================="
echo "RBAC API Testing"
echo "========================================="
echo

# Test authentication
test_endpoint "No auth header" "" "/api/v1/users/me" "401"
test_endpoint "Invalid user" "nonexistent@prefect.io" "/api/v1/users/me" "404"

# Test /users/me
test_endpoint "Get user (rep)" "trent@prefect.io" "/api/v1/users/me" "200"
test_endpoint "Get user (manager)" "ann@prefect.io" "/api/v1/users/me" "200"
test_endpoint "Get user (admin)" "admin@prefect.io" "/api/v1/users/me" "200"

# Test /team/reps
test_endpoint "Team reps (rep - forbidden)" "trent@prefect.io" "/api/v1/team/reps" "403"
test_endpoint "Team reps (manager)" "ann@prefect.io" "/api/v1/team/reps" "200"
test_endpoint "Team reps (admin)" "admin@prefect.io" "/api/v1/team/reps" "200"

# Test /team/calls
test_endpoint "Team calls (rep - forbidden)" "trent@prefect.io" "/api/v1/team/calls" "403"
test_endpoint "Team calls (manager)" "ann@prefect.io" "/api/v1/team/calls" "200"
test_endpoint "Team calls (admin)" "admin@prefect.io" "/api/v1/team/calls" "200"

# Test /calls
test_endpoint "Calls (rep)" "trent@prefect.io" "/api/v1/calls?limit=5" "200"
test_endpoint "Calls (manager)" "ann@prefect.io" "/api/v1/calls?limit=5" "200"
test_endpoint "Calls (admin)" "admin@prefect.io" "/api/v1/calls?limit=5" "200"

echo
echo "========================================="
echo "Results: $PASS passed, $FAIL failed"
echo "========================================="

exit $FAIL
EOF

chmod +x test_rbac_live.sh
./test_rbac_live.sh
```

---

## Common Issues

### Issue: All endpoints return 404

**Solution:** The API server needs to be restarted to load the new routes.

```bash
# Find the process
ps aux | grep rest_server

# Kill it
kill <PID>

# Restart
python api/rest_server.py
```

### Issue: User not found (404)

**Solution:** Ensure the user exists in the database.

```bash
# Check users
python -c "from db import queries; users = queries.fetch_all('SELECT email, role FROM users'); print('\\n'.join(f'{u[\"email\"]}: {u[\"role\"]}' for u in users))"
```

### Issue: Manager sees no reps

**Solution:** Ensure reps have their `manager_id` set in the speakers table.

```sql
-- Check manager assignments
SELECT u.email, u.role, u2.email as manager_email
FROM users u
LEFT JOIN speakers s ON u.email = s.email
LEFT JOIN users u2 ON s.manager_id = u2.id
WHERE u.role = 'rep';
```

---

## Integration with Frontend

The Next.js frontend should:

1. Get user session from Clerk
2. Extract user email from session
3. Pass email in `X-User-Email` header (or use Clerk JWT in production)
4. Handle 401/403/404 responses appropriately

Example frontend code:

```typescript
// lib/api-client.ts
import { auth } from '@clerk/nextjs/server';

export async function apiClient(endpoint: string, options?: RequestInit) {
  const { userId } = await auth();

  if (!userId) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${process.env.API_URL}${endpoint}`, {
    ...options,
    headers: {
      'X-User-Email': userId, // or extract from Clerk user object
      ...options?.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Not authenticated');
    }
    if (response.status === 403) {
      throw new Error('Insufficient permissions');
    }
    if (response.status === 404) {
      throw new Error('Resource not found');
    }
    throw new Error('API request failed');
  }

  return response.json();
}
```
