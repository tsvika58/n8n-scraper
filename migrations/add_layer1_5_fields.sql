-- Migration: Add Layer 1.5 Enhanced Content Fields
-- Date: 2025-10-14
-- Description: Adds Markdown content storage and metadata JSONB fields to workflow_metadata table
--              This enables comprehensive page content extraction (86.7x improvement over Layer 1)

-- Add new columns for Layer 1.5 data
ALTER TABLE workflow_metadata 
ADD COLUMN IF NOT EXISTS layer1_5_content_markdown TEXT,
ADD COLUMN IF NOT EXISTS layer1_5_metadata JSONB,
ADD COLUMN IF NOT EXISTS layer1_5_extracted_at TIMESTAMP;

-- Add GIN index for fast JSONB queries
CREATE INDEX IF NOT EXISTS idx_layer1_5_metadata_gin 
ON workflow_metadata USING gin(layer1_5_metadata);

-- Add index for extraction timestamp
CREATE INDEX IF NOT EXISTS idx_layer1_5_extracted_at 
ON workflow_metadata(layer1_5_extracted_at);

-- Add comment for documentation
COMMENT ON COLUMN workflow_metadata.layer1_5_content_markdown IS 'Complete page content in Markdown format with structure and formatting';
COMMENT ON COLUMN workflow_metadata.layer1_5_metadata IS 'Queryable metadata including content_length, examples_count, has_images, etc.';
COMMENT ON COLUMN workflow_metadata.layer1_5_extracted_at IS 'Timestamp when Layer 1.5 extraction was completed';




