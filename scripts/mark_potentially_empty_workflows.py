#!/usr/bin/env python3
"""
Mark Potentially Empty Workflows

Identifies and marks workflows that potentially don't have content:
1. Workflows without categories (54 workflows)
2. Workflows without metadata
3. Workflows that failed previous scraping attempts

Adds flags to the database:
- needs_validation: TRUE for workflows needing manual review
- validation_reason: Why this workflow needs validation

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from sqlalchemy import text

print("=" * 80)
print("🔍 IDENTIFYING POTENTIALLY EMPTY WORKFLOWS")
print("=" * 80)
print()

try:
    with get_session() as session:
        # Add validation columns if they don't exist
        print("🔧 Adding validation tracking columns...")
        try:
            session.execute(text("""
                ALTER TABLE workflows 
                ADD COLUMN IF NOT EXISTS needs_validation BOOLEAN DEFAULT FALSE
            """))
            session.execute(text("""
                ALTER TABLE workflows 
                ADD COLUMN IF NOT EXISTS validation_reason TEXT
            """))
            session.execute(text("""
                ALTER TABLE workflows 
                ADD COLUMN IF NOT EXISTS validation_priority INTEGER DEFAULT 0
            """))
            session.commit()
            print("✅ Columns added/verified")
        except Exception as e:
            print(f"⚠️  Columns might already exist: {e}")
            session.rollback()
        
        print()
        print("=" * 80)
        print("🔍 IDENTIFYING WORKFLOWS NEEDING VALIDATION")
        print("=" * 80)
        print()
        
        # Category 1: Workflows without categories (highest priority)
        print("1️⃣  Workflows WITHOUT categories...")
        result = session.execute(text("""
            UPDATE workflows w
            SET needs_validation = TRUE,
                validation_reason = 'No categories found - potential content issue',
                validation_priority = 1
            FROM workflow_metadata wm
            WHERE w.workflow_id = wm.workflow_id
              AND (wm.categories IS NULL OR wm.categories = '[]'::jsonb)
            RETURNING w.workflow_id
        """))
        
        no_category_ids = [row[0] for row in result]
        session.commit()
        
        print(f"   ✅ Marked {len(no_category_ids)} workflows")
        if no_category_ids[:10]:
            print(f"   Sample IDs: {', '.join(no_category_ids[:10])}")
        print()
        
        # Category 2: Workflows without metadata at all (high priority)
        print("2️⃣  Workflows WITHOUT metadata...")
        result = session.execute(text("""
            UPDATE workflows w
            SET needs_validation = TRUE,
                validation_reason = 'No metadata record - never scraped',
                validation_priority = 2
            WHERE NOT EXISTS (
                SELECT 1 FROM workflow_metadata wm 
                WHERE wm.workflow_id = w.workflow_id
            )
            AND needs_validation IS NOT TRUE
            RETURNING w.workflow_id
        """))
        
        no_metadata_ids = [row[0] for row in result]
        session.commit()
        
        print(f"   ✅ Marked {len(no_metadata_ids)} workflows")
        if no_metadata_ids[:10]:
            print(f"   Sample IDs: {', '.join(no_metadata_ids[:10])}")
        print()
        
        # Category 3: Workflows with very short/empty titles (medium priority)
        print("3️⃣  Workflows with EMPTY or very short titles...")
        result = session.execute(text("""
            UPDATE workflows w
            SET needs_validation = TRUE,
                validation_reason = 'Empty or very short title - potential placeholder',
                validation_priority = 3
            FROM workflow_metadata wm
            WHERE w.workflow_id = wm.workflow_id
              AND (wm.title IS NULL OR LENGTH(wm.title) < 5)
              AND needs_validation IS NOT TRUE
            RETURNING w.workflow_id
        """))
        
        short_title_ids = [row[0] for row in result]
        session.commit()
        
        print(f"   ✅ Marked {len(short_title_ids)} workflows")
        if short_title_ids[:10]:
            print(f"   Sample IDs: {', '.join(short_title_ids[:10])}")
        print()
        
        # Category 4: Workflows with error messages (medium priority)
        print("4️⃣  Workflows with ERROR messages...")
        result = session.execute(text("""
            UPDATE workflows w
            SET needs_validation = TRUE,
                validation_reason = 'Has error message from previous scraping attempt',
                validation_priority = 4
            WHERE w.error_message IS NOT NULL
              AND needs_validation IS NOT TRUE
            RETURNING w.workflow_id
        """))
        
        error_ids = [row[0] for row in result]
        session.commit()
        
        print(f"   ✅ Marked {len(error_ids)} workflows")
        if error_ids[:10]:
            print(f"   Sample IDs: {', '.join(error_ids[:10])}")
        print()
        
        print()
        print("=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)
        print()
        
        # Get overall statistics
        result = session.execute(text("""
            SELECT 
                needs_validation,
                validation_priority,
                validation_reason,
                COUNT(*) as count
            FROM workflows
            GROUP BY needs_validation, validation_priority, validation_reason
            ORDER BY needs_validation DESC NULLS LAST, validation_priority
        """))
        
        print("Workflows by validation status:")
        print()
        
        total_needs_validation = 0
        for row in result:
            needs_val = row[0]
            priority = row[1]
            reason = row[2]
            count = row[3]
            
            if needs_val:
                total_needs_validation += count
                print(f"   Priority {priority}: {count:4d} workflows")
                print(f"      Reason: {reason}")
                print()
        
        print(f"📊 TOTALS:")
        print(f"   Needs validation: {total_needs_validation}")
        print(f"   Valid workflows:  {6022 - total_needs_validation}")
        print()
        
        # Show detailed breakdown
        print("=" * 80)
        print("📋 WORKFLOWS NEEDING VALIDATION (Detailed List)")
        print("=" * 80)
        print()
        
        result = session.execute(text("""
            SELECT 
                w.workflow_id,
                w.url,
                w.validation_priority,
                w.validation_reason,
                wm.title
            FROM workflows w
            LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            WHERE w.needs_validation = TRUE
            ORDER BY w.validation_priority, w.workflow_id::integer
            LIMIT 50
        """))
        
        print("First 50 workflows needing validation:")
        print()
        
        for row in result:
            workflow_id = row[0]
            url = row[1]
            priority = row[2]
            reason = row[3]
            title = row[4] or 'No title'
            
            print(f"[P{priority}] Workflow {workflow_id}: {title}")
            print(f"     URL: {url}")
            print(f"     Reason: {reason}")
            print()
        
        print()
        print("=" * 80)
        print("🎉 MARKING COMPLETE!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Review workflows marked for validation")
        print("2. Run Playwright validation on high-priority workflows")
        print("3. Mark truly invalid workflows as deleted")
        print("4. Re-extract categories for valid workflows")
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)





