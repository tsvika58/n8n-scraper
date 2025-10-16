-- Fix Missing Fields Migration
-- Adds missing timestamp fields to workflows table

-- Add missing extraction timestamp fields
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS layer2_extracted_at TIMESTAMP;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS layer3_extracted_at TIMESTAMP;

-- Add unified extraction fields for new approach
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS unified_extraction_success BOOLEAN DEFAULT FALSE;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS unified_extraction_at TIMESTAMP;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflows_layer2_extracted ON workflows(layer2_extracted_at);
CREATE INDEX IF NOT EXISTS idx_workflows_layer3_extracted ON workflows(layer3_extracted_at);
CREATE INDEX IF NOT EXISTS idx_workflows_unified_extraction ON workflows(unified_extraction_success);

-- Add comments for documentation
COMMENT ON COLUMN workflows.layer2_extracted_at IS 'Timestamp when Layer 2 extraction completed';
COMMENT ON COLUMN workflows.layer3_extracted_at IS 'Timestamp when Layer 3 extraction completed';
COMMENT ON COLUMN workflows.unified_extraction_success IS 'Whether unified extraction (L2+L3 combined) was successful';
COMMENT ON COLUMN workflows.unified_extraction_at IS 'Timestamp when unified extraction completed';

