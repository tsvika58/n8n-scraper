#!/usr/bin/env python3
"""
Production Layer 1 Scraping - Full Database Population

Features:
- Batch processing with immediate saves (no data loss)
- Automatic retry on failures (3 attempts per workflow)
- Progress tracking with resume capability
- Parallel processing (10 workers)
- Comprehensive error handling
- Real-time statistics and reporting

Author: AI Assistant
Date: October 13, 2025
"""

import sys
sys.path.insert(0, '/app')

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import text
from loguru import logger

from src.storage.database import get_session
from src.scrapers.layer1_metadata import PageMetadataExtractor

# Configuration
BATCH_SIZE = 50  # Save every 50 workflows
MAX_RETRIES = 3  # Retry failed workflows 3 times
PARALLEL_WORKERS = 10  # Run 10 scrapers in parallel
PROGRESS_FILE = '/app/data/layer1_progress.txt'

class Layer1FullScraper:
    """Production-grade Layer 1 scraper with robust error handling."""
    
    def __init__(self):
        self.extractor = PageMetadataExtractor()
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'retried': 0
        }
        self.failed_workflows = []
        
    def get_workflows_to_scrape(self) -> List[Dict]:
        """Get all workflows that need Layer 1 scraping."""
        with get_session() as session:
            # Get workflows that haven't been scraped yet (no description)
            # OR workflows that were scraped but failed
            result = session.execute(text("""
                SELECT w.workflow_id, w.url, wm.description
                FROM workflows w
                LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                WHERE wm.description IS NULL OR wm.description = ''
                ORDER BY w.workflow_id::integer
            """))
            
            workflows = [
                {'workflow_id': row[0], 'url': row[1], 'has_data': row[2] is not None}
                for row in result
            ]
            
            logger.info(f"Found {len(workflows)} workflows to scrape")
            return workflows
    
    def get_all_workflows(self) -> List[Dict]:
        """Get ALL workflows for complete scraping."""
        with get_session() as session:
            result = session.execute(text("""
                SELECT w.workflow_id, w.url
                FROM workflows w
                ORDER BY w.workflow_id::integer
            """))
            
            workflows = [
                {'workflow_id': row[0], 'url': row[1]}
                for row in result
            ]
            
            logger.info(f"Found {len(workflows)} total workflows")
            return workflows
    
    async def scrape_workflow(self, workflow: Dict, retry_count: int = 0) -> Optional[Dict]:
        """Scrape a single workflow with retry logic."""
        workflow_id = workflow['workflow_id']
        url = workflow['url']
        
        try:
            logger.info(f"Scraping workflow {workflow_id} (attempt {retry_count + 1}/{MAX_RETRIES})")
            
            # Extract Layer 1 metadata
            result = await self.extractor.extract(workflow_id, url)
            
            if result['success']:
                logger.success(f"✅ Successfully scraped workflow {workflow_id}")
                return result
            else:
                logger.warning(f"⚠️ Failed to scrape workflow {workflow_id}: {result.get('error', 'Unknown error')}")
                
                # Retry if we haven't exceeded max retries
                if retry_count < MAX_RETRIES - 1:
                    self.stats['retried'] += 1
                    logger.info(f"Retrying workflow {workflow_id}...")
                    await asyncio.sleep(2)  # Wait before retry
                    return await self.scrape_workflow(workflow, retry_count + 1)
                else:
                    self.stats['failed'] += 1
                    self.failed_workflows.append({
                        'workflow_id': workflow_id,
                        'url': url,
                        'error': result.get('error', 'Unknown error')
                    })
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Exception scraping workflow {workflow_id}: {str(e)}")
            
            # Retry if we haven't exceeded max retries
            if retry_count < MAX_RETRIES - 1:
                self.stats['retried'] += 1
                logger.info(f"Retrying workflow {workflow_id} after exception...")
                await asyncio.sleep(2)
                return await self.scrape_workflow(workflow, retry_count + 1)
            else:
                self.stats['failed'] += 1
                self.failed_workflows.append({
                    'workflow_id': workflow_id,
                    'url': url,
                    'error': str(e)
                })
                return None
    
    def save_batch(self, results: List[Dict]) -> int:
        """Save a batch of results to database immediately."""
        if not results:
            return 0
        
        saved_count = 0
        
        with get_session() as session:
            for result in results:
                if not result or not result.get('success'):
                    continue
                
                workflow_id = result['workflow_id']
                data = result['data']
                
                try:
                    # Update workflow_metadata with Layer 1 data
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
                        'raw_metadata': self._format_raw_metadata(data),
                        'workflow_id': workflow_id
                    })
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save workflow {workflow_id}: {str(e)}")
                    continue
            
            # Commit the batch
            session.commit()
            logger.success(f"💾 Saved batch of {saved_count} workflows to database")
        
        return saved_count
    
    def _format_tags(self, data: Dict) -> str:
        """Format tags as JSON array."""
        import json
        node_tags = data.get('node_tags', [])
        general_tags = data.get('general_tags', [])
        all_tags = list(set(node_tags + general_tags))  # Remove duplicates
        return json.dumps(all_tags)
    
    def _format_industry(self, industry_list: List[str]) -> str:
        """Format industry list as comma-separated string."""
        if isinstance(industry_list, list) and industry_list:
            return ', '.join(industry_list)
        return 'General'
    
    def _parse_time_to_minutes(self, time_str: str) -> Optional[int]:
        """Parse time string to minutes."""
        import re
        
        if not time_str or time_str == 'Unknown':
            return None
        
        # Try to extract numbers and units
        time_str = time_str.lower()
        
        # Hours
        hours_match = re.search(r'(\d+)\s*(?:hour|hr)s?', time_str)
        if hours_match:
            return int(hours_match.group(1)) * 60
        
        # Minutes
        minutes_match = re.search(r'(\d+)\s*(?:min|minute)s?', time_str)
        if minutes_match:
            return int(minutes_match.group(1))
        
        # Seconds (convert to minutes)
        seconds_match = re.search(r'(\d+)\s*(?:sec|second)s?', time_str)
        if seconds_match:
            return max(1, int(seconds_match.group(1)) // 60)  # At least 1 minute
        
        # Days
        days_match = re.search(r'(\d+)\s*day?s?', time_str)
        if days_match:
            return int(days_match.group(1)) * 24 * 60
        
        return None
    
    def _format_raw_metadata(self, data: Dict) -> str:
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
    
    def save_progress(self, processed_count: int):
        """Save progress to file for resume capability."""
        try:
            with open(PROGRESS_FILE, 'w') as f:
                f.write(f"{processed_count}\n")
                f.write(f"{datetime.now().isoformat()}\n")
        except Exception as e:
            logger.warning(f"Could not save progress: {e}")
    
    def load_progress(self) -> int:
        """Load progress from file."""
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return int(f.readline().strip())
        except:
            return 0
    
    async def process_batch(self, workflows: List[Dict]) -> List[Dict]:
        """Process a batch of workflows in parallel."""
        tasks = [self.scrape_workflow(wf) for wf in workflows]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
    
    async def run(self, resume: bool = True):
        """Run the full Layer 1 scraping process."""
        logger.info("="*70)
        logger.info("STARTING LAYER 1 FULL DATABASE SCRAPING")
        logger.info("="*70)
        
        # Get all workflows
        all_workflows = self.get_all_workflows()
        self.stats['total'] = len(all_workflows)
        
        # Resume from previous progress if requested
        start_index = 0
        if resume:
            start_index = self.load_progress()
            if start_index > 0:
                logger.info(f"📍 Resuming from workflow {start_index}")
        
        # Process in batches
        batch_results = []
        
        for i in range(start_index, len(all_workflows), PARALLEL_WORKERS):
            batch = all_workflows[i:i + PARALLEL_WORKERS]
            batch_num = (i // PARALLEL_WORKERS) + 1
            total_batches = (len(all_workflows) + PARALLEL_WORKERS - 1) // PARALLEL_WORKERS
            
            logger.info(f"\n{'='*70}")
            logger.info(f"BATCH {batch_num}/{total_batches} - Processing workflows {i+1} to {min(i+PARALLEL_WORKERS, len(all_workflows))}")
            logger.info(f"{'='*70}")
            
            # Scrape batch in parallel
            results = await self.process_batch(batch)
            batch_results.extend(results)
            
            self.stats['processed'] += len(batch)
            self.stats['successful'] += len(results)
            
            # Save batch immediately (every BATCH_SIZE workflows or end of parallel batch)
            if len(batch_results) >= BATCH_SIZE or i + PARALLEL_WORKERS >= len(all_workflows):
                saved = self.save_batch(batch_results)
                batch_results = []  # Clear after saving
                
                # Save progress
                self.save_progress(i + len(batch))
                
                # Print statistics
                self.print_stats()
            
            # Small delay between batches to be polite
            await asyncio.sleep(1)
        
        # Save any remaining results
        if batch_results:
            self.save_batch(batch_results)
        
        # Final report
        self.print_final_report()
    
    def print_stats(self):
        """Print current statistics."""
        pct = (self.stats['processed'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        logger.info(f"\n📊 PROGRESS: {self.stats['processed']}/{self.stats['total']} ({pct:.1f}%)")
        logger.info(f"   ✅ Successful: {self.stats['successful']}")
        logger.info(f"   ❌ Failed: {self.stats['failed']}")
        logger.info(f"   🔄 Retried: {self.stats['retried']}")
    
    def print_final_report(self):
        """Print final scraping report."""
        logger.info("\n" + "="*70)
        logger.info("LAYER 1 SCRAPING COMPLETE")
        logger.info("="*70)
        logger.info(f"\n📊 FINAL STATISTICS:")
        logger.info(f"   Total workflows: {self.stats['total']}")
        logger.info(f"   Successfully scraped: {self.stats['successful']}")
        logger.info(f"   Failed: {self.stats['failed']}")
        logger.info(f"   Retry attempts: {self.stats['retried']}")
        logger.info(f"   Success rate: {self.stats['successful']/self.stats['total']*100:.1f}%")
        
        if self.failed_workflows:
            logger.warning(f"\n⚠️ FAILED WORKFLOWS ({len(self.failed_workflows)}):")
            for wf in self.failed_workflows[:10]:
                logger.warning(f"   - {wf['workflow_id']}: {wf['error'][:100]}")
            if len(self.failed_workflows) > 10:
                logger.warning(f"   ... and {len(self.failed_workflows) - 10} more")
            
            # Save failed workflows to file
            failed_file = '/app/data/layer1_failed_workflows.txt'
            with open(failed_file, 'w') as f:
                f.write("# Failed Layer 1 Workflows\n")
                f.write(f"# Total: {len(self.failed_workflows)}\n\n")
                for wf in self.failed_workflows:
                    f.write(f"{wf['workflow_id']}\t{wf['url']}\t{wf['error']}\n")
            logger.info(f"\n💾 Failed workflows saved to: {failed_file}")
        
        logger.success("\n✅ LAYER 1 SCRAPING COMPLETE!")
        logger.info("\nNext steps:")
        logger.info("  1. Review failed workflows (if any)")
        logger.info("  2. Verify database population")
        logger.info("  3. Proceed to Layer 2 scraping")

def main():
    """Main entry point."""
    scraper = Layer1FullScraper()
    asyncio.run(scraper.run(resume=True))

if __name__ == "__main__":
    main()




