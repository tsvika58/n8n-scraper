#!/usr/bin/env python3
"""
STICKY PROGRESS MONITOR - Real sticky progress bar at terminal bottom
"""
import time
import sys
import os
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
            
            # Get completed workflows
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

def create_progress_bar(completed, total, width=30):
    """Create a progress bar"""
    if total == 0:
        return "[" + "░" * width + "]"
    
    filled = int((completed / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"

def print_sticky_progress(stats, elapsed, jerusalem_time):
    """Print sticky progress bar at bottom of terminal"""
    if stats['total'] == 0:
        return
    
    progress_pct = (stats['completed'] / stats['total']) * 100
    bar = create_progress_bar(stats['completed'], stats['total'])
    
    # Calculate ETA
    if stats['completed'] > 0 and elapsed > 0:
        rate = stats['completed'] / elapsed
        eta_seconds = stats['remaining'] / rate if rate > 0 else 0
        eta_str = format_time(eta_seconds)
    else:
        eta_str = "Calculating..."
    
    # STICKY PROGRESS BAR - This stays at bottom
    separator = "─" * 80
    progress_line = (f"🔄 {bar} {progress_pct:.0f}% ({stats['completed']}/{stats['total']}) | "
                    f"Failed: {stats['failed']} | "
                    f"Remaining: {stats['remaining']} | "
                    f"⏱️ {format_time(elapsed)} | "
                    f"ETA: {eta_str} | "
                    f"🕐 {jerusalem_time}")
    
    # Clear screen and print sticky bar
    os.system('clear')
    print(f"{separator}")
    print(progress_line)
    print(f"{separator}")

def main():
    """Main monitoring loop with sticky progress bar"""
    print("🚀 STARTING STICKY PROGRESS MONITOR")
    print("This will clear the screen and show a sticky progress bar at the bottom")
    print("Press Ctrl+C to stop")
    time.sleep(3)
    
    start_time = time.time()
    
    try:
        while True:
            stats = get_progress_stats()
            current_time = time.time()
            elapsed = current_time - start_time
            jerusalem_time = get_jerusalem_time()
            
            print_sticky_progress(stats, elapsed, jerusalem_time)
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped.")
        final_stats = get_progress_stats()
        if final_stats['total'] > 0:
            final_progress = (final_stats['completed'] / final_stats['total']) * 100
            print(f"Final Progress: {final_progress:.1f}% ({final_stats['completed']}/{final_stats['total']})")
            print(f"Failed: {final_stats['failed']}")
            print(f"Remaining: {final_stats['remaining']}")

if __name__ == "__main__":
    main()
