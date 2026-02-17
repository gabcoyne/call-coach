# Type Generation Guide

This document explains how types flow from the Python backend to the TypeScript frontend.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE SOURCE OF TRUTH                        │
│                                                                  │
│   db/models.py (Pydantic models)                                │
│   api/rest_server.py (Request schemas)                          │
│              │                                                   │
│              ▼                                                   │
│   FastAPI auto-generates /openapi.json                          │
│              │                                                   │
│              ▼                                                   │
│   openapi-typescript generates TypeScript types                 │
│              │                                                   │
│              ▼                                                   │
│   frontend/types/generated/api.ts (Request types)               │
│                                                                  │
│   Note: Response types remain in types/coaching.ts because      │
│   FastAPI endpoints return dict[str, Any] (not typed responses) │
└─────────────────────────────────────────────────────────────────┘
```

## Commands

```bash
# Generate types (requires API server running or saved schema)
cd frontend && npm run generate:types

# Type check frontend
npm run type-check

# Full build (includes type generation)
npm run build
```

## Directory Structure

```
frontend/
├── types/
│   ├── generated/          # AUTO-GENERATED - DO NOT EDIT
│   │   ├── api.ts          # Generated Request types from OpenAPI
│   │   └── index.ts        # Re-exports for convenience
│   ├── coaching.ts         # Response types + Zod schemas (re-exports Request types)
│   └── rubric.ts           # Custom types (Five Wins, etc.)
```

## Current Type Organization

### Request Types (Auto-Generated)

Request types are generated from Pydantic models in `api/rest_server.py`:

- `AnalyzeCallRequest`
- `RepInsightsRequest`
- `SearchCallsRequest`
- `AnalyzeOpportunityRequest`
- `LearningInsightsRequest`
- `CoachingFeedRequest`

### Response Types (Manual)

Response types remain in `types/coaching.ts` because FastAPI endpoints return `dict[str, Any]`:

- `AnalyzeCallResponse`
- `RepInsightsResponse`
- `SearchCallsResponse`
- `FeedResponse`
- `CallMetadata`, `CallParticipant`, `DimensionScores`, etc.

### Zod Schemas (Runtime Validation)

Zod schemas in `types/coaching.ts` provide runtime validation for API requests:

- `analyzeCallRequestSchema`
- `repInsightsRequestSchema`
- `searchCallsRequestSchema`
- `feedRequestSchema`

## Usage

### Importing Types

```typescript
// Option 1: Import from coaching.ts (backward compatible)
import type {
  AnalyzeCallRequest, // Re-exported from generated
  AnalyzeCallResponse, // Defined in coaching.ts
} from "@/types/coaching";

// Option 2: Import directly from generated
import type { AnalyzeCallRequest } from "@/types/generated";

// Option 3: Import Zod schemas for runtime validation
import { analyzeCallRequestSchema } from "@/types/coaching";
```

### Type-Safe API Calls

```typescript
import type { paths } from "@/types/generated";

// Use paths for endpoint types
type AnalyzeEndpoint = paths["/api/v1/tools/analyze_call"]["post"];
```

## Adding New API Endpoints

1. **Define Pydantic model in backend:**

   ```python
   # api/rest_server.py
   class NewFeatureRequest(BaseModel):
       field1: str = Field(..., description="Required field")
       field2: int | None = Field(None, description="Optional field")
   ```

1. **Add endpoint:**

   ```python
   @app.post("/api/v1/new_feature")
   async def new_feature_endpoint(request: NewFeatureRequest) -> dict[str, Any]:
       ...
   ```

1. **Regenerate types:**

   ```bash
   cd frontend && npm run generate:types
   ```

1. **Use in frontend:**

   ```typescript
   import type { components } from "@/types/generated";

   type NewFeatureRequest = components["schemas"]["NewFeatureRequest"];
   ```

1. **Add Response type (if needed):**

   ```typescript
   // types/coaching.ts
   export interface NewFeatureResponse {
     result: string;
     data: SomeData;
   }
   ```

## Future Improvements

To get auto-generated Response types, FastAPI endpoints need to return typed Pydantic models instead of `dict[str, Any]`:

```python
# Current (no response type generation)
async def analyze_call(request: AnalyzeCallRequest) -> dict[str, Any]:
    ...

# Future (generates response types)
async def analyze_call(request: AnalyzeCallRequest) -> AnalyzeCallResponse:
    ...
```

## Troubleshooting

### Types not updating

1. Regenerate: `cd frontend && npm run generate:types`
2. Check for errors: `npm run type-check`
3. If server not running, it uses cached `openapi.json`

### Type mismatch between frontend and backend

1. Ensure Request types come from `@/types/generated`
2. Regenerate types after backend changes
3. Check Response types in `coaching.ts` match backend

### Missing types in generated file

The type must be exposed through the OpenAPI schema:

1. Add a Pydantic model to `api/rest_server.py`
2. Use it in an endpoint parameter (not just return type)
3. Regenerate types

## Best Practices

1. **Never edit files in `types/generated/`** - they will be overwritten
2. **Import Request types from generated** - ensures sync with backend
3. **Keep Response types in coaching.ts** - until FastAPI returns typed responses
4. **Run `npm run generate:types` after backend changes**
5. **Use Zod schemas for runtime validation** - TypeScript types don't validate at runtime
