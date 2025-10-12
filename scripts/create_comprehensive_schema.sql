-- Comprehensive Database Schema Expansion for N8N Scraper
-- Creates 6 new tables with 200+ fields for complete data capture
-- Author: RND Team - Comprehensive Scraping Expansion
-- Date: October 12, 2025

-- ============================================================================
-- PHASE 1: CREATE WORKFLOW BUSINESS INTELLIGENCE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_business_intelligence (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Revenue & Cost Metrics
    revenue_impact DECIMAL(10,2),
    cost_savings DECIMAL(10,2),
    efficiency_gains DECIMAL(5,2),
    time_savings INTEGER,
    resource_savings DECIMAL(10,2),
    error_reduction DECIMAL(5,2),
    productivity_gains DECIMAL(5,2),
    quality_improvements DECIMAL(5,2),
    customer_satisfaction DECIMAL(5,2),
    
    -- Business Value Metrics
    business_value_score DECIMAL(5,2),
    roi_estimate DECIMAL(5,2),
    payback_period INTEGER,
    
    -- Cost Breakdown
    implementation_cost DECIMAL(10,2),
    maintenance_cost DECIMAL(10,2),
    support_cost DECIMAL(10,2),
    training_cost DECIMAL(10,2),
    customization_cost DECIMAL(10,2),
    integration_cost DECIMAL(10,2),
    
    -- Business Context
    business_function VARCHAR(100),
    business_process VARCHAR(100),
    business_outcome VARCHAR(100),
    business_metric VARCHAR(100),
    business_kpi VARCHAR(100),
    business_goal VARCHAR(100),
    
    -- Business Details
    business_requirement TEXT,
    business_constraint TEXT,
    business_risk TEXT,
    business_opportunity TEXT,
    business_challenge TEXT,
    business_solution TEXT,
    business_benefit TEXT,
    business_advantage TEXT,
    business_competitive_advantage TEXT,
    
    -- Business Transformation
    business_innovation TEXT,
    business_transformation TEXT,
    business_digitalization TEXT,
    business_automation TEXT,
    business_optimization TEXT,
    business_standardization TEXT,
    
    -- Compliance & Governance
    business_compliance TEXT,
    business_governance TEXT,
    business_audit TEXT,
    business_security TEXT,
    business_privacy TEXT,
    business_ethics TEXT,
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PHASE 2: CREATE WORKFLOW COMMUNITY DATA TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_community_data (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Engagement Metrics
    comments_count INTEGER DEFAULT 0,
    reviews_count INTEGER DEFAULT 0,
    questions_count INTEGER DEFAULT 0,
    answers_count INTEGER DEFAULT 0,
    discussions_count INTEGER DEFAULT 0,
    mentions_count INTEGER DEFAULT 0,
    
    -- Social Metrics
    bookmarks_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    follows_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    clones_count INTEGER DEFAULT 0,
    remixes_count INTEGER DEFAULT 0,
    
    -- Usage Metrics
    downloads_count INTEGER DEFAULT 0,
    installs_count INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    
    -- Community Ratings
    community_rating DECIMAL(3,2),
    community_rating_count INTEGER DEFAULT 0,
    
    -- Community Analytics
    community_engagement_score DECIMAL(5,2),
    community_activity_score DECIMAL(5,2),
    community_growth_rate DECIMAL(5,2),
    community_retention_rate DECIMAL(5,2),
    community_sentiment_score DECIMAL(5,2),
    community_satisfaction_score DECIMAL(5,2),
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PHASE 3: CREATE WORKFLOW TECHNICAL DETAILS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_technical_details (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- API Information
    api_endpoints JSONB,
    api_authentication_types JSONB,
    api_rate_limits JSONB,
    
    -- Security & Credentials
    credential_requirements JSONB,
    credential_types JSONB,
    security_requirements JSONB,
    
    -- Performance Metrics
    performance_metrics JSONB,
    execution_time DECIMAL(10,3),
    memory_usage DECIMAL(10,2),
    cpu_usage DECIMAL(5,2),
    
    -- Error Handling
    error_handling_patterns JSONB,
    retry_mechanisms JSONB,
    fallback_strategies JSONB,
    
    -- Data Processing
    data_validation_rules JSONB,
    data_transformation_rules JSONB,
    
    -- Workflow Structure
    workflow_triggers JSONB,
    workflow_conditions JSONB,
    workflow_actions JSONB,
    workflow_branches JSONB,
    workflow_loops JSONB,
    workflow_parallelism JSONB,
    
    -- Workflow Management
    workflow_error_handling JSONB,
    workflow_logging JSONB,
    workflow_monitoring JSONB,
    workflow_backup_strategies JSONB,
    workflow_recovery_strategies JSONB,
    workflow_scaling_strategies JSONB,
    workflow_optimization_strategies JSONB,
    
    -- Development & Deployment
    workflow_testing_strategies JSONB,
    workflow_deployment_strategies JSONB,
    workflow_maintenance_strategies JSONB,
    workflow_support_strategies JSONB,
    
    -- Documentation & Examples
    workflow_documentation_level VARCHAR(50),
    workflow_tutorial_level VARCHAR(50),
    workflow_example_count INTEGER DEFAULT 0,
    workflow_template_count INTEGER DEFAULT 0,
    
    -- Capability Levels
    workflow_customization_level VARCHAR(50),
    workflow_configuration_level VARCHAR(50),
    workflow_integration_level VARCHAR(50),
    workflow_extension_level VARCHAR(50),
    workflow_automation_level VARCHAR(50),
    workflow_intelligence_level VARCHAR(50),
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PHASE 4: CREATE WORKFLOW PERFORMANCE ANALYTICS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_performance_analytics (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Execution Metrics
    execution_success_rate DECIMAL(5,2),
    execution_failure_rate DECIMAL(5,2),
    execution_error_rate DECIMAL(5,2),
    
    -- Performance Data
    performance_benchmarks JSONB,
    performance_metrics JSONB,
    performance_trends JSONB,
    
    -- Usage Analytics
    usage_statistics JSONB,
    usage_patterns JSONB,
    usage_analytics JSONB,
    
    -- Error Analytics
    error_analytics JSONB,
    error_patterns JSONB,
    error_trends JSONB,
    
    -- Optimization
    optimization_opportunities JSONB,
    optimization_recommendations JSONB,
    
    -- Scaling
    scaling_requirements JSONB,
    scaling_limitations JSONB,
    scaling_recommendations JSONB,
    
    -- Monitoring
    monitoring_requirements JSONB,
    monitoring_metrics JSONB,
    monitoring_alerts JSONB,
    
    -- Cost Analysis
    maintenance_cost DECIMAL(10,2),
    support_cost DECIMAL(10,2),
    training_cost DECIMAL(10,2),
    documentation_cost DECIMAL(10,2),
    testing_cost DECIMAL(10,2),
    deployment_cost DECIMAL(10,2),
    integration_cost DECIMAL(10,2),
    customization_cost DECIMAL(10,2),
    security_cost DECIMAL(10,2),
    compliance_cost DECIMAL(10,2),
    governance_cost DECIMAL(10,2),
    audit_cost DECIMAL(10,2),
    backup_cost DECIMAL(10,2),
    
    -- Requirements
    maintenance_requirements JSONB,
    support_requirements JSONB,
    training_requirements JSONB,
    documentation_requirements JSONB,
    testing_requirements JSONB,
    deployment_requirements JSONB,
    integration_requirements JSONB,
    customization_requirements JSONB,
    security_requirements JSONB,
    compliance_requirements JSONB,
    governance_requirements JSONB,
    audit_requirements JSONB,
    backup_requirements JSONB,
    
    -- Levels
    support_level VARCHAR(50),
    training_level VARCHAR(50),
    documentation_level VARCHAR(50),
    testing_level VARCHAR(50),
    deployment_level VARCHAR(50),
    integration_level VARCHAR(50),
    customization_level VARCHAR(50),
    security_level VARCHAR(50),
    compliance_level VARCHAR(50),
    governance_level VARCHAR(50),
    audit_level VARCHAR(50),
    backup_level VARCHAR(50),
    
    -- Schedules
    maintenance_schedule JSONB,
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PHASE 5: CREATE WORKFLOW RELATIONSHIPS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_relationships (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Family Relationships
    parent_workflows JSONB,
    child_workflows JSONB,
    sibling_workflows JSONB,
    
    -- Dependencies
    dependent_workflows JSONB,
    dependency_workflows JSONB,
    prerequisite_workflows JSONB,
    
    -- Similarity & Alternatives
    related_workflows JSONB,
    similar_workflows JSONB,
    alternative_workflows JSONB,
    
    -- Version Control
    workflow_versions JSONB,
    workflow_branches JSONB,
    workflow_forks JSONB,
    
    -- Derivative Works
    workflow_clones JSONB,
    workflow_remixes JSONB,
    workflow_adaptations JSONB,
    
    -- Extensions & Integrations
    workflow_integrations JSONB,
    workflow_extensions JSONB,
    workflow_plugins JSONB,
    
    -- Support Materials
    workflow_templates JSONB,
    workflow_examples JSONB,
    workflow_tutorials JSONB,
    workflow_documentation JSONB,
    workflow_guides JSONB,
    workflow_manuals JSONB,
    
    -- Community & Support
    workflow_support JSONB,
    workflow_community JSONB,
    workflow_forums JSONB,
    
    -- Updates & Maintenance
    workflow_updates JSONB,
    workflow_patches JSONB,
    workflow_fixes JSONB,
    workflow_migrations JSONB,
    workflow_upgrades JSONB,
    workflow_downgrades JSONB,
    
    -- Lifecycle
    workflow_retirements JSONB,
    workflow_deprecations JSONB,
    workflow_archivals JSONB,
    
    -- Legal & Attribution
    workflow_licenses JSONB,
    workflow_permissions JSONB,
    workflow_restrictions JSONB,
    workflow_ownership JSONB,
    workflow_attribution JSONB,
    workflow_credits JSONB,
    
    -- Collaboration
    workflow_collaboration JSONB,
    workflow_contributors JSONB,
    workflow_maintainers JSONB,
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PHASE 6: CREATE WORKFLOW ENHANCED CONTENT TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_enhanced_content (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Enhanced Content
    tutorial_content TEXT,
    documentation_content TEXT,
    faq_content TEXT,
    troubleshooting_content TEXT,
    best_practices_content TEXT,
    
    -- Video Content
    video_count INTEGER DEFAULT 0,
    video_duration INTEGER DEFAULT 0,
    video_quality VARCHAR(50),
    video_views INTEGER DEFAULT 0,
    
    -- Image Content
    image_count INTEGER DEFAULT 0,
    image_types JSONB,
    image_quality VARCHAR(50),
    image_alt_text JSONB,
    
    -- Diagram Content
    diagram_count INTEGER DEFAULT 0,
    flowchart_count INTEGER DEFAULT 0,
    architecture_count INTEGER DEFAULT 0,
    
    -- Example Content
    code_example_count INTEGER DEFAULT 0,
    configuration_example_count INTEGER DEFAULT 0,
    use_case_example_count INTEGER DEFAULT 0,
    business_case_example_count INTEGER DEFAULT 0,
    integration_example_count INTEGER DEFAULT 0,
    customization_example_count INTEGER DEFAULT 0,
    performance_example_count INTEGER DEFAULT 0,
    security_example_count INTEGER DEFAULT 0,
    maintenance_example_count INTEGER DEFAULT 0,
    support_example_count INTEGER DEFAULT 0,
    community_example_count INTEGER DEFAULT 0,
    feedback_example_count INTEGER DEFAULT 0,
    update_example_count INTEGER DEFAULT 0,
    version_example_count INTEGER DEFAULT 0,
    migration_example_count INTEGER DEFAULT 0,
    upgrade_example_count INTEGER DEFAULT 0,
    troubleshooting_example_count INTEGER DEFAULT 0,
    debugging_example_count INTEGER DEFAULT 0,
    
    -- Metadata
    extracted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PHASE 7: UPDATE EXISTING TABLES WITH MISSING FIELDS
-- ============================================================================

-- Add missing fields to workflows table
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS version VARCHAR(50);
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS fork_count INTEGER DEFAULT 0;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS clone_count INTEGER DEFAULT 0;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS star_count INTEGER DEFAULT 0;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS download_count INTEGER DEFAULT 0;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT true;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT false;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT false;

-- Add missing fields to workflow_metadata table
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS author_id VARCHAR(100);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS author_followers INTEGER DEFAULT 0;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS author_workflows_count INTEGER DEFAULT 0;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS author_verified BOOLEAN DEFAULT false;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS author_bio TEXT;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS author_location VARCHAR(100);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_rating DECIMAL(3,2);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_rating_count INTEGER DEFAULT 0;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_reviews_count INTEGER DEFAULT 0;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_difficulty_score DECIMAL(5,2);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_complexity_score DECIMAL(5,2);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_estimated_time INTEGER;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_skill_level VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_industry VARCHAR(100);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_company_size VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_use_case_category VARCHAR(100);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_business_value DECIMAL(5,2);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_roi_estimate DECIMAL(5,2);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_maintenance_level VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_support_level VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_security_level VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_compliance_level VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_integration_count INTEGER DEFAULT 0;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_dependency_count INTEGER DEFAULT 0;
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_customization_level VARCHAR(50);
ALTER TABLE workflow_metadata ADD COLUMN IF NOT EXISTS workflow_scalability_level VARCHAR(50);

-- ============================================================================
-- PHASE 8: CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Business Intelligence Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_business_intelligence_workflow_id ON workflow_business_intelligence(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_business_intelligence_roi ON workflow_business_intelligence(roi_estimate);
CREATE INDEX IF NOT EXISTS idx_workflow_business_intelligence_value ON workflow_business_intelligence(business_value_score);

-- Community Data Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_community_data_workflow_id ON workflow_community_data(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_community_data_engagement ON workflow_community_data(community_engagement_score);
CREATE INDEX IF NOT EXISTS idx_workflow_community_data_rating ON workflow_community_data(community_rating);

-- Technical Details Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_technical_details_workflow_id ON workflow_technical_details(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_technical_details_performance ON workflow_technical_details(execution_time);

-- Performance Analytics Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_performance_analytics_workflow_id ON workflow_performance_analytics(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_performance_analytics_success ON workflow_performance_analytics(execution_success_rate);

-- Relationships Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_relationships_workflow_id ON workflow_relationships(workflow_id);

-- Enhanced Content Indexes
CREATE INDEX IF NOT EXISTS idx_workflow_enhanced_content_workflow_id ON workflow_enhanced_content(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_enhanced_content_video_count ON workflow_enhanced_content(video_count);

-- Updated workflows table indexes
CREATE INDEX IF NOT EXISTS idx_workflows_fork_count ON workflows(fork_count);
CREATE INDEX IF NOT EXISTS idx_workflows_star_count ON workflows(star_count);
CREATE INDEX IF NOT EXISTS idx_workflows_download_count ON workflows(download_count);
CREATE INDEX IF NOT EXISTS idx_workflows_is_featured ON workflows(is_featured);
CREATE INDEX IF NOT EXISTS idx_workflows_is_verified ON workflows(is_verified);

-- Updated workflow_metadata table indexes
CREATE INDEX IF NOT EXISTS idx_workflow_metadata_author_id ON workflow_metadata(author_id);
CREATE INDEX IF NOT EXISTS idx_workflow_metadata_rating ON workflow_metadata(workflow_rating);
CREATE INDEX IF NOT EXISTS idx_workflow_metadata_difficulty ON workflow_metadata(workflow_difficulty_score);
CREATE INDEX IF NOT EXISTS idx_workflow_metadata_industry ON workflow_metadata(workflow_industry);

-- ============================================================================
-- PHASE 9: CREATE TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for all new tables
CREATE TRIGGER update_workflow_business_intelligence_updated_at BEFORE UPDATE ON workflow_business_intelligence FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_community_data_updated_at BEFORE UPDATE ON workflow_community_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_technical_details_updated_at BEFORE UPDATE ON workflow_technical_details FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_performance_analytics_updated_at BEFORE UPDATE ON workflow_performance_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_relationships_updated_at BEFORE UPDATE ON workflow_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_enhanced_content_updated_at BEFORE UPDATE ON workflow_enhanced_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PHASE 10: VERIFY SCHEMA CREATION
-- ============================================================================

-- Verify all tables were created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename LIKE 'workflow_%' 
ORDER BY tablename;

-- Verify all new tables have the expected columns
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name IN (
    'workflow_business_intelligence',
    'workflow_community_data', 
    'workflow_technical_details',
    'workflow_performance_analytics',
    'workflow_relationships',
    'workflow_enhanced_content'
)
ORDER BY table_name, ordinal_position;

