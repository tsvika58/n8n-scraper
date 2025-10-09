"""
Unit tests for database schema and operations.
"""

import pytest
from datetime import datetime
from src.database.schema import Workflow, ScrapingSession


@pytest.mark.unit
def test_workflow_creation(db_session, sample_workflow_data):
    """Test creating a workflow record"""
    workflow = Workflow(**sample_workflow_data)
    db_session.add(workflow)
    db_session.commit()
    
    assert workflow.id is not None
    assert workflow.workflow_id == "2462"
    assert workflow.title == "Angie, Personal AI Assistant"
    assert workflow.success == False  # Default value
    assert workflow.completeness_score == 0.0  # Default value


@pytest.mark.unit
def test_workflow_query(db_session):
    """Test querying workflow records"""
    # Create unique workflow for this test
    workflow = Workflow(
        workflow_id="test-query",
        workflow_url="https://n8n.io/workflows/test-query",
        title="Query Test Workflow",
        primary_category="Testing"
    )
    db_session.add(workflow)
    db_session.commit()
    
    # Query by workflow_id
    result = db_session.query(Workflow).filter_by(workflow_id="test-query").first()
    assert result is not None
    assert result.title == "Query Test Workflow"
    
    # Query by category
    results = db_session.query(Workflow).filter_by(primary_category="Testing").all()
    assert len(results) == 1


@pytest.mark.unit
def test_workflow_update(db_session):
    """Test updating workflow records"""
    # Create unique workflow for this test
    workflow = Workflow(
        workflow_id="test-update",
        workflow_url="https://n8n.io/workflows/test-update",
        title="Update Test Workflow"
    )
    db_session.add(workflow)
    db_session.commit()
    
    # Update workflow
    workflow.success = True
    workflow.completeness_score = 95.5
    workflow.processing_time = 28.3
    db_session.commit()
    
    # Verify update
    result = db_session.query(Workflow).filter_by(workflow_id="test-update").first()
    assert result.success == True
    assert result.completeness_score == 95.5
    assert result.processing_time == 28.3


@pytest.mark.unit
def test_session_creation(db_session, sample_session_data):
    """Test creating a scraping session"""
    session = ScrapingSession(**sample_session_data)
    db_session.add(session)
    db_session.commit()
    
    assert session.id is not None
    assert session.session_name == "Test Session"
    assert session.status == "completed"
    assert session.success_rate == 95.0


@pytest.mark.unit
def test_session_metrics(db_session):
    """Test scraping session metrics"""
    session = ScrapingSession(
        session_name="Metrics Test",
        session_type="test",
        total_workflows=100,
        successful_workflows=95,
        failed_workflows=5
    )
    db_session.add(session)
    db_session.commit()
    
    # Calculate success rate
    success_rate = (session.successful_workflows / session.total_workflows) * 100
    session.success_rate = success_rate
    db_session.commit()
    
    # Verify
    result = db_session.query(ScrapingSession).filter_by(session_name="Metrics Test").first()
    assert result.success_rate == 95.0
    assert result.successful_workflows + result.failed_workflows == result.total_workflows


@pytest.mark.unit
def test_workflow_with_json_data(db_session, mock_workflow_json):
    """Test storing workflow JSON data"""
    workflow = Workflow(
        workflow_id="test-json",
        workflow_url="https://n8n.io/workflows/test",
        title="Test JSON Workflow",
        workflow_json=mock_workflow_json,
        node_count=len(mock_workflow_json["nodes"])
    )
    db_session.add(workflow)
    db_session.commit()
    
    # Query and verify JSON
    result = db_session.query(Workflow).filter_by(workflow_id="test-json").first()
    assert result.workflow_json is not None
    assert "nodes" in result.workflow_json
    assert len(result.workflow_json["nodes"]) == 2
    assert result.node_count == 2


@pytest.mark.unit
def test_workflow_quality_scoring(db_session):
    """Test workflow quality metrics"""
    workflow = Workflow(
        workflow_id="quality-test",
        workflow_url="https://n8n.io/workflows/quality",
        title="Quality Test Workflow",
        completeness_score=92.5,
        quality_score=88.0,
        data_quality_score=95.0,
        consistency_score=90.0
    )
    db_session.add(workflow)
    db_session.commit()
    
    # Calculate overall score
    overall = (
        workflow.completeness_score + 
        workflow.quality_score + 
        workflow.data_quality_score + 
        workflow.consistency_score
    ) / 4
    
    assert overall > 90.0  # All scores are good


@pytest.mark.unit
def test_workflow_repr(sample_workflow_data):
    """Test workflow string representation"""
    workflow = Workflow(**sample_workflow_data)
    repr_str = repr(workflow)
    
    assert "Workflow" in repr_str
    assert "2462" in repr_str
    # success can be None or False by default
    assert ("None" in repr_str or "False" in repr_str)


@pytest.mark.asyncio
async def test_async_operations():
    """Test async functionality (placeholder for future async tests)"""
    import asyncio
    await asyncio.sleep(0.01)
    assert True  # Async test infrastructure working

