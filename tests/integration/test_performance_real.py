"""
Integration tests for performance validation with real workflows.

Tests processing performance under real-world conditions.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import pytest
import time
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.asyncio
class TestPerformanceIntegration:
    """Integration tests for performance validation."""
    
    async def test_processing_performance_workflow_6270(self, test_db_path):
        """Test processing performance on workflow 6270."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            workflow_id = "6270"
            workflow_url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            
            start_time = time.time()
            result = await processor.process_workflow(workflow_id, workflow_url)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Verify performance targets
            assert execution_time < 30, f"Processing took {execution_time}s, should be under 30s"
            assert result["processing_time"] < 30, f"Reported time {result['processing_time']}s, should be under 30s"
            
            # Verify processing was successful
            assert result["success"] is True
            assert result["images_processed"] > 0
    
    async def test_processing_performance_multiple_workflows(self, known_iframe_workflows, test_db_path):
        """Test processing performance across multiple workflows."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            results = []
            
            for wf_id, wf_data in known_iframe_workflows.items():
                start_time = time.time()
                result = await processor.process_workflow(wf_id, wf_data["url"])
                end_time = time.time()
                
                results.append({
                    "workflow_id": wf_id,
                    "processing_time": end_time - start_time,
                    "reported_time": result["processing_time"],
                    "success": result["success"]
                })
            
            # Verify all workflows processed successfully
            assert all(r["success"] for r in results), "All workflows should process successfully"
            
            # Verify individual processing times
            for r in results:
                assert r["processing_time"] < 30, f"Workflow {r['workflow_id']} took {r['processing_time']}s"
            
            # Verify average processing time
            avg_time = sum(r["processing_time"] for r in results) / len(results)
            assert avg_time < 30, f"Average processing time {avg_time}s should be under 30s"
    
    async def test_memory_management_during_processing(self, test_db_path):
        """Test memory management during workflow processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            # Process workflow
            await processor.process_workflow("6270", "https://n8n.io/workflows/6270-build-your-first-ai-agent/")
            
            # Check memory after processing
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Verify memory usage is reasonable (should be under 500MB increase)
            assert memory_increase < 500, f"Memory increased by {memory_increase}MB, should be under 500MB"
    
    async def test_browser_automation_reliability(self, test_db_path):
        """Test browser automation reliability across multiple operations."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            # Perform multiple operations to test reliability
            operations_successful = 0
            total_operations = 5
            url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            
            for i in range(total_operations):
                try:
                    page = await processor.browser.new_page()
                    
                    iframes = await processor.discover_iframes(page, url)
                    if len(iframes) > 0:
                        operations_successful += 1
                    
                    await page.close()
                except Exception:
                    pass
            
            # Verify reliability (should succeed most of the time)
            reliability_rate = operations_successful / total_operations
            assert reliability_rate >= 0.8, f"Browser automation reliability {reliability_rate} below 80%"

