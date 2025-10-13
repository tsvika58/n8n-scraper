#!/usr/bin/env python3
"""
Import Complete 6,022 Workflow Inventory

Imports all 6,022 workflows from SCRAPE-002B inventory into the main database.
Uses UPSERT logic to preserve existing scraped workflows (58 successful).

This creates the complete workflow database:
- All 6,022 workflows pre-mapped
- Existing 58 successful scrapes preserved
- New 5,964 workflows added as pending
- Dashboard shows accurate 0.96% completion
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from sqlalchemy import text

print("=" * 80)
print("📦 IMPORTING COMPLETE WORKFLOW INVENTORY (6,022 workflows)")
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
        if line:
            # Format: "ID | URL"
            parts = line.split('|')
            if len(parts) == 2:
                workflow_id = parts[0].strip()
                url = parts[1].strip()
                workflows.append({
                    'workflow_id': workflow_id,
                    'url': url
                })

print(f"✅ Loaded {len(workflows)} workflows from inventory")
print()

# Import into database with UPSERT logic
print("💾 Importing workflows into database...")
print("   Using UPSERT logic to preserve existing scraped workflows")
print()

try:
    with get_session() as session:
        # Get current stats
        print("📊 Current database state:")
        current_total = session.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
        current_successful = session.execute(text('SELECT COUNT(*) FROM workflows WHERE quality_score > 0')).scalar()
        print(f"   Total workflows: {current_total}")
        print(f"   Successful scrapes: {current_successful}")
        print()
        
        # Insert/update workflows with UPSERT logic
        print("📥 Importing workflows...")
        inserted = 0
        skipped = 0
        batch_size = 100
        
        for i, workflow in enumerate(workflows, 1):
            workflow_id = workflow['workflow_id']
            url = workflow['url']
            
            # UPSERT: Insert if not exists, otherwise do nothing (preserve existing data)
            upsert_sql = text("""
                INSERT INTO workflows (
                    workflow_id, 
                    url, 
                    extracted_at, 
                    updated_at, 
                    processing_time, 
                    quality_score, 
                    layer1_success, 
                    layer2_success, 
                    layer3_success, 
                    error_message, 
                    retry_count
                ) VALUES (
                    :workflow_id,
                    :url,
                    NOW(),
                    NOW(),
                    NULL,
                    NULL,
                    false,
                    false,
                    false,
                    NULL,
                    0
                )
                ON CONFLICT (workflow_id) DO NOTHING
            """)
            
            result = session.execute(upsert_sql, {
                'workflow_id': workflow_id,
                'url': url
            })
            
            if result.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
            
            # Progress update every batch
            if i % batch_size == 0:
                session.commit()
                print(f"   Progress: {i}/{len(workflows)} workflows processed ({inserted} new, {skipped} existing)")
        
        # Final commit
        session.commit()
        
        print()
        print(f"✅ Import completed!")
        print(f"   New workflows added: {inserted}")
        print(f"   Existing workflows preserved: {skipped}")
        print()
        
        # Verify final state
        print("🔍 Verifying import...")
        final_total = session.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
        final_successful = session.execute(text('SELECT COUNT(*) FROM workflows WHERE quality_score > 0')).scalar()
        final_pending = session.execute(text('SELECT COUNT(*) FROM workflows WHERE quality_score IS NULL')).scalar()
        
        print()
        print("=" * 80)
        print("🎉 INVENTORY IMPORT COMPLETE!")
        print("=" * 80)
        print()
        print("📊 Final Database State:")
        print(f"   Total workflows: {final_total}")
        print(f"   ├─ Successfully scraped: {final_successful}")
        print(f"   └─ Pending (not yet scraped): {final_pending}")
        print()
        print(f"📈 Completion Progress:")
        completion_pct = (final_successful / final_total * 100) if final_total > 0 else 0
        print(f"   {final_successful} / {final_total} workflows = {completion_pct:.2f}% complete")
        print()
        print("✅ Data Integrity:")
        print(f"   • Preserved {skipped} existing scrapes (no data loss)")
        print(f"   • Added {inserted} new workflows to scrape")
        print()
        print("🎯 Next Steps:")
        print("   1. Check dashboard: http://localhost:5001")
        print(f"   2. Should show {final_successful}/{final_total} ({completion_pct:.2f}%)")
        print("   3. Start production scraping to complete remaining workflows")
        print()
        print("🚀 System ready for production scraping!")
        print("=" * 80)

except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




