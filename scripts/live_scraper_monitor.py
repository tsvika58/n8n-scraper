#!/usr/bin/env python3
"""
Live Scraper Monitor - Real-time Status Display

Shows live status of the L3 scraper with:
- Real-time progress updates
- Live log streaming
- Process health monitoring
- Database connection status
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
import urllib.parse

# Add paths
sys.path.append('../n8n-shared')

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_database_connection():
    """Get database connection for monitoring."""
    load_dotenv()
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    encoded_password = urllib.parse.quote_plus(db_password)
    database_url = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
    return database_url

def get_progress_data():
    """Get current progress from database."""
    try:
        from sqlalchemy import create_engine, text
        database_url = get_database_connection()
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Get overall progress
            total = connection.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
            l3_complete = connection.execute(text('SELECT COUNT(*) FROM workflows WHERE layer3_success = true')).scalar()
            l3_incomplete = total - l3_complete
            progress_pct = (l3_complete / total) * 100 if total > 0 else 0
            
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
                'with_videos': content_stats[1] or 0,
                'with_transcripts': content_stats[0] or 0,
                'avg_transcript_length': content_stats[2] or 0,
                'recent': recent
            }
    except Exception as e:
        return {
            'total': 0,
            'l3_complete': 0,
            'l3_incomplete': 0,
            'progress_pct': 0,
            'with_videos': 0,
            'with_transcripts': 0,
            'avg_transcript_length': 0,
            'recent': []
        }

def check_process_status():
    """Check if scraper process is running."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'layer3_enhanced_v2' in result.stdout
    except:
        return False

def display_status(data, start_time):
    """Display the current status."""
    current_time = datetime.now()
    elapsed = current_time - start_time
    
    # Calculate processing rate
    if data['l3_complete'] > 0 and elapsed.total_seconds() > 0:
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
    
    print(f"🚀 L3 SCRAPER LIVE MONITOR - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Process status
    if check_process_status():
        print("✅ L3 Scraper Process: RUNNING")
    else:
        print("❌ L3 Scraper Process: NOT RUNNING")
    
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
    if data['avg_transcript_length'] > 0:
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

def stream_logs():
    """Stream live logs from the scraper."""
    log_file = "l3_scraping_live.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                # Go to end of file
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(f"📝 {line.strip()}")
                    else:
                        time.sleep(0.1)
        except:
            pass

def main():
    """Main monitoring loop."""
    print("🚀 Starting L3 Scraper Live Monitor...")
    print("Updates every 5 seconds")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    start_time = datetime.now()
    
    try:
        while True:
            clear_screen()
            
            try:
                data = get_progress_data()
                display_status(data, start_time)
            except Exception as e:
                print(f"❌ Error getting progress data: {e}")
                print("Retrying in 5 seconds...")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        print("L3 scraping process continues in background")

if __name__ == "__main__":
    main()