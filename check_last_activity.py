#!/usr/bin/env python3
"""
Check last workflow activity
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.database import get_session
from sqlalchemy import text

def main():
    print("🔍 CHECKING LAST WORKFLOW ACTIVITY")
    print("="*60)
    
    with get_session() as session:
        # Check last 20 workflows
        result = session.execute(text("""
            SELECT 
                workflow_id,
                extracted_at,
                quality_score,
                error_message,
                NOW() - extracted_at as time_ago
            FROM workflows 
            ORDER BY extracted_at DESC 
            LIMIT 20;
        """))
        
        workflows = result.fetchall()
        
        print(f"\n📍 Last 20 workflows:")
        for wf in workflows:
            print(f"  ID: {wf[0]}, Time: {wf[1]}, Quality: {wf[2]}, Ago: {wf[4]}")
        
        # Check if any workflows in last 1 hour
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflows 
            WHERE extracted_at > NOW() - INTERVAL '1 hour';
        """))
        
        recent_count = result.fetchone()[0]
        print(f"\n📍 Workflows in last hour: {recent_count}")

if __name__ == "__main__":
    main()





