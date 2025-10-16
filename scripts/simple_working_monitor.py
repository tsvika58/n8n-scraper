#!/usr/bin/env python3
"""
SIMPLE WORKING MONITOR - No errors, correct data
"""
import time
import os
from datetime import datetime
import pytz
from sqlalchemy import text
from src.storage.database import get_session

def get_jerusalem_time():
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    return datetime.now(jerusalem_tz).strftime('%H:%M:%S')

def get_stats():
    try:
        with get_session() as session:
            # Total workflows
            total = session.execute(text("SELECT COUNT(*) FROM workflows")).fetchone()[0]
            
            # Completed (unified_extraction_success = true)
            completed = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = true
            """)).fetchone()[0]
            
            # Failed (unified_extraction_success = false AND has error message)
            failed = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = false 
                AND error_message IS NOT NULL 
                AND error_message != ''
            """)).fetchone()[0]
            
            # Remaining (not processed yet = total - completed - failed)
            remaining = total - completed - failed
            
            return {
                'total': total,
                'completed': completed,
                'failed': failed,
                'remaining': remaining
            }
    except Exception as e:
        print(f"Error: {e}")
        return {'total': 0, 'completed': 0, 'failed': 0, 'remaining': 0}

def create_bar(completed, total, width=30):
    if total == 0:
        return "[" + "░" * width + "]"
    filled = int((completed / total) * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m"
    else:
        return f"{seconds/3600:.1f}h"

def main():
    print("🚀 SIMPLE WORKING MONITOR")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    start_time = time.time()
    
    try:
        while True:
            stats = get_stats()
            elapsed = time.time() - start_time
            jerusalem_time = get_jerusalem_time()
            
            if stats['total'] > 0:
                progress_pct = (stats['completed'] / stats['total']) * 100
                bar = create_bar(stats['completed'], stats['total'])
                
                # Calculate ETA
                if stats['completed'] > 0 and elapsed > 0:
                    rate = stats['completed'] / elapsed
                    eta_seconds = stats['remaining'] / rate if rate > 0 else 0
                    eta_str = format_time(eta_seconds)
                else:
                    eta_str = "Calculating..."
                
                # Clear and show
                os.system('clear')
                print("🚀 LIVE SCRAPER MONITOR")
                print("=" * 60)
                print()
                print("📊 PROGRESS:")
                print(f"  Total: {stats['total']}")
                print(f"  Completed: {stats['completed']}")
                print(f"  Remaining: {stats['remaining']}")
                print(f"  Failed: {stats['failed']}")
                print()
                print("⏱️ TIMING:")
                print(f"  Elapsed: {format_time(elapsed)}")
                print(f"  ETA: {eta_str}")
                print(f"  Jerusalem Time: {jerusalem_time}")
                print()
                print("📈 PROGRESS BAR:")
                print(f"  {bar} {progress_pct:.1f}%")
                print()
                print("=" * 60)
            else:
                print("No data available")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n✅ Monitor stopped.")

if __name__ == "__main__":
    main()
