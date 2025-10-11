"""
Unit tests for MultimodalContentProcessor with Unified Schema

Tests the core functionality of text extraction from iframes and video discovery
using the unified Workflow table with JSON fields.

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
import sqlite3
import json

from src.scrapers.multimodal_processor import MultimodalProcessor


@pytest.fixture
def test_db():
    """Create a temporary test database with workflows table."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Create workflows table
    conn = sqlite3.connect(temp_db.name)
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
    
    yield temp_db.name
    
    # Cleanup
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


class TestMultimodalProcessorInitialization:
    """Test MultimodalProcessor initialization and configuration."""
    
    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        processor = MultimodalProcessor()
        
        assert processor.headless is True
        assert processor.timeout == 30000
        assert str(processor.db_path) == "data/workflows.db"
        assert processor.browser is None
        assert processor.playwright is None
    
    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        processor = MultimodalProcessor(
            headless=False,
            timeout=60000,
            db_path="test.db"
        )
        
        assert processor.headless is False
        assert processor.timeout == 60000
        assert str(processor.db_path) == "test.db"


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
    
    def test_extract_youtube_video_id_none_url(self):
        """Test extracting video ID from None URL."""
        video_id = self.processor.extract_video_id_from_url(None)
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
    
    def test_determine_element_type_general_text(self):
        """Test determining general text element type."""
        classes = "text-container"
        text = "Short text"
        element_type = self.processor._determine_element_type(classes, text)
        assert element_type == "general_text"
    
    def test_determine_element_type_with_none_inputs(self):
        """Test determining element type with None inputs."""
        element_type = self.processor._determine_element_type(None, None)
        assert element_type == "general_text"
    
    def test_determine_element_type_with_empty_strings(self):
        """Test determining element type with empty strings."""
        element_type = self.processor._determine_element_type("", "")
        assert element_type == "general_text"


class TestDatabaseOperations:
    """Test database storage operations with unified schema."""
    
    def test_store_image_data_creates_new_workflow(self, test_db):
        """Test storing image data creates new workflow record."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        image_url = "iframe_1_text_tutorial_1234"
        success = True
        content = "Try this workflow out"
        
        processor.store_image_data(workflow_id, image_url, success, content, None)
        
        # Verify data was stored
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT workflow_id, image_urls, ocr_text FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == workflow_id
        
        image_urls = json.loads(result[1])
        assert len(image_urls) == 1
        assert image_urls[0] == image_url
        
        assert result[2] == content
    
    def test_store_image_data_appends_to_existing_workflow(self, test_db):
        """Test storing image data appends to existing workflow."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        
        # Store first image
        processor.store_image_data(workflow_id, "image_1", True, "Text 1", None)
        
        # Store second image
        processor.store_image_data(workflow_id, "image_2", True, "Text 2", None)
        
        # Verify data was appended
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT image_urls, ocr_text FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        image_urls = json.loads(result[0])
        assert len(image_urls) == 2
        assert "image_1" in image_urls
        assert "image_2" in image_urls
        
        # Check aggregated text
        assert "Text 1" in result[1]
        assert "Text 2" in result[1]
    
    def test_store_video_data_creates_new_workflow(self, test_db):
        """Test storing video data creates new workflow record."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        video_url = "https://youtube.com/embed/test123"
        video_id = "test123"
        success = True
        transcript = "Video transcript content"
        
        processor.store_video_data(workflow_id, video_url, video_id, success, transcript, None)
        
        # Verify data was stored
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT workflow_id, video_urls, video_transcripts FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == workflow_id
        
        video_urls = json.loads(result[1])
        assert len(video_urls) == 1
        assert video_urls[0] == video_url
        
        video_transcripts = json.loads(result[2])
        assert len(video_transcripts) == 1
        assert video_transcripts[0]["video_id"] == video_id
        assert video_transcripts[0]["transcript"] == transcript
        assert video_transcripts[0]["success"] is True
    
    def test_store_video_data_appends_to_existing_workflow(self, test_db):
        """Test storing video data appends to existing workflow."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        
        # Store first video
        processor.store_video_data(workflow_id, "video_url_1", "vid_1", True, "Transcript 1", None)
        
        # Store second video
        processor.store_video_data(workflow_id, "video_url_2", "vid_2", True, "Transcript 2", None)
        
        # Verify data was appended
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT video_urls, video_transcripts FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        video_urls = json.loads(result[0])
        assert len(video_urls) == 2
        assert "video_url_1" in video_urls
        assert "video_url_2" in video_urls
        
        video_transcripts = json.loads(result[1])
        assert len(video_transcripts) == 2
        assert video_transcripts[0]["video_id"] == "vid_1"
        assert video_transcripts[1]["video_id"] == "vid_2"
    
    def test_store_image_data_with_empty_text(self, test_db):
        """Test storing image data with empty text."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        
        processor.store_image_data(workflow_id, "image_1", True, "", None)
        
        # Verify data was stored
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT image_urls, ocr_text FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        image_urls = json.loads(result[0])
        assert len(image_urls) == 1
        assert result[1] == ""
    
    def test_store_video_data_with_null_transcript(self, test_db):
        """Test storing video data with null transcript."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        
        processor.store_video_data(workflow_id, "video_url", "vid_1", False, None, "No transcript available")
        
        # Verify data was stored
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT video_transcripts FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        video_transcripts = json.loads(result[0])
        assert len(video_transcripts) == 1
        assert video_transcripts[0]["transcript"] is None
        assert video_transcripts[0]["success"] is False
        assert video_transcripts[0]["error"] == "No transcript available"
    
    def test_store_image_data_with_special_characters(self, test_db):
        """Test storing image data with special characters."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        content = "Text with special chars: àáâãäåæçèéêë"
        
        processor.store_image_data(workflow_id, "image_1", True, content, None)
        
        # Verify data was stored correctly
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT ocr_text FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == content
    
    def test_store_image_data_with_long_content(self, test_db):
        """Test storing image data with very long content."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        content = "A" * 10000  # Very long content
        
        processor.store_image_data(workflow_id, "image_1", True, content, None)
        
        # Verify data was stored correctly
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT ocr_text FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == content
        assert len(result[0]) == 10000


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test instance."""
        self.processor = MultimodalProcessor()
    
    def test_extract_video_id_from_url_with_malformed_url(self):
        """Test extracting video ID from malformed URL."""
        video_id = self.processor.extract_video_id_from_url("not-a-url")
        assert video_id is None
    
    def test_determine_element_type_handles_none_gracefully(self):
        """Test element type determination handles None gracefully."""
        element_type = self.processor._determine_element_type(None, "Some text")
        assert element_type in ["general_text", "instruction", "explanatory_text"]
    
    def test_determine_element_type_handles_empty_text(self):
        """Test element type determination handles empty text."""
        element_type = self.processor._determine_element_type("some-class", "")
        assert element_type == "general_text"


class TestAsyncContextManagement:
    """Test async context management."""
    
    @pytest.mark.asyncio
    async def test_async_context_manager_initialization(self):
        """Test async context manager properly initializes."""
        with patch('src.scrapers.multimodal_processor.async_playwright') as mock_playwright:
            # Setup mocks
            mock_pw_instance = AsyncMock()
            mock_browser = AsyncMock()
            
            async def mock_start():
                return mock_pw_instance
            
            mock_playwright.return_value.start = mock_start
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            # Test context manager
            async with MultimodalProcessor() as processor:
                assert processor.browser is not None
                assert processor.playwright is not None
            
            # Verify cleanup
            mock_browser.close.assert_called_once()
            mock_pw_instance.stop.assert_called_once()


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_multiple_operations_maintain_data_integrity(self, test_db):
        """Test multiple operations maintain data integrity."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        
        # Store multiple images
        for i in range(5):
            processor.store_image_data(workflow_id, f"image_{i}", True, f"Text {i}", None)
        
        # Store multiple videos
        for i in range(3):
            processor.store_video_data(workflow_id, f"video_url_{i}", f"vid_{i}", True, f"Transcript {i}", None)
        
        # Verify all data was stored correctly
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT image_urls, video_urls, video_transcripts FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        image_urls = json.loads(result[0])
        assert len(image_urls) == 5
        
        video_urls = json.loads(result[1])
        assert len(video_urls) == 3
        
        video_transcripts = json.loads(result[2])
        assert len(video_transcripts) == 3
    
    def test_json_structure_is_valid(self, test_db):
        """Test that stored JSON structure is valid and parseable."""
        processor = MultimodalProcessor(db_path=test_db)
        
        workflow_id = "test_workflow"
        
        processor.store_image_data(workflow_id, "image_1", True, "Text 1", None)
        processor.store_video_data(workflow_id, "video_url_1", "vid_1", True, "Transcript 1", None)
        
        # Retrieve and verify JSON structure
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT image_urls, video_urls, video_transcripts FROM workflows WHERE workflow_id = ?", 
                      (workflow_id,))
        result = cursor.fetchone()
        conn.close()
        
        # Verify JSON is parseable
        try:
            image_urls = json.loads(result[0])
            video_urls = json.loads(result[1])
            video_transcripts = json.loads(result[2])
            
            assert isinstance(image_urls, list)
            assert isinstance(video_urls, list)
            assert isinstance(video_transcripts, list)
            assert isinstance(video_transcripts[0], dict)
        except json.JSONDecodeError:
            pytest.fail("Invalid JSON structure stored in database")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/scrapers/multimodal_processor", "--cov-report=term-missing"])

