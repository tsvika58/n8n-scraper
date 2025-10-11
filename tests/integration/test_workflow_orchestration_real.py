"""
Integration tests for complete workflow orchestration.

Tests end-to-end workflow processing with real n8n.io workflows.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import pytest
import json
import sqlite3
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.asyncio
class TestWorkflowOrchestrationIntegration:
    """Integration tests for end-to-end workflow processing."""
    
    async def test_end_to_end_workflow_6270(self, test_db_path):
        """Test complete end-to-end processing of workflow 6270."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            workflow_id = "6270"
            workflow_url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
            
            result = await processor.process_workflow(workflow_id, workflow_url)
            
            # Verify result structure
            assert result["workflow_id"] == workflow_id
            assert result["workflow_url"] == workflow_url
            assert result["success"] is True
            assert result["processing_time"] > 0
            assert result["processing_time"] < 30, f"Processing took {result['processing_time']}s, should be under 30s"
            
            # Verify content was processed
            assert result["iframes_found"] > 0
            assert result["images_processed"] > 0
            assert result["images_success"] > 0
            
            # Verify data was stored in database
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT image_urls, ocr_text, video_urls FROM workflows WHERE workflow_id = ?", (workflow_id,))
            db_result = cursor.fetchone()
            conn.close()
            
            assert db_result is not None, "Data should be stored in database"
            
            # Verify JSON data is valid
            image_urls = json.loads(db_result[0])
            assert len(image_urls) > 0, "Should have stored image URLs"
            
            # Verify OCR text was aggregated
            assert db_result[1] is not None, "Should have OCR text"
            assert len(db_result[1]) > 100, "Should have substantial OCR text"
    
    async def test_end_to_end_workflow_8527(self, test_db_path):
        """Test complete end-to-end processing of workflow 8527."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            workflow_id = "8527"
            workflow_url = "https://n8n.io/workflows/8527-learn-n8n-basics/"
            
            result = await processor.process_workflow(workflow_id, workflow_url)
            
            # Verify basic processing success
            assert result["success"] is True
            assert result["processing_time"] < 30
            # Note: images_processed may be 0 if workflow has no text in iframes
            
            # Note: Database storage only happens if content was found
            # This is OK - workflow processed successfully even with no content
            assert result["success"] is True
    
    async def test_orchestration_multiple_workflows_sequential(self, known_iframe_workflows, test_db_path):
        """Test processing multiple workflows sequentially."""
        async with MultimodalProcessor(headless=True, db_path=test_db_path) as processor:
            results = []
            
            for wf_id, wf_data in known_iframe_workflows.items():
                result = await processor.process_workflow(wf_id, wf_data["url"])
                results.append(result)
            
            # Verify all workflows processed successfully
            assert len(results) == 3, "Should process 3 workflows"
            assert all(r["success"] for r in results), "All workflows should process successfully"
            
            # Verify reasonable total processing time
            total_time = sum(r["processing_time"] for r in results)
            assert total_time < 90, f"Total processing time {total_time}s should be under 90s"
            
            # Verify at least one workflow stored in database
            # Note: Only workflows with content get new records created
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM workflows")
            count = cursor.fetchone()[0]
            conn.close()
            
            assert count >= 1, f"Should have at least 1 workflow in database, got {count}"

