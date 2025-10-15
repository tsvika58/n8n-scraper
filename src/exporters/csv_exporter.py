"""
CSV Exporter.

Exports workflow metadata summary in CSV format.
Suitable for spreadsheets and basic analytics.

Author: RND Manager
Task: SCRAPE-012
"""

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class CSVExporter(BaseExporter):
    """Export workflows to CSV format (metadata summary)."""
    
    def __init__(self, output_dir: str = "exports", delimiter: str = ","):
        """
        Initialize CSV exporter.
        
        Args:
            output_dir: Directory for export files
            delimiter: CSV delimiter (default: comma)
        """
        super().__init__(output_dir)
        self.delimiter = delimiter
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".csv"
    
    def export(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows to CSV file.
        
        Args:
            workflows: List of workflow dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        # Validate
        if not self.validate_workflows(workflows):
            raise ValueError("Invalid workflow data")
        
        # Start export
        self.start_export(len(workflows))
        
        # Get output path
        output_path = self.get_export_path(filename)
        
        # Define CSV columns
        columns = [
            'workflow_id',
            'url',
            'title',
            'description',
            'author',
            'categories',
            'use_case',
            'node_count',
            'connection_count',
            'node_types',
            'extraction_type',
            'has_videos',
            'video_count',
            'quality_score',
            'processing_status',
            'processing_time',
            'views',
            'shares',
            'created_at',
            'updated_at',
        ]
        
        # Write to file
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, delimiter=self.delimiter)
            writer.writeheader()
            
            for workflow in workflows:
                row = self._prepare_csv_row(workflow)
                writer.writerow(row)
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def _prepare_csv_row(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare workflow data for CSV row.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            CSV row data
        """
        metadata = workflow.get('metadata') or {}
        structure = workflow.get('structure') or {}
        content = workflow.get('content') or {}
        
        return {
            'workflow_id': workflow.get('workflow_id', ''),
            'url': workflow.get('url', ''),
            'title': metadata.get('title', ''),
            'description': self._truncate(metadata.get('description', ''), 200),
            'author': metadata.get('author', ''),
            'categories': '|'.join(metadata.get('categories', [])),
            'use_case': self._truncate(metadata.get('use_case', ''), 100),
            'node_count': structure.get('node_count', 0),
            'connection_count': structure.get('connection_count', 0),
            'node_types': '|'.join(structure.get('node_types', [])),
            'extraction_type': structure.get('extraction_type', ''),
            'has_videos': 'Yes' if content.get('has_videos') else 'No',
            'video_count': content.get('video_count', 0),
            'quality_score': workflow.get('quality_score', 0),
            'processing_status': workflow.get('processing_status', ''),
            'processing_time': workflow.get('processing_time', 0),
            'views': metadata.get('views', 0),
            'shares': metadata.get('shares', 0),
            'created_at': workflow.get('created_at', ''),
            'updated_at': workflow.get('updated_at', ''),
        }
    
    def _truncate(self, text: str, max_length: int) -> str:
        """
        Truncate text to max length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if not text:
            return ''
        
        text = str(text)
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + '...'
    
    def export_detailed(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows with detailed columns (more fields).
        
        Args:
            workflows: List of workflow dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        # Validate
        if not self.validate_workflows(workflows):
            raise ValueError("Invalid workflow data")
        
        # Start export
        self.start_export(len(workflows))
        
        # Get output path
        output_path = self.get_export_path(filename or "workflows_detailed.csv")
        
        # Define extended CSV columns
        columns = [
            'workflow_id',
            'url',
            'title',
            'description',
            'author',
            'categories',
            'tags',
            'use_case',
            'node_count',
            'connection_count',
            'node_types',
            'extraction_type',
            'fallback_used',
            'explainer_text',
            'setup_instructions',
            'use_instructions',
            'has_videos',
            'video_count',
            'has_iframes',
            'iframe_count',
            'quality_score',
            'processing_status',
            'processing_time',
            'views',
            'shares',
            'created_date',
            'updated_date',
            'created_at',
            'updated_at',
        ]
        
        # Write to file
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, delimiter=self.delimiter)
            writer.writeheader()
            
            for workflow in workflows:
                row = self._prepare_detailed_csv_row(workflow)
                writer.writerow(row)
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def _prepare_detailed_csv_row(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare workflow data for detailed CSV row.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Detailed CSV row data
        """
        metadata = workflow.get('metadata') or {}
        structure = workflow.get('structure') or {}
        content = workflow.get('content') or {}
        
        return {
            'workflow_id': workflow.get('workflow_id', ''),
            'url': workflow.get('url', ''),
            'title': metadata.get('title', ''),
            'description': self._truncate(metadata.get('description', ''), 500),
            'author': metadata.get('author', ''),
            'categories': '|'.join(metadata.get('categories', [])),
            'tags': '|'.join(metadata.get('tags', [])),
            'use_case': self._truncate(metadata.get('use_case', ''), 200),
            'node_count': structure.get('node_count', 0),
            'connection_count': structure.get('connection_count', 0),
            'node_types': '|'.join(structure.get('node_types', [])),
            'extraction_type': structure.get('extraction_type', ''),
            'fallback_used': 'Yes' if structure.get('fallback_used') else 'No',
            'explainer_text': self._truncate(content.get('explainer_text', ''), 500),
            'setup_instructions': self._truncate(content.get('setup_instructions', ''), 300),
            'use_instructions': self._truncate(content.get('use_instructions', ''), 300),
            'has_videos': 'Yes' if content.get('has_videos') else 'No',
            'video_count': content.get('video_count', 0),
            'has_iframes': 'Yes' if content.get('has_iframes') else 'No',
            'iframe_count': content.get('iframe_count', 0),
            'quality_score': workflow.get('quality_score', 0),
            'processing_status': workflow.get('processing_status', ''),
            'processing_time': workflow.get('processing_time', 0),
            'views': metadata.get('views', 0),
            'shares': metadata.get('shares', 0),
            'created_date': metadata.get('created_date', ''),
            'updated_date': metadata.get('updated_date', ''),
            'created_at': workflow.get('created_at', ''),
            'updated_at': workflow.get('updated_at', ''),
        }






