-- Opportunity Analysis Cache Table
-- Caches expensive Claude API calls for opportunity-level analysis
-- Cache key includes all call IDs, so it auto-invalidates when calls change

CREATE TABLE IF NOT EXISTS opportunity_analysis_cache (
    cache_key VARCHAR(64) PRIMARY KEY,  -- SHA256 hash
    opportunity_id UUID NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,  -- patterns, themes, objections, relationship, recommendations
    analysis_result JSONB NOT NULL,
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for invalidation by opportunity
CREATE INDEX IF NOT EXISTS idx_opp_analysis_cache_opp_id
ON opportunity_analysis_cache (opportunity_id);

-- Index for cleanup of old cache entries
CREATE INDEX IF NOT EXISTS idx_opp_analysis_cache_cached_at
ON opportunity_analysis_cache (cached_at);

-- Comment explaining cache strategy
COMMENT ON TABLE opportunity_analysis_cache IS
'Caches opportunity-level coaching analysis. Cache key includes all call IDs for the opportunity, so adding a new call automatically invalidates the cache. TTL is 7 days, enforced in application code.';
