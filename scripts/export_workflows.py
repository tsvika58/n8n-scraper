#!/usr/bin/env python3
"""
Export Workflows Script.

Example script showing how to use the export pipeline.

Usage:
    python scripts/export_workflows.py --limit 100 --formats json,csv
    python scripts/export_workflows.py --all-formats
    python scripts/export_workflows.py --from-database

Author: RND Manager
Task: SCRAPE-012
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.exporters.export_manager import ExportManager
from src.storage.database import get_session
from src.storage.repository import WorkflowRepository


def export_from_database(
    limit: int = None, 
    formats: list = None, 
    output_dir: str = "exports"
):
    """
    Export workflows from database.
    
    Args:
        limit: Maximum number of workflows to export
        formats: List of formats to export to
        output_dir: Output directory
    """
    print(f"📦 Exporting workflows from database...")
    
    # Initialize export manager
    manager = ExportManager(output_dir)
    
    # Get database session and repository
    session = get_session()
    repository = WorkflowRepository(session)
    
    # Export from database
    results = manager.export_from_database(
        repository=repository,
        limit=limit,
        formats=formats
    )
    
    # Print results
    print(f"\n✅ Export complete!")
    print(f"\nExported files:")
    for format_name, path in results.items():
        print(f"  • {format_name.upper()}: {path}")
    
    # Get stats
    stats = manager.get_export_stats()
    print(f"\nExport statistics:")
    print(f"  • Total exports: {stats['total_exports']}")
    print(f"  • Total workflows: {stats['total_workflows_exported']}")
    print(f"  • Formats used: {', '.join(stats['formats_used'])}")


def export_sample_data(formats: list = None, output_dir: str = "exports"):
    """
    Export sample workflow data.
    
    Args:
        formats: List of formats to export to
        output_dir: Output directory
    """
    print(f"📦 Exporting sample workflow data...")
    
    # Create sample data
    sample_workflows = [
        {
            'workflow_id': 'SAMPLE-001',
            'url': 'https://n8n.io/workflows/SAMPLE-001',
            'processing_status': 'complete',
            'quality_score': 85.5,
            'processing_time': 12.3,
            'metadata': {
                'title': 'Sample Email Automation Workflow',
                'description': 'Automates email sending based on CRM triggers',
                'author': 'Sample Author',
                'categories': ['Sales', 'Marketing', 'Automation'],
                'tags': ['email', 'crm', 'automation', 'sales'],
                'use_case': 'Automated follow-up emails',
                'views': 5000,
                'shares': 250,
            },
            'structure': {
                'node_count': 8,
                'connection_count': 7,
                'node_types': ['webhook', 'httpRequest', 'email', 'if', 'code'],
                'extraction_type': 'full',
                'fallback_used': False,
            },
            'content': {
                'explainer_text': 'This workflow listens for CRM events and sends personalized follow-up emails to leads based on their engagement stage.',
                'setup_instructions': '1. Configure CRM webhook\n2. Set up email credentials\n3. Customize email templates',
                'use_instructions': '1. Trigger the workflow via webhook\n2. System will process lead data\n3. Personalized email will be sent automatically',
                'has_videos': True,
                'video_count': 1,
                'has_iframes': True,
                'iframe_count': 1,
            },
            'video_transcripts': [],
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-03-15T12:00:00',
        }
    ]
    
    # Initialize export manager
    manager = ExportManager(output_dir)
    
    # Export
    if formats:
        results = manager._export_selected_formats(sample_workflows, formats)
    else:
        results = manager.export_all_formats(sample_workflows, "sample_export")
    
    # Print results
    print(f"\n✅ Sample export complete!")
    print(f"\nExported files:")
    for format_name, path in results.items():
        print(f"  • {format_name.upper()}: {path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export workflows to various formats"
    )
    
    parser.add_argument(
        '--from-database',
        action='store_true',
        help='Export from database (default: sample data)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of workflows to export'
    )
    
    parser.add_argument(
        '--formats',
        type=str,
        default=None,
        help='Comma-separated list of formats (json,jsonl,csv,parquet)'
    )
    
    parser.add_argument(
        '--all-formats',
        action='store_true',
        help='Export to all available formats'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='exports',
        help='Output directory for exports'
    )
    
    args = parser.parse_args()
    
    # Parse formats
    formats = None
    if args.formats:
        formats = [f.strip() for f in args.formats.split(',')]
    elif not args.all_formats:
        formats = ['json', 'csv']  # Default formats
    
    # Execute export
    if args.from_database:
        export_from_database(
            limit=args.limit,
            formats=formats,
            output_dir=args.output_dir
        )
    else:
        export_sample_data(
            formats=formats,
            output_dir=args.output_dir
        )


if __name__ == "__main__":
    main()




