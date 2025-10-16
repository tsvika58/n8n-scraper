#!/usr/bin/env python3
"""
Demo Monitoring System

This script simulates a scraper to show how the monitoring system works.
It creates fake progress data so you can test the monitor without running
a real scraper.

Usage:
    # Terminal 1: Run this demo scraper
    python scripts/demo_monitoring_system.py
    
    # Terminal 2: Monitor it
    python scripts/monitor_scraper.py --watch

Author: AI Assistant
Date: October 16, 2025
"""

import sys
import time
import asyncio
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring import ProgressTracker


async def simulate_workflow_scraping(tracker: ProgressTracker, workflow_id: str, workflow_num: int, total: int):
    """
    Simulate scraping a single workflow.
    
    Args:
        tracker: ProgressTracker instance
        workflow_id: Fake workflow ID
        workflow_num: Current workflow number (1-based)
        total: Total workflows
    """
    # Update status to "Extracting"
    tracker.update(
        current_workflow_id=workflow_id,
        status="Extracting..."
    )
    
    # Simulate extraction time (1-3 seconds)
    extraction_time = random.uniform(1, 3)
    await asyncio.sleep(extraction_time)
    
    # 90% success rate
    success = random.random() < 0.90
    
    if success:
        tracker.update(
            current_workflow_id=workflow_id,
            status="Saved",
            completed_delta=1
        )
        print(f"✅ [{workflow_num}/{total}] Workflow {workflow_id} - Success ({extraction_time:.1f}s)")
    else:
        # Generate random error
        errors = [
            "Network timeout",
            "Page not found",
            "JSON parse error",
            "Video extraction failed",
            "'NoneType' object has no attribute 'get'"
        ]
        error = random.choice(errors)
        
        tracker.update(
            current_workflow_id=workflow_id,
            status="Failed",
            failed_delta=1,
            error=error
        )
        print(f"❌ [{workflow_num}/{total}] Workflow {workflow_id} - Failed: {error}")
    
    # Small delay between workflows
    await asyncio.sleep(0.5)


async def main():
    """Main demo loop"""
    print("=" * 80)
    print("  DEMO: Monitoring System".center(80))
    print("=" * 80)
    print()
    print("This is a DEMO scraper that simulates workflow extraction.")
    print("It creates fake progress data to show how the monitoring system works.")
    print()
    print("To see the monitoring in action:")
    print("  1. Keep this terminal running")
    print("  2. Open a NEW terminal/chat")
    print("  3. Run: docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch")
    print()
    print("=" * 80)
    print()
    
    # Wait for user to set up monitoring
    print("⏳ Starting in 5 seconds... (set up monitor in another terminal now!)")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print()
    print("🚀 Starting demo scraper!")
    print()
    
    # Initialize tracker
    tracker = ProgressTracker(scraper_id="DEMO_scraper")
    
    # Simulate 50 workflows
    total_workflows = 50
    tracker.start(total_workflows=total_workflows)
    
    print(f"📊 Processing {total_workflows} fake workflows...")
    print(f"📁 Progress state: /tmp/scraper_progress.json")
    print()
    
    # Process workflows
    for i in range(1, total_workflows + 1):
        # Generate fake workflow ID
        workflow_id = f"DEMO_{random.randint(1000, 9999)}"
        
        await simulate_workflow_scraping(tracker, workflow_id, i, total_workflows)
    
    # Finish
    tracker.finish(status="Demo Completed")
    
    print()
    print("=" * 80)
    print("  DEMO COMPLETE!".center(80))
    print("=" * 80)
    print()
    
    # Show final stats
    progress = tracker.progress
    print(f"📊 FINAL STATISTICS:")
    print(f"   ✅ Completed: {progress.completed:,}")
    print(f"   ❌ Failed:    {progress.failed:,}")
    print(f"   📈 Success:   {progress.success_rate:.2f}%")
    print(f"   ⏱️  Duration:  {progress.elapsed_seconds:.1f}s")
    print()
    print("💡 The monitor should show these same stats!")
    print("   You can still open the monitor now to see the final state:")
    print("   → python scripts/monitor_scraper.py")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(1)

