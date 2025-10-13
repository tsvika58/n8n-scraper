-- ============================================================================
-- MIGRATION: Add Layer 2 Enhanced Fields to workflow_structure
-- ============================================================================
-- Date: October 13, 2025
-- Purpose: Support iframe data extraction from all 4 phases
-- Author: Developer-2
-- 
-- This migration adds support for:
--   • Phase 1: Node metadata from demo iframe
--   • Phase 2: Visual layout (positions, canvas state, spatial metrics)
--   • Phase 3: Enhanced text content with categorization
--   • Phase 4: Media content (videos, images, SVGs)
--   • Extraction source tracking
--   • Completeness metrics
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Add new JSONB columns for iframe data
-- ============================================================================

ALTER TABLE workflow_structure
ADD COLUMN IF NOT EXISTS iframe_data JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS visual_layout JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS enhanced_content JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS media_content JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS extraction_sources JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS completeness_metrics JSONB DEFAULT NULL;

-- ============================================================================
-- STEP 2: Add GIN indexes for JSONB columns (performance optimization)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_workflow_structure_iframe_data 
ON workflow_structure USING GIN (iframe_data);

CREATE INDEX IF NOT EXISTS idx_workflow_structure_visual_layout 
ON workflow_structure USING GIN (visual_layout);

CREATE INDEX IF NOT EXISTS idx_workflow_structure_enhanced_content 
ON workflow_structure USING GIN (enhanced_content);

CREATE INDEX IF NOT EXISTS idx_workflow_structure_media_content 
ON workflow_structure USING GIN (media_content);

-- ============================================================================
-- STEP 3: Add column comments for documentation
-- ============================================================================

COMMENT ON COLUMN workflow_structure.iframe_data IS 
'Phase 1: Node metadata from demo iframe (node names, types, IDs, UI hints, icons)';

COMMENT ON COLUMN workflow_structure.visual_layout IS 
'Phase 2: Visual layout data (node X/Y positions, canvas zoom/pan state, spatial metrics like density and bounding box)';

COMMENT ON COLUMN workflow_structure.enhanced_content IS 
'Phase 3: Enhanced text content (all text blocks with categorization, help texts, tooltips, error messages)';

COMMENT ON COLUMN workflow_structure.media_content IS 
'Phase 4: Media content (videos, images, SVGs with categorization and metadata)';

COMMENT ON COLUMN workflow_structure.extraction_sources IS 
'Extraction source tracking (API success, iframe success, extraction times for each source)';

COMMENT ON COLUMN workflow_structure.completeness_metrics IS 
'Data completeness metrics (API only %, iframe only %, merged %)';

-- ============================================================================
-- STEP 4: Add helper function to calculate completeness
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_workflow_completeness(workflow_id_param VARCHAR)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'api_completeness', 
        CASE 
            WHEN workflow_json IS NOT NULL THEN 85.0
            ELSE 0.0
        END,
        'iframe_completeness',
        CASE
            WHEN iframe_data IS NOT NULL THEN 15.0
            ELSE 0.0
        END,
        'total_completeness',
        CASE
            WHEN workflow_json IS NOT NULL AND iframe_data IS NOT NULL THEN 100.0
            WHEN workflow_json IS NOT NULL THEN 85.0
            WHEN iframe_data IS NOT NULL THEN 15.0
            ELSE 0.0
        END
    ) INTO result
    FROM workflow_structure
    WHERE workflow_id = workflow_id_param;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 5: Create view for complete workflow data
-- ============================================================================

CREATE OR REPLACE VIEW workflow_complete_data AS
SELECT 
    w.workflow_id,
    w.url,
    w.layer1_status,
    w.layer2_status,
    w.layer3_status,
    
    -- Layer 2 API data
    ws.workflow_json,
    ws.node_count,
    ws.connection_count,
    ws.extraction_type,
    ws.fallback_used,
    
    -- Layer 2 Enhanced iframe data
    ws.iframe_data,
    ws.visual_layout,
    ws.enhanced_content,
    ws.media_content,
    
    -- Metadata
    ws.extraction_sources,
    ws.completeness_metrics,
    ws.extracted_at,
    
    -- Calculated completeness
    calculate_workflow_completeness(w.workflow_id) as completeness
    
FROM workflows w
LEFT JOIN workflow_structure ws ON w.workflow_id = ws.workflow_id;

-- ============================================================================
-- STEP 6: Add sample data structure comments
-- ============================================================================

COMMENT ON TABLE workflow_structure IS 
'Workflow technical structure including API data and iframe extraction data.

Example iframe_data structure:
{
  "nodes": [{"name": "Node1", "type": "n8n-nodes-base.trigger", ...}],
  "text_content": {"all_text": "...", "text_blocks": [...]},
  "images": [{"src": "/icons/...", "type": "node_icon"}]
}

Example visual_layout structure:
{
  "node_positions": [{"node_name": "Node1", "x": 100, "y": 200, "width": 20, "height": 20}],
  "canvas_state": {"zoom": "1", "width": 709, "height": 520},
  "spatial_metrics": {"density": 0.000275, "bounding_box": {...}}
}

Example enhanced_content structure:
{
  "all_text_blocks": [{"text": "...", "category": "paragraph", "tag": "p"}],
  "help_texts": [{"type": "title", "text": "..."}],
  "total_text_length": 23928
}

Example media_content structure:
{
  "videos": [{"platform": "youtube", "source": "..."}],
  "images": [{"src": "...", "type": "node_icon", "width": "20"}],
  "svgs": [{"viewBox": "0 0 24 24"}],
  "video_count": 1, "image_count": 9, "svg_count": 63
}';

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check new columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'workflow_structure'
AND column_name IN ('iframe_data', 'visual_layout', 'enhanced_content', 'media_content', 'extraction_sources', 'completeness_metrics');

-- Check indexes created
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'workflow_structure'
AND indexname LIKE 'idx_workflow_structure_%';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================


