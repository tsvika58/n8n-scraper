-- Extraction Snapshots Schema
-- Stores raw JSON payloads per workflow and layer for auditing/replay

CREATE TABLE IF NOT EXISTS workflow_extraction_snapshots (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) REFERENCES workflows(workflow_id),
    layer VARCHAR(20) NOT NULL, -- e.g., L2V2, L3V3
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_workflow ON workflow_extraction_snapshots(workflow_id);
CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_layer ON workflow_extraction_snapshots(layer);
CREATE INDEX IF NOT EXISTS idx_extraction_snapshots_gin ON workflow_extraction_snapshots USING GIN (payload);

COMMENT ON TABLE workflow_extraction_snapshots IS 'Raw JSON snapshots per workflow/layer for auditing and deterministic reprocessing.';


