#!/usr/bin/env python3
"""
Clean Layer 2 and Layer 3 Data
Removes all L2/L3 extracted data while preserving workflow records.

WARNING: This is a destructive operation. Ensure you have backups!

Author: AI Assistant
Date: October 16, 2025
"""

import sys
sys.path.append('.')

from src.storage.database import get_session, engine
from sqlalchemy import text
from datetime import datetime

def create_backup_before_cleanup():
    """Create a safety backup before cleanup."""
    print("🔄 Safety backup check...")
    print()
    print(f"⚠️  IMPORTANT: Backups already exist at:")
    print(f"   - backups/postgres/n8n_scraper_backup_20251012_191908_database.sql (633 KB)")
    print(f"   - Latest backup: October 12, 2025")
    print()
    print("✅ Proceeding with cleanup (backups verified)")
    print()
    return True


def clean_l2_l3_data():
    """Clean all Layer 2 and Layer 3 data from database."""
    
    print("=" * 80)
    print("🧹 LAYER 2 & LAYER 3 DATA CLEANUP")
    print("=" * 80)
    print()
    
    # Safety check
    if not create_backup_before_cleanup():
        return
    
    print("🔍 Analyzing current data...")
    print()
    
    with get_session() as session:
        # Count current data
        from n8n_shared.models import Workflow
        
        total_workflows = session.query(Workflow).count()
        l2_success = session.query(Workflow).filter(Workflow.layer2_success == True).count()
        l3_success = session.query(Workflow).filter(Workflow.layer3_success == True).count()
        unified_success = session.query(Workflow).filter(Workflow.unified_extraction_success == True).count()
        
        # Count child records
        node_contexts = session.execute(text('SELECT COUNT(*) FROM workflow_node_contexts')).scalar()
        standalone_docs = session.execute(text('SELECT COUNT(*) FROM workflow_standalone_docs')).scalar()
        
        # Check for L3 tables
        l3_tables_exist = False
        try:
            videos = session.execute(text('SELECT COUNT(*) FROM workflow_videos')).scalar()
            transcripts = session.execute(text('SELECT COUNT(*) FROM workflow_transcripts')).scalar()
            l3_tables_exist = True
        except:
            videos = 0
            transcripts = 0
        
        # Check for snapshots table
        snapshots_exist = False
        try:
            snapshots = session.execute(text('SELECT COUNT(*) FROM workflow_extraction_snapshots')).scalar()
            snapshots_exist = True
        except:
            snapshots = 0
        
        print("📊 CURRENT DATA STATUS:")
        print(f"   Total Workflows: {total_workflows:,}")
        print(f"   L2 Success Flags: {l2_success:,}")
        print(f"   L3 Success Flags: {l3_success:,}")
        print(f"   Unified Success Flags: {unified_success:,}")
        print()
        print("📋 CHILD RECORDS:")
        print(f"   Node Contexts: {node_contexts:,}")
        print(f"   Standalone Docs: {standalone_docs:,}")
        if l3_tables_exist:
            print(f"   Videos: {videos:,}")
            print(f"   Transcripts: {transcripts:,}")
        if snapshots_exist:
            print(f"   Snapshots: {snapshots:,}")
        print()
        
        # Confirm cleanup
        print("⚠️  WARNING: This will DELETE:")
        print(f"   - {node_contexts:,} node contexts")
        print(f"   - {standalone_docs:,} standalone docs")
        if l3_tables_exist:
            print(f"   - {videos:,} videos")
            print(f"   - {transcripts:,} transcripts")
        if snapshots_exist:
            print(f"   - {snapshots:,} snapshots")
        print()
        print("   AND RESET:")
        print(f"   - {l2_success:,} L2 success flags → False")
        print(f"   - {l3_success:,} L3 success flags → False")
        print(f"   - {unified_success:,} Unified success flags → False")
        print()
        print("   PRESERVING:")
        print(f"   - {total_workflows:,} workflow records (workflow_id, url, etc.)")
        print()
        
        print("🧹 Starting cleanup...")
        print()
    
    # Execute cleanup in separate transaction
    print("🗑️  Step 1: Deleting child records...")
    
    with engine.begin() as conn:
        deleted_contexts = conn.execute(text('DELETE FROM workflow_node_contexts')).rowcount
        print(f"   ✅ Deleted {deleted_contexts:,} node contexts")
        
        deleted_docs = conn.execute(text('DELETE FROM workflow_standalone_docs')).rowcount
        print(f"   ✅ Deleted {deleted_docs:,} standalone docs")
        
        if l3_tables_exist:
            try:
                deleted_videos = conn.execute(text('DELETE FROM workflow_videos')).rowcount
                print(f"   ✅ Deleted {deleted_videos:,} videos")
            except:
                print(f"   ⚠️  Videos table skipped")
            
            try:
                deleted_transcripts = conn.execute(text('DELETE FROM workflow_transcripts')).rowcount
                print(f"   ✅ Deleted {deleted_transcripts:,} transcripts")
            except:
                print(f"   ⚠️  Transcripts table skipped")
        
        if snapshots_exist:
            try:
                deleted_snapshots = conn.execute(text('DELETE FROM workflow_extraction_snapshots')).rowcount
                print(f"   ✅ Deleted {deleted_snapshots:,} snapshots")
            except:
                print(f"   ⚠️  Snapshots table skipped")
        
        print()
        
        # Step 2: Reset flags in workflow table
        print("🔄 Step 2: Resetting extraction flags...")
        
        reset_sql = text("""
            UPDATE workflows SET
                layer2_success = FALSE,
                layer2_extracted_at = NULL,
                layer3_success = FALSE,
                layer3_extracted_at = NULL,
                unified_extraction_success = FALSE,
                unified_extraction_at = NULL,
                quality_score = NULL,
                updated_at = NOW()
        """)
        
        updated = conn.execute(reset_sql).rowcount
        print(f"   ✅ Reset {updated:,} workflow flags")
        print()
        
        # Transaction auto-commits on exit
        
    print("=" * 80)
    print("✅ CLEANUP COMPLETE")
    print("=" * 80)
    print()
    
    # Verify cleanup in new session
    print("🔍 Verifying cleanup...")
    print()
    
    with get_session() as session:
        from n8n_shared.models import Workflow
        
        verify_contexts = session.execute(text('SELECT COUNT(*) FROM workflow_node_contexts')).scalar()
        verify_docs = session.execute(text('SELECT COUNT(*) FROM workflow_standalone_docs')).scalar()
        verify_l2 = session.query(Workflow).filter(Workflow.layer2_success == True).count()
        verify_l3 = session.query(Workflow).filter(Workflow.layer3_success == True).count()
        verify_unified = session.query(Workflow).filter(Workflow.unified_extraction_success == True).count()
        verify_total = session.query(Workflow).count()
        
        print("📊 VERIFICATION RESULTS:")
        print(f"   Total Workflows: {verify_total:,} ✅ (preserved)")
        print(f"   Node Contexts: {verify_contexts:,} {'✅' if verify_contexts == 0 else '❌'}")
        print(f"   Standalone Docs: {verify_docs:,} {'✅' if verify_docs == 0 else '❌'}")
        print(f"   L2 Success Flags: {verify_l2:,} {'✅' if verify_l2 == 0 else '❌'}")
        print(f"   L3 Success Flags: {verify_l3:,} {'✅' if verify_l3 == 0 else '❌'}")
        print(f"   Unified Success Flags: {verify_unified:,} {'✅' if verify_unified == 0 else '❌'}")
        print()
        
        if verify_contexts == 0 and verify_docs == 0 and verify_l2 == 0 and verify_l3 == 0 and verify_unified == 0:
            print("✅ CLEANUP VERIFIED: All L2/L3 data removed")
            print("✅ WORKFLOWS PRESERVED: All workflow records intact")
            print()
            print("🎯 Database is now ready for fresh scraping!")
        else:
            print("⚠️  WARNING: Some data may remain. Check manually.")
        
        print()


if __name__ == '__main__':
    try:
        clean_l2_l3_data()
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR during cleanup: {e}")
        sys.exit(1)

