#!/usr/bin/env python3
"""
WORKING STICKY MONITOR - Uses a different approach for sticky progress bar
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

def print_progress_summary(completed, total, failed, current_workflow, status, elapsed, jerusalem_time):
    """Print progress summary that updates in place"""
    progress_pct = (completed / total) * 100 if total > 0 else 0
    bar = create_progress_bar(completed, total)
    
    # Calculate ETA
    if completed > 0 and elapsed > 0:
        rate = completed / elapsed
        eta_seconds = (total - completed) / rate if rate > 0 else 0
        eta_str = format_time(eta_seconds)
    else:
        eta_str = "Calculating..."
    
    # Print progress summary
    print(f"\n{'='*80}")
    print(f"🔄 {bar} {progress_pct:.1f}% | Done: {completed}/{total} | Failed: {failed} | Current: {current_workflow} | {status} | ⏱️ {format_time(elapsed)} | ETA: {eta_str} | 🕐 {jerusalem_time}")
    print(f"{'='*80}")

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
    """Main scraping function with progress updates"""
    print("🚀 PRODUCTION UNIFIED WORKFLOW SCRAPING")
    print("=" * 60)
    print("Started at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Get workflows to process
    workflows = get_workflows_to_process()
    total_workflows = len(workflows)
    
    if total_workflows == 0:
        print("No workflows to process!")
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
        
        # Process workflow
        success = await scrape_workflow(workflow_id)
        
        if success:
            completed += 1
            print(f"✅ [{i}/{total_workflows}] SUCCESS: {workflow_id}")
        else:
            failed += 1
            print(f"❌ [{i}/{total_workflows}] FAILED: {workflow_id}")
        
        # Print progress summary every 5 workflows or at the end
        if i % 5 == 0 or i == total_workflows:
            print_progress_summary(
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

if __name__ == "__main__":
    asyncio.run(main())
