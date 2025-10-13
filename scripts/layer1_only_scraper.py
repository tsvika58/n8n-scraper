#!/usr/bin/env python3
"""
Layer 1 Only Scraper - Using Proven Layer 1 from 3-Layer Package

Uses the exact same Layer 1 scraper that we know works, with solid DB saving.
"""

import sys
sys.path.insert(0, '/app')

import asyncio
import time
from datetime import datetime
from sqlalchemy import text
from loguru import logger

from src.storage.database import get_session
from src.scrapers.layer1_metadata import PageMetadataExtractor

class Layer1OnlyScraper:
    """Layer 1 scraper using the proven extractor with solid DB saving."""
    
    def __init__(self):
        self.extractor = PageMetadataExtractor()
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0
        }
        self.start_time = time.time()
        
    def get_all_workflows(self):
        """Get ALL workflows for complete scraping."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT w.workflow_id, w.url
                FROM workflows w
                ORDER BY w.workflow_id::integer
            """))
            
            workflows = [(row[0], row[1]) for row in result]
            logger.info(f"Found {len(workflows)} total workflows")
            return workflows
    
    async def scrape_and_save_workflow(self, workflow_id, url):
        """Scrape one workflow using proven Layer 1 and save to DB."""
        try:
            logger.info(f"🔄 Scraping workflow {workflow_id}...")
            
            # Use the EXACT same Layer 1 extractor that works
            result = await self.extractor.extract(workflow_id, url)
            
            if result['success']:
                # Save to database using proven method
                self.save_workflow_data(workflow_id, result['data'])
                self.stats['successful'] += 1
                logger.success(f"✅ Workflow {workflow_id} completed successfully")
                return True
            else:
                logger.error(f"❌ Workflow {workflow_id} failed: {result.get('error', 'Unknown error')}")
                self.stats['failed'] += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception scraping workflow {workflow_id}: {str(e)}")
            self.stats['failed'] += 1
            return False
    
    def save_workflow_data(self, workflow_id, data):
        """Save workflow data to database - SOLID METHOD using direct SQL."""
        with get_session() as session:
            try:
                # Use direct SQL with proper parameter binding
                session.execute(text("""
                    UPDATE workflow_metadata
                    SET 
                        description = :description,
                        author_name = :author_name,
                        use_case = :use_case,
                        views = :views,
                        tags = :tags::jsonb,
                        workflow_created_at = :created_at,
                        workflow_updated_at = :updated_at,
                        workflow_skill_level = :skill_level,
                        workflow_industry = :industry,
                        workflow_estimated_time = :estimated_time,
                        raw_metadata = :raw_metadata::jsonb,
                        extracted_at = NOW()
                    WHERE workflow_id = :workflow_id
                """), {
                    'workflow_id': workflow_id,
                    'description': data.get('description', ''),
                    'author_name': data.get('author', 'Unknown Author'),
                    'use_case': data.get('use_case', ''),
                    'views': data.get('views', 0),
                    'tags': self._format_tags(data),
                    'created_at': data.get('created_date'),
                    'updated_at': data.get('updated_date'),
                    'skill_level': data.get('difficulty_level', 'intermediate'),
                    'industry': self._format_industry(data.get('industry', [])),
                    'estimated_time': self._parse_time_to_minutes(data.get('estimated_setup_time', 'Unknown')),
                    'raw_metadata': self._format_raw_metadata(data)
                })
                
                session.commit()
                logger.debug(f"💾 Saved workflow {workflow_id} to database")
                
            except Exception as e:
                logger.error(f"Failed to save workflow {workflow_id}: {str(e)}")
                session.rollback()
                raise
    
    def _format_tags(self, data):
        """Format tags as JSON array."""
        import json
        node_tags = data.get('node_tags', [])
        general_tags = data.get('general_tags', [])
        all_tags = list(set(node_tags + general_tags))
        return json.dumps(all_tags)
    
    def _format_industry(self, industry_list):
        """Format industry list as comma-separated string."""
        if isinstance(industry_list, list) and industry_list:
            return ', '.join(industry_list)
        return 'General'
    
    def _parse_time_to_minutes(self, time_str):
        """Parse time string to minutes."""
        import re
        
        if not time_str or time_str == 'Unknown':
            return None
        
        time_str = time_str.lower()
        
        # Hours
        hours_match = re.search(r'(\d+)\s*(?:hour|hr)s?', time_str)
        if hours_match:
            return int(hours_match.group(1)) * 60
        
        # Minutes
        minutes_match = re.search(r'(\d+)\s*(?:min|minute)s?', time_str)
        if minutes_match:
            return int(minutes_match.group(1))
        
        # Seconds
        seconds_match = re.search(r'(\d+)\s*(?:sec|second)s?', time_str)
        if seconds_match:
            return max(1, int(seconds_match.group(1)) // 60)
        
        # Days
        days_match = re.search(r'(\d+)\s*day?s?', time_str)
        if days_match:
            return int(days_match.group(1)) * 24 * 60
        
        return None
    
    def _format_raw_metadata(self, data):
        """Format complete Layer 1 data as JSON."""
        import json
        return json.dumps({
            'title': data.get('title'),
            'description': data.get('description'),
            'author': data.get('author'),
            'use_case': data.get('use_case'),
            'primary_category': data.get('primary_category'),
            'secondary_categories': data.get('secondary_categories', []),
            'node_tags': data.get('node_tags', []),
            'general_tags': data.get('general_tags', []),
            'difficulty_level': data.get('difficulty_level'),
            'views': data.get('views'),
            'upvotes': data.get('upvotes'),
            'created_date': data.get('created_date'),
            'updated_date': data.get('updated_date'),
            'setup_instructions': data.get('setup_instructions'),
            'prerequisites': data.get('prerequisites', []),
            'estimated_setup_time': data.get('estimated_setup_time'),
            'industry': data.get('industry', [])
        })
    
    def print_progress(self):
        """Print current progress."""
        elapsed = time.time() - self.start_time
        pct = (self.stats['processed'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        
        # Calculate ETA
        if self.stats['processed'] > 0:
            avg_time = elapsed / self.stats['processed']
            remaining = self.stats['total'] - self.stats['processed']
            eta_seconds = remaining * avg_time
            eta_str = f"{int(eta_seconds//3600)}h {int((eta_seconds%3600)//60)}m"
        else:
            eta_str = "Unknown"
        
        logger.info(f"📊 Progress: {self.stats['processed']}/{self.stats['total']} ({pct:.1f}%) | "
                   f"✅ {self.stats['successful']} | ❌ {self.stats['failed']} | "
                   f"⏱️ {int(elapsed//60)}m elapsed | ETA: {eta_str}")
    
    async def run(self, limit=None):
        """Run the Layer 1 scraping process."""
        logger.info("="*70)
        logger.info("STARTING LAYER 1 ONLY SCRAPING")
        logger.info("="*70)
        
        # Get workflows to scrape
        workflows = self.get_all_workflows()
        if limit:
            workflows = workflows[:limit]
        
        self.stats['total'] = len(workflows)
        logger.info(f"Will scrape {len(workflows)} workflows using proven Layer 1 extractor")
        
        # Process each workflow
        for i, (workflow_id, url) in enumerate(workflows, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"WORKFLOW {i}/{len(workflows)}: {workflow_id}")
            logger.info(f"{'='*50}")
            
            # Scrape and save
            success = await self.scrape_and_save_workflow(workflow_id, url)
            self.stats['processed'] += 1
            
            # Print progress every 10 workflows
            if i % 10 == 0 or i == len(workflows):
                self.print_progress()
            
            # Small delay to be polite
            await asyncio.sleep(1)
        
        # Final report
        self.print_final_report()
    
    def print_final_report(self):
        """Print final report."""
        elapsed = time.time() - self.start_time
        logger.info("\n" + "="*70)
        logger.info("LAYER 1 SCRAPING COMPLETE")
        logger.info("="*70)
        logger.info(f"Total workflows: {self.stats['total']}")
        logger.info(f"Successfully scraped: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Success rate: {self.stats['successful']/self.stats['total']*100:.1f}%")
        logger.info(f"Total time: {int(elapsed//60)}m {int(elapsed%60)}s")
        logger.info(f"Average time per workflow: {elapsed/self.stats['total']:.1f}s")

async def main():
    """Main entry point."""
    scraper = Layer1OnlyScraper()
    
    # Start with a small batch to test
    logger.info("Starting with first 5 workflows for testing...")
    await scraper.run(limit=5)
    
    # If successful, ask user if they want to continue with all
    logger.info("\n" + "="*70)
    logger.info("TEST BATCH COMPLETE")
    logger.info("="*70)
    logger.info("If this looks good, run without limit to scrape all workflows:")
    logger.info("python /app/scripts/layer1_only_scraper.py --all")

if __name__ == "__main__":
    import sys
    if '--all' in sys.argv:
        scraper = Layer1OnlyScraper()
        asyncio.run(scraper.run())
    else:
        asyncio.run(main())
