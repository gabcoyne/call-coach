# RBAC API Documentation

## Overview

The Call Coach API implements role-based access control (RBAC) with three user roles:

- **Admin**: Full access to all calls and data
- **Manager**: Access to their team's calls and coaching data
- **Rep**: Access only to their own calls and coaching data

## Authentication

For testing, authentication uses the `X-User-Email` header:

```bash
curl -H "X-User-Email: user@prefect.io" http://localhost:8000/api/v1/users/me
```

In production, this will be replaced with Clerk JWT authentication.

## Endpoints

### Users

#### GET /api/v1/users/me

Get current authenticated user profile.

**Headers:**
- `X-User-Email`: User email for authentication

**Response:**
```json
{
  "id": "uuid",
  "email": "user@prefect.io",
  "name": "User Name",
  "role": "rep"
}
```

**Status Codes:**
- `200`: Success
- `401`: Not authenticated (missing header)
- `404`: User not found

**Example:**
```bash
curl -H "X-User-Email: trent@prefect.io" http://localhost:8000/api/v1/users/me
```

---

### Team Management (Managers & Admins Only)

#### GET /api/v1/team/reps

Get all reps managed by current user.

**Access:** Managers and admins only

**Headers:**
- `X-User-Email`: Manager email for authentication

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "rep@prefect.io",
    "name": "Rep Name",
    "role": "rep"
  }
]
```

**Status Codes:**
- `200`: Success
- `401`: Not authenticated
- `403`: Insufficient permissions (not a manager or admin)
- `404`: User not found

**Example:**
```bash
curl -H "X-User-Email: ann@prefect.io" http://localhost:8000/api/v1/team/reps
```

---

#### GET /api/v1/team/calls

Get all calls from managed reps.

**Access:** Managers and admins only

**Headers:**
- `X-User-Email`: Manager email for authentication

**Query Parameters:**
- `limit` (optional): Maximum number of calls to return (default: 50)

**Response:**
```json
[
  {
    "id": "uuid",
    "gong_call_id": "string",
    "title": "Call Title",
    "scheduled_at": "2026-01-23T13:00:00",
    "duration_seconds": 3007,
    "call_type": null,
    "product": null
  }
]
```

**Status Codes:**
- `200`: Success
- `401`: Not authenticated
- `403`: Insufficient permissions (not a manager or admin)
- `404`: User not found

**Example:**
```bash
curl -H "X-User-Email: ann@prefect.io" "http://localhost:8000/api/v1/team/calls?limit=20"
```

---

### Calls (Role-Based Access)

#### GET /api/v1/calls

Get calls filtered by user role:
- **Reps**: Only their own calls
- **Managers**: Calls from their team members
- **Admins**: All calls

**Headers:**
- `X-User-Email`: User email for authentication

**Query Parameters:**
- `limit` (optional): Maximum number of calls to return (default: 50, max: 200)

**Response:**
```json
[
  {
    "id": "uuid",
    "gong_call_id": "string",
    "title": "Call Title",
    "scheduled_at": "2026-01-23T13:00:00",
    "duration_seconds": 3007,
    "call_type": null,
    "product": null,
    "created_at": "2026-02-06T03:27:39.925328",
    "processed_at": "2026-02-06T03:27:39.925328",
    "metadata": {}
  }
]
```

**Status Codes:**
- `200`: Success
- `401`: Not authenticated
- `404`: User not found

**Examples:**

Get calls as a rep (only sees own calls):
```bash
curl -H "X-User-Email: trent@prefect.io" http://localhost:8000/api/v1/calls
```

Get calls as a manager (sees team calls):
```bash
curl -H "X-User-Email: ann@prefect.io" http://localhost:8000/api/v1/calls
```

Get calls as admin (sees all calls):
```bash
curl -H "X-User-Email: admin@prefect.io" http://localhost:8000/api/v1/calls
```

---

## Role Matrix

| Endpoint | Admin | Manager | Rep |
|----------|-------|---------|-----|
| `GET /users/me` | ✅ | ✅ | ✅ |
| `GET /team/reps` | ✅ | ✅ | ❌ |
| `GET /team/calls` | ✅ | ✅ | ❌ |
| `GET /calls` | ✅ (all) | ✅ (team) | ✅ (own) |

---

## Implementation Details

### Database Schema

```sql
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'rep');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    role user_role NOT NULL DEFAULT 'rep',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Link reps to their managers
ALTER TABLE speakers ADD COLUMN manager_id UUID REFERENCES users(id);
```

### Middleware

The RBAC middleware (`api/middleware/rbac.py`) provides:

- `get_current_user(request)`: Extract and validate user from request headers
- `require_role(allowed_roles)`: Decorator to enforce role requirements

### Database Queries

The following query functions support RBAC (`db/queries.py`):

- `get_user_by_email(email)`: Get user by email
- `get_user_by_id(user_id)`: Get user by UUID
- `get_managed_reps(manager_email)`: Get reps managed by a manager
- `get_calls_for_user(user_email, role, limit)`: Get calls filtered by role

---

## Testing

Run the test suite:

```bash
python test_rbac_endpoints.py
```

This tests:
- User authentication
- Role-based access control
- Manager-only endpoints
- Call filtering by role
- Error handling (401, 403, 404)

---

## Migration to Production

When deploying to production with Clerk:

1. Update `api/middleware/rbac.py` to extract user from Clerk JWT instead of header
2. Add Clerk webhook to sync user creation/updates to the users table
3. Remove `X-User-Email` header authentication
4. Configure Clerk public metadata to store user role

Example Clerk JWT extraction:

```python
from clerk_backend_api import Clerk

async def get_current_user(request: Request) -> dict[str, Any]:
    # Extract JWT from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]

    # Verify JWT with Clerk
    clerk = Clerk()
    try:
        session = clerk.verify_token(token)
        email = session.user.email_addresses[0].email_address
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user from database
    user = queries.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```
