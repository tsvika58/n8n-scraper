"""
Pytest configuration and fixtures for N8N Workflow Scraper tests.

Provides shared fixtures for unit testing with mocked external dependencies.
"""

import pytest
import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
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


# ============================================================================
# MOCK EXTERNAL DEPENDENCIES (For Unit Tests)
# ============================================================================

@pytest.fixture
def mock_aiohttp_response():
    """Mock aiohttp response object."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={'success': True})
    response.text = AsyncMock(return_value='<html>Success</html>')
    response.headers = {'content-type': 'application/json'}
    return response


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.post = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_playwright_page():
    """Mock Playwright page object."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.content = AsyncMock(return_value='<html>Test content</html>')
    page.query_selector = AsyncMock()
    page.query_selector_all = AsyncMock(return_value=[])
    page.wait_for_selector = AsyncMock()
    page.evaluate = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser object."""
    browser = AsyncMock()
    browser.new_page = AsyncMock()
    browser.close = AsyncMock()
    return browser


# ============================================================================
# ENHANCED MOCK DATA (For Layer 2 Testing)
# ============================================================================

@pytest.fixture
def mock_layer2_workflow_json():
    """Mock Layer 2 workflow JSON response (template API format)."""
    return {
        'id': '2462',
        'name': 'Test Workflow',
        'workflow': {
            'nodes': [
                {
                    'id': 'node1',
                    'name': 'Start',
                    'type': 'n8n-nodes-base.start',
                    'position': [100, 200],
                    'parameters': {}
                },
                {
                    'id': 'node2',
                    'name': 'HTTP Request',
                    'type': 'n8n-nodes-base.httpRequest',
                    'position': [300, 200],
                    'parameters': {
                        'url': 'https://api.example.com',
                        'method': 'GET'
                    }
                }
            ],
            'connections': {
                'Start': {
                    'main': [
                        [
                            {
                                'node': 'HTTP Request',
                                'type': 'main',
                                'index': 0
                            }
                        ]
                    ]
                }
            }
        }
    }


@pytest.fixture
def mock_layer3_content():
    """Mock Layer 3 content response."""
    return {
        'explainer_text': 'This workflow automates email sending',
        'explainer_html': '<p>This workflow automates email sending</p>',
        'setup_instructions': '1. Configure API credentials\n2. Set up email template',
        'use_instructions': '1. Run the workflow\n2. Check results',
        'has_videos': True,
        'videos': [
            {
                'url': 'https://youtube.com/watch?v=test123',
                'video_id': 'test123',
                'platform': 'youtube',
                'transcript': {
                    'text': 'Welcome to this workflow tutorial',
                    'duration': 300,
                    'language': 'en'
                }
            }
        ],
        'has_iframes': True,
        'iframe_count': 2
    }


# ============================================================================
# TEST DATA UTILITIES
# ============================================================================

@pytest.fixture
def sample_workflow_id():
    """Sample workflow ID for testing."""
    return '2462'


@pytest.fixture
def sample_workflow_url():
    """Sample workflow URL for testing."""
    return 'https://n8n.io/workflows/2462'


@pytest.fixture
def mock_extraction_result(mock_layer1_data, mock_layer2_workflow_json, mock_layer3_content):
    """Complete mock extraction result."""
    return {
        'workflow_id': '2462',
        'url': 'https://n8n.io/workflows/2462',
        'processing_time': 14.5,
        'quality_score': 85.3,
        'layers': {
            'layer1': {
                'success': True,
                'data': mock_layer1_data['data']
            },
            'layer2': {
                'success': True,
                'node_count': 2,
                'connection_count': 1,
                'node_types': ['start', 'httpRequest'],
                'extraction_type': 'full',
                'fallback_used': False,
                'data': mock_layer2_workflow_json
            },
            'layer3': {
                'success': True,
                'data': mock_layer3_content
            }
        }
    }


# ============================================================================
# ASYNC TEST HELPERS
# ============================================================================

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# PATCH DECORATORS (Global Mocks)
# ============================================================================

@pytest.fixture
def mock_youtube_api():
    """Patch YouTube API for transcript tests."""
    with patch('youtube_transcript_api.YouTubeTranscriptApi') as mock:
        mock.get_transcript.return_value = [
            {'text': 'Welcome to this tutorial', 'start': 0.0, 'duration': 5.0}
        ]
        yield mock
