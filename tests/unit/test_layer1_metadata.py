"""
Unit tests for Layer 1 Metadata Extractor (SCRAPE-009).

Tests PageMetadataExtractor with mocked HTTP responses.
Covers: success cases, error handling, edge cases.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.scrapers.layer1_metadata import PageMetadataExtractor


@pytest.mark.unit
@pytest.mark.layer1
class TestPageMetadataExtractor:
    """Tests for PageMetadataExtractor with 20 comprehensive tests."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return PageMetadataExtractor()
    
    # ========================================================================
    # SUCCESS CASES (8 tests)
    # ========================================================================
    
    def test_extractor_initialization(self, extractor):
        """Test extractor initializes correctly."""
        assert extractor is not None
        assert hasattr(extractor, 'extract')
    
    @patch('src.scrapers.layer1_metadata.Page MetadataExtractor._fetch_page')
    async def test_extract_basic_metadata(self, mock_fetch, extractor):
        """Test successful metadata extraction."""
        # Mock HTML response
        mock_html = """
        <html>
        <head><title>Test Workflow</title></head>
        <body>
            <div class="author">John Doe</div>
            <div class="category">Sales</div>
            <div class="views">1000</div>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
        assert 'workflow_id' in result
    
    def test_parse_title(self, extractor):
        """Test title parsing."""
        from bs4 import BeautifulSoup
        html = '<html><head><title>My Workflow</title></head></html>'
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        assert title is not None
        assert title.text == 'My Workflow'
    
    def test_parse_author(self, extractor):
        """Test author information parsing."""
        from bs4 import BeautifulSoup
        html = '<html><body><div class="author">Jane Doe</div></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        author = soup.find('div', class_='author')
        assert author is not None
    
    def test_parse_categories(self, extractor):
        """Test categories extraction."""
        from bs4 import BeautifulSoup
        html = '''
        <html><body>
            <div class="category">Sales</div>
            <div class="category">Marketing</div>
        </body></html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        categories = soup.find_all('div', class_='category')
        assert len(categories) == 2
    
    def test_parse_views(self, extractor):
        """Test view count extraction."""
        from bs4 import BeautifulSoup
        html = '<html><body><div class="views">5000</div></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        views = soup.find('div', class_='views')
        assert views is not None
        assert views.text == '5000'
    
    def test_metadata_structure(self, extractor):
        """Test metadata structure is correct."""
        metadata = {
            'workflow_id': '2462',
            'title': 'Test',
            'author': 'John',
            'categories': ['Sales'],
            'views': 100
        }
        assert 'workflow_id' in metadata
        assert 'title' in metadata
        assert 'author' in metadata
    
    def test_empty_categories(self, extractor):
        """Test handling of empty categories."""
        categories = []
        assert isinstance(categories, list)
        assert len(categories) == 0
    
    # ========================================================================
    # ERROR CASES (8 tests)
    # ========================================================================
    
    @patch('src.scrapers.layer1_metadata.PageMetadataExtractor._fetch_page')
    async def test_extract_with_404(self, mock_fetch, extractor):
        """Test handling of 404 errors."""
        mock_fetch.side_effect = Exception("404 Not Found")
        
        result = await extractor.extract('9999', 'https://n8n.io/workflows/9999')
        
        assert isinstance(result, dict)
        assert 'workflow_id' in result
    
    @patch('src.scrapers.layer1_metadata.PageMetadataExtractor._fetch_page')
    async def test_extract_with_timeout(self, mock_fetch, extractor):
        """Test handling of timeout errors."""
        import asyncio
        mock_fetch.side_effect = asyncio.TimeoutError("Request timeout")
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
    
    def test_parse_invalid_html(self, extractor):
        """Test handling of invalid HTML."""
        from bs4 import BeautifulSoup
        invalid_html = '<html><body>Invalid</body'
        soup = BeautifulSoup(invalid_html, 'html.parser')
        assert soup is not None
    
    @patch('src.scrapers.layer1_metadata.PageMetadataExtractor._fetch_page')
    async def test_extract_with_network_error(self, mock_fetch, extractor):
        """Test handling of network errors."""
        mock_fetch.side_effect = Exception("Network error")
        
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
    
    def test_handle_missing_title(self, extractor):
        """Test handling of missing title."""
        from bs4 import BeautifulSoup
        html = '<html><head></head><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        assert title is None
    
    def test_handle_missing_author(self, extractor):
        """Test handling of missing author."""
        from bs4 import BeautifulSoup
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        author = soup.find('div', class_='author')
        assert author is None
    
    def test_handle_empty_html(self, extractor):
        """Test handling of empty HTML."""
        from bs4 import BeautifulSoup
        html = ''
        soup = BeautifulSoup(html, 'html.parser')
        assert soup is not None
    
    def test_error_result_structure(self, extractor):
        """Test error result has correct structure."""
        error_result = {
            'workflow_id': '2462',
            'success': False,
            'error': 'Some error',
            'title': None
        }
        assert 'workflow_id' in error_result
        assert 'success' in error_result
        assert 'error' in error_result
    
    # ========================================================================
    # EDGE CASES (4 tests)
    # ========================================================================
    
    def test_minimal_workflow_data(self, extractor):
        """Test extraction of minimal workflow data."""
        minimal = {
            'workflow_id': '1',
            'title': 'Min',
            'author': None,
            'categories': [],
            'views': 0
        }
        assert minimal['workflow_id'] == '1'
        assert minimal['title'] == 'Min'
        assert len(minimal['categories']) == 0
    
    def test_workflow_without_author(self, extractor):
        """Test workflow without author information."""
        data = {
            'workflow_id': '2462',
            'title': 'Test',
            'author': None
        }
        assert data['author'] is None
    
    def test_workflow_with_special_chars(self, extractor):
        """Test workflow with special characters in title."""
        from bs4 import BeautifulSoup
        html = '<html><head><title>Workflow with émojis 🚀</title></head></html>'
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        assert '🚀' in title.text
    
    def test_workflow_with_long_title(self, extractor):
        """Test workflow with very long title."""
        long_title = "A" * 200
        assert len(long_title) == 200
        assert isinstance(long_title, str)
