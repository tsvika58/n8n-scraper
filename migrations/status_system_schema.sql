-- Status System Schema Migration
-- Adds new status tracking for scraping vs analytical completion

-- Add new status columns to workflows table
ALTER TABLE workflows 
ADD COLUMN IF NOT EXISTS scraping_status VARCHAR(20) DEFAULT 'not_started',
ADD COLUMN IF NOT EXISTS scraping_quality_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS overall_quality_score INTEGER DEFAULT 0;

-- Create index on scraping_status for efficient filtering
CREATE INDEX IF NOT EXISTS idx_workflows_scraping_status ON workflows(scraping_status);

-- Update existing workflows with calculated status
-- Note: Using available columns from workflows table
UPDATE workflows SET 
    scraping_status = CASE 
        WHEN layer1_success = true AND layer2_success = true AND layer3_success = true THEN 'scraping_complete'
        WHEN layer1_success = true OR layer2_success = true OR layer3_success = true THEN 'scraping_in_progress'
        ELSE 'not_started'
    END,
    scraping_quality_score = CASE 
        WHEN layer3_success = true THEN 100
        WHEN layer2_success = true THEN 75
        WHEN layer1_success = true THEN 25
        ELSE 0
    END,
    overall_quality_score = CASE 
        WHEN layer1_success = true AND layer2_success = true AND layer3_success = true 
             AND layer4_success = true AND layer5_success = true AND layer6_success = true AND layer7_success = true THEN 100
        WHEN layer1_success = true AND layer2_success = true AND layer3_success = true THEN 80
        WHEN layer2_success = true AND layer3_success = true THEN 60
        WHEN layer1_success = true AND layer2_success = true THEN 40
        WHEN layer1_success = true THEN 10
        ELSE 0
    END;

-- Add comments for documentation
COMMENT ON COLUMN workflows.scraping_status IS 'Status of data scraping: not_started, scraping_in_progress, scraping_complete, fully_complete, error';
COMMENT ON COLUMN workflows.scraping_quality_score IS 'Quality score based on L1-L3 scraping completion (0-100)';
COMMENT ON COLUMN workflows.overall_quality_score IS 'Overall quality score including all layers L1-L8 (0-100)';
