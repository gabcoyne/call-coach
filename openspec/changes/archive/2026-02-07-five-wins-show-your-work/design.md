## Context

### Current State

- Coaching analysis returns scores (0-100) without transparency into how they're calculated
- Prompts use SPICED/Challenger/Sandler frameworks as primary scoring mechanisms
- Evidence is quote-based (single transcript snippets) which lacks context for multi-turn exchanges
- UI shows flat scores with no drill-down capability
- Prefect's sales team uses "Five Wins" methodology internally but analysis doesn't reflect this

### User Feedback

1. "Transcript quotes will be unusable, as it's hard to capture what's relevant across an exchange" - Need multi-turn exchange summaries
2. "The most important rubric is the 'five wins' that's the way we look at sales internally" - Five Wins must be primary, not SPICED/Challenger/Sandler

### Technical Constraints

- Must maintain prompt caching (90% cost reduction) - can't restructure cached rubric sections
- Backward compatibility required - old API responses must still render correctly
- Frontend has history of type mismatches causing runtime errors - need strong type safety

## Goals / Non-Goals

**Goals:**

- Five Wins becomes the PRIMARY scoring mechanism (100 points) with clear "X of 5 wins secured" visibility
- Evidence shows conversational patterns across multiple turns, not isolated quotes
- Users can expand any score to see rubric criteria, evidence, and gaps
- Maintain prompt cache efficiency (>80% cache hit rate)
- Backward compatible - works with both new and old API response formats
- Type-safe frontend prevents rendering errors

**Non-Goals:**

- Clickable timestamps to jump to Gong recordings (future enhancement)
- Manager override of AI scores (out of scope for this change)
- Real-time scoring during live calls (analysis is post-call only)
- Mobile-optimized UI (responsive layout acceptable, but not mobile-first)

## Decisions

### Decision 1: Five Wins as Primary, Other Frameworks as Supplementary

**Choice**: Restructure response to have `five_wins_evaluation` (primary, 100 points) and `supplementary_frameworks` (optional, for coaching depth)

**Alternatives Considered**:

- Keep SPICED/Challenger as primary, add Five Wins alongside → Rejected: Doesn't align with how team thinks about sales
- Compute Five Wins from SPICED scores → Rejected: Point allocation wouldn't match win importance (Business Win 35pts != sum of SPICED elements)

**Rationale**: Five Wins is Prefect's internal sales language. Scoring must reflect what actually closes deals. SPICED/Challenger/Sandler provide coaching depth (HOW to improve each win) but aren't the primary evaluation.

**Implementation**:

- Prompts return `five_wins_evaluation` object with 5 wins
- SPICED/Challenger/Sandler moved to `supplementary_frameworks.discovery_rubric` etc.
- Frontend displays Five Wins first (expanded), supplementary collapsed by default
- Overall score (0-100) = sum of five_wins_evaluation scores

### Decision 2: Exchange Summaries Instead of Quotes

**Choice**: Evidence uses `timestamp_start`, `timestamp_end`, `exchange_summary` (multi-turn dialogue), `impact` (why it matters)

**Alternatives Considered**:

- Keep quote-based evidence → Rejected: User feedback that quotes lack context
- Transcript excerpts (full verbatim multi-turn) → Rejected: Too verbose, doesn't highlight pattern
- Quote arrays (multiple quotes per criterion) → Rejected: Still isolated statements

**Rationale**: Sales conversations are patterns across exchanges. Single quotes miss the context (e.g., "Yeah, we have concerns" loses that rep didn't follow up). Exchange summaries capture the flow and missed opportunities.

**Implementation**:

```typescript
interface ExchangeEvidence {
  timestamp_start: number; // seconds
  timestamp_end: number; // seconds
  exchange_summary: string; // "Rep asked X, customer said Y, rep did/didn't Z"
  impact: string; // "Missed opportunity because..." or "Strong because..."
}
```

Prompts instructed: "Capture multi-turn dialogue patterns, not isolated quotes. Show what happened across the exchange."

### Decision 3: Post-Processing vs. Prompt Changes for Rubric Structure

**Choice**: Add new output fields to prompts (`five_wins_evaluation`) rather than post-processing existing output

**Alternatives Considered**:

- Post-process existing `strengths`/`improvements` to infer Five Wins scores → Rejected: Loses precision, can't map free text to structured wins
- Separate API call to score Five Wins → Rejected: Doubles token cost and latency

**Rationale**: Prompts have full transcript context and can accurately evaluate each win during analysis. Adding output fields has minimal cache impact (doesn't change rubric evaluation logic).

**Cache Preservation**:

- Rubric definitions remain in system prompt (cached)
- OUTPUT_REQUIREMENTS section updated (not cached)
- Cache hit rate maintained >80%

### Decision 4: Frontend Type Safety and Backward Compatibility

**Choice**: Use TypeScript discriminated unions and type guards for response parsing

**Alternatives Considered**:

- Runtime schema validation (Zod) → Rejected: Adds bundle size, validation overhead
- Assume new format always present → Rejected: Breaks on cached old responses

**Rationale**: Previous frontend errors were type mismatches (objects vs strings). Strict TypeScript types catch these at compile time. Type guards provide runtime safety.

**Implementation**:

```typescript
// Type guard
function hasFiveWinsEvaluation(response: any): response is NewAnalysisResponse {
  return response?.five_wins_evaluation !== undefined;
}

// Usage in component
if (hasFiveWinsEvaluation(analysisData)) {
  return <FiveWinsScoreCard evaluation={analysisData.five_wins_evaluation} />;
} else {
  return <LegacyScoreDisplay score={analysisData.score} />; // Fallback
}
```

### Decision 5: Component Architecture - Composition over Monolith

**Choice**: Break UI into composable components (FiveWinsScoreCard, WinBreakdown, ExchangeEvidenceCard, SupplementaryFrameworksPanel)

**Alternatives Considered**:

- Single mega-component with all logic → Rejected: Hard to test, maintain, reuse
- One component per win (BusinessWinCard, TechnicalWinCard, etc.) → Rejected: Too granular, duplicates logic

**Rationale**: Composition allows reuse (same ExchangeEvidenceCard for wins and supplementary frameworks), easier testing (unit test each component), clearer separation of concerns.

**Component Hierarchy**:

```
CallAnalysisViewer
  └─ ScoreCard (enhanced with expand/collapse)
      ├─ FiveWinsScoreCard (primary)
      │   └─ WinBreakdown (per win)
      │       └─ ExchangeEvidenceCard (per evidence)
      └─ SupplementaryFrameworksPanel (optional, collapsed)
          └─ CriterionBreakdown (SPICED/Challenger)
              └─ ExchangeEvidenceCard (shared component)
```

## Risks / Trade-offs

### Risk 1: Exchange Summary Quality Inconsistent

**Impact**: If Claude generates vague summaries (e.g., "Rep and customer discussed requirements"), evidence won't be actionable

**Mitigation**:

- Add explicit examples in prompts ("Good: Rep asked X, customer said Y, rep didn't follow up. Bad: Rep asked about requirements")
- Iterate on prompt with 10+ test calls to tune summary quality
- Include `impact` field to ensure "why this matters" is clear
- If summaries are poor, can add post-processing to flag vague ones for human review

### Risk 2: API Response Size Increases

**Impact**: Adding five_wins_evaluation + supplementary_frameworks + exchange summaries could double response size, increasing latency and token costs

**Mitigation**:

- Limit evidence to 3 exchanges per win (vs unlimited)
- Gzip compression on API responses (already enabled)
- Monitor token usage in production - if costs spike, make supplementary_frameworks opt-in (query param)
- Lazy-load supplementary frameworks only when user expands

**Measurement**: Current avg response ~15KB, new format ~25KB (67% increase). Acceptable tradeoff for transparency.

### Risk 3: Frontend Breaks on Malformed Data

**Impact**: If API returns unexpected structure (missing fields, wrong types), React crashes with "[object Object]" errors

**Mitigation**:

- TypeScript types with strict validation
- Type guards for runtime checks
- Error boundaries around score card components
- Graceful degradation (fallback to old format if new fields missing)
- Unit tests for edge cases (null, undefined, empty arrays, invalid status values)

**Test Scenarios**: Missing five_wins_evaluation, partial data (only 3 of 5 wins), scores don't sum to total, invalid status value, empty evidence arrays

### Risk 4: Backward Compatibility Failures

**Impact**: Deployed frontend works with new API but breaks when old cached responses are served (prompts not yet updated)

**Mitigation**:

- Deploy frontend with type guards first (can handle both old and new)
- Roll out backend prompt changes gradually (10% → 50% → 100%)
- Monitor error rates during rollout
- Keep backward compatible for at least 2 weeks until all cached responses expire

**Rollback Plan**: Frontend type guards allow instant revert to old format display. Backend rollback = revert prompt changes.

### Risk 5: User Overwhelm from Complexity

**Impact**: Showing Five Wins + supplementary frameworks + detailed evidence might overwhelm users

**Mitigation**:

- Progressive disclosure: Five Wins expanded by default, supplementary collapsed
- Clear visual hierarchy (primary vs secondary styling)
- "X of 5 Wins Secured" summary at top for quick scan
- Mobile: Stack vertically, but same progressive disclosure
- User testing with 5-10 reps before full rollout

### Risk 6: Five Wins Point Distribution Wrong

**Impact**: If Business Win shouldn't be 35 points (e.g., should be 30), we need to re-score historical data

**Mitigation**:

- Validate with stakeholders BEFORE implementation (confirm: Business 35, Technical 25, Security 15, Commercial 15, Legal 10)
- If distribution changes, it's a config change (update rubric file), not code change
- Historical data doesn't need re-scoring (point in time evaluation)

**Open Question**: Confirm with sales leadership that point distribution matches deal importance.

## Migration Plan

### Phase 1: Backend Foundation (Week 1)

1. Complete remaining rubric definitions (product_knowledge, objection_handling)
2. Update all prompts to return five_wins_evaluation
3. Validate API response structure with 10+ test calls
4. Deploy to staging

**Validation**:

- Run test suite (30+ rubric tests)
- Manual analysis of 10 calls, verify JSON structure
- Check token usage (should be <20% increase from baseline)

### Phase 2: Frontend Components (Week 1-2)

1. Create TypeScript types and utilities
2. Build core components (FiveWinsScoreCard, WinBreakdown, ExchangeEvidenceCard)
3. Unit test components with mock data
4. Integration test with CallAnalysisViewer

**Validation**:

- All component tests passing
- Type errors = 0
- Manual testing with both new and old API response formats

### Phase 3: Gradual Rollout (Week 2)

1. Deploy frontend to production (with type guards for backward compatibility)
2. Enable new API responses for 10% of calls (feature flag)
3. Monitor error rates, user engagement (expand/collapse interactions)
4. If stable, increase to 50%, then 100%

**Success Metrics**:

- 0 console errors on call detail page
- > 80% cache hit rate maintained
- <3s page load time
- User engagement: >50% of users expand at least one win

### Phase 4: Cleanup (Week 3)

1. Remove old format fallback code (once 100% on new format)
2. Archive old response examples
3. Update documentation

**Rollback Strategy**:

- Frontend rollback: Revert to old ScoreCard component (type guards allow instant switch)
- Backend rollback: Revert prompt changes via git
- Database: No schema changes, so no migration rollback needed

## Open Questions

1. **Five Wins Point Distribution**: Confirm Business (35), Technical (25), Security (15), Commercial (15), Legal (10) matches sales team priorities? Or should Security be higher than Commercial?

2. **Exchange Summary Length**: Target 1-2 sentences per exchange. Too short? Too long? Should we show full summaries or truncate with "show more"?

3. **Supplementary Frameworks Visibility**: Should SPICED/Challenger/Sandler be collapsed by default or always visible? User testing can inform this.

4. **Mobile Experience**: Is responsive layout (stacks vertically) sufficient for MVP, or do we need mobile-specific component (simplified view)?

5. **Product Knowledge & Objection Handling Calls**: Do these also use Five Wins as primary rubric? Or do they need different primary rubrics (e.g., "Product Mastery" dimensions for product calls)?

6. **Historical Data**: Do we need to re-analyze past calls with new Five Wins rubric, or is it OK that old calls only have SPICED scores?
