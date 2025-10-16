#!/usr/bin/env python3
"""
L3 Scraping Progress Monitor

This script monitors the progress of the full L3 scraping operation
on all 6,022 workflows in the database.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib.parse

def get_database_connection():
    """Get database connection."""
    load_dotenv()
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    encoded_password = urllib.parse.quote_plus(db_password)
    database_url = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(database_url)

def check_progress():
    """Check L3 scraping progress."""
    engine = get_database_connection()
    
    with engine.connect() as connection:
        # Get overall progress
        total = connection.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
        l3_complete = connection.execute(text('SELECT COUNT(*) FROM workflows WHERE layer3_success = true')).scalar()
        l3_incomplete = total - l3_complete
        progress_pct = (l3_complete / total) * 100
        
        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 L3 SCRAPING PROGRESS:")
        print(f"   Total Workflows: {total:,}")
        print(f"   L3 Complete: {l3_complete:,}")
        print(f"   L3 Incomplete: {l3_incomplete:,}")
        print(f"   Progress: {progress_pct:.1f}%")
        
        # Get content statistics
        content_stats = connection.execute(text('''
            SELECT 
                COUNT(CASE WHEN transcripts IS NOT NULL AND transcripts != '{}' THEN 1 END) as with_transcripts,
                COUNT(CASE WHEN video_urls IS NOT NULL AND video_urls != '{}' THEN 1 END) as with_videos,
                AVG(CASE WHEN transcripts IS NOT NULL AND transcripts != '{}' 
                    THEN LENGTH(transcripts::text) END) as avg_transcript_length
            FROM workflow_content 
            WHERE layer3_success = true
        ''')).fetchone()
        
        print(f"\n🎬 CONTENT STATISTICS:")
        print(f"   With Videos: {content_stats[1]:,}")
        print(f"   With Transcripts: {content_stats[0]:,}")
        if content_stats[2]:
            print(f"   Avg Transcript Length: {content_stats[2]:.0f} chars")
        
        # Get recent completions
        recent = connection.execute(text('''
            SELECT workflow_id, layer3_extracted_at 
            FROM workflow_content 
            WHERE layer3_success = true 
            ORDER BY layer3_extracted_at DESC 
            LIMIT 3
        ''')).fetchall()
        
        print(f"\n🕒 Recent Completions:")
        for row in recent:
            print(f"   {row[0]}: {row[1]}")
        
        # Estimate completion time
        if l3_complete > 0:
            # Rough estimate based on current progress
            remaining = l3_incomplete
            # Assuming ~15 seconds per workflow + delays
            estimated_seconds = remaining * 20  # Conservative estimate
            estimated_hours = estimated_seconds / 3600
            
            print(f"\n⏰ ESTIMATED COMPLETION:")
            print(f"   Remaining: {remaining:,} workflows")
            print(f"   Estimated Time: {estimated_hours:.1f} hours")
        
        print("-" * 60)

def check_process_status():
    """Check if the L3 scraping process is running."""
    import subprocess
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'layer3_enhanced_v2' in result.stdout:
            print("✅ L3 Scraping Process: RUNNING")
        else:
            print("❌ L3 Scraping Process: NOT RUNNING")
    except Exception as e:
        print(f"⚠️  Could not check process status: {e}")

def main():
    """Main monitoring function."""
    print("🚀 L3 SCRAPING PROGRESS MONITOR")
    print("=" * 60)
    
    try:
        check_process_status()
        print()
        check_progress()
        
    except Exception as e:
        print(f"❌ Error monitoring progress: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

