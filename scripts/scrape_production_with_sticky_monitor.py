#!/usr/bin/env python3
"""
PRODUCTION SCRAPING WITH STICKY PROGRESS BAR
- Logs scroll above
- Progress bar STAYS at bottom (never moves)
- Uses ANSI escape codes for sticky behavior
"""
import asyncio
import time
import sys
import os
import shutil
from datetime import datetime, timezone
import pytz
from sqlalchemy import text
from src.storage.database import get_session
from src.scrapers.unified_workflow_extractor import extract_workflow_unified

def get_jerusalem_time():
    """Get current time in Jerusalem timezone"""
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    return datetime.now(jerusalem_tz).strftime('%H:%M:%S')

def format_time(seconds):
    """Format seconds into readable time"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m"
    else:
        return f"{seconds/3600:.1f}h"

def create_progress_bar(completed, total, width=20):
    """Create a progress bar"""
    if total == 0:
        return "[" + "░" * width + "]"
    filled = int((completed / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"

def get_terminal_height():
    """Get terminal height"""
    try:
        return shutil.get_terminal_size().lines
    except:
        return 24  # Default fallback

def setup_scrolling_region():
    """Set up scrolling region to reserve bottom lines for sticky progress bar"""
    terminal_height = get_terminal_height()
    # Set scrolling region from line 1 to line (height - 3), leaving 3 lines for progress bar
    scroll_bottom = terminal_height - 3
    sys.stdout.write(f"\033[1;{scroll_bottom}r")
    sys.stdout.flush()

def reset_scrolling_region():
    """Reset scrolling region to default"""
    sys.stdout.write("\033[r")
    sys.stdout.flush()

def print_sticky_progress(completed, total, failed, current_workflow, status, elapsed, jerusalem_time):
    """Print STICKY progress bar at terminal bottom using ANSI codes"""
    progress_pct = (completed / total) * 100 if total > 0 else 0
    bar = create_progress_bar(completed, total)
    
    # Calculate ETA
    if completed > 0 and elapsed > 0:
        rate = completed / elapsed
        eta_seconds = (total - completed) / rate if rate > 0 else 0
        eta_str = format_time(eta_seconds)
    else:
        eta_str = "Calculating..."
    
    # STICKY PROGRESS BAR - This stays at bottom using ANSI codes
    separator = "─" * 80
    progress_data = (f"🔄 {bar} {progress_pct:.1f}% | "
                    f"Done: {completed}/{total} | "
                    f"Failed: {failed} | "
                    f"Current: {current_workflow} | "
                    f"{status} | "
                    f"⏱️ {format_time(elapsed)} | "
                    f"ETA: {eta_str} | "
                    f"🕐 {jerusalem_time}")
    
    # Get terminal height and position at bottom
    terminal_height = get_terminal_height()
    bottom_line = terminal_height - 2  # Leave 2 lines for progress bar
    
    # CRITICAL: ANSI codes for sticky behavior
    # Save cursor, move to bottom, clear lines, print sticky content, restore cursor
    sys.stdout.write(f"\033[s"                    # Save current cursor position
                    f"\033[{bottom_line};0H"       # Move cursor to bottom line
                    f"\033[K"                     # Clear the entire line
                    f"{separator}\n"              # Print separator line
                    f"\033[K"                     # Clear next line
                    f"{progress_data}\n"          # Print progress data
                    f"\033[K"                     # Clear next line
                    f"{separator}"                # Print separator line
                    f"\033[u")                    # Restore cursor to saved position
    sys.stdout.flush()

def print_log_with_scroll_limit(message):
    """Print log message with scroll limit to preserve sticky banner"""
    terminal_height = get_terminal_height()
    max_scroll_line = terminal_height - 4  # Leave 4 lines for sticky banner
    
    # Print the log message
    print(message)
    
    # Check if we need to scroll up to make room
    # This is a simple approach - in practice you might want more sophisticated scrolling
    pass

def get_workflows_to_process():
    """Get workflows that need processing"""
    try:
        with get_session() as session:
            result = session.execute(text("""
                SELECT workflow_id FROM workflows 
                WHERE unified_extraction_success = false 
                ORDER BY id
            """)).fetchall()
            return [row[0] for row in result]
    except Exception as e:
        print(f"Error getting workflows: {e}")
        return []

def get_current_stats():
    """Get current progress statistics"""
    try:
        with get_session() as session:
            # Total workflows
            total = session.execute(text("SELECT COUNT(*) FROM workflows")).fetchone()[0]
            
            # Completed
            completed = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = true
            """)).fetchone()[0]
            
            # Failed (with error message)
            failed = session.execute(text("""
                SELECT COUNT(*) FROM workflows 
                WHERE unified_extraction_success = false 
                AND error_message IS NOT NULL 
                AND error_message != ''
            """)).fetchone()[0]
            
            return total, completed, failed
    except Exception as e:
        print(f"Error getting stats: {e}")
        return 0, 0, 0

async def scrape_workflow(workflow_id):
    """Scrape a single workflow"""
    try:
        url = f"https://n8n.io/workflows/{workflow_id}"
        print(f"🔍 Unified extraction for workflow {workflow_id}")
        print(f"   URL: {url}")
        
        # Extract workflow data (this automatically saves to database)
        result = await extract_workflow_unified(workflow_id, url, headless=True, save_to_db=True)
        
        if result and result.get('success'):
            data = result.get('data', {})
            print(f"✅ Successfully extracted workflow {workflow_id}")
            print(f"   📊 Nodes: {data.get('nodes_count', 0)}")
            print(f"   📝 Contexts: {data.get('contexts_count', 0)}")
            print(f"   🎬 Videos: {data.get('videos_count', 0)}")
            print(f"   📜 Transcripts: {data.get('transcripts_count', 0)}")
            print(f"✅ Successfully saved unified data for {workflow_id}")
            
            return True
        else:
            print(f"❌ Failed to extract workflow {workflow_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing workflow {workflow_id}: {e}")
        return False

async def main():
    """Main scraping function with sticky progress bar"""
    # Set up scrolling region to reserve bottom lines for sticky progress bar
    setup_scrolling_region()
    
    print("🚀 PRODUCTION UNIFIED WORKFLOW SCRAPING")
    print("=" * 60)
    print("Started at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Get workflows to process
    workflows = get_workflows_to_process()
    total_workflows = len(workflows)
    
    if total_workflows == 0:
        print("No workflows to process!")
        reset_scrolling_region()
        return
    
    print(f"Found {total_workflows} workflows to process")
    print()
    
    start_time = time.time()
    completed = 0
    failed = 0
    
    # Process workflows
    for i, workflow_id in enumerate(workflows, 1):
        current_time = time.time()
        elapsed = current_time - start_time
        jerusalem_time = get_jerusalem_time()
        
        # Print sticky progress bar
        print_sticky_progress(
            completed=completed,
            total=total_workflows,
            failed=failed,
            current_workflow=workflow_id,
            status="Extracting...",
            elapsed=elapsed,
            jerusalem_time=jerusalem_time
        )
        
        # Process workflow
        success = await scrape_workflow(workflow_id)
        
        if success:
            completed += 1
            print(f"✅ [{i}/{total_workflows}] SUCCESS: {workflow_id}")
        else:
            failed += 1
            print(f"❌ [{i}/{total_workflows}] FAILED: {workflow_id}")
        
        # Update sticky progress after each workflow
        print_sticky_progress(
            completed=completed,
            total=total_workflows,
            failed=failed,
            current_workflow=workflow_id,
            status="Completed" if success else "Failed",
            elapsed=elapsed,
            jerusalem_time=jerusalem_time
        )
        
        # Small delay between workflows
        await asyncio.sleep(0.1)
    
    # Final stats
    total_time = time.time() - start_time
    print()
    print("=" * 60)
    print("🎉 SCRAPING COMPLETED!")
    print(f"Total workflows: {total_workflows}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Total time: {format_time(total_time)}")
    print(f"Average time per workflow: {format_time(total_time / total_workflows)}")
    print("=" * 60)
    
    # Reset scrolling region
    reset_scrolling_region()

if __name__ == "__main__":
    asyncio.run(main())