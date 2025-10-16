"""
Export Manager.

Unified interface for managing all export formats.
Simplifies exporting to multiple formats simultaneously.

Author: RND Manager
Task: SCRAPE-012
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

from .json_exporter import JSONExporter
from .jsonl_exporter import JSONLExporter
from .csv_exporter import CSVExporter
from .parquet_exporter import ParquetExporter, PARQUET_AVAILABLE

logger = logging.getLogger(__name__)


class ExportManager:
    """Manage exports across multiple formats."""
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize export manager.
        
        Args:
            output_dir: Base directory for exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize exporters
        self.json_exporter = JSONExporter(output_dir)
        self.jsonl_exporter = JSONLExporter(output_dir)
        self.csv_exporter = CSVExporter(output_dir)
        
        # Parquet is optional
        self.parquet_exporter = None
        if PARQUET_AVAILABLE:
            try:
                self.parquet_exporter = ParquetExporter(output_dir)
            except ImportError:
                logger.warning("Parquet export unavailable")
        
        self.export_history = []
    
    def export_all_formats(
        self, 
        workflows: List[Dict[str, Any]], 
        base_filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export workflows to all available formats.
        
        Args:
            workflows: List of workflow dictionaries
            base_filename: Optional base filename (without extension)
            
        Returns:
            Dictionary mapping format to output path
        """
        if not workflows:
            logger.warning("No workflows to export")
            return {}
        
        # Generate base filename if not provided
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"workflows_export_{timestamp}"
        
        results = {}
        
        # Export to JSON
        try:
            json_path = self.json_exporter.export(workflows, f"{base_filename}.json")
            results['json'] = json_path
            logger.info(f"✅ JSON export: {json_path}")
        except Exception as e:
            logger.error(f"❌ JSON export failed: {e}")
        
        # Export to JSONL
        try:
            jsonl_path = self.jsonl_exporter.export(workflows, f"{base_filename}.jsonl")
            results['jsonl'] = jsonl_path
            logger.info(f"✅ JSONL export: {jsonl_path}")
        except Exception as e:
            logger.error(f"❌ JSONL export failed: {e}")
        
        # Export to CSV
        try:
            csv_path = self.csv_exporter.export(workflows, f"{base_filename}.csv")
            results['csv'] = csv_path
            logger.info(f"✅ CSV export: {csv_path}")
        except Exception as e:
            logger.error(f"❌ CSV export failed: {e}")
        
        # Export to Parquet (if available)
        if self.parquet_exporter:
            try:
                parquet_path = self.parquet_exporter.export(workflows, f"{base_filename}.parquet")
                results['parquet'] = parquet_path
                logger.info(f"✅ Parquet export: {parquet_path}")
            except Exception as e:
                logger.error(f"❌ Parquet export failed: {e}")
        
        # Record export
        self.export_history.append({
            'timestamp': datetime.now().isoformat(),
            'workflow_count': len(workflows),
            'formats': list(results.keys()),
            'paths': results
        })
        
        return results
    
    def export_from_database(
        self, 
        repository,
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        formats: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Export workflows directly from database.
        
        Args:
            repository: WorkflowRepository instance
            limit: Optional limit on number of workflows
            filters: Optional filters for workflow selection
            formats: Optional list of formats to export (default: all)
            
        Returns:
            Dictionary mapping format to output path
        """
        # Fetch workflows from database
        logger.info("Fetching workflows from database...")
        
        if filters:
            workflows_db = repository.search_workflows(filters, limit=limit)
        else:
            workflows_db = repository.list_workflows(limit=limit)
        
        if not workflows_db:
            logger.warning("No workflows found in database")
            return {}
        
        logger.info(f"Found {len(workflows_db)} workflows")
        
        # Convert to dictionaries
        workflows = [self._workflow_to_dict(w) for w in workflows_db]
        
        # Export to specified formats or all
        if formats:
            return self._export_selected_formats(workflows, formats)
        else:
            return self.export_all_formats(workflows)
    
    def _workflow_to_dict(self, workflow_obj) -> Dict[str, Any]:
        """
        Convert SQLAlchemy workflow object to dictionary.
        
        Args:
            workflow_obj: SQLAlchemy Workflow object
            
        Returns:
            Workflow dictionary
        """
        return {
            'workflow_id': workflow_obj.workflow_id,
            'url': workflow_obj.url,
            'processing_status': workflow_obj.processing_status,
            'quality_score': workflow_obj.quality_score,
            'processing_time': workflow_obj.processing_time,
            'metadata': self._metadata_to_dict(workflow_obj.metadata) if workflow_obj.metadata else None,
            'structure': self._structure_to_dict(workflow_obj.structure) if workflow_obj.structure else None,
            'content': self._content_to_dict(workflow_obj.content) if workflow_obj.content else None,
            'video_transcripts': [
                self._transcript_to_dict(t) for t in workflow_obj.video_transcripts
            ] if workflow_obj.video_transcripts else [],
            'created_at': workflow_obj.created_at.isoformat() if workflow_obj.created_at else None,
            'updated_at': workflow_obj.updated_at.isoformat() if workflow_obj.updated_at else None,
        }
    
    def _metadata_to_dict(self, metadata_obj) -> Dict[str, Any]:
        """Convert metadata object to dictionary."""
        return {
            'title': metadata_obj.title,
            'description': metadata_obj.description,
            'author': metadata_obj.author,
            'categories': metadata_obj.categories,
            'tags': metadata_obj.tags,
            'use_case': metadata_obj.use_case,
            'views': metadata_obj.views,
            'shares': metadata_obj.shares,
            'created_date': metadata_obj.created_date,
            'updated_date': metadata_obj.updated_date,
        }
    
    def _structure_to_dict(self, structure_obj) -> Dict[str, Any]:
        """Convert structure object to dictionary."""
        return {
            'node_count': structure_obj.node_count,
            'connection_count': structure_obj.connection_count,
            'node_types': structure_obj.node_types,
            'extraction_type': structure_obj.extraction_type,
            'fallback_used': structure_obj.fallback_used,
            'nodes': structure_obj.nodes,
            'connections': structure_obj.connections,
            'workflow_settings': structure_obj.workflow_settings,
        }
    
    def _content_to_dict(self, content_obj) -> Dict[str, Any]:
        """Convert content object to dictionary."""
        return {
            'explainer_text': content_obj.explainer_text,
            'explainer_html': content_obj.explainer_html,
            'setup_instructions': content_obj.setup_instructions,
            'use_instructions': content_obj.use_instructions,
            'has_videos': content_obj.has_videos,
            'video_count': content_obj.video_count,
            'videos': content_obj.videos,
            'has_iframes': content_obj.has_iframes,
            'iframe_count': content_obj.iframe_count,
            'iframe_sources': content_obj.iframe_sources,
        }
    
    def _transcript_to_dict(self, transcript_obj) -> Dict[str, Any]:
        """Convert transcript object to dictionary."""
        return {
            'video_url': transcript_obj.video_url,
            'video_id': transcript_obj.video_id,
            'platform': transcript_obj.platform,
            'transcript_text': transcript_obj.transcript_text,
            'transcript_language': transcript_obj.transcript_language,
            'extraction_method': transcript_obj.extraction_method,
            'duration_seconds': transcript_obj.duration_seconds,
        }
    
    def _export_selected_formats(
        self, 
        workflows: List[Dict[str, Any]], 
        formats: List[str]
    ) -> Dict[str, str]:
        """
        Export to selected formats only.
        
        Args:
            workflows: List of workflow dictionaries
            formats: List of format names ('json', 'jsonl', 'csv', 'parquet')
            
        Returns:
            Dictionary mapping format to output path
        """
        results = {}
        
        for fmt in formats:
            try:
                if fmt == 'json':
                    path = self.json_exporter.export(workflows)
                    results['json'] = path
                elif fmt == 'jsonl':
                    path = self.jsonl_exporter.export(workflows)
                    results['jsonl'] = path
                elif fmt == 'csv':
                    path = self.csv_exporter.export(workflows)
                    results['csv'] = path
                elif fmt == 'parquet':
                    if self.parquet_exporter:
                        path = self.parquet_exporter.export(workflows)
                        results['parquet'] = path
                    else:
                        logger.warning("Parquet export not available")
                else:
                    logger.warning(f"Unknown format: {fmt}")
            except Exception as e:
                logger.error(f"Export to {fmt} failed: {e}")
        
        return results
    
    def get_export_stats(self) -> Dict[str, Any]:
        """
        Get export statistics.
        
        Returns:
            Dictionary with export stats
        """
        if not self.export_history:
            return {'total_exports': 0}
        
        total_workflows = sum(e['workflow_count'] for e in self.export_history)
        
        return {
            'total_exports': len(self.export_history),
            'total_workflows_exported': total_workflows,
            'latest_export': self.export_history[-1] if self.export_history else None,
            'formats_used': list(set(
                fmt for e in self.export_history for fmt in e['formats']
            ))
        }







