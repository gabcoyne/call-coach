-- Knowledge Base Ingestion Schema
-- Supports version tracking, change detection, and ingestion metadata

-- ============================================================================
-- KNOWLEDGE BASE VERSIONING
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_base_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL, -- SHA256 for change detection
    metadata JSONB, -- {url, source, title, sections, code_examples}
    ingestion_timestamp TIMESTAMP DEFAULT NOW(),
    detected_changes BOOLEAN DEFAULT false,
    change_summary TEXT,
    UNIQUE(knowledge_base_id, version_number)
);

CREATE INDEX idx_knowledge_base_versions_product
    ON knowledge_base_versions(ingestion_timestamp DESC);
CREATE INDEX idx_knowledge_base_versions_hash
    ON knowledge_base_versions(content_hash);

-- ============================================================================
-- INGESTION JOBS (Track pipeline runs)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    source VARCHAR NOT NULL, -- 'prefect_docs', 'horizon_docs', 'competitive'
    documents_scraped INT,
    documents_processed INT,
    documents_stored INT,
    documents_updated INT,
    errors JSONB, -- Array of error messages
    metadata JSONB, -- {manifest_version, scraper_config}
    error_message TEXT
);

CREATE INDEX idx_ingestion_jobs_status ON ingestion_jobs(status, completed_at DESC);
CREATE INDEX idx_ingestion_jobs_source ON ingestion_jobs(source, completed_at DESC);

-- ============================================================================
-- SCRAPED DOCUMENTS (Raw content before processing)
-- ============================================================================

CREATE TABLE IF NOT EXISTS scraped_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ingestion_job_id UUID NOT NULL REFERENCES ingestion_jobs(id) ON DELETE CASCADE,
    url VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    raw_content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    processing_status VARCHAR DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processed', 'failed')),
    processing_error TEXT,
    scraped_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

CREATE INDEX idx_scraped_documents_url ON scraped_documents(url);
CREATE INDEX idx_scraped_documents_hash ON scraped_documents(content_hash);
CREATE INDEX idx_scraped_documents_status ON scraped_documents(processing_status);

-- ============================================================================
-- DOCUMENT INDEXING (For semantic search)
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
    section_title VARCHAR NOT NULL,
    section_content TEXT NOT NULL,
    section_order INT,
    has_code_examples BOOLEAN DEFAULT false,
    embedding_vector VECTOR(1536), -- For semantic search with pgvector
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_document_sections_kb ON document_sections(knowledge_base_id);
CREATE INDEX idx_document_sections_vector ON document_sections USING ivfflat(embedding_vector vector_cosine_ops)
    WHERE embedding_vector IS NOT NULL;

-- ============================================================================
-- LINK VALIDATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_base_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
    link_url VARCHAR NOT NULL,
    link_text VARCHAR,
    is_internal BOOLEAN DEFAULT false,
    validation_status VARCHAR CHECK (validation_status IN ('untested', 'valid', 'broken', 'timeout')),
    last_validated TIMESTAMP,
    http_status_code INT,
    validation_error TEXT
);

CREATE INDEX idx_knowledge_base_links_status
    ON knowledge_base_links(validation_status, last_validated DESC);
CREATE INDEX idx_knowledge_base_links_url ON knowledge_base_links(link_url);

-- ============================================================================
-- INGESTION MANIFEST (Track what's been ingested)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ingestion_manifest (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manifest_version VARCHAR NOT NULL,
    last_successful_ingestion TIMESTAMP,
    total_documents INT,
    ingestion_duration_seconds INT,
    metadata JSONB, -- {prefect_count, horizon_count, competitive_count}
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(manifest_version)
);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to detect content changes
CREATE OR REPLACE FUNCTION detect_content_change()
RETURNS TRIGGER AS $$
DECLARE
    prev_version RECORD;
    change_detected BOOLEAN;
BEGIN
    -- Get previous version if exists
    SELECT * INTO prev_version
    FROM knowledge_base_versions
    WHERE knowledge_base_id = NEW.knowledge_base_id
    ORDER BY version_number DESC
    LIMIT 1;

    -- Compare hashes
    IF prev_version IS NULL THEN
        NEW.detected_changes := TRUE;
    ELSE
        NEW.detected_changes := (NEW.content_hash != prev_version.content_hash);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER knowledge_base_change_detection
    BEFORE INSERT ON knowledge_base_versions
    FOR EACH ROW
    EXECUTE FUNCTION detect_content_change();

-- Function to update knowledge base last_updated on version insert
CREATE OR REPLACE FUNCTION update_kb_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE knowledge_base
    SET last_updated = NOW()
    WHERE id = NEW.knowledge_base_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER knowledge_base_version_timestamp
    AFTER INSERT ON knowledge_base_versions
    FOR EACH ROW
    EXECUTE FUNCTION update_kb_last_updated();
