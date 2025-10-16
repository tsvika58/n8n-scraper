-- Performance Indexes Only
-- Add only the missing performance indexes without changing schema

-- =====================================================
-- PERFORMANCE INDEXES FOR WORKFLOWS
-- =====================================================

-- Index for extraction status queries
CREATE INDEX IF NOT EXISTS idx_workflows_extraction_status 
ON workflows (unified_extraction_success, layer2_success, layer3_success);

-- Index for created_at queries
CREATE INDEX IF NOT EXISTS idx_workflows_created_at 
ON workflows (created_at);

-- Index for updated_at queries  
CREATE INDEX IF NOT EXISTS idx_workflows_updated_at 
ON workflows (updated_at);

-- Index for quality score queries
CREATE INDEX IF NOT EXISTS idx_workflows_quality_score 
ON workflows (quality_score);

-- Index for scraping status queries
CREATE INDEX IF NOT EXISTS idx_workflows_scraping_status 
ON workflows (scraping_status);

-- =====================================================
-- PERFORMANCE INDEXES FOR NODE CONTEXTS
-- =====================================================

-- Index for node type queries
CREATE INDEX IF NOT EXISTS idx_node_contexts_node_type 
ON workflow_node_contexts (node_type);

-- Index for confidence queries
CREATE INDEX IF NOT EXISTS idx_node_contexts_confidence 
ON workflow_node_contexts (match_confidence);

-- Index for extraction method queries
CREATE INDEX IF NOT EXISTS idx_node_contexts_extraction_method 
ON workflow_node_contexts (extraction_method);

-- =====================================================
-- PERFORMANCE INDEXES FOR STANDALONE DOCS
-- =====================================================

-- Index for doc type queries
CREATE INDEX IF NOT EXISTS idx_standalone_docs_doc_type 
ON workflow_standalone_docs (doc_type);

-- Index for confidence queries
CREATE INDEX IF NOT EXISTS idx_standalone_docs_confidence 
ON workflow_standalone_docs (confidence_score);

-- =====================================================
-- PERFORMANCE INDEXES FOR EXTRACTION SNAPSHOTS
-- =====================================================

-- Index for created_at queries
CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_created_at 
ON workflow_extraction_snapshots (created_at);

-- Index for layer queries
CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_layer 
ON workflow_extraction_snapshots (layer);

-- =====================================================
-- JSONB INDEXES FOR EFFICIENT QUERYING
-- =====================================================

-- JSONB index for node positions
CREATE INDEX IF NOT EXISTS idx_node_contexts_position_gin 
ON workflow_node_contexts USING GIN (node_position);

-- JSONB index for doc positions
CREATE INDEX IF NOT EXISTS idx_standalone_docs_position_gin 
ON workflow_standalone_docs USING GIN (doc_position);

-- JSONB index for extraction snapshots payload
CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_payload_gin 
ON workflow_extraction_snapshots USING GIN (payload);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Performance indexes added successfully!';
    RAISE NOTICE 'Database is now optimized for production queries.';
END $$;

