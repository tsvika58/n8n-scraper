"""
JSON Exporter.

Exports complete workflow data in JSON format.
Includes all layers (metadata, structure, content, transcripts).

Author: RND Manager
Task: SCRAPE-012
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class JSONExporter(BaseExporter):
    """Export workflows to JSON format (complete data)."""
    
    def __init__(self, output_dir: str = "exports", indent: int = 2):
        """
        Initialize JSON exporter.
        
        Args:
            output_dir: Directory for export files
            indent: JSON indentation (2 for readability, None for compact)
        """
        super().__init__(output_dir)
        self.indent = indent
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".json"
    
    def export(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows to JSON file.
        
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
        
        # Prepare export data
        export_data = {
            'export_metadata': {
                'format': 'json',
                'version': '1.0',
                'workflow_count': len(workflows),
                'exported_at': self.export_start_time.isoformat(),
                'description': 'Complete workflow data export with all layers'
            },
            'workflows': []
        }
        
        # Process each workflow
        for workflow in workflows:
            export_data['workflows'].append(self._prepare_workflow(workflow))
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=self.indent, ensure_ascii=False)
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def _prepare_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare workflow data for JSON export.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Prepared workflow data
        """
        return {
            'workflow_id': workflow.get('workflow_id'),
            'url': workflow.get('url'),
            'processing_status': workflow.get('processing_status'),
            'quality_score': workflow.get('quality_score'),
            'processing_time': workflow.get('processing_time'),
            'metadata': self._prepare_metadata(workflow.get('metadata')),
            'structure': self._prepare_structure(workflow.get('structure')),
            'content': self._prepare_content(workflow.get('content')),
            'video_transcripts': self._prepare_transcripts(workflow.get('video_transcripts', [])),
            'created_at': workflow.get('created_at'),
            'updated_at': workflow.get('updated_at'),
        }
    
    def _prepare_metadata(self, metadata: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Prepare metadata for export."""
        if not metadata:
            return None
        
        return {
            'title': metadata.get('title'),
            'description': metadata.get('description'),
            'author': metadata.get('author'),
            'categories': metadata.get('categories'),
            'tags': metadata.get('tags'),
            'views': metadata.get('views'),
            'shares': metadata.get('shares'),
            'use_case': metadata.get('use_case'),
            'created_date': metadata.get('created_date'),
            'updated_date': metadata.get('updated_date'),
        }
    
    def _prepare_structure(self, structure: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Prepare structure for export."""
        if not structure:
            return None
        
        return {
            'node_count': structure.get('node_count'),
            'connection_count': structure.get('connection_count'),
            'node_types': structure.get('node_types'),
            'extraction_type': structure.get('extraction_type'),
            'fallback_used': structure.get('fallback_used'),
            'nodes': structure.get('nodes'),
            'connections': structure.get('connections'),
            'workflow_settings': structure.get('workflow_settings'),
        }
    
    def _prepare_content(self, content: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Prepare content for export."""
        if not content:
            return None
        
        return {
            'explainer_text': content.get('explainer_text'),
            'explainer_html': content.get('explainer_html'),
            'setup_instructions': content.get('setup_instructions'),
            'use_instructions': content.get('use_instructions'),
            'has_videos': content.get('has_videos'),
            'video_count': content.get('video_count'),
            'videos': content.get('videos'),
            'has_iframes': content.get('has_iframes'),
            'iframe_count': content.get('iframe_count'),
            'iframe_sources': content.get('iframe_sources'),
        }
    
    def _prepare_transcripts(self, transcripts: List[Dict]) -> List[Dict[str, Any]]:
        """Prepare video transcripts for export."""
        if not transcripts:
            return []
        
        return [
            {
                'video_url': t.get('video_url'),
                'video_id': t.get('video_id'),
                'platform': t.get('platform'),
                'transcript_text': t.get('transcript_text'),
                'transcript_language': t.get('transcript_language'),
                'extraction_method': t.get('extraction_method'),
                'duration_seconds': t.get('duration_seconds'),
            }
            for t in transcripts
        ]
    
    def export_compact(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows in compact JSON format (no indentation).
        
        Args:
            workflows: List of workflow dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        original_indent = self.indent
        self.indent = None
        try:
            return self.export(workflows, filename)
        finally:
            self.indent = original_indent


