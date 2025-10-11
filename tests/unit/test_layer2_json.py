"""
Unit tests for Layer 2 JSON Extractor (SCRAPE-009).

Tests WorkflowJSONExtractor with mocked API responses.
Covers: success cases, fallback API, error handling, edge cases.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.scrapers.layer2_json import WorkflowJSONExtractor


@pytest.mark.unit
@pytest.mark.layer2
class TestWorkflowJSONExtractor:
    """Tests for WorkflowJSONExtractor with 25 comprehensive tests."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return WorkflowJSONExtractor()
    
    # ========================================================================
    # SUCCESS CASES (10 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession')
    async def test_extract_full_workflow_json(
        self, 
        mock_session_class, 
        extractor, 
        mock_layer2_workflow_json
    ):
        """Test successful full workflow JSON extraction."""
        # Mock primary API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        # Test extraction
        result = await extractor.extract('2462')
        
        # Assertions
        assert result['success'] == True
        assert result['node_count'] == 2
        assert result['extraction_type'] == 'full'
        assert result['fallback_used'] == False
        assert 'data' in result
        assert result['data']['id'] == '2462'
    
    @patch('aiohttp.ClientSession')
    async def test_extract_nodes(self, mock_session_class, extractor):
        """Test node extraction and counting."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [
                    {'id': 'node1', 'type': 'start'},
                    {'id': 'node2', 'type': 'httpRequest'},
                    {'id': 'node3', 'type': 'email'}
                ],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 3
        assert len(result['data']['workflow']['nodes']) == 3
    
    @patch('aiohttp.ClientSession')
    async def test_extract_connections(self, mock_session_class, extractor):
        """Test connection extraction and counting."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [
                    {'id': 'node1', 'type': 'start'},
                    {'id': 'node2', 'type': 'httpRequest'}
                ],
                'connections': {
                    'node1': {
                        'main': [[{'node': 'node2', 'type': 'main', 'index': 0}]]
                    }
                }
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['connection_count'] == 1
        assert 'node1' in result['data']['workflow']['connections']
    
    @patch('aiohttp.ClientSession')
    async def test_extract_node_parameters(self, mock_session_class, extractor):
        """Test node parameter extraction."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [
                    {
                        'id': 'node1',
                        'type': 'httpRequest',
                        'parameters': {
                            'url': 'https://api.example.com',
                            'method': 'POST',
                            'headers': {'Content-Type': 'application/json'}
                        }
                    }
                ],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        node = result['data']['workflow']['nodes'][0]
        assert node['parameters']['url'] == 'https://api.example.com'
        assert node['parameters']['method'] == 'POST'
    
    @patch('aiohttp.ClientSession')
    async def test_count_nodes_correctly(self, mock_session_class, extractor):
        """Test accurate node counting."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [{'id': f'node{i}', 'type': 'test'} for i in range(5)],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 5
        assert result['node_count'] == len(result['data']['workflow']['nodes'])
    
    @patch('aiohttp.ClientSession')
    async def test_count_connections_correctly(self, mock_session_class, extractor):
        """Test accurate connection counting."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [{'id': f'node{i}', 'type': 'test'} for i in range(3)],
                'connections': {
                    'node0': {'main': [[{'node': 'node1', 'type': 'main', 'index': 0}]]},
                    'node1': {'main': [[{'node': 'node2', 'type': 'main', 'index': 0}]]}
                }
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['connection_count'] == 2
    
    @patch('aiohttp.ClientSession')
    async def test_extraction_time_recorded(self, mock_session_class, extractor, mock_layer2_workflow_json):
        """Test that extraction time is recorded."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert 'extraction_time' in result
        assert isinstance(result['extraction_time'], (int, float))
        assert result['extraction_time'] >= 0
    
    @patch('aiohttp.ClientSession')
    async def test_workflow_id_preserved(self, mock_session_class, extractor, mock_layer2_workflow_json):
        """Test that workflow ID is preserved in result."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['workflow_id'] == '2462'
    
    @patch('aiohttp.ClientSession')
    async def test_data_structure_valid(self, mock_session_class, extractor, mock_layer2_workflow_json):
        """Test that returned data structure is valid."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert 'data' in result
        assert 'workflow' in result['data']
        assert 'nodes' in result['data']['workflow']
        assert 'connections' in result['data']['workflow']
    
    @patch('aiohttp.ClientSession')
    async def test_statistics_tracking(self, mock_session_class, extractor, mock_layer2_workflow_json):
        """Test that statistics are tracked correctly."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        # Check initial state
        assert extractor.statistics['total'] == 0
        assert extractor.statistics['primary_success'] == 0
        
        # Extract
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert extractor.statistics['primary_success'] == 1
    
    # ========================================================================
    # FALLBACK & ERROR CASES (10 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession')
    async def test_primary_api_404_triggers_fallback(self, mock_session_class, extractor):
        """Test that 404 on primary API triggers fallback."""
        # Mock primary API 404
        primary_response = AsyncMock()
        primary_response.status = 404
        
        # Mock fallback API success (HTTP 204 in reality)
        fallback_response = AsyncMock()
        fallback_response.status = 204
        
        mock_session = AsyncMock()
        
        # Configure mock to return different responses for each call
        call_count = [0]
        
        async def get_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return primary_response
            else:
                return fallback_response
        
        mock_session.get = AsyncMock(side_effect=get_side_effect)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        primary_response.__aenter__ = AsyncMock(return_value=primary_response)
        primary_response.__aexit__ = AsyncMock(return_value=None)
        fallback_response.__aenter__ = AsyncMock(return_value=fallback_response)
        fallback_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2021')
        
        assert result['success'] == False
        assert result['fallback_used'] == True
        assert 'both APIs failed' in result['error'].lower() or '204' in result['error']
    
    @patch('aiohttp.ClientSession')
    async def test_fallback_api_204_handling(self, mock_session_class, extractor):
        """Test fallback API HTTP 204 handling."""
        # Mock primary API failure
        primary_response = AsyncMock()
        primary_response.status = 404
        
        # Mock fallback API 204
        fallback_response = AsyncMock()
        fallback_response.status = 204
        
        mock_session = AsyncMock()
        call_count = [0]
        
        async def get_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return primary_response
            else:
                return fallback_response
        
        mock_session.get = AsyncMock(side_effect=get_side_effect)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        primary_response.__aenter__ = AsyncMock(return_value=primary_response)
        primary_response.__aexit__ = AsyncMock(return_value=None)
        fallback_response.__aenter__ = AsyncMock(return_value=fallback_response)
        fallback_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2021')
        
        assert result['success'] == False
        assert 'error' in result
        assert result['fallback_used'] == True
    
    @patch('aiohttp.ClientSession')
    async def test_extract_with_timeout(self, mock_session_class, extractor):
        """Test handling of timeout errors."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(side_effect=asyncio.TimeoutError("Request timeout"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'timeout' in result['error'].lower()
    
    @patch('aiohttp.ClientSession')
    async def test_extract_with_network_error(self, mock_session_class, extractor):
        """Test handling of network errors."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(side_effect=Exception("Network error"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'error' in result
    
    @patch('aiohttp.ClientSession')
    async def test_extract_with_500_error(self, mock_session_class, extractor):
        """Test handling of HTTP 500 errors."""
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert '500' in result['error']
    
    @patch('aiohttp.ClientSession')
    async def test_extract_with_invalid_json(self, mock_session_class, extractor):
        """Test handling of invalid JSON responses."""
        import json
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'json' in result['error'].lower() or 'error' in result['error'].lower()
    
    @patch('aiohttp.ClientSession')
    async def test_fallback_used_flag_false_on_primary_success(self, mock_session_class, extractor, mock_layer2_workflow_json):
        """Test fallback_used flag is False when primary succeeds."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['fallback_used'] == False
    
    @patch('aiohttp.ClientSession')
    async def test_extraction_type_full_on_primary(self, mock_session_class, extractor, mock_layer2_workflow_json):
        """Test extraction_type is 'full' on primary API success."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['extraction_type'] == 'full'
    
    @patch('aiohttp.ClientSession')
    async def test_error_on_connection_error(self, mock_session_class, extractor):
        """Test handling of connection errors."""
        import aiohttp
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(side_effect=aiohttp.ClientConnectionError("Connection failed"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'error' in result
    
    @patch('aiohttp.ClientSession')
    async def test_error_details_included(self, mock_session_class, extractor):
        """Test that error details are included in result."""
        mock_response = AsyncMock()
        mock_response.status = 403
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'error' in result
        assert '403' in result['error']
    
    # ========================================================================
    # EDGE CASES (5 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession')
    async def test_extract_workflow_no_nodes(self, mock_session_class, extractor):
        """Test extraction of workflow with no nodes."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 0
        assert result['connection_count'] == 0
    
    @patch('aiohttp.ClientSession')
    async def test_extract_workflow_no_connections(self, mock_session_class, extractor):
        """Test extraction of workflow with no connections."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [
                    {'id': 'node1', 'type': 'start'},
                    {'id': 'node2', 'type': 'httpRequest'}
                ],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 2
        assert result['connection_count'] == 0
    
    @patch('aiohttp.ClientSession')
    async def test_extract_minimal_json(self, mock_session_class, extractor):
        """Test extraction of minimal valid JSON."""
        minimal_json = {
            'id': '2462',
            'workflow': {
                'nodes': [{'id': 'node1', 'type': 'start'}],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=minimal_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 1
        assert result['data']['id'] == '2462'
    
    @patch('aiohttp.ClientSession')
    async def test_extract_complex_workflow(self, mock_session_class, extractor):
        """Test extraction of complex workflow with many nodes."""
        # Create complex workflow with 10 nodes and multiple connections
        nodes = [{'id': f'node{i}', 'type': f'type{i}'} for i in range(10)]
        connections = {
            f'node{i}': {
                'main': [[{'node': f'node{i+1}', 'type': 'main', 'index': 0}]]
            } for i in range(9)
        }
        
        complex_json = {
            'id': '2462',
            'workflow': {'nodes': nodes, 'connections': connections}
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=complex_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 10
        assert result['connection_count'] == 9
    
    @patch('aiohttp.ClientSession')
    async def test_extract_invalid_json_structure(self, mock_session_class, extractor):
        """Test handling of invalid JSON structure."""
        invalid_json = {
            'id': '2462',
            'workflow': 'invalid_structure'  # Should be dict
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=invalid_json)
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await extractor.extract('2462')
        
        # Should handle gracefully
        assert result['success'] == False or result['node_count'] == 0
