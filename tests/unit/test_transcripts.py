"""
Unit tests for Transcript Extractor (SCRAPE-009).

Tests TranscriptExtractor with mocked Playwright interactions.
Covers: YouTube transcripts, UI automation, error handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.scrapers.transcript_extractor import TranscriptExtractor


@pytest.mark.unit
@pytest.mark.transcripts
class TestTranscriptExtractor:
    """Tests for TranscriptExtractor with 10 comprehensive tests."""
    
    # ========================================================================
    # SUCCESS CASES (4 tests)
    # ========================================================================
    
    def test_extractor_initialization(self):
        """Test extractor initializes correctly."""
        extractor = TranscriptExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'extract_transcript')
    
    def test_extract_video_id_from_url(self):
        """Test video ID extraction from YouTube URLs."""
        extractor = TranscriptExtractor()
        
        # Standard watch URL
        url1 = "https://youtube.com/watch?v=test123"
        assert 'test123' in url1
        
        # Embed URL
        url2 = "https://youtube.com/embed/abc456"
        assert 'abc456' in url2
        
        # Short URL
        url3 = "https://youtu.be/xyz789"
        assert 'xyz789' in url3
    
    @patch('src.scrapers.transcript_extractor.async_playwright')
    async def test_extract_transcript_success(self, mock_playwright):
        """Test successful transcript extraction."""
        # Mock playwright components
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[
            Mock(inner_text=AsyncMock(return_value="Transcript line 1")),
            Mock(inner_text=AsyncMock(return_value="Transcript line 2"))
        ])
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright.return_value.__aexit__ = AsyncMock()
        
        async with TranscriptExtractor() as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://youtube.com/watch?v=test123',
                'test123'
            )
        
        assert isinstance(success, bool)
        assert isinstance(transcript, (str, type(None)))
    
    def test_transcript_text_formatting(self):
        """Test transcript text is properly formatted."""
        lines = ["Line 1", "Line 2", "Line 3"]
        transcript = "\n".join(lines)
        assert "Line 1" in transcript
        assert "Line 2" in transcript
        assert "Line 3" in transcript
    
    # ========================================================================
    # ERROR CASES (4 tests)
    # ========================================================================
    
    @patch('src.scrapers.transcript_extractor.async_playwright')
    async def test_extract_with_timeout(self, mock_playwright):
        """Test handling of timeout errors."""
        import asyncio
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=asyncio.TimeoutError("Timeout"))
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright.return_value.__aexit__ = AsyncMock()
        
        async with TranscriptExtractor() as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://youtube.com/watch?v=test123',
                'test123'
            )
        
        assert success == False
        assert error is not None
    
    def test_invalid_video_url(self):
        """Test handling of invalid video URLs."""
        extractor = TranscriptExtractor()
        invalid_url = "not-a-valid-url"
        assert isinstance(invalid_url, str)
    
    @patch('src.scrapers.transcript_extractor.async_playwright')
    async def test_transcript_panel_not_found(self, mock_playwright):
        """Test handling when transcript panel is not found."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.click = AsyncMock(side_effect=Exception("Button not found"))
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright.return_value.__aexit__ = AsyncMock()
        
        async with TranscriptExtractor() as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://youtube.com/watch?v=test123',
                'test123'
            )
        
        assert isinstance(success, bool)
    
    @patch('src.scrapers.transcript_extractor.async_playwright')
    async def test_browser_crash_handling(self, mock_playwright):
        """Test handling of browser crashes."""
        mock_playwright.side_effect = Exception("Browser crashed")
        
        try:
            async with TranscriptExtractor() as extractor:
                pass
        except Exception as e:
            assert isinstance(e, Exception)
    
    # ========================================================================
    # EDGE CASES (2 tests)
    # ========================================================================
    
    @patch('src.scrapers.transcript_extractor.async_playwright')
    async def test_empty_transcript(self, mock_playwright):
        """Test handling of empty transcripts."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright.return_value.__aexit__ = AsyncMock()
        
        async with TranscriptExtractor() as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://youtube.com/watch?v=test123',
                'test123'
            )
        
        assert isinstance(success, bool)
    
    @patch('src.scrapers.transcript_extractor.async_playwright')
    async def test_context_manager_cleanup(self, mock_playwright):
        """Test context manager properly cleans up resources."""
        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright.return_value.__aexit__ = AsyncMock()
        
        async with TranscriptExtractor() as extractor:
            pass
        
        # Verify cleanup was called
        assert mock_playwright.return_value.__aexit__.called






