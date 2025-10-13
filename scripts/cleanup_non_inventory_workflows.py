#!/usr/bin/env python3
"""
Clean Up Non-Inventory Workflows

Deletes all workflows from the database that are NOT part of the official
6,022 workflow inventory from SCRAPE-002B.

This removes:
- Test workflows
- Invalid workflow IDs
- Accidentally created workflows
- Any workflows outside the inventory

Preserves:
- All 6,022 workflows from the official inventory
- All their associated data (metadata, structure, content, etc.)

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow

print("=" * 80)
print("🧹 CLEANING UP NON-INVENTORY WORKFLOWS")
print("=" * 80)
print()

# Load the official inventory
inventory_file = Path(".coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt")

if not inventory_file.exists():
    print(f"❌ Inventory file not found: {inventory_file}")
    sys.exit(1)

print("📂 Loading official inventory...")
official_workflow_ids = set()
with open(inventory_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and '|' in line:
            parts = line.split('|')
            if len(parts) == 2:
                workflow_id = parts[0].strip()
                official_workflow_ids.add(workflow_id)

print(f"✅ Loaded {len(official_workflow_ids)} official workflow IDs")
print()

# Connect to database
print("🔄 Connecting to Supabase database...")
print()

try:
    with get_session() as session:
        # Get all workflows from database
        print("📊 Checking database workflows...")
        all_workflows = session.query(Workflow).all()
        total_in_db = len(all_workflows)
        
        print(f"   Total workflows in database: {total_in_db}")
        print(f"   Official inventory size:     {len(official_workflow_ids)}")
        print()
        
        # Identify workflows to delete
        workflows_to_delete = []
        for workflow in all_workflows:
            if workflow.workflow_id not in official_workflow_ids:
                workflows_to_delete.append(workflow)
        
        if not workflows_to_delete:
            print("✅ Database is clean! All workflows are part of the official inventory.")
            print()
            sys.exit(0)
        
        print(f"🗑️  Found {len(workflows_to_delete)} workflows to delete:")
        print()
        
        # Show workflows to be deleted
        for wf in workflows_to_delete[:10]:
            print(f"   • {wf.workflow_id}: {wf.url}")
        
        if len(workflows_to_delete) > 10:
            print(f"   ... and {len(workflows_to_delete) - 10} more")
        
        print()
        
        # Confirm deletion
        print("⚠️  These workflows will be permanently deleted along with ALL their data:")
        print("   - workflow_metadata")
        print("   - workflow_structure")
        print("   - workflow_content")
        print("   - workflow_business_intelligence")
        print("   - workflow_community_data")
        print("   - workflow_technical_details")
        print("   - workflow_performance_analytics")
        print()
        
        # Delete workflows
        print("🗑️  Deleting workflows...")
        deleted_count = 0
        
        for workflow in workflows_to_delete:
            try:
                session.delete(workflow)
                deleted_count += 1
                
                if deleted_count % 10 == 0:
                    print(f"   Deleted {deleted_count}/{len(workflows_to_delete)} workflows...")
                    
            except Exception as e:
                print(f"   ❌ Error deleting workflow {workflow.workflow_id}: {e}")
        
        # Commit deletion
        print(f"   Committing {deleted_count} deletions...")
        session.commit()
        
        print()
        print("=" * 80)
        print("📊 CLEANUP COMPLETE")
        print("=" * 80)
        print(f"Workflows deleted:           {deleted_count}")
        print(f"Workflows remaining:         {total_in_db - deleted_count}")
        print(f"Official inventory size:     {len(official_workflow_ids)}")
        print()
        
        # Verify final state
        final_count = session.query(Workflow).count()
        print(f"✅ Final database count: {final_count}")
        
        if final_count == len(official_workflow_ids):
            print("✅ Database now matches official inventory perfectly!")
        else:
            print(f"⚠️  Database has {final_count - len(official_workflow_ids)} extra workflows")
            print("   (This is normal if some inventory workflows weren't in the database)")
        
        print()
        print("=" * 80)
        print("🎉 DATABASE CLEANUP SUCCESSFUL!")
        print("=" * 80)
        print()
        
except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ CLEANUP FAILED: {e}")
    print("=" * 80)
    print()
    sys.exit(1)


