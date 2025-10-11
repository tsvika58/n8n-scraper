"""
Unit tests for storage layer.

Tests SQLAlchemy models, repository CRUD operations,
and database session management.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

import pytest
from datetime import datetime

from src.storage.database import get_session, init_database, drop_all_tables
from src.storage.models import Workflow, WorkflowMetadata, WorkflowStructure
from src.storage.repository import WorkflowRepository


@pytest.fixture(scope="function")
def clean_database():
    """Provide a clean database for testing."""
    # Drop and recreate tables before each test
    drop_all_tables()
    init_database()
    yield
    # Clean up after test
    drop_all_tables()


@pytest.fixture
def sample_extraction_result():
    """Sample E2E pipeline extraction result."""
    return {
        'workflow_id': 'TEST-001',
        'url': 'https://n8n.io/workflows/TEST-001',
        'processing_time': 14.5,
        'quality_score': 85.3,
        'layers': {
            'layer1': {
                'success': True,
                'title': 'Test Workflow',
                'description': 'Test description',
                'author': {'name': 'Test Author', 'url': 'https://example.com'},
                'categories': ['Sales', 'Marketing'],
                'tags': ['email', 'automation'],
                'views': 100,
                'shares': 10
            },
            'layer2': {
                'success': True,
                'node_count': 5,
                'connection_count': 4,
                'node_types': ['start', 'httpRequest', 'set'],
                'extraction_type': 'full',
                'fallback_used': False,
                'data': {'nodes': [], 'connections': {}}
            },
            'layer3': {
                'success': True,
                'explainer_text': 'Test explainer',
                'setup_instructions': 'Test setup',
                'has_videos': True,
                'videos': [
                    {
                        'url': 'https://youtube.com/watch?v=test',
                        'video_id': 'test',
                        'platform': 'youtube',
                        'transcript': {
                            'text': 'Test transcript',
                            'duration': 300,
                            'language': 'en'
                        }
                    }
                ]
            }
        }
    }


class TestWorkflowModel:
    """Tests for Workflow model."""
    
    def test_create_workflow(self, clean_database):
        """Test creating a workflow."""
        with get_session() as session:
            workflow = Workflow(
                workflow_id='TEST-001',
                url='https://n8n.io/workflows/TEST-001',
                quality_score=85.5,
                layer1_success=True
            )
            
            session.add(workflow)
            session.commit()
            
            assert workflow.id is not None
            assert workflow.workflow_id == 'TEST-001'
            assert workflow.quality_score == 85.5
    
    def test_workflow_relationships(self, clean_database):
        """Test workflow relationships."""
        with get_session() as session:
            workflow = Workflow(workflow_id='TEST-002', url='https://example.com')
            metadata = WorkflowMetadata(workflow_id='TEST-002', title='Test')
            
            session.add(workflow)
            session.add(metadata)
            session.commit()
            
            # Refresh to load relationships
            session.refresh(workflow)
            
            assert workflow.workflow_metadata is not None
            assert workflow.workflow_metadata.title == 'Test'


class TestWorkflowRepository:
    """Tests for WorkflowRepository."""
    
    def test_create_workflow_complete(self, clean_database, sample_extraction_result):
        """Test creating a complete workflow with all data."""
        repo = WorkflowRepository()
        
        workflow = repo.create_workflow(
            workflow_id='TEST-001',
            url=sample_extraction_result['url'],
            extraction_result=sample_extraction_result
        )
        
        assert workflow.workflow_id == 'TEST-001'
        assert workflow.quality_score == 85.3
        assert workflow.layer1_success == True
        assert workflow.layer2_success == True
        assert workflow.layer3_success == True
    
    def test_get_workflow(self, clean_database, sample_extraction_result):
        """Test retrieving a workflow."""
        repo = WorkflowRepository()
        
        # Create workflow
        repo.create_workflow('TEST-002', sample_extraction_result['url'], sample_extraction_result)
        
        # Retrieve workflow
        workflow = repo.get_workflow('TEST-002')
        
        assert workflow is not None
        assert workflow.workflow_id == 'TEST-002'
        assert workflow.workflow_metadata.title == 'Test Workflow'
    
    def test_list_workflows_pagination(self, clean_database, sample_extraction_result):
        """Test paginated workflow listing."""
        repo = WorkflowRepository()
        
        # Create 5 workflows
        for i in range(5):
            result = sample_extraction_result.copy()
            result['workflow_id'] = f'TEST-{i:03d}'
            result['layers'] = sample_extraction_result['layers'].copy()
            repo.create_workflow(f'TEST-{i:03d}', result['url'], result)
        
        # List first 3
        workflows = repo.list_workflows(offset=0, limit=3)
        
        assert len(workflows) == 3
    
    def test_update_workflow(self, clean_database, sample_extraction_result):
        """Test updating workflow fields."""
        repo = WorkflowRepository()
        
        # Create workflow
        repo.create_workflow('TEST-003', sample_extraction_result['url'], sample_extraction_result)
        
        # Update workflow
        updated = repo.update_workflow('TEST-003', {'quality_score': 95.0})
        
        assert updated is not None
        assert updated.quality_score == 95.0
    
    def test_delete_workflow_cascade(self, clean_database, sample_extraction_result):
        """Test workflow deletion with cascade."""
        repo = WorkflowRepository()
        
        # Create workflow
        repo.create_workflow('TEST-004', sample_extraction_result['url'], sample_extraction_result)
        
        # Delete workflow
        deleted = repo.delete_workflow('TEST-004')
        
        assert deleted == True
        assert repo.get_workflow('TEST-004') is None
    
    def test_get_statistics(self, clean_database, sample_extraction_result):
        """Test statistics calculation."""
        repo = WorkflowRepository()
        
        # Create workflows
        for i in range(10):
            result = sample_extraction_result.copy()
            result['workflow_id'] = f'STAT-{i:03d}'
            result['layers'] = sample_extraction_result['layers'].copy()
            
            # Make some fail Layer 2 (60% success rate)
            if i >= 6:
                result['layers']['layer2']['success'] = False
            
            repo.create_workflow(f'STAT-{i:03d}', result['url'], result)
        
        # Get statistics
        stats = repo.get_statistics()
        
        assert stats['total_workflows'] == 10
        assert stats['layer1_success_rate'] == 100.0
        assert stats['layer2_success_rate'] == 60.0  # 6/10
        assert stats['layer3_success_rate'] == 100.0
    
    def test_list_with_filters(self, clean_database, sample_extraction_result):
        """Test filtering workflows."""
        repo = WorkflowRepository()
        
        # Create workflows with different success rates
        for i in range(5):
            result = sample_extraction_result.copy()
            result['workflow_id'] = f'FILTER-{i:03d}'
            result['quality_score'] = 50.0 + (i * 10)
            result['layers'] = sample_extraction_result['layers'].copy()
            
            repo.create_workflow(f'FILTER-{i:03d}', result['url'], result)
        
        # Filter by quality
        high_quality = repo.list_workflows(filters={'min_quality': 70.0})
        
        assert len(high_quality) == 3  # 70, 80, 90
    
    def test_search_workflows(self, clean_database, sample_extraction_result):
        """Test workflow search."""
        repo = WorkflowRepository()
        
        # Create workflows with different titles
        for i, title in enumerate(['Email Automation', 'Slack Integration', 'Email Notifications']):
            result = sample_extraction_result.copy()
            result['workflow_id'] = f'SEARCH-{i:03d}'
            result['layers'] = sample_extraction_result['layers'].copy()
            result['layers']['layer1']['title'] = title
            
            repo.create_workflow(f'SEARCH-{i:03d}', result['url'], result)
        
        # Search for 'email'
        results = repo.search_workflows('email')
        
        assert len(results) == 2  # Email Automation, Email Notifications


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
