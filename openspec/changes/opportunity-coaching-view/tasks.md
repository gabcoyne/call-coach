## 1. Database Schema for Opportunities and Emails

- [x] 1.1 Add opportunities table to db/schema.sql with columns: id, gong_opportunity_id (unique), name, account_name, owner_email, stage, close_date, amount, health_score, metadata (JSONB), created_at, updated_at
- [x] 1.2 Add emails table with columns: id, gong_email_id (unique), opportunity_id (FK), subject, sender_email, recipients (array), sent_at, body_snippet (500 chars), metadata (JSONB), created_at
- [x] 1.3 Add call_opportunities junction table with columns: call_id (FK), opportunity_id (FK), created_at, PRIMARY KEY (call_id, opportunity_id)
- [x] 1.4 Add indexes: idx_opportunities_owner (owner_email, updated_at DESC), idx_opportunities_stage (stage, close_date), idx_emails_opportunity (opportunity_id, sent_at DESC), idx_call_opportunities_opp (opportunity_id)
- [x] 1.5 Add sync_status table to track last sync timestamps per entity type (opportunities, calls, emails)
- [x] 1.6 Run database migration on Neon to create new tables
- [x] 1.7 Verify schema with query to check all tables and indexes exist

## 2. Gong API Client Extensions

- [x] 2.1 Add list_opportunities(modified_after: datetime) method to gong/client.py
- [x] 2.2 Add get_opportunity_calls(opportunity_id: str) method to fetch calls for an opportunity
- [x] 2.3 Add get_opportunity_emails(opportunity_id: str) method to fetch emails for an opportunity
- [x] 2.4 Add pagination support to handle large result sets (>100 items)
- [x] 2.5 Add rate limit handling with exponential backoff
- [ ] 2.6 Test API methods with real Gong credentials and log responses

## 3. Database Access Layer for Opportunities

- [x] 3.1 Add upsert_opportunity(opp_data: dict) function to db/queries.py
- [x] 3.2 Add upsert_email(email_data: dict) function to db/queries.py
- [x] 3.3 Add link_call_to_opportunity(call_id: str, opp_id: str) function
- [x] 3.4 Add get_opportunity(opp_id: str) query returning opportunity with counts of calls/emails
- [x] 3.5 Add get_opportunity_timeline(opp_id: str, limit: int, offset: int) query returning calls and emails sorted chronologically
- [x] 3.6 Add search_opportunities(filters: dict, sort: str, limit: int, offset: int) query with support for owner, stage, health_score, search text
- [x] 3.7 Add get/update sync_status functions for tracking last sync timestamps
- [ ] 3.8 Test all queries with sample data

## 4. Daily Sync Flow Implementation

- [x] 4.1 Create flows/daily_gong_sync.py with main() entry point
- [x] 4.2 Implement sync_opportunities() task that fetches modified opportunities and upserts to database
- [x] 4.3 Implement sync_opportunity_calls() task that fetches calls for each opportunity and creates junction records
- [x] 4.4 Implement sync_opportunity_emails() task that fetches and stores emails with body truncation
- [x] 4.5 Add structured logging for sync progress (counts, errors, timing)
- [x] 4.6 Add error handling that continues on individual failures but logs errors
- [x] 4.7 Update sync_status table with timestamps after successful sync
- [ ] 4.8 Test sync flow locally with `uv run python -m flows.daily_gong_sync`
- [ ] 4.9 Verify idempotency by running sync twice and checking no duplicates created

## 5. Vercel Cron Integration

- [x] 5.1 Create api/cron/daily-sync.py Vercel serverless function that calls flows.daily_gong_sync.main()
- [x] 5.2 Add vercel.json with cron configuration for daily execution at 6am
- [x] 5.3 Add error handling and response formatting for serverless environment
- [ ] 5.4 Test locally using Vercel CLI `vercel dev`
- [ ] 5.5 Document deployment instructions in README for Vercel environment variable setup

## 6. Backend API for Opportunities List

- [x] 6.1 Create app/api/opportunities/route.ts GET handler
- [x] 6.2 Add query parameter parsing for filters (owner, stage, health_score_min/max, search)
- [x] 6.3 Add query parameter parsing for sorting (field, direction) and pagination (page, limit)
- [x] 6.4 Call db.search_opportunities with parsed filters
- [x] 6.5 Return JSON with opportunities array, total count, and pagination metadata
- [x] 6.6 Add error handling for invalid parameters
- [ ] 6.7 Test endpoint with various filter combinations using curl/Postman

## 7. Backend API for Opportunity Detail

- [x] 7.1 Create app/api/opportunities/[id]/route.ts GET handler
- [x] 7.2 Fetch opportunity data with call/email counts using db.get_opportunity
- [x] 7.3 Return 404 if opportunity not found
- [x] 7.4 Return JSON with opportunity metadata
- [ ] 7.5 Test endpoint with valid and invalid IDs

## 8. Backend API for Opportunity Timeline

- [x] 8.1 Create app/api/opportunities/[id]/timeline/route.ts GET handler
- [x] 8.2 Add pagination support (page, limit query params)
- [x] 8.3 Fetch timeline items using db.get_opportunity_timeline
- [x] 8.4 Format response with type-tagged items (call vs email) sorted chronologically
- [x] 8.5 Include summary data only (no transcript/email body in list view)
- [x] 8.6 Return pagination metadata (total, hasMore)
- [ ] 8.7 Test endpoint with different page sizes

## 9. Opportunities List Page UI

- [ ] 9.1 Create app/opportunities/page.tsx with server component for initial data
- [ ] 9.2 Create components/OpportunitiesList.tsx client component for interactive table
- [ ] 9.3 Add search input with debounced onChange handler (300ms)
- [ ] 9.4 Add filter dropdowns for owner, stage (multi-select using shadcn/ui)
- [ ] 9.5 Add health score range filter with slider component
- [ ] 9.6 Add sort controls (close date, health score, amount) with direction toggle
- [ ] 9.7 Add pagination controls (previous, next, page numbers)
- [ ] 9.8 Fetch data from /api/opportunities with useSWR and query string from filters
- [ ] 9.9 Display opportunities in table/card layout with name, account, owner, stage, close date, health score
- [ ] 9.10 Add visual indicators for low health score (<50 = red) and stale opportunities (14+ days = amber)
- [ ] 9.11 Add click handler to navigate to /opportunities/[id]
- [ ] 9.12 Add responsive design for mobile (switch to card layout)
- [ ] 9.13 Test filters, sorting, pagination, and navigation

## 10. Opportunity Detail Page UI

- [ ] 10.1 Create app/opportunities/[id]/page.tsx with dynamic route parameter
- [ ] 10.2 Fetch opportunity data from /api/opportunities/[id] with useSWR
- [ ] 10.3 Create components/OpportunityHeader.tsx displaying name, account, owner, stage, close date, amount, health score
- [ ] 10.4 Add color-coded health indicator (green >70, yellow 40-70, red <40)
- [ ] 10.5 Create components/OpportunityTimeline.tsx for chronological call/email list
- [ ] 10.6 Fetch timeline data from /api/opportunities/[id]/timeline with pagination
- [ ] 10.7 Create components/CallTimelineCard.tsx with collapsed/expanded states
- [ ] 10.8 Create components/EmailTimelineCard.tsx with collapsed/expanded states
- [ ] 10.9 Implement expand/collapse functionality with smooth animations
- [ ] 10.10 Load full transcript/email body only when expanding (lazy loading)
- [ ] 10.11 Add "Load More" button for timeline pagination
- [ ] 10.12 Add breadcrumb navigation (Opportunities > [Opportunity Name])
- [ ] 10.13 Test responsive layout on mobile and desktop

## 11. Holistic Opportunity Coaching Analysis

- [x] 11.1 Create analysis/opportunity_coaching.py module
- [x] 11.2 Implement analyze_opportunity_patterns() function that aggregates coaching scores across all calls
- [x] 11.3 Implement identify_recurring_themes() using Claude to find patterns in transcripts
- [x] 11.4 Implement analyze_objection_progression() tracking objections across timeline
- [x] 11.5 Implement assess_relationship_strength() based on engagement metrics over time
- [x] 11.6 Implement generate_coaching_recommendations() for next steps based on patterns
- [ ] 11.7 Add caching for opportunity-level analysis (cache_key includes all call IDs)
- [ ] 11.8 Test analysis functions with sample opportunities

## 12. Learning Insights from Top Performers

- [x] 12.1 Create analysis/learning_insights.py module
- [x] 12.2 Implement find_similar_won_opportunities() query filtering by product, size, closed-won
- [x] 12.3 Implement aggregate_coaching_patterns() comparing rep vs top performers
- [x] 12.4 Implement extract_exemplar_moments() identifying specific high-scoring call segments
- [x] 12.5 Use Claude to generate comparative analysis with concrete examples
- [x] 12.6 Return structured response with behavioral differences and links to call timestamps
- [ ] 12.7 Test with real closed-won opportunities and verify examples are relevant

## 13. FastMCP Tools for Opportunity Coaching

- [x] 13.1 Create coaching_mcp/tools/analyze_opportunity.py MCP tool
- [x] 13.2 Implement tool that takes opportunity_id and returns holistic insights
- [x] 13.3 Create coaching_mcp/tools/get_learning_insights.py MCP tool
- [x] 13.4 Implement tool that takes rep_email and focus_area, returns comparison to top performers
- [x] 13.5 Register both tools in coaching_mcp/server.py
- [x] 13.6 Add input validation and error handling
- [ ] 13.7 Test tools via Claude Desktop with real opportunity data

## 14. Opportunity Insights UI Component

- [ ] 14.1 Create components/OpportunityInsights.tsx component
- [ ] 14.2 Create backend API endpoint app/api/opportunities/[id]/insights/route.ts
- [ ] 14.3 Call analyze_opportunity tool and return formatted insights
- [ ] 14.4 Display insights section on opportunity detail page above timeline
- [ ] 14.5 Show recurring themes, objection patterns, relationship trends
- [ ] 14.6 Display 3-5 actionable coaching recommendations
- [ ] 14.7 Add expand/collapse functionality for insights section
- [ ] 14.8 Add skeleton loader during AI analysis
- [ ] 14.9 Ensure insights load within 5 seconds
- [ ] 14.10 Test with various opportunities and verify relevance

## 15. Integration Testing and Polish

- [ ] 15.1 Test full flow: run daily sync → verify data in database → view in UI
- [ ] 15.2 Test opportunity search with all filter combinations
- [ ] 15.3 Test timeline pagination with opportunity having 50+ items
- [ ] 15.4 Test expand/collapse for calls and emails
- [ ] 15.5 Test opportunity insights generation end-to-end
- [ ] 15.6 Test learning insights MCP tool with various focus areas
- [ ] 15.7 Verify mobile responsive design on phone and tablet
- [ ] 15.8 Test keyboard navigation and screen reader accessibility
- [ ] 15.9 Check performance: opportunities list loads <500ms, detail page <1s
- [ ] 15.10 Verify sync idempotency and error recovery
- [ ] 15.11 Test Vercel cron locally with `vercel dev`
- [ ] 15.12 Document setup instructions for local development and Vercel deployment
