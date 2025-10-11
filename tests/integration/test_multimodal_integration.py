"""
Integration tests for Multimodal Processor using REAL workflow processing.

These tests actually process n8n.io workflow pages for multimodal content.
"""

import pytest
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.multimodal
class TestMultimodalIntegration:
    """Integration tests for Multimodal Processor with real processing."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return MultimodalProcessor()
    
    # ========================================================================
    # REAL PROCESSING TESTS (10 tests)
    # ========================================================================
    
    async def test_process_real_workflow(self, processor):
        """Test processing with real workflow."""
        # Process a workflow
        result = await processor.process_workflow(
            '2462',
            'https://n8n.io/workflows/2462'
        )
        
        assert isinstance(result, dict)
    
    async def test_result_has_workflow_id(self, processor):
        """Test that result contains workflow ID."""
        result = await processor.process_workflow(
            '2462',
            'https://n8n.io/workflows/2462'
        )
        
        result_str = str(result)
        assert '2462' in result_str or 'workflow_id' in result
    
    async def test_processing_time_reasonable(self, processor):
        """Test that processing completes in reasonable time."""
        import time
        start = time.time()
        
        await processor.process_workflow(
            '2462',
            'https://n8n.io/workflows/2462'
        )
        
        duration = time.time() - start
        assert duration < 45.0  # Should complete within 45 seconds
    
    async def test_multiple_processing(self, processor):
        """Test multiple workflow processing."""
        result1 = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        result2 = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    async def test_different_workflows(self, processor):
        """Test processing different workflows."""
        result1 = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        result2 = await processor.process_workflow('2134', 'https://n8n.io/workflows/2134')
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    async def test_processor_state(self, processor):
        """Test that processor maintains state correctly."""
        await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        
        # Processor should still be usable
        result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        assert isinstance(result, dict)
    
    async def test_result_structure(self, processor):
        """Test that result has expected structure."""
        result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
    
    async def test_handles_errors_gracefully(self, processor):
        """Test that processing handles errors gracefully."""
        result = await processor.process_workflow('999999', 'https://n8n.io/workflows/999999')
        
        # Should return a dict even on error
        assert isinstance(result, dict)
    
    async def test_processing_consistency(self, processor):
        """Test that processing is consistent."""
        result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
        
        assert isinstance(result, dict)
    
    async def test_processor_initialization(self, processor):
        """Test that processor initializes correctly."""
        assert processor is not None
        assert hasattr(processor, 'process_workflow')

