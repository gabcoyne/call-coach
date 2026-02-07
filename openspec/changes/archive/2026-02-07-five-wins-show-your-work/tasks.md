## 1. Backend: Complete Rubric Definitions

- [ ] 1.1 Create analysis/rubrics/product_knowledge_rubric.py with 100-point structure
- [ ] 1.2 Create analysis/rubrics/objection_handling_rubric.py with 100-point structure
- [ ] 1.3 Update analysis/rubrics/**init**.py to export product_knowledge and objection_handling rubrics
- [ ] 1.4 Add test cases to tests/test_rubrics.py for product_knowledge rubric (6 tests)
- [ ] 1.5 Add test cases to tests/test_rubrics.py for objection_handling rubric (6 tests)
- [ ] 1.6 Run all rubric tests and verify 30 tests passing

## 2. Backend: Update Prompts for Five Wins Evaluation

- [ ] 2.1 Update analysis/prompts/product_knowledge.py to return five_wins_evaluation (if applicable)
- [ ] 2.2 Update analysis/prompts/objection_handling.py to return five_wins_evaluation (if applicable)
- [ ] 2.3 Add exchange_summary evidence format to product_knowledge.py prompt
- [ ] 2.4 Add exchange_summary evidence format to objection_handling.py prompt
- [ ] 2.5 Add EVALUATION INSTRUCTIONS for five_wins_evaluation scoring to all prompts
- [ ] 2.6 Verify prompt OUTPUT_REQUIREMENTS match TypeScript types

## 3. Backend: API Response Validation

- [ ] 3.1 Review coaching_mcp/tools/analyze_call.py current response structure
- [ ] 3.2 Verify five_wins_evaluation is returned correctly in response
- [ ] 3.3 Add validation that sum of win scores equals overall score
- [ ] 3.4 Test with real call to verify JSON structure and field presence
- [ ] 3.5 Add error handling for missing or malformed five_wins_evaluation

## 4. Frontend: TypeScript Types

- [ ] 4.1 Create frontend/types/rubric.ts with ExchangeEvidence interface
- [ ] 4.2 Add WinEvaluation interface to frontend/types/rubric.ts
- [ ] 4.3 Add FiveWinsEvaluation interface to frontend/types/rubric.ts
- [ ] 4.4 Add CriterionEvaluation interface for supplementary frameworks
- [ ] 4.5 Add SupplementaryFrameworks interface
- [ ] 4.6 Update frontend/types/coaching.ts to include five_wins_evaluation and supplementary_frameworks
- [ ] 4.7 Verify TypeScript compilation succeeds with no errors

## 5. Frontend: Utility Functions

- [ ] 5.1 Create frontend/lib/rubric-utils.ts file
- [ ] 5.2 Implement formatTimeRange(start, end) function
- [ ] 5.3 Implement getStatusIcon(status) function (✅ ⚠️ ❌)
- [ ] 5.4 Implement getStatusColor(status) function (green/amber/red)
- [ ] 5.5 Implement countWinsSecured(evaluation) function
- [ ] 5.6 Implement getAtRiskWins(evaluation) function
- [ ] 5.7 Implement formatWinName(key) function (snake_case to Title Case)
- [ ] 5.8 Add unit tests for all utility functions

## 6. Frontend: Core Components - FiveWinsScoreCard

- [ ] 6.1 Create frontend/components/coaching/FiveWinsScoreCard.tsx
- [ ] 6.2 Implement "X of 5 Wins Secured" header display
- [ ] 6.3 Implement at-risk wins alert display
- [ ] 6.4 Implement individual win list with status indicators
- [ ] 6.5 Add score/max_score display for each win
- [ ] 6.6 Implement color coding by status (green/amber/red)
- [ ] 6.7 Add expand/collapse functionality for individual wins
- [ ] 6.8 Add "Show All Frameworks" button at bottom

## 7. Frontend: Core Components - WinBreakdown

- [ ] 7.1 Create frontend/components/coaching/WinBreakdown.tsx
- [ ] 7.2 Implement win name and description display
- [ ] 7.3 Add score/max_score with visual progress bar
- [ ] 7.4 Implement status indicator display
- [ ] 7.5 Add exchange evidence list rendering
- [ ] 7.6 Implement "missed" explanation display (if partial/missed)
- [ ] 7.7 Add timestamp formatting (MM:SS)

## 8. Frontend: Core Components - ExchangeEvidenceCard

- [ ] 8.1 Create frontend/components/coaching/ExchangeEvidenceCard.tsx
- [ ] 8.2 Implement timestamp range badge display (e.g., "5:20 - 10:15")
- [ ] 8.3 Add exchange_summary text display
- [ ] 8.4 Add impact statement display (visually distinguished)
- [ ] 8.5 Implement long summary handling (truncation or wrap)
- [ ] 8.6 Add optional timestamp click handler (for future Gong integration)

## 9. Frontend: Core Components - SupplementaryFrameworksPanel

- [ ] 9.1 Create frontend/components/coaching/SupplementaryFrameworksPanel.tsx
- [ ] 9.2 Implement collapsed-by-default state
- [ ] 9.3 Add "Show Coaching Frameworks (SPICED/Challenger/Sandler)" button
- [ ] 9.4 Implement expansion to show discovery_rubric, engagement_rubric, etc.
- [ ] 9.5 Use same criterion breakdown pattern as Five Wins
- [ ] 9.6 Add secondary/supplementary visual styling
- [ ] 9.7 Reuse ExchangeEvidenceCard component for evidence display

## 10. Frontend: Update Existing ScoreCard

- [ ] 10.1 Update frontend/components/coaching/ScoreCard.tsx to support expand/collapse
- [ ] 10.2 Add "Show How This Score Was Calculated" button
- [ ] 10.3 Integrate FiveWinsScoreCard when expanded
- [ ] 10.4 Add smooth expand/collapse animation
- [ ] 10.5 Ensure backward compatibility with existing ScoreCard uses

## 11. Frontend: Integration with CallAnalysisViewer

- [ ] 11.1 Update frontend/app/calls/[callId]/CallAnalysisViewer.tsx to use expandable ScoreCard
- [ ] 11.2 Pass five_wins_evaluation data to FiveWinsScoreCard
- [ ] 11.3 Add type guard for hasFiveWinsEvaluation(response)
- [ ] 11.4 Implement fallback to old format if five_wins_evaluation missing
- [ ] 11.5 Add loading states during data fetch
- [ ] 11.6 Add error boundary around score card components
- [ ] 11.7 Verify no regression on existing features

## 12. Frontend: API Client Updates

- [ ] 12.1 Update frontend/lib/mcp-client.ts types for new response structure
- [ ] 12.2 Add type guards for five_wins_evaluation
- [ ] 12.3 Add backward compatibility checks for old API responses
- [ ] 12.4 Update error handling for malformed data
- [ ] 12.5 Add response validation (log warnings for invalid data)

## 13. Testing: Real Data Integration Tests

- [ ] 13.1 Test with call where all 5 wins are met (score 90+)
- [ ] 13.2 Test with call where 0 wins are met (score <20)
- [ ] 13.3 Test with call where 2-3 wins are partial (score 50-70)
- [ ] 13.4 Test with call missing five_wins_evaluation (fallback scenario)
- [ ] 13.5 Test with call having empty evidence arrays
- [ ] 13.6 Test with call having very long exchange summaries
- [ ] 13.7 Test discovery call vs demo call vs technical call
- [ ] 13.8 Verify score math: sum of wins = overall score for all test calls
- [ ] 13.9 Check console for errors during all tests
- [ ] 13.10 Verify expand/collapse works smoothly in all tests

## 14. Testing: Edge Cases and Error Handling

- [ ] 14.1 Test missing five_wins_evaluation field (graceful fallback)
- [ ] 14.2 Test partial data (some wins missing)
- [ ] 14.3 Test invalid status values (defaults to "missed" with warning)
- [ ] 14.4 Test negative scores (validation error)
- [ ] 14.5 Test scores that don't sum to total (show warning)
- [ ] 14.6 Test missing evidence arrays (show empty state)
- [ ] 14.7 Test very long exchange summaries (truncation handling)
- [ ] 14.8 Verify no crashes on any malformed data

## 15. Testing: Accessibility and Performance

- [ ] 15.1 Test keyboard navigation (tab through all interactive elements)
- [ ] 15.2 Test screen reader announcements (win status, expand/collapse state)
- [ ] 15.3 Run axe DevTools accessibility audit (0 violations)
- [ ] 15.4 Verify color contrast meets WCAG AA (4.5:1 minimum)
- [ ] 15.5 Test focus indicators visibility
- [ ] 15.6 Measure initial render time (<500ms)
- [ ] 15.7 Measure expand/collapse animation performance (60fps)
- [ ] 15.8 Verify page load time <3s

## 16. Testing: Mobile and Responsive

- [ ] 16.1 Test on mobile viewport (width < 768px)
- [ ] 16.2 Verify wins stack vertically on mobile
- [ ] 16.3 Verify evidence cards stack vertically on mobile
- [ ] 16.4 Check tap target sizes (min 44px)
- [ ] 16.5 Test touch interactions (expand/collapse)

## 17. Frontend: Visual Polish

- [ ] 17.1 Adjust spacing/padding for visual balance
- [ ] 17.2 Ensure consistent color usage across components
- [ ] 17.3 Add subtle animations (fade in, slide)
- [ ] 17.4 Polish typography (font sizes, line heights, weights)
- [ ] 17.5 Add hover states to interactive elements
- [ ] 17.6 Test visual consistency at different score ranges (0-20, 50-70, 90+)

## 18. Code Quality and Cleanup

- [ ] 18.1 Remove console.logs from production code
- [ ] 18.2 Remove commented code
- [ ] 18.3 Ensure consistent code formatting (prettier)
- [ ] 18.4 Add JSDoc comments to public component APIs
- [ ] 18.5 Check for unused imports
- [ ] 18.6 Verify no TypeScript `any` types
- [ ] 18.7 Run linter and fix all issues
- [ ] 18.8 Verify all tests passing (backend + frontend)

## 19. Documentation

- [ ] 19.1 Update component usage examples in code comments
- [ ] 19.2 Document API response structure (five_wins_evaluation format)
- [ ] 19.3 Add inline code comments for complex logic
- [ ] 19.4 Update README if new features need documentation
- [ ] 19.5 Document exchange evidence format for future prompt updates

## 20. Pre-Commit Hooks and Testing

- [ ] 20.1 Add frontend tests to pre-commit hook (.git/hooks/pre-commit or .husky/)
- [ ] 20.2 Add TypeScript type checking to pre-commit hook
- [ ] 20.3 Add linter (ESLint) to pre-commit hook
- [ ] 20.4 Add backend tests (pytest) to pre-commit hook
- [ ] 20.5 Configure pre-commit to prevent --no-verify bypassing
- [ ] 20.6 Test pre-commit hook by making intentional error and committing
- [ ] 20.7 Document pre-commit hook requirements in CONTRIBUTING.md

## 21. Deployment Preparation

- [ ] 21.1 Run full test suite (backend + frontend)
- [ ] 21.2 Verify no TypeScript compilation errors
- [ ] 21.3 Verify no console errors on call detail page
- [ ] 21.4 Check bundle size impact (<100KB increase acceptable)
- [ ] 21.5 Verify backward compatibility with old API responses
- [ ] 21.6 Test with production-like data volume
- [ ] 21.7 Review security: no sensitive data exposed in console logs

## 22. Gradual Rollout

- [ ] 22.1 Deploy frontend with type guards (supports both old and new format)
- [ ] 22.2 Enable new API responses for 10% of calls (feature flag)
- [ ] 22.3 Monitor error rates and user engagement for 24 hours
- [ ] 22.4 If stable, increase to 50% of calls
- [ ] 22.5 Monitor for another 24 hours
- [ ] 22.6 If stable, enable for 100% of calls
- [ ] 22.7 Monitor cache hit rate (should remain >80%)
- [ ] 22.8 Monitor token costs (<20% increase from baseline)
