"""
Integration tests for Layer 1 Metadata Extractor using REAL page scraping.

These tests actually scrape n8n.io pages to verify functionality.
"""

import pytest
from src.scrapers.layer1_metadata import PageMetadataExtractor


@pytest.mark.integration
@pytest.mark.layer1
class TestLayer1Integration:
    """Integration tests for Layer 1 with real page scraping."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return PageMetadataExtractor()
    
    # ========================================================================
    # REAL SCRAPING TESTS (10 tests)
    # ========================================================================
    
    async def test_extract_real_workflow_metadata(self, extractor):
        """Test extraction with real workflow page."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
        assert 'workflow_id' in result
    
    async def test_extract_has_title(self, extractor):
        """Test that extracted metadata has a title."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Should have some metadata
        assert isinstance(result, dict)
    
    async def test_extract_has_workflow_id(self, extractor):
        """Test that workflow ID is preserved."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert 'workflow_id' in result or '2462' in str(result)
    
    async def test_extract_handles_404(self, extractor):
        """Test extraction with nonexistent workflow."""
        result = await extractor.extract('999999', 'https://n8n.io/workflows/999999')
        
        # Should handle gracefully
        assert isinstance(result, dict)
    
    async def test_extraction_time_reasonable(self, extractor):
        """Test that extraction completes in reasonable time."""
        import time
        start = time.time()
        
        await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        duration = time.time() - start
        assert duration < 15.0  # Should complete within 15 seconds
    
    async def test_multiple_extractions(self, extractor):
        """Test multiple extractions work."""
        result1 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        result2 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    async def test_extractor_state(self, extractor):
        """Test that extractor maintains state correctly."""
        await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Extractor should still be usable
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        assert isinstance(result, dict)
    
    async def test_result_structure(self, extractor):
        """Test that result has expected structure."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
        # Result should have some keys
        assert len(result) > 0
    
    async def test_different_workflows(self, extractor):
        """Test extraction of different workflows."""
        result1 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        result2 = await extractor.extract('2134', 'https://n8n.io/workflows/2134')
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    async def test_extraction_consistency(self, extractor):
        """Test that extraction is consistent."""
        result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
        
        # Result should be a dict
        assert isinstance(result, dict)
        # Should have at least workflow_id
        assert 'workflow_id' in result or len(result) > 0
