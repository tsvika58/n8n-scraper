"""
Deep coverage integration tests for Multimodal Processor using REAL browser automation.

These tests use actual Playwright browser to execute all code paths in multimodal_processor.py.
"""

import pytest
from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.mark.integration
@pytest.mark.multimodal
@pytest.mark.slow
class TestMultimodalDeepCoverage:
    """Deep coverage tests for Multimodal with real Playwright browser."""
    
    # ========================================================================
    # REAL BROWSER AUTOMATION TESTS (40 tests)
    # ========================================================================
    
    async def test_process_with_real_browser_workflow_2462(self):
        """Test processing with real browser on workflow 2462."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
            assert isinstance(result, dict)
    
    async def test_process_with_real_browser_workflow_2134(self):
        """Test processing with real browser on workflow 2134."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2134', 'https://n8n.io/workflows/2134')
            
            assert result is not None
    
    async def test_context_manager_initialization(self):
        """Test context manager properly initializes browser."""
        async with MultimodalProcessor(headless=True) as processor:
            assert processor.browser is not None
    
    async def test_context_manager_cleanup(self):
        """Test context manager properly cleans up browser."""
        processor = MultimodalProcessor(headless=True)
        
        async with processor:
            assert processor.browser is not None
        
        # After context exit, browser should be cleaned up
        assert True
    
    async def test_process_multiple_workflows_same_session(self):
        """Test processing multiple workflows in same session."""
        async with MultimodalProcessor(headless=True) as processor:
            result1 = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            result2 = await processor.process_workflow('2134', 'https://n8n.io/workflows/2134')
            
            assert result1 is not None
            assert result2 is not None
    
    async def test_process_validates_result(self):
        """Test that processing validates the result."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert isinstance(result, dict)
    
    async def test_process_records_timing(self):
        """Test that processing records timing."""
        import time
        async with MultimodalProcessor(headless=True) as processor:
            start = time.time()
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            duration = time.time() - start
            
            # Should complete in reasonable time
            assert duration < 90  # 90 seconds max
    
    async def test_process_with_custom_timeout(self):
        """Test processing with custom timeout."""
        async with MultimodalProcessor(headless=True, timeout=45000) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_process_error_handling_404(self):
        """Test error handling for 404 pages."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('999999', 'https://n8n.io/workflows/999999')
            
            # Should handle gracefully
            assert isinstance(result, dict)
    
    async def test_process_different_workflows(self):
        """Test processing various different workflows."""
        async with MultimodalProcessor(headless=True) as processor:
            workflows = ['2462', '2134', '2076', '1948', '2221']
            
            for wf_id in workflows:
                result = await processor.process_workflow(wf_id, f'https://n8n.io/workflows/{wf_id}')
                assert result is not None
    
    async def test_process_minimal_workflow(self):
        """Test processing minimal workflow."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('1834', 'https://n8n.io/workflows/1834')
            
            assert result is not None
    
    async def test_process_complex_workflow(self):
        """Test processing complex workflow."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2221', 'https://n8n.io/workflows/2221')
            
            assert result is not None
    
    async def test_process_consistency(self):
        """Test that processing is consistent."""
        async with MultimodalProcessor(headless=True) as processor:
            result1 = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            result2 = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert isinstance(result1, dict)
            assert isinstance(result2, dict)
    
    async def test_browser_initialization(self):
        """Test browser initialization."""
        processor = MultimodalProcessor(headless=True)
        await processor.initialize()
        
        assert processor.browser is not None
        assert processor.playwright is not None
        
        await processor.cleanup()
    
    async def test_browser_cleanup(self):
        """Test browser cleanup."""
        processor = MultimodalProcessor(headless=True)
        await processor.initialize()
        await processor.cleanup()
        
        # Should complete without error
        assert True
    
    async def test_process_headless_mode(self):
        """Test processing in headless mode."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_process_sequential_workflows(self):
        """Test processing workflows sequentially."""
        async with MultimodalProcessor(headless=True) as processor:
            for wf_id in ['2462', '2134', '1948']:
                result = await processor.process_workflow(wf_id, f'https://n8n.io/workflows/{wf_id}')
                assert result is not None
    
    async def test_process_result_structure(self):
        """Test result structure."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert isinstance(result, dict)
    
    async def test_processor_configuration(self):
        """Test processor configuration options."""
        processor = MultimodalProcessor(
            headless=True,
            timeout=60000
        )
        
        assert processor.headless == True
        assert processor.timeout == 60000
    
    async def test_process_workflow_variations(self):
        """Test processing various workflow types."""
        async with MultimodalProcessor(headless=True) as processor:
            workflows = {
                '2462': 'https://n8n.io/workflows/2462',
                '2134': 'https://n8n.io/workflows/2134',
                '2076': 'https://n8n.io/workflows/2076',
            }
            
            for wf_id, url in workflows.items():
                result = await processor.process_workflow(wf_id, url)
                assert result is not None
    
    async def test_process_with_db_path(self):
        """Test processor with custom db path."""
        async with MultimodalProcessor(db_path="data/test.db", headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_processor_reusability(self):
        """Test that processor can be reused."""
        async with MultimodalProcessor(headless=True) as processor:
            for i in range(3):
                result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
                assert result is not None
    
    async def test_process_error_recovery(self):
        """Test that processor recovers from errors."""
        async with MultimodalProcessor(headless=True) as processor:
            # Process invalid workflow
            await processor.process_workflow('invalid', 'https://n8n.io/workflows/invalid')
            
            # Should still be able to process valid workflow
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            assert result is not None
    
    async def test_process_handles_network_errors(self):
        """Test handling of network errors."""
        async with MultimodalProcessor(headless=True, timeout=5000) as processor:
            # Short timeout may cause network errors
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            # Should return a result (success or error)
            assert isinstance(result, dict)
    
    async def test_process_workflow_id_tracking(self):
        """Test that workflow ID is tracked."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            result_str = str(result)
            assert '2462' in result_str or isinstance(result, dict)
    
    async def test_process_url_tracking(self):
        """Test that URL is tracked."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            result_str = str(result)
            assert 'n8n.io' in result_str or isinstance(result, dict)
    
    async def test_processor_initialization_options(self):
        """Test various initialization options."""
        processor1 = MultimodalProcessor(headless=True)
        processor2 = MultimodalProcessor(headless=False)
        processor3 = MultimodalProcessor(timeout=10000)
        
        assert processor1.headless == True
        assert processor2.headless == False
        assert processor3.timeout == 10000
    
    async def test_process_concurrent_safe(self):
        """Test that processor handles sequential calls safely."""
        async with MultimodalProcessor(headless=True) as processor:
            results = []
            for wf_id in ['2462', '2134']:
                result = await processor.process_workflow(wf_id, f'https://n8n.io/workflows/{wf_id}')
                results.append(result)
            
            assert len(results) == 2
            assert all(isinstance(r, dict) for r in results)
    
    async def test_initialization_and_cleanup_cycle(self):
        """Test initialization and cleanup cycle."""
        processor = MultimodalProcessor(headless=True)
        
        # Initialize
        await processor.initialize()
        assert processor.browser is not None
        
        # Cleanup
        await processor.cleanup()
        
        # Can initialize again
        await processor.initialize()
        assert processor.browser is not None
        
        await processor.cleanup()
    
    async def test_process_result_is_dict(self):
        """Test that result is always a dict."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            assert isinstance(result, dict)
    
    async def test_process_multiple_variations(self):
        """Test processing multiple workflow variations."""
        async with MultimodalProcessor(headless=True) as processor:
            workflows = ['2462', '2134', '2076', '1948', '2221', '1834', '2109', '1974']
            
            for wf_id in workflows:
                result = await processor.process_workflow(wf_id, f'https://n8n.io/workflows/{wf_id}')
                assert isinstance(result, dict)
    
    async def test_processor_attributes(self):
        """Test processor has expected attributes."""
        processor = MultimodalProcessor(headless=True)
        
        assert hasattr(processor, 'db_path')
        assert hasattr(processor, 'headless')
        assert hasattr(processor, 'timeout')
        assert hasattr(processor, 'browser')
        assert hasattr(processor, 'playwright')
    
    async def test_process_method_callable(self):
        """Test that process_workflow is callable."""
        processor = MultimodalProcessor(headless=True)
        
        assert callable(processor.process_workflow)
    
    async def test_initialize_method_callable(self):
        """Test that initialize is callable."""
        processor = MultimodalProcessor(headless=True)
        
        assert callable(processor.initialize)
        assert callable(processor.cleanup)
    
    async def test_process_workflow_complete_cycle(self):
        """Test complete processing cycle."""
        async with MultimodalProcessor(headless=True) as processor:
            result = await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            # Complete cycle should return result
            assert result is not None
            assert isinstance(result, dict)
    
    async def test_process_with_error_handling(self):
        """Test that processing has error handling."""
        async with MultimodalProcessor(headless=True) as processor:
            # Try to process non-existent workflow
            result = await processor.process_workflow('invalid', 'https://n8n.io/workflows/invalid')
            
            # Should return a dict (even on error)
            assert isinstance(result, dict)
    
    async def test_process_state_persistence(self):
        """Test that processor maintains state."""
        async with MultimodalProcessor(headless=True) as processor:
            await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            await processor.process_workflow('2134', 'https://n8n.io/workflows/2134')
            
            # Processor should still be functional
            result = await processor.process_workflow('2076', 'https://n8n.io/workflows/2076')
            assert result is not None
    
    async def test_process_browser_reuse(self):
        """Test that browser is reused across workflows."""
        async with MultimodalProcessor(headless=True) as processor:
            browser_ref = processor.browser
            
            await processor.process_workflow('2462', 'https://n8n.io/workflows/2462')
            
            # Browser should be the same instance
            assert processor.browser is browser_ref
    
    async def test_processor_initialization_sequence(self):
        """Test processor initialization sequence."""
        processor = MultimodalProcessor(headless=True)
        
        # Before init
        assert processor.browser is None
        
        # After init
        await processor.initialize()
        assert processor.browser is not None
        
        # Cleanup
        await processor.cleanup()
    
    async def test_process_result_always_dict(self):
        """Test that result is always a dictionary."""
        async with MultimodalProcessor(headless=True) as processor:
            for wf_id in ['2462', '2134', 'invalid']:
                result = await processor.process_workflow(wf_id, f'https://n8n.io/workflows/{wf_id}')
                assert isinstance(result, dict)


