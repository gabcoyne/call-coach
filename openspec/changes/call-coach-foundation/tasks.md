## 1. Phase 1: Foundation (Database & Webhook Infrastructure)

- [x] 1.1 Create database schema with 14 tables and partitioning
- [x] 1.2 Add indexes on all critical queries (cache lookups, call searches, transcript FTS)
- [x] 1.3 Create Pydantic models for all database entities
- [x] 1.4 Implement connection pooling utilities (psycopg2)
- [x] 1.5 Create query helper functions for common operations
- [x] 1.6 Implement Gong API client with retries and error handling
- [x] 1.7 Create webhook endpoint with HMAC-SHA256 signature verification
- [x] 1.8 Implement idempotency handling via gong_webhook_id
- [x] 1.9 Build FastAPI webhook server with <500ms response time
- [x] 1.10 Create process_new_call Prefect flow
- [x] 1.11 Implement transcript chunking with 20% overlap
- [x] 1.12 Add SHA256 transcript hashing for cache keys
- [x] 1.13 Build caching utilities (cache lookup, statistics)
- [x] 1.14 Create Docker Compose for local development
- [x] 1.15 Write tests for chunking module
- [x] 1.16 Create comprehensive documentation (README, SETUP, STATUS)

## 2. Phase 2: Knowledge Base Loading

- [ ] 2.1 Create discovery coaching rubric v1.0.0 (JSON format)
- [ ] 2.2 Create product knowledge coaching rubric v1.0.0
- [ ] 2.3 Create objection handling coaching rubric v1.0.0
- [ ] 2.4 Create engagement coaching rubric v1.0.0
- [ ] 2.5 Structure Prefect product documentation (features, use cases, differentiators)
- [ ] 2.6 Structure Horizon product documentation
- [ ] 2.7 Create competitive positioning content (vs Airflow, Temporal, Dagster)
- [ ] 2.8 Implement knowledge base loader (knowledge/loader.py)
- [ ] 2.9 Add CLI commands for loading rubrics and docs
- [ ] 2.10 Validate rubric structure and versioning
- [ ] 2.11 Load all rubrics into coaching_rubrics table
- [ ] 2.12 Load all product docs into knowledge_base table
- [ ] 2.13 Verify knowledge base queries work correctly

## 3. Phase 3: Analysis Engine (Claude API Integration)

- [ ] 3.1 Create product knowledge prompt template
- [ ] 3.2 Create discovery prompt template
- [ ] 3.3 Create objection handling prompt template
- [ ] 3.4 Create engagement prompt template
- [ ] 3.5 Implement Claude API integration with prompt caching
- [ ] 3.6 Replace placeholder in analysis/engine.py with real implementation
- [ ] 3.7 Add structured output parsing for analysis results
- [ ] 3.8 Implement token usage tracking in analysis_runs table
- [ ] 3.9 Create Prefect tasks for each dimension analysis
- [ ] 3.10 Implement parallel execution with .map()
- [ ] 3.11 Add result aggregation across dimensions
- [ ] 3.12 Test analysis with 10 sample calls
- [ ] 3.13 Validate cache hit rate >60%
- [ ] 3.14 Verify score quality matches manual coaching

## 4. Phase 4: FastMCP Server (On-Demand Coaching Tools)

- [ ] 4.1 Initialize FastMCP project in mcp/server.py
- [ ] 4.2 Set up database connection in MCP server
- [ ] 4.3 Implement analyze_call tool
- [ ] 4.4 Implement get_rep_insights tool
- [ ] 4.5 Implement search_calls tool
- [ ] 4.6 Implement compare_calls tool
- [ ] 4.7 Implement analyze_product_knowledge tool
- [ ] 4.8 Implement get_coaching_plan tool
- [ ] 4.9 Implement update_knowledge_base tool
- [ ] 4.10 Implement batch_analyze_calls tool
- [ ] 4.11 Implement export_coaching_report tool
- [ ] 4.12 Add authentication middleware (JWT-based)
- [ ] 4.13 Test all tools in Claude Desktop
- [ ] 4.14 Document tool usage with examples
- [ ] 4.15 Optimize response times (<10s for cached queries)

## 5. Phase 5: Weekly Reviews (Automated Batch Processing)

- [ ] 5.1 Create weekly_coaching_review Prefect flow
- [ ] 5.2 Implement batch call query (last 7 days)
- [ ] 5.3 Add rep performance aggregation logic
- [ ] 5.4 Implement trend analysis (vs previous weeks)
- [ ] 5.5 Create team-wide analytics (top performers, common gaps)
- [ ] 5.6 Build Jinja2 templates for rep-specific reports
- [ ] 5.7 Build template for team summary report
- [ ] 5.8 Implement report generation module
- [ ] 5.9 Add email notification support
- [ ] 5.10 Add Slack notification support
- [ ] 5.11 Schedule flow for Monday 6am PT
- [ ] 5.12 Test weekly review with sample data
- [ ] 5.13 Validate reports sent to correct recipients

## 6. Phase 6: Production Hardening (Monitoring & Security)

- [ ] 6.1 Add comprehensive error handling with exponential backoff
- [ ] 6.2 Implement circuit breaker for Gong API
- [ ] 6.3 Add graceful degradation for Claude API outages
- [ ] 6.4 Create cost monitoring dashboard (token usage, cache hit rate)
- [ ] 6.5 Add latency tracking (webhook response, analysis time)
- [ ] 6.6 Implement error alerting (Slack/PagerDuty)
- [ ] 6.7 Audit webhook signature verification
- [ ] 6.8 Enable database encryption at rest (Neon SSL)
- [ ] 6.9 Create API key rotation procedure
- [ ] 6.10 Define PII data retention policies
- [ ] 6.11 Implement soft delete for departed reps
- [ ] 6.12 Load test with 500 calls/week
- [ ] 6.13 Write unit tests (>80% coverage)
- [ ] 6.14 Write integration tests for flows
- [ ] 6.15 Create user guide for MCP tools
- [ ] 6.16 Create troubleshooting guide
- [ ] 6.17 Write runbook for common issues
- [ ] 6.18 Deploy to production (Neon + Horizon)

## 7. Deployment & Rollout

- [ ] 7.1 Provision Neon production database
- [ ] 7.2 Run database migrations in production
- [ ] 7.3 Configure Gong webhook in production
- [ ] 7.4 Deploy webhook server to hosting platform
- [ ] 7.5 Deploy Prefect flows to Horizon
- [ ] 7.6 Configure environment variables
- [ ] 7.7 Test end-to-end with production Gong webhook
- [ ] 7.8 Pilot with 5 sales managers for 1 week
- [ ] 7.9 Gather feedback and iterate
- [ ] 7.10 Roll out MCP tools to all sales managers
- [ ] 7.11 Enable weekly reviews for full team
- [ ] 7.12 Monitor costs and cache hit rates
- [ ] 7.13 Schedule check-in after 30 days
