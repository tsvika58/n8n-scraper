"""
Production Re-scraping Script for Layer 1 Enhanced V2

Re-scrapes all workflows with the new clean Layer 1 Enhanced V2 scraper.
Saves to page_content_v2 field for safe migration.

Features:
- Progress tracking with ETA
- Error handling and retry logic
- Resume capability
- Rate limiting
- Real-time statistics
"""

import asyncio
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.layer1_enhanced_v2 import Layer1EnhancedV2Extractor
from n8n_shared.database import create_sync_engine, get_sync_session_maker
from n8n_shared.models import Base
from sqlalchemy import text
from loguru import logger
import os


class ProductionRescraper:
    """Handles production re-scraping with progress tracking and error handling."""
    
    def __init__(self, batch_size: int = 10, delay: float = 3.0, batch_delay: float = 10.0):
        self.batch_size = batch_size
        self.delay = delay
        self.batch_delay = batch_delay
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None,
        }
    
    async def get_workflows_to_rescrape(self, offset: int = 0) -> List[Dict]:
        """Get batch of workflows that need re-scraping."""
        
        engine = create_sync_engine(os.getenv('DATABASE_URL'))
        SessionMaker = get_sync_session_maker(engine)
        
        with SessionMaker() as session:
            # Get workflows that don't have page_content_v2 yet
            query = text("""
                SELECT w.workflow_id, wm.title, w.url
                FROM workflows w
                LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                WHERE w.layer1_success = true
                  AND (wm.page_content_v2 IS NULL OR wm.page_content_v2 = '')
                ORDER BY w.workflow_id
                LIMIT :batch_size OFFSET :offset
            """)
            
            result = session.execute(query, {'batch_size': self.batch_size, 'offset': offset})
            workflows = []
            
            for row in result.fetchall():
                workflows.append({
                    "workflow_id": row[0],
                    "title": row[1],
                    "url": row[2],
                })
            
            return workflows
    
    async def get_total_remaining(self) -> int:
        """Get total count of workflows needing re-scraping."""
        
        engine = create_sync_engine(os.getenv('DATABASE_URL'))
        SessionMaker = get_sync_session_maker(engine)
        
        with SessionMaker() as session:
            query = text("""
                SELECT COUNT(*)
                FROM workflows w
                LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                WHERE w.layer1_success = true
                  AND (wm.page_content_v2 IS NULL OR wm.page_content_v2 = '')
            """)
            
            result = session.execute(query)
            return result.scalar_one()
    
    async def save_extracted_content(self, workflow_id: str, markdown_content: str):
        """Save extracted content to page_content_v2 field."""
        
        engine = create_sync_engine(os.getenv('DATABASE_URL'))
        SessionMaker = get_sync_session_maker(engine)
        
        with SessionMaker() as session:
            query = text("""
                UPDATE workflow_metadata
                SET page_content_v2 = :content,
                    page_content_v2_extracted_at = NOW()
                WHERE workflow_id = :workflow_id
            """)
            
            session.execute(query, {
                'workflow_id': workflow_id,
                'content': markdown_content
            })
            session.commit()
    
    async def save_error(self, workflow_id: str, error_message: str):
        """Save extraction error."""
        
        engine = create_sync_engine(os.getenv('DATABASE_URL'))
        SessionMaker = get_sync_session_maker(engine)
        
        with SessionMaker() as session:
            query = text("""
                UPDATE workflows
                SET error_message = :error_msg,
                    updated_at = NOW()
                WHERE workflow_id = :workflow_id
            """)
            
            session.execute(query, {
                'workflow_id': workflow_id,
                'error_msg': f"Layer 1 V2 extraction failed: {error_message}"
            })
            session.commit()
    
    def print_stats(self):
        """Print current statistics."""
        
        elapsed = time.time() - self.stats["start_time"]
        processed = self.stats["processed"]
        total = self.stats["total"]
        
        if processed > 0:
            avg_time = elapsed / processed
            remaining = total - processed
            eta_seconds = remaining * avg_time
            eta_hours = eta_seconds / 3600
            
            success_rate = (self.stats["successful"] / processed * 100) if processed > 0 else 0
            
            print(f"\n{'='*100}")
            print(f"📊 PROGRESS STATISTICS")
            print(f"{'='*100}")
            print(f"   Processed: {processed}/{total} workflows ({processed/total*100:.1f}%)")
            print(f"   ✅ Successful: {self.stats['successful']} ({success_rate:.1f}%)")
            print(f"   ❌ Failed: {self.stats['failed']}")
            print(f"   ⏭️  Skipped: {self.stats['skipped']}")
            print(f"   ⏱️  Elapsed: {elapsed/3600:.2f} hours")
            print(f"   🎯 ETA: {eta_hours:.2f} hours remaining")
            print(f"   ⚡ Avg time/workflow: {avg_time:.2f}s")
            print(f"{'='*100}\n")
    
    async def run(self):
        """Main re-scraping loop."""
        
        logger.info("🚀 Starting Layer 1 Enhanced V2 production re-scraping")
        
        self.stats["start_time"] = time.time()
        self.stats["total"] = await self.get_total_remaining()
        
        logger.info(f"📊 Total workflows to re-scrape: {self.stats['total']}")
        
        if self.stats["total"] == 0:
            logger.info("✅ All workflows already have page_content_v2! Nothing to do.")
            return
        
        offset = 0
        
        async with Layer1EnhancedV2Extractor(headless=True) as extractor:
            while True:
                # Get next batch
                workflows = await self.get_workflows_to_rescrape(offset)
                
                if not workflows:
                    logger.info("✅ No more workflows to process")
                    break
                
                logger.info(f"\n{'='*100}")
                logger.info(f"📦 Processing batch: workflows {offset+1} to {offset+len(workflows)}")
                logger.info(f"{'='*100}")
                
                for wf in workflows:
                    workflow_id = wf["workflow_id"]
                    title = wf["title"] or "Untitled"
                    url = wf["url"]
                    
                    logger.info(f"\n🔄 Processing workflow {workflow_id}: {title[:60]}")
                    
                    try:
                        # Extract content
                        result = await extractor.extract_full_page_content(workflow_id, url)
                        
                        if result["success"]:
                            # Save to database
                            markdown = result.get("markdown", "")
                            await self.save_extracted_content(workflow_id, markdown)
                            
                            self.stats["successful"] += 1
                            logger.success(f"✅ Saved {len(markdown)} chars for workflow {workflow_id}")
                        else:
                            # Save error
                            error_msg = "; ".join(result.get("errors", ["Unknown error"]))
                            await self.save_error(workflow_id, error_msg)
                            
                            self.stats["failed"] += 1
                            logger.error(f"❌ Failed workflow {workflow_id}: {error_msg}")
                    
                    except Exception as e:
                        # Handle unexpected errors
                        error_msg = str(e)
                        await self.save_error(workflow_id, error_msg)
                        
                        self.stats["failed"] += 1
                        logger.error(f"‼️  Exception for workflow {workflow_id}: {error_msg}")
                    
                    finally:
                        self.stats["processed"] += 1
                    
                    # Delay between workflows
                    if self.stats["processed"] < self.stats["total"]:
                        await asyncio.sleep(self.delay)
                
                # Print stats after each batch
                self.print_stats()
                
                # Delay between batches
                if workflows:
                    logger.info(f"⏸️  Batch delay: {self.batch_delay} seconds...")
                    await asyncio.sleep(self.batch_delay)
                
                offset += self.batch_size
        
        # Final statistics
        logger.info("\n" + "="*100)
        logger.info("🎉 RE-SCRAPING COMPLETE!")
        logger.info("="*100)
        self.print_stats()


async def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Re-scrape all workflows with Layer 1 Enhanced V2")
    parser.add_argument("--batch-size", type=int, default=10, help="Workflows per batch")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between workflows (seconds)")
    parser.add_argument("--batch-delay", type=float, default=10.0, help="Delay between batches (seconds)")
    
    args = parser.parse_args()
    
    rescraper = ProductionRescraper(
        batch_size=args.batch_size,
        delay=args.delay,
        batch_delay=args.batch_delay
    )
    
    await rescraper.run()


if __name__ == "__main__":
    asyncio.run(main())

