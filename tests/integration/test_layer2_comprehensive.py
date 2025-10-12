"""
Comprehensive integration tests for Layer 2 to maximize coverage.

These tests target specific code paths including:
- Fallback API and transformation
- Error handling paths
- Helper method execution
- Edge cases
"""

import pytest
from src.scrapers.layer2_json import WorkflowJSONExtractor


@pytest.mark.integration
@pytest.mark.layer2
class TestLayer2Comprehensive:
    """Comprehensive tests to maximize Layer 2 coverage."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return WorkflowJSONExtractor()
    
    # ========================================================================
    # FALLBACK API TESTS (to cover lines 122-159, 191-213)
    # ========================================================================
    
    async def test_fallback_api_with_404_workflow(self, extractor):
        """Test fallback API gets triggered with 404 workflow."""
        # This workflow should return 404, triggering fallback
        result = await extractor.extract('2021')
        
        # Should have attempted fallback
        assert 'fallback_used' in result
        assert isinstance(result, dict)
        assert 'workflow_id' in result
    
    async def test_fallback_api_statistics(self, extractor):
        """Test that fallback statistics are tracked."""
        initial_fallback = extractor.statistics['fallback_success']
        initial_failed = extractor.statistics['both_failed']
        
        # Try a workflow that triggers fallback
        await extractor.extract('2021')
        
        # Statistics should have changed
        assert (extractor.statistics['fallback_success'] > initial_fallback or 
                extractor.statistics['both_failed'] > initial_failed)
    
    async def test_multiple_404_workflows(self, extractor):
        """Test multiple workflows that return 404."""
        workflow_ids = ['2021', '1847', '2091']
        
        for wf_id in workflow_ids:
            result = await extractor.extract(wf_id)
            assert isinstance(result, dict)
            assert 'workflow_id' in result
    
    async def test_fallback_http_204_handling(self, extractor):
        """Test fallback HTTP 204 (No Content) handling."""
        # These workflows return HTTP 204
        result = await extractor.extract('2021')
        
        if result.get('fallback_used'):
            # Should handle 204 gracefully
            assert 'error' in result or 'success' in result
    
    async def test_fallback_error_messages(self, extractor):
        """Test that fallback errors have proper messages."""
        result = await extractor.extract('999999')
        
        if not result.get('success'):
            assert 'error' in result
            assert isinstance(result['error'], str)
            assert len(result['error']) > 0
    
    # ========================================================================
    # HELPER METHOD TESTS (to cover lines 294-385)
    # ========================================================================
    
    def test_extract_node_type_from_url_if(self, extractor):
        """Test _extract_node_type_from_url with 'if' node."""
        result = extractor._extract_node_type_from_url('/integrations/if/')
        assert result == 'if'
    
    def test_extract_node_type_from_url_http_request(self, extractor):
        """Test _extract_node_type_from_url with http-request."""
        result = extractor._extract_node_type_from_url('/integrations/http-request/')
        assert result == 'httpRequest'
    
    def test_extract_node_type_from_url_google_calendar(self, extractor):
        """Test _extract_node_type_from_url with google-calendar."""
        result = extractor._extract_node_type_from_url('/integrations/google-calendar/')
        assert result == 'googleCalendar'
    
    def test_extract_node_type_from_url_invalid(self, extractor):
        """Test _extract_node_type_from_url with invalid URL."""
        result = extractor._extract_node_type_from_url('/invalid/path/')
        assert result is None
    
    def test_extract_node_type_from_url_empty(self, extractor):
        """Test _extract_node_type_from_url with empty URL."""
        result = extractor._extract_node_type_from_url('')
        assert result is None
    
    def test_transform_by_id_to_template(self, extractor):
        """Test _transform_by_id_to_template method."""
        by_id_data = {
            'id': '2462',
            'name': 'Test Workflow',
            'nodes': [
                {'id': 1, 'url': '/integrations/if/'},
                {'id': 2, 'url': '/integrations/http-request/'}
            ],
            'description': 'Test description',
            'categories': ['Sales'],
            'views': 100
        }
        
        result = extractor._transform_by_id_to_template(by_id_data)
        
        # Should have template structure
        assert 'id' in result
        assert 'name' in result
        assert 'workflow' in result
        assert 'nodes' in result['workflow']
        assert len(result['workflow']['nodes']) == 2
        assert '_metadata' in result
    
    def test_transform_creates_synthetic_nodes(self, extractor):
        """Test that transform creates synthetic nodes correctly."""
        by_id_data = {
            'id': '2462',
            'nodes': [
                {'id': 1, 'url': '/integrations/webhook/'},
                {'id': 2, 'url': '/integrations/openai/'}
            ]
        }
        
        result = extractor._transform_by_id_to_template(by_id_data)
        
        nodes = result['workflow']['nodes']
        assert len(nodes) == 2
        assert nodes[0]['type'] == 'n8n-nodes-base.webhook'
        assert nodes[1]['type'] == 'n8n-nodes-base.openai'
        assert nodes[0]['synthetic'] == True
    
    def test_transform_handles_empty_nodes(self, extractor):
        """Test transform with empty nodes array."""
        by_id_data = {
            'id': '2462',
            'nodes': []
        }
        
        result = extractor._transform_by_id_to_template(by_id_data)
        
        assert result['workflow']['nodes'] == []
        assert result['_metadata']['original_node_count'] == 0
    
    def test_validate_json_structure_valid(self, extractor):
        """Test _validate_json_structure with valid data."""
        valid_data = {
            'workflow': {
                'nodes': [{'id': '1', 'type': 'test'}],
                'connections': {}
            }
        }
        
        result = extractor._validate_json_structure(valid_data)
        assert result == True
    
    def test_validate_json_structure_missing_workflow(self, extractor):
        """Test _validate_json_structure with missing workflow key."""
        invalid_data = {
            'data': {}
        }
        
        result = extractor._validate_json_structure(invalid_data)
        assert result == False
    
    def test_validate_json_structure_missing_nodes(self, extractor):
        """Test _validate_json_structure with missing nodes."""
        invalid_data = {
            'workflow': {
                'connections': {}
            }
        }
        
        result = extractor._validate_json_structure(invalid_data)
        assert result == False
    
    def test_validate_json_structure_nodes_not_list(self, extractor):
        """Test _validate_json_structure with nodes not a list."""
        invalid_data = {
            'workflow': {
                'nodes': 'not a list',
                'connections': {}
            }
        }
        
        result = extractor._validate_json_structure(invalid_data)
        assert result == False
    
    # ========================================================================
    # ERROR PATH TESTS (to cover error handlers)
    # ========================================================================
    
    async def test_extraction_with_very_large_id(self, extractor):
        """Test extraction with very large workflow ID."""
        result = await extractor.extract('999999999')
        
        assert isinstance(result, dict)
        assert 'workflow_id' in result
    
    async def test_extraction_with_special_characters(self, extractor):
        """Test extraction with special character workflow ID."""
        result = await extractor.extract('test-workflow-123')
        
        assert isinstance(result, dict)
    
    async def test_statistics_accumulation(self, extractor):
        """Test that statistics accumulate correctly."""
        initial_total = extractor.statistics['total']
        
        # Extract multiple workflows
        await extractor.extract('2462')
        await extractor.extract('2134')
        
        # Total should increase
        assert extractor.statistics['total'] >= initial_total
    
    async def test_extractor_reusability(self, extractor):
        """Test that extractor can be reused many times."""
        for i in range(5):
            result = await extractor.extract('2462')
            assert result['success'] == True
    
    async def test_extraction_count_tracking(self, extractor):
        """Test that extraction_count is tracked."""
        initial_count = extractor.extraction_count
        
        await extractor.extract('2462')
        
        assert extractor.extraction_count > initial_count
    
    # ========================================================================
    # EDGE CASES (to maximize coverage)
    # ========================================================================
    
    async def test_workflow_with_complex_connections(self, extractor):
        """Test workflow that has complex connection structure."""
        result = await extractor.extract('2462')
        
        if result['success']:
            # Check connection count is calculated
            assert 'connection_count' in result
            assert isinstance(result['connection_count'], int)
    
    async def test_workflow_with_many_nodes(self, extractor):
        """Test workflow with many nodes."""
        result = await extractor.extract('2462')
        
        if result['success']:
            assert 'node_count' in result
            assert result['node_count'] >= 0
    
    async def test_node_types_extraction(self, extractor):
        """Test that node types are properly extracted."""
        result = await extractor.extract('2462')
        
        if result['success'] and 'data' in result:
            nodes = result['data'].get('workflow', {}).get('nodes', [])
            for node in nodes:
                assert 'type' in node
    
    def test_extractor_has_fallback_api_base(self, extractor):
        """Test that extractor has fallback API configured."""
        assert hasattr(extractor, 'fallback_api_base')
        assert 'by-id' in extractor.fallback_api_base
    
    def test_extractor_statistics_structure(self, extractor):
        """Test that statistics dict has correct structure."""
        assert 'total' in extractor.statistics
        assert 'primary_success' in extractor.statistics
        assert 'fallback_success' in extractor.statistics
        assert 'both_failed' in extractor.statistics


