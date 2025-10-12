#!/usr/bin/env python3
"""
Import Phase 1 Results to Database

This script imports the metadata and value scores from Phase 1 smart filtering
results into the database, updating workflow_metadata table.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text


async def import_phase1_results(results_file: str):
    """Import Phase 1 results into database"""
    print("🔄 IMPORTING PHASE 1 RESULTS TO DATABASE")
    print("=" * 60)
    
    # Load results
    print(f"📂 Loading results from: {results_file}")
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    print(f"📊 Found {len(results)} workflows to import")
    
    successful = 0
    failed = 0
    updated = 0
    created = 0
    
    with get_session() as session:
        for result in results:
            try:
                workflow_id = result['workflow_id']
                
                if not result.get('success'):
                    print(f"   ⏭️  Skipping {workflow_id} (extraction failed)")
                    failed += 1
                    continue
                
                # Get workflow
                workflow = session.query(Workflow).filter(
                    Workflow.workflow_id == workflow_id
                ).first()
                
                if not workflow:
                    print(f"   ⚠️  Workflow {workflow_id} not found in database")
                    continue
                
                # Extract Layer 1 data
                layer1_data = result.get('layers', {}).get('layer1', {}).get('data', {})
                if not layer1_data:
                    print(f"   ⚠️  No Layer 1 data for {workflow_id}")
                    continue
                
                # Check if metadata exists
                metadata = session.query(WorkflowMetadata).filter(
                    WorkflowMetadata.workflow_id == workflow_id
                ).first()
                
                if metadata:
                    # Update existing metadata
                    metadata.title = layer1_data.get('title')
                    metadata.description = layer1_data.get('description')
                    metadata.use_case = layer1_data.get('use_case')
                    
                    # Handle author (could be dict or string)
                    author = layer1_data.get('author', {})
                    if isinstance(author, dict):
                        metadata.author_name = author.get('name')
                        metadata.author_url = author.get('url')
                    elif isinstance(author, str):
                        metadata.author_name = author
                        metadata.author_url = None
                    
                    metadata.views = layer1_data.get('views')
                    metadata.shares = layer1_data.get('shares')
                    
                    # Extract categories and tags
                    categories = layer1_data.get('general_tags', [])
                    if isinstance(categories, list):
                        metadata.categories = categories
                    
                    metadata.workflow_created_at = layer1_data.get('created_at')
                    metadata.workflow_updated_at = layer1_data.get('updated_at')
                    
                    # Store raw metadata
                    metadata.raw_metadata = layer1_data
                    
                    updated += 1
                    action = "📝 Updated"
                else:
                    # Create new metadata
                    # Handle author (could be dict or string)
                    author = layer1_data.get('author', {})
                    if isinstance(author, dict):
                        author_name = author.get('name')
                        author_url = author.get('url')
                    elif isinstance(author, str):
                        author_name = author
                        author_url = None
                    else:
                        author_name = None
                        author_url = None
                    
                    metadata = WorkflowMetadata(
                        workflow_id=workflow_id,
                        title=layer1_data.get('title'),
                        description=layer1_data.get('description'),
                        use_case=layer1_data.get('use_case'),
                        author_name=author_name,
                        author_url=author_url,
                        views=layer1_data.get('views'),
                        shares=layer1_data.get('shares'),
                        categories=layer1_data.get('general_tags', []) if isinstance(layer1_data.get('general_tags'), list) else [],
                        workflow_created_at=layer1_data.get('created_at'),
                        workflow_updated_at=layer1_data.get('updated_at'),
                        raw_metadata=layer1_data
                    )
                    session.add(metadata)
                    created += 1
                    action = "✅ Created"
                
                # Get value score
                value_score = result.get('value_score', {})
                title = layer1_data.get('title', 'Unknown')[:40]
                score = value_score.get('total_score', 0)
                
                print(f"   {action} {workflow_id}: {title} (Score: {score:.1f})")
                
                successful += 1
                
                # Commit every 10 workflows
                if successful % 10 == 0:
                    session.commit()
                    
            except Exception as e:
                print(f"   ❌ Error importing {result.get('workflow_id', 'unknown')}: {e}")
                session.rollback()
                failed += 1
                continue
        
        # Final commit
        session.commit()
    
    print("\n" + "=" * 60)
    print("📊 IMPORT SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully imported: {successful}")
    print(f"   • Created new metadata: {created}")
    print(f"   • Updated existing metadata: {updated}")
    print(f"❌ Failed: {failed}")
    print("=" * 60)


def main():
    """Main entry point"""
    # Find the most recent results file
    results_files = sorted(Path('/app').glob('smart_filtering_phase1_results_*.json'))
    
    if not results_files:
        print("❌ No Phase 1 results files found!")
        sys.exit(1)
    
    latest_file = results_files[-1]
    print(f"\n📁 Using latest results file: {latest_file.name}\n")
    
    asyncio.run(import_phase1_results(str(latest_file)))


if __name__ == "__main__":
    main()
