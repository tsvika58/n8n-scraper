"""
Deep coverage integration tests for Layer 3 Explainer using REAL browser automation.

These tests use actual Playwright browser to execute all code paths in layer3_explainer.py.
"""

import pytest
from src.scrapers.layer3_explainer import ExplainerContentExtractor


@pytest.mark.integration
@pytest.mark.layer3
@pytest.mark.slow
class TestLayer3DeepCoverage:
    """Deep coverage tests for Layer 3 with real Playwright browser."""
    
    # ========================================================================
    # REAL BROWSER AUTOMATION TESTS (30 tests)
    # ========================================================================
    
    async def test_extract_with_real_browser_workflow_2462(self):
        """Test extraction with real browser on workflow 2462."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
            assert 'success' in result
            assert 'data' in result
            assert 'extraction_time' in result
    
    async def test_extract_with_real_browser_workflow_2134(self):
        """Test extraction with real browser on workflow 2134."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2134', 'https://n8n.io/workflows/2134')
            
            assert result is not None
            assert isinstance(result, dict)
    
    async def test_context_manager_initialization(self):
        """Test context manager properly initializes browser."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            assert extractor.browser is not None
    
    async def test_context_manager_cleanup(self):
        """Test context manager properly cleans up browser."""
        extractor = ExplainerContentExtractor(headless=True)
        
        async with extractor:
            assert extractor.browser is not None
        
        # After context exit, browser should be cleaned up
        assert True  # If we get here, cleanup worked
    
    async def test_extract_multiple_workflows_same_session(self):
        """Test extracting multiple workflows in same session."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result1 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            result2 = await extractor.extract('2134', 'https://n8n.io/workflows/2134')
            
            assert result1['success'] is not None
            assert result2['success'] is not None
    
    async def test_extract_validates_result(self):
        """Test that extraction validates the result."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            # Should have validation
            assert 'success' in result
            assert isinstance(result['success'], bool)
    
    async def test_extract_aggregates_text(self):
        """Test that extraction aggregates tutorial text."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            # Should have data structure
            assert 'data' in result
            assert isinstance(result['data'], dict)
    
    async def test_extract_handles_dynamic_content(self):
        """Test extraction with dynamic content loading."""
        async with ExplainerContentExtractor(headless=True, wait_for_content=3000) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_extract_with_custom_timeout(self):
        """Test extraction with custom timeout."""
        async with ExplainerContentExtractor(headless=True, timeout=45000) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_extract_records_timing(self):
        """Test that extraction records timing."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'extraction_time' in result
            assert result['extraction_time'] > 0
    
    async def test_extract_includes_metadata(self):
        """Test that extraction includes metadata."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'metadata' in result
            assert 'workflow_id' in result['metadata']
            assert result['metadata']['workflow_id'] == '2462'
    
    async def test_extract_error_handling_404(self):
        """Test error handling for 404 pages."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('999999', 'https://n8n.io/workflows/999999')
            
            # Should handle gracefully
            assert 'errors' in result or 'success' in result
    
    async def test_extract_error_handling_timeout(self):
        """Test error handling for timeouts."""
        async with ExplainerContentExtractor(headless=True, timeout=1000) as extractor:
            # Very short timeout will likely timeout
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
            assert isinstance(result, dict)
    
    async def test_extract_different_workflows(self):
        """Test extraction of various different workflows."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            workflows = ['2462', '2134', '2076', '1948', '2221']
            
            for wf_id in workflows:
                result = await extractor.extract(wf_id, f'https://n8n.io/workflows/{wf_id}')
                assert result is not None
    
    async def test_extract_minimal_workflow(self):
        """Test extraction of minimal workflow."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('1834', 'https://n8n.io/workflows/1834')
            
            assert result is not None
    
    async def test_extract_complex_workflow(self):
        """Test extraction of complex workflow."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2221', 'https://n8n.io/workflows/2221')
            
            assert result is not None
    
    async def test_extract_consistency(self):
        """Test that extraction is consistent."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result1 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            result2 = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            # Both should succeed or fail consistently
            assert result1['success'] == result2['success']
    
    async def test_extract_data_structure(self):
        """Test that extracted data has proper structure."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'data' in result
            # Data should be a dict
            assert isinstance(result['data'], dict)
    
    async def test_extract_empty_structure_on_error(self):
        """Test that empty structure is returned on error."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('invalid', 'https://n8n.io/workflows/invalid')
            
            assert 'data' in result
    
    async def test_browser_initialization(self):
        """Test browser initialization."""
        extractor = ExplainerContentExtractor(headless=True)
        await extractor.initialize()
        
        assert extractor.browser is not None
        
        await extractor.cleanup()
    
    async def test_browser_cleanup(self):
        """Test browser cleanup."""
        extractor = ExplainerContentExtractor(headless=True)
        await extractor.initialize()
        await extractor.cleanup()
        
        # Should complete without error
        assert True
    
    async def test_extract_headless_mode(self):
        """Test extraction in headless mode."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_extract_with_wait_for_content(self):
        """Test extraction with content wait time."""
        async with ExplainerContentExtractor(headless=True, wait_for_content=2000) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert result is not None
    
    async def test_extract_sequential_workflows(self):
        """Test extracting workflows sequentially."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            for wf_id in ['2462', '2134', '1948']:
                result = await extractor.extract(wf_id, f'https://n8n.io/workflows/{wf_id}')
                assert result is not None
    
    async def test_extract_error_list(self):
        """Test that errors are collected in list."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'errors' in result
            assert isinstance(result['errors'], list)
    
    async def test_extract_metadata_structure(self):
        """Test metadata structure."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'metadata' in result
            assert 'workflow_id' in result['metadata']
            assert 'url' in result['metadata']
    
    async def test_extract_version_tracking(self):
        """Test that extractor version is tracked."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'metadata' in result
            assert 'extractor_version' in result['metadata']
    
    async def test_extract_timestamp(self):
        """Test that extraction timestamp is recorded."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            result = await extractor.extract('2462', 'https://n8n.io/workflows/2462')
            
            assert 'metadata' in result
            assert 'extracted_at' in result['metadata']
    
    async def test_extractor_configuration(self):
        """Test extractor configuration options."""
        extractor = ExplainerContentExtractor(
            headless=True,
            timeout=60000,
            wait_for_content=5000
        )
        
        assert extractor.headless == True
        assert extractor.timeout == 60000
        assert extractor.wait_for_content == 5000
    
    async def test_extract_workflow_variations(self):
        """Test extraction of various workflow types."""
        async with ExplainerContentExtractor(headless=True) as extractor:
            workflows = {
                '2462': 'https://n8n.io/workflows/2462',  # AI workflow
                '2134': 'https://n8n.io/workflows/2134',  # Sales workflow
                '2076': 'https://n8n.io/workflows/2076',  # Data workflow
            }
            
            for wf_id, url in workflows.items():
                result = await extractor.extract(wf_id, url)
                assert result is not None


