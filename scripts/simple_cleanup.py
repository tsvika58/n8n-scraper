#!/usr/bin/env python3
"""
Simple cleanup script for test workflows
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from sqlalchemy import text

def simple_cleanup():
    """Simple cleanup of test workflows"""
    print("🧹 Simple test workflow cleanup...")
    
    with get_session() as session:
        try:
            # Get the actual table names first
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'workflow%'
                ORDER BY table_name
            """)
            
            tables = session.execute(tables_query).fetchall()
            print(f"Found tables: {[t[0] for t in tables]}")
            
            # Define test workflow IDs to delete
            test_workflow_ids = [
                '4001', '4002', '4003', '4004', '4005', '4006', '4007', '4008', '4009', '4010',
                '4011', '4012', '4013', '4014', '4015', '999999', '9999999', 'invalid_url', 
                'abc123', '500000'
            ]
            
            # Delete from each table
            for table_name in [t[0] for t in tables]:
                if table_name == 'workflows':
                    # Delete from main workflows table
                    delete_query = text("DELETE FROM workflows WHERE workflow_id = ANY(:ids)")
                    result = session.execute(delete_query, {'ids': test_workflow_ids})
                    print(f"Deleted {result.rowcount} records from {table_name}")
                else:
                    # Delete from related tables
                    delete_query = text(f"DELETE FROM {table_name} WHERE workflow_id = ANY(:ids)")
                    result = session.execute(delete_query, {'ids': test_workflow_ids})
                    print(f"Deleted {result.rowcount} records from {table_name}")
            
            session.commit()
            print("✅ Cleanup completed successfully!")
            
            # Verify cleanup
            remaining_query = text("""
                SELECT COUNT(*) FROM workflows 
                WHERE workflow_id = ANY(:ids)
            """)
            remaining = session.execute(remaining_query, {'ids': test_workflow_ids}).fetchone()[0]
            
            if remaining == 0:
                print("✅ All test workflows successfully removed")
            else:
                print(f"⚠️  {remaining} test workflows still remain")
            
            # Show final stats
            stats_query = text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE quality_score > 0) as successful,
                    COUNT(*) FILTER (WHERE quality_score = 0) as partial
                FROM workflows
            """)
            
            stats = session.execute(stats_query).fetchone()
            print(f"\n📊 Final database stats:")
            print(f"   • Total workflows: {stats.total}")
            print(f"   • Successful: {stats.successful}")
            print(f"   • Partial: {stats.partial}")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    simple_cleanup()






