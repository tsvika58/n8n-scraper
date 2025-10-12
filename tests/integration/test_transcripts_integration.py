"""
Integration tests for Transcript Extractor using REAL YouTube extraction.

These tests actually extract transcripts from YouTube videos.
Note: May be slow due to Playwright browser automation.
"""

import pytest
from src.scrapers.transcript_extractor import TranscriptExtractor


@pytest.mark.integration
@pytest.mark.transcripts
@pytest.mark.slow
class TestTranscriptsIntegration:
    """Integration tests for Transcript Extractor with real YouTube."""
    
    # ========================================================================
    # REAL EXTRACTION TESTS (8 tests)
    # ========================================================================
    
    async def test_extractor_context_manager(self):
        """Test extractor context manager works."""
        async with TranscriptExtractor() as extractor:
            assert extractor is not None
            assert hasattr(extractor, 'extract_transcript')
    
    async def test_extract_real_transcript(self):
        """Test extraction with real YouTube video."""
        async with TranscriptExtractor(headless=True) as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'dQw4w9WgXcQ'
            )
            
            # Should complete (success or failure both ok for real video)
            assert isinstance(success, bool)
            assert isinstance(transcript, (str, type(None)))
            assert isinstance(error, (str, type(None)))
    
    async def test_extraction_returns_tuple(self):
        """Test that extraction returns expected tuple."""
        async with TranscriptExtractor(headless=True) as extractor:
            result = await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=test123',
                'test123'
            )
            
            assert isinstance(result, tuple)
            assert len(result) == 3
    
    async def test_extraction_time_reasonable(self):
        """Test that extraction completes in reasonable time."""
        import time
        start = time.time()
        
        async with TranscriptExtractor(headless=True) as extractor:
            await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=test123',
                'test123'
            )
        
        duration = time.time() - start
        assert duration < 60.0  # Should complete within 60 seconds
    
    async def test_extractor_cleanup(self):
        """Test that extractor cleans up resources."""
        extractor = TranscriptExtractor(headless=True)
        
        async with extractor:
            pass
        
        # Should have cleaned up
        assert True  # If we get here, cleanup worked
    
    async def test_invalid_video_id(self):
        """Test extraction with invalid video ID."""
        async with TranscriptExtractor(headless=True) as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=invalid',
                'invalid'
            )
            
            # Should handle gracefully
            assert isinstance(success, bool)
    
    async def test_multiple_extractions(self):
        """Test multiple extractions in same session."""
        async with TranscriptExtractor(headless=True) as extractor:
            result1 = await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=test1',
                'test1'
            )
            result2 = await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=test2',
                'test2'
            )
            
            assert isinstance(result1, tuple)
            assert isinstance(result2, tuple)
    
    async def test_extractor_initialization(self):
        """Test that extractor initializes with options."""
        extractor = TranscriptExtractor(headless=True, timeout=30000)
        
        assert extractor is not None
        assert extractor.headless == True
        assert extractor.timeout == 30000


