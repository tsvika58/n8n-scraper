#!/usr/bin/env python3
"""
Monitor Layer 1.5 Scraping Progress

Real-time monitoring of Layer 1.5 extraction progress
"""

import sys
sys.path.append('/app')

from src.storage.database import get_session
from sqlalchemy import text
import time
from datetime import datetime, timedelta
import pytz

def get_start_time():
    """Get the earliest extraction time as start time"""
    with get_session() as session:
        result = session.execute(text("""
            SELECT MIN(layer1_5_extracted_at) 
            FROM workflow_metadata
            WHERE layer1_5_extracted_at IS NOT NULL
        """)).fetchone()
        return result[0] if result and result[0] else datetime.utcnow()

def format_time(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def monitor_progress():
    """Monitor Layer 1.5 scraping progress"""
    
    print("📊 LAYER 1.5 SCRAPING PROGRESS MONITOR")
    print("=" * 70)
    print("Press Ctrl+C to stop monitoring\n")
    
    start_time = get_start_time()
    
    try:
        while True:
            with get_session() as session:
                # Get overall stats
                result = session.execute(text("""
                    SELECT 
                        COUNT(*) as total_workflows,
                        COUNT(CASE WHEN layer1_5_extracted_at IS NOT NULL THEN 1 END) as completed,
                        COUNT(CASE WHEN layer1_5_extracted_at IS NULL THEN 1 END) as remaining
                    FROM workflow_metadata
                """)).fetchone()
                
                total, completed, remaining = result
                pct = (completed / total * 100) if total > 0 else 0
                
                # Calculate times
                now = datetime.utcnow()
                elapsed_seconds = (now - start_time).total_seconds()
                elapsed_str = format_time(elapsed_seconds)
                
                # Calculate ETA
                if completed > 0 and elapsed_seconds > 0:
                    rate = completed / elapsed_seconds  # workflows per second
                    eta_seconds = remaining / rate if rate > 0 else 0
                    eta_str = format_time(eta_seconds)
                    
                    # Calculate completion time in Jerusalem timezone
                    completion_time_utc = now + timedelta(seconds=eta_seconds)
                    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
                    completion_time_jst = completion_time_utc.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
                    eta_jst = completion_time_jst.strftime('%H:%M:%S')
                else:
                    eta_str = "--:--:--"
                    eta_jst = "--:--:--"
                
                # Progress bar
                bar_length = 50
                filled = int(bar_length * completed / total) if total > 0 else 0
                bar = '█' * filled + '░' * (bar_length - filled)
                
                # Get average content length
                if completed > 0:
                    avg_result = session.execute(text("""
                        SELECT AVG((layer1_5_metadata->>'content_length')::int) as avg_length
                        FROM workflow_metadata
                        WHERE layer1_5_extracted_at IS NOT NULL
                    """)).fetchone()
                    
                    avg_length = int(avg_result[0]) if avg_result[0] else 0
                else:
                    avg_length = 0
                
                # Print progress
                print(f"\r📊 Progress: {completed}/{total} ({pct:.1f}%) [{bar}]", end='')
                print(f" | Avg: {avg_length:,} chars", end='')
                print(f"\n⏱️  Elapsed: {elapsed_str} | ETA: {eta_str} | Complete at: {eta_jst} Jerusalem", end='', flush=True)
                print("\033[F", end='')  # Move cursor up one line
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        print_final_summary()


def print_final_summary():
    """Print final summary of Layer 1.5 extraction"""
    
    with get_session() as session:
        result = session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer1_5_extracted_at IS NOT NULL THEN 1 END) as completed,
                AVG((layer1_5_metadata->>'content_length')::int) as avg_content,
                AVG((layer1_5_metadata->>'description_length')::int) as avg_desc,
                AVG((layer1_5_metadata->>'examples_count')::int) as avg_examples,
                SUM(CASE WHEN (layer1_5_metadata->>'has_examples')::boolean THEN 1 ELSE 0 END) as with_examples
            FROM workflow_metadata
            WHERE layer1_5_extracted_at IS NOT NULL
        """)).fetchone()
        
        total, completed, avg_content, avg_desc, avg_examples, with_examples = result
        
        print("\n📊 FINAL SUMMARY")
        print("=" * 70)
        print(f"✅ Completed: {completed}/{total} workflows")
        print(f"📏 Average content length: {int(avg_content or 0):,} characters")
        print(f"📝 Average description length: {int(avg_desc or 0):,} characters")
        print(f"📋 Average examples per workflow: {avg_examples or 0:.1f}")
        print(f"🎯 Workflows with examples: {with_examples or 0}")
        print("=" * 70)


if __name__ == "__main__":
    monitor_progress()

