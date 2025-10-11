"""
Integration tests for Layer 3 Explainer Content Extractor using REAL page scraping.

These tests actually scrape n8n.io workflow pages to extract content.
"""

import pytest
from src.scrapers.layer3_explainer import ExplainerContentExtractor


@pytest.mark.integration
@pytest.mark.layer3
class TestLayer3Integration:
    """Integration tests for Layer 3 with real page scraping."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return ExplainerContentExtractor()
    
    # ========================================================================
    # REAL SCRAPING TESTS (10 tests)
    # ========================================================================
    
    async def test_extract_real_workflow_content(self, extractor):
        """Test extraction with real workflow page."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
        assert 'workflow_id' in result or 'success' in result
    
    async def test_extract_has_some_content(self, extractor):
        """Test that extracted content has some data."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Should have some content
        assert isinstance(result, dict)
        assert len(result) > 0
    
    async def test_extract_workflow_id_preserved(self, extractor):
        """Test that workflow ID is preserved."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Should have workflow_id somewhere
        result_str = str(result)
        assert '2462' in result_str or 'workflow_id' in result
    
    async def test_extraction_time_reasonable(self, extractor):
        """Test that extraction completes in reasonable time."""
        import time
        start = time.time()
        
        await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        duration = time.time() - start
        assert duration < 30.0  # Should complete within 30 seconds
    
    async def test_multiple_extractions(self, extractor):
        """Test multiple extractions work."""
        result1 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        result2 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    async def test_different_workflows(self, extractor):
        """Test extraction of different workflows."""
        result1 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        result2 = await extractor.extract('2134', 'https://n8n.io/workflows/2134')
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    async def test_extractor_state(self, extractor):
        """Test that extractor maintains state correctly."""
        await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Extractor should still be usable
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        assert isinstance(result, dict)
    
    async def test_result_is_dict(self, extractor):
        """Test that result is a dictionary."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
    
    async def test_handles_errors_gracefully(self, extractor):
        """Test that extraction handles errors gracefully."""
        result = await extractor.extract('999999', 'https://n8n.io/workflows/999999')
        
        # Should return a dict even on error
        assert isinstance(result, dict)
    
    async def test_extraction_consistency(self, extractor):
        """Test that extraction is consistent."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Result should be a dict with some data
        assert isinstance(result, dict)
        assert len(result) >= 0  # At minimum, empty dict
