# Five Wins Coaching Rubric - Technical Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Call Analysis Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Transcript ──► Five Wins    ──► Consolidation ──► Coaching     │
│                 Evaluator        Layer              Output       │
│                                                                  │
│                 ┌──────────┐     ┌───────────┐    ┌──────────┐  │
│                 │ Business │     │ Narrative │    │ Summary  │  │
│                 │ Win      │     │ Generator │    │          │  │
│                 ├──────────┤     ├───────────┤    │ Primary  │  │
│                 │ Technical│ ──► │ Action    │ ──►│ Action   │  │
│                 │ Win      │     │ Selector  │    │          │  │
│                 ├──────────┤     ├───────────┤    │ Win      │  │
│                 │ Security │     │ Moment    │    │ Progress │  │
│                 │ Win      │     │ Linker    │    └──────────┘  │
│                 ├──────────┤     └───────────┘                   │
│                 │Commercial│                                     │
│                 │ Win      │                                     │
│                 ├──────────┤                                     │
│                 │ Legal    │                                     │
│                 │ Win      │                                     │
│                 └──────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
analysis/
├── rubrics/
│   ├── five_wins_unified.py      # NEW: Single source of truth
│   ├── five_wins_rubric.py       # DEPRECATED: Keep for reference
│   ├── discovery_rubric.py       # DEPRECATED
│   ├── engagement_rubric.py      # DEPRECATED
│   └── ...
├── prompts/
│   ├── five_wins_prompt.py       # NEW: Unified prompt
│   ├── discovery.py              # DEPRECATED
│   └── ...
├── consolidation/                 # NEW: Post-processing
│   ├── __init__.py
│   ├── narrative_generator.py    # Synthesize wins into narrative
│   ├── action_selector.py        # Pick single best action
│   └── moment_linker.py          # Link actions to timestamps
└── engine.py                      # Updated to use new pipeline
```

## Data Models

### FiveWinsEvaluation

```python
from pydantic import BaseModel
from typing import Literal

class WinProgress(BaseModel):
    """Progress toward securing a single win."""
    score: int  # 0-100
    exit_criteria_met: bool
    discovery_complete: bool
    blockers: list[str]
    evidence: list[str]  # Quotes/moments supporting the score

class ChampionAssessment(BaseModel):
    """Business Win specific: Champion evaluation."""
    identified: bool
    name: str | None
    incentive_clear: bool  # What's in it for them?
    influence_confirmed: bool  # Can they move the deal?
    information_flowing: bool  # Are they giving real intel?

class BusinessWinEvaluation(WinProgress):
    """Extended evaluation for Business Win."""
    champion: ChampionAssessment | None
    budget_confirmed: bool
    exec_sponsor_engaged: bool
    business_case_strength: Literal["weak", "moderate", "strong"]

class TechnicalWinEvaluation(WinProgress):
    """Extended evaluation for Technical Win."""
    vendor_of_choice_confirmed: bool
    poc_scoped: bool
    poc_success_criteria_defined: bool

class SecurityWinEvaluation(WinProgress):
    """Extended evaluation for Security Win."""
    infosec_timeline_known: bool
    trust_portal_shared: bool
    architecture_review_scheduled: bool

class CommercialWinEvaluation(WinProgress):
    """Extended evaluation for Commercial Win."""
    exec_sponsor_aligned: bool
    scope_agreed: bool
    pricing_discussed: bool

class LegalWinEvaluation(WinProgress):
    """Extended evaluation for Legal Win."""
    terms_impact_discussed: bool
    legal_timeline_known: bool
    redlines_in_progress: bool

class FiveWinsEvaluation(BaseModel):
    """Complete Five Wins evaluation for a call."""
    business: BusinessWinEvaluation
    technical: TechnicalWinEvaluation
    security: SecurityWinEvaluation
    commercial: CommercialWinEvaluation
    legal: LegalWinEvaluation

    overall_score: int  # Weighted average
    wins_secured: int  # Count of exit_criteria_met
```

### CoachingOutput

```python
class CallMoment(BaseModel):
    """A specific moment in the call."""
    timestamp_seconds: int
    speaker: str
    summary: str

class PrimaryAction(BaseModel):
    """The ONE thing the rep should do."""
    win: Literal["business", "technical", "security", "commercial", "legal"]
    action: str  # Specific, actionable instruction
    context: str  # Why this matters, linked to call moment
    related_moment: CallMoment | None

class CoachingOutput(BaseModel):
    """Final coaching output - what the rep sees."""

    # Primary: 2-3 sentence narrative
    narrative: str

    # Win progress summary
    wins_addressed: dict[str, str]  # win -> what was accomplished
    wins_missed: dict[str, str]  # win -> what was missed

    # Single action item
    primary_action: PrimaryAction

    # Supporting detail (collapsed by default in UI)
    five_wins_detail: FiveWinsEvaluation
    key_moments: list[CallMoment]
```

## Prompt Design

### System Prompt Structure

```python
FIVE_WINS_SYSTEM_PROMPT = """You are a sales coach evaluating a call for Prefect Cloud.

Your job is to assess progress toward the Five Wins and provide ONE actionable recommendation.

## The Five Wins Framework

{five_wins_definitions}

## This Call's Context

- Call Type: {call_type}
- Primary Win to Advance: {primary_win}
- Secondary Wins: {secondary_wins}

## Evaluation Instructions

For each win, assess:
1. What discovery was completed?
2. What progress was made toward exit criteria?
3. What's blocking this win?

Then provide:
1. A 2-3 sentence narrative summary
2. ONE specific action for the rep's next call

## Output Format

{json_schema}

## Important Guidelines

- Never mention sales methodologies by name (SPICED, Challenger, Sandler, MEDDIC)
- Focus on the Five Wins exit criteria
- Reference specific moments from the call (timestamps)
- Make the action item specific enough that the rep knows exactly what to say/do
"""
```

### User Prompt Structure

```python
FIVE_WINS_USER_PROMPT = """## Call Transcript

{transcript}

---

Evaluate this {call_type} call for Five Wins progress.

The rep should be primarily advancing: {primary_win}

Provide your evaluation in the specified JSON format. Remember:
- ONE primary action item only
- Reference specific timestamps
- No methodology jargon
"""
```

## Consolidation Layer

### Narrative Generator

```python
# analysis/consolidation/narrative_generator.py

def generate_narrative(evaluation: FiveWinsEvaluation, call_type: str) -> str:
    """
    Synthesize Five Wins evaluation into 2-3 sentence narrative.

    Pattern:
    1. What went well (wins addressed)
    2. What's at risk (wins missed or blocked)
    3. Net assessment
    """

    addressed = [w for w in WINS if evaluation[w].score >= 60]
    at_risk = [w for w in WINS if evaluation[w].score < 40]
    blocked = [w for w in WINS if evaluation[w].blockers]

    # Generate narrative focusing on most important insight
    # Prioritize by: blocked wins > at_risk wins > addressed wins
    ...
```

### Action Selector

```python
# analysis/consolidation/action_selector.py

def select_primary_action(
    evaluation: FiveWinsEvaluation,
    call_type: str,
    moments: list[CallMoment]
) -> PrimaryAction:
    """
    Select the single most important action item.

    Priority order:
    1. Unblock a blocked win (if something is stuck)
    2. Advance the primary win for this call type
    3. Prevent a win from becoming at-risk

    The action must:
    - Reference a specific win
    - Be tied to a specific call moment
    - Be concrete enough to execute
    """

    # Find the highest priority action
    blocked_wins = [w for w in WINS if evaluation[w].blockers]
    if blocked_wins:
        # Prioritize unblocking
        win = blocked_wins[0]
        blocker = evaluation[win].blockers[0]
        return create_unblock_action(win, blocker, moments)

    # Otherwise advance primary win
    primary_win = CALL_TYPE_TO_PRIMARY_WIN[call_type]
    if evaluation[primary_win].score < 80:
        return create_advance_action(primary_win, evaluation, moments)

    # Otherwise prevent risk
    ...
```

### Moment Linker

```python
# analysis/consolidation/moment_linker.py

def link_action_to_moment(
    action: str,
    win: str,
    moments: list[CallMoment]
) -> CallMoment | None:
    """
    Find the call moment most relevant to the action.

    This creates the connection between "what to do" and
    "what happened in the call that makes this important."
    """

    # Filter moments relevant to this win
    relevant_moments = [m for m in moments if is_relevant_to_win(m, win)]

    # Find the moment that best illustrates the issue
    # Prefer moments that show a missed opportunity or mistake
    ...
```

## Migration Strategy

### Phase 1: Parallel Implementation

1. Create new rubric/prompt files without removing old ones
2. Add feature flag: `USE_FIVE_WINS_UNIFIED=true`
3. Run both pipelines in shadow mode, compare outputs

### Phase 2: A/B Testing

1. Route 50% of analyses to new pipeline
2. Collect feedback metrics:
   - Time spent reading coaching
   - Action item completion rate
   - Rep satisfaction scores

### Phase 3: Cutover

1. Make new pipeline default
2. Deprecate old rubric files
3. Update UI to match new output structure

## Database Changes

No schema changes required. The `coaching_sessions` table already stores:

- `strengths: text[]`
- `areas_for_improvement: text[]`
- `action_items: text[]`
- `full_analysis: text`
- `metadata: jsonb`

The new `CoachingOutput` structure maps to:

- `narrative` → `full_analysis`
- `primary_action` → `action_items[0]`
- `five_wins_detail` → `metadata.five_wins_evaluation`

## API Changes

The `analyze_call_tool` response structure changes:

**Before:**

```json
{
  "scores": {"overall": 68, "discovery": 42, ...},
  "strengths": ["...", "...", "..."],
  "areas_for_improvement": ["...", "...", "..."],
  "action_items": ["...", "...", "...", "...", "...", "...", "..."],
  "dimension_details": {...}
}
```

**After:**

```json
{
  "scores": {"overall": 68, "business": 45, "technical": 72, ...},
  "narrative": "In this call, you made good progress on Technical Win...",
  "wins_addressed": {"technical": "Validated infrastructure requirements"},
  "wins_missed": {"business": "No champion identified"},
  "primary_action": {
    "win": "business",
    "action": "Before your next call with Mark, prepare three questions...",
    "context": "At 13:00 you offered pricing before confirming budget authority."
  },
  "five_wins_detail": {...}
}
```

Backward compatibility: Keep old fields populated during transition.
