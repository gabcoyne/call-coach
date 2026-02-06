# API Error Codes Reference

Complete reference for HTTP status codes and error responses.

## HTTP Status Codes

### 200 OK

**Meaning**: Request succeeded

**Example Response**:

```json
{
  "call_id": "1464927526043145564",
  "overall_score": 85,
  "dimensions": {...}
}
```

**Action**: None, request was successful.

---

### 400 Bad Request

**Meaning**: Request is invalid or malformed

**Common Causes**:

- Missing required parameter
- Invalid parameter type
- Invalid parameter value
- Malformed JSON

**Example Response**:

```json
{
  "error": "Invalid parameter",
  "detail": "focus_area must be one of: discovery, product, objections, engagement",
  "parameter": "focus_area",
  "received": "invalid_value"
}
```

**Solution**:

1. Check request format
2. Verify all required parameters present
3. Check parameter types (string, number, etc.)
4. Verify parameter values are in allowed list
5. Ensure JSON is valid (no syntax errors)

**Example Fix**:

```bash
# Wrong:
curl -X POST http://localhost:8001/coaching/analyze-call \
  -d '{"gong_call_id": "abc"}'

# Right:
curl -X POST http://localhost:8001/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d '{"gong_call_id": "1464927526043145564"}'
```

---

### 401 Unauthorized

**Meaning**: Authentication failed or missing

**Common Causes**:

- Missing API key
- Invalid API key
- Expired credentials
- Wrong authentication method

**Example Response**:

```json
{
  "error": "Unauthorized",
  "detail": "Missing or invalid API key"
}
```

**Solution**:

**Local Development** (no auth needed):

```bash
# Should work without auth
curl http://localhost:8001/health
```

**Production** (auth required):

```bash
# Include Bearer token
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.your-company.com/coaching/analyze-call
```

**Getting API Key**:

1. Contact your administrator
2. Check your access credentials
3. Verify key hasn't expired

---

### 403 Forbidden

**Meaning**: Authenticated but not authorized

**Common Causes**:

- Rep trying to view other rep's data
- Insufficient permissions
- Resource outside your scope

**Example Response**:

```json
{
  "error": "Forbidden",
  "detail": "You do not have permission to view this rep's data",
  "user": "sarah@company.com",
  "requested_rep": "tom@company.com"
}
```

**Solution**:

1. Check your role (Rep vs Manager)
2. Verify you're not trying to access restricted data
3. If you should have access, contact manager

**Common Scenario**:

```
Rep Sarah tries to view Tom's call analysis
├─ System checks: Is Sarah a manager?
├─ Answer: No
├─ System denies access
└─ Result: 403 Forbidden
```

---

### 404 Not Found

**Meaning**: Requested resource does not exist

**Common Causes**:

- Wrong call ID
- Call not processed yet
- Rep email not found
- Database entry deleted

**Example Response**:

```json
{
  "error": "Not Found",
  "detail": "Call ID 1464927526043145564 not found in database",
  "resource": "call",
  "identifier": "1464927526043145564"
}
```

**Solution**:

**For Calls**:

1. Verify call ID is correct

   ```bash
   # Check in Gong: https://gong.app.gong.io/calls
   ```

2. Wait for processing (if recent call)

   ```bash
   # Takes 5-30 seconds after call completes
   # Try again in 1 minute
   ```

3. Check if call was successfully ingested

   ```bash
   # Query database
   psql $DATABASE_URL -c "SELECT * FROM calls WHERE gong_call_id = '1464927526043145564'"
   ```

**For Rep Email**:

1. Verify email spelling and case
2. Check rep exists in system
3. Wait for rep's first call to be processed

---

### 422 Unprocessable Entity

**Meaning**: Request is syntactically valid but semantically invalid

**Common Causes**:

- Invalid date format
- Invalid email format
- Out-of-range values
- Invalid filter combination

**Example Response**:

```json
{
  "error": "Validation error",
  "detail": "Invalid date format for date_from",
  "field": "date_from",
  "expected_format": "ISO 8601 (2026-02-05T00:00:00Z)",
  "received": "02/05/2026"
}
```

**Solution**:

**For Dates**:

```bash
# Wrong format:
date_from=02/05/2026

# Right format:
date_from=2026-02-05T00:00:00Z
```

**For Email**:

```bash
# Wrong format:
rep_email=sarah.jones @ company.com

# Right format:
rep_email=sarah.jones@company.com
```

**For Ranges**:

```bash
# Wrong:
{
  "min_score": 150  # Out of range (0-100)
}

# Right:
{
  "min_score": 85   # Valid range (0-100)
}
```

---

### 429 Too Many Requests

**Meaning**: Rate limit exceeded

**Only in Production**: Local development has no rate limits.

**Common Causes**:

- Exceeded 100 requests/minute
- Concurrent request spike
- Polling too frequently

**Example Response**:

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "reset_time": "2026-02-05T15:35:00Z",
  "limit": 100,
  "remaining": 0
}
```

**Headers Included**:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1670000000
Retry-After: 60
```

**Solution**:

1. Wait until `Retry-After` seconds
2. Or wait until `reset_time`
3. Implement exponential backoff
4. Reduce request frequency
5. Contact support if consistently hitting limits

**Implementation Example** (Python):

```python
import time
import requests

def call_api_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

### 500 Internal Server Error

**Meaning**: Server error, something went wrong

**Common Causes**:

- Database connection failure
- Claude API error
- Gong API error
- Unhandled exception

**Example Response**:

```json
{
  "error": "Internal Server Error",
  "detail": "An unexpected error occurred",
  "request_id": "req-abc123def456",
  "timestamp": "2026-02-05T14:30:00Z"
}
```

**Solution**:

**Immediate**:

1. Note the `request_id`
2. Wait 30 seconds
3. Try request again

**Persistent Error**:

1. Check backend status
2. Check database status
3. Check Claude API status (<https://status.anthropic.com>)
4. Check Gong API status
5. Contact support with `request_id`

**Debugging**:

```bash
# Check backend is running
curl http://localhost:8001/health

# Check database
psql $DATABASE_URL -c "SELECT 1"

# Check Claude API
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Check Gong API
curl -H "Authorization: Bearer $GONG_API_SECRET" \
  "$GONG_API_BASE_URL/calls"
```

---

### 503 Service Unavailable

**Meaning**: Server temporarily unavailable

**Common Causes**:

- Maintenance
- Overloaded server
- Database restart
- Deployment in progress

**Example Response**:

```json
{
  "error": "Service Unavailable",
  "detail": "Server is temporarily unavailable. Please try again in a few moments.",
  "retry_after": 300
}
```

**Solution**:

1. Wait the `retry_after` seconds
2. Try request again
3. If persists, contact support

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Error Type",
  "detail": "Human-readable description",
  "request_id": "req-xyz123",
  "timestamp": "2026-02-05T14:30:00Z",
  "additional_field": "context-specific info"
}
```

**Fields**:

- `error`: Error type (always present)
- `detail`: Description of error
- `request_id`: For tracking (always present)
- `timestamp`: When error occurred
- Additional fields: Context-specific (depends on error type)

---

## Common Scenarios

### Scenario 1: Invalid Call ID

```
Request:
  POST /coaching/analyze-call
  Body: {"gong_call_id": "invalid"}

Response: 404 Not Found
{
  "error": "Not Found",
  "detail": "Call ID invalid not found in database",
  "resource": "call"
}

Solution:
  1. Check call ID format (should be 18-19 digits)
  2. Verify call exists in Gong
  3. Wait if call is very recent
  4. Try again with correct ID
```

---

### Scenario 2: Database Connection Failure

```
Request:
  POST /coaching/analyze-call
  Body: {"gong_call_id": "1464927526043145564"}

Response: 500 Internal Server Error
{
  "error": "Internal Server Error",
  "detail": "Database connection failed",
  "request_id": "req-abc123"
}

Solution:
  1. Check DATABASE_URL is set
  2. Verify database is running
  3. Check network connectivity
  4. Try again after 30 seconds
```

---

### Scenario 3: Rate Limited

```
Request 1-100: All succeed
Request 101: Returns 429
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "remaining": 0,
  "reset_time": "2026-02-05T15:35:00Z"
}

Solution:
  1. Wait 60 seconds
  2. Request 102 succeeds
  3. Implement backoff for future requests
```

---

### Scenario 4: Rep Accessing Other Rep's Data

```
Request:
  POST /coaching/rep-insights
  Body: {"rep_email": "tom@company.com"}
  User: Sarah (rep)

Response: 403 Forbidden
{
  "error": "Forbidden",
  "detail": "You do not have permission to view this data",
  "user": "sarah@company.com",
  "requested": "tom@company.com"
}

Solution:
  1. Verify you're trying to view your own data
  2. If you should access this data, ask to be upgraded to Manager
  3. Contact your manager or administrator
```

---

## Testing Error Handling

### Python Example

```python
import requests
import json
import time

def call_api_safe(url, data, max_retries=3):
    """Make API call with error handling"""

    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            # Check for errors
            if response.status_code == 200:
                return response.json()

            elif response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue

            elif response.status_code == 404:
                # Not found - don't retry
                raise ValueError(f"Resource not found: {response.json()}")

            elif response.status_code in [400, 422]:
                # Validation error - don't retry
                raise ValueError(f"Invalid request: {response.json()}")

            elif response.status_code == 500:
                # Server error - retry
                print(f"Server error. Retrying... (attempt {attempt+1}/{max_retries})")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue

            else:
                raise Exception(f"Unexpected status {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"Timeout. Retrying... (attempt {attempt+1}/{max_retries})")
            time.sleep(2 ** attempt)
            continue

        except requests.exceptions.ConnectionError:
            print(f"Connection error. Retrying... (attempt {attempt+1}/{max_retries})")
            time.sleep(2 ** attempt)
            continue

    raise Exception(f"Max retries exceeded for {url}")

# Usage
try:
    result = call_api_safe(
        "http://localhost:8001/coaching/analyze-call",
        {"gong_call_id": "1464927526043145564"}
    )
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
```

---

## Support

Having issues not covered here?

1. Check [Troubleshooting Guide](./README.md)
2. Review [API Documentation](../api/endpoints.md)
3. Contact support with `request_id` from error response

---

**Still stuck?** Include your `request_id` when contacting support for faster resolution.
