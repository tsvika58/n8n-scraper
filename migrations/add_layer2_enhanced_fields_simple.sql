-- ============================================================================
-- MIGRATION: Add Layer 2 Enhanced Fields (Simplified)
-- ============================================================================
-- Date: October 13, 2025
-- Purpose: Add iframe extraction fields to workflow_structure
-- Safe to run while Layer 1 is scraping
-- ============================================================================

BEGIN;

-- Add new JSONB columns
ALTER TABLE workflow_structure
ADD COLUMN IF NOT EXISTS iframe_data JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS visual_layout JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS enhanced_content JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS media_content JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS extraction_sources JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS completeness_metrics JSONB DEFAULT NULL;

-- Add GIN indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_structure_iframe_data 
ON workflow_structure USING GIN (iframe_data);

CREATE INDEX IF NOT EXISTS idx_workflow_structure_visual_layout 
ON workflow_structure USING GIN (visual_layout);

CREATE INDEX IF NOT EXISTS idx_workflow_structure_enhanced_content 
ON workflow_structure USING GIN (enhanced_content);

CREATE INDEX IF NOT EXISTS idx_workflow_structure_media_content 
ON workflow_structure USING GIN (media_content);

-- Add column comments
COMMENT ON COLUMN workflow_structure.iframe_data IS 
'Phase 1: Node metadata from demo iframe (node names, types, IDs, UI hints, icons)';

COMMENT ON COLUMN workflow_structure.visual_layout IS 
'Phase 2: Visual layout data (node X/Y positions, canvas zoom/pan state, spatial metrics)';

COMMENT ON COLUMN workflow_structure.enhanced_content IS 
'Phase 3: Enhanced text content (all text blocks with categorization, help texts)';

COMMENT ON COLUMN workflow_structure.media_content IS 
'Phase 4: Media content (videos, images, SVGs with categorization)';

COMMENT ON COLUMN workflow_structure.extraction_sources IS 
'Extraction source tracking (API success, iframe success, extraction times)';

COMMENT ON COLUMN workflow_structure.completeness_metrics IS 
'Data completeness metrics (API %, iframe %, merged %)';

COMMIT;

-- Verification
SELECT 'Migration completed successfully!' as status;
SELECT column_name, data_type 
FROM information_schema.columns
WHERE table_name = 'workflow_structure'
AND column_name IN ('iframe_data', 'visual_layout', 'enhanced_content', 'media_content')
ORDER BY column_name;


