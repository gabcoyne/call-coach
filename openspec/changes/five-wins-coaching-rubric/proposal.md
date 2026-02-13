# Five Wins Coaching Rubric Overhaul

## Problem

Current coaching feedback is overwhelming and unhelpful:

1. **Too granular** - 7+ action items per call, each citing different sales methodologies
2. **Methodology soup** - Feedback explicitly references SPICED, Challenger, Sandler, MEDDIC, creating noise instead of clarity
3. **Generic advice** - "Practice the pause technique" and "Develop Impact quantification questions" read like textbook excerpts, not coaching
4. **No connection to outcomes** - Action items don't tie back to securing specific wins or advancing the deal

Example of current bad feedback:

> "Massive Sandler discipline violation: Rep offers to close before qualifying Pain depth, Budget, or Decision process. No Impact quantification, no Critical Event identified, no business case built."

This tells the rep they did something wrong using jargon they may not know, without telling them what to do differently.

## Proposed Solution

Create a unified Five Wins rubric where:

1. **Five Wins is the ONLY framework** - SPICED, Challenger, Sandler, MEDDIC become invisible scaffolding
2. **Feedback references exit criteria** - "You haven't secured Business Win yet because there's no identified champion with budget authority"
3. **Action items are specific and singular** - One clear thing to do before the next call
4. **Coaching adapts to call type** - Discovery calls focus on Business Win, technical calls focus on Technical Win

## Five Wins Framework

### Business Win (35% weight)

**Exit Criteria:** Budget and resources allocated to evaluate and implement a solution.

**What "good" looks like:**

- Discovery covers: current state, pain, future state, success metrics, executive priorities, evaluation/decision process
- Business case answers: Why change? Why Prefect? Why now?
- Champion identified and tested (incentive, influence, information)
- Executive sponsor engaged
- Budget confirmed

**Coaching focus:** Did the rep advance toward these exit criteria? What's blocking?

### Technical Win (25% weight)

**Exit Criteria:** Received "vendor of choice" from technical evaluators.

**What "good" looks like:**

- Technical discovery complete: requirements, use case alignment, infrastructure, CI/CD
- Demo tailored to business AND technical discovery findings
- POC scoped with defined timeline and success criteria
- Explicit confirmation received (not passive approval)

**Coaching focus:** Is the technical evaluation progressing? Is the POC scoped or open-ended?

### Security Win (15% weight)

**Exit Criteria:** InfoSec/Architecture gives formal approval.

**What "good" looks like:**

- Discovery covers: InfoSec requirements, review process, timeline, questionnaire needs
- Trust portal shared proactively
- Architecture review scheduled/completed
- Formal sign-off received

**Coaching focus:** Is security review on track? Will it become a late-stage blocker?

### Commercial Win (15% weight)

**Exit Criteria:** Executive sponsor gives final approval on scope and commercials.

**What "good" looks like:**

- Discovery covers: required scope, usage, support level
- EB alignment on: scope, implementation plan, adoption plan, pricing
- Agreement confirmed by exec sponsor (not just mid-level manager)

**Coaching focus:** Is there real executive sponsorship? Are commercial terms aligned?

### Legal Win (10% weight)

**Exit Criteria:** Contract signed.

**What "good" looks like:**

- Discovery covers: required terms, legal lead time, review intensity
- Upfront expectation set on terms that impact price
- Redlines managed efficiently
- Mutual language reached, contract signed

**Coaching focus:** Is legal on track? Were price-impacting terms discussed early?

## Rubric Structure

### Per-Win Evaluation

For each win, evaluate:

```yaml
win_name:
  progress_toward_exit: 0-100 # How close to securing this win?
  discovery_complete: boolean # Has necessary discovery been done?
  blockers: [] # What's preventing progress?
  next_action: string # Single specific action to advance this win
```

### Call-Type Mapping

| Call Type              | Primary Win          | Secondary Wins                              |
| ---------------------- | -------------------- | ------------------------------------------- |
| Discovery              | Business             | Technical, Security, Legal (seed questions) |
| Technical Deep-dive    | Technical            | Business (context)                          |
| Demo                   | Technical            | Business                                    |
| POC Kickoff            | Technical            | Security                                    |
| Architecture Review    | Security             | Technical                                   |
| Executive Presentation | Business, Commercial | -                                           |
| Negotiation            | Commercial, Legal    | -                                           |

### Coaching Output Structure

Replace the current 7+ action items with:

```yaml
coaching_summary:
  # 2-3 sentence narrative (the "full_analysis" promoted to primary)
  narrative: "In this call, you made good progress on Technical Win by validating their Kubernetes requirements. However, you jumped to pricing at 13:00 before Business Win was secured - there's no confirmed champion or budget yet."

  # Which wins were addressed and which were missed
  wins_addressed:
    - technical: "Validated infrastructure requirements"
  wins_missed:
    - business: "No champion identified, no budget discussion"
    - security: "InfoSec timeline not discovered"

  # ONE specific action, tied to a win and a call moment
  primary_action:
    win: "business"
    action: "Before your next call with Mark, prepare three questions: (1) Who else needs to approve this? (2) What budget have you allocated? (3) What happens if this isn't solved by Q2?"
    context: "At 13:00 you offered to send pricing, but you don't yet know if Mark can actually approve the purchase."
```

## Implementation Changes

### 1. New Rubric File

Create `analysis/rubrics/five_wins_unified.py`:

```python
FIVE_WINS_RUBRIC = {
    "business_win": {
        "weight": 35,
        "exit_criteria": "Budget and resources allocated to evaluate and implement",
        "discovery_topics": [
            "current_state",
            "pain_points",
            "future_state",
            "success_metrics",
            "executive_priorities",
            "evaluation_process",
            "decision_process"
        ],
        "champion_criteria": ["incentive", "influence", "information"],
        "business_case_questions": ["why_change", "why_prefect", "why_now"]
    },
    # ... other wins
}
```

### 2. Updated Prompts

Replace `analysis/prompts/discovery.py` methodology references:

**Before:**

> "From a SPICED perspective... From a Challenger Sale perspective... Sandler discipline violation..."

**After:**

> "Evaluate progress toward securing Business Win. Has the rep identified a champion? Is there confirmed budget? What's blocking the exit criteria?"

### 3. Post-Processing Consolidation

Update `analysis/action_filter.py` to:

- Limit to 1 primary action item
- Require action items to reference a specific win
- Require action items to reference a specific call moment (timestamp)

### 4. UI Changes

Update `CallAnalysisViewer.tsx`:

- Promote narrative summary to top of coaching section
- Show Five Wins progress as primary visualization
- Collapse detailed dimension breakdowns by default
- Show single "Primary Action" prominently

## Success Metrics

1. **Reduced cognitive load** - Reps can read and act on coaching in <30 seconds
2. **Actionable feedback** - Every coaching session results in one clear next step
3. **Deal progression** - Coaching ties directly to advancing wins and reducing late-stage risk
4. **No methodology jargon** - Feedback never mentions SPICED, Challenger, Sandler, MEDDIC

## Migration Path

1. Create new unified rubric alongside existing rubrics
2. A/B test new coaching output format
3. Gather feedback from reps on clarity and actionability
4. Deprecate old methodology-heavy rubrics

## Out of Scope

- Changes to scoring algorithms (Five Wins weighting already exists)
- Changes to transcript processing
- Changes to call type detection
