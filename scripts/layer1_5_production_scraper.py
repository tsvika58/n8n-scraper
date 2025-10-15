#!/usr/bin/env python3
"""
Layer 1.5 Production Scraper

Replaces Layer 1 with comprehensive page content extraction.
Maintains backward compatibility by preserving existing fields.

Usage:
  --test   Test on 100 workflows
  --all    Run on all workflows
  --resume Resume from where you left off (default)
"""

import asyncio
import sys
sys.path.append('/app')

from src.scrapers.layer1_5_page_content import Layer1_5PageContentExtractor
from src.storage.database import get_session
from sqlalchemy import text
from loguru import logger
import time
import json


class Layer1_5ProductionScraper:
    """Production scraper for Layer 1.5 migration"""
    
    def __init__(self):
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0
        }
        self.start_time = time.time()
    
    async def run(self, limit=None, skip_completed=True):
        """Run Layer 1.5 scraping"""
        
        # Get workflows to process
        workflows = self.get_workflows(skip_completed, limit)
        self.stats['total'] = len(workflows)
        
        if self.stats['total'] == 0:
            logger.info("✅ All workflows already have Layer 1.5 data - nothing to scrape!")
            return
        
        logger.info(f"🚀 Processing {len(workflows)} workflows with Layer 1.5")
        logger.info(f"⏱️  Estimated time: {self.stats['total'] * 19 / 3600:.1f} hours")
        
        async with Layer1_5PageContentExtractor() as extractor:
            for i, (workflow_id, url) in enumerate(workflows, 1):
                logger.info(f"📊 Processing {i}/{len(workflows)}: {workflow_id}")
                
                try:
                    # Extract with Layer 1.5
                    result = await extractor.extract_full_page_content(workflow_id, url)
                    
                    if result["success"]:
                        # Save to database
                        self.save_to_database(
                            workflow_id, 
                            result["markdown"],
                            result["metadata"]
                        )
                        self.stats['successful'] += 1
                        logger.success(f"✅ {workflow_id}: {result['metadata']['content_length']} chars extracted")
                    else:
                        logger.error(f"❌ {workflow_id}: Extraction failed - {result['errors']}")
                        self.stats['failed'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ {workflow_id}: Error - {e}")
                    self.stats['failed'] += 1
                
                self.stats['processed'] += 1
                
                # Progress update every 10 workflows
                if i % 10 == 0:
                    self.print_progress()
                
                # Small delay to be polite
                await asyncio.sleep(1)
        
        self.print_final_report()
    
    def get_workflows(self, skip_completed=True, limit=None):
        """Get workflows to process"""
        with get_session() as session:
            if skip_completed:
                # Only get workflows that don't have Layer 1.5 data yet
                query = """
                    SELECT w.workflow_id, w.url
                    FROM workflows w
                    LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                    WHERE wm.layer1_5_extracted_at IS NULL
                    ORDER BY w.workflow_id::integer
                """
            else:
                # Get all workflows (force re-extraction)
                query = """
                    SELECT w.workflow_id, w.url
                    FROM workflows w
                    ORDER BY w.workflow_id::integer
                """
            
            if limit:
                query += f" LIMIT {limit}"
            
            result = session.execute(text(query))
            workflows = [(row[0], row[1]) for row in result]
            
            # Log completion status
            if skip_completed:
                completed_result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM workflow_metadata
                    WHERE layer1_5_extracted_at IS NOT NULL
                """))
                completed_count = completed_result.scalar()
                logger.info(f"📈 Already completed: {completed_count} workflows with Layer 1.5 data")
            
            return workflows
    
    def save_to_database(self, workflow_id: str, markdown: str, metadata: dict):
        """Save Layer 1.5 data to database"""
        
        with get_session() as session:
            # Convert metadata dict to JSON string
            metadata_json = json.dumps(metadata)
            
            session.execute(text("""
                UPDATE workflow_metadata
                SET 
                    layer1_5_content_markdown = :markdown,
                    layer1_5_metadata = :metadata,
                    layer1_5_extracted_at = CURRENT_TIMESTAMP
                WHERE workflow_id = :workflow_id
            """), {
                "workflow_id": workflow_id,
                "markdown": markdown,
                "metadata": metadata_json
            })
            session.commit()
            
            logger.debug(f"💾 Saved Layer 1.5 data for {workflow_id}")
    
    def print_progress(self):
        """Print progress update"""
        pct = (self.stats['processed'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        elapsed = time.time() - self.start_time
        rate = self.stats['processed'] / elapsed if elapsed > 0 else 0
        remaining = (self.stats['total'] - self.stats['processed']) / rate if rate > 0 else 0
        
        # Progress bar
        bar_length = 30
        filled = int(bar_length * self.stats['processed'] / self.stats['total'])
        bar = '█' * filled + '░' * (bar_length - filled)
        
        logger.info(f"📊 PROGRESS: {self.stats['processed']}/{self.stats['total']} ({pct:.1f}%) [{bar}]")
        logger.info(f"   ✅ Success: {self.stats['successful']} | ❌ Failed: {self.stats['failed']}")
        logger.info(f"   ⏱️  Rate: {rate:.2f} workflows/sec | ETA: {int(remaining//60)}m {int(remaining%60)}s")
    
    def print_final_report(self):
        """Print final report"""
        elapsed = time.time() - self.start_time
        logger.info("\n" + "="*70)
        logger.info("🎉 LAYER 1.5 SCRAPING COMPLETE")
        logger.info("="*70)
        logger.info(f"📊 Total workflows: {self.stats['total']}")
        logger.info(f"✅ Successfully scraped: {self.stats['successful']}")
        logger.info(f"❌ Failed: {self.stats['failed']}")
        
        if self.stats['total'] > 0:
            success_rate = self.stats['successful'] / self.stats['total'] * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")
            logger.info(f"⏱️  Total time: {int(elapsed//60)}m {int(elapsed%60)}s")
            logger.info(f"⚡ Average time per workflow: {elapsed/self.stats['total']:.1f}s")
        
        logger.info("="*70)


async def main():
    """Main entry point"""
    scraper = Layer1_5ProductionScraper()
    
    if '--test' in sys.argv:
        # Test mode: 100 workflows
        logger.info("🧪 TEST MODE: Running on 100 workflows")
        await scraper.run(limit=100)
    elif '--all' in sys.argv:
        # Production mode: all workflows
        logger.info("🚀 PRODUCTION MODE: Running on all workflows")
        await scraper.run()
    else:
        logger.info("Usage:")
        logger.info("  python layer1_5_production_scraper.py --test   # Test on 100 workflows")
        logger.info("  python layer1_5_production_scraper.py --all    # Run on all workflows")
        logger.info("\nNote: By default, resumes from where you left off (skips completed workflows)")


if __name__ == "__main__":
    asyncio.run(main())



