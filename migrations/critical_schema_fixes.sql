-- Critical Schema Fixes for Production Readiness
-- Author: Dev1
-- Date: October 16, 2025
-- Purpose: Fix schema mismatches and add critical indexes

-- =====================================================
-- PHASE 1: CRITICAL SCHEMA FIXES
-- =====================================================

-- 1.1 Fix field name mismatches
-- Note: These may need to be adjusted based on actual model definitions

-- Add missing columns if they don't exist
ALTER TABLE workflows 
ADD COLUMN IF NOT EXISTS title VARCHAR(500),
ADD COLUMN IF NOT EXISTS layer2_extracted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS layer3_extracted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS unified_extraction_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS unified_extraction_success BOOLEAN DEFAULT FALSE;

-- Add missing columns to node contexts
ALTER TABLE workflow_node_contexts 
ADD COLUMN IF NOT EXISTS node_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS node_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS node_type VARCHAR(100),
ADD COLUMN IF NOT EXISTS node_position JSONB,
ADD COLUMN IF NOT EXISTS sticky_title VARCHAR(500),
ADD COLUMN IF NOT EXISTS sticky_content TEXT,
ADD COLUMN IF NOT EXISTS sticky_markdown TEXT,
ADD COLUMN IF NOT EXISTS match_confidence FLOAT,
ADD COLUMN IF NOT EXISTS extraction_method VARCHAR(50),
ADD COLUMN IF NOT EXISTS extracted_at TIMESTAMP DEFAULT NOW();

-- Add missing columns to standalone docs
ALTER TABLE workflow_standalone_docs 
ADD COLUMN IF NOT EXISTS doc_id SERIAL,
ADD COLUMN IF NOT EXISTS doc_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS doc_title VARCHAR(500),
ADD COLUMN IF NOT EXISTS doc_content TEXT,
ADD COLUMN IF NOT EXISTS doc_markdown TEXT,
ADD COLUMN IF NOT EXISTS doc_position JSONB,
ADD COLUMN IF NOT EXISTS confidence_score FLOAT,
ADD COLUMN IF NOT EXISTS extracted_at TIMESTAMP DEFAULT NOW();

-- =====================================================
-- PHASE 2: CRITICAL INDEXES
-- =====================================================

-- 2.1 Performance indexes for workflows
CREATE INDEX IF NOT EXISTS idx_workflows_extraction_status 
ON workflows (unified_extraction_success, layer2_scraped, layer3_scraped);

CREATE INDEX IF NOT EXISTS idx_workflows_created_at 
ON workflows (created_at);

CREATE INDEX IF NOT EXISTS idx_workflows_updated_at 
ON workflows (updated_at);

CREATE INDEX IF NOT EXISTS idx_workflows_title 
ON workflows (title);

-- 2.2 Performance indexes for node contexts
CREATE INDEX IF NOT EXISTS idx_node_contexts_workflow_id 
ON workflow_node_contexts (workflow_id);

CREATE INDEX IF NOT EXISTS idx_node_contexts_node_type 
ON workflow_node_contexts (node_type);

CREATE INDEX IF NOT EXISTS idx_node_contexts_confidence 
ON workflow_node_contexts (match_confidence);

-- 2.3 Performance indexes for standalone docs
CREATE INDEX IF NOT EXISTS idx_standalone_docs_workflow_id 
ON workflow_standalone_docs (workflow_id);

CREATE INDEX IF NOT EXISTS idx_standalone_docs_type 
ON workflow_standalone_docs (doc_type);

CREATE INDEX IF NOT EXISTS idx_standalone_docs_confidence 
ON workflow_standalone_docs (confidence_score);

-- 2.4 Performance indexes for extraction snapshots
CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_workflow_layer 
ON workflow_extraction_snapshots (workflow_id, layer);

CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_created_at 
ON workflow_extraction_snapshots (created_at);

-- 2.5 JSONB indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_workflows_metadata_gin 
ON workflows USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_node_contexts_position_gin 
ON workflow_node_contexts USING GIN (node_position);

CREATE INDEX IF NOT EXISTS idx_standalone_docs_position_gin 
ON workflow_standalone_docs USING GIN (doc_position);

CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_payload_gin 
ON workflow_extraction_snapshots USING GIN (payload);

-- =====================================================
-- PHASE 3: FOREIGN KEY CONSTRAINTS
-- =====================================================

-- 3.1 Add foreign key constraints for data integrity
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_node_contexts_workflow') THEN
        ALTER TABLE workflow_node_contexts 
        ADD CONSTRAINT fk_node_contexts_workflow 
        FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_standalone_docs_workflow') THEN
        ALTER TABLE workflow_standalone_docs 
        ADD CONSTRAINT fk_standalone_docs_workflow 
        FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_extraction_snapshots_workflow') THEN
        ALTER TABLE workflow_extraction_snapshots 
        ADD CONSTRAINT fk_extraction_snapshots_workflow 
        FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE;
    END IF;
END $$;

-- =====================================================
-- PHASE 4: DATA VALIDATION CONSTRAINTS
-- =====================================================

-- 4.1 Add data validation constraints
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_workflow_id_format') THEN
        ALTER TABLE workflows 
        ADD CONSTRAINT chk_workflow_id_format 
        CHECK (workflow_id ~ '^[0-9]+$');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_url_format') THEN
        ALTER TABLE workflows 
        ADD CONSTRAINT chk_url_format 
        CHECK (url ~ '^https://n8n\.io/workflows/');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_node_confidence_range') THEN
        ALTER TABLE workflow_node_contexts 
        ADD CONSTRAINT chk_node_confidence_range 
        CHECK (match_confidence >= 0 AND match_confidence <= 1);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_doc_confidence_range') THEN
        ALTER TABLE workflow_standalone_docs 
        ADD CONSTRAINT chk_doc_confidence_range 
        CHECK (confidence_score >= 0 AND confidence_score <= 1);
    END IF;
END $$;

-- =====================================================
-- PHASE 5: ANALYTICS VIEWS
-- =====================================================

-- 5.1 Workflow extraction summary view
CREATE OR REPLACE VIEW workflow_extraction_summary AS
SELECT 
    w.workflow_id,
    w.title,
    w.url,
    w.unified_extraction_success,
    w.layer2_scraped,
    w.layer3_scraped,
    w.unified_extraction_at,
    w.created_at,
    w.updated_at,
    COUNT(DISTINCT nc.id) as node_context_count,
    COUNT(DISTINCT sd.id) as standalone_doc_count,
    COUNT(DISTINCT es.id) as snapshot_count
FROM workflows w
LEFT JOIN workflow_node_contexts nc ON w.workflow_id = nc.workflow_id
LEFT JOIN workflow_standalone_docs sd ON w.workflow_id = sd.workflow_id
LEFT JOIN workflow_extraction_snapshots es ON w.workflow_id = es.workflow_id
GROUP BY w.workflow_id, w.title, w.url, w.unified_extraction_success, 
         w.layer2_scraped, w.layer3_scraped, w.unified_extraction_at,
         w.created_at, w.updated_at;

-- 5.2 Extraction analytics view
CREATE OR REPLACE VIEW extraction_analytics AS
SELECT 
    DATE_TRUNC('day', created_at) as extraction_date,
    COUNT(*) as total_workflows,
    COUNT(*) FILTER (WHERE unified_extraction_success = true) as successful_extractions,
    COUNT(*) FILTER (WHERE layer2_scraped = true) as layer2_completed,
    COUNT(*) FILTER (WHERE layer3_scraped = true) as layer3_completed,
    ROUND(AVG(EXTRACT(EPOCH FROM (unified_extraction_at - created_at))), 2) as avg_extraction_time_seconds
FROM workflows
WHERE created_at IS NOT NULL
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY extraction_date DESC;

-- 5.3 Performance metrics view
CREATE OR REPLACE VIEW performance_metrics AS
SELECT 
    'Node Contexts' as metric_type,
    COUNT(*) as total_count,
    ROUND(AVG(match_confidence), 3) as avg_confidence,
    ROUND(MIN(match_confidence), 3) as min_confidence,
    ROUND(MAX(match_confidence), 3) as max_confidence
FROM workflow_node_contexts
WHERE match_confidence IS NOT NULL
UNION ALL
SELECT 
    'Standalone Docs' as metric_type,
    COUNT(*) as total_count,
    ROUND(AVG(confidence_score), 3) as avg_confidence,
    ROUND(MIN(confidence_score), 3) as min_confidence,
    ROUND(MAX(confidence_score), 3) as max_confidence
FROM workflow_standalone_docs
WHERE confidence_score IS NOT NULL;

-- =====================================================
-- PHASE 6: DATA QUALITY MONITORING
-- =====================================================

-- 6.1 Data quality metrics view
CREATE OR REPLACE VIEW data_quality_metrics AS
SELECT 
    'Workflows' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE title IS NULL OR title = '') as missing_titles,
    COUNT(*) FILTER (WHERE url IS NULL OR url = '') as missing_urls,
    COUNT(*) FILTER (WHERE description IS NULL OR description = '') as missing_descriptions,
    COUNT(*) FILTER (WHERE unified_extraction_success IS NULL) as missing_extraction_status
FROM workflows
UNION ALL
SELECT 
    'Node Contexts' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE node_name IS NULL OR node_name = '') as missing_names,
    COUNT(*) FILTER (WHERE sticky_content IS NULL OR sticky_content = '') as missing_content,
    COUNT(*) FILTER (WHERE match_confidence IS NULL) as missing_confidence,
    0 as missing_extraction_status
FROM workflow_node_contexts
UNION ALL
SELECT 
    'Standalone Docs' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE doc_title IS NULL OR doc_title = '') as missing_titles,
    COUNT(*) FILTER (WHERE doc_content IS NULL OR doc_content = '') as missing_content,
    COUNT(*) FILTER (WHERE confidence_score IS NULL) as missing_confidence,
    0 as missing_extraction_status
FROM workflow_standalone_docs;

-- =====================================================
-- PHASE 7: MAINTENANCE PROCEDURES
-- =====================================================

-- 7.1 Automated maintenance function
CREATE OR REPLACE FUNCTION perform_maintenance()
RETURNS void AS $$
BEGIN
    -- Update statistics
    ANALYZE workflows;
    ANALYZE workflow_node_contexts;
    ANALYZE workflow_standalone_docs;
    ANALYZE workflow_extraction_snapshots;
    
    -- Clean up old extraction snapshots (keep last 6 months)
    DELETE FROM workflow_extraction_snapshots 
    WHERE created_at < NOW() - INTERVAL '6 months';
    
    -- Log maintenance completion
    RAISE NOTICE 'Maintenance completed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- 7.2 Data cleanup function
CREATE OR REPLACE FUNCTION cleanup_orphaned_data()
RETURNS void AS $$
BEGIN
    -- Remove orphaned node contexts
    DELETE FROM workflow_node_contexts 
    WHERE workflow_id NOT IN (SELECT workflow_id FROM workflows);
    
    -- Remove orphaned standalone docs
    DELETE FROM workflow_standalone_docs 
    WHERE workflow_id NOT IN (SELECT workflow_id FROM workflows);
    
    -- Remove orphaned extraction snapshots
    DELETE FROM workflow_extraction_snapshots 
    WHERE workflow_id NOT IN (SELECT workflow_id FROM workflows);
    
    -- Log cleanup completion
    RAISE NOTICE 'Orphaned data cleanup completed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Critical schema fixes completed successfully!';
    RAISE NOTICE 'Added indexes, constraints, and views for production readiness.';
    RAISE NOTICE 'Run ANALYZE to update table statistics.';
END $$;
