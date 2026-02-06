# Gong Client Implementation Audit

**Date**: 2026-02-04
**OpenAPI Spec Version**: V2 (OpenAPI 3.0.1)
**Spec Source**: <https://gong.app.gong.io/ajax/settings/api/documentation/specs?version=>

## Summary

Our `gong/client.py` implementation has **critical mismatches** with the official Gong API v2 OpenAPI specification. The most significant issue is the transcript retrieval endpoint which doesn't exist in the official API.

## Critical Issues

### 1. ❌ Transcript Endpoint - DOES NOT EXIST

**Our Implementation**:

```python
# Line 154 in gong/client.py
def get_transcript(self, call_id: str) -> GongTranscript:
    response = self._make_request("GET", f"/calls/{call_id}/transcript")
```

**Official Spec**:

```http
POST /v2/calls/transcript
Content-Type: application/json

{
  "filter": {
    "fromDateTime": "2018-02-17T02:30:00-08:00",
    "toDateTime": "2018-02-19T02:30:00-08:00",
    "callIds": ["7782342274025937895"]
  },
  "cursor": "optional_pagination_cursor"
}
```

**Response Structure**:

```json
{
  "requestId": "4al018gzaztcr8nbukw",
  "records": {...},
  "callTranscripts": [
    {
      "callId": "7782342274025937895",
      "transcript": [
        {
          "speakerId": "6432345678555530067",
          "topic": "Objections",
          "sentences": [
            {
              "start": 460230,  // milliseconds from call start
              "end": 462343,
              "text": "No wait, I think we should check that out first."
            }
          ]
        }
      ]
    }
  ]
}
```

**Impact**:

- **High** - This endpoint doesn't exist. GET `/calls/{id}/transcript` is **not in the official spec**.
- Our transcript retrieval will fail in production against real Gong API
- Data structure returned is completely different:
  - Spec uses `Monologue` (speaker + topic + sentences) structure
  - Our implementation expects flat segments with start/duration
  - Timestamps in spec are absolute milliseconds, not duration-based

**Fix Required**: Rewrite `get_transcript()` to use POST `/v2/calls/transcript` with proper filter body

---

### 2. ⚠️ Missing /v2 Prefix on All Endpoints

**Our Implementation**:

```python
# Line 105
response = self._make_request("GET", f"/calls/{call_id}")

# Line 204
response = self._make_request("GET", "/calls", params=params)

# Line 252
response = self._make_request("GET", "/calls/search", params=params)
```

**Official Spec**:

- All endpoints are under `/v2/` prefix: `/v2/calls`, `/v2/calls/{id}`, etc.

**Impact**:

- **Medium** - The `base_url` in our config includes `/v2` already (see `.env.example` line 4: `GONG_API_BASE_URL=https://api.gong.io/v2`)
- If config is correct, this works. But it's brittle and confusing.

**Fix Required**: Either:

1. Remove `/v2` from `GONG_API_BASE_URL` and add it to all endpoint paths, OR
2. Document clearly that base URL must include `/v2`

---

### 3. ❌ Search Endpoint - DOES NOT EXIST

**Our Implementation**:

```python
# Line 252 in gong/client.py
def search_calls(self, query: str, ...) -> list[str]:
    response = self._make_request("GET", "/calls/search", params=params)
```

**Official Spec**:

- No `/v2/calls/search` endpoint exists
- The spec provides GET `/v2/calls` with filters (fromDateTime, toDateTime, workspaceId)
- No text search capability documented

**Impact**:

- **High** - This endpoint doesn't exist. Calls to `search_calls()` will fail with 404.

**Fix Required**: Either:

1. Remove `search_calls()` method entirely, OR
2. Implement using GET `/v2/calls` with date filters (not text search)

---

## Working Implementations

### ✅ Get Specific Call

**Our Implementation**:

```python
# Line 105
response = self._make_request("GET", f"/calls/{call_id}")
```

**Official Spec**:

```http
GET /v2/calls/{id}
```

**Status**: ✅ **Correct** (assuming base_url includes `/v2`)

**Response Schema Match**:

- ✅ `call.id`, `call.title`, `call.scheduled`, `call.started`, `call.duration`
- ✅ `call.participants` → our `GongSpeaker` mapping
- ✅ `call.direction`, `call.system`, `call.scope`, `call.media`

---

### ✅ List Calls

**Our Implementation**:

```python
# Line 204
response = self._make_request("GET", "/calls", params={
    "fromDateTime": from_date,
    "toDateTime": to_date,
    "workspaceId": workspace_id,
    "limit": limit
})
```

**Official Spec**:

```http
GET /v2/calls?fromDateTime=...&toDateTime=...&workspaceId=...&cursor=...
```

**Status**: ✅ **Mostly Correct**

**Issues**:

- ⚠️ `limit` parameter is **not in the spec** - pagination uses `cursor` instead
- ⚠️ Missing `cursor` support for pagination (spec returns `records.cursor` for next page)

**Fix Required**: Remove `limit` param, add `cursor` support

---

## Authentication

**Our Implementation**:

```python
# Line 34
self.client = httpx.Client(
    base_url=self.base_url,
    auth=(self.api_key, ""),  # Basic auth with API key as username
    ...
)
```

**Official Spec**:

- `securitySchemes: null` in OpenAPI spec (not documented)
- Documentation states: "When accessed through a Bearer token authorization method, this endpoint requires the scope 'api:calls:read:basic'"

**Status**: ⚠️ **Unknown**

Our implementation uses **Basic Auth** (API key as username, empty password). The spec documentation mentions **Bearer token** with scopes. The credentials provided by the user:

- Access Key: `UQ4SK2LPUPBCFN7QHVLH6JRYEFSXEQML`
- Secret Key (JWT): `eyJhbGciOiJIUzI1NiJ9...`

**Testing Required**: Verify which auth method works with real Gong API

---

## Data Model Mismatches

### Transcript Structure

**Our GongTranscriptSegment**:

```python
class GongTranscriptSegment:
    speaker_id: str
    start_time: int  # assumed to be milliseconds
    duration: int    # duration in milliseconds
    text: str
    sentiment: str | None
```

**Official Spec (Monologue + Sentence)**:

```typescript
{
  speakerId: string
  topic: string  // "Objections", "Introduction", etc.
  sentences: [
    {
      start: number  // absolute time in ms from call start
      end: number    // absolute time in ms
      text: string
    }
  ]
}
```

**Mismatches**:

- ❌ We use `start_time` + `duration`, spec uses `start` + `end`
- ❌ We have flat segments, spec groups by speaker `Monologue` with topic
- ❌ We expect `sentiment`, spec doesn't provide it
- ❌ Spec groups sentences by topic, we don't capture topics

---

## Recommended Actions

### Immediate (Blocking Production)

1. **Rewrite `get_transcript()`**:

   ```python
   def get_transcript(self, call_id: str) -> GongTranscript:
       """Fetch transcript using POST /v2/calls/transcript endpoint."""
       response = self._make_request(
           "POST",
           "/calls/transcript",  # assuming base_url has /v2
           json_data={
               "filter": {
                   "callIds": [call_id],
                   # Must provide date range - use wide range or track call date
                   "fromDateTime": "2020-01-01T00:00:00Z",
                   "toDateTime": "2030-01-01T00:00:00Z"
               }
           }
       )

       # Parse response.callTranscripts[0].transcript
       # Convert Monologue structure to our GongTranscript
   ```

2. **Update `GongTranscriptSegment` model**:

   - Change `start_time` + `duration` to `start` + `end`
   - Add `topic` field
   - Remove `sentiment` (not in API response)
   - Update parsing logic in `flows/process_new_call.py`

3. **Remove or fix `search_calls()`**:
   - Either delete it entirely, or
   - Rename to `list_calls_by_date()` and use GET `/v2/calls`

### Medium Priority

4. **Fix `list_calls()` pagination**:

   - Remove `limit` parameter
   - Add `cursor` parameter for pagination
   - Update return type to include cursor for next page

5. **Clarify `/v2` prefix handling**:

   - Document in README that `GONG_API_BASE_URL` must include `/v2`
   - Or refactor to add `/v2` explicitly in endpoint paths

6. **Test authentication**:
   - Verify if Basic Auth works or if Bearer token is required
   - Test with actual Gong API using provided credentials

### Nice-to-Have

7. **Generate client from OpenAPI spec**:

   - Use `openapi-python-client` or similar to auto-generate
   - Ensures perfect alignment with official API

8. **Add extensive endpoint**:
   - Spec has `/v2/calls/extensive` for detailed call data
   - Consider adding `get_call_extensive()` method

---

## Testing Checklist

Before Phase 3 (Webhook Processing), verify:

- [ ] `get_call(call_id)` works against real Gong API
- [ ] `get_transcript(call_id)` works with new POST endpoint
- [ ] `list_calls(from_date, to_date)` returns calls correctly
- [ ] Pagination with `cursor` works for large result sets
- [ ] Webhook signature verification works (test in `gong/webhook.py`)
- [ ] Transcript parsing correctly handles Monologue → Sentence structure
- [ ] Database schema in `db/schema.sql` matches actual Gong data structure

---

## Reference

- **OpenAPI Spec**: Saved to `.openspec/gong-api-v2-openapi.json`
- **Official Docs**: <https://help.gong.io/docs/what-the-gong-api-provides>
- **Endpoint Discovery**: <https://gong.app.gong.io/ajax/settings/api/documentation/specs?version=>
- **Authentication**: Test both Basic Auth and Bearer Token approaches

---

## Sources

- [Gong API Overview](https://help.gong.io/docs/what-the-gong-api-provides)
- [Gong API Developer Guide 2026](https://www.claap.io/blog/gong-api)
- [gong-api-client (Node.js) - Reference Implementation](https://github.com/aaronsb/gong-api-client)
- [gong-rs (Rust) - Generated from OpenAPI](https://github.com/cedricziel/gong-rs)
