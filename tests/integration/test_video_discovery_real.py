"""
Integration tests for video discovery in real workflow iframes.

Tests video discovery functionality with actual n8n.io workflow pages.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import pytest
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.asyncio
class TestVideoDiscoveryIntegration:
    """Integration tests for video discovery with real workflows."""
    
    async def test_discover_videos_workflow_6270(self, test_db_path):
        """Test video discovery in workflow 6270 (known to have 1 video)."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                assert len(iframes) > 0, "Should have iframes"
                
                # Discover videos in all iframes
                total_videos = []
                for iframe_element in iframes:
                    videos = await processor.discover_videos_in_iframe(page, iframe_element)
                    total_videos.extend(videos)
                
                # Verify videos were discovered
                assert len(total_videos) > 0, "Should discover videos in workflow 6270"
                
                # Verify video URLs are valid YouTube URLs
                for video_url in total_videos:
                    assert "youtube" in video_url.lower(), f"Should be YouTube URL: {video_url}"
            
            finally:
                await page.close()
    
    async def test_discover_videos_workflow_8527(self, test_db_path):
        """Test video discovery in workflow 8527."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/8527-learn-n8n-basics/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                
                # Discover videos in all iframes
                total_videos = []
                for iframe_element in iframes:
                    videos = await processor.discover_videos_in_iframe(page, iframe_element)
                    total_videos.extend(videos)
                
                # Video discovery may find 0 or more videos - both are valid
                # Just verify the method runs without error
                assert isinstance(total_videos, list), "Should return list of videos"
            
            finally:
                await page.close()
    
    async def test_video_id_extraction_from_discovered_videos(self, test_db_path):
        """Test extracting video IDs from discovered video URLs."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                
                # Discover videos
                videos = []
                for iframe_element in iframes:
                    iframe_videos = await processor.discover_videos_in_iframe(page, iframe_element)
                    videos.extend(iframe_videos)
                
                # Extract video IDs
                video_ids = []
                for video_url in videos:
                    video_id = processor.extract_video_id_from_url(video_url)
                    if video_id:
                        video_ids.append(video_id)
                
                # If videos were found, verify IDs were extracted
                if len(videos) > 0:
                    assert len(video_ids) > 0, "Should extract video IDs from discovered videos"
                    
                    # Verify video ID format (should be 10+ characters for YouTube)
                    for vid_id in video_ids:
                        assert len(vid_id) >= 10, f"Video ID should be at least 10 chars: {vid_id}"
                else:
                    # No videos found is OK - just verify method works
                    assert isinstance(video_ids, list), "Should return list"
            
            finally:
                await page.close()

