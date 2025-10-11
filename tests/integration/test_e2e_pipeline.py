"""
Integration Tests for E2E Pipeline - SCRAPE-007

Tests the complete end-to-end pipeline orchestrator that integrates
all extraction layers.

Author: RND Manager
Task: SCRAPE-007
Date: October 11, 2025
"""

import pytest
import asyncio
from src.orchestrator.e2e_pipeline import E2EPipeline


# Test workflows - diverse set for comprehensive testing
TEST_WORKFLOWS = [
    {
        'workflow_id': '2462',
        'url': 'https://n8n.io/workflows/2462',
        'name': 'Angie Personal AI Assistant',
        'expected_nodes': 15  # Approximate
    },
    {
        'workflow_id': '1804',
        'url': 'https://n8n.io/workflows/1804',
        'name': 'Connect Shopify',
        'expected_nodes': 10
    },
    {
        'workflow_id': '1956',
        'url': 'https://n8n.io/workflows/1956',
        'name': 'Send Slack notification',
        'expected_nodes': 5
    }
]


@pytest.fixture
async def pipeline():
    """Create E2E pipeline instance."""
    return E2EPipeline(
        db_path="data/workflows_test.db",
        headless=True,
        timeout=30000
    )


@pytest.mark.asyncio
async def test_pipeline_initialization(pipeline):
    """Test that pipeline initializes correctly."""
    assert pipeline is not None
    assert pipeline.layer1_extractor is not None
    assert pipeline.layer2_extractor is not None
    assert pipeline.layer1_validator is not None
    assert pipeline.layer2_validator is not None
    assert pipeline.layer3_validator is not None
    assert pipeline.quality_scorer is not None
    
    # Check statistics initialization
    stats = pipeline.get_statistics()
    assert stats['total_processed'] == 0
    assert stats['total_successful'] == 0
    assert stats['total_failed'] == 0


@pytest.mark.asyncio
async def test_single_workflow_processing(pipeline):
    """Test processing a single workflow through complete pipeline."""
    workflow = TEST_WORKFLOWS[0]
    
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,  # Skip multimodal for speed
        include_transcripts=False  # Skip transcripts for speed
    )
    
    # Verify result structure
    assert isinstance(result, dict)
    assert 'success' in result
    assert 'workflow_id' in result
    assert 'url' in result
    assert 'layers' in result
    assert 'extraction_time' in result
    assert 'errors' in result
    
    # Verify workflow ID
    assert result['workflow_id'] == workflow['workflow_id']
    assert result['url'] == workflow['url']
    
    # Verify layers structure
    assert 'layer1' in result['layers']
    assert 'layer2' in result['layers']
    assert 'layer3' in result['layers']
    
    # Verify extraction time is reasonable (<45s with some buffer)
    assert 0 < result['extraction_time'] < 45
    
    # At least one layer should succeed
    layers_successful = sum([
        result['layers']['layer1'].get('success', False) if result['layers']['layer1'] else False,
        result['layers']['layer2'].get('success', False) if result['layers']['layer2'] else False,
        result['layers']['layer3'].get('success', False) if result['layers']['layer3'] else False
    ])
    assert layers_successful >= 1, f"At least one layer should succeed, got {layers_successful}"


@pytest.mark.asyncio
async def test_layer1_extraction(pipeline):
    """Test that Layer 1 metadata extraction works."""
    workflow = TEST_WORKFLOWS[0]
    
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,
        include_transcripts=False
    )
    
    layer1 = result['layers']['layer1']
    
    # Layer 1 should have standard fields
    assert layer1 is not None
    assert 'success' in layer1
    assert 'workflow_id' in layer1
    assert 'extraction_time' in layer1
    
    # If successful, should have data
    if layer1.get('success'):
        assert 'data' in layer1
        assert layer1['data'] is not None


@pytest.mark.asyncio
async def test_layer2_extraction(pipeline):
    """Test that Layer 2 JSON extraction works."""
    workflow = TEST_WORKFLOWS[0]
    
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,
        include_transcripts=False
    )
    
    layer2 = result['layers']['layer2']
    
    # Layer 2 should have standard fields
    assert layer2 is not None
    assert 'success' in layer2
    assert 'workflow_id' in layer2
    assert 'extraction_time' in layer2
    
    # If successful, should have data and node counts
    if layer2.get('success'):
        assert 'data' in layer2
        assert 'node_count' in layer2
        assert 'connection_count' in layer2
        assert layer2['node_count'] > 0, "Should have at least one node"


@pytest.mark.asyncio
async def test_layer3_extraction(pipeline):
    """Test that Layer 3 content extraction works."""
    workflow = TEST_WORKFLOWS[0]
    
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,
        include_transcripts=False
    )
    
    layer3 = result['layers']['layer3']
    
    # Layer 3 should have standard fields
    assert layer3 is not None
    assert 'success' in layer3
    assert 'extraction_time' in layer3
    
    # If successful, should have data
    if layer3.get('success'):
        assert 'data' in layer3
        assert layer3['data'] is not None


@pytest.mark.asyncio
async def test_validation_and_scoring(pipeline):
    """Test that validation and quality scoring works."""
    workflow = TEST_WORKFLOWS[0]
    
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,
        include_transcripts=False
    )
    
    # Should have validation results
    assert 'validation' in result
    assert 'quality' in result
    
    validation = result['validation']
    quality = result['quality']
    
    # Validation structure
    assert 'layer1' in validation
    assert 'layer2' in validation
    assert 'layer3' in validation
    
    # Quality score structure
    assert 'overall_score' in quality
    assert 'classification' in quality
    assert 'total_issues' in quality
    
    # Quality score should be 0-100
    assert 0 <= quality['overall_score'] <= 100


@pytest.mark.asyncio
async def test_pipeline_statistics(pipeline):
    """Test that pipeline tracks statistics correctly."""
    workflow = TEST_WORKFLOWS[0]
    
    # Get initial stats
    stats_before = pipeline.get_statistics()
    assert stats_before['total_processed'] == 0
    
    # Process workflow
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,
        include_transcripts=False
    )
    
    # Get updated stats
    stats_after = pipeline.get_statistics()
    
    # Statistics should be updated
    assert stats_after['total_processed'] == 1
    assert stats_after['total_successful'] + stats_after['total_failed'] == 1
    assert stats_after['total_time'] > 0
    assert stats_after['avg_time_per_workflow'] > 0


@pytest.mark.asyncio
async def test_batch_processing(pipeline):
    """Test batch processing of multiple workflows."""
    workflows = TEST_WORKFLOWS[:2]  # Test with 2 workflows
    
    result = await pipeline.process_batch(
        workflows,
        include_multimodal=False,
        include_transcripts=False,
        max_concurrent=2
    )
    
    # Verify batch result structure
    assert isinstance(result, dict)
    assert 'batch_success' in result
    assert 'total_workflows' in result
    assert 'successful' in result
    assert 'failed' in result
    assert 'success_rate' in result
    assert 'batch_time' in result
    assert 'results' in result
    
    # Verify counts
    assert result['total_workflows'] == len(workflows)
    assert result['successful'] + result['failed'] == len(workflows)
    assert len(result['results']) == len(workflows)
    
    # Verify success rate is reasonable
    assert 0 <= result['success_rate'] <= 100


@pytest.mark.asyncio
async def test_error_handling_invalid_workflow(pipeline):
    """Test that pipeline handles invalid workflows gracefully."""
    result = await pipeline.process_workflow(
        'invalid-id-99999',
        'https://n8n.io/workflows/99999',
        include_multimodal=False,
        include_transcripts=False
    )
    
    # Should complete without crashing
    assert isinstance(result, dict)
    assert 'success' in result
    assert 'errors' in result
    
    # Should have some errors
    assert len(result['errors']) > 0
    
    # Success should be False
    assert result['success'] == False


@pytest.mark.asyncio
async def test_performance_target(pipeline):
    """Test that pipeline meets performance target (<35s per workflow)."""
    workflow = TEST_WORKFLOWS[1]  # Use a simpler workflow
    
    result = await pipeline.process_workflow(
        workflow['workflow_id'],
        workflow['url'],
        include_multimodal=False,
        include_transcripts=False
    )
    
    # Should complete in under 35 seconds
    # Using 40s as buffer for CI/CD environments
    assert result['extraction_time'] < 40, \
        f"Pipeline took {result['extraction_time']:.2f}s, target is <35s"


@pytest.mark.asyncio
async def test_youtube_id_extraction(pipeline):
    """Test YouTube video ID extraction utility."""
    test_urls = [
        ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/embed/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://invalid-url.com', None)
    ]
    
    for url, expected_id in test_urls:
        video_id = pipeline._extract_youtube_id(url)
        assert video_id == expected_id, f"Failed to extract ID from {url}"


# Performance test with multiple workflows
@pytest.mark.asyncio
@pytest.mark.slow
async def test_batch_performance_10_workflows(pipeline):
    """
    Test batch processing performance with 10 workflows.
    
    This is a slow test, marked with @pytest.mark.slow
    """
    # Use first 3 test workflows repeated to make 10
    workflows = []
    for i in range(10):
        workflow = TEST_WORKFLOWS[i % len(TEST_WORKFLOWS)]
        workflows.append({
            'workflow_id': workflow['workflow_id'],
            'url': workflow['url']
        })
    
    result = await pipeline.process_batch(
        workflows,
        include_multimodal=False,
        include_transcripts=False,
        max_concurrent=3
    )
    
    # Should process all workflows
    assert result['total_workflows'] == 10
    
    # Average time should be under 35s
    assert result['avg_time_per_workflow'] < 40, \
        f"Average time {result['avg_time_per_workflow']:.2f}s exceeds target"
    
    # Success rate should be at least 70% (being conservative)
    assert result['success_rate'] >= 70, \
        f"Success rate {result['success_rate']:.1f}% below 70% threshold"

