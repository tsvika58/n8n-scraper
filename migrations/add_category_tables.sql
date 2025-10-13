-- ============================================================================
-- N8N Workflow Category System - Database Schema
-- ============================================================================
-- 
-- This migration adds support for workflow categorization with many-to-many
-- relationships (workflows can have multiple categories).
--
-- Tables Created:
-- 1. categories - Master list of all categories
-- 2. workflow_categories - Junction table linking workflows to categories
--
-- Author: N8N Scraper System
-- Date: October 13, 2025
-- ============================================================================

-- ============================================================================
-- TABLE: categories
-- ============================================================================
-- Stores all unique workflow categories discovered from n8n.io

CREATE TABLE IF NOT EXISTS categories (
    -- Primary Key
    category_id SERIAL PRIMARY KEY,
    
    -- Category Information
    category_slug VARCHAR(255) NOT NULL UNIQUE,  -- URL-friendly slug (e.g., "lead-generation")
    category_name VARCHAR(255) NOT NULL,          -- Display name (e.g., "Lead Generation")
    
    -- Discovery Information
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_seen_workflow_id VARCHAR(50),            -- First workflow where we found this category
    
    -- Statistics
    workflow_count INTEGER DEFAULT 0,              -- Number of workflows in this category
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    is_main_category BOOLEAN DEFAULT FALSE,        -- True for 7 main categories (AI, Sales, etc.)
    parent_category_slug VARCHAR(255),             -- For subcategory hierarchy (optional)
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for categories table
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(category_slug);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(category_name);
CREATE INDEX IF NOT EXISTS idx_categories_main ON categories(is_main_category);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_category_slug);

-- ============================================================================
-- TABLE: workflow_categories
-- ============================================================================
-- Junction table for many-to-many relationship between workflows and categories

CREATE TABLE IF NOT EXISTS workflow_categories (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    category_slug VARCHAR(255) NOT NULL REFERENCES categories(category_slug) ON DELETE CASCADE,
    
    -- Metadata
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_primary BOOLEAN DEFAULT FALSE,              -- True if this is the main category for the workflow
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique workflow-category pairs
    UNIQUE(workflow_id, category_slug)
);

-- Indexes for workflow_categories table
CREATE INDEX IF NOT EXISTS idx_workflow_categories_workflow ON workflow_categories(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_categories_category ON workflow_categories(category_slug);
CREATE INDEX IF NOT EXISTS idx_workflow_categories_primary ON workflow_categories(is_primary);

-- ============================================================================
-- FUNCTION: Update category workflow count
-- ============================================================================
-- Automatically updates the workflow_count when relationships are added/removed

CREATE OR REPLACE FUNCTION update_category_workflow_count()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the workflow count for the affected category
    IF TG_OP = 'INSERT' THEN
        UPDATE categories 
        SET workflow_count = workflow_count + 1,
            last_updated = CURRENT_TIMESTAMP
        WHERE category_slug = NEW.category_slug;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE categories 
        SET workflow_count = workflow_count - 1,
            last_updated = CURRENT_TIMESTAMP
        WHERE category_slug = OLD.category_slug;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_category_count ON workflow_categories;
CREATE TRIGGER trigger_update_category_count
AFTER INSERT OR DELETE ON workflow_categories
FOR EACH ROW
EXECUTE FUNCTION update_category_workflow_count();

-- ============================================================================
-- SEED DATA: Main Categories
-- ============================================================================
-- Insert the 7 main categories from n8n.io navigation

INSERT INTO categories (category_slug, category_name, is_main_category) VALUES
    ('ai', 'AI', TRUE),
    ('sales', 'Sales', TRUE),
    ('it-ops', 'IT Ops', TRUE),
    ('marketing', 'Marketing', TRUE),
    ('document-ops', 'Document Ops', TRUE),
    ('support', 'Support', TRUE),
    ('other', 'Other', TRUE)
ON CONFLICT (category_slug) DO NOTHING;

-- ============================================================================
-- VIEWS: Category Analytics
-- ============================================================================

-- View: Category statistics with workflow counts
CREATE OR REPLACE VIEW category_stats AS
SELECT 
    c.category_slug,
    c.category_name,
    c.is_main_category,
    c.parent_category_slug,
    COUNT(DISTINCT wc.workflow_id) as workflow_count,
    c.discovered_at,
    c.last_updated
FROM categories c
LEFT JOIN workflow_categories wc ON c.category_slug = wc.category_slug
GROUP BY c.category_id, c.category_slug, c.category_name, c.is_main_category, 
         c.parent_category_slug, c.discovered_at, c.last_updated
ORDER BY workflow_count DESC;

-- View: Workflows with their categories
CREATE OR REPLACE VIEW workflows_with_categories AS
SELECT 
    w.workflow_id,
    w.url,
    STRING_AGG(c.category_name, ', ' ORDER BY wc.is_primary DESC, c.category_name) as categories,
    STRING_AGG(c.category_slug, ', ' ORDER BY wc.is_primary DESC, c.category_slug) as category_slugs,
    COUNT(wc.category_slug) as category_count
FROM workflows w
LEFT JOIN workflow_categories wc ON w.workflow_id = wc.workflow_id
LEFT JOIN categories c ON wc.category_slug = c.category_slug
GROUP BY w.workflow_id, w.url
ORDER BY w.workflow_id;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE categories IS 'Master list of all workflow categories discovered from n8n.io';
COMMENT ON TABLE workflow_categories IS 'Many-to-many junction table linking workflows to categories';
COMMENT ON COLUMN categories.category_slug IS 'URL-friendly slug extracted from category page URLs';
COMMENT ON COLUMN categories.is_main_category IS 'True for the 7 main categories in n8n navigation';
COMMENT ON COLUMN workflow_categories.is_primary IS 'True if this is the primary/main category for the workflow';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
SELECT 
    table_name, 
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name IN ('categories', 'workflow_categories')
ORDER BY table_name;

-- Show main categories
SELECT category_slug, category_name, is_main_category, workflow_count 
FROM categories 
WHERE is_main_category = TRUE
ORDER BY category_name;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================


