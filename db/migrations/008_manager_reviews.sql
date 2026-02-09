-- Migration 008: Manager Reviews & Feedback Training System
-- Enables managers to review AI analysis, provide their own ratings,
-- and create training data for continuous model improvement

-- ============================================================================
-- Manager Reviews Table
-- ============================================================================
-- Stores manager reviews of AI-analyzed calls, including their own ratings
-- and feedback on what the AI got right or wrong

CREATE TABLE IF NOT EXISTS manager_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    manager_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Manager's Ratings
    overall_score INT CHECK (overall_score >= 0 AND overall_score <= 100),
    dimension_scores JSONB NOT NULL DEFAULT '{}', -- {"discovery": 55, "engagement": 80, ...}

    -- AI Comparison (snapshot at time of review)
    ai_overall_score INT,
    ai_dimension_scores JSONB NOT NULL DEFAULT '{}',
    agreement_level TEXT CHECK (agreement_level IN ('agree', 'mostly', 'disagree')),

    -- Manager Feedback
    what_ai_missed TEXT, -- Free-form text explaining AI errors or omissions
    key_moments JSONB DEFAULT '[]', -- [{"timestamp": 765, "note": "Great budget question", "type": "positive"}, ...]
    coaching_notes TEXT, -- Private notes for the rep

    -- Metadata
    reviewed_at TIMESTAMP DEFAULT NOW(),
    review_duration_seconds INT, -- How long manager spent reviewing

    -- Status
    shared_with_rep BOOLEAN DEFAULT FALSE,
    rep_acknowledged_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT manager_reviews_unique_call_manager UNIQUE(call_id, manager_id)
);

-- Indexes for efficient querying
CREATE INDEX idx_manager_reviews_call ON manager_reviews(call_id);
CREATE INDEX idx_manager_reviews_manager ON manager_reviews(manager_id);
CREATE INDEX idx_manager_reviews_agreement ON manager_reviews(agreement_level);
CREATE INDEX idx_manager_reviews_reviewed_at ON manager_reviews(reviewed_at DESC);
CREATE INDEX idx_manager_reviews_shared ON manager_reviews(shared_with_rep) WHERE shared_with_rep = TRUE;
CREATE INDEX idx_manager_reviews_unacknowledged ON manager_reviews(rep_acknowledged_at) WHERE rep_acknowledged_at IS NULL AND shared_with_rep = TRUE;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_manager_reviews_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER manager_reviews_updated_at
    BEFORE UPDATE ON manager_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_manager_reviews_updated_at();

-- ============================================================================
-- Feedback Training Data Table
-- ============================================================================
-- Stores examples for model fine-tuning, capturing where AI and managers disagree

CREATE TABLE IF NOT EXISTS feedback_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manager_review_id UUID NOT NULL REFERENCES manager_reviews(id) ON DELETE CASCADE,

    -- Input: What the AI analyzed
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    dimension TEXT NOT NULL, -- Which coaching dimension (discovery, engagement, etc.)

    -- AI Output (snapshot at time of analysis)
    ai_score INT NOT NULL,
    ai_reasoning TEXT, -- Extracted from AI analysis (strengths, improvements, etc.)
    ai_rubric_version TEXT, -- Version of rubric used for this analysis

    -- Manager Correction (Ground Truth)
    manager_score INT NOT NULL,
    manager_reasoning TEXT, -- Why manager scored differently

    -- Difference Analysis
    score_delta INT NOT NULL, -- manager_score - ai_score
    delta_category TEXT CHECK (delta_category IN (
        'major_overestimate',    -- AI > 20 points too high
        'minor_overestimate',    -- AI 10-20 points too high
        'accurate',              -- Within ±10 points
        'minor_underestimate',   -- AI 10-20 points too low
        'major_underestimate'    -- AI > 20 points too low
    )),

    -- Training Status
    used_for_training BOOLEAN DEFAULT FALSE,
    training_batch_id UUID, -- Groups examples used together for training
    trained_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CHECK (ai_score >= 0 AND ai_score <= 100),
    CHECK (manager_score >= 0 AND manager_score <= 100)
);

-- Indexes for training data queries
CREATE INDEX idx_training_data_manager_review ON feedback_training_data(manager_review_id);
CREATE INDEX idx_training_data_call ON feedback_training_data(call_id);
CREATE INDEX idx_training_data_dimension ON feedback_training_data(dimension);
CREATE INDEX idx_training_data_delta ON feedback_training_data(score_delta);
CREATE INDEX idx_training_data_delta_category ON feedback_training_data(delta_category);
CREATE INDEX idx_training_data_unused ON feedback_training_data(used_for_training) WHERE used_for_training = FALSE;
CREATE INDEX idx_training_data_batch ON feedback_training_data(training_batch_id) WHERE training_batch_id IS NOT NULL;

-- Trigger to automatically categorize score delta
CREATE OR REPLACE FUNCTION categorize_score_delta()
RETURNS TRIGGER AS $$
BEGIN
    -- Categorize based on score_delta (already calculated as manager_score - ai_score)
    NEW.delta_category = CASE
        WHEN NEW.score_delta > 20 THEN 'major_underestimate'
        WHEN NEW.score_delta >= 10 THEN 'minor_underestimate'
        WHEN NEW.score_delta >= -10 THEN 'accurate'
        WHEN NEW.score_delta >= -20 THEN 'minor_overestimate'
        ELSE 'major_overestimate'
    END;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER feedback_training_data_categorize
    BEFORE INSERT OR UPDATE ON feedback_training_data
    FOR EACH ROW
    EXECUTE FUNCTION categorize_score_delta();

-- ============================================================================
-- Manager Review Statistics View
-- ============================================================================
-- Aggregates manager review patterns for calibration and insights

CREATE OR REPLACE VIEW manager_review_stats AS
SELECT
    mr.manager_id,
    COUNT(*) as total_reviews,
    AVG(mr.review_duration_seconds) as avg_review_duration_seconds,

    -- Agreement rates
    COUNT(*) FILTER (WHERE mr.agreement_level = 'agree') as agree_count,
    COUNT(*) FILTER (WHERE mr.agreement_level = 'mostly') as mostly_count,
    COUNT(*) FILTER (WHERE mr.agreement_level = 'disagree') as disagree_count,

    ROUND(100.0 * COUNT(*) FILTER (WHERE mr.agreement_level = 'agree') / NULLIF(COUNT(*), 0), 1) as agree_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE mr.agreement_level = 'mostly') / NULLIF(COUNT(*), 0), 1) as mostly_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE mr.agreement_level = 'disagree') / NULLIF(COUNT(*), 0), 1) as disagree_pct,

    -- Score deltas (how much managers differ from AI)
    AVG(mr.overall_score - mr.ai_overall_score) as avg_overall_delta,

    -- Shared with reps
    COUNT(*) FILTER (WHERE mr.shared_with_rep = TRUE) as shared_count,
    COUNT(*) FILTER (WHERE mr.rep_acknowledged_at IS NOT NULL) as acknowledged_count

FROM manager_reviews mr
GROUP BY mr.manager_id;

-- ============================================================================
-- Dimension Score Deltas View
-- ============================================================================
-- Shows per-dimension scoring differences between managers and AI

CREATE OR REPLACE VIEW dimension_score_deltas AS
WITH dimension_unpacked AS (
    SELECT
        mr.manager_id,
        mr.call_id,
        mr.reviewed_at,
        dim.key as dimension,
        (dim.value)::int as manager_score,
        (ai_dim.value)::int as ai_score,
        (dim.value)::int - (ai_dim.value)::int as score_delta
    FROM manager_reviews mr
    CROSS JOIN LATERAL jsonb_each(mr.dimension_scores) AS dim(key, value)
    LEFT JOIN LATERAL jsonb_each(mr.ai_dimension_scores) AS ai_dim(key, value)
        ON dim.key = ai_dim.key
    WHERE (ai_dim.value)::int IS NOT NULL
)
SELECT
    manager_id,
    dimension,
    COUNT(*) as review_count,
    AVG(manager_score) as avg_manager_score,
    AVG(ai_score) as avg_ai_score,
    AVG(score_delta) as avg_score_delta,
    STDDEV(score_delta) as stddev_score_delta,
    MIN(score_delta) as min_delta,
    MAX(score_delta) as max_delta
FROM dimension_unpacked
GROUP BY manager_id, dimension;

-- ============================================================================
-- Training Data Summary View
-- ============================================================================
-- Aggregates feedback training data for model improvement insights

CREATE OR REPLACE VIEW training_data_summary AS
SELECT
    dimension,
    delta_category,
    COUNT(*) as example_count,
    AVG(score_delta) as avg_score_delta,
    COUNT(*) FILTER (WHERE used_for_training = FALSE) as unused_count,
    MIN(created_at) as oldest_example,
    MAX(created_at) as newest_example
FROM feedback_training_data
GROUP BY dimension, delta_category
ORDER BY dimension, delta_category;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE manager_reviews IS
'Manager reviews of AI-analyzed calls with their own ratings and feedback';

COMMENT ON TABLE feedback_training_data IS
'Training examples extracted from manager reviews for model fine-tuning';

COMMENT ON VIEW manager_review_stats IS
'Aggregated statistics per manager showing review patterns and AI agreement rates';

COMMENT ON VIEW dimension_score_deltas IS
'Per-dimension scoring differences between managers and AI for calibration';

COMMENT ON VIEW training_data_summary IS
'Summary of available training data for model improvement';

-- ============================================================================
-- Grant Permissions
-- ============================================================================
-- Note: Permissions are managed by the application layer, not database roles
