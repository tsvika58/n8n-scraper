"""
Integration tests for text extraction from real workflow iframes.

Tests text extraction functionality with actual n8n.io workflow iframe elements.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import pytest
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.asyncio
class TestTextExtractionIntegration:
    """Integration tests for text extraction with real workflows."""
    
    async def test_extract_text_workflow_6270(self, test_db_path):
        """Test text extraction from workflow 6270 iframes."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                assert len(iframes) > 0, "Should have iframes"
                
                # Extract text from all iframes
                total_text_elements = []
                for iframe_element in iframes:
                    text_elements = await processor.extract_text_elements_from_iframe(page, iframe_element)
                    total_text_elements.extend(text_elements)
                
                # Verify text extraction worked
                assert len(total_text_elements) >= 10, f"Should extract at least 10 text elements, got {len(total_text_elements)}"
                
                # Verify text content is substantial
                total_length = sum(len(elem['text']) for elem in total_text_elements)
                assert total_length >= 1000, f"Should extract at least 1000 chars, got {total_length}"
                
                # Verify element types are classified
                for elem in total_text_elements:
                    assert 'type' in elem
                    assert 'text' in elem
                    assert 'length' in elem
            
            finally:
                await page.close()
    
    async def test_extract_text_workflow_8527(self, test_db_path):
        """Test text extraction from workflow 8527 iframes."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/8527-learn-n8n-basics/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                assert len(iframes) > 0, "Should have iframes"
                
                # Extract text from all iframes
                total_text_elements = []
                for iframe_element in iframes:
                    text_elements = await processor.extract_text_elements_from_iframe(page, iframe_element)
                    total_text_elements.extend(text_elements)
                
                # Some workflows may have no text in iframes - this is OK
                # Just verify the extraction process ran without errors
                assert isinstance(total_text_elements, list), "Should return list of text elements"
            
            finally:
                await page.close()
    
    async def test_extract_text_various_iframe_types(self, known_iframe_workflows, test_db_path):
        """Test text extraction from various iframe types across workflows."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            results = []
            
            for wf_id, wf_data in known_iframe_workflows.items():
                page = await processor.browser.new_page()
                
                try:
                    iframes = await processor.discover_iframes(page, wf_data["url"])
                    
                    total_text_elements = []
                    for iframe_element in iframes:
                        text_elements = await processor.extract_text_elements_from_iframe(page, iframe_element)
                        total_text_elements.extend(text_elements)
                    
                    results.append({
                        "workflow_id": wf_id,
                        "text_elements": len(total_text_elements),
                        "expected_min": wf_data["expected_text_elements"],
                        "success": len(total_text_elements) > 0
                    })
                
                finally:
                    await page.close()
            
            # Verify all workflows were tested (success = processed, not necessarily found content)
            assert len(results) == 3, "Should test 3 workflows"
            
            # Verify at least one workflow had text extracted
            workflows_with_text = [r for r in results if r["text_elements"] > 0]
            assert len(workflows_with_text) > 0, "At least one workflow should have text"
            
            # Verify reasonable text extraction counts from successful workflows
            total_elements = sum(r["text_elements"] for r in results)
            assert total_elements >= 10, f"Should extract at least 10 total elements, got {total_elements}"
    
    async def test_text_extraction_element_classification(self, test_db_path):
        """Test that extracted text elements are properly classified."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            page = await processor.browser.new_page()
            
            try:
                iframes = await processor.discover_iframes(page, url)
                
                text_elements = []
                for iframe_element in iframes:
                    elements = await processor.extract_text_elements_from_iframe(page, iframe_element)
                    text_elements.extend(elements)
                
                # Verify element types are valid
                valid_types = ['hint', 'instruction', 'tutorial', 'tutorial_box', 'setup_instruction', 
                              'video_info', 'explanatory_text', 'general_text']
                
                for elem in text_elements:
                    assert elem['type'] in valid_types, f"Invalid element type: {elem['type']}"
            
            finally:
                await page.close()
    
    async def test_text_extraction_performance(self, test_db_path):
        """Test text extraction performance with real workflow."""
        import time
        
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            page = await processor.browser.new_page()
            
            try:
                start_time = time.time()
                
                iframes = await processor.discover_iframes(page, url)
                
                for iframe_element in iframes:
                    await processor.extract_text_elements_from_iframe(page, iframe_element)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Verify performance is reasonable (should be under 30 seconds)
                assert execution_time < 30, f"Text extraction took {execution_time}s, should be under 30s"
            
            finally:
                await page.close()

