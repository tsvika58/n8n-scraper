"""
Real workflow fixtures for integration testing.

Provides known n8n.io workflows with expected content for validation.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import pytest


@pytest.fixture
def known_iframe_workflows():
    """Workflows known to contain iframes with text content."""
    return {
        "6270": {
            "workflow_id": "6270",
            "url": "https://n8n.io/workflows/6270-build-your-first-ai-agent/",
            "expected_iframes": 2,
            "expected_text_elements": 15,
            "expected_min_text_length": 1000,
            "description": "AI Agent workflow with tutorial content"
        },
        "8527": {
            "workflow_id": "8527",
            "url": "https://n8n.io/workflows/8527-learn-n8n-basics/",
            "expected_iframes": 1,
            "expected_text_elements": 20,
            "expected_min_text_length": 500,
            "description": "Learn n8n Basics with step-by-step instructions"
        },
        "8237": {
            "workflow_id": "8237",
            "url": "https://n8n.io/workflows/8237-personal-life-manager/",
            "expected_iframes": 1,
            "expected_text_elements": 33,
            "expected_min_text_length": 1000,
            "description": "Personal Life Manager with comprehensive explanations"
        }
    }


@pytest.fixture
def known_video_workflows():
    """Workflows known to contain YouTube videos."""
    return {
        "6270": {
            "workflow_id": "6270",
            "url": "https://n8n.io/workflows/6270-build-your-first-ai-agent/",
            "expected_videos": 1,
            "video_ids": ["laHIzhsz12E"],
            "description": "AI Agent workflow with video tutorial"
        },
        "8527": {
            "workflow_id": "8527",
            "url": "https://n8n.io/workflows/8527-learn-n8n-basics/",
            "expected_videos": 3,
            "description": "Learn n8n Basics with multiple video tutorials"
        },
        "8237": {
            "workflow_id": "8237",
            "url": "https://n8n.io/workflows/8237-personal-life-manager/",
            "expected_videos": 1,
            "description": "Personal Life Manager with video explanation"
        }
    }


@pytest.fixture
def integration_test_config():
    """Configuration for integration tests."""
    return {
        "timeout": 30000,  # 30 seconds
        "headless": True,
        "max_retries": 3,
        "workflow_timeout": 60000,  # 60 seconds per workflow
        "wait_for_content": 5000,  # 5 seconds for dynamic content
        "max_concurrent_workflows": 5
    }


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path for integration testing."""
    db_path = tmp_path / "test_integration.db"
    
    # Create workflows table
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id TEXT UNIQUE NOT NULL,
            title TEXT,
            image_urls TEXT,
            ocr_text TEXT,
            video_urls TEXT,
            video_transcripts TEXT,
            scrape_date TIMESTAMP,
            layer3_success BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    
    return str(db_path)


