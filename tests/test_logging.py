"""
Unit tests for logging configuration and utilities.
"""

import pytest
from pathlib import Path
from src.utils import logging as log_module
from src.utils.logging import (
    logger,
    setup_logging,
    log_extraction_start,
    log_extraction_success,
    log_extraction_failure,
    log_session_start,
    log_session_complete,
    log_progress
)


@pytest.mark.unit
def test_setup_logging_default(tmp_path):
    """Test default logging setup"""
    log_file = tmp_path / "test.log"
    test_logger = setup_logging(log_file=str(log_file))
    
    assert test_logger is not None
    assert log_file.parent.exists()


@pytest.mark.unit
def test_setup_logging_levels(tmp_path):
    """Test logging with different levels"""
    log_file = tmp_path / "test_levels.log"
    
    # Test INFO level
    logger_info = setup_logging(log_level="INFO", log_file=str(log_file))
    logger_info.info("Test INFO")
    
    # Test DEBUG level
    logger_debug = setup_logging(log_level="DEBUG", log_file=str(log_file))
    logger_debug.debug("Test DEBUG")
    
    assert log_file.exists()


@pytest.mark.unit
def test_setup_logging_console_only(tmp_path):
    """Test logging with console only (no file)"""
    test_logger = setup_logging(enable_console=True, enable_file=False)
    test_logger.info("Console only test")
    
    assert test_logger is not None


@pytest.mark.unit
def test_setup_logging_file_only(tmp_path):
    """Test logging with file only (no console)"""
    log_file = tmp_path / "file_only.log"
    test_logger = setup_logging(
        enable_console=False,
        enable_file=True,
        log_file=str(log_file)
    )
    test_logger.info("File only test")
    
    assert log_file.exists()


@pytest.mark.unit
def test_log_extraction_start():
    """Test extraction start logging"""
    # Should not raise exception
    log_extraction_start("test-123", "Layer 1")
    log_extraction_start("test-456", "Layer 2")
    log_extraction_start("test-789", "Layer 3")


@pytest.mark.unit
def test_log_extraction_success():
    """Test extraction success logging"""
    # Should not raise exception
    log_extraction_success("test-123", "Layer 1", 3.45)
    log_extraction_success("test-456", "Layer 2", 4.12)
    log_extraction_success("test-789", "Layer 3", 11.23)


@pytest.mark.unit
def test_log_extraction_failure():
    """Test extraction failure logging"""
    # Should not raise exception
    log_extraction_failure("test-123", "Layer 1", "Test error message")
    log_extraction_failure("test-456", "Layer 2", "Connection timeout")
    log_extraction_failure("test-789", "Layer 3", "Parse error")


@pytest.mark.unit
def test_log_session_start():
    """Test session start logging"""
    # Should not raise exception
    log_session_start("Test Session", 100)
    log_session_start("Production Session", 2100)


@pytest.mark.unit
def test_log_session_complete():
    """Test session complete logging"""
    # Should not raise exception
    log_session_complete("Test Session", 95, 100, 2850.5)
    log_session_complete("Production Session", 2000, 2100, 58800.0)


@pytest.mark.unit
def test_log_progress():
    """Test progress logging"""
    # Should not raise exception
    log_progress(50, 100, "Scraping workflows")
    log_progress(100, 2100, "Complete dataset")
    log_progress(0, 100, "Starting")


@pytest.mark.unit
def test_logging_with_various_messages():
    """Test logging with various message types"""
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.success("Success message")
    logger.debug("Debug message")
    
    # All should execute without errors
    assert True


@pytest.mark.unit
def test_log_directory_creation(tmp_path):
    """Test that log directory is created automatically"""
    log_dir = tmp_path / "test_logs"
    log_file = log_dir / "test.log"
    
    # Directory doesn't exist yet
    assert not log_dir.exists()
    
    # Setup logging should create it
    setup_logging(log_file=str(log_file))
    
    assert log_dir.exists()
    assert log_file.exists()




