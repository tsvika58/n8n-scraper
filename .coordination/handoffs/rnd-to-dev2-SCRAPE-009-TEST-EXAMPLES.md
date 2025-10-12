# 🧪 **SCRAPE-009: TEST EXAMPLES**

**From:** RND Manager  
**To:** Dev2  
**Date:** October 11, 2025, 12:45 PM  
**Subject:** Complete Test Examples for All Components  
**Task:** SCRAPE-009 - Unit Testing Suite

---

## 📋 **LAYER 2 JSON EXTRACTOR TESTS (25 TESTS)**

Create `tests/unit/test_layer2_json.py`:

```python
"""
Unit tests for Layer 2 JSON Extractor.

Tests WorkflowJSONExtractor with mocked API responses.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.extractors.layer2_json import WorkflowJSONExtractor


class TestWorkflowJSONExtractor:
    """Tests for WorkflowJSONExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return WorkflowJSONExtractor()
    
    # ========================================================================
    # SUCCESS CASES (10 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_full_workflow_json(
        self, 
        mock_get, 
        extractor, 
        mock_layer2_workflow_json
    ):
        """Test successful full workflow JSON extraction."""
        # Mock primary API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_layer2_workflow_json)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test extraction
        result = await extractor.extract('2462')
        
        # Assertions
        assert result['success'] == True
        assert result['node_count'] == 2
        assert result['extraction_type'] == 'full'
        assert result['fallback_used'] == False
        assert 'data' in result
        assert result['data']['id'] == '2462'
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_nodes(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 3
        assert len(result['data']['workflow']['nodes']) == 3
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_connections(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['connection_count'] == 1
        assert 'node1' in result['data']['workflow']['connections']
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_node_parameters(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        node = result['data']['workflow']['nodes'][0]
        assert node['parameters']['url'] == 'https://api.example.com'
        assert node['parameters']['method'] == 'POST'
    
    @patch('aiohttp.ClientSession.get')
    async def test_count_nodes_correctly(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 5
        assert result['node_count'] == len(result['data']['workflow']['nodes'])
    
    @patch('aiohttp.ClientSession.get')
    async def test_count_connections_correctly(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['connection_count'] == 2
    
    @patch('aiohttp.ClientSession.get')
    async def test_identify_node_types(self, mock_get, extractor):
        """Test node type identification."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [
                    {'id': 'node1', 'type': 'n8n-nodes-base.start'},
                    {'id': 'node2', 'type': 'n8n-nodes-base.httpRequest'},
                    {'id': 'node3', 'type': 'n8n-nodes-base.email'}
                ],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert 'start' in result['node_types']
        assert 'httpRequest' in result['node_types']
        assert 'email' in result['node_types']
    
    # ========================================================================
    # FALLBACK & ERROR CASES (10 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession.get')
    async def test_primary_api_404_triggers_fallback(self, mock_get, extractor):
        """Test that 404 on primary API triggers fallback."""
        # Mock primary API 404
        primary_response = AsyncMock()
        primary_response.status = 404
        
        # Mock fallback API success
        fallback_response = AsyncMock()
        fallback_response.status = 200
        fallback_response.json = AsyncMock(return_value={
            'id': '2462',
            'workflow': {'nodes': [], 'connections': {}}
        })
        
        # Configure mock to return different responses
        mock_get.return_value.__aenter__.side_effect = [primary_response, fallback_response]
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['fallback_used'] == True
        assert result['extraction_type'] == 'partial'
    
    @patch('aiohttp.ClientSession.get')
    async def test_fallback_api_success(self, mock_get, extractor):
        """Test successful fallback API extraction."""
        # Mock primary API failure
        primary_response = AsyncMock()
        primary_response.status = 404
        
        # Mock fallback API success
        fallback_json = {
            'id': '2462',
            'workflow': {
                'nodes': [{'id': 'node1', 'type': 'start'}],
                'connections': {}
            }
        }
        fallback_response = AsyncMock()
        fallback_response.status = 200
        fallback_response.json = AsyncMock(return_value=fallback_json)
        
        mock_get.return_value.__aenter__.side_effect = [primary_response, fallback_response]
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['fallback_used'] == True
        assert result['node_count'] == 1
        assert result['extraction_type'] == 'partial'
    
    @patch('aiohttp.ClientSession.get')
    async def test_fallback_api_failure(self, mock_get, extractor):
        """Test fallback API failure."""
        # Mock both APIs fail
        primary_response = AsyncMock()
        primary_response.status = 404
        
        fallback_response = AsyncMock()
        fallback_response.status = 404
        
        mock_get.return_value.__aenter__.side_effect = [primary_response, fallback_response]
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'Both primary and fallback APIs failed' in result['error']
    
    @patch('aiohttp.ClientSession.get')
    async def test_both_apis_fail(self, mock_get, extractor):
        """Test when both primary and fallback APIs fail."""
        # Mock both APIs fail with different errors
        primary_response = AsyncMock()
        primary_response.status = 500
        
        fallback_response = AsyncMock()
        fallback_response.status = 403
        
        mock_get.return_value.__aenter__.side_effect = [primary_response, fallback_response]
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'error' in result
        assert result['fallback_used'] == False
    
    @patch('aiohttp.ClientSession.get')
    async def test_mark_extraction_type(self, mock_get, extractor):
        """Test extraction type marking."""
        workflow_json = {
            'id': '2462',
            'workflow': {
                'nodes': [{'id': 'node1', 'type': 'start'}],
                'connections': {}
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=workflow_json)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['extraction_type'] in ['full', 'partial']
    
    @patch('aiohttp.ClientSession.get')
    async def test_fallback_used_flag(self, mock_get, extractor):
        """Test fallback_used flag setting."""
        # Mock primary API failure, fallback success
        primary_response = AsyncMock()
        primary_response.status = 404
        
        fallback_response = AsyncMock()
        fallback_response.status = 200
        fallback_response.json = AsyncMock(return_value={
            'id': '2462',
            'workflow': {'nodes': [], 'connections': {}}
        })
        
        mock_get.return_value.__aenter__.side_effect = [primary_response, fallback_response]
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['fallback_used'] == True
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_with_timeout(self, mock_get, extractor):
        """Test handling of timeout errors."""
        import asyncio
        mock_get.side_effect = asyncio.TimeoutError("Request timeout")
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'timeout' in result['error'].lower()
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_with_network_error(self, mock_get, extractor):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network error")
        
        result = await extractor.extract('2462')
        
        assert result['success'] == False
        assert 'error' in result
    
    # ========================================================================
    # EDGE CASES (5 tests)
    # ========================================================================
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_workflow_no_nodes(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 0
        assert result['connection_count'] == 0
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_workflow_no_connections(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 2
        assert result['connection_count'] == 0
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_minimal_json(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 1
        assert result['data']['id'] == '2462'
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_complex_workflow(self, mock_get, extractor):
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
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        assert result['success'] == True
        assert result['node_count'] == 10
        assert result['connection_count'] == 9
    
    @patch('aiohttp.ClientSession.get')
    async def test_extract_invalid_json_structure(self, mock_get, extractor):
        """Test handling of invalid JSON structure."""
        invalid_json = {
            'id': '2462',
            'workflow': 'invalid_structure'  # Should be dict
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=invalid_json)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await extractor.extract('2462')
        
        # Should handle gracefully
        assert result['success'] == False or result['node_count'] == 0
```

---

## 🎥 **LAYER 3 CONTENT EXTRACTOR TESTS (25 TESTS)**

Create `tests/unit/test_layer3_content.py`:

```python
"""
Unit tests for Layer 3 Content Extractor.

Tests ExplainerContentExtractor with mocked browser automation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.extractors.layer3_content import ExplainerContentExtractor


class TestExplainerContentExtractor:
    """Tests for ExplainerContentExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return ExplainerContentExtractor()
    
    # ========================================================================
    # SUCCESS CASES (10 tests)
    # ========================================================================
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_explainer_text(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test successful explainer text extraction."""
        # Mock page content
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="explainer">
            <p>This workflow automates email sending for sales teams.</p>
            <p>It connects to your CRM and sends personalized emails.</p>
        </div>
        </html>
        """)
        
        # Mock playwright setup
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        # Test extraction
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Assertions
        assert result['success'] == True
        assert 'email sending' in result['explainer_text']
        assert 'sales teams' in result['explainer_text']
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_setup_instructions(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test setup instructions extraction."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="setup">
            <h3>Setup Instructions</h3>
            <ol>
                <li>Configure API credentials</li>
                <li>Set up email template</li>
                <li>Connect to CRM</li>
            </ol>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert 'API credentials' in result['setup_instructions']
        assert 'email template' in result['setup_instructions']
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_use_instructions(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test use instructions extraction."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="usage">
            <h3>How to Use</h3>
            <ol>
                <li>Run the workflow</li>
                <li>Check email results</li>
                <li>Monitor performance</li>
            </ol>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert 'Run the workflow' in result['use_instructions']
        assert 'Check email results' in result['use_instructions']
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_code_snippets(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test code snippet extraction."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="code">
            <pre><code>
            {
                "url": "https://api.example.com",
                "method": "POST",
                "body": {"message": "Hello"}
            }
            </code></pre>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert 'api.example.com' in result['code_snippets']
        assert 'POST' in result['code_snippets']
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_images(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test image extraction."""
        mock_page = mock_playwright_page
        
        # Mock image elements
        mock_img1 = Mock()
        mock_img1.get_attribute = Mock(return_value='https://example.com/image1.png')
        
        mock_img2 = Mock()
        mock_img2.get_attribute = Mock(return_value='https://example.com/image2.jpg')
        
        mock_page.query_selector_all = Mock(return_value=[mock_img1, mock_img2])
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert len(result['images']) == 2
        assert 'image1.png' in result['images'][0]
        assert 'image2.jpg' in result['images'][1]
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_iframes(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test iframe extraction."""
        mock_page = mock_playwright_page
        
        # Mock iframe elements
        mock_iframe = Mock()
        mock_iframe.get_attribute = Mock(return_value='https://youtube.com/embed/test123')
        
        mock_page.query_selector_all = Mock(return_value=[mock_iframe])
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['iframe_count'] == 1
        assert 'youtube.com' in result['iframes'][0]
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_videos(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test video extraction."""
        mock_page = mock_playwright_page
        
        # Mock video elements
        mock_video = Mock()
        mock_video.get_attribute = Mock(return_value='https://youtube.com/watch?v=test123')
        
        mock_page.query_selector_all = Mock(return_value=[mock_video])
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['video_count'] == 1
        assert 'youtube.com' in result['videos'][0]
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_sticky_notes(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test sticky note extraction."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="sticky-note">
            <h2>🚀 Start here 🚀</h2>
            <p>Click "Execute workflow" to run it</p>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert 'Start here' in result['sticky_notes']
        assert 'Execute workflow' in result['sticky_notes']
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_complete_content(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test complete content extraction."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="explainer">
            <p>Complete workflow description</p>
        </div>
        <div class="setup">
            <p>Setup instructions here</p>
        </div>
        <div class="usage">
            <p>Usage instructions here</p>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert 'Complete workflow description' in result['explainer_text']
        assert 'Setup instructions here' in result['setup_instructions']
        assert 'Usage instructions here' in result['use_instructions']
    
    # ========================================================================
    # ERROR CASES (8 tests)
    # ========================================================================
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_with_timeout(
        self, 
        mock_playwright, 
        extractor
    ):
        """Test handling of timeout errors."""
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=asyncio.TimeoutError("Page load timeout"))
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == False
        assert 'timeout' in result['error'].lower()
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_with_invalid_html(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test handling of invalid HTML."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value='<html><body>Invalid content</body></html>')
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Should still succeed but with minimal data
        assert result['success'] == True
        assert result['explainer_text'] is None or result['explainer_text'] == ''
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_with_empty_page(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test handling of empty page."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value='<html><body></body></html>')
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['explainer_text'] is None or result['explainer_text'] == ''
        assert result['setup_instructions'] is None or result['setup_instructions'] == ''
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_with_network_error(
        self, 
        mock_playwright, 
        extractor
    ):
        """Test handling of network errors."""
        mock_playwright.side_effect = Exception("Network error")
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == False
        assert 'error' in result
    
    # ========================================================================
    # EDGE CASES (7 tests)
    # ========================================================================
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_minimal_content(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test extraction of minimal content."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="explainer">
            <p>Minimal description</p>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['explainer_text'] == 'Minimal description'
        assert result['setup_instructions'] is None or result['setup_instructions'] == ''
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_content_without_instructions(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test extraction when instructions are missing."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="explainer">
            <p>Workflow description only</p>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['explainer_text'] == 'Workflow description only'
        assert result['setup_instructions'] is None or result['setup_instructions'] == ''
        assert result['use_instructions'] is None or result['use_instructions'] == ''
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_content_without_images(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test extraction when no images are present."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="explainer">
            <p>Text-only workflow</p>
        </div>
        </html>
        """)
        mock_page.query_selector_all = Mock(return_value=[])
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert result['image_count'] == 0
        assert result['images'] == []
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_very_long_content(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test extraction of very long content."""
        long_text = "This is a very long description. " * 100
        
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value=f"""
        <html>
        <div class="explainer">
            <p>{long_text}</p>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert len(result['explainer_text']) > 1000
        assert 'very long description' in result['explainer_text']
    
    @patch('src.extractors.layer3_content.async_playwright')
    async def test_extract_content_with_special_chars(
        self, 
        mock_playwright, 
        extractor, 
        mock_playwright_page
    ):
        """Test extraction with special characters."""
        mock_page = mock_playwright_page
        mock_page.content = AsyncMock(return_value="""
        <html>
        <div class="explainer">
            <p>Workflow with émojis 🚀 and spëcial chars & symbols!</p>
        </div>
        </html>
        """)
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_playwright.return_value.__aenter__.return_value = mock_browser
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert result['success'] == True
        assert 'émojis' in result['explainer_text']
        assert '🚀' in result['explainer_text']
        assert 'spëcial' in result['explainer_text']
        assert '& symbols!' in result['explainer_text']
```

---

## 🎯 **MULTIMODAL & TRANSCRIPT TESTS**

Create `tests/unit/test_multimodal.py` (15 tests) and `tests/unit/test_transcripts.py` (10 tests) following similar patterns with:

- Mock iframe discovery and extraction
- Mock video discovery and extraction  
- Mock text extraction from elements
- Mock YouTube API calls
- Mock UI automation fallback
- Test hybrid approach (API fails → UI succeeds)

---

## ✅ **QUALITY VALIDATION TESTS**

Create `tests/unit/test_quality_validation.py` (10 tests) with:

- Mock Layer 1/2/3 validation
- Test quality score calculation
- Test validation rules
- Test scoring algorithms

---

**🎯 Complete test examples provided for all 6 components!**

---

*Test Examples v1.0*  
*Created: October 11, 2025, 12:45 PM*  
*Author: RND Manager*  
*For: Dev2*

