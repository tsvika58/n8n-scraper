"""
Logging Configuration for N8N Workflow Scraper
Uses Loguru for beautiful, structured logging with Rich console output.
"""

from loguru import logger
from rich.console import Console
from rich.theme import Theme
from pathlib import Path
import sys


# Rich console for beautiful output
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "debug": "dim blue"
})

console = Console(theme=custom_theme)


def setup_logging(
    log_level="INFO",
    log_file="logs/scraper.log",
    enable_console=True,
    enable_file=True
):
    """
    Configure Loguru logging with console and file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        enable_console: Enable console logging with colors
        enable_file: Enable file logging with rotation
        
    Returns:
        Configured logger instance
    """
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors (if enabled)
    if enable_console:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True,
            enqueue=True  # Thread-safe
        )
    
    # File handler with rotation (if enabled)
    if enable_file:
        # Ensure logs directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",  # Always log DEBUG to file
            rotation="100 MB",  # Rotate when file reaches 100MB
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated logs
            enqueue=True  # Thread-safe
        )
    
    logger.info("🚀 Logging configured successfully")
    logger.debug(f"Log level: {log_level}")
    logger.debug(f"Console logging: {enable_console}")
    logger.debug(f"File logging: {enable_file}")
    if enable_file:
        logger.debug(f"Log file: {Path(log_file).absolute()}")
    
    return logger


# Initialize logging on import
Path("logs").mkdir(exist_ok=True)
logger = setup_logging()


# Convenience functions
def log_extraction_start(workflow_id: str, layer: str):
    """Log start of extraction"""
    logger.info(f"🔍 Starting {layer} extraction for workflow {workflow_id}")


def log_extraction_success(workflow_id: str, layer: str, duration: float):
    """Log successful extraction"""
    logger.success(f"✅ {layer} extraction completed for workflow {workflow_id} in {duration:.2f}s")


def log_extraction_failure(workflow_id: str, layer: str, error: str):
    """Log extraction failure"""
    logger.error(f"❌ {layer} extraction failed for workflow {workflow_id}: {error}")


def log_session_start(session_name: str, total_workflows: int):
    """Log scraping session start"""
    logger.info(f"🎯 Starting scraping session: {session_name} ({total_workflows} workflows)")


def log_session_complete(session_name: str, success_count: int, total_count: int, duration: float):
    """Log scraping session completion"""
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    logger.success(
        f"🎉 Session '{session_name}' complete: {success_count}/{total_count} "
        f"({success_rate:.1f}%) in {duration:.1f}s"
    )


def log_progress(current: int, total: int, message: str = "Progress"):
    """Log progress update"""
    percentage = (current / total * 100) if total > 0 else 0
    logger.info(f"📊 {message}: {current}/{total} ({percentage:.1f}%)")




