#!/usr/bin/env python3
"""
Populate Database with Proven 3-Layer Scraper

Uses the tested, working 3-layer scraper to populate the database.
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
from src.scrapers.layer2_json_extractor import Layer2JSONExtractor
from src.scrapers.multimodal_processor import MultimodalProcessor

class DatabasePopulator:
    """Populate database using proven 3-layer scraper."""
    
    def __init__(self):
        self.layer1 = PageMetadataExtractor()
        self.layer2 = Layer2JSONExtractor()
        self.layer3 = MultimodalProcessor()
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0
        }
        self.start_time = time.time()
        
    def get_workflows_to_scrape(self):
        """Get workflows that need Layer 1 data."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT w.workflow_id, w.url
                FROM workflows w
                LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                WHERE wm.description IS NULL OR wm.description = ''
                ORDER BY w.workflow_id::integer
            """))
            
            workflows = [(row[0], row[1]) for row in result]
            logger.info(f"Found {len(workflows)} workflows to scrape")
            return workflows
    
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
    
    async def scrape_workflow(self, workflow_id, url):
        """Scrape workflow using proven 3-layer approach."""
        try:
            logger.info(f"🔄 Scraping workflow {workflow_id}...")
            
            # Layer 1: Page Metadata
            layer1_result = await self.layer1.extract(workflow_id, url)
            if not layer1_result['success']:
                logger.error(f"❌ Layer 1 failed for {workflow_id}")
                return False
            
            # Layer 2: Workflow JSON
            layer2_result = self.layer2.extract_workflow_json(workflow_id)
            if not layer2_result['success']:
                logger.warning(f"⚠️ Layer 2 failed for {workflow_id}, continuing...")
            
            # Layer 3: Multimedia
            layer3_result = await self.layer3.process_workflow(workflow_id, url)
            if not layer3_result['success']:
                logger.warning(f"⚠️ Layer 3 failed for {workflow_id}, continuing...")
            
            # Save to database
            self.save_workflow_data(workflow_id, layer1_result['data'], layer2_result.get('data', {}), layer3_result.get('data', {}))
            
            self.stats['successful'] += 1
            logger.success(f"✅ Workflow {workflow_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Exception scraping workflow {workflow_id}: {str(e)}")
            self.stats['failed'] += 1
            return False
    
    def save_workflow_data(self, workflow_id, layer1_data, layer2_data, layer3_data):
        """Save all layer data to database."""
        with get_session() as session:
            try:
                # Update workflow_metadata with all layer data
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
                    'description': layer1_data.get('description', ''),
                    'author_name': layer1_data.get('author', 'Unknown Author'),
                    'use_case': layer1_data.get('use_case', ''),
                    'views': layer1_data.get('views', 0),
                    'tags': self._format_tags(layer1_data),
                    'created_at': layer1_data.get('created_date'),
                    'updated_at': layer1_data.get('updated_date'),
                    'skill_level': layer1_data.get('difficulty_level', 'intermediate'),
                    'industry': self._format_industry(layer1_data.get('industry', [])),
                    'estimated_time': self._parse_time_to_minutes(layer1_data.get('estimated_setup_time', 'Unknown')),
                    'raw_metadata': self._format_all_layer_data(layer1_data, layer2_data, layer3_data)
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
    
    def _format_all_layer_data(self, layer1_data, layer2_data, layer3_data):
        """Format all layer data as JSON."""
        import json
        return json.dumps({
            'layer1': {
                'title': layer1_data.get('title'),
                'description': layer1_data.get('description'),
                'author': layer1_data.get('author'),
                'use_case': layer1_data.get('use_case'),
                'primary_category': layer1_data.get('primary_category'),
                'secondary_categories': layer1_data.get('secondary_categories', []),
                'node_tags': layer1_data.get('node_tags', []),
                'general_tags': layer1_data.get('general_tags', []),
                'difficulty_level': layer1_data.get('difficulty_level'),
                'views': layer1_data.get('views'),
                'upvotes': layer1_data.get('upvotes'),
                'created_date': layer1_data.get('created_date'),
                'updated_date': layer1_data.get('updated_date'),
                'setup_instructions': layer1_data.get('setup_instructions'),
                'prerequisites': layer1_data.get('prerequisites', []),
                'estimated_setup_time': layer1_data.get('estimated_setup_time'),
                'industry': layer1_data.get('industry', [])
            },
            'layer2': layer2_data,
            'layer3': layer3_data
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
        """Run the database population process."""
        logger.info("="*70)
        logger.info("STARTING DATABASE POPULATION WITH PROVEN 3-LAYER SCRAPER")
        logger.info("="*70)
        
        # Get workflows to scrape
        workflows = self.get_all_workflows()
        if limit:
            workflows = workflows[:limit]
        
        self.stats['total'] = len(workflows)
        logger.info(f"Will scrape {len(workflows)} workflows")
        
        # Process each workflow
        for i, (workflow_id, url) in enumerate(workflows, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"WORKFLOW {i}/{len(workflows)}: {workflow_id}")
            logger.info(f"{'='*50}")
            
            # Scrape and save
            success = await self.scrape_workflow(workflow_id, url)
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
        logger.info("DATABASE POPULATION COMPLETE")
        logger.info("="*70)
        logger.info(f"Total workflows: {self.stats['total']}")
        logger.info(f"Successfully scraped: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Success rate: {self.stats['successful']/self.stats['total']*100:.1f}%")
        logger.info(f"Total time: {int(elapsed//60)}m {int(elapsed%60)}s")
        logger.info(f"Average time per workflow: {elapsed/self.stats['total']:.1f}s")

async def main():
    """Main entry point."""
    populator = DatabasePopulator()
    
    # Start with a small batch to test
    logger.info("Starting with first 5 workflows for testing...")
    await populator.run(limit=5)
    
    # If successful, ask user if they want to continue with all
    logger.info("\n" + "="*70)
    logger.info("TEST BATCH COMPLETE")
    logger.info("="*70)
    logger.info("If this looks good, run without limit to scrape all workflows:")
    logger.info("python /app/scripts/populate_database_with_proven_scraper.py --all")

if __name__ == "__main__":
    import sys
    if '--all' in sys.argv:
        populator = DatabasePopulator()
        asyncio.run(populator.run())
    else:
        asyncio.run(main())


