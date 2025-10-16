-- Node Context Schema Migration
-- Creates tables for enhanced Layer 2 and Layer 3 node context extraction

-- Table for node-specific contexts (Layer 2 enhancement)
CREATE TABLE IF NOT EXISTS workflow_node_contexts (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) REFERENCES workflows(workflow_id),
    node_name VARCHAR(255),
    node_type VARCHAR(100),
    node_position JSONB,
    sticky_title VARCHAR(500),
    sticky_content TEXT,
    sticky_markdown TEXT,
    match_confidence FLOAT,
    extraction_method VARCHAR(50),
    extracted_at TIMESTAMP DEFAULT NOW()
);

-- Table for standalone docs (Layer 3 enhancement)
CREATE TABLE IF NOT EXISTS workflow_standalone_docs (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) REFERENCES workflows(workflow_id),
    doc_type VARCHAR(50),
    doc_title VARCHAR(500),
    doc_content TEXT,
    doc_markdown TEXT,
    doc_position JSONB,
    confidence_score FLOAT,
    extracted_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_node_contexts_workflow ON workflow_node_contexts(workflow_id);
CREATE INDEX IF NOT EXISTS idx_standalone_docs_workflow ON workflow_standalone_docs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_node_contexts_node_name ON workflow_node_contexts(node_name);
CREATE INDEX IF NOT EXISTS idx_standalone_docs_type ON workflow_standalone_docs(doc_type);

-- Add comments for documentation
COMMENT ON TABLE workflow_node_contexts IS 'Node-specific sticky notes and contextual explanations extracted from n8n workflow iframes';
COMMENT ON TABLE workflow_standalone_docs IS 'Standalone documentation and section headers not tied to specific nodes';

COMMENT ON COLUMN workflow_node_contexts.node_position IS 'JSONB containing x,y coordinates and transform data from Vue Flow';
COMMENT ON COLUMN workflow_node_contexts.match_confidence IS 'Confidence score (0-1) for node-sticky matching accuracy';
COMMENT ON COLUMN workflow_node_contexts.extraction_method IS 'Method used to match sticky to node: name_exact, proximity, fuzzy, etc.';

COMMENT ON COLUMN workflow_standalone_docs.doc_type IS 'Type of documentation: setup_instructions, section_header, workflow_note, etc.';
COMMENT ON COLUMN workflow_standalone_docs.doc_position IS 'JSONB containing position data for standalone elements';
COMMENT ON COLUMN workflow_standalone_docs.confidence_score IS 'Confidence score (0-1) for document classification accuracy';

