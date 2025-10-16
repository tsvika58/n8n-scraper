#!/usr/bin/env python3
"""
Simple Live Monitor - Shows real-time progress without ANSI escape codes
"""
import time
import sys
from datetime import datetime, timezone
import pytz
from sqlalchemy import text
from src.storage.database import get_session

def get_jerusalem_time():
    """Get current time in Jerusalem timezone"""
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    return datetime.now(jerusalem_tz).strftime('%H:%M:%S')

def get_progress_stats():
    """Get current progress statistics"""
    try:
        with get_session() as session:
            # Get total workflows
            total_result = session.execute(text("SELECT COUNT(*) FROM workflows")).fetchone()
            total_workflows = total_result[0] if total_result else 0
            
            # Get completed workflows (unified_extraction_success = true)
            completed_result = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = true
            """)).fetchone()
            completed = completed_result[0] if completed_result else 0
            
            # Get failed workflows
            failed_result = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = false
            """)).fetchone()
            failed = failed_result[0] if failed_result else 0
            
            return {
                'total': total_workflows,
                'completed': completed,
                'failed': failed,
                'remaining': total_workflows - completed - failed
            }
    except Exception as e:
        return {'total': 0, 'completed': 0, 'failed': 0, 'remaining': 0}

def format_time(seconds):
    """Format seconds into readable time"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m"
    else:
        return f"{seconds/3600:.1f}h"

def create_progress_bar(completed, total, width=50):
    """Create a simple text progress bar"""
    if total == 0:
        return "[" + " " * width + "]"
    
    filled = int((completed / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"

def main():
    """Main monitoring loop"""
    print("🚀 LIVE SCRAPER MONITOR - Updates every 5 seconds")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        while True:
            stats = get_progress_stats()
            current_time = time.time()
            elapsed = current_time - start_time
            
            if stats['total'] > 0:
                progress_pct = (stats['completed'] / stats['total']) * 100
                bar = create_progress_bar(stats['completed'], stats['total'])
                
                # Calculate ETA
                if stats['completed'] > 0:
                    rate = stats['completed'] / elapsed
                    eta_seconds = stats['remaining'] / rate if rate > 0 else 0
                    eta_str = format_time(eta_seconds)
                else:
                    eta_str = "Calculating..."
                
                jerusalem_time = get_jerusalem_time()
                
                print(f"\r🔄 {bar} {progress_pct:.1f}% ({stats['completed']}/{stats['total']}) | "
                      f"Failed: {stats['failed']} | "
                      f"Remaining: {stats['remaining']} | "
                      f"⏱️ {format_time(elapsed)} | "
                      f"ETA: {eta_str} | "
                      f"🕐 {jerusalem_time}", end='', flush=True)
            else:
                print(f"\r⏳ Waiting for data... | ⏱️ {format_time(elapsed)} | 🕐 {get_jerusalem_time()}", end='', flush=True)
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitor stopped. Final stats:")
        final_stats = get_progress_stats()
        if final_stats['total'] > 0:
            final_progress = (final_stats['completed'] / final_stats['total']) * 100
            print(f"   Progress: {final_progress:.1f}% ({final_stats['completed']}/{final_stats['total']})")
            print(f"   Failed: {final_stats['failed']}")
            print(f"   Remaining: {final_stats['remaining']}")

if __name__ == "__main__":
    main()
