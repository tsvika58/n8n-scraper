#!/usr/bin/env python3
"""
Import Complete Workflow Inventory to Supabase

Imports all 6,022 workflows from SCRAPE-002B inventory into Supabase database.
Uses UPSERT logic to preserve existing scraped workflows.

This creates the complete workflow database:
- All 6,022 workflows pre-mapped from sitemap
- Existing scraped workflows preserved
- New workflows added as pending
- Foundation for category mapping

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow
from sqlalchemy import text

print("=" * 80)
print("📦 IMPORTING COMPLETE WORKFLOW INVENTORY TO SUPABASE")
print("=" * 80)
print()

# Load the workflow URLs
inventory_file = Path(".coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt")

if not inventory_file.exists():
    print(f"❌ Inventory file not found: {inventory_file}")
    sys.exit(1)

print("📂 Loading inventory data...")
workflows = []
with open(inventory_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and '|' in line:
            # Format: "ID | URL"
            parts = line.split('|')
            if len(parts) == 2:
                workflow_id = parts[0].strip()
                url = parts[1].strip()
                
                # Extract title from URL slug
                # Format: https://n8n.io/workflows/1234-workflow-title-here
                if '/workflows/' in url:
                    slug = url.split('/workflows/')[-1].rstrip('/')
                    if '-' in slug:
                        # Remove ID prefix and convert to title
                        title_part = '-'.join(slug.split('-')[1:])
                        title = title_part.replace('-', ' ').title()
                    else:
                        title = f"Workflow {workflow_id}"
                else:
                    title = f"Workflow {workflow_id}"
                
                workflows.append({
                    'workflow_id': workflow_id,
                    'url': url,
                    'title': title
                })

print(f"✅ Loaded {len(workflows)} workflows from inventory file")
print()

# Connect to database and import
print("🔄 Connecting to Supabase database...")
print()

try:
    with get_session() as session:
        print("📊 Checking existing workflows...")
        
        # Get existing workflow IDs
        existing_workflows = session.query(Workflow.workflow_id).all()
        existing_ids = {wf.workflow_id for wf in existing_workflows}
        
        print(f"   Found {len(existing_ids)} existing workflows in database")
        print()
        
        # Statistics
        stats = {
            'total_attempted': len(workflows),
            'new_workflows': 0,
            'existing_skipped': 0,
            'errors': 0
        }
        
        print("🚀 Starting import...")
        print()
        
        # Import workflows in batches
        batch_size = 100
        for i in range(0, len(workflows), batch_size):
            batch = workflows[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(workflows) + batch_size - 1) // batch_size
            
            print(f"   Batch {batch_num}/{total_batches}: Processing {len(batch)} workflows...")
            
            for wf_data in batch:
                workflow_id = wf_data['workflow_id']
                
                try:
                    if workflow_id in existing_ids:
                        # Workflow already exists - skip
                        stats['existing_skipped'] += 1
                    else:
                        # Create new workflow
                        workflow = Workflow(
                            workflow_id=workflow_id,
                            url=wf_data['url']
                        )
                        session.add(workflow)
                        stats['new_workflows'] += 1
                        
                except Exception as e:
                    print(f"      ❌ Error importing workflow {workflow_id}: {e}")
                    stats['errors'] += 1
                    continue
            
            # Commit batch
            try:
                session.commit()
                print(f"      ✅ Batch {batch_num} committed ({stats['new_workflows']} new, {stats['existing_skipped']} existing)")
            except Exception as e:
                session.rollback()
                print(f"      ❌ Batch {batch_num} failed: {e}")
                stats['errors'] += len(batch)
        
        print()
        print("=" * 80)
        print("📊 IMPORT COMPLETE")
        print("=" * 80)
        print(f"Total workflows processed: {stats['total_attempted']}")
        print(f"New workflows added:       {stats['new_workflows']}")
        print(f"Existing workflows:        {stats['existing_skipped']}")
        print(f"Errors:                    {stats['errors']}")
        print()
        
        # Verify final count
        total_in_db = session.query(Workflow).count()
        print(f"✅ Total workflows in database: {total_in_db}")
        print()
        
        # Show sample of newly imported
        if stats['new_workflows'] > 0:
            print("📋 Sample of newly imported workflows:")
            new_samples = session.query(Workflow).filter(
                Workflow.workflow_id.in_([wf['workflow_id'] for wf in workflows[:5]])
            ).limit(5).all()
            
            for wf in new_samples:
                print(f"   • {wf.workflow_id}: {wf.url}")
        
        print()
        print("=" * 80)
        print("🎉 READY FOR CATEGORY MAPPING!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Run category discovery to extract categories from workflow pages")
        print("2. Build workflow-to-category mapping")
        print("3. Create category analytics and reporting")
        print()
        
except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ IMPORT FAILED: {e}")
    print("=" * 80)
    print()
    sys.exit(1)




