#!/usr/bin/env python3
"""
Check database for recent workflows
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.database import get_session
from sqlalchemy import text

def main():
    print("🔍 CHECKING DATABASE FOR RECENT WORKFLOWS")
    print("="*60)
    
    with get_session() as session:
        # Check recent workflows
        result = session.execute(text("""
            SELECT 
                workflow_id,
                extracted_at,
                quality_score,
                error_message,
                NOW() - extracted_at as time_ago
            FROM workflows 
            WHERE extracted_at > NOW() - INTERVAL '10 minutes'
            ORDER BY extracted_at DESC 
            LIMIT 10;
        """))
        
        recent_workflows = result.fetchall()
        
        print(f"\n📍 Found {len(recent_workflows)} recent workflows:")
        for wf in recent_workflows:
            print(f"  ID: {wf[0]}, Time: {wf[1]}, Quality: {wf[2]}, Error: {wf[3]}, Ago: {wf[4]}")
        
        # Check session stats
        result = session.execute(text("""
            SELECT 
                COUNT(*) FILTER (WHERE quality_score > 0) as session_success,
                COUNT(*) FILTER (WHERE error_message IS NOT NULL AND error_message != '') as session_failed,
                0 as session_empty,
                COUNT(*) as session_total
            FROM workflows 
            WHERE extracted_at > NOW() - INTERVAL '5 minutes';
        """))
        
        session_stats = result.fetchone()
        print(f"\n📍 Session stats (last 5 minutes):")
        print(f"  Success: {session_stats[0]}")
        print(f"  Failed: {session_stats[1]}")
        print(f"  Empty: {session_stats[2]}")
        print(f"  Total: {session_stats[3]}")
        
        # Check all workflows
        result = session.execute(text("SELECT COUNT(*) FROM workflows;"))
        total_count = result.fetchone()[0]
        print(f"\n📍 Total workflows in database: {total_count}")

if __name__ == "__main__":
    main()






