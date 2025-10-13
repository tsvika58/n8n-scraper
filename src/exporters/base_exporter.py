"""
Base Exporter Class.

Provides common interface and functionality for all exporters.

Author: RND Manager
Task: SCRAPE-012
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Abstract base class for all exporters."""
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize base exporter.
        
        Args:
            output_dir: Directory for export files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.export_count = 0
        self.export_start_time = None
        self.export_end_time = None
    
    @abstractmethod
    def export(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows to file.
        
        Args:
            workflows: List of workflow dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this exporter."""
        pass
    
    def get_default_filename(self) -> str:
        """Generate default filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = self.get_file_extension()
        return f"workflows_export_{timestamp}{extension}"
    
    def get_export_path(self, filename: Optional[str] = None) -> Path:
        """
        Get full export file path.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Full path to export file
        """
        if filename is None:
            filename = self.get_default_filename()
        return self.output_dir / filename
    
    def start_export(self, workflow_count: int):
        """
        Mark export start.
        
        Args:
            workflow_count: Number of workflows to export
        """
        self.export_start_time = datetime.now()
        self.export_count = workflow_count
        logger.info(f"Starting export of {workflow_count} workflows")
    
    def end_export(self, output_path: Path):
        """
        Mark export end and log stats.
        
        Args:
            output_path: Path to exported file
        """
        self.export_end_time = datetime.now()
        duration = (self.export_end_time - self.export_start_time).total_seconds()
        file_size = output_path.stat().st_size / 1024 / 1024  # MB
        
        logger.info(f"Export complete:")
        logger.info(f"  - Workflows: {self.export_count}")
        logger.info(f"  - Duration: {duration:.2f}s")
        logger.info(f"  - File size: {file_size:.2f} MB")
        logger.info(f"  - Output: {output_path}")
        logger.info(f"  - Rate: {self.export_count / duration:.1f} workflows/sec")
    
    def validate_workflows(self, workflows: List[Dict[str, Any]]) -> bool:
        """
        Validate workflow data before export.
        
        Args:
            workflows: List of workflow dictionaries
            
        Returns:
            True if valid, False otherwise
        """
        if not workflows:
            logger.warning("No workflows to export")
            return False
        
        if not isinstance(workflows, list):
            logger.error("Workflows must be a list")
            return False
        
        # Check first workflow structure
        sample = workflows[0]
        required_fields = ['workflow_id', 'url']
        
        for field in required_fields:
            if field not in sample:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def get_export_stats(self) -> Dict[str, Any]:
        """
        Get export statistics.
        
        Returns:
            Dictionary with export stats
        """
        if not self.export_start_time or not self.export_end_time:
            return {}
        
        duration = (self.export_end_time - self.export_start_time).total_seconds()
        
        return {
            'workflow_count': self.export_count,
            'duration_seconds': duration,
            'workflows_per_second': self.export_count / duration if duration > 0 else 0,
            'start_time': self.export_start_time.isoformat(),
            'end_time': self.export_end_time.isoformat(),
        }




