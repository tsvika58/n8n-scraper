#!/usr/bin/env python3
"""
Complete Title Extraction - Resume from Progress

Extracts titles only for workflows that don't have them yet.
Simple, robust, saves immediately.
"""

import sys
from pathlib import Path
import asyncio
import aiohttp
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text

async def extract_title(session_obj, url: str) -> str:
    """Extract title from page or URL."""
    try:
        async with session_obj.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                # Use slug
                slug = url.split('/workflows/')[-1].rstrip('/')
                return '-'.join(slug.split('-')[1:]).replace('-', ' ').title() if '-' in slug else 'Unknown'
            
            html = await response.text()
            
            # Try twitter:title
            match = re.search(r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']+)["\']', html)
            if match:
                return match.group(1).replace(' | n8n workflow template', '').strip()
            
            # Try h1
            match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
            if match:
                return match.group(1).strip().replace('&amp;', '&')
            
            # Fallback to slug
            slug = url.split('/workflows/')[-1].rstrip('/')
            return '-'.join(slug.split('-')[1:]).replace('-', ' ').title() if '-' in slug else 'Unknown'
            
    except:
        slug = url.split('/workflows/')[-1].rstrip('/')
        return '-'.join(slug.split('-')[1:]).replace('-', ' ').title() if '-' in slug else 'Unknown'

async def main():
    print('🔄 Completing title extraction...')
    print()
    
    # Get workflows without titles
    with get_session() as session:
        result = session.execute(text('''
            SELECT w.workflow_id, w.url
            FROM workflows w
            LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            WHERE wm.title IS NULL OR wm.title = ''
        '''))
        
        missing = [(row[0], row[1]) for row in result]
    
    print(f'Found {len(missing)} workflows without titles')
    
    if not missing:
        print('✅ All workflows have titles!')
        return
    
    print()
    
    # Extract titles
    async with aiohttp.ClientSession() as http_session:
        for i, (wf_id, url) in enumerate(missing, 1):
            print(f'[{i}/{len(missing)}] Extracting {wf_id}...', end=' ')
            
            title = await extract_title(http_session, url)
            
            # Save immediately
            with get_session() as session:
                metadata = session.query(WorkflowMetadata).filter_by(workflow_id=wf_id).first()
                if metadata:
                    metadata.title = title
                else:
                    metadata = WorkflowMetadata(workflow_id=wf_id, title=title)
                    session.add(metadata)
                session.commit()
            
            print(f'✅ {title[:50]}')
            
            if i % 100 == 0:
                print()
    
    print()
    print(f'✅ Completed {len(missing)} titles')

if __name__ == '__main__':
    asyncio.run(main())





