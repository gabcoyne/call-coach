# Role-Aware MCP Tools Implementation Summary

## Overview
Updated all MCP coaching tools to support role-aware evaluation and comparison. Reps are now evaluated against role-specific rubrics (AE, SE, CSM) and compared only to peers in the same role.

## Changes Made

### 1. analyze_call.py
**Location:** `coaching_mcp/tools/analyze_call.py`

**Changes:**
- Added `role` parameter (optional) to allow manual role override
- Auto-detects speaker role using `detect_speaker_role()` from analysis engine
- Passes detected role to evaluation engine
- Returns `evaluated_as_role` field in response showing which rubric was used

**Usage:**
```python
# Auto-detect role
result = analyze_call("call-id")
print(result['rep_analyzed']['evaluated_as_role'])  # 'ae', 'se', or 'csm'

# Override role
result = analyze_call("call-id", role="se")  # Force SE rubric
```

### 2. get_learning_insights.py
**Location:** `coaching_mcp/tools/get_learning_insights.py`

**Changes:**
- Tool already had role filtering implemented in the backend
- Updated tool description to explicitly mention role-aware comparison
- Tool now prominently shows it compares "AE to AE, SE to SE, CSM to CSM"

**Behavior:**
- Auto-detects rep's role from staff_roles table
- Filters top performer comparisons to same role only
- Response includes `rep_role`, `role_display`, and `comparison_note` fields

### 3. search_calls.py
**Location:** `coaching_mcp/tools/search_calls.py`

**Changes:**
- Added `role` parameter to filter calls by speaker role
- Searches `coaching_sessions.metadata->>'rubric_role'` field
- Allows finding examples from specific role cohorts

**Usage:**
```python
# Find high-scoring SE calls
se_calls = search_calls(role="se", min_score=80)

# Find AE discovery calls
ae_calls = search_calls(role="ae", call_type="discovery")
```

### 4. get_rep_insights.py
**Location:** `coaching_mcp/tools/get_rep_insights.py`

**Changes:**
- Updated skill gap comparison to be role-aware
- Team averages now filtered by `metadata->>'rubric_role'`
- Compares rep only to team members evaluated with same role rubric

**Behavior:**
- Detects rep's role from speakers table
- Skill gaps show comparison to same-role peers only
- Fair benchmarking: AEs vs AEs, SEs vs SEs, CSMs vs CSMs

### 5. server.py
**Location:** `coaching_mcp/server.py`

**Changes:**
- Updated all tool descriptions to mention role-aware features
- Added "ROLE-AWARE" prefix to relevant tools
- Documented role parameter and evaluated_as_role response field
- Updated examples to show role usage

## Testing

### Test Results
All tests passed successfully:

```
✅ Role Detection Logic - Correctly detects speaker role from call
✅ Analyze Call with Auto Detection - Auto-detects and uses correct rubric
✅ Analyze Call with Role Override - Respects manual role parameter
✅ Search Calls with Role Filter - Filters by rubric_role correctly
```

**Test File:** `test_role_aware_tools.py`

### Example Output
```python
# Analyze call with auto-detection
result = analyze_call("895209263795581011")
# Returns:
{
  "rep_analyzed": {
    "name": "John Doe",
    "email": "john@prefect.io",
    "role": "ae",
    "evaluated_as_role": "ae"  # ← Shows which rubric was used
  },
  "scores": {...}
}

# Search for SE calls
se_calls = search_calls(role="se", limit=10)
# Returns calls evaluated with SE rubric only
```

## Benefits

### 1. Fair Evaluation
- AEs judged on selling skills, SEs on technical communication, CSMs on relationship management
- No more comparing apples to oranges

### 2. Relevant Comparisons
- Reps only compared to peers in same role
- Learning insights show examples from same role
- Skill gaps benchmarked against appropriate cohort

### 3. Flexibility
- Auto-detection handles most cases
- Manual override available when needed
- Search can filter by role for targeted analysis

## Integration Points

### Database Fields Used
- `staff_roles.role` - Primary role assignment
- `speakers.role` - Speaker role on call
- `coaching_sessions.metadata->>'rubric_role'` - Role used for evaluation

### Analysis Engine Integration
- Uses `detect_speaker_role()` from `analysis/engine.py`
- Role detection logic: @prefect.io email → highest talk time → staff_roles lookup
- Defaults to 'ae' if no role assigned

## Future Enhancements

### Potential Improvements
1. Add role filter to opportunity-level analysis
2. Create role-specific coaching templates
3. Build role cohort performance dashboards
4. Add cross-role collaboration metrics (AE+SE teamwork)

### Known Issues
- Pre-existing issue in analyze_call_tool calling pattern (not related to role changes)
- Some calls may not have role metadata if analyzed before this update (will re-analyze on next run)

## Documentation Updates

### Tool Descriptions
All MCP tool descriptions now mention:
- Role-aware evaluation/comparison
- Auto-detection vs manual override
- Which fields show role information
- Examples using role parameters

### Response Fields
New fields in responses:
- `evaluated_as_role` - Role rubric used for evaluation
- `rep_role` - Detected role of rep being analyzed
- `comparison_note` - Explanation of role-filtered comparison

## Deliverables

✅ All MCP tools are role-aware
✅ Tool schemas updated with role parameters
✅ Documentation updated with role-aware features
✅ Test suite created and passing
✅ Integration with existing role detection logic

## Testing in Claude Desktop

To test in Claude Desktop:

1. Start the MCP server:
   ```bash
   uv run python -m coaching_mcp.server
   ```

2. In Claude Desktop, try:
   ```
   Analyze call 895209263795581011 and show me what role was used for evaluation.

   Search for high-scoring SE calls.

   Compare this rep to other AEs (or SEs, CSMs).
   ```

3. Verify responses include role information:
   - `evaluated_as_role` field in analyze_call
   - Role filtering working in search_calls
   - Same-role comparisons in get_learning_insights

---

**Implementation Date:** 2026-02-05
**Task:** batch-2-mcp-tools
**Status:** ✅ Complete
