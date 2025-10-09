"""
Pytest configuration and fixtures for N8N Workflow Scraper tests.
"""

import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.schema import Base, Workflow, ScrapingSession


@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory test database engine"""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_db_engine):
    """Get fresh database session for each test"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()  # Rollback to keep tests isolated
    session.close()


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing"""
    return {
        "workflow_id": "2462",
        "workflow_url": "https://n8n.io/workflows/2462",
        "title": "Angie, Personal AI Assistant",
        "author": "John Doe",
        "primary_category": "Automation",
        "secondary_categories": ["AI", "Productivity"],
        "node_tags": ["OpenAI", "Telegram", "Webhook"],
        "general_tags": ["ai", "assistant", "personal"],
        "description": "AI-powered personal assistant for daily tasks",
        "use_case": "Automate personal productivity tasks",
        "difficulty_level": "intermediate",
        "views": 1250,
        "upvotes": 45,
        "node_count": 5,
        "node_types": ["webhook", "openai", "telegram"],
        "trigger_type": "webhook",
        "execution_mode": "automatic"
    }


@pytest.fixture
def sample_session_data():
    """Sample scraping session data for testing"""
    return {
        "session_name": "Test Session",
        "session_type": "test",
        "total_workflows": 100,
        "successful_workflows": 95,
        "failed_workflows": 5,
        "success_rate": 95.0,
        "average_time": 28.5,
        "status": "completed"
    }


@pytest.fixture
def mock_workflow_json():
    """Mock n8n workflow JSON"""
    return {
        "name": "Angie Personal AI Assistant",
        "nodes": [
            {
                "id": "webhook-1",
                "type": "n8n-nodes-base.webhook",
                "name": "Webhook Trigger",
                "position": [100, 200],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "angie-webhook"
                }
            },
            {
                "id": "openai-1",
                "type": "n8n-nodes-base.openai",
                "name": "OpenAI",
                "position": [300, 200],
                "parameters": {
                    "model": "gpt-3.5-turbo"
                }
            }
        ],
        "connections": {
            "webhook-1": {
                "main": [[{"node": "openai-1", "type": "main", "index": 0}]]
            }
        }
    }


@pytest.fixture
def mock_layer1_data():
    """Mock Layer 1 (page metadata) extraction result"""
    return {
        "success": True,
        "workflow_id": "2462",
        "data": {
            "title": "Angie, Personal AI Assistant",
            "author": "John Doe",
            "primary_category": "Automation",
            "secondary_categories": ["AI", "Productivity"],
            "node_tags": ["OpenAI", "Telegram"],
            "description": "AI assistant for personal tasks",
            "views": 1250,
            "upvotes": 45
        },
        "extraction_time": 3.2
    }


@pytest.fixture
def mock_layer2_data():
    """Mock Layer 2 (workflow JSON) extraction result"""
    return {
        "success": True,
        "workflow_id": "2462",
        "data": {
            "workflow_json": {
                "name": "Angie Assistant",
                "nodes": [{"id": "1", "type": "webhook"}],
                "connections": {}
            },
            "node_count": 1,
            "node_types": ["webhook"]
        },
        "extraction_time": 4.5
    }


@pytest.fixture
def mock_layer3_data():
    """Mock Layer 3 (explainer content) extraction result"""
    return {
        "success": True,
        "workflow_id": "2462",
        "data": {
            "introduction": "This workflow creates a personal AI assistant...",
            "tutorial_text": "Complete tutorial content here...",
            "tutorial_sections": [
                {"title": "Setup", "content": "First, configure..."}
            ],
            "image_urls": ["https://n8n.io/images/setup.png"],
            "video_urls": []
        },
        "extraction_time": 11.2
    }

