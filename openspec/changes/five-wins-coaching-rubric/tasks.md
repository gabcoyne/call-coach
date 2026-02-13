# Five Wins Coaching Rubric - Implementation Tasks

## Phase 1: Core Rubric & Models

### Task 1.1: Create Five Wins Unified Rubric ✅

**File:** `analysis/rubrics/five_wins_unified.py`

Create the single source of truth for Five Wins definitions:

- All five wins with exit criteria
- Discovery topics per win
- Call type to primary win mapping
- Weighting (Business 35%, Technical 25%, Security 15%, Commercial 15%, Legal 10%)

**Acceptance:**

- [x] All five wins defined with exit criteria matching SKO deck
- [x] Champion criteria included (incentive, influence, information)
- [x] Business case questions included (why change, why prefect, why now)
- [x] Call type mapping complete

### Task 1.2: Create Pydantic Models ✅

**File:** `analysis/models/five_wins.py`

Create data models for evaluation results:

- `WinProgress` base model
- `BusinessWinEvaluation` with champion assessment
- `TechnicalWinEvaluation` with POC tracking
- `SecurityWinEvaluation` with timeline tracking
- `CommercialWinEvaluation` with exec sponsor tracking
- `LegalWinEvaluation` with terms tracking
- `FiveWinsEvaluation` composite model
- `CoachingOutput` final output model

**Acceptance:**

- [x] All models have proper validation
- [x] Models are JSON serializable
- [x] Tests pass for model creation

---

## Phase 2: Prompt Engineering

### Task 2.1: Create Five Wins Prompt ✅

**File:** `analysis/prompts/five_wins_prompt.py`

Create the unified prompt that:

- Defines Five Wins without methodology jargon
- Requests structured JSON output
- Emphasizes single action item
- Requires timestamp references

**Acceptance:**

- [x] Prompt produces valid JSON output
- [x] No mentions of SPICED, Challenger, Sandler, MEDDIC (only in negative instructions)
- [x] Output includes narrative, wins assessment, and single action

### Task 2.2: Test Prompt with Sample Transcripts ✅

**File:** `tests/unit/analysis/test_five_wins_prompt.py`

Test the prompt against known call transcripts:

- Discovery call should focus on Business Win
- Technical call should focus on Technical Win
- Verify action items are specific and actionable

**Acceptance:**

- [x] Prompt produces consistent output format (15 tests passing)
- [x] Call type affects primary win focus
- [x] Weights sum to 100 verified

---

## Phase 3: Consolidation Layer

### Task 3.1: Narrative Generator ✅

**File:** `analysis/consolidation/narrative_generator.py`

Create function to synthesize evaluation into narrative:

- Identify wins addressed vs missed
- Prioritize most important insight
- Generate 2-3 sentence summary

**Acceptance:**

- [x] Narratives are concise and actionable
- [x] No generic platitudes
- [x] References specific wins by name

### Task 3.2: Action Selector ✅

**File:** `analysis/consolidation/action_selector.py`

Create function to select single best action:

- Priority: unblock > advance primary > prevent risk
- Must tie to specific win
- Must tie to specific call moment

**Acceptance:**

- [x] Returns exactly ONE action
- [x] Action references a win
- [x] Action includes timestamp context

### Task 3.3: Moment Linker ✅

**File:** `analysis/consolidation/moment_linker.py`

Create function to link actions to call moments:

- Find relevant moment for the action
- Prefer moments showing missed opportunities
- Include timestamp and speaker

**Acceptance:**

- [x] Moments are correctly linked
- [x] Timestamps are accurate
- [x] Speaker attribution is correct

---

## Phase 4: Engine Integration

### Task 4.1: Update Analysis Engine ✅

**File:** `analysis/engine.py`

Modify `get_or_create_coaching_session` to:

- Use Five Wins prompt when feature flag enabled
- Run consolidation layer on results
- Store new output format

**Acceptance:**

- [x] Feature flag `USE_FIVE_WINS_UNIFIED` added to config
- [x] `run_five_wins_unified_analysis()` function added
- [x] `_apply_consolidation_layer()` function for fallback

### Task 4.2: Update analyze_call_tool ✅

**File:** `coaching_mcp/tools/analyze_call.py`

Modify tool to return new output structure:

- Add `narrative` field
- Add `wins_addressed` and `wins_missed`
- Add `primary_action` object
- Keep old fields for backward compatibility

**Acceptance:**

- [x] API response includes new fields when feature flag enabled
- [x] Old fields still populated
- [x] Frontend doesn't break
- [x] `_add_fallback_unified_output()` for graceful degradation

---

## Phase 5: Frontend Updates

### Task 5.1: Update CoachingOutput Types ✅

**File:** `frontend/types/coaching.ts`

Add TypeScript types for new output:

- `PrimaryAction` interface
- `CallMoment` interface
- Updated `AnalyzeCallResponse`

**Acceptance:**

- [x] Types compile without errors
- [x] Types match backend models

### Task 5.2: Update CallAnalysisViewer ✅

**File:** `frontend/app/calls/[callId]/CallAnalysisViewer.tsx`

Modify UI to:

- Show narrative prominently at top
- Display Five Wins progress visualization
- Show single Primary Action prominently
- Collapse detailed breakdowns by default

**Acceptance:**

- [x] Narrative is first thing visible (when Five Wins Unified output present)
- [x] Primary Action is clearly displayed
- [x] UI doesn't overwhelm with detail

**New Components Created:**

- `frontend/components/coaching/NarrativeSummary.tsx`
- `frontend/components/coaching/PrimaryActionCard.tsx`

### Task 5.3: Create Five Wins Progress Component ✅

**File:** `frontend/components/coaching/FiveWinsScoreCard.tsx`

Create visual showing progress on each win:

- Five horizontal bars or cards
- Color coded by progress (red/yellow/green)
- Click to expand details

**Acceptance:**

- [x] All five wins visible at glance
- [x] Progress is clear
- [x] Details available on demand

---

## Phase 6: Testing & Migration

### Task 6.1: Pipeline Unit Tests ✅

**File:** `tests/unit/analysis/test_five_wins_pipeline.py`

Unit tests for the pipeline components:

- Prompt generation produces expected structure
- Consolidation layer works correctly
- Pydantic models validate and serialize correctly

**Acceptance:**

- [x] All 16 pipeline tests pass
- [x] Output format validated through model tests

### Task 6.2: A/B Test Setup ✅

**File:** `analysis/ab_testing.py`

Create A/B testing infrastructure:

- Route percentage of calls to new pipeline
- Log which pipeline was used
- Collect comparison metrics

**Acceptance:**

- [x] Can route traffic by percentage via `should_use_unified_pipeline()`
- [x] Pipeline choice is logged via `log_pipeline_usage()`
- [x] Metrics are captured in `ab_test_results` table

### Task 6.3: Migration Script ✅

**File:** `scripts/migrate_to_five_wins.py`

Script to enable new pipeline:

- Set feature flag
- Validate output
- Rollback capability

**Acceptance:**

- [x] Can enable/disable new pipeline (`enable`, `rollback` commands)
- [x] Rollback works cleanly
- [x] Pipeline validation before deployment (`validate` command)

---

## Dependencies

```
Task 1.1 ─┬─► Task 2.1 ─┬─► Task 3.1 ─┬─► Task 4.1 ─► Task 4.2 ─► Task 5.1 ─► Task 5.2
          │             │             │                                        │
Task 1.2 ─┘             │             ├─► Task 3.2 ─┘                          │
                        │             │                                        │
                        └─► Task 2.2  └─► Task 3.3                             ├─► Task 5.3
                                                                               │
                                                                               └─► Task 6.1 ─► Task 6.2 ─► Task 6.3
```

## Progress Summary

| Phase                  | Tasks | Status      |
| ---------------------- | ----- | ----------- |
| Phase 1: Core          | 2     | ✅ Complete |
| Phase 2: Prompts       | 2     | ✅ Complete |
| Phase 3: Consolidation | 3     | ✅ Complete |
| Phase 4: Engine        | 2     | ✅ Complete |
| Phase 5: Frontend      | 3     | ✅ Complete |
| Phase 6: Testing       | 3     | ✅ Complete |

## Files Created This Session

### Backend

- `analysis/rubrics/five_wins_unified.py` - Unified Five Wins definitions
- `analysis/models/__init__.py` - Models package
- `analysis/models/five_wins.py` - Pydantic models
- `analysis/prompts/five_wins_prompt.py` - Unified prompt (no jargon)
- `analysis/consolidation/__init__.py` - Consolidation package
- `analysis/consolidation/narrative_generator.py` - 2-3 sentence narratives
- `analysis/consolidation/action_selector.py` - Single action selection
- `analysis/consolidation/moment_linker.py` - Timestamp linking

### Frontend

- `frontend/components/coaching/NarrativeSummary.tsx` - Narrative display
- `frontend/components/coaching/PrimaryActionCard.tsx` - Primary action display

### Tests

- `tests/unit/analysis/test_five_wins_prompt.py` - 15 tests passing
- `tests/unit/analysis/test_five_wins_pipeline.py` - 16 tests passing (pipeline components)

### Scripts

- `scripts/migrate_to_five_wins.py` - Migration and A/B testing management CLI

### A/B Testing

- `analysis/ab_testing.py` - A/B testing infrastructure

### Modified

- `coaching_mcp/shared/config.py` - Added `USE_FIVE_WINS_UNIFIED` flag
- `analysis/engine.py` - Added `run_five_wins_unified_analysis()` and `_apply_consolidation_layer()`
- `coaching_mcp/tools/analyze_call.py` - Integrated Five Wins Unified pipeline with fallback
- `frontend/types/coaching.ts` - Added new types
- `frontend/app/calls/[callId]/CallAnalysisViewer.tsx` - Integrated new components
