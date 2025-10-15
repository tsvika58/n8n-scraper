#!/usr/bin/env python3
"""
Live L3 Scraping Progress Monitor

This script monitors the progress of the full L3 scraping operation
with real-time updates every 5 seconds.
"""

import os
import sys
import time
from datetime import datetime, timedelta
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

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def check_process_status():
    """Check if the L3 scraping process is running."""
    import subprocess
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'layer3_enhanced_v2' in result.stdout:
            return True
        else:
            return False
    except Exception:
        return False

def get_progress_data():
    """Get current progress data from database."""
    engine = get_database_connection()
    
    with engine.connect() as connection:
        # Get overall progress
        total = connection.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
        l3_complete = connection.execute(text('SELECT COUNT(*) FROM workflows WHERE layer3_success = true')).scalar()
        l3_incomplete = total - l3_complete
        progress_pct = (l3_complete / total) * 100
        
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
        
        # Get recent completions
        recent = connection.execute(text('''
            SELECT workflow_id, layer3_extracted_at 
            FROM workflow_content 
            WHERE layer3_success = true 
            ORDER BY layer3_extracted_at DESC 
            LIMIT 3
        ''')).fetchall()
        
        return {
            'total': total,
            'l3_complete': l3_complete,
            'l3_incomplete': l3_incomplete,
            'progress_pct': progress_pct,
            'with_videos': content_stats[1],
            'with_transcripts': content_stats[0],
            'avg_transcript_length': content_stats[2],
            'recent': recent
        }

def display_progress(data, start_time):
    """Display the current progress."""
    current_time = datetime.now()
    elapsed = current_time - start_time
    
    # Calculate processing rate
    if data['l3_complete'] > 0:
        rate = data['l3_complete'] / elapsed.total_seconds() * 3600  # workflows per hour
        remaining_seconds = data['l3_incomplete'] / (data['l3_complete'] / elapsed.total_seconds()) if data['l3_complete'] > 0 else 0
        eta = current_time + timedelta(seconds=remaining_seconds)
    else:
        rate = 0
        eta = None
    
    # Create progress bar
    bar_length = 50
    filled_length = int(bar_length * data['progress_pct'] / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"🚀 L3 SCRAPING LIVE MONITOR (FRESH START) - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Process status
    if check_process_status():
        print("✅ L3 Scraping Process: RUNNING")
    else:
        print("❌ L3 Scraping Process: NOT RUNNING")
    
    print()
    
    # Progress bar
    print(f"📊 PROGRESS: {data['progress_pct']:.1f}%")
    print(f"[{bar}] {data['l3_complete']:,}/{data['total']:,}")
    print()
    
    # Statistics
    print(f"📈 STATISTICS:")
    print(f"   Total Workflows: {data['total']:,}")
    print(f"   L3 Complete: {data['l3_complete']:,}")
    print(f"   L3 Incomplete: {data['l3_incomplete']:,}")
    print(f"   With Videos: {data['with_videos']:,}")
    print(f"   With Transcripts: {data['with_transcripts']:,}")
    if data['avg_transcript_length']:
        print(f"   Avg Transcript Length: {data['avg_transcript_length']:.0f} chars")
    print()
    
    # Performance metrics
    print(f"⚡ PERFORMANCE:")
    print(f"   Elapsed Time: {str(elapsed).split('.')[0]}")
    print(f"   Processing Rate: {rate:.1f} workflows/hour")
    if eta:
        print(f"   Estimated Completion: {eta.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Recent completions
    print(f"🕒 RECENT COMPLETIONS:")
    for row in data['recent']:
        print(f"   {row[0]}: {row[1]}")
    print()
    
    print("=" * 80)
    print("Press Ctrl+C to stop monitoring")

def main():
    """Main monitoring loop."""
    print("🚀 Starting L3 Scraping Live Monitor...")
    print("Updates every 5 seconds")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    start_time = datetime.now()
    
    try:
        while True:
            clear_screen()
            
            try:
                data = get_progress_data()
                display_progress(data, start_time)
            except Exception as e:
                print(f"❌ Error getting progress data: {e}")
                print("Retrying in 5 seconds...")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        print("L3 scraping process continues in background")

if __name__ == "__main__":
    main()
