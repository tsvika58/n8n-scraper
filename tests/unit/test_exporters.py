"""
Unit Tests for Export Pipeline.

Tests all export formats (JSON, JSONL, CSV, Parquet).

Author: RND Manager
Task: SCRAPE-012
"""

import pytest
import json
import csv
from pathlib import Path
from datetime import datetime

from src.exporters.json_exporter import JSONExporter
from src.exporters.jsonl_exporter import JSONLExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.export_manager import ExportManager

# Try importing Parquet exporter
try:
    from src.exporters.parquet_exporter import ParquetExporter
    import pandas as pd
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False


@pytest.fixture
def sample_workflows():
    """Sample workflow data for testing."""
    return [
        {
            'workflow_id': 'TEST-001',
            'url': 'https://n8n.io/workflows/TEST-001',
            'processing_status': 'complete',
            'quality_score': 85.5,
            'processing_time': 12.3,
            'metadata': {
                'title': 'Test Workflow 1',
                'description': 'This is a test workflow',
                'author': 'Test Author',
                'categories': ['Sales', 'Marketing'],
                'tags': ['email', 'automation'],
                'views': 1000,
                'shares': 50,
            },
            'structure': {
                'node_count': 5,
                'connection_count': 4,
                'node_types': ['start', 'httpRequest', 'email'],
                'extraction_type': 'full',
                'fallback_used': False,
            },
            'content': {
                'explainer_text': 'This workflow automates email sending',
                'has_videos': False,
                'video_count': 0,
                'has_iframes': True,
                'iframe_count': 1,
            },
            'video_transcripts': [],
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-15T12:00:00',
        },
        {
            'workflow_id': 'TEST-002',
            'url': 'https://n8n.io/workflows/TEST-002',
            'processing_status': 'partial',
            'quality_score': 65.0,
            'processing_time': 15.7,
            'metadata': {
                'title': 'Test Workflow 2',
                'description': 'Another test workflow',
                'author': 'Test Author 2',
                'categories': ['Technical'],
                'tags': ['api', 'webhook'],
                'views': 500,
                'shares': 25,
            },
            'structure': {
                'node_count': 3,
                'connection_count': 2,
                'node_types': ['webhook', 'code'],
                'extraction_type': 'partial',
                'fallback_used': True,
            },
            'content': {
                'explainer_text': 'Webhook integration workflow',
                'has_videos': True,
                'video_count': 1,
                'has_iframes': False,
                'iframe_count': 0,
            },
            'video_transcripts': [
                {
                    'video_url': 'https://youtube.com/watch?v=test',
                    'video_id': 'test',
                    'platform': 'youtube',
                    'transcript_text': 'This is a test transcript',
                    'transcript_language': 'en',
                    'extraction_method': 'api',
                }
            ],
            'created_at': '2024-02-01T00:00:00',
            'updated_at': '2024-02-15T12:00:00',
        }
    ]


@pytest.fixture
def temp_export_dir(tmp_path):
    """Temporary export directory."""
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    return str(export_dir)


# ============================================================================
# JSON EXPORTER TESTS
# ============================================================================

def test_json_exporter_creates_file(sample_workflows, temp_export_dir):
    """Test JSON exporter creates file successfully."""
    exporter = JSONExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.json")
    
    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".json"


def test_json_exporter_valid_json(sample_workflows, temp_export_dir):
    """Test JSON exporter produces valid JSON."""
    exporter = JSONExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.json")
    
    with open(output_path) as f:
        data = json.load(f)
    
    assert 'export_metadata' in data
    assert 'workflows' in data
    assert data['export_metadata']['workflow_count'] == 2
    assert len(data['workflows']) == 2


def test_json_exporter_complete_data(sample_workflows, temp_export_dir):
    """Test JSON exporter includes all workflow data."""
    exporter = JSONExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.json")
    
    with open(output_path) as f:
        data = json.load(f)
    
    workflow = data['workflows'][0]
    assert workflow['workflow_id'] == 'TEST-001'
    assert workflow['metadata']['title'] == 'Test Workflow 1'
    assert workflow['structure']['node_count'] == 5
    assert workflow['content']['explainer_text'] is not None


def test_json_exporter_compact_format(sample_workflows, temp_export_dir):
    """Test JSON exporter compact format."""
    exporter = JSONExporter(temp_export_dir, indent=None)
    output_path = exporter.export(sample_workflows, "test_compact.json")
    
    # Compact should be smaller
    compact_size = Path(output_path).stat().st_size
    
    exporter_indented = JSONExporter(temp_export_dir, indent=2)
    output_path_indented = exporter_indented.export(sample_workflows, "test_indented.json")
    indented_size = Path(output_path_indented).stat().st_size
    
    assert compact_size < indented_size


# ============================================================================
# JSONL EXPORTER TESTS
# ============================================================================

def test_jsonl_exporter_creates_file(sample_workflows, temp_export_dir):
    """Test JSONL exporter creates file successfully."""
    exporter = JSONLExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.jsonl")
    
    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".jsonl"


def test_jsonl_exporter_one_per_line(sample_workflows, temp_export_dir):
    """Test JSONL exporter writes one JSON object per line."""
    exporter = JSONLExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.jsonl")
    
    with open(output_path) as f:
        lines = f.readlines()
    
    # Should have metadata line + 2 workflow lines
    assert len(lines) == 3
    
    # Each line should be valid JSON
    for line in lines:
        data = json.loads(line)
        assert isinstance(data, dict)


def test_jsonl_exporter_training_format(sample_workflows, temp_export_dir):
    """Test JSONL training format."""
    exporter = JSONLExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_training.jsonl")
    
    with open(output_path) as f:
        lines = f.readlines()
    
    # Skip metadata line, check workflow lines
    workflow_line = json.loads(lines[1])
    
    # Should have flattened structure
    assert 'id' in workflow_line
    assert 'title' in workflow_line
    assert 'node_count' in workflow_line
    assert 'categories' in workflow_line


def test_jsonl_exporter_finetuning_format(sample_workflows, temp_export_dir):
    """Test JSONL fine-tuning format."""
    exporter = JSONLExporter(temp_export_dir)
    output_path = exporter.export_for_finetuning(
        sample_workflows, 
        "test_finetuning.jsonl",
        instruction_template="Explain this workflow:"
    )
    
    with open(output_path) as f:
        lines = f.readlines()
    
    # Should have 2 instruction-response pairs
    assert len(lines) == 2
    
    pair = json.loads(lines[0])
    assert 'instruction' in pair
    assert 'response' in pair
    assert 'metadata' in pair
    assert 'Explain this workflow:' in pair['instruction']


# ============================================================================
# CSV EXPORTER TESTS
# ============================================================================

def test_csv_exporter_creates_file(sample_workflows, temp_export_dir):
    """Test CSV exporter creates file successfully."""
    exporter = CSVExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.csv")
    
    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".csv"


def test_csv_exporter_valid_csv(sample_workflows, temp_export_dir):
    """Test CSV exporter produces valid CSV."""
    exporter = CSVExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.csv")
    
    with open(output_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 2
    assert 'workflow_id' in rows[0]
    assert 'title' in rows[0]


def test_csv_exporter_data_integrity(sample_workflows, temp_export_dir):
    """Test CSV exporter preserves data."""
    exporter = CSVExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.csv")
    
    with open(output_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    row = rows[0]
    assert row['workflow_id'] == 'TEST-001'
    assert row['title'] == 'Test Workflow 1'
    assert row['node_count'] == '5'
    assert 'Sales' in row['categories']


def test_csv_exporter_detailed_format(sample_workflows, temp_export_dir):
    """Test CSV detailed format."""
    exporter = CSVExporter(temp_export_dir)
    output_path = exporter.export_detailed(sample_workflows, "test_detailed.csv")
    
    with open(output_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Detailed format has more columns
    assert 'explainer_text' in rows[0]
    assert 'setup_instructions' in rows[0]
    assert 'fallback_used' in rows[0]


# ============================================================================
# PARQUET EXPORTER TESTS (if available)
# ============================================================================

@pytest.mark.skipif(not PARQUET_AVAILABLE, reason="Parquet dependencies not installed")
def test_parquet_exporter_creates_file(sample_workflows, temp_export_dir):
    """Test Parquet exporter creates file successfully."""
    exporter = ParquetExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.parquet")
    
    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".parquet"


@pytest.mark.skipif(not PARQUET_AVAILABLE, reason="Parquet dependencies not installed")
def test_parquet_exporter_valid_data(sample_workflows, temp_export_dir):
    """Test Parquet exporter produces valid data."""
    exporter = ParquetExporter(temp_export_dir)
    output_path = exporter.export(sample_workflows, "test_export.parquet")
    
    # Read back the data
    df = pd.read_parquet(output_path)
    
    assert len(df) == 2
    assert 'workflow_id' in df.columns
    assert 'title' in df.columns
    assert df.iloc[0]['workflow_id'] == 'TEST-001'


# ============================================================================
# EXPORT MANAGER TESTS
# ============================================================================

def test_export_manager_all_formats(sample_workflows, temp_export_dir):
    """Test export manager exports all formats."""
    manager = ExportManager(temp_export_dir)
    results = manager.export_all_formats(sample_workflows, "test_all")
    
    assert 'json' in results
    assert 'jsonl' in results
    assert 'csv' in results
    
    # Check all files exist
    for path in results.values():
        assert Path(path).exists()


def test_export_manager_export_stats(sample_workflows, temp_export_dir):
    """Test export manager tracks statistics."""
    manager = ExportManager(temp_export_dir)
    manager.export_all_formats(sample_workflows, "test_stats")
    
    stats = manager.get_export_stats()
    
    assert stats['total_exports'] == 1
    assert stats['total_workflows_exported'] == 2
    assert 'latest_export' in stats


def test_export_manager_validates_data(temp_export_dir):
    """Test export manager validates workflow data."""
    manager = ExportManager(temp_export_dir)
    
    # Invalid data (empty list)
    results = manager.export_all_formats([], "test_empty")
    assert len(results) == 0
    
    # Invalid data (not a list) - should fail gracefully
    results = manager.export_all_formats("not a list", "test_invalid")
    assert len(results) == 0  # All exports should fail gracefully


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_export_performance_large_dataset(temp_export_dir):
    """Test export performance with larger dataset."""
    # Generate 100 workflows
    workflows = []
    for i in range(100):
        workflows.append({
            'workflow_id': f'TEST-{i:03d}',
            'url': f'https://n8n.io/workflows/TEST-{i:03d}',
            'processing_status': 'complete',
            'quality_score': 75.0,
            'processing_time': 10.0,
            'metadata': {
                'title': f'Test Workflow {i}',
                'description': f'Description {i}',
                'author': 'Test Author',
                'categories': ['Test'],
                'tags': ['test'],
                'views': 100,
                'shares': 10,
            },
            'structure': {
                'node_count': 3,
                'connection_count': 2,
                'node_types': ['start', 'code'],
                'extraction_type': 'full',
                'fallback_used': False,
            },
            'content': {
                'explainer_text': 'Test content',
                'has_videos': False,
                'video_count': 0,
            },
            'video_transcripts': [],
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00',
        })
    
    # Test JSON export
    exporter = JSONExporter(temp_export_dir)
    output_path = exporter.export(workflows, "test_large.json")
    
    # Should complete in reasonable time and create valid file
    assert Path(output_path).exists()
    
    with open(output_path) as f:
        data = json.load(f)
    
    assert data['export_metadata']['workflow_count'] == 100
    assert len(data['workflows']) == 100

