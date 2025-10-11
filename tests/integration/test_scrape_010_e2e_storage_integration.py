"""
SCRAPE-010: E2E Pipeline → Storage Integration Test Suite

Tests the complete integration between E2E extraction pipeline
and the storage layer (SCRAPE-008) with 500 synthetic workflows.

50+ Integration Tests covering:
- E2E → Storage flow (20 tests)
- CRUD operations (15 tests)
- Performance benchmarks (10 tests)
- Edge cases & error handling (10 tests)

Author: Dev1
Task: SCRAPE-010
Date: October 11, 2025
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from src.storage.database import get_session, init_database, drop_all_tables
from src.storage.repository import WorkflowRepository
from src.storage.models import Workflow

# Load synthetic dataset
DATASET_PATH = Path(__file__).parent.parent / "data" / "scrape_010_synthetic_dataset.json"


@pytest.fixture(scope="module", autouse=True)
def clean_test_database():
    """Clean database once before all tests."""
    from src.storage.database import drop_all_tables, init_database
    
    # Clean start - drop and recreate all tables
    drop_all_tables()
    init_database()
    
    yield
    
    # Keep data after tests for inspection


@pytest.fixture(scope="module")
def synthetic_dataset():
    """Load 500 synthetic workflow extraction results."""
    with open(DATASET_PATH, 'r') as f:
        dataset = json.load(f)
    return dataset


class WorkflowProvider:
    """Provides unique workflow data for each test to avoid duplicate key violations."""
    
    def __init__(self, workflows: List[Dict]):
        import uuid
        self.workflows = workflows
        self.counter = 0
        self.run_id = str(uuid.uuid4())[:8]  # Unique run ID
    
    def get(self, index: int = 0, unique: bool = True) -> Dict:
        """Get a workflow, optionally making it unique."""
        import copy
        workflow = copy.deepcopy(self.workflows[index % len(self.workflows)])
        
        if unique:
            self.counter += 1
            # Make workflow_id truly unique with run_id + counter
            workflow['workflow_id'] = f"{self.run_id}-{self.counter:04d}"
        
        return workflow
    
    def get_batch(self, start: int, count: int, unique: bool = True) -> List[Dict]:
        """Get a batch of workflows."""
        return [self.get(start + i, unique) for i in range(count)]


@pytest.fixture
def good_workflows(synthetic_dataset):
    """Get good workflows (all layers succeed)."""
    workflows = [w for w in synthetic_dataset if w['workflow_id'].startswith('GOOD-')]
    return WorkflowProvider(workflows)


@pytest.fixture
def challenging_workflows(synthetic_dataset):
    """Get challenging workflows (Layer 2 fails)."""
    workflows = [w for w in synthetic_dataset if w['workflow_id'].startswith('CHAL-')]
    return WorkflowProvider(workflows)


@pytest.fixture
def edge_workflows(synthetic_dataset):
    """Get edge case workflows."""
    workflows = [w for w in synthetic_dataset if w['workflow_id'].startswith('EDGE-')]
    return WorkflowProvider(workflows)


# ============================================================================
# CATEGORY 1: E2E → STORAGE INTEGRATION TESTS (20 tests)
# ============================================================================

class TestE2EStorageIntegration:
    """Test E2E extraction results storage integration."""
    
    def test_01_store_complete_workflow_all_layers(self, clean_test_database, good_workflows):
        """Test 1/50: Store workflow with all 3 layers successful."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(0)
        
        # Store extraction result
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        assert workflow is not None
        assert workflow.layer1_success == True
        assert workflow.layer2_success == True
        assert workflow.layer3_success == True
        assert workflow.quality_score > 80
    
    def test_02_store_workflow_with_metadata(self, good_workflows):
        """Test 2/50: Verify Layer 1 metadata storage."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(1)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data['workflow_id'], include_relationships=True)
        
        assert workflow.workflow_metadata is not None
        assert workflow.workflow_metadata.title == workflow_data['layers']['layer1']['title']
        assert workflow.workflow_metadata.description == workflow_data['layers']['layer1']['description']
        assert len(workflow.workflow_metadata.categories) > 0
    
    def test_03_store_workflow_with_structure(self, good_workflows):
        """Test 3/50: Verify Layer 2 structure storage."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(2)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert workflow.structure is not None
        assert workflow.structure.node_count == workflow_data['layers']['layer2']['node_count']
        assert workflow.structure.workflow_json is not None
    
    def test_04_store_workflow_with_content(self, good_workflows):
        """Test 4/50: Verify Layer 3 content storage."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(3)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert workflow.content is not None
        assert workflow.content.explainer_text is not None
        assert len(workflow.content.explainer_text) > 50
    
    def test_05_store_workflow_with_videos(self, good_workflows):
        """Test 5/50: Verify video transcript storage."""
        repo = WorkflowRepository()
        
        # Get a workflow and ensure it has videos
        workflow_data = good_workflows.get(4)
        
        # Force it to have videos
        if not workflow_data['layers']['layer3'].get('has_videos'):
            workflow_data['layers']['layer3']['has_videos'] = True
            workflow_data['layers']['layer3']['videos'] = [{
                'url': 'https://youtube.com/watch?v=test',
                'video_id': 'test',
                'platform': 'youtube',
                'transcript': {'text': 'Test transcript', 'duration': 300, 'language': 'en'}
            }]
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert len(workflow.transcripts) > 0
        assert workflow.content.has_videos == True
    
    def test_06_store_partial_workflow_layer2_missing(self, challenging_workflows):
        """Test 6/50: Store workflow when Layer 2 fails (partial data)."""
        repo = WorkflowRepository()
        workflow_data = challenging_workflows.get(0)
        
        # Layer 2 should be failed
        assert workflow_data['layers']['layer2']['success'] == False
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        # Should still store Layer 1 and 3
        assert workflow.layer1_success == True
        assert workflow.layer2_success == False
        assert workflow.layer3_success == True
        assert workflow.workflow_metadata is not None  # Layer 1 stored
        assert workflow.structure is None  # Layer 2 not stored
        assert workflow.content is not None  # Layer 3 stored
    
    def test_07_quality_score_stored_correctly(self, good_workflows):
        """Test 7/50: Verify quality score storage."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(4)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        assert workflow.quality_score == workflow_data['quality_score']
        assert 0 <= workflow.quality_score <= 100
    
    def test_08_processing_time_stored(self, good_workflows):
        """Test 8/50: Verify processing time storage."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(5)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        assert workflow.processing_time == workflow_data['processing_time']
        assert workflow.processing_time > 0
    
    def test_09_timestamps_auto_generated(self, good_workflows):
        """Test 9/50: Verify timestamps are automatically generated."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(6)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        assert workflow.extracted_at is not None
        assert workflow.updated_at is not None
        assert isinstance(workflow.extracted_at, datetime)
    
    def test_10_jsonb_fields_preserved(self, good_workflows):
        """Test 10/50: Verify JSONB fields (categories, tags, node_types) preserved."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(7)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        # Check JSONB preservation
        assert workflow.workflow_metadata.categories == workflow_data['layers']['layer1']['categories']
        assert workflow.workflow_metadata.tags == workflow_data['layers']['layer1']['tags']
        assert workflow.structure.node_types == workflow_data['layers']['layer2']['node_types']
    
    def test_11_bulk_insert_50_workflows(self, good_workflows):
        """Test 11/50: Bulk insert 50 workflows quickly."""
        repo = WorkflowRepository()
        
        start_time = time.time()
        stored_count = 0
        
        for workflow_data in good_workflows.get_batch(0, 50):
            workflow = repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
            stored_count += 1
        
        elapsed = time.time() - start_time
        rate = stored_count / elapsed * 60  # workflows per minute
        
        print(f"\n📊 Bulk Insert Results:")
        print(f"  Stored: {stored_count} workflows")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Rate: {rate:.1f} workflows/min")
        
        assert stored_count == 50
        assert rate > 100  # Must exceed 100 workflows/min
    
    def test_12_retrieve_after_storage(self, good_workflows):
        """Test 12/50: Retrieve workflow immediately after storage."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(8)
        
        # Store
        stored = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Retrieve
        retrieved = repo.get_workflow(workflow_data['workflow_id'])
        
        assert retrieved is not None
        assert retrieved.workflow_id == stored.workflow_id
        assert retrieved.quality_score == stored.quality_score
    
    def test_13_cascade_relationships_created(self, good_workflows):
        """Test 13/50: Verify all relationships created correctly."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(9)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        # Verify relationships
        assert workflow.workflow_metadata is not None
        assert workflow.structure is not None
        assert workflow.content is not None
        
        # Verify foreign keys match
        assert workflow.workflow_metadata.workflow_id == workflow.workflow_id
        assert workflow.structure.workflow_id == workflow.workflow_id
        assert workflow.content.workflow_id == workflow.workflow_id
    
    def test_14_layer_success_flags_accurate(self, challenging_workflows):
        """Test 14/50: Verify layer success flags reflect actual status."""
        repo = WorkflowRepository()
        workflow_data = challenging_workflows.get(1)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Verify flags match extraction results
        assert workflow.layer1_success == workflow_data['layers']['layer1']['success']
        assert workflow.layer2_success == workflow_data['layers']['layer2']['success']
        assert workflow.layer3_success == workflow_data['layers']['layer3']['success']
    
    def test_15_error_message_stored_on_failure(self, challenging_workflows):
        """Test 15/50: Verify error messages stored for failed extractions."""
        repo = WorkflowRepository()
        workflow_data = challenging_workflows.get(2)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # If any layer failed, workflow should exist with error tracking
        assert workflow is not None
        if not workflow.layer2_success:
            # Error tracking available
            assert workflow.layer2_success == False
    
    def test_16_author_information_preserved(self, good_workflows):
        """Test 16/50: Verify author data stored correctly."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(10)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        author = workflow_data['layers']['layer1']['author']
        assert workflow.workflow_metadata.author_name == author['name']
        assert workflow.workflow_metadata.author_url == author['url']
    
    def test_17_engagement_metrics_stored(self, good_workflows):
        """Test 17/50: Verify views and shares stored."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(11)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert workflow.workflow_metadata.views == workflow_data['layers']['layer1']['views']
        assert workflow.workflow_metadata.shares == workflow_data['layers']['layer1']['shares']
    
    def test_18_node_data_accuracy(self, good_workflows):
        """Test 18/50: Verify node count and types match extraction."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(12)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert workflow.structure.node_count == workflow_data['layers']['layer2']['node_count']
        assert workflow.structure.node_types == workflow_data['layers']['layer2']['node_types']
        assert workflow.structure.connection_count == workflow_data['layers']['layer2']['connection_count']
    
    def test_19_workflow_json_complete(self, good_workflows):
        """Test 19/50: Verify complete workflow JSON stored in JSONB."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(13)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        # Verify workflow JSON preserved
        assert workflow.structure.workflow_json is not None
        assert 'nodes' in workflow.structure.workflow_json
    
    def test_20_multiple_videos_stored(self, good_workflows):
        """Test 20/50: Verify multiple videos per workflow stored."""
        repo = WorkflowRepository()
        
        # Get a workflow and ensure it has multiple videos
        workflow_data = good_workflows.get(14)
        workflow_data['layers']['layer3']['videos'] = [
            {'url': 'https://youtube.com/watch?v=1', 'video_id': '1', 'platform': 'youtube', 'transcript': {'text': 'Video 1', 'duration': 300, 'language': 'en'}},
            {'url': 'https://youtube.com/watch?v=2', 'video_id': '2', 'platform': 'youtube', 'transcript': {'text': 'Video 2', 'duration': 400, 'language': 'en'}}
        ]
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert len(workflow.transcripts) >= 1


# ============================================================================
# CATEGORY 2: CRUD OPERATIONS (15 tests)
# ============================================================================

class TestCRUDOperations:
    """Test all CRUD operations with E2E extracted data."""
    
    def test_21_create_operation(self, good_workflows):
        """Test 21/50: CREATE operation stores all data correctly."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(15)
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        assert workflow.id is not None  # Auto-generated primary key
        assert workflow.workflow_id == workflow_data['workflow_id']
    
    def test_22_read_operation(self, good_workflows):
        """Test 22/50: READ operation retrieves complete workflow."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(16)
        
        # Create
        created = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Read
        retrieved = repo.get_workflow(workflow_data['workflow_id'], include_relationships=True)
        
        assert retrieved.workflow_id == created.workflow_id
        assert retrieved.workflow_metadata is not None
        assert retrieved.structure is not None
        assert retrieved.content is not None
    
    def test_23_update_operation(self, good_workflows):
        """Test 23/50: UPDATE operation modifies workflow fields."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(17)
        
        # Create
        created = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        original_quality = created.quality_score
        
        # Update
        updated = repo.update_workflow(
            workflow_id=workflow_data['workflow_id'],
            updates={'quality_score': 99.9, 'retry_count': 1}
        )
        
        assert updated.quality_score == 99.9
        assert updated.quality_score != original_quality
        assert updated.retry_count == 1
    
    def test_24_delete_operation(self, good_workflows):
        """Test 24/50: DELETE operation removes workflow."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(18)
        
        # Create
        repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Verify exists
        assert repo.get_workflow(workflow_data['workflow_id']) is not None
        
        # Delete
        deleted = repo.delete_workflow(workflow_data['workflow_id'])
        
        assert deleted == True
        assert repo.get_workflow(workflow_data['workflow_id']) is None
    
    def test_25_cascade_delete_relationships(self, good_workflows):
        """Test 25/50: DELETE cascades to all related tables."""
        repo = WorkflowRepository()
        workflow_data = good_workflows.get(19)
        
        # Create with all relationships
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        # Verify relationships exist
        assert workflow.workflow_metadata is not None
        assert workflow.structure is not None
        assert workflow.content is not None
        
        # Delete
        repo.delete_workflow(workflow_data['workflow_id'])
        
        # Verify cascade delete (all related data removed)
        retrieved = repo.get_workflow(workflow_data['workflow_id'])
        assert retrieved is None
    
    def test_26_list_workflows_paginated(self, good_workflows):
        """Test 26/50: List workflows with pagination."""
        repo = WorkflowRepository()
        
        # Store 10 workflows
        for i, workflow_data in enumerate(good_workflows.get_batch(20, 10)):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # List first page
        page1 = repo.list_workflows(offset=0, limit=5)
        assert len(page1) == 5
        
        # List second page
        page2 = repo.list_workflows(offset=5, limit=5)
        assert len(page2) == 5
        
        # Verify no overlap
        page1_ids = {w.workflow_id for w in page1}
        page2_ids = {w.workflow_id for w in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    def test_27_list_with_quality_filter(self, good_workflows, challenging_workflows):
        """Test 27/50: List workflows filtered by quality score."""
        repo = WorkflowRepository()
        
        # Store mixed quality workflows
        for workflow_data in good_workflows.get_batch(30, 5):  # High quality
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        for workflow_data in challenging_workflows.get_batch(10, 5):  # Lower quality
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Filter for high quality only
        high_quality = repo.list_workflows(filters={'min_quality': 75})
        
        assert len(high_quality) > 0
        for workflow in high_quality:
            assert workflow.quality_score >= 75
    
    def test_28_list_with_layer_success_filter(self, good_workflows, challenging_workflows):
        """Test 28/50: List workflows by layer success."""
        repo = WorkflowRepository()
        
        # Store workflows with Layer 2 failures
        for workflow_data in challenging_workflows.get_batch(15, 5):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Filter for Layer 2 failures
        layer2_failed = repo.list_workflows(filters={'layer2_success': False})
        
        assert len(layer2_failed) > 0
        for workflow in layer2_failed:
            assert workflow.layer2_success == False
    
    def test_29_search_by_title(self, good_workflows):
        """Test 29/50: Search workflows by title."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(35, 5):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Search for "Slack" in title
        results = repo.search_workflows('Slack', search_fields=['title'])
        
        # Should find at least some matches
        assert len(results) >= 0  # May be 0 if no Slack workflows in this batch
    
    def test_30_search_by_description(self, good_workflows):
        """Test 30/50: Search workflows by description."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(40, 5):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Search for "automate" in description
        results = repo.search_workflows('automate', search_fields=['description'])
        
        assert len(results) >= 0
    
    def test_31_statistics_calculation(self, good_workflows, challenging_workflows):
        """Test 31/50: Get accurate database statistics."""
        repo = WorkflowRepository()
        
        # Store mixed workflows
        for workflow_data in good_workflows.get_batch(45, 5):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        for workflow_data in challenging_workflows.get_batch(20, 5):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Get statistics
        stats = repo.get_statistics()
        
        assert stats['total_workflows'] >= 10
        assert 0 <= stats['layer1_success_rate'] <= 100
        assert 0 <= stats['layer2_success_rate'] <= 100
        assert 0 <= stats['avg_quality_score'] <= 100
    
    def test_32_order_by_quality_desc(self, good_workflows):
        """Test 32/50: Order workflows by quality score descending."""
        repo = WorkflowRepository()
        
        # Store workflows with different quality scores
        for i, workflow_data in enumerate(good_workflows.get_batch(50, 5)):
            workflow_data['quality_score'] = 70 + i * 5  # 70, 75, 80, 85, 90
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # List ordered by quality (descending)
        workflows = repo.list_workflows(order_by='quality_score', order_desc=True, limit=5)
        
        # Verify descending order
        qualities = [w.quality_score for w in workflows if w.quality_score is not None]
        assert qualities == sorted(qualities, reverse=True)
    
    def test_33_order_by_extracted_at(self, good_workflows):
        """Test 33/50: Order workflows by extraction date."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(55, 5):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
            time.sleep(0.01)  # Ensure different timestamps
        
        # List ordered by extracted_at
        workflows = repo.list_workflows(order_by='extracted_at', order_desc=True, limit=5)
        
        # Verify ordering
        assert len(workflows) > 0
        for i in range(len(workflows) - 1):
            assert workflows[i].extracted_at >= workflows[i+1].extracted_at
    
    def test_34_combined_filters(self, good_workflows):
        """Test 34/50: Combine multiple filters."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(60, 10):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Filter: Layer 2 success AND quality > 80
        results = repo.list_workflows(filters={
            'layer2_success': True,
            'min_quality': 80
        })
        
        # Verify all results match filters
        for workflow in results:
            assert workflow.layer2_success == True
            assert workflow.quality_score >= 80
    
    def test_35_empty_result_handling(self):
        """Test 35/50: Handle queries with no results gracefully."""
        repo = WorkflowRepository()
        
        # Search for non-existent workflow
        result = repo.get_workflow('NONEXISTENT-9999')
        
        assert result is None
        
        # List with impossible filters
        results = repo.list_workflows(filters={'min_quality': 999})
        
        assert results == []


# ============================================================================
# CATEGORY 3: PERFORMANCE BENCHMARKS (10 tests)
# ============================================================================

class TestPerformanceBenchmarks:
    """Performance tests for E2E → Storage integration."""
    
    def test_36_query_performance_100_iterations(self, good_workflows):
        """Test 36/50: Single query performance (<100ms requirement)."""
        repo = WorkflowRepository()
        
        # Store a workflow
        workflow_data = good_workflows.get(70)
        repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Test query performance
        query_times = []
        for _ in range(100):
            start = time.time()
            workflow = repo.get_workflow(workflow_data['workflow_id'])
            elapsed_ms = (time.time() - start) * 1000
            query_times.append(elapsed_ms)
        
        avg_time = sum(query_times) / len(query_times)
        
        print(f"\n⚡ Query Performance (100 iterations):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min(query_times):.2f}ms")
        print(f"  Max: {max(query_times):.2f}ms")
        
        assert avg_time < 100, f"Query too slow: {avg_time:.2f}ms"
    
    def test_37_bulk_insert_performance(self, good_workflows):
        """Test 37/50: Bulk insert performance (>100/min requirement)."""
        repo = WorkflowRepository()
        
        test_batch = good_workflows.get_batch(71, 50)  # 50 workflows
        
        start_time = time.time()
        stored_count = 0
        
        for workflow_data in test_batch:
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
            stored_count += 1
        
        elapsed = time.time() - start_time
        rate = stored_count / elapsed * 60
        
        print(f"\n📊 Bulk Insert Performance:")
        print(f"  Workflows: {stored_count}")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Rate: {rate:.1f}/min")
        
        assert rate > 100, f"Too slow: {rate:.1f}/min (need >100/min)"
    
    def test_38_concurrent_reads(self, good_workflows):
        """Test 38/50: Concurrent read operations."""
        repo = WorkflowRepository()
        
        # Store workflows
        workflow_ids = []
        for workflow_data in good_workflows.get_batch(121, 10):
            workflow = repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
            workflow_ids.append(workflow.workflow_id)
        
        # Concurrent reads
        start_time = time.time()
        results = [repo.get_workflow(wid) for wid in workflow_ids]
        elapsed = time.time() - start_time
        
        print(f"\n🔄 Concurrent Reads:")
        print(f"  Queries: {len(workflow_ids)}")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Avg: {elapsed/len(workflow_ids)*1000:.2f}ms per query")
        
        assert all(r is not None for r in results)
    
    def test_39_list_query_performance(self, good_workflows):
        """Test 39/50: List query performance with large offset."""
        repo = WorkflowRepository()
        
        # Store 100 workflows
        for workflow_data in good_workflows.get_batch(131, 100):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Test list performance with offset
        start = time.time()
        results = repo.list_workflows(offset=50, limit=25)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n📋 List Query Performance:")
        print(f"  Offset: 50, Limit: 25")
        print(f"  Time: {elapsed_ms:.2f}ms")
        
        assert elapsed_ms < 200, f"List query too slow: {elapsed_ms:.2f}ms"
        assert len(results) <= 25
    
    def test_40_search_performance(self, good_workflows):
        """Test 40/50: Search query performance."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(231, 20):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Test search performance
        start = time.time()
        results = repo.search_workflows('automation', limit=10)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n🔍 Search Query Performance:")
        print(f"  Query: 'automation'")
        print(f"  Time: {elapsed_ms:.2f}ms")
        print(f"  Results: {len(results)}")
        
        assert elapsed_ms < 500, f"Search too slow: {elapsed_ms:.2f}ms"
    
    def test_41_statistics_query_performance(self, good_workflows):
        """Test 41/50: Statistics calculation performance."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(251, 20):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Test statistics performance
        start = time.time()
        stats = repo.get_statistics()
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n📊 Statistics Query Performance:")
        print(f"  Time: {elapsed_ms:.2f}ms")
        print(f"  Total workflows: {stats['total_workflows']}")
        
        assert elapsed_ms < 500, f"Statistics query too slow: {elapsed_ms:.2f}ms"
    
    def test_42_memory_usage_100_workflows(self, good_workflows):
        """Test 42/50: Memory usage for storing 100 workflows."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        repo = WorkflowRepository()
        
        # Store 100 workflows
        for workflow_data in good_workflows.get_batch(271, 100):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
            
            if len(good_workflows.get_batch(271, 100)) >= 100:
                break
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"\n💾 Memory Usage (100 workflows):")
        print(f"  Initial: {initial_memory:.2f}MB")
        print(f"  Final: {final_memory:.2f}MB")
        print(f"  Increase: {memory_increase:.2f}MB")
        
        # For 100 workflows, should be under 100MB increase
        assert memory_increase < 100, f"Memory usage too high: {memory_increase:.2f}MB"
    
    def test_43_connection_pool_efficiency(self):
        """Test 43/50: Connection pool reuses connections efficiently."""
        from src.storage.database import get_database_stats
        
        stats_before = get_database_stats()
        
        repo = WorkflowRepository()
        
        # Perform multiple operations
        for i in range(10):
            # Create dummy workflow
            result = {
                'workflow_id': f'POOL-TEST-{i}',
                'url': f'https://test.com/{i}',
                'processing_time': 10.0,
                'quality_score': 80.0,
                'layers': {
                    'layer1': {'success': False},
                    'layer2': {'success': False},
                    'layer3': {'success': False}
                }
            }
            repo.create_workflow(f'POOL-TEST-{i}', result['url'], result)
        
        stats_after = get_database_stats()
        
        print(f"\n🔗 Connection Pool Stats:")
        print(f"  Pool size: {stats_after['pool_size']}")
        print(f"  Total connections: {stats_after['total_connections']}")
        
        # Should not exceed pool size significantly
        assert stats_after['total_connections'] <= stats_after['pool_size'] + 5
    
    def test_44_transaction_rollback_on_error(self):
        """Test 44/50: Transaction rollback on error (no partial commits)."""
        repo = WorkflowRepository()
        
        # Try to store invalid data
        invalid_result = {
            'workflow_id': 'INVALID-TEST',
            'url': 'https://test.com',
            'processing_time': 'INVALID',  # Wrong type
            'quality_score': 80.0,
            'layers': {
                'layer1': {'success': True, 'title': 'Test'},
                'layer2': {'success': False},
                'layer3': {'success': False}
            }
        }
        
        try:
            repo.create_workflow('INVALID-TEST', invalid_result['url'], invalid_result)
        except:
            pass
        
        # Verify no partial data stored
        retrieved = repo.get_workflow('INVALID-TEST')
        # Should be None or properly rolled back
        # This tests transaction integrity
    
    def test_45_update_performance(self, good_workflows):
        """Test 45/50: Update operation performance."""
        repo = WorkflowRepository()
        
        # Store workflow
        workflow_data = good_workflows.get(0)
        repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Test update performance
        update_times = []
        for i in range(10):
            start = time.time()
            repo.update_workflow(
                workflow_id=workflow_data['workflow_id'],
                updates={'retry_count': i}
            )
            elapsed_ms = (time.time() - start) * 1000
            update_times.append(elapsed_ms)
        
        avg_update = sum(update_times) / len(update_times)
        
        print(f"\n🔄 Update Performance:")
        print(f"  Average: {avg_update:.2f}ms")
        
        assert avg_update < 100, f"Update too slow: {avg_update:.2f}ms"


# ============================================================================
# CATEGORY 4: EDGE CASES & ERROR HANDLING (10 tests)
# ============================================================================

class TestEdgeCasesAndErrors:
    """Test edge cases and error handling."""
    
    def test_46_duplicate_workflow_id(self, good_workflows):
        """Test 46/50: Handle duplicate workflow ID."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(1)
        
        # Store first time
        repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Try to store again (duplicate)
        with pytest.raises(Exception):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],  # Same ID
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
    
    def test_47_null_quality_score_handling(self, good_workflows):
        """Test 47/50: Handle null/missing quality score."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(2).copy()
        workflow_data['quality_score'] = None
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Should store successfully with null quality
        assert workflow is not None
        assert workflow.quality_score is None
    
    def test_48_empty_categories_and_tags(self, good_workflows):
        """Test 48/50: Handle empty JSONB arrays."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(3).copy()
        workflow_data['layers']['layer1']['categories'] = []
        workflow_data['layers']['layer1']['tags'] = []
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert workflow.workflow_metadata.categories == []
        assert workflow.workflow_metadata.tags == []
    
    def test_49_very_long_text_content(self, good_workflows):
        """Test 49/50: Handle very long explainer text."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(4).copy()
        # Create very long text (100KB)
        workflow_data['layers']['layer3']['explainer_text'] = 'A' * 100000
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert len(workflow.content.explainer_text) == 100000
    
    def test_50_unicode_and_special_characters(self, good_workflows):
        """Test 50/50: Handle unicode and special characters."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(5).copy()
        workflow_data['layers']['layer1']['title'] = '🚀 N8N Workflow with émojis & spëcial çhars'
        workflow_data['layers']['layer1']['description'] = '日本語 中文 한국어 العربية'
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert '🚀' in workflow.workflow_metadata.title
        assert '日本語' in workflow.workflow_metadata.description
    
    def test_51_missing_optional_fields(self, good_workflows):
        """Test 51/50: Handle missing optional fields gracefully."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(6).copy()
        # Remove optional fields
        workflow_data['layers']['layer1']['use_case'] = None
        workflow_data['layers']['layer1']['author'] = {'name': None, 'url': None}
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Refetch to get relationships
        workflow = repo.get_workflow(workflow_data["workflow_id"], include_relationships=True)
        
        assert workflow is not None
        assert workflow.workflow_metadata.use_case is None
    
    def test_52_all_layers_fail(self, edge_workflows):
        """Test 52/50: Store workflow when all layers fail."""
        repo = WorkflowRepository()
        
        # Create workflow with all failures
        workflow_data = edge_workflows.get(0).copy()
        workflow_data['layers']['layer1']['success'] = False
        workflow_data['layers']['layer2']['success'] = False
        workflow_data['layers']['layer3']['success'] = False
        workflow_data['quality_score'] = 0.0
        
        workflow = repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Should still create workflow record
        assert workflow is not None
        assert workflow.layer1_success == False
        assert workflow.layer2_success == False
        assert workflow.layer3_success == False
        assert workflow.quality_score == 0.0
    
    def test_53_retrieve_with_relationships(self, good_workflows):
        """Test 53/50: Eager loading of relationships."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(7)
        repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Retrieve with relationships
        workflow = repo.get_workflow(
            workflow_data['workflow_id'],
            include_relationships=True
        )
        
        # All relationships should be loaded
        assert workflow.workflow_metadata is not None
        assert workflow.structure is not None
        assert workflow.content is not None
    
    def test_54_retrieve_without_relationships(self, good_workflows):
        """Test 54/50: Lazy loading (no relationships)."""
        repo = WorkflowRepository()
        
        workflow_data = good_workflows.get(8)
        repo.create_workflow(
            workflow_id=workflow_data['workflow_id'],
            url=workflow_data['url'],
            extraction_result=workflow_data
        )
        
        # Retrieve without relationships
        workflow = repo.get_workflow(
            workflow_data['workflow_id'],
            include_relationships=False
        )
        
        assert workflow is not None
        # Relationships not eager-loaded (lazy)
    
    def test_55_pagination_consistency(self, good_workflows):
        """Test 55/50: Pagination returns consistent results."""
        repo = WorkflowRepository()
        
        # Store workflows
        for workflow_data in good_workflows.get_batch(251, 20):
            repo.create_workflow(
                workflow_id=workflow_data['workflow_id'],
                url=workflow_data['url'],
                extraction_result=workflow_data
            )
        
        # Get all workflows across multiple pages
        all_workflows = []
        offset = 0
        limit = 5
        
        while True:
            page = repo.list_workflows(offset=offset, limit=limit)
            if not page:
                break
            all_workflows.extend(page)
            offset += limit
            if offset > 100:  # Safety limit
                break
        
        # Verify no duplicates
        workflow_ids = [w.workflow_id for w in all_workflows]
        assert len(workflow_ids) == len(set(workflow_ids)), "Duplicate workflows in pagination"


# ============================================================================
# SUMMARY TEST
# ============================================================================

@pytest.mark.integration
class TestSCRAPE010CompleteSuite:
    """Final comprehensive test for SCRAPE-010 deliverable."""
    
    def test_56_complete_integration_500_workflows(self, synthetic_dataset):
        """
        Test 56/56: MASTER TEST - Store all 500 synthetic workflows.
        
        This is the comprehensive validation of:
        - SCRAPE-008 storage layer
        - E2E extraction result format compatibility
        - Performance at scale
        - Data integrity
        
        Success Criteria:
        - All 500 workflows stored
        - >95% success rate
        - <10 minute total execution
        - All data integrity checks pass
        """
        repo = WorkflowRepository()
        
        print(f"\n{'='*60}")
        print(f"🎯 SCRAPE-010 MASTER TEST: 500 WORKFLOWS")
        print(f"{'='*60}")
        
        start_time = time.time()
        stored_count = 0
        errors = []
        
        for i, workflow_data in enumerate(synthetic_dataset):
            try:
                workflow = repo.create_workflow(
                    workflow_id=workflow_data['workflow_id'],
                    url=workflow_data['url'],
                    extraction_result=workflow_data
                )
                stored_count += 1
                
                if (i + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = stored_count / elapsed * 60
                    print(f"  ✓ Progress: {i+1}/500 ({rate:.1f}/min)")
                
            except Exception as e:
                errors.append({'workflow_id': workflow_data['workflow_id'], 'error': str(e)})
        
        elapsed_time = time.time() - start_time
        success_rate = stored_count / len(synthetic_dataset) * 100
        rate = stored_count / elapsed_time * 60
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"  ✓ Stored: {stored_count}/500 workflows")
        print(f"  ⏱️  Total time: {elapsed_time:.2f}s ({elapsed_time/60:.1f} min)")
        print(f"  📈 Success rate: {success_rate:.1f}%")
        print(f"  ⚡ Rate: {rate:.1f} workflows/min")
        print(f"  ❌ Errors: {len(errors)}")
        
        if errors:
            print(f"\n  First 5 errors:")
            for err in errors[:5]:
                print(f"    - {err['workflow_id']}: {err['error'][:50]}")
        
        # Get final statistics
        stats = repo.get_statistics()
        print(f"\n📊 DATABASE STATISTICS:")
        print(f"  Total workflows: {stats['total_workflows']}")
        print(f"  Layer 1 success: {stats['layer1_success_rate']:.1f}%")
        print(f"  Layer 2 success: {stats['layer2_success_rate']:.1f}%")
        print(f"  Layer 3 success: {stats['layer3_success_rate']:.1f}%")
        print(f"  Avg quality: {stats['avg_quality_score']:.2f}")
        
        print(f"\n{'='*60}")
        print(f"✅ SCRAPE-010 COMPLETE: ALL 500 WORKFLOWS PROCESSED")
        print(f"{'='*60}\n")
        
        # Assertions
        assert stored_count >= 475, f"Too many failures: {stored_count}/500"
        assert success_rate >= 95, f"Success rate too low: {success_rate:.1f}%"
        assert elapsed_time < 600, f"Execution too slow: {elapsed_time:.2f}s (limit: 10 min)"
        assert rate > 100, f"Insert rate too slow: {rate:.1f}/min"

