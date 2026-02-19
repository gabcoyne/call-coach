# Adding Features

Guide for developing and adding new features to Call Coach.

## Feature Development Workflow

### 1. Plan the Feature

Before writing code, plan what you're building:

**Create a Design Document**:

```markdown
# Feature: [Feature Name]

## Problem

What user problem does this solve?

## Solution

How does this feature solve it?

## Changes Required

- Backend changes
- Frontend changes
- Database changes
- API changes

## Testing Strategy

How will we verify it works?

## Timeline

How long will this take?
```

**Example**:

```markdown
# Feature: Rep Comparison Dashboard

## Problem

Managers can't easily compare rep performance.

## Solution

Add new "Compare Reps" page that shows side-by-side metrics.

## Changes Required

- Backend: Add comparison endpoint
- Frontend: Add Compare page
- Database: No schema changes needed
- API: GET /coaching/compare-reps

## Testing

- Unit test comparison logic
- E2E test compare page
- Manual testing with real data

## Timeline

3 days (2 days dev + 1 day testing)
```

### 2. Create Feature Branch

```bash
# Start from develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/compare-reps

# Or use short issue ID
git checkout -b feature/eng-123-compare-reps
```

### 3. Implement Backend Changes

**Add new API endpoint**:

**api/rest_server.py**:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CompareReqsRequest(BaseModel):
    rep_emails: list[str]
    time_period: str = "month"

@app.post("/coaching/compare-reps")
async def compare_reps(request: CompareReqsRequest):
    """Compare multiple reps' performance."""

    results = {}
    for email in request.rep_emails:
        insights = get_rep_insights(email, request.time_period)
        results[email] = insights

    return {
        "reps": request.rep_emails,
        "period": request.time_period,
        "data": results,
        "analysis_time_seconds": 2.5
    }
```

**Add business logic**:

**coaching_mcp/tools/compare_reps.py**:

```python
from typing import list
from db import queries

def compare_reps(rep_emails: list[str], time_period: str) -> dict:
    """Compare multiple reps' performance.

    Args:
        rep_emails: List of rep emails to compare
        time_period: "week", "month", or "quarter"

    Returns:
        Comparison data with scores, trends, etc.
    """

    comparison = {}

    for email in rep_emails:
        calls = queries.get_calls_by_rep(email, time_period)
        scores = calculate_scores(calls)
        comparison[email] = scores

    return comparison

def calculate_scores(calls) -> dict:
    """Calculate average scores from calls."""
    if not calls:
        return {"error": "No calls found"}

    dimensions = ["discovery", "product", "objections", "engagement"]
    avg_scores = {}

    for dimension in dimensions:
        scores = [call[f"{dimension}_score"] for call in calls]
        avg_scores[dimension] = sum(scores) / len(scores)

    return avg_scores
```

**Add database query**:

**db/queries.py**:

```python
def get_calls_by_rep(rep_email: str, time_period: str) -> list[dict]:
    """Get calls for a rep in time period."""

    period_map = {
        "week": "1 week",
        "month": "1 month",
        "quarter": "3 months"
    }

    interval = period_map.get(time_period, "1 month")

    return fetch_all(
        """
        SELECT c.*, cs.*
        FROM calls c
        JOIN speakers s ON c.id = s.call_id
        JOIN coaching_sessions cs ON c.id = cs.call_id
        WHERE s.email = %s
        AND s.role = 'ae'
        AND c.created_at > NOW() - INTERVAL %s
        ORDER BY c.created_at DESC
        """,
        (rep_email, interval)
    )
```

### 4. Add Tests

**tests/test_compare_reps.py**:

```python
import pytest
from coaching_mcp.tools.compare_reps import compare_reps, calculate_scores

class TestCompareReps:

    def test_compare_two_reps(self, mock_database):
        """Should compare two reps' performance."""

        result = compare_reps(
            ["sarah@company.com", "tom@company.com"],
            "month"
        )

        assert "sarah@company.com" in result
        assert "tom@company.com" in result
        assert result["sarah@company.com"]["discovery"] > 0

    def test_compare_with_no_calls(self):
        """Should handle reps with no calls."""

        result = compare_reps(
            ["new-rep@company.com"],
            "month"
        )

        assert result["new-rep@company.com"]["error"] == "No calls found"

    def test_calculate_scores(self):
        """Should calculate average scores correctly."""

        calls = [
            {"discovery_score": 80, "product_score": 85, ...},
            {"discovery_score": 90, "product_score": 75, ...},
        ]

        scores = calculate_scores(calls)

        assert scores["discovery"] == 85  # (80 + 90) / 2
        assert scores["product"] == 80    # (85 + 75) / 2
```

### 5. Implement Frontend Changes

**frontend/app/compare/page.tsx**:

```typescript
"use client";

import { useState } from "react";
import { SearchReps } from "@/components/SearchReps";
import { ComparisonTable } from "@/components/ComparisonTable";

export default function ComparePage() {
  const [selectedReps, setSelectedReps] = useState<string[]>([]);
  const [period, setPeriod] = useState("month");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    if (selectedReps.length < 2) {
      alert("Select at least 2 reps");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/coaching/compare-reps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rep_emails: selectedReps,
          time_period: period,
        }),
      });

      const result = await res.json();
      setData(result);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Compare Reps</h1>

      <SearchReps
        selected={selectedReps}
        onChange={setSelectedReps}
        multiple
      />

      <div>
        <label>Time Period</label>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        >
          <option value="week">Last Week</option>
          <option value="month">Last Month</option>
          <option value="quarter">Last Quarter</option>
        </select>
      </div>

      <button
        onClick={handleCompare}
        disabled={loading || selectedReps.length < 2}
      >
        {loading ? "Comparing..." : "Compare"}
      </button>

      {data && <ComparisonTable data={data} />}
    </div>
  );
}
```

**frontend/components/ComparisonTable.tsx**:

```typescript
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@/components/ui/table";
import { ScoreBar } from "@/components/ScoreBar";

interface ComparisonTableProps {
  data: {
    reps: string[];
    data: Record<string, any>;
  };
}

export function ComparisonTable({ data }: ComparisonTableProps) {
  const dimensions = ["discovery", "product", "objections", "engagement"];

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Dimension</TableCell>
          {data.reps.map((rep) => (
            <TableCell key={rep}>{rep}</TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {dimensions.map((dim) => (
          <TableRow key={dim}>
            <TableCell className="font-medium">{dim}</TableCell>
            {data.reps.map((rep) => (
              <TableCell key={`${rep}-${dim}`}>
                <ScoreBar score={data.data[rep][dim]} />
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

### 6. Create API Route

**frontend/app/api/coaching/compare-reps/route.ts**:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

export async function POST(request: NextRequest) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();

  // Call backend API
  const response = await fetch(`${process.env.NEXT_PUBLIC_MCP_BACKEND_URL}/coaching/compare-reps`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data);
}
```

### 7. Test the Feature

**Run tests**:

```bash
# Backend tests
pytest tests/test_compare_reps.py -v

# Frontend tests
npm run test -- ComparePage.test.tsx

# Manual testing
npm run dev  # Frontend
uv run uvicorn api.rest_server:app --reload  # Backend
# Visit http://localhost:3000/compare
```

### 8. Code Review

**Before committing**:

```bash
# Format code
black coaching_mcp/
cd frontend && npm run format

# Run linting
ruff check coaching_mcp/
npm run lint

# Run all tests
pytest tests/ -v
npm run test

# Check coverage
pytest --cov=coaching_mcp
```

### 9. Commit and Push

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add rep comparison dashboard

- Add /api/coaching/compare-reps endpoint
- Add frontend Compare page with side-by-side metrics
- Add compare_reps business logic and tests
- Support week/month/quarter comparisons"

# Push to GitHub
git push origin feature/compare-reps

# Create PR on GitHub
# Request reviewers
# Wait for CI to pass
# Get approval
# Merge to develop
```

---

## Adding New Coaching Dimensions

To add a new coaching dimension (e.g., "Customer Success Alignment"):

### 1. Update Database Schema

**db/migrations/002_add_dimension.sql**:

```sql
ALTER TABLE coaching_sessions
ADD COLUMN customer_success_alignment_score INT CHECK (customer_success_alignment_score >= 0 AND customer_success_alignment_score <= 100);

ALTER TABLE analysis_runs
ADD COLUMN dimension_name VARCHAR CHECK (dimension_name IN ('discovery', 'product', 'objections', 'engagement', 'customer_success'));
```

### 2. Update Models

**db/models.py**:

```python
from enum import Enum

class CoachingDimension(str, Enum):
    DISCOVERY = "discovery"
    PRODUCT = "product"
    OBJECTIONS = "objections"
    ENGAGEMENT = "engagement"
    CUSTOMER_SUCCESS = "customer_success"
```

### 3. Create Analysis Prompt

**analysis/prompts/customer_success.md**:

```markdown
# Customer Success Alignment Analysis

Analyze the call for how well the sales rep
considers long-term customer success outcomes.

Score from 0-100:

- 90-100: Continuously references success metrics,
  support options, and long-term partnership
- 70-89: Mentions success considerations,
  some questions about support
- 50-69: Minimal focus on customer success
- 0-49: No consideration of long-term outcomes
```

### 4. Update Analysis Engine

**analysis/engine.py**:

```python
async def analyze_call(transcript: str, call_id: UUID):
    """Analyze call across all dimensions."""

    dimensions = [
        "discovery",
        "product_knowledge",
        "objection_handling",
        "engagement",
        "customer_success",  # NEW
    ]

    results = {}
    for dimension in dimensions:
        score = await analyze_dimension(
            transcript,
            dimension,
            call_id
        )
        results[dimension] = score

    return results
```

### 5. Update Frontend Components

**frontend/components/DimensionCard.tsx**:

```typescript
const dimensions = [
  { id: "discovery", label: "Discovery" },
  { id: "product", label: "Product Knowledge" },
  { id: "objections", label: "Objection Handling" },
  { id: "engagement", label: "Engagement" },
  { id: "customer_success", label: "Customer Success Alignment" }, // NEW
];
```

### 6. Test New Dimension

```bash
# Test analysis
pytest tests/test_analysis.py -v

# Manual test
curl -X POST http://localhost:8001/coaching/analyze-call \
  -H "Content-Type: application/json" \
  -d '{"call_id": "..."}'

# Should include customer_success in response
```

---

## Best Practices

1. **Start with tests**: Write tests before code
2. **Keep changes small**: One feature per PR
3. **Document changes**: Update comments and docstrings
4. **Consider edge cases**: Empty data, errors, limits
5. **Get feedback**: Code review before merging
6. **Measure impact**: Track metrics for new features
7. **Deprecate old code**: Don't remove without warning

---

## Common Patterns

### Adding Database Query

```python
# In db/queries.py
def get_calls_by_dimension_score(
    dimension: str,
    min_score: int,
    limit: int = 10
) -> list[dict]:
    """Get calls with high scores for a dimension."""
    return fetch_all(
        """
        SELECT * FROM coaching_sessions
        WHERE %s_score >= %%s
        ORDER BY created_at DESC
        LIMIT %%s
        """ % dimension,
        (min_score, limit)
    )
```

### Adding Frontend Page

```typescript
// frontend/app/[page]/page.tsx
"use client";

import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";

export default function Page() {
  const { userId } = useAuth();
  const router = useRouter();

  if (!userId) {
    router.push("/sign-in");
  }

  return (
    <main className="container mx-auto py-8">
      <h1>Your Page</h1>
    </main>
  );
}
```

### Adding API Endpoint

```python
# api/rest_server.py
@app.get("/coaching/new-endpoint")
async def new_endpoint(param: str):
    """New endpoint description."""
    try:
        result = do_something(param)
        return {"success": True, "data": result}
    except Exception as e:
        return {"error": str(e)}, 500
```

---

## See Also

- [Local Development](./setup.md) - Set up dev environment
- [Architecture](./architecture.md) - System design
- [Testing](./testing.md) - How to test
- [Git Workflow](../docs/git-workflow.md) - Commit guidelines

---

**Ready to build?** Start with [Local Development Setup](./setup.md) and create your feature branch!
