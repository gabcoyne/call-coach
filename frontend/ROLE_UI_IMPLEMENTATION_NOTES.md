# Role-Based Coaching UI Implementation Notes

## Completed Tasks (Tasks 8-10)

### Task 8 & 9: Role Assignment UI with Bulk Operations ✅

**Files Created:**

- `frontend/app/settings/roles/page.tsx` - Manager-only role assignment page
- `frontend/components/RoleAssignmentTable.tsx` - Full-featured table component

**Features Implemented:**

- Manager-only authorization guard (redirects non-managers to 403)
- Staff list with current role assignments
- Search by name or email
- Filter by role (all/AE/SE/CSM/unassigned)
- Individual role assignment via dropdown
- Bulk selection with checkboxes
- Bulk role assignment for multiple staff members
- Last updated timestamp with assigned_by tooltip
- Success/error toast notifications
- Responsive design for mobile/tablet/desktop

**Backend APIs Used:**

- `GET /api/settings/roles` - List all staff with roles
- `PUT /api/settings/roles/[email]` - Update individual role
- `DELETE /api/settings/roles/[email]` - Remove role assignment

### Task 10: Call Detail Page Rubric Badge ✅

**Files Created:**

- `frontend/components/RubricBadge.tsx` - Role-specific rubric indicator

**Files Modified:**

- `frontend/types/coaching.ts` - Added `evaluated_as_role` to `RepAnalyzed` interface
- `frontend/app/calls/[callId]/CallAnalysisViewer.tsx` - Added RubricBadge display

**Features Implemented:**

- Colored badge showing which rubric was used (AE=blue, SE=green, CSM=purple)
- Tooltip with full role name and dimension breakdown
- Displays only when `rep_analyzed.evaluated_as_role` is present in API response
- Positioned prominently above Performance Scores section

## Remaining Tasks (Tasks 11-12)

### Task 11: Rep Dashboard Role-Specific Metrics ⚠️

**Status:** Requires backend data integration

**Required Changes:**

1. **API Enhancement Needed:**

   - `GET /api/coaching/rep-insights` should return the rep's assigned role
   - Include role-specific dimension weights in response

2. **Frontend Changes:**

   ```typescript
   // In frontend/app/dashboard/[repEmail]/page.tsx

   // 1. Fetch rep role from staff_roles table
   const { data: repRole } = useSWR(`/api/settings/roles/${repEmail}`);

   // 2. Load role-specific rubric config
   const ROLE_WEIGHTS = {
     ae: { discovery: 0.30, objection_handling: 0.25, ... },
     se: { technical_accuracy: 0.35, architecture_fit: 0.30, ... },
     csm: { value_realization: 0.30, risk_identification: 0.25, ... }
   };

   // 3. Emphasize high-weight dimensions in UI
   // - Sort dimensions by weight (highest first)
   // - Use larger cards or highlight color for top dimensions
   // - Add weight percentage badges: "Discovery: 30%"
   // - De-emphasize or hide dimensions not in rep's rubric

   // 4. Add section header with role context
   <h2>Performance by {role.toUpperCase()} Standards</h2>
   ```

3. **Visual Design:**
   - Top 3 dimensions (by weight) should be larger or highlighted
   - Add weight percentage indicators next to each dimension score
   - Filter out dimensions that aren't in the role's rubric
   - Consider role-specific color themes (matching RubricBadge)

### Task 12: Opportunity Insights Role-Aware Aggregation ⚠️

**Status:** Requires backend MCP tool updates

**Required Changes:**

1. **Backend MCP Tool:** `coaching_mcp/tools/analyze_opportunity.py`

   ```python
   # 1. Detect roles of all Prefect speakers on opportunity calls
   speakers_with_roles = []
   for call in opportunity_calls:
       prefect_speakers = detect_prefect_speakers(call.id)
       for speaker in prefect_speakers:
           role = get_staff_role(speaker.email)
           speakers_with_roles.append({
               "call_id": call.id,
               "speaker": speaker,
               "role": role or "ae",
               "rubric_used": role or "ae"
           })

   # 2. Group calls by speaker role
   calls_by_role = {
       "ae": [c for c in speakers_with_roles if c["role"] == "ae"],
       "se": [c for c in speakers_with_roles if c["role"] == "se"],
       "csm": [c for c in speakers_with_roles if c["role"] == "csm"]
   }

   # 3. Generate separate coaching summaries per role
   insights = {
       "ae_performance": analyze_role_performance(calls_by_role["ae"], "ae"),
       "se_performance": analyze_role_performance(calls_by_role["se"], "se"),
       "csm_performance": analyze_role_performance(calls_by_role["csm"], "csm")
   }
   ```

2. **Frontend Component:** `frontend/components/opportunities/OpportunityInsights.tsx`

   ```typescript
   // 1. Update interface to support role-grouped insights
   interface OpportunityInsights {
     ae_performance?: RolePerformance;
     se_performance?: RolePerformance;
     csm_performance?: RolePerformance;
   }

   interface RolePerformance {
     calls_analyzed: number;
     avg_score: number;
     top_strengths: string[];
     areas_for_improvement: string[];
     recommendations: string[];
   }

   // 2. Render separate sections per role
   <div className="space-y-6">
     {insights.ae_performance && (
       <RolePerformanceSection
         role="ae"
         performance={insights.ae_performance}
       />
     )}
     {insights.se_performance && (
       <RolePerformanceSection
         role="se"
         performance={insights.se_performance}
       />
     )}
   </div>

   // 3. Add role badges to call timeline
   <OpportunityTimeline calls={calls}>
     {calls.map(call => (
       <CallTimelineItem key={call.id}>
         <RubricBadge role={call.rubric_used} />
         {/* ... rest of call details */}
       </CallTimelineItem>
     ))}
   </OpportunityTimeline>
   ```

## Testing Checklist

### Task 8 & 9: Role Assignment UI ✅

- [x] Manager can access `/settings/roles` page
- [x] Non-manager redirected to 403
- [ ] Search filters staff list correctly
- [ ] Role filter works (all/AE/SE/CSM/unassigned)
- [ ] Individual role assignment updates database
- [ ] Bulk selection toggles correctly
- [ ] Bulk assignment updates multiple staff members
- [ ] Toast notifications appear on success/error
- [ ] Last updated tooltip shows assigned_by
- [ ] Responsive on mobile devices

### Task 10: Rubric Badge ✅

- [x] Badge displays on call detail page
- [ ] Badge shows correct role (AE/SE/CSM)
- [ ] Badge colors match role (blue/green/purple)
- [ ] Tooltip shows dimension breakdown
- [ ] Badge only appears when evaluated_as_role is present

### Task 11: Rep Dashboard (Pending)

- [ ] Dashboard fetches rep's assigned role
- [ ] Role-specific dimensions are emphasized
- [ ] Dimension weights displayed (e.g., "Discovery: 30%")
- [ ] Section header shows role context
- [ ] Dimensions not in rubric are de-emphasized or hidden

### Task 12: Opportunity Insights (Pending)

- [ ] Calls grouped by speaker role
- [ ] Separate performance sections per role
- [ ] Role badges on call timeline
- [ ] Role-specific recommendations generated

## API Endpoints Reference

### Existing Endpoints

- `GET /api/settings/roles` - List all staff with role assignments
- `PUT /api/settings/roles/[email]` - Update staff role
- `DELETE /api/settings/roles/[email]` - Remove staff role
- `GET /api/coaching/analyze-call?call_id=...` - Get call analysis (includes evaluated_as_role)

### Needed Endpoints (for Tasks 11-12)

- `GET /api/coaching/rep-insights?rep_email=...` should include:

  ```json
  {
    "rep_info": {
      "assigned_role": "ae",
      "rubric_weights": {
        "discovery": 0.3,
        "objection_handling": 0.25
      }
    }
  }
  ```

- `GET /api/opportunities/[id]/insights` should include:

  ```json
  {
    "insights": {
      "ae_performance": { ... },
      "se_performance": { ... }
    }
  }
  ```

## Rubric Configuration Reference

**AE (Account Executive) Dimensions:**

- Discovery & Qualification: 30%
- Objection Handling: 25%
- Product Positioning: 20%
- Relationship Building: 15%
- Call Control: 10%

**SE (Sales Engineer) Dimensions:**

- Technical Accuracy: 35%
- Architecture Fit: 30%
- Problem-Solution Mapping: 20%
- Technical Objection Resolution: 10%
- Collaboration with AE: 5%

**CSM (Customer Success Manager) Dimensions:**

- Value Realization: 30%
- Risk Identification: 25%
- Relationship Depth: 20%
- Expansion Opportunity: 15%
- Product Adoption: 10%

## Next Steps

1. **Immediate (can be done now):**

   - Test role assignment UI end-to-end with real manager account
   - Verify rubric badge displays correctly on analyzed calls
   - Test bulk assignment with 10+ staff members

2. **Short-term (requires backend work):**

   - Add rep role to rep-insights API response
   - Implement dashboard dimension emphasis based on role
   - Test dashboard shows different metrics for AE vs SE vs CSM

3. **Medium-term (requires MCP tool updates):**

   - Update analyze_opportunity MCP tool to group by role
   - Modify opportunity insights component for role sections
   - Test opportunity with mixed AE+SE calls shows separate evaluations

4. **Long-term (nice-to-have):**
   - Add role-based coaching templates
   - Implement role comparison reports (AEs vs SEs vs CSMs)
   - Add role-specific leaderboards
