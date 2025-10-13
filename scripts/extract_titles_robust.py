#!/usr/bin/env python3
"""
Extract All Workflow Titles - Robust Version

Extracts titles for all 6,022 workflows with robust database saving.
Saves after EVERY batch to prevent data loss.

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
import asyncio
import aiohttp
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text

BATCH_SIZE = 50
CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 15

class TitleExtractor:
    """Extracts workflow titles from pages."""
    
    def __init__(self):
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        )
    
    async def cleanup(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    def extract_slug_title(self, url: str) -> str:
        """Extract title from URL slug as fallback."""
        if '/workflows/' not in url:
            return 'Unknown Workflow'
        
        slug = url.split('/workflows/')[-1].rstrip('/')
        if '-' in slug:
            parts = slug.split('-')
            if parts[0].isdigit():
                slug = '-'.join(parts[1:])
        
        return slug.replace('-', ' ').title()
    
    async def extract_title(self, url: str, workflow_id: str) -> dict:
        """Extract title from workflow page."""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        'workflow_id': workflow_id,
                        'title': self.extract_slug_title(url),
                        'source': 'slug_fallback'
                    }
                
                html = await response.text()
                
                # Try h1
                h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
                if h1_match:
                    title = h1_match.group(1).strip()
                    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    if len(title) > 3:
                        return {'workflow_id': workflow_id, 'title': title, 'source': 'h1'}
                
                # Try twitter:title
                twitter_match = re.search(r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']+)["\']', html)
                if twitter_match:
                    title = twitter_match.group(1).strip()
                    title = title.replace(' | n8n workflow template', '').replace(' - n8n', '')
                    if len(title) > 3:
                        return {'workflow_id': workflow_id, 'title': title, 'source': 'meta_twitter'}
                
                # Fallback to slug
                return {
                    'workflow_id': workflow_id,
                    'title': self.extract_slug_title(url),
                    'source': 'slug_fallback'
                }
                
        except Exception:
            return {
                'workflow_id': workflow_id,
                'title': self.extract_slug_title(url),
                'source': 'slug_error'
            }

async def process_batch(extractor, workflows):
    """Process a batch with concurrency control."""
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    
    async def bounded_extract(wf):
        async with semaphore:
            return await extractor.extract_title(wf.url, wf.workflow_id)
    
    tasks = [bounded_extract(wf) for wf in workflows]
    return await asyncio.gather(*tasks, return_exceptions=True)

def save_batch_to_db(results):
    """Save a batch of results to database immediately."""
    saved = 0
    with get_session() as session:
        for result in results:
            if isinstance(result, Exception):
                continue
            
            workflow_id = result['workflow_id']
            title = result['title']
            
            # Update or create metadata
            metadata = session.query(WorkflowMetadata).filter_by(
                workflow_id=workflow_id
            ).first()
            
            if metadata:
                metadata.title = title
            else:
                metadata = WorkflowMetadata(
                    workflow_id=workflow_id,
                    title=title
                )
                session.add(metadata)
            
            saved += 1
        
        session.commit()
    
    return saved

async def main():
    print('=' * 80)
    print('📝 EXTRACTING ALL WORKFLOW TITLES (ROBUST VERSION)')
    print('=' * 80)
    print()
    
    # Load workflows
    with get_session() as session:
        workflows = session.query(Workflow).all()
        total = len(workflows)
    
    print(f'✅ Found {total} workflows')
    print()
    
    # Initialize
    extractor = TitleExtractor()
    await extractor.initialize()
    
    try:
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        stats = {'h1': 0, 'meta_twitter': 0, 'meta_og': 0, 'slug_fallback': 0, 'slug_error': 0, 'slug_timeout': 0}
        
        for i in range(0, total, BATCH_SIZE):
            batch = workflows[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            print(f'📦 Batch {batch_num}/{total_batches}: Processing {len(batch)} workflows...')
            
            # Extract titles
            results = await process_batch(extractor, batch)
            
            # Count sources
            for r in results:
                if isinstance(r, dict) and 'source' in r:
                    stats[r['source']] = stats.get(r['source'], 0) + 1
            
            # Save to database IMMEDIATELY after EVERY batch
            print(f'   💾 Saving batch {batch_num} to database...')
            saved = save_batch_to_db(results)
            
            print(f'   ✅ Batch {batch_num}: Extracted and saved {saved}/{len(batch)} titles')
            print()
        
        print()
        print('=' * 80)
        print('📊 EXTRACTION COMPLETE')
        print('=' * 80)
        print()
        print('Title Sources:')
        for source, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                pct = (count / total * 100)
                print(f'   {count:5d} ({pct:5.1f}%) - {source}')
        
        print()
        
        # Final verification
        with get_session() as session:
            result = session.execute(text('''
                SELECT COUNT(*) 
                FROM workflow_metadata 
                WHERE title IS NOT NULL AND title != ''
            '''))
            final_count = result.scalar()
            
            print(f'✅ Final count: {final_count}/{total} workflows have titles')
            print()
        
        print('=' * 80)
        print('🎉 ALL TITLES EXTRACTED AND SAVED!')
        print('=' * 80)
        print()
        
    finally:
        await extractor.cleanup()

if __name__ == '__main__':
    asyncio.run(main())

