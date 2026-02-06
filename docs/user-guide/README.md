# User Guide: Getting Started with Call Coach

Welcome to Call Coach - your AI-powered sales coaching assistant. This guide introduces key features and shows you how to get the most from the platform.

## What is Call Coach?

Call Coach is an AI-powered system that analyzes Gong sales call recordings to provide:

- **Instant Coaching Insights** - Within seconds of a call, get specific feedback on what went well and where to improve
- **Performance Tracking** - Monitor your progress across key coaching dimensions week-over-week
- **Personalized Recommendations** - AI-generated coaching plans tailored to your strengths and development areas
- **Peer Comparison** - See how your performance compares to team averages
- **Call Search & Analysis** - Find specific calls and learn from top performers

All analysis uses **Claude AI** to deeply understand sales conversations and provide contextual, actionable feedback.

## Key Concepts

### Coaching Dimensions

Call Coach analyzes every call across **4 key coaching dimensions**:

1. **Discovery** (Learning customer needs)

   - Understanding the customer's business challenges
   - Asking qualifying questions
   - Identifying pain points and priorities
   - Exploring current solutions
   - Uncovering decision criteria

2. **Product Knowledge** (Demonstrating expertise)

   - Accurate product feature explanation
   - Relevant use case examples
   - Competitive positioning
   - Technical depth when needed
   - Connecting features to customer needs

3. **Objection Handling** (Overcoming concerns)

   - Listening to and understanding objections
   - Addressing concerns with evidence
   - Value-based responses to pricing
   - Technical objection resolution
   - Building confidence in solutions

4. **Engagement** (Building relationships)
   - Rapport and active listening
   - Clear communication
   - Customer language and terminology use
   - Enthusiasm and confidence
   - Building long-term relationships

Each dimension gets a **score from 0-100**, with specific findings and recommendations.

### Call Types

Calls are categorized by purpose:

- **Discovery** - Initial conversation to understand customer needs
- **Demo** - Product demonstration and feature walkthrough
- **Negotiation** - Contract and pricing discussion
- **Technical Deep Dive** - Technical requirements discussion

### Products

Analysis covers two product lines:

- **Prefect** - Data orchestration platform
- **Horizon** - Managed Prefect cloud service

## Getting Started

### Step 1: Access the Platform

**Option A: Web Dashboard** (Recommended)

1. Navigate to the Call Coach dashboard
2. Sign in with your Prefect email
3. Complete Clerk authentication setup (one-time)

**Option B: Claude Desktop** (For power users)

1. Ensure MCP server is running locally
2. Add to Claude Desktop configuration
3. Ask Claude questions about calls naturally

### Step 2: View Your Dashboard

Your personal dashboard shows:

- **This Week's Performance** - Current week's average scores across all dimensions
- **Monthly Trends** - Performance over the past 30 days
- **Skill Gaps** - Areas identified for improvement
- **Recent Calls** - Latest analyzed calls with scores
- **Coaching Plan** - Personalized next steps

Example dashboard data:

```
This Month: 82 average
├─ Discovery: 80 (trend: improving +5)
├─ Product Knowledge: 88 (trend: stable)
├─ Objection Handling: 75 (trend: declining -3)
└─ Engagement: 85 (trend: stable +2)

Skill Gaps:
1. Objection Handling (High Priority)
   → Practice pricing objection scenarios
   → Focus on value-based responses
```

### Step 3: Analyze Your First Call

**To analyze a call:**

1. Go to **Analyze Call** section
2. Enter the **Gong Call ID** (9-digit number from Gong)
3. Optionally select a **Focus Area** (discovery, product, objections, engagement)
4. Click **Analyze** and wait 30-45 seconds

Example analysis result:

```
Call: Acme Corp - Discovery Demo
Duration: 30 minutes
Overall Score: 85/100

Discovery: 82/100
├─ ✓ Effectively asked about current tools
├─ ✓ Identified key pain point (integration complexity)
└─ → Could explore timeline and budget earlier

Product Knowledge: 92/100
├─ ✓ Strong understanding of Horizon features
├─ ✓ Clear deployment options explanation
└─ → (No improvement areas)

Objection Handling: 78/100
├─ ✓ Handled pricing objection with ROI discussion
└─ → Prepare ROI calculator before calls

Engagement: 88/100
├─ ✓ Built strong rapport
├─ ✓ Used customer's language
└─ → (Minor improvement opportunities)

Next Steps:
1. Review ROI-based pricing discussion framework
2. Practice discovery questions about timeline/budget
3. Celebrate strong product knowledge demonstration!
```

## Using Coaching Insights

### Reading a Coaching Analysis

Each analysis includes:

**Findings** - What was observed in the call

- Positive findings show what went well
- Improvement findings show opportunities

**Recommendations** - Specific actions to improve

- Actionable and skill-specific
- Prioritized by impact
- Include supporting evidence

**Evidence** - Direct quotes from the call

- Shows exactly where findings are based
- Includes timestamp in call
- Provides context for recommendations

**Score Interpretation**:

- **90-100**: Excellent performance, minimal improvement needed
- **80-89**: Good performance, some opportunities to build on strength
- **70-79**: Average performance, meaningful improvement possible
- **60-69**: Below average, recommend focused coaching
- **Below 60**: Significant opportunity for improvement

### Comparing Calls

Use **Call Search** to find similar calls:

1. Go to **Search**
2. Enter keywords: "discovery", "pricing objection", "integration", etc.
3. Apply filters:
   - **Call Type**: discovery, demo, etc.
   - **Product**: Prefect, Horizon
   - **Min Score**: Find high-scoring examples
   - **Date Range**: Recent calls or time period
4. Compare results to see patterns

Example search:

```
Query: "discovery"
Filters:
  Type: Discovery
  Min Score: 90
  Product: Horizon

Results: 12 calls found
├─ Call 1: 95/100 - Acme Corp (2026-02-03)
├─ Call 2: 93/100 - TechStart Inc (2026-01-29)
├─ Call 3: 92/100 - FinCorp (2026-01-22)
```

Pick the highest-scoring call and study:

1. What did the rep do differently?
2. How did they structure the discovery?
3. What questions did they ask?
4. How did they transition to product discussion?

### Creating Your Coaching Plan

Based on your skill gaps, create a focused improvement plan:

**Step 1: Identify Priority Gaps**

- Review your last 10 calls
- Find the lowest-scoring dimension
- Check if it's declining over time

**Step 2: Set a Specific Goal**

- Example: "Improve objection handling from 75 to 85 in 30 days"
- Break it down: "+2-3 points per week"

**Step 3: Take Action**

- Find high-scoring calls in the area
- Practice specific scenarios (role-play)
- Study competitor objections
- Shadow top performers

**Step 4: Measure Progress**

- Review your scores weekly
- Compare to baseline
- Celebrate improvements
- Adjust plan as needed

## Dashboard Features

### Performance Trends

View trends over time:

```
Last 30 Days - Discovery Dimension

Week 1: 78 (4 calls)
Week 2: 80 (5 calls)
Week 3: 82 (3 calls)
Week 4: 84 (3 calls)

Trend: ↑ Improving +6 points
```

### Peer Comparison

See how you compare to your team:

```
Team Average: 79/100
Your Score: 82/100
Percentile: 78th

Better than average in:
├─ Product Knowledge (+8 points)
└─ Engagement (+5 points)

Below average in:
└─ Objection Handling (-4 points)
```

### Coaching Plan

Your personalized development plan includes:

```
Priority 1: Objection Handling (High)
├─ Action: Complete objection handling workshop
├─ Date: February 12, 2026
├─ Time: 1.5 hours
├─ Expected Improvement: +8 points
└─ Status: Scheduled

Priority 2: Discovery Depth (Medium)
├─ Action: Review discovery questioning framework
├─ Estimated Time: 2 hours
├─ Expected Improvement: +5 points
└─ Status: Not started
```

## Call Analysis Viewer

When analyzing a call, you'll see:

### Call Summary

- Call title and date
- Duration and participants
- Product discussed
- Call outcome (if tracked)

### Dimension Breakdown

- Score for each dimension (0-100)
- Specific findings (strengths and gaps)
- Actionable recommendations
- Supporting evidence with timestamps

### Full Transcript

- Complete call transcript with timestamps
- Speaker identification
- Search across transcript
- Jump to specific moments in recording

### Coaching Recommendations

- Prioritized action items
- Skill development suggestions
- Resources and references
- Next conversation points

## Search & Filtering

### Quick Search

Find calls by keywords:

```
Search: "pricing objection"
Results: All calls mentioning pricing or objections

Search: "Sarah"
Results: All calls with Sarah as participant
```

### Advanced Filters

Combine multiple filters:

```
Search: "horizon"
Filters:
  Call Type: Demo
  Min Score: 85
  Product: Horizon
  Date Range: Last 30 days
  Rep Email: sarah.jones@prefect.io

Results: 3 calls found
```

### Saved Searches

Save frequent searches:

1. Create a filtered search
2. Click "Save Search"
3. Name it (e.g., "High-Scoring Discovery Calls")
4. Access from sidebar

Suggested saved searches:

- "My highest scoring calls" - Min score 90
- "Discovery calls" - Type: Discovery
- "Objection handling practice" - Keywords: objection, pricing
- "Product demos" - Type: Demo, Product: Horizon

## Weekly Reports

Every Monday, you receive an automated report:

### Report Contents

**Your Performance This Week**

```
Calls Analyzed: 5
Average Score: 83/100
Trend: ↑ Improving
Best Call: 94/100
```

**Dimension Breakdown**

```
Discovery: 81 (down 2 from last week)
Product Knowledge: 89 (up 3)
Objection Handling: 77 (stable)
Engagement: 86 (up 4)
```

**Key Insights**

- Highlighted patterns in your calls
- Compared to team averages
- Progress on goals
- Learning opportunities

**Recommended Actions**

- Specific next steps based on this week
- Skill development suggestions
- Calls to study from top performers

See [Weekly Reports Guide](./weekly-reports.md) for details.

## Role-Based Access

### If You're a Sales Rep

You can:

- View your own call analyses
- See your personal dashboard
- Create coaching plans
- Search your calls
- Compare to team averages (anonymized)

You cannot:

- See other reps' detailed call data
- View other reps' dashboards
- Export rep data

### If You're a Manager

You can:

- View all team members' analyses
- Compare rep performance
- Identify team skill gaps
- Create team coaching plans
- Generate team reports
- Export data for analysis

See [Role Management Guide](./role-management.md) for details.

## Tips & Best Practices

### 1. Review Calls Regularly

- Review analyses within 24 hours while call is fresh
- Note key learnings
- Update your practice

### 2. Learn from Top Performers

- Find calls with 90+ scores
- Study what made them successful
- Identify patterns in their approach

### 3. Focus on One Dimension

- Pick your lowest dimension
- Find 3 calls with 85+ scores in that area
- Practice the techniques used

### 4. Use Evidence-Based Feedback

- Reference specific quotes and timestamps
- Use as training material
- Share with manager for coaching

### 5. Track Your Progress

- Set weekly improvement targets (+2-3 points)
- Review trends monthly
- Celebrate wins
- Adjust strategy as needed

### 6. Create Group Studies

- Use Call Search to find interesting calls
- Share with team members
- Discuss in team meetings
- Build collective learning

## Troubleshooting

### "Call not found in database"

The call hasn't been processed yet. This can happen if:

1. Call is still being transferred from Gong (wait 5-10 minutes)
2. Gong webhook wasn't received
3. Call ID is incorrect

**Solution**: Check Gong for the correct call ID, wait a few minutes, try again.

### "Analysis is taking longer than expected"

This happens with very long calls (60+ minutes). This is normal.

**Typical times**:

- Standard call (15-30 min): 30-45 seconds
- Long call (45-60 min): 60-90 seconds
- Very long call (60+ min): Up to 3 minutes

### "Dimension score seems inaccurate"

Scores are based on Claude's analysis of the transcript and can vary based on context.

**To review**:

1. Check the "Evidence" section - see exact quotes
2. Read recommendations - understand the reasoning
3. Share feedback with your manager if needed

## Next Steps

1. **Analyze your first call** - Try the [Call Analysis Viewer](coaching.md)
2. **Review your coaching plan** - See [Creating Coaching Plans](./README.md#creating-your-coaching-plan)
3. **Search for learning calls** - Find high-scoring examples
4. **Understand your role** - See [Role Management](./role-management.md)
5. **Read weekly reports** - See [Weekly Reports](./weekly-reports.md)

## Support

Need help?

1. **Troubleshooting**: Check [Troubleshooting Guide](../troubleshooting/README.md)
2. **Concepts**: Review [Coaching Dimensions](#coaching-dimensions)
3. **API Issues**: See [API Error Codes](../troubleshooting/api-errors.md)
4. **Contact Support**: Email support with your issue and request ID

---

**Ready to improve your sales skills?** Start by [analyzing your first call](coaching.md)!
