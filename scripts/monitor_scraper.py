#!/usr/bin/env python3
"""
Standalone Scraper Monitor

This script monitors scraper progress by reading a shared state file.
It runs independently of the scraper process and works in any terminal.

Usage:
    # Watch mode (updates every 2 seconds)
    python scripts/monitor_scraper.py --watch
    
    # Single snapshot
    python scripts/monitor_scraper.py
    
    # Custom refresh interval
    python scripts/monitor_scraper.py --watch --interval 5

Author: AI Assistant
Date: October 16, 2025
"""

import sys
import time
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring import (
    ProgressTracker,
    format_time,
    format_progress_bar,
    get_jerusalem_time
)


def print_progress(progress, clear_screen=True):
    """
    Print progress in a clean, readable format.
    
    Args:
        progress: ScraperProgress object
        clear_screen: Whether to clear screen before printing
    """
    if clear_screen:
        # Use simple clear that works everywhere
        print("\033[2J\033[H", end='')
    
    # Header
    print("=" * 80)
    print(f"  N8N WORKFLOW SCRAPER - MONITORING DASHBOARD".center(80))
    print("=" * 80)
    print()
    
    # Scraper info
    print(f"📋 Scraper ID: {progress.scraper_id}")
    print(f"🕐 Jerusalem Time: {get_jerusalem_time()}")
    print(f"⏱️  Elapsed: {format_time(progress.elapsed_seconds)}")
    print()
    
    # Progress bar
    bar = format_progress_bar(progress.completed + progress.failed, progress.total_workflows)
    print(f"Progress: {bar} {progress.progress_percent:.2f}%")
    print()
    
    # Statistics
    print(f"📊 STATISTICS:")
    print(f"   Total Workflows:  {progress.total_workflows:,}")
    print(f"   ✅ Completed:     {progress.completed:,}")
    print(f"   ❌ Failed:        {progress.failed:,}")
    print(f"   ⏳ Remaining:     {progress.total_workflows - progress.completed - progress.failed:,}")
    print(f"   📈 Success Rate:  {progress.success_rate:.2f}%")
    print()
    
    # Current status
    print(f"🔄 CURRENT STATUS:")
    print(f"   Workflow: {progress.current_workflow_id or 'N/A'}")
    print(f"   Status:   {progress.current_status}")
    print()
    
    # ETA
    if progress.eta_seconds:
        print(f"⏰ ESTIMATED TIME:")
        print(f"   ETA: {format_time(progress.eta_seconds)}")
        
        # Calculate completion time
        completion_timestamp = time.time() + progress.eta_seconds
        completion_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(completion_timestamp))
        print(f"   Completion: {completion_time}")
    else:
        print(f"⏰ ESTIMATED TIME: Calculating...")
    print()
    
    # Recent errors (if any)
    if progress.errors:
        recent_errors = progress.errors[-5:]  # Last 5 errors
        print(f"⚠️  RECENT ERRORS ({len(progress.errors)} total):")
        for error in recent_errors:
            workflow_id = error.get('workflow_id', 'N/A')
            error_msg = error.get('error', 'Unknown error')
            # Truncate long error messages
            if len(error_msg) > 60:
                error_msg = error_msg[:57] + "..."
            print(f"   • WF {workflow_id}: {error_msg}")
        print()
    
    # Footer
    print("=" * 80)
    
    # Check if scraper is alive
    time_since_update = time.time() - progress.last_update
    if time_since_update > 120:  # 2 minutes
        print(f"⚠️  WARNING: No update for {format_time(time_since_update)} - scraper may have stopped")
    else:
        print(f"✅ Scraper active (last update {format_time(time_since_update)} ago)")
    
    print("=" * 80)


def print_no_scraper():
    """Print message when no scraper is running"""
    print("\033[2J\033[H", end='')
    print("=" * 80)
    print(f"  N8N WORKFLOW SCRAPER - MONITORING DASHBOARD".center(80))
    print("=" * 80)
    print()
    print("❌ No scraper is currently running")
    print()
    print("To start a scraper, run:")
    print("   docker exec n8n-scraper-app python scripts/scrape_production_unified.py")
    print()
    print("=" * 80)


def watch_mode(interval: int = 2):
    """
    Continuously monitor scraper progress.
    
    Args:
        interval: Refresh interval in seconds
    """
    print("Starting monitor in watch mode...")
    print(f"Refresh interval: {interval}s")
    print("Press Ctrl+C to exit")
    print()
    time.sleep(1)
    
    try:
        while True:
            progress = ProgressTracker.read_state()
            
            if progress:
                print_progress(progress, clear_screen=True)
            else:
                print_no_scraper()
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor n8n scraper progress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch mode (default 2s refresh)
  python scripts/monitor_scraper.py --watch
  
  # Watch with 5 second refresh
  python scripts/monitor_scraper.py --watch --interval 5
  
  # Single snapshot
  python scripts/monitor_scraper.py
        """
    )
    
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Continuously monitor (refresh every N seconds)'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=2,
        help='Refresh interval in seconds (default: 2)'
    )
    
    args = parser.parse_args()
    
    if args.watch:
        watch_mode(args.interval)
    else:
        # Single snapshot
        progress = ProgressTracker.read_state()
        
        if progress:
            print_progress(progress, clear_screen=False)
        else:
            print_no_scraper()


if __name__ == '__main__':
    main()

