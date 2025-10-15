#!/usr/bin/env python3
"""
Layer 1 Scraper to Supabase - Using Proven Methods

Uses:
1. Proven Layer 1 scraper (PageMetadataExtractor)
2. Proven database save method (SQLAlchemy ORM via WorkflowRepository)
3. Saves directly to Supabase

No SQL syntax errors, no parameter mixing - just proven, working code.
"""

import sys
sys.path.insert(0, '/app')

import asyncio
import time
from datetime import datetime
from loguru import logger

from src.storage.database import get_session
from n8n_shared.models import WorkflowMetadata, Workflow
from src.scrapers.layer1_metadata import PageMetadataExtractor
from sqlalchemy import text

class Layer1ToSupabase:
    """Layer 1 scraper using proven extractor, saving to Supabase via ORM."""
    
    def __init__(self):
        self.extractor = PageMetadataExtractor()
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0
        }
        self.start_time = time.time()
        
    def get_all_workflows(self, skip_completed=True):
        """
        Get workflows from Supabase.
        
        Args:
            skip_completed: If True, only return workflows that don't have Layer 1 data yet
        """
        with get_session() as session:
            if skip_completed:
                # Only get workflows that DON'T have Layer 1 success flag set
                # (use the layer1_success flag as the definitive indicator)
                result = session.execute(text("""
                    SELECT w.workflow_id, w.url
                    FROM workflows w
                    WHERE w.layer1_success IS NULL OR w.layer1_success = false
                    ORDER BY w.workflow_id::integer
                """))
                
                workflows = [(row[0], row[1]) for row in result]
                logger.info(f"Found {len(workflows)} workflows WITHOUT Layer 1 data (resume mode)")
                
                # Also get count of already completed workflows
                completed_result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM workflows w
                    WHERE w.layer1_success = true
                """))
                completed_count = completed_result.scalar()
                logger.info(f"Already completed: {completed_count} workflows with Layer 1 data")
                
            else:
                # Get ALL workflows (original behavior)
                result = session.execute(text("""
                    SELECT w.workflow_id, w.url
                    FROM workflows w
                    ORDER BY w.workflow_id::integer
                """))
                
                workflows = [(row[0], row[1]) for row in result]
                logger.info(f"Found {len(workflows)} total workflows in Supabase")
            
            return workflows
    
    async def scrape_and_save_workflow(self, workflow_id, url):
        """Scrape one workflow using proven Layer 1 and save to Supabase via ORM."""
        try:
            logger.info(f"🔄 Scraping workflow {workflow_id}...")
            
            # Use the PROVEN Layer 1 extractor
            result = await self.extractor.extract(workflow_id, url)
            
            if result['success']:
                # Save to Supabase using PROVEN ORM method
                self.save_to_supabase(workflow_id, result['data'])
                self.stats['successful'] += 1
                logger.success(f"✅ Workflow {workflow_id} completed and saved to Supabase")
                return True
            else:
                logger.error(f"❌ Workflow {workflow_id} extraction failed: {result.get('error', 'Unknown error')}")
                self.stats['failed'] += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception scraping workflow {workflow_id}: {str(e)}")
            self.stats['failed'] += 1
            return False
    
    def save_to_supabase(self, workflow_id, data):
        """
        Save workflow data to Supabase using PROVEN SQLAlchemy ORM method.
        This is the same approach used in WorkflowRepository.
        """
        with get_session() as session:
            try:
                # Check if metadata already exists
                existing_metadata = session.query(WorkflowMetadata).filter(
                    WorkflowMetadata.workflow_id == workflow_id
                ).first()
                
                if existing_metadata:
                    # Update existing metadata using ORM
                    existing_metadata.description = data.get('description', '')
                    existing_metadata.author_name = data.get('author', 'Unknown Author')
                    existing_metadata.use_case = data.get('use_case', '')
                    existing_metadata.views = data.get('views', 0)
                    existing_metadata.tags = self._extract_tags(data)
                    existing_metadata.workflow_created_at = self._parse_date(data.get('created_date'))
                    existing_metadata.workflow_updated_at = self._parse_date(data.get('updated_date'))
                    existing_metadata.workflow_skill_level = data.get('difficulty_level', 'intermediate')
                    existing_metadata.workflow_industry = self._format_industry(data.get('industry', []))
                    existing_metadata.workflow_estimated_time = self._parse_time_to_minutes(data.get('estimated_setup_time'))
                    existing_metadata.raw_metadata = data
                    existing_metadata.extracted_at = datetime.utcnow()
                    
                    logger.debug(f"💾 Updated existing metadata for workflow {workflow_id}")
                else:
                    # Create new metadata using ORM
                    metadata = WorkflowMetadata(
                        workflow_id=workflow_id,
                        description=data.get('description', ''),
                        author_name=data.get('author', 'Unknown Author'),
                        use_case=data.get('use_case', ''),
                        views=data.get('views', 0),
                        tags=self._extract_tags(data),
                        workflow_created_at=self._parse_date(data.get('created_date')),
                        workflow_updated_at=self._parse_date(data.get('updated_date')),
                        workflow_skill_level=data.get('difficulty_level', 'intermediate'),
                        workflow_industry=self._format_industry(data.get('industry', [])),
                        workflow_estimated_time=self._parse_time_to_minutes(data.get('estimated_setup_time')),
                        raw_metadata=data,
                        extracted_at=datetime.utcnow()
                    )
                    session.add(metadata)
                    logger.debug(f"💾 Created new metadata for workflow {workflow_id}")
                
                # Update layer1_success flag in workflows table
                workflow = session.query(Workflow).filter(
                    Workflow.workflow_id == workflow_id
                ).first()
                
                if workflow:
                    workflow.layer1_success = True
                    workflow.extracted_at = datetime.utcnow()
                    logger.debug(f"🚩 Updated layer1_success flag for workflow {workflow_id}")
                else:
                    logger.warning(f"⚠️  Workflow {workflow_id} not found in workflows table")
                
                # Commit to Supabase
                session.commit()
                logger.debug(f"✅ Saved workflow {workflow_id} to Supabase")
                
            except Exception as e:
                logger.error(f"Failed to save workflow {workflow_id} to Supabase: {str(e)}")
                session.rollback()
                raise
    
    def _extract_tags(self, data):
        """Extract tags as JSON array (proven method from repository)."""
        tags = []
        
        # Extract general tags
        general_tags = data.get('general_tags', [])
        if isinstance(general_tags, list):
            tags.extend(general_tags)
        
        # Extract node tags
        node_tags = data.get('node_tags', [])
        if isinstance(node_tags, list):
            tags.extend(node_tags)
        
        # Remove duplicates
        return list(set([tag for tag in tags if tag and isinstance(tag, str)]))
    
    def _format_industry(self, industry_list):
        """Format industry list as comma-separated string."""
        if isinstance(industry_list, list) and industry_list:
            return ', '.join(industry_list)
        return 'General'
    
    def _parse_date(self, date_str):
        """Parse date string to datetime."""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return None
    
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
    
    def print_progress(self, force=False):
        """Print current progress with visual feedback."""
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
        
        # Visual progress bar
        bar_length = 50
        filled = int(bar_length * pct / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 PROGRESS: {self.stats['processed']}/{self.stats['total']} ({pct:.1f}%) [{bar}]")
        logger.info(f"✅ Success: {self.stats['successful']} | ❌ Failed: {self.stats['failed']}")
        logger.info(f"⏱️  Elapsed: {int(elapsed//60)}m {int(elapsed%60)}s | ETA: {eta_str}")
        logger.info(f"⚡ Speed: {avg_time:.1f}s per workflow" if self.stats['processed'] > 0 else "")
        logger.info(f"{'='*80}\n")
    
    async def run(self, limit=None, skip_completed=True):
        """
        Run the Layer 1 scraping process.
        
        Args:
            limit: Optional limit on number of workflows to process
            skip_completed: If True, skip workflows that already have Layer 1 data (resume mode)
        """
        logger.info("="*70)
        logger.info("STARTING LAYER 1 SCRAPING TO SUPABASE")
        logger.info("Using proven Layer 1 extractor + proven ORM save method")
        logger.info("="*70)
        
        # Get workflows to scrape
        workflows = self.get_all_workflows(skip_completed=skip_completed)
        if limit:
            workflows = workflows[:limit]
        
        self.stats['total'] = len(workflows)
        logger.info(f"Will scrape {len(workflows)} workflows and save to Supabase")
        
        # Process each workflow
        for i, (workflow_id, url) in enumerate(workflows, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"WORKFLOW {i}/{len(workflows)}: {workflow_id}")
            logger.info(f"{'='*50}")
            
            # Scrape and save
            success = await self.scrape_and_save_workflow(workflow_id, url)
            self.stats['processed'] += 1
            
            # Print progress EVERY workflow for continuous visual feedback
            self.print_progress()
            
            # Small delay to be polite to n8n.io
            await asyncio.sleep(1)
        
        # Final report
        self.print_final_report()
    
    def print_final_report(self):
        """Print final report."""
        elapsed = time.time() - self.start_time
        logger.info("\n" + "="*70)
        logger.info("LAYER 1 SCRAPING TO SUPABASE COMPLETE")
        logger.info("="*70)
        logger.info(f"Total workflows: {self.stats['total']}")
        logger.info(f"Successfully scraped & saved: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        
        if self.stats['total'] > 0:
            logger.info(f"Success rate: {self.stats['successful']/self.stats['total']*100:.1f}%")
            logger.info(f"Total time: {int(elapsed//60)}m {int(elapsed%60)}s")
            logger.info(f"Average time per workflow: {elapsed/self.stats['total']:.1f}s")
        else:
            logger.info("✅ All workflows already have Layer 1 data - nothing to scrape!")
            logger.info(f"Check completed in: {int(elapsed)}s")

async def main():
    """Main entry point."""
    scraper = Layer1ToSupabase()
    
    # Start with a small test batch
    logger.info("Starting with first 5 workflows for testing...")
    await scraper.run(limit=5, skip_completed=False)
    
    logger.info("\n" + "="*70)
    logger.info("TEST BATCH COMPLETE")
    logger.info("="*70)
    logger.info("If this looks good, run with:")
    logger.info("  --all           Scrape all workflows (will resume from where you left off)")
    logger.info("  --all --force   Scrape all workflows from scratch (ignores completed ones)")
    logger.info("python /app/scripts/layer1_to_supabase.py --all")

if __name__ == "__main__":
    import sys
    
    if '--all' in sys.argv:
        scraper = Layer1ToSupabase()
        # By default, skip already completed workflows (resume mode)
        # Use --force to start from scratch
        skip_completed = '--force' not in sys.argv
        
        if skip_completed:
            logger.info("🔄 RESUME MODE: Will skip already completed workflows")
        else:
            logger.info("⚠️  FORCE MODE: Will re-scrape ALL workflows from scratch")
        
        asyncio.run(scraper.run(skip_completed=skip_completed))
    else:
        asyncio.run(main())

