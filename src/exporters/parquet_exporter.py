"""
Parquet Exporter.

Exports workflows in Parquet format for analytics and data science.
Columnar format optimized for query performance.

Author: RND Manager
Task: SCRAPE-012
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import json

from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)

# Parquet is optional dependency
try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    logger.warning("Parquet export unavailable: install pandas and pyarrow")


class ParquetExporter(BaseExporter):
    """Export workflows to Parquet format (columnar analytics)."""
    
    def __init__(self, output_dir: str = "exports", compression: str = "snappy"):
        """
        Initialize Parquet exporter.
        
        Args:
            output_dir: Directory for export files
            compression: Compression codec (snappy, gzip, brotli, none)
        """
        super().__init__(output_dir)
        self.compression = compression
        
        if not PARQUET_AVAILABLE:
            raise ImportError(
                "Parquet export requires pandas and pyarrow. "
                "Install with: pip install pandas pyarrow"
            )
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".parquet"
    
    def export(self, workflows: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export workflows to Parquet file.
        
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
        
        # Prepare data for DataFrame
        records = []
        for workflow in workflows:
            record = self._prepare_parquet_record(workflow)
            records.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Write to Parquet
        df.to_parquet(
            output_path,
            engine='pyarrow',
            compression=self.compression,
            index=False
        )
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def _prepare_parquet_record(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare workflow data for Parquet format.
        
        Flattens nested structures for columnar storage.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Flattened workflow record
        """
        metadata = workflow.get('metadata') or {}
        structure = workflow.get('structure') or {}
        content = workflow.get('content') or {}
        
        return {
            # Identifiers
            'workflow_id': workflow.get('workflow_id'),
            'url': workflow.get('url'),
            
            # Metadata columns
            'title': metadata.get('title'),
            'description': metadata.get('description'),
            'author': metadata.get('author'),
            'categories_json': json.dumps(metadata.get('categories', [])),
            'tags_json': json.dumps(metadata.get('tags', [])),
            'use_case': metadata.get('use_case'),
            'views': metadata.get('views', 0),
            'shares': metadata.get('shares', 0),
            'metadata_created_date': metadata.get('created_date'),
            'metadata_updated_date': metadata.get('updated_date'),
            
            # Structure columns
            'node_count': structure.get('node_count', 0),
            'connection_count': structure.get('connection_count', 0),
            'node_types_json': json.dumps(structure.get('node_types', [])),
            'extraction_type': structure.get('extraction_type'),
            'fallback_used': structure.get('fallback_used', False),
            
            # Content columns
            'explainer_text': content.get('explainer_text'),
            'setup_instructions': content.get('setup_instructions'),
            'use_instructions': content.get('use_instructions'),
            'has_videos': content.get('has_videos', False),
            'video_count': content.get('video_count', 0),
            'has_iframes': content.get('has_iframes', False),
            'iframe_count': content.get('iframe_count', 0),
            
            # Processing metadata
            'quality_score': workflow.get('quality_score', 0.0),
            'processing_status': workflow.get('processing_status'),
            'processing_time': workflow.get('processing_time', 0.0),
            'created_at': workflow.get('created_at'),
            'updated_at': workflow.get('updated_at'),
        }
    
    def export_with_schema(
        self, 
        workflows: List[Dict[str, Any]], 
        filename: Optional[str] = None
    ) -> str:
        """
        Export workflows with explicit schema definition.
        
        Provides better type safety and compression.
        
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
        
        # Prepare data
        records = [self._prepare_parquet_record(w) for w in workflows]
        df = pd.DataFrame(records)
        
        # Define explicit schema
        schema = pa.schema([
            ('workflow_id', pa.string()),
            ('url', pa.string()),
            ('title', pa.string()),
            ('description', pa.string()),
            ('author', pa.string()),
            ('categories_json', pa.string()),
            ('tags_json', pa.string()),
            ('use_case', pa.string()),
            ('views', pa.int64()),
            ('shares', pa.int64()),
            ('metadata_created_date', pa.string()),
            ('metadata_updated_date', pa.string()),
            ('node_count', pa.int32()),
            ('connection_count', pa.int32()),
            ('node_types_json', pa.string()),
            ('extraction_type', pa.string()),
            ('fallback_used', pa.bool_()),
            ('explainer_text', pa.string()),
            ('setup_instructions', pa.string()),
            ('use_instructions', pa.string()),
            ('has_videos', pa.bool_()),
            ('video_count', pa.int32()),
            ('has_iframes', pa.bool_()),
            ('iframe_count', pa.int32()),
            ('quality_score', pa.float64()),
            ('processing_status', pa.string()),
            ('processing_time', pa.float64()),
            ('created_at', pa.string()),
            ('updated_at', pa.string()),
        ])
        
        # Convert to Arrow Table with schema
        table = pa.Table.from_pandas(df, schema=schema)
        
        # Write to Parquet with schema
        pq.write_table(
            table,
            output_path,
            compression=self.compression
        )
        
        # End export
        self.end_export(output_path)
        
        return str(output_path)
    
    def export_partitioned(
        self, 
        workflows: List[Dict[str, Any]], 
        partition_col: str = 'processing_status',
        output_dirname: Optional[str] = None
    ) -> str:
        """
        Export workflows as partitioned Parquet dataset.
        
        Partitions data by specified column for efficient querying.
        
        Args:
            workflows: List of workflow dictionaries
            partition_col: Column to partition by
            output_dirname: Optional custom output directory name
            
        Returns:
            Path to partitioned dataset directory
        """
        # Validate
        if not self.validate_workflows(workflows):
            raise ValueError("Invalid workflow data")
        
        # Start export
        self.start_export(len(workflows))
        
        # Get output directory
        if output_dirname is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dirname = f"workflows_partitioned_{timestamp}"
        
        output_dir = self.output_dir / output_dirname
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare data
        records = [self._prepare_parquet_record(w) for w in workflows]
        df = pd.DataFrame(records)
        
        # Write partitioned dataset
        df.to_parquet(
            output_dir,
            engine='pyarrow',
            compression=self.compression,
            partition_cols=[partition_col],
            index=False
        )
        
        # End export (use directory path)
        self.end_export(output_dir)
        
        return str(output_dir)






