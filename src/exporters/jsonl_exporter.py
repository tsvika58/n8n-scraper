"""
JSONL Exporter.

Exports workflows in JSONL format (JSON Lines).
Optimized for training data and streaming processing.
Each line is a complete JSON object.

Author: RND Manager
Task: SCRAPE-012
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class JSONLExporter(BaseExporter):
    """Export workflows to JSONL format (training-optimized)."""
    
    def __init__(self, output_dir: str = "exports", include_metadata: bool = True):
        """
        Initialize JSONL exporter.
        
        Args:
            output_dir: Directory for export files
            include_metadata: Include export metadata header
        """
        super().__init__(output_dir)
        self.include_metadata = include_metadata
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".jsonl"
    
    def export(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows to JSONL file.
        
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
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            # Optional metadata header (as first line comment)
            if self.include_metadata:
                metadata = {
                    '_metadata': {
                        'format': 'jsonl',
                        'version': '1.0',
                        'workflow_count': len(workflows),
                        'exported_at': self.export_start_time.isoformat(),
                        'description': 'JSONL format - one JSON object per line'
                    }
                }
                f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
            
            # Write each workflow as a line
            for workflow in workflows:
                workflow_data = self._prepare_workflow_for_training(workflow)
                f.write(json.dumps(workflow_data, ensure_ascii=False) + '\n')
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def _prepare_workflow_for_training(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare workflow data optimized for training.
        
        Flattens structure and focuses on key fields for ML/AI training.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Training-optimized workflow data
        """
        metadata = workflow.get('metadata') or {}
        structure = workflow.get('structure') or {}
        content = workflow.get('content') or {}
        transcripts = workflow.get('video_transcripts', [])
        
        # Flatten for training
        training_data = {
            # Identifiers
            'id': workflow.get('workflow_id'),
            'url': workflow.get('url'),
            
            # Metadata (flattened)
            'title': metadata.get('title'),
            'description': metadata.get('description'),
            'author': metadata.get('author'),
            'categories': metadata.get('categories', []),
            'tags': metadata.get('tags', []),
            'use_case': metadata.get('use_case'),
            
            # Structure (key metrics only)
            'node_count': structure.get('node_count', 0),
            'connection_count': structure.get('connection_count', 0),
            'node_types': structure.get('node_types', []),
            'extraction_type': structure.get('extraction_type'),
            
            # Content (text focus)
            'explainer_text': content.get('explainer_text'),
            'setup_instructions': content.get('setup_instructions'),
            'use_instructions': content.get('use_instructions'),
            
            # Video transcripts (combined text)
            'video_transcripts': [
                {
                    'platform': t.get('platform'),
                    'text': t.get('transcript_text'),
                    'language': t.get('transcript_language'),
                }
                for t in transcripts
            ],
            
            # Quality metrics
            'quality_score': workflow.get('quality_score'),
            'processing_status': workflow.get('processing_status'),
        }
        
        return training_data
    
    def export_for_finetuning(
        self, 
        workflows: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        instruction_template: str = "Explain this n8n workflow:"
    ) -> str:
        """
        Export workflows in format optimized for LLM fine-tuning.
        
        Creates instruction-response pairs.
        
        Args:
            workflows: List of workflow dictionaries
            filename: Optional custom filename
            instruction_template: Template for instruction field
            
        Returns:
            Path to exported file
        """
        # Validate
        if not self.validate_workflows(workflows):
            raise ValueError("Invalid workflow data")
        
        # Start export
        self.start_export(len(workflows))
        
        # Get output path
        output_path = self.get_export_path(filename or "workflows_finetuning.jsonl")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            for workflow in workflows:
                finetuning_data = self._prepare_finetuning_pair(workflow, instruction_template)
                if finetuning_data:  # Only write if we have valid data
                    f.write(json.dumps(finetuning_data, ensure_ascii=False) + '\n')
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def _prepare_finetuning_pair(
        self, 
        workflow: Dict[str, Any],
        instruction_template: str
    ) -> Optional[Dict[str, Any]]:
        """
        Prepare instruction-response pair for fine-tuning.
        
        Args:
            workflow: Workflow dictionary
            instruction_template: Template for instruction
            
        Returns:
            Fine-tuning pair or None if insufficient data
        """
        metadata = workflow.get('metadata') or {}
        content = workflow.get('content') or {}
        
        title = metadata.get('title')
        description = metadata.get('description')
        explainer = content.get('explainer_text')
        
        # Need at least title and some explanation
        if not title or not (description or explainer):
            return None
        
        # Construct instruction
        instruction = f"{instruction_template}\nTitle: {title}"
        
        # Construct response (combine available text)
        response_parts = []
        if description:
            response_parts.append(f"Description: {description}")
        if explainer:
            response_parts.append(f"Explanation: {explainer}")
        if content.get('setup_instructions'):
            response_parts.append(f"Setup: {content.get('setup_instructions')}")
        if content.get('use_instructions'):
            response_parts.append(f"Usage: {content.get('use_instructions')}")
        
        response = "\n\n".join(response_parts)
        
        return {
            'instruction': instruction,
            'response': response,
            'metadata': {
                'workflow_id': workflow.get('workflow_id'),
                'categories': metadata.get('categories', []),
                'node_count': workflow.get('structure', {}).get('node_count', 0),
            }
        }

