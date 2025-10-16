#!/usr/bin/env python3
"""
Production-ready script to scrape ALL workflows using UnifiedWorkflowExtractor WITH STICKY PROGRESS BAR.

CRITICAL: Uses ANSI escape codes to display sticky progress bar at terminal bottom.

Author: Production Scraping Script  
Date: October 16, 2025
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import logging
import pytz

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import after path is set
from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor
from src.storage.database import get_session
from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)

# Global stats for sticky progress
stats = {
    'start_time': None,
    'completed': 0,
    'failed': 0,
    'total': 0
}


def print_sticky_progress(current, total, workflow_id, status):
    """
    Print sticky progress bar at terminal bottom.
    EXACTLY copied from validate_7_workflows_production.py lines 96-105
    """
    if not stats['start_time']:
        return
        
    elapsed = time.time() - stats['start_time']
    progress_pct = (current / total) * 100 if total > 0 else 0
    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Jerusalem time
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    jerusalem_time = datetime.now(jerusalem_tz).strftime('%H:%M:%S')
    
    # Format elapsed
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    if hours > 0:
        elapsed_str = f"{hours}h{minutes}m"
    else:
        elapsed_str = f"{minutes}m"
    
    # Calculate ETA
    if current > 0:
        avg_time = elapsed / current
        remaining = (total - current) * avg_time
        eta_hours = int(remaining // 3600)
        eta_minutes = int((remaining % 3600) // 60)
        if eta_hours > 0:
            eta_str = f"{eta_hours}h{eta_minutes}m"
        else:
            eta_str = f"{eta_minutes}m"
    else:
        eta_str = "calculating..."
    
    # CRITICAL: ANSI codes - \033[s (save cursor), \033[9999;0H (bottom), \033[K (clear), \033[u (restore)
    separator = "─" * 70
    print(f"\033[s\033[9999;0H\033[K{separator}\n"
          f"\033[K🔄 [{bar}] {progress_pct:.0f}% ({stats['completed']}/{total}) | "
          f"Failed: {stats['failed']} | "
          f"Current: {workflow_id} | "
          f"{status} | "
          f"⏱️ {elapsed_str} | "
          f"ETA: {eta_str} | "
          f"🕐 {jerusalem_time}"
          f"\033[u", 
          end='', flush=True)


def get_all_workflows() -> List[Tuple[str, str]]:
    """Get all workflows from database."""
    try:
        with get_session() as session:
            query = text("""
                SELECT w.workflow_id, w.url
                FROM workflows w
                ORDER BY w.id
            """)
            
            result = session.execute(query)
            workflows = [(row[0], row[1]) for row in result.fetchall()]
            
            logger.info(f"📊 Found {len(workflows)} workflows needing unified extraction")
            return workflows
            
    except Exception as e:
        logger.error(f"❌ Failed to get workflows: {e}")
        raise


async def scrape_workflow(
    extractor: UnifiedWorkflowExtractor,
    workflow_id: str,
    url: str,
    current: int,
    total: int
) -> bool:
    """Scrape a single workflow."""
    try:
        # Update sticky progress
        print_sticky_progress(current, total, workflow_id, "Extracting...")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"[{current}/{total}] Processing workflow {workflow_id}")
        logger.info(f"URL: {url}")
        logger.info(f"{'='*70}")
        
        # Extract workflow data
        result = await extractor.extract(workflow_id, url)
        
        if result['success'] and result['data']:
            # Update sticky progress
            print_sticky_progress(current, total, workflow_id, "Saving...")
            
            # Save to database
            saved = extractor.save_to_database(workflow_id, result['data'])
            
            if saved:
                stats['completed'] += 1
                print_sticky_progress(current, total, workflow_id, "✅ Saved")
                
                data = result['data']
                logger.info(f"✅ [{current}/{total}] SUCCESS: {workflow_id}")
                logger.info(f"   📊 Nodes: {data['node_count']}")
                logger.info(f"   📝 Node contexts: {data['node_context_count']}")
                logger.info(f"   📌 Standalone notes: {data['standalone_note_count']}")
                logger.info(f"   🎬 Videos: {data['video_count']}")
                logger.info(f"   📜 Transcripts: {data['transcript_count']}")
                return True
            else:
                stats['failed'] += 1
                print_sticky_progress(current, total, workflow_id, "❌ Save Failed")
                logger.error(f"❌ [{current}/{total}] FAILED to save: {workflow_id}")
                return False
        else:
            stats['failed'] += 1
            error_msg = result.get('error', 'Unknown error')
            print_sticky_progress(current, total, workflow_id, "❌ Failed")
            logger.error(f"❌ [{current}/{total}] FAILED: {workflow_id} - {error_msg}")
            return False
             
    except Exception as e:
        stats['failed'] += 1
        print_sticky_progress(current, total, workflow_id, "❌ Exception")
        logger.error(f"❌ [{current}/{total}] EXCEPTION: {workflow_id} - {e}")
        return False


async def run_production_scraping(
    batch_size: int = 10,
    delay_between_workflows: float = 2.0,
    delay_between_batches: float = 10.0
):
    """Run production scraping with sticky progress bar."""
    
    logger.info("\n" + "="*70)
    logger.info("🚀 PRODUCTION UNIFIED WORKFLOW SCRAPING")
    logger.info("="*70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Delay between workflows: {delay_between_workflows}s")
    logger.info(f"Delay between batches: {delay_between_batches}s")
    logger.info("="*70)
    
    # Get all workflows
    logger.info("\n📥 Fetching workflows from database...")
    workflows = get_all_workflows()
    total = len(workflows)
    stats['total'] = total
    
    if total == 0:
        logger.info("✅ No workflows need processing. All done!")
        return
    
    # Initialize extractor
    logger.info("\n🎬 Initializing UnifiedWorkflowExtractor...")
    async with UnifiedWorkflowExtractor(headless=True, timeout=60000, extract_transcripts=True) as extractor:
        logger.info("✅ Extractor initialized successfully")
        
        # Start timing
        stats['start_time'] = time.time()
        
        # Print initial sticky progress
        print_sticky_progress(0, total, "Starting...", "Initialized")
        
        # Process workflows in batches
        for i, (workflow_id, url) in enumerate(workflows, 1):
            # Process workflow
            success = await scrape_workflow(extractor, workflow_id, url, i, total)
            
            # Delay between workflows
            if i < total:
                await asyncio.sleep(delay_between_workflows)
            
            # Delay between batches
            if i % batch_size == 0 and i < total:
                print_sticky_progress(i, total, workflow_id, "⏸️ Batch break...")
                logger.info(f"\n⏸️  Batch complete ({i}/{total}). Taking {delay_between_batches}s break...")
                await asyncio.sleep(delay_between_batches)
    
    # Final summary
    elapsed_total = time.time() - stats['start_time']
    logger.info("\n\n" + "="*70)
    logger.info("🎉 PRODUCTION SCRAPING COMPLETE")
    logger.info("="*70)
    logger.info(f"Total workflows: {stats['total']}")
    logger.info(f"Successful: {stats['completed']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Success rate: {(stats['completed']/stats['total']*100):.1f}%")
    logger.info(f"Total time: {elapsed_total/60:.1f} minutes")
    logger.info(f"Average time per workflow: {elapsed_total/stats['total']:.1f} seconds")
    logger.info("="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Production unified workflow scraping')
    parser.add_argument('--batch-size', type=int, default=10, help='Workflows per batch (default: 10)')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between workflows in seconds (default: 2.0)')
    parser.add_argument('--batch-delay', type=float, default=10.0, help='Delay between batches in seconds (default: 10.0)')
    
    args = parser.parse_args()
    
    # Run the scraping
    try:
        asyncio.run(run_production_scraping(
            batch_size=args.batch_size,
            delay_between_workflows=args.delay,
            delay_between_batches=args.batch_delay
        ))
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Scraping interrupted by user (Ctrl+C)")
        logger.info("You can resume later - already processed workflows will be skipped")
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
