#!/usr/bin/env python3
"""
SCROLL WITH STICKY MONITOR - Shows terminal traffic scrolling above sticky progress bar
"""
import time
import sys
import os
import subprocess
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
            
            # Get failed workflows (those that failed extraction)
            failed_result = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = false
            """)).fetchone()
            failed = failed_result[0] if failed_result else 0
            
            # Remaining = total - completed - failed
            remaining = total_workflows - completed - failed
            
            return {
                'total': total_workflows,
                'completed': completed,
                'failed': failed,
                'remaining': remaining
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

def get_docker_logs():
    """Get recent Docker logs from the scraper"""
    try:
        result = subprocess.run([
            'docker', 'logs', '--tail', '30', 'n8n-scraper-app'
        ], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        # Filter for scraper-related logs only
        scraper_logs = []
        for line in lines:
            if 'Processing workflow' in line or 'SUCCESS:' in line or 'ERROR:' in line or 'Unified extraction' in line or 'Saving unified' in line:
                scraper_logs.append(line.strip())
        return scraper_logs[-15:] if scraper_logs else ["No scraper logs available"]
    except:
        return ["No logs available"]

def print_scroll_with_sticky(stats, elapsed, jerusalem_time, logs):
    """Print scrolling logs with sticky progress bar at bottom"""
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
    
    # Clear screen
    os.system('clear')
    
    # Print header
    print("🚀 LIVE SCRAPER MONITOR - Terminal Traffic + Sticky Progress")
    print("=" * 80)
    print()
    
    # Print recent logs (scrolling content)
    print("📋 RECENT SCRAPER LOGS:")
    print("-" * 40)
    for log_line in logs[-15:]:  # Show last 15 lines
        if log_line.strip():
            print(f"  {log_line}")
    
    print()
    print("=" * 80)
    
    # STICKY PROGRESS BAR at bottom
    separator = "─" * 80
    progress_line = (f"🔄 {bar} {progress_pct:.0f}% ({stats['completed']}/{stats['total']}) | "
                    f"Remaining: {stats['remaining']} | "
                    f"Failed: {stats['failed']} | "
                    f"⏱️ {format_time(elapsed)} | "
                    f"ETA: {eta_str} | "
                    f"🕐 {jerusalem_time}")
    
    print(f"{separator}")
    print(progress_line)
    print(f"{separator}")

def main():
    """Main monitoring loop with scrolling logs and sticky progress bar"""
    print("🚀 STARTING SCROLL WITH STICKY MONITOR")
    print("This will show terminal traffic scrolling above a sticky progress bar")
    print("Press Ctrl+C to stop")
    time.sleep(3)
    
    start_time = time.time()
    
    try:
        while True:
            stats = get_progress_stats()
            current_time = time.time()
            elapsed = current_time - start_time
            jerusalem_time = get_jerusalem_time()
            logs = get_docker_logs()
            
            print_scroll_with_sticky(stats, elapsed, jerusalem_time, logs)
            time.sleep(3)  # Update every 3 seconds
            
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
