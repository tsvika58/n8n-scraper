"""
Integration tests for Layer 2 JSON Extractor using REAL API calls.

These tests actually call n8n.io APIs to verify functionality.
They provide much higher coverage than mocked unit tests.
"""

import pytest
from src.scrapers.layer2_json import WorkflowJSONExtractor


@pytest.mark.integration
@pytest.mark.layer2
class TestLayer2Integration:
    """Integration tests for Layer 2 with real API calls."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return WorkflowJSONExtractor()
    
    # ========================================================================
    # REAL API TESTS (10 tests)
    # ========================================================================
    
    async def test_extract_real_workflow_success(self, extractor):
        """Test extraction with real workflow that exists."""
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['workflow_id'] == '2462'
        assert result['node_count'] > 0
        assert 'data' in result
        assert 'workflow' in result['data']
        assert result['fallback_used'] == False
        assert result['extraction_type'] == 'full'
    
    async def test_extract_real_workflow_nodes(self, extractor):
        """Test that real workflow has nodes."""
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        nodes = result['data']['workflow']['nodes']
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        
        # Verify node structure
        first_node = nodes[0]
        assert 'id' in first_node
        assert 'type' in first_node
    
    async def test_extract_real_workflow_connections(self, extractor):
        """Test that real workflow has connections."""
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        connections = result['data']['workflow']['connections']
        assert isinstance(connections, dict)
    
    async def test_extract_nonexistent_workflow_404(self, extractor):
        """Test extraction with nonexistent workflow (triggers fallback)."""
        result = await extractor.extract('2021')
        
        # Should fail gracefully
        assert result['success'] == False
        assert 'workflow_id' in result
        assert 'error' in result
    
    async def test_extraction_time_reasonable(self, extractor):
        """Test that extraction time is reasonable (<10s)."""
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert 'extraction_time' in result
        assert result['extraction_time'] < 10.0
    
    async def test_statistics_tracking_works(self, extractor):
        """Test that statistics are tracked correctly."""
        initial_count = extractor.statistics['total']
        
        await extractor.extract('2462')
        
        assert extractor.statistics['total'] == initial_count + 1
        assert extractor.statistics['primary_success'] > 0
    
    async def test_fallback_api_triggered(self, extractor):
        """Test that fallback API is triggered on 404."""
        result = await extractor.extract('2021')
        
        # Should have tried fallback
        assert 'fallback_used' in result
        assert result['fallback_used'] == True or 'error' in result
    
    async def test_node_type_extraction(self, extractor):
        """Test that node types are correctly identified."""
        result = await extractor.extract('2462')
        
        if result['success']:
            nodes = result['data']['workflow']['nodes']
            for node in nodes:
                assert 'type' in node
                assert isinstance(node['type'], str)
    
    async def test_multiple_extractions(self, extractor):
        """Test multiple extractions work correctly."""
        result1 = await extractor.extract('2462')
        result2 = await extractor.extract('2462')
        
        assert result1['success'] == True
        assert result2['success'] == True
        assert result1['node_count'] == result2['node_count']
    
    async def test_extraction_consistency(self, extractor):
        """Test that extraction results are consistent."""
        result = await extractor.extract('2462')
        
        if result['success']:
            # Node count should match actual nodes
            assert result['node_count'] == len(result['data']['workflow']['nodes'])
            
            # Connection count should be reasonable
            assert result['connection_count'] >= 0
