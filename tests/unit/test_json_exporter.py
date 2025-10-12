"""
Unit tests for JSON Exporter to maximize coverage.

Tests JSON export functionality, validation, error handling.
"""

import pytest
import json
from pathlib import Path
from src.exporters.json_exporter import JSONExporter


@pytest.mark.unit
class TestJSONExporter:
    """Comprehensive tests for JSONExporter."""
    
    @pytest.fixture
    def exporter(self, tmp_path):
        """Create exporter with temp directory."""
        return JSONExporter(output_dir=str(tmp_path))
    
    @pytest.fixture
    def sample_workflows(self):
        """Sample workflow data for testing."""
        return [
            {
                'workflow_id': '2462',
                'url': 'https://n8n.io/workflows/2462',
                'title': 'Test Workflow 1',
                'node_count': 5
            },
            {
                'workflow_id': '2134',
                'url': 'https://n8n.io/workflows/2134',
                'title': 'Test Workflow 2',
                'node_count': 10
            }
        ]
    
    # ========================================================================
    # BASIC FUNCTIONALITY (5 tests)
    # ========================================================================
    
    def test_initialization(self, tmp_path):
        """Test exporter initializes correctly."""
        exporter = JSONExporter(output_dir=str(tmp_path), indent=4)
        
        assert str(exporter.output_dir) == str(tmp_path)
        assert exporter.indent == 4
    
    def test_get_file_extension(self, exporter):
        """Test file extension is correct."""
        assert exporter.get_file_extension() == ".json"
    
    def test_export_basic_workflows(self, exporter, sample_workflows, tmp_path):
        """Test basic workflow export."""
        output_file = exporter.export(sample_workflows)
        
        assert Path(output_file).exists()
        
        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]['workflow_id'] == '2462'
    
    def test_export_with_custom_filename(self, exporter, sample_workflows):
        """Test export with custom filename."""
        output_file = exporter.export(sample_workflows, filename='custom.json')
        
        assert 'custom.json' in output_file
        assert Path(output_file).exists()
    
    def test_export_creates_output_dir(self, tmp_path, sample_workflows):
        """Test that export creates output directory if not exists."""
        nonexistent_dir = tmp_path / 'new_exports'
        exporter = JSONExporter(output_dir=str(nonexistent_dir))
        
        output_file = exporter.export(sample_workflows)
        
        assert Path(output_file).exists()
        assert nonexistent_dir.exists()
    
    # ========================================================================
    # EDGE CASES (5 tests)
    # ========================================================================
    
    def test_export_empty_list(self, exporter, tmp_path):
        """Test exporting empty workflow list."""
        output_file = exporter.export([])
        
        assert Path(output_file).exists()
        
        with open(output_file) as f:
            data = json.load(f)
            assert data == []
    
    def test_export_with_null_values(self, exporter, tmp_path):
        """Test exporting workflows with null values."""
        workflows = [
            {
                'workflow_id': '1',
                'url': 'https://n8n.io/workflows/1',
                'title': None,
                'author': None,
                'metadata': None
            }
        ]
        
        output_file = exporter.export(workflows)
        
        assert Path(output_file).exists()
        
        with open(output_file) as f:
            data = json.load(f)
            assert data[0]['title'] is None
    
    def test_export_with_special_characters(self, exporter, tmp_path):
        """Test exporting with special characters."""
        workflows = [
            {
                'workflow_id': '1',
                'url': 'https://n8n.io/workflows/1',
                'title': 'Test "quotes" and émojis 🚀',
                'description': 'Backslash \\ and newline \n test'
            }
        ]
        
        output_file = exporter.export(workflows)
        
        assert Path(output_file).exists()
        
        # Verify proper JSON encoding
        with open(output_file) as f:
            data = json.load(f)
            assert '🚀' in data[0]['title']
            assert '\\' in data[0]['description']
    
    def test_export_with_nested_data(self, exporter, tmp_path):
        """Test exporting with nested data structures."""
        workflows = [
            {
                'workflow_id': '1',
                'url': 'https://n8n.io/workflows/1',
                'metadata': {
                    'author': 'John Doe',
                    'tags': ['sales', 'automation']
                },
                'nodes': [
                    {'id': '1', 'type': 'webhook'},
                    {'id': '2', 'type': 'http'}
                ]
            }
        ]
        
        output_file = exporter.export(workflows)
        
        assert Path(output_file).exists()
        
        with open(output_file) as f:
            data = json.load(f)
            assert data[0]['metadata']['author'] == 'John Doe'
            assert len(data[0]['nodes']) == 2
    
    def test_export_large_dataset(self, exporter, tmp_path):
        """Test exporting large dataset."""
        workflows = [
            {
                'workflow_id': str(i),
                'url': f'https://n8n.io/workflows/{i}',
                'title': f'Workflow {i}',
                'node_count': i
            }
            for i in range(100)
        ]
        
        output_file = exporter.export(workflows)
        
        assert Path(output_file).exists()
        
        with open(output_file) as f:
            data = json.load(f)
            assert len(data) == 100
    
    # ========================================================================
    # VALIDATION (3 tests)
    # ========================================================================
    
    def test_validate_workflows_valid(self, exporter, sample_workflows):
        """Test validation with valid workflows."""
        result = exporter.validate_workflows(sample_workflows)
        
        assert result is True
    
    def test_validate_workflows_empty(self, exporter):
        """Test validation with empty list."""
        result = exporter.validate_workflows([])
        
        # Empty list is invalid (returns False)
        assert result is False
    
    def test_validate_workflows_invalid_type(self, exporter):
        """Test validation with invalid type."""
        result = exporter.validate_workflows("not a list")
        
        assert result is False

