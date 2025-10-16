#!/usr/bin/env python3
"""
Production Unified Scraper with Built-in Progress Tracking

This scraper uses the ProgressTracker to write state that can be
monitored from a separate terminal/process.

Usage:
    # Run scraper (in one terminal)
    docker exec n8n-scraper-app python scripts/scrape_production_unified.py
    
    # Monitor progress (in another terminal)
    docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch

Author: AI Assistant
Date: October 16, 2025
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor
from src.storage.database import get_session
from n8n_shared.models import Workflow
from src.monitoring import ProgressTracker
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


async def scrape_workflow(extractor: UnifiedWorkflowExtractor, 
                          tracker: ProgressTracker,
                          workflow_id: str, 
                          url: str) -> bool:
    """
    Scrape a single workflow with progress tracking.
    
    Args:
        extractor: UnifiedWorkflowExtractor instance
        tracker: ProgressTracker instance
        workflow_id: Workflow ID
        url: Workflow URL
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Update tracker
        tracker.update(
            current_workflow_id=workflow_id,
            status="Extracting..."
        )
        
        # Extract
        result = await extractor.extract(workflow_id, url)
        
        if result['success'] and result['data']:
            # Save to database
            saved = extractor.save_to_database(workflow_id, result['data'])
            
            if saved:
                tracker.update(
                    current_workflow_id=workflow_id,
                    status="Saved",
                    completed_delta=1
                )
                logger.info(f"✅ [{workflow_id}] Success - "
                           f"{result['data']['node_count']} nodes, "
                           f"{result['data']['video_count']} videos")
                return True
            else:
                tracker.update(
                    current_workflow_id=workflow_id,
                    status="Save failed",
                    failed_delta=1,
                    error="Database save failed"
                )
                logger.error(f"❌ [{workflow_id}] Save failed")
                return False
        else:
            error_msg = result.get('error', 'Unknown error')
            tracker.update(
                current_workflow_id=workflow_id,
                status="Failed",
                failed_delta=1,
                error=error_msg
            )
            logger.error(f"❌ [{workflow_id}] Failed: {error_msg}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        tracker.update(
            current_workflow_id=workflow_id,
            status="Error",
            failed_delta=1,
            error=error_msg
        )
        logger.error(f"❌ [{workflow_id}] Error: {error_msg}")
        return False


async def main():
    """Main scraping loop"""
    logger.info("=" * 80)
    logger.info("  N8N UNIFIED WORKFLOW SCRAPER - PRODUCTION MODE")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize progress tracker
    tracker = ProgressTracker(scraper_id="production_unified")
    
    # Get workflows to process
    logger.info("📋 Querying workflows to process...")
    with get_session() as session:
        workflows = session.query(Workflow).filter(
            Workflow.unified_extraction_success == False
        ).order_by(Workflow.id).all()
        
        total = len(workflows)
        logger.info(f"   Found {total:,} workflows to process")
    
    if total == 0:
        logger.info("✅ All workflows already processed!")
        return
    
    # Start tracking
    tracker.start(total_workflows=total)
    logger.info("")
    logger.info(f"🚀 Starting scraper...")
    logger.info(f"   Progress tracking: /tmp/scraper_progress.json")
    logger.info(f"   Monitor from another terminal:")
    logger.info(f"   → docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch")
    logger.info("")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize extractor
    async with UnifiedWorkflowExtractor(headless=True) as extractor:
        for idx, workflow in enumerate(workflows, 1):
            logger.info(f"[{idx}/{total}] Processing workflow {workflow.workflow_id}...")
            
            await scrape_workflow(
                extractor,
                tracker,
                workflow.workflow_id,
                workflow.url
            )
            
            # Rate limiting
            await asyncio.sleep(0.5)
    
    # Finish tracking
    tracker.finish(status="Completed")
    
    # Final summary
    progress = tracker.progress
    logger.info("")
    logger.info("=" * 80)
    logger.info("  SCRAPING COMPLETED")
    logger.info("=" * 80)
    logger.info(f"✅ Completed: {progress.completed:,}")
    logger.info(f"❌ Failed:    {progress.failed:,}")
    logger.info(f"📈 Success:   {progress.success_rate:.2f}%")
    logger.info(f"⏱️  Duration:  {progress.elapsed_seconds/3600:.2f}h")
    logger.info("=" * 80)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)

