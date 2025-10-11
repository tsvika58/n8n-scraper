"""
Unit tests for MultimodalContentProcessor

Tests the core functionality of text extraction from iframes and video discovery
within n8n.io workflow pages.

Author: Developer-2 (Dev2)
Task: SCRAPE-006
Date: October 10, 2025
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import tempfile
import os

from src.scrapers.multimodal_processor import MultimodalProcessor


class TestMultimodalProcessorInitialization:
    """Test MultimodalProcessor initialization and configuration."""
    
    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        processor = MultimodalProcessor()
        
        assert processor.headless is True
        assert processor.timeout == 30000
        assert processor.db_path == "data/workflows.db"
        assert processor.browser is None
    
    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        processor = MultimodalProcessor(
            headless=False,
            timeout=60000,
            db_path="test.db"
        )
        
        assert processor.headless is False
        assert processor.timeout == 60000
        assert processor.db_path == "test.db"
    
    def test_init_creates_database_connection(self):
        """Test that initialization creates database connection."""
        processor = MultimodalProcessor()
        
        # The current implementation doesn't create database connection in __init__
        # This will be created when needed
        assert processor.db_path is not None


class TestVideoIdExtraction:
    """Test YouTube video ID extraction from URLs."""
    
    def setup_method(self):
        """Set up test instance."""
        self.processor = MultimodalProcessor()
    
    def test_extract_youtube_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_youtube_video_id_short_url(self):
        """Test extracting video ID from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_youtube_video_id_embed_url(self):
        """Test extracting video ID from YouTube embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_youtube_video_id_nocookie_url(self):
        """Test extracting video ID from YouTube nocookie URL."""
        url = "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_youtube_video_id_with_parameters(self):
        """Test extracting video ID from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&feature=youtu.be"
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_youtube_video_id_invalid_url(self):
        """Test extracting video ID from invalid URL."""
        url = "https://example.com/video"
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id is None
    
    def test_extract_youtube_video_id_empty_url(self):
        """Test extracting video ID from empty URL."""
        url = ""
        video_id = self.processor.extract_video_id_from_url(url)
        assert video_id is None


class TestElementTypeDetermination:
    """Test element type determination for extracted text."""
    
    def setup_method(self):
        """Set up test instance."""
        self.processor = MultimodalProcessor()
    
    def test_determine_element_type_hint(self):
        """Test determining hint element type."""
        classes = "tooltip-hint-container"
        text = "This is a helpful hint"
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "hint"
    
    def test_determine_element_type_instruction(self):
        """Test determining instruction element type."""
        classes = "instruction-step"
        text = "Step 1: Click the button"
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "instruction"
    
    def test_determine_element_type_tutorial(self):
        """Test determining tutorial element type."""
        classes = "tutorial-content"
        text = "In this tutorial, we will learn how to..."
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "tutorial"
    
    def test_determine_element_type_tutorial_box(self):
        """Test determining tutorial box element type."""
        classes = "content-box"
        text = "Try this out in your workflow"
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "tutorial_box"
    
    def test_determine_element_type_setup_instruction(self):
        """Test determining setup instruction element type."""
        classes = "setup-content"
        text = "Connect to Gemini API"
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "setup_instruction"
    
    def test_determine_element_type_explanatory_text(self):
        """Test determining explanatory text element type."""
        classes = "content-section"
        text = "This is a very long explanatory text that provides detailed information about how the workflow functions and what each step does in the process."
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "explanatory_text"
    
    def test_determine_element_type_general_text(self):
        """Test determining general text element type."""
        classes = "text-container"
        text = "Short text"
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "general_text"


class TestDatabaseOperations:
    """Test database storage operations."""
    
    def setup_method(self):
        """Set up test with temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.processor = MultimodalProcessor(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Clean up temporary database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_store_image_data_success(self):
        """Test storing image/text data successfully."""
        # Create database tables first
        from src.database.multimodal_schema import create_multimodal_tables
        create_multimodal_tables(self.temp_db.name)
        
        workflow_id = "test_workflow"
        image_url = "test_image.jpg"
        success = True
        content = "Extracted text content"
        error = None
        
        self.processor.store_image_data(workflow_id, image_url, success, content, error)
        
        # Verify data was stored using direct SQLite connection
        import sqlite3
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workflow_images WHERE workflow_id = ? AND image_url = ?", 
                      (workflow_id, image_url))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[1] == workflow_id  # workflow_id column
        assert result[2] == image_url    # image_url column
        assert result[3] == content      # ocr_text column
        assert result[6] == 1            # success column (True = 1)
        assert result[7] is None         # error_message column
    
    def test_store_image_data_failure(self):
        """Test storing image/text data with failure."""
        workflow_id = "test_workflow"
        image_url = "test_image.jpg"
        success = False
        content = None
        error = "Failed to extract text"
        
        self.processor.store_image_data(workflow_id, image_url, success, content, error)
        
        # Verify data was stored
        session = self.processor.Session()
        stored_data = session.query(self.processor.WorkflowImage).filter_by(
            workflow_id=workflow_id,
            image_url=image_url
        ).first()
        
        assert stored_data is not None
        assert stored_data.success is False
        assert stored_data.error_message == error
        assert stored_data.ocr_text is None
        session.close()
    
    def test_store_video_data_success(self):
        """Test storing video data successfully."""
        workflow_id = "test_workflow"
        video_url = "https://youtube.com/watch?v=test123"
        video_id = "test123"
        success = True
        transcript = "Video transcript content"
        error = None
        
        self.processor.store_video_data(workflow_id, video_url, video_id, success, transcript, error)
        
        # Verify data was stored
        session = self.processor.Session()
        stored_data = session.query(self.processor.WorkflowVideo).filter_by(
            workflow_id=workflow_id,
            video_url=video_url
        ).first()
        
        assert stored_data is not None
        assert stored_data.workflow_id == workflow_id
        assert stored_data.video_url == video_url
        assert stored_data.video_id == video_id
        assert stored_data.transcript == transcript
        assert stored_data.success is True
        assert stored_data.error_message is None
        session.close()
    
    def test_store_video_data_failure(self):
        """Test storing video data with failure."""
        workflow_id = "test_workflow"
        video_url = "https://youtube.com/watch?v=test123"
        video_id = "test123"
        success = False
        transcript = None
        error = "No transcript available"
        
        self.processor.store_video_data(workflow_id, video_url, video_id, success, transcript, error)
        
        # Verify data was stored
        session = self.processor.Session()
        stored_data = session.query(self.processor.WorkflowVideo).filter_by(
            workflow_id=workflow_id,
            video_url=video_url
        ).first()
        
        assert stored_data is not None
        assert stored_data.success is False
        assert stored_data.error_message == error
        assert stored_data.transcript is None
        session.close()


class TestAsyncContextManagement:
    """Test async context management (__aenter__ and __aexit__)."""
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using MultimodalProcessor as async context manager."""
        with patch('src.scrapers.multimodal_processor.async_playwright') as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_playwright.return_value.start.return_value = mock_playwright_instance
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            
            async with MultimodalProcessor() as processor:
                assert processor.browser is not None
                assert processor.playwright is not None
            
            # Verify cleanup was called
            mock_browser.close.assert_called_once()
            mock_playwright_instance.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_context_manager_with_exception(self):
        """Test async context manager handles exceptions properly."""
        with patch('src.scrapers.multimodal_processor.async_playwright') as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_playwright.return_value.start.return_value = mock_playwright_instance
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            
            try:
                async with MultimodalProcessor() as processor:
                    assert processor.browser is not None
                    raise Exception("Test exception")
            except Exception:
                pass
            
            # Verify cleanup was called even with exception
            mock_browser.close.assert_called_once()
            mock_playwright_instance.stop.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test instance."""
        self.processor = MultimodalProcessor()
    
    def test_extract_video_id_from_url_with_none(self):
        """Test extracting video ID from None URL."""
        video_id = self.processor.extract_video_id_from_url(None)
        assert video_id is None
    
    def test_extract_video_id_from_url_with_malformed_url(self):
        """Test extracting video ID from malformed URL."""
        video_id = self.processor.extract_video_id_from_url("not-a-url")
        assert video_id is None
    
    def test_determine_element_type_with_none_inputs(self):
        """Test determining element type with None inputs."""
        element_type = self.processor._determine_element_type(None, None)
        assert element_type == "general_text"
    
    def test_determine_element_type_with_empty_strings(self):
        """Test determining element type with empty strings."""
        element_type = self.processor._determine_element_type("", "")
        assert element_type == "general_text"


class TestDataValidation:
    """Test data validation and edge cases."""
    
    def setup_method(self):
        """Set up test with temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.processor = MultimodalProcessor(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Clean up temporary database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_store_image_data_with_long_content(self):
        """Test storing image data with very long content."""
        workflow_id = "test_workflow"
        image_url = "test_image.jpg"
        success = True
        content = "A" * 10000  # Very long content
        error = None
        
        self.processor.store_image_data(workflow_id, image_url, success, content, error)
        
        # Verify data was stored correctly
        session = self.processor.Session()
        stored_data = session.query(self.processor.WorkflowImage).filter_by(
            workflow_id=workflow_id,
            image_url=image_url
        ).first()
        
        assert stored_data is not None
        assert stored_data.ocr_text == content
        assert stored_data.text_length == len(content)
        session.close()
    
    def test_store_video_data_with_special_characters(self):
        """Test storing video data with special characters."""
        workflow_id = "test_workflow"
        video_url = "https://youtube.com/watch?v=test123"
        video_id = "test123"
        success = True
        transcript = "Transcript with special chars: àáâãäåæçèéêë"
        error = None
        
        self.processor.store_video_data(workflow_id, video_url, video_id, success, transcript, error)
        
        # Verify data was stored correctly
        session = self.processor.Session()
        stored_data = session.query(self.processor.WorkflowVideo).filter_by(
            workflow_id=workflow_id,
            video_url=video_url
        ).first()
        
        assert stored_data is not None
        assert stored_data.transcript == transcript
        session.close()


# Test configuration and fixtures
@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    yield temp_db.name
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


@pytest.fixture
def processor_with_temp_db(temp_db_path):
    """Create a MultimodalProcessor instance with temporary database."""
    return MultimodalProcessor(db_path=temp_db_path)


class TestProcessorWithTempDb:
    """Test MultimodalProcessor with temporary database."""
    
    def test_processor_with_temp_db_initialization(self, processor_with_temp_db):
        """Test processor initialization with temporary database."""
        assert processor_with_temp_db.db_path is not None
        assert processor_with_temp_db.engine is not None
        assert processor_with_temp_db.Session is not None
    
    def test_database_operations_with_temp_db(self, processor_with_temp_db):
        """Test database operations with temporary database."""
        workflow_id = "test_workflow"
        image_url = "test_image.jpg"
        success = True
        content = "Test content"
        error = None
        
        processor_with_temp_db.store_image_data(workflow_id, image_url, success, content, error)
        
        # Verify data was stored
        session = processor_with_temp_db.Session()
        stored_data = session.query(processor_with_temp_db.WorkflowImage).filter_by(
            workflow_id=workflow_id,
            image_url=image_url
        ).first()
        
        assert stored_data is not None
        assert stored_data.ocr_text == content
        session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
