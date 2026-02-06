# Testing Role-Aware MCP Tools in Claude Desktop

## Prerequisites

1. MCP server is running:

   ```bash
   uv run python -m coaching_mcp.server
   ```

2. Claude Desktop is configured to connect to the MCP server

3. Database has some analyzed calls with role metadata

## Test Cases

### Test 1: Auto-Detect Role in Call Analysis

**Prompt:**

```
Analyze call 895209263795581011 and tell me what role was used for the evaluation.
```

**Expected Response:**

- Should show analysis results
- Should include a field showing `evaluated_as_role` (ae, se, or csm)
- Should auto-detect based on primary speaker's role

**Verification:**

- Look for "evaluated as: [role]" in the response
- Verify it matches the primary speaker's actual role

---

### Test 2: Manual Role Override

**Prompt:**

```
Analyze call 895209263795581011 but evaluate it as if it were an SE (Sales Engineer) call,
even if the primary speaker was an AE.
```

**Expected Response:**

- Should analyze the call using SE rubric
- `evaluated_as_role` should be "se"
- Feedback should be SE-focused (technical communication, demos, etc.)

**Verification:**

- Response should explicitly mention using SE evaluation criteria
- Coaching feedback should be appropriate for SE role

---

### Test 3: Search for Role-Specific Calls

**Prompt:**

```
Show me the top 5 highest-scoring calls by Sales Engineers (SEs) from the last month.
```

**Expected Response:**

- Should return only calls evaluated with SE rubric
- Should show scores and call titles
- Should be sorted by score descending

**Verification:**

- All returned calls should have been evaluated as SE calls
- Check that results actually have high scores

---

### Test 4: Compare Rep to Same Role Peers

**Prompt:**

```
Get learning insights for [rep-email] focusing on discovery skills.
Make sure you're comparing them only to other reps in the same role.
```

**Expected Response:**

- Should show rep's detected role
- Should include a note about "comparing to [Role] peers only"
- Exemplar moments should be from same role

**Verification:**

- Response should explicitly state role comparison
- Look for "AE to AE" or "SE to SE" language
- Behavioral examples should be role-appropriate

---

### Test 5: Rep Performance Insights (Role-Aware Benchmarking)

**Prompt:**

```
Get performance insights for [rep-email] over the last 30 days.
Show me how they compare to their role cohort.
```

**Expected Response:**

- Should show rep info including role
- Skill gaps should be compared to same role only
- Team averages should be role-filtered

**Verification:**

- Look for role field in rep_info
- Verify team comparisons make sense for that role
- Check that target scores are reasonable for the role

---

### Test 6: Cross-Role Search Verification

**Prompt:**

```
Find discovery calls by AEs with high scores, then find discovery calls by SEs with high scores.
Compare the types of feedback each group received.
```

**Expected Response:**

- Should return two separate result sets
- AE calls should have AE-focused feedback (rapport, closing, etc.)
- SE calls should have SE-focused feedback (technical depth, demos, etc.)

**Verification:**

- Verify different feedback themes for different roles
- Ensure role filtering is working correctly
- Check that scores are comparable within role but not across roles

---

## Common Issues

### Issue: "No role found, defaulting to AE"

**Cause:** Speaker doesn't have role assigned in staff_roles table
**Fix:** Assign role via admin interface or SQL:

```sql
INSERT INTO staff_roles (email, role)
VALUES ('rep@prefect.io', 'se');
```

### Issue: "No calls found with role filter"

**Cause:** Calls analyzed before role-aware system was implemented
**Fix:** Re-analyze calls to populate metadata->>'rubric_role':

```python
analyze_call(call_id, force_reanalysis=True)
```

### Issue: "Comparison shows no peers"

**Cause:** Not enough calls from same role in database
**Fix:** Either:

1. Analyze more calls from that role
2. Use a longer time period for comparison
3. Check that role assignments are correct

---

## Validation Checklist

After running tests, verify:

- [ ] Role detection works automatically
- [ ] Manual role override works
- [ ] Search filters by role correctly
- [ ] Learning insights compare same role only
- [ ] Rep insights benchmark against same role
- [ ] All responses include role information
- [ ] Feedback is appropriate for detected role
- [ ] No cross-role contamination in comparisons

---

## Example Session Transcript

```
Human: Analyze call 895209263795581011

Claude: I'll analyze this call for you.

[Analysis results...]

The call was evaluated as an AE (Account Executive) call. The primary speaker
was [name] who spoke for 65% of the call. Here are the key findings:

- Discovery Score: 72/100 (compared to AE avg of 68)
- Objection Handling: 85/100 (top 15% of AEs)
- [more results...]
```
