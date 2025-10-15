-- Layer 3 Comprehensive Schema Migration
-- Creates/updates workflow_content table for comprehensive Layer 3 extraction
-- 
-- Features:
-- - Video URLs storage (array)
-- - Video metadata with deduplication tracking
-- - Transcript storage (JSONB for multiple videos)
-- - Complete DOM content (text + HTML)
-- - Multi-pass extraction metadata
-- - GIN indexes for fast JSONB queries
--
-- Author: Developer-2 (Dev2)
-- Task: SCRAPE-010
-- Date: October 14, 2025

-- Drop old table if exists (WARNING: This deletes data!)
-- Comment this out if you want to preserve existing data
-- DROP TABLE IF EXISTS workflow_content CASCADE;

-- Create comprehensive workflow_content table
CREATE TABLE IF NOT EXISTS workflow_content (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Video Data
    video_urls TEXT[] DEFAULT '{}',                     -- Array of video URLs (deduplicated)
    video_metadata JSONB DEFAULT '[]',                  -- Complete video data including types, titles, etc.
    video_count INTEGER DEFAULT 0,                      -- Total unique videos
    has_videos BOOLEAN DEFAULT FALSE,                   -- Quick check for videos
    
    -- Transcript Data
    transcripts JSONB DEFAULT '{}',                     -- Keyed by video URL
    transcript_count INTEGER DEFAULT 0,                 -- Total transcripts extracted
    has_transcripts BOOLEAN DEFAULT FALSE,              -- Quick check for transcripts
    
    -- Content Data
    content_text TEXT,                                  -- All text content (from DOM traversal)
    content_html TEXT,                                  -- Complete HTML (from DOM traversal)
    content_markdown TEXT,                              -- Markdown formatted content (optional)
    total_text_length INTEGER DEFAULT 0,                -- Character count
    
    -- Media Data
    image_urls TEXT[] DEFAULT '{}',                     -- Array of image URLs
    image_count INTEGER DEFAULT 0,                      -- Total images
    link_urls TEXT[] DEFAULT '{}',                      -- Array of all links
    link_count INTEGER DEFAULT 0,                       -- Total links
    
    -- Iframe Data
    iframe_sources TEXT[] DEFAULT '{}',                 -- Array of iframe sources
    iframe_count INTEGER DEFAULT 0,                     -- Total iframes
    has_iframes BOOLEAN DEFAULT FALSE,                  -- Quick check for iframes
    iframe_content JSONB DEFAULT '[]',                  -- Complete iframe data
    
    -- Meta Data
    meta_tags JSONB DEFAULT '{}',                       -- All meta tags
    data_attributes JSONB DEFAULT '[]',                 -- Data attributes found
    
    -- Extraction Metadata
    extraction_passes JSONB DEFAULT '{}',               -- Results from each pass (1-5)
    deduplication_stats JSONB DEFAULT '{}',             -- Deduplication statistics
    quality_score INTEGER DEFAULT 0,                    -- Quality score (0-100)
    
    -- Validation Data
    content_hash VARCHAR(64),                           -- SHA-256 hash for validation
    screenshot_path TEXT,                               -- Path to validation screenshot
    validation_data JSONB DEFAULT '{}',                 -- Validation metadata
    
    -- Status & Timestamps
    layer3_success BOOLEAN DEFAULT FALSE,               -- Extraction success flag
    layer3_extracted_at TIMESTAMP,                      -- When extracted
    layer3_version VARCHAR(20) DEFAULT '3.0.0-comprehensive',  -- Extractor version
    
    -- Indexes
    CONSTRAINT workflow_content_workflow_id_unique UNIQUE (workflow_id)
);

-- Create GIN indexes for JSONB columns (fast JSON queries)
CREATE INDEX IF NOT EXISTS idx_video_metadata_gin 
    ON workflow_content USING gin(video_metadata);

CREATE INDEX IF NOT EXISTS idx_transcripts_gin 
    ON workflow_content USING gin(transcripts);

CREATE INDEX IF NOT EXISTS idx_iframe_content_gin 
    ON workflow_content USING gin(iframe_content);

CREATE INDEX IF NOT EXISTS idx_meta_tags_gin 
    ON workflow_content USING gin(meta_tags);

CREATE INDEX IF NOT EXISTS idx_extraction_passes_gin 
    ON workflow_content USING gin(extraction_passes);

CREATE INDEX IF NOT EXISTS idx_deduplication_stats_gin 
    ON workflow_content USING gin(deduplication_stats);

-- Create B-tree indexes for common queries
CREATE INDEX IF NOT EXISTS idx_has_videos 
    ON workflow_content(has_videos);

CREATE INDEX IF NOT EXISTS idx_has_transcripts 
    ON workflow_content(has_transcripts);

CREATE INDEX IF NOT EXISTS idx_layer3_success 
    ON workflow_content(layer3_success);

CREATE INDEX IF NOT EXISTS idx_quality_score 
    ON workflow_content(quality_score);

CREATE INDEX IF NOT EXISTS idx_video_count 
    ON workflow_content(video_count);

CREATE INDEX IF NOT EXISTS idx_transcript_count 
    ON workflow_content(transcript_count);

-- Create indexes for array columns (using GIN for array containment queries)
CREATE INDEX IF NOT EXISTS idx_video_urls_gin 
    ON workflow_content USING gin(video_urls);

CREATE INDEX IF NOT EXISTS idx_iframe_sources_gin 
    ON workflow_content USING gin(iframe_sources);

-- Create text search index for content_text (full-text search)
CREATE INDEX IF NOT EXISTS idx_content_text_fulltext 
    ON workflow_content USING gin(to_tsvector('english', COALESCE(content_text, '')));

-- Comments for documentation
COMMENT ON TABLE workflow_content IS 'Comprehensive Layer 3 extraction data with videos, transcripts, and complete content';
COMMENT ON COLUMN workflow_content.video_urls IS 'Array of deduplicated video URLs';
COMMENT ON COLUMN workflow_content.video_metadata IS 'JSONB array of complete video data including type, title, YouTube ID, etc.';
COMMENT ON COLUMN workflow_content.transcripts IS 'JSONB object keyed by video URL containing transcript text';
COMMENT ON COLUMN workflow_content.extraction_passes IS 'JSONB object containing results from each extraction pass (1-5)';
COMMENT ON COLUMN workflow_content.deduplication_stats IS 'JSONB object with raw_count, deduplicated_count, duplicates_removed';

-- Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'workflow_content'
ORDER BY indexname;


