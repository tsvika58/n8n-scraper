#!/usr/bin/env python3
"""
Extract All Workflow Titles from Pages

Extracts the actual page titles for all 6,022 workflows using HTTP requests.

Title Extraction Priority:
1. <h1> tag content (primary title on page)
2. Meta tag: twitter:title
3. Meta tag: og:title
4. Fallback: URL slug converted to title

Updates workflow_metadata.title for all workflows.

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
import asyncio
import aiohttp
import re
from typing import Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text

# ============================================================================
# Configuration
# ============================================================================

BATCH_SIZE = 50
CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 20

# ============================================================================
# Title Extractor
# ============================================================================

class TitleExtractor:
    """Extracts workflow titles from pages."""
    
    def __init__(self):
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
    
    async def cleanup(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    def extract_slug_title(self, url: str) -> str:
        """
        Extract title from URL slug as fallback.
        
        Example: '/workflows/7423-lead-generation-agent/' -> 'Lead Generation Agent'
        """
        if '/workflows/' not in url:
            return 'Unknown Workflow'
        
        slug = url.split('/workflows/')[-1].rstrip('/')
        
        if '-' in slug:
            parts = slug.split('-')
            if parts[0].isdigit():
                slug = '-'.join(parts[1:])
        
        # Convert to title case
        title = slug.replace('-', ' ').title()
        return title
    
    async def extract_title(self, url: str, workflow_id: str) -> Dict:
        """
        Extract title from workflow page.
        
        Returns:
        {
            'workflow_id': '7423',
            'title': 'Lead Generation Agent',
            'source': 'h1' | 'meta_twitter' | 'meta_og' | 'slug',
            'success': True/False
        }
        """
        result = {
            'workflow_id': workflow_id,
            'title': None,
            'source': None,
            'success': False
        }
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    # Use slug fallback
                    result['title'] = self.extract_slug_title(url)
                    result['source'] = 'slug_fallback'
                    result['success'] = True
                    return result
                
                html = await response.text()
                
                # Priority 1: Extract from <h1> tag
                h1_pattern = r'<h1[^>]*>([^<]+)</h1>'
                h1_match = re.search(h1_pattern, html)
                if h1_match:
                    title = h1_match.group(1).strip()
                    # Clean up HTML entities
                    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    if len(title) > 3:  # Sanity check
                        result['title'] = title
                        result['source'] = 'h1'
                        result['success'] = True
                        return result
                
                # Priority 2: Extract from twitter:title meta tag
                twitter_pattern = r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']+)["\']'
                twitter_match = re.search(twitter_pattern, html)
                if twitter_match:
                    title = twitter_match.group(1).strip()
                    # Remove template suffix
                    title = title.replace(' | n8n workflow template', '')
                    title = title.replace(' - n8n', '')
                    if len(title) > 3:
                        result['title'] = title
                        result['source'] = 'meta_twitter'
                        result['success'] = True
                        return result
                
                # Priority 3: Extract from og:title meta tag
                og_pattern = r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']'
                og_match = re.search(og_pattern, html)
                if og_match:
                    title = og_match.group(1).strip()
                    title = title.replace(' | n8n workflow template', '')
                    title = title.replace(' - n8n', '')
                    if len(title) > 3:
                        result['title'] = title
                        result['source'] = 'meta_og'
                        result['success'] = True
                        return result
                
                # Priority 4: Fallback to slug
                result['title'] = self.extract_slug_title(url)
                result['source'] = 'slug_fallback'
                result['success'] = True
                return result
                
        except asyncio.TimeoutError:
            result['title'] = self.extract_slug_title(url)
            result['source'] = 'slug_timeout'
            result['success'] = True
            return result
            
        except Exception as e:
            result['title'] = self.extract_slug_title(url)
            result['source'] = 'slug_error'
            result['success'] = True
            return result
        
        return result

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    print('=' * 80)
    print('📝 EXTRACTING ALL WORKFLOW TITLES')
    print('=' * 80)
    print()
    
    # Load workflows
    with get_session() as session:
        from src.storage.models import Workflow
        workflows = session.query(Workflow).all()
        total = len(workflows)
        print(f'✅ Found {total} workflows to process')
        print()
    
    # Initialize extractor
    print('🚀 Initializing HTTP session...')
    extractor = TitleExtractor()
    await extractor.initialize()
    print('✅ Session ready')
    print()
    
    try:
        print(f'📝 Extracting titles for {total} workflows...')
        print(f'   Batch size: {BATCH_SIZE}')
        print(f'   Concurrent requests: {CONCURRENT_REQUESTS}')
        print()
        
        all_results = []
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        
        for i in range(0, total, BATCH_SIZE):
            batch = workflows[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            print(f'📦 Batch {batch_num}/{total_batches}: Processing {len(batch)} workflows...')
            
            # Create tasks for concurrent processing
            semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
            
            async def bounded_extract(workflow):
                async with semaphore:
                    return await extractor.extract_title(workflow.url, workflow.workflow_id)
            
            tasks = [bounded_extract(wf) for wf in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful = 0
            for result in batch_results:
                if isinstance(result, Exception):
                    continue
                if result.get('success'):
                    successful += 1
                    all_results.append(result)
            
            print(f'   ✅ Batch {batch_num} complete: {successful}/{len(batch)} titles extracted')
            
            # Save to database periodically
            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f'   💾 Saving batch to database...')
                with get_session() as session:
                    for result in all_results[-len(batch_results):]:
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
                    
                    session.commit()
                    print(f'   ✅ Saved to database')
            
            print()
        
        # Final summary
        print()
        print('=' * 80)
        print('📊 TITLE EXTRACTION COMPLETE')
        print('=' * 80)
        print(f'Total workflows: {total}')
        print(f'Titles extracted: {len(all_results)}')
        print()
        
        # Count by source
        from collections import Counter
        sources = Counter([r['source'] for r in all_results if not isinstance(r, Exception)])
        
        print('📊 Title Sources:')
        for source, count in sources.most_common():
            pct = (count / len(all_results) * 100) if all_results else 0
            print(f'   {count:5d} ({pct:5.1f}%) - {source}')
        
        print()
        
        # Verify in database
        with get_session() as session:
            result = session.execute(text('''
                SELECT COUNT(*) 
                FROM workflow_metadata 
                WHERE title IS NOT NULL AND title != ''
            '''))
            count_with_title = result.scalar()
            
            print(f'✅ Database verification: {count_with_title}/{total} workflows have titles')
            print()
        
        print('=' * 80)
        print('🎉 ALL TITLES UPDATED!')
        print('=' * 80)
        print()
        
    finally:
        await extractor.cleanup()

if __name__ == '__main__':
    asyncio.run(main())

