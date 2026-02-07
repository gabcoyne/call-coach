## Why

Users see coaching scores (e.g., "Discovery: 42/100") but cannot understand why they received that score. Without transparency into how scores are calculated, users cannot trust the AI evaluation or take targeted action to improve. Prefect's internal sales methodology centers on the "Five Wins" framework (Business, Technical, Security, Commercial, Legal), but current scoring uses SPICED/Challenger/Sandler frameworks that don't align with how the team thinks about and coaches deals.

## What Changes

- Implement Five Wins as the PRIMARY scoring rubric (100 points: Business 35, Technical 25, Security 15, Commercial 15, Legal 10)
- Add structured rubric evaluation to all analysis dimensions with exchange-based evidence (not isolated quotes)
- Build expandable score card UI components showing "X of 5 Wins Secured" with detailed breakdowns
- Move SPICED/Challenger/Sandler frameworks to supplementary coaching insights (collapsed by default)
- Add exchange summary evidence format to capture multi-turn dialogue patterns instead of single quotes
- Create comprehensive test coverage for rubrics and UI components

## Capabilities

### New Capabilities

- `five-wins-rubric`: Primary evaluation framework with Business Win (35pts), Technical Win (25pts), Security Win (15pts), Commercial Win (15pts), Legal Win (10pts) - aligned with Prefect's internal sales methodology
- `exchange-evidence`: Evidence structure using multi-turn dialogue summaries with timestamp ranges instead of isolated quotes
- `rubric-score-cards`: Expandable UI components for displaying Five Wins evaluation with status indicators (met/partial/missed)
- `supplementary-frameworks`: Collapsible panels for SPICED/Challenger/Sandler coaching insights (secondary to Five Wins)

### Modified Capabilities

- `discovery-analysis`: Update to return `five_wins_evaluation` as primary output with `supplementary_frameworks.discovery_rubric` for SPICED insights
- `engagement-analysis`: Update to use exchange-based evidence instead of quote-based evidence

## Impact

### Backend

- `analysis/rubrics/` - New rubric modules (five_wins, discovery, engagement, product_knowledge, objection_handling)
- `analysis/prompts/` - All dimension prompts updated to return `five_wins_evaluation` with exchange summaries
- `coaching_mcp/tools/analyze_call.py` - Response structure includes `five_wins_evaluation` and `supplementary_frameworks`
- `tests/test_rubrics.py` - Comprehensive test coverage for all rubric definitions

### Frontend

- `frontend/types/rubric.ts` - New TypeScript types for Five Wins, exchange evidence, criterion evaluation
- `frontend/lib/rubric-utils.ts` - Utility functions for formatting, status colors, win counting
- `frontend/components/coaching/` - New components: FiveWinsScoreCard, WinBreakdown, ExchangeEvidenceCard, SupplementaryFrameworksPanel
- `frontend/components/coaching/ScoreCard.tsx` - Updated to support expand/collapse with Five Wins integration
- `frontend/app/calls/[callId]/CallAnalysisViewer.tsx` - Integration of Five Wins display as primary scoring view

### Database

- No schema changes required (backward compatible with existing `coaching_sessions` table)
- Response JSON structure extended with new fields (`five_wins_evaluation`, `supplementary_frameworks`)

### Dependencies

- No new dependencies required
- Backward compatible with existing API responses (graceful fallback if new fields missing)
