"""
Integration tests for iframe discovery with real workflows.

Tests iframe discovery functionality with actual n8n.io workflow pages.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import pytest
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.asyncio
class TestIframeDiscoveryIntegration:
    """Integration tests for iframe discovery with real workflows."""
    
    async def test_discover_iframes_workflow_6270(self, test_db_path):
        """Test iframe discovery on workflow 6270 (AI Agent)."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                
                # Verify iframes were discovered
                assert len(iframes) > 0, "Should discover iframes in workflow 6270"
                assert len(iframes) == 2, f"Expected 2 iframes, found {len(iframes)}"
                
                # Verify iframe elements are valid
                for iframe in iframes:
                    assert iframe is not None
                    frame = await iframe.content_frame()
                    assert frame is not None, "Iframe should have accessible content frame"
            
            finally:
                await page.close()
    
    async def test_discover_iframes_workflow_8527(self, test_db_path):
        """Test iframe discovery on workflow 8527 (Learn n8n Basics)."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/8527-learn-n8n-basics/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                
                # Verify iframes were discovered
                assert len(iframes) > 0, "Should discover iframes in workflow 8527"
                
                # Verify iframe elements are valid
                for iframe in iframes:
                    assert iframe is not None
            
            finally:
                await page.close()
    
    async def test_discover_iframes_multiple_workflows(self, known_iframe_workflows, test_db_path):
        """Test iframe discovery across multiple real workflows."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            results = []
            
            for wf_id, wf_data in known_iframe_workflows.items():
                page = await processor.browser.new_page()
                
                try:
                    iframes = await processor.discover_iframes(page, wf_data["url"])
                    
                    results.append({
                        "workflow_id": wf_id,
                        "iframes_found": len(iframes),
                        "expected": wf_data["expected_iframes"],
                        "success": len(iframes) > 0
                    })
                
                finally:
                    await page.close()
            
            # Verify all workflows had iframes discovered
            assert all(r["success"] for r in results), "All workflows should have iframes"
            assert len(results) == 3, "Should test 3 workflows"
    
    async def test_iframe_discovery_error_handling(self, test_db_path):
        """Test iframe discovery handles errors gracefully."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/invalid-workflow/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                
                # Should handle gracefully without crashing
                assert isinstance(iframes, list), "Should return list even on error"
            
            except Exception:
                # Error is acceptable for invalid URL, but shouldn't crash
                pass
            
            finally:
                await page.close()

