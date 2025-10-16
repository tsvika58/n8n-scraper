#!/usr/bin/env python3
"""
FIXED MONITOR - Correct progress calculation and real-time logs
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
            
            # Get completed workflows (success = true)
            completed_result = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = true
            """)).fetchone()
            completed = completed_result[0] if completed_result else 0
            
            # Get actually failed workflows (success = false AND has error)
            failed_result = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = false 
                AND (unified_extraction_error IS NOT NULL OR unified_extraction_error != '')
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
        print(f"Database error: {e}")
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

def get_scraper_logs():
    """Get real-time scraper logs"""
    try:
        # Get logs from the running scraper process
        result = subprocess.run([
            'docker', 'exec', 'n8n-scraper-app', 'tail', '-n', '20', '/proc/1/fd/1'
        ], capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            # Filter for important scraper messages
            scraper_logs = []
            for line in lines:
                if any(keyword in line for keyword in [
                    'Processing workflow', 'SUCCESS:', 'ERROR:', 'Unified extraction', 
                    'Saving unified', 'workflow', 'nodes', 'videos', 'transcripts'
                ]):
                    # Clean up the line
                    clean_line = line.strip()
                    if clean_line and len(clean_line) > 10:
                        scraper_logs.append(clean_line)
            return scraper_logs[-10:] if scraper_logs else ["No recent scraper activity"]
        else:
            return ["Cannot access scraper logs"]
    except Exception as e:
        return [f"Log error: {str(e)[:50]}"]

def print_monitor(stats, elapsed, jerusalem_time, logs):
    """Print the monitor with scrolling logs and sticky progress"""
    if stats['total'] == 0:
        print("No data available")
        return
    
    progress_pct = (stats['completed'] / stats['total']) * 100
    bar = create_progress_bar(stats['completed'], stats['total'])
    
    # Calculate ETA
    if stats['completed'] > 0 and elapsed > 0:
        rate = stats['completed'] / elapsed  # workflows per second
        eta_seconds = stats['remaining'] / rate if rate > 0 else 0
        eta_str = format_time(eta_seconds)
    else:
        eta_str = "Calculating..."
    
    # Clear screen
    os.system('clear')
    
    # Header
    print("🚀 LIVE SCRAPER MONITOR - Real-time Progress")
    print("=" * 80)
    print()
    
    # Recent logs (scrolling content)
    print("📋 RECENT SCRAPER ACTIVITY:")
    print("-" * 50)
    for i, log_line in enumerate(logs[-8:], 1):  # Show last 8 lines
        print(f"  {i:2d}. {log_line}")
    
    print()
    print("=" * 80)
    
    # STICKY PROGRESS BAR at bottom
    separator = "─" * 80
    progress_line = (f"🔄 {bar} {progress_pct:.1f}% ({stats['completed']}/{stats['total']}) | "
                    f"Remaining: {stats['remaining']} | "
                    f"Failed: {stats['failed']} | "
                    f"⏱️ {format_time(elapsed)} | "
                    f"ETA: {eta_str} | "
                    f"🕐 {jerusalem_time}")
    
    print(f"{separator}")
    print(progress_line)
    print(f"{separator}")

def main():
    """Main monitoring loop"""
    print("🚀 STARTING FIXED MONITOR")
    print("This will show correct progress and real-time logs")
    print("Press Ctrl+C to stop")
    time.sleep(2)
    
    start_time = time.time()
    
    try:
        while True:
            stats = get_progress_stats()
            current_time = time.time()
            elapsed = current_time - start_time
            jerusalem_time = get_jerusalem_time()
            logs = get_scraper_logs()
            
            print_monitor(stats, elapsed, jerusalem_time, logs)
            time.sleep(3)  # Update every 3 seconds
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped.")
        final_stats = get_progress_stats()
        if final_stats['total'] > 0:
            final_progress = (final_stats['completed'] / final_stats['total']) * 100
            print(f"Final Progress: {final_progress:.1f}% ({final_stats['completed']}/{final_stats['total']})")
            print(f"Remaining: {final_stats['remaining']}")
            print(f"Failed: {final_stats['failed']}")

if __name__ == "__main__":
    main()
