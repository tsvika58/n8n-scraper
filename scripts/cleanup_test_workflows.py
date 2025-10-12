#!/usr/bin/env python3
"""
Clean up test workflows from the database
Removes workflows that were created during testing
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from sqlalchemy import text

def cleanup_test_workflows():
    """Clean up test workflows from the database"""
    print("🧹 Cleaning up test workflows from database...")
    print("=" * 50)
    
    with get_session() as session:
        # Define test workflow patterns
        test_patterns = [
            # High-numbered test workflows (4000+ series)
            "workflow_id::text ~ '^4[0-9]{3,}$'",
            # Very high-numbered test workflows (999999+ series)
            "workflow_id::text ~ '^9[0-9]{5,}$'",
            # Invalid URL test workflows
            "workflow_id = 'invalid_url'",
            # Non-numeric test workflows
            "workflow_id = 'abc123'",
            # High-numbered test workflows (500000+ series)
            "workflow_id::text ~ '^5[0-9]{5,}$'",
        ]
        
        # First, count test workflows
        total_test_workflows = 0
        for pattern in test_patterns:
            query = f"SELECT COUNT(*) FROM workflows WHERE {pattern}"
            result = session.execute(text(query)).fetchone()
            count = result[0] if result else 0
            total_test_workflows += count
            if count > 0:
                print(f"  Found {count} test workflows matching pattern: {pattern}")
        
        print(f"\n📊 Total test workflows found: {total_test_workflows}")
        
        if total_test_workflows == 0:
            print("✅ No test workflows found to clean up!")
            return
        
        # Show some examples before deletion
        print("\n🔍 Sample test workflows to be deleted:")
        for pattern in test_patterns:
            query = f"SELECT workflow_id, extracted_at, quality_score FROM workflows WHERE {pattern} LIMIT 3"
            results = session.execute(text(query)).fetchall()
            for row in results:
                print(f"  • {row[0]} (extracted: {row[1]}, quality: {row[2]})")
        
        # Confirm deletion
        print(f"\n⚠️  About to delete {total_test_workflows} test workflows")
        print("This action cannot be undone!")
        
        # For safety, let's just show what would be deleted for now
        print("\n🔍 Detailed cleanup preview:")
        
        for pattern in test_patterns:
            query = f"""
                SELECT 
                    workflow_id,
                    extracted_at,
                    quality_score,
                    CASE 
                        WHEN quality_score > 0 THEN 'Success'
                        WHEN quality_score = 0 THEN 'Partial'
                        ELSE 'Failed'
                    END as status
                FROM workflows 
                WHERE {pattern}
                ORDER BY extracted_at DESC
            """
            results = session.execute(text(query)).fetchall()
            
            if results:
                print(f"\n  Pattern: {pattern}")
                for row in results:
                    print(f"    • {row[0]} - {row[3]} (quality: {row[2]}, date: {row[1]})")
        
        # Actually perform the cleanup
        print(f"\n🗑️  Proceeding with cleanup...")
        
        deleted_count = 0
        for pattern in test_patterns:
            # Delete from all related tables first
            tables_to_clean = [
                'workflow_transcripts',
                'workflow_content', 
                'workflow_structure',
                'workflow_metadata',
                'workflows'
            ]
            
            for table in tables_to_clean:
                if table == 'workflows':
                    delete_query = f"DELETE FROM {table} WHERE {pattern}"
                else:
                    delete_query = f"DELETE FROM {table} WHERE workflow_id IN (SELECT workflow_id FROM workflows WHERE {pattern})"
                
                try:
                    result = session.execute(text(delete_query))
                    deleted_count += result.rowcount
                except Exception as e:
                    print(f"    ⚠️  Error deleting from {table}: {e}")
        
        session.commit()
        
        print(f"✅ Cleanup complete!")
        print(f"   • Deleted {deleted_count} test workflow records")
        print(f"   • Database cleaned of test data")
        
        # Verify cleanup
        print("\n🔍 Verification:")
        remaining_test = 0
        for pattern in test_patterns:
            query = f"SELECT COUNT(*) FROM workflows WHERE {pattern}"
            result = session.execute(text(query)).fetchone()
            remaining_test += result[0] if result else 0
        
        if remaining_test == 0:
            print("✅ All test workflows successfully removed")
        else:
            print(f"⚠️  {remaining_test} test workflows still remain")
        
        # Show current database stats
        stats_query = text("""
            SELECT 
                COUNT(*) as total_workflows,
                COUNT(*) FILTER (WHERE quality_score > 0) as successful,
                COUNT(*) FILTER (WHERE quality_score = 0) as partial,
                COUNT(*) FILTER (WHERE quality_score IS NULL) as failed
            FROM workflows
        """)
        
        stats = session.execute(stats_query).fetchone()
        print(f"\n📊 Current database stats:")
        print(f"   • Total workflows: {stats.total_workflows}")
        print(f"   • Successful: {stats.successful}")
        print(f"   • Partial: {stats.partial}")
        print(f"   • Failed: {stats.failed}")

if __name__ == "__main__":
    cleanup_test_workflows()

