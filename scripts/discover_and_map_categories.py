#!/usr/bin/env python3
"""
Category Discovery and Mapping

Crawls all 6,022 workflow pages to discover and map categories.

This script:
1. Extracts category links from each workflow page
2. Stores categories in workflow_metadata.categories (JSONB array)
3. Builds a complete category index
4. Creates category analytics

Strategy:
- Uses lightweight HTTP requests (no Playwright)
- Extracts categories using regex pattern matching
- Batch processing for efficiency
- UPSERT logic to preserve existing metadata

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
import asyncio
import aiohttp
import re
from typing import List, Dict, Set
from datetime import datetime
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from sqlalchemy import text

# ============================================================================
# Configuration
# ============================================================================

BATCH_SIZE = 50  # Process 50 workflows at a time
CONCURRENT_REQUESTS = 10  # 10 simultaneous HTTP requests
REQUEST_TIMEOUT = 30  # 30 second timeout per request

# ============================================================================
# Category Extractor
# ============================================================================

class CategoryExtractor:
    """Extracts categories from workflow page HTML."""
    
    def __init__(self):
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        )
    
    async def cleanup(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def extract_categories(self, url: str) -> List[str]:
        """
        Extract category names from workflow page.
        
        Returns list of category names (not slugs).
        Example: ["Lead Generation", "Multimodal AI"]
        """
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                
                # Extract category links
                # Pattern: href="/workflows/categories/{slug}/"
                pattern = r'href="/workflows/categories/([^"]+)/"'
                matches = re.findall(pattern, html)
                
                if not matches:
                    return []
                
                # Convert slugs to display names
                categories = []
                for slug in matches:
                    # Convert slug to title case
                    # Example: "lead-generation" -> "Lead Generation"
                    name = slug.replace('-', ' ').title()
                    categories.append(name)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_categories = []
                for cat in categories:
                    if cat not in seen:
                        seen.add(cat)
                        unique_categories.append(cat)
                
                return unique_categories
                
        except asyncio.TimeoutError:
            print(f"      ⏱️  Timeout extracting categories from {url}")
            return []
        except Exception as e:
            print(f"      ❌ Error extracting categories from {url}: {e}")
            return []

# ============================================================================
# Category Discovery Orchestrator
# ============================================================================

class CategoryDiscovery:
    """Orchestrates category discovery across all workflows."""
    
    def __init__(self):
        self.extractor = CategoryExtractor()
        self.all_categories = Counter()  # Category name -> count
        self.stats = {
            'total_workflows': 0,
            'processed': 0,
            'with_categories': 0,
            'without_categories': 0,
            'errors': 0
        }
    
    async def process_batch(self, workflows: List[Workflow]) -> Dict:
        """Process a batch of workflows to extract categories."""
        batch_results = []
        
        # Create tasks for concurrent processing
        tasks = []
        for workflow in workflows:
            task = self.process_workflow(workflow)
            tasks.append(task)
        
        # Execute concurrently (limited by semaphore)
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        
        async def bounded_task(workflow, task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[bounded_task(wf, task) for wf, task in zip(workflows, tasks)],
            return_exceptions=True
        )
        
        return results
    
    async def process_workflow(self, workflow: Workflow) -> Dict:
        """Extract categories for a single workflow."""
        try:
            categories = await self.extractor.extract_categories(workflow.url)
            
            # Update statistics
            if categories:
                self.stats['with_categories'] += 1
                for cat in categories:
                    self.all_categories[cat] += 1
            else:
                self.stats['without_categories'] += 1
            
            self.stats['processed'] += 1
            
            return {
                'workflow_id': workflow.workflow_id,
                'categories': categories,
                'success': True
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            return {
                'workflow_id': workflow.workflow_id,
                'categories': [],
                'success': False,
                'error': str(e)
            }
    
    async def run(self):
        """Main execution method."""
        print("=" * 80)
        print("🗺️  CATEGORY DISCOVERY AND MAPPING")
        print("=" * 80)
        print()
        
        # Initialize
        await self.extractor.initialize()
        
        try:
            # Get all workflows from database
            with get_session() as session:
                print("📊 Loading workflows from database...")
                workflows = session.query(Workflow).all()
                self.stats['total_workflows'] = len(workflows)
                print(f"✅ Found {len(workflows)} workflows to process")
                print()
                
                # Process in batches
                total_batches = (len(workflows) + BATCH_SIZE - 1) // BATCH_SIZE
                
                print(f"🚀 Processing {len(workflows)} workflows in {total_batches} batches")
                print(f"   Batch size: {BATCH_SIZE}")
                print(f"   Concurrent requests: {CONCURRENT_REQUESTS}")
                print()
                
                for i in range(0, len(workflows), BATCH_SIZE):
                    batch = workflows[i:i+BATCH_SIZE]
                    batch_num = (i // BATCH_SIZE) + 1
                    
                    print(f"📦 Batch {batch_num}/{total_batches}: Processing {len(batch)} workflows...")
                    
                    # Extract categories for batch
                    results = await self.process_batch(batch)
                    
                    # Save results to database
                    for result in results:
                        if isinstance(result, Exception):
                            continue
                        
                        if not result['success']:
                            continue
                        
                        workflow_id = result['workflow_id']
                        categories = result['categories']
                        
                        # Check if metadata exists
                        metadata = session.query(WorkflowMetadata).filter_by(
                            workflow_id=workflow_id
                        ).first()
                        
                        if metadata:
                            # Update existing metadata
                            metadata.categories = categories
                            metadata.extracted_at = datetime.utcnow()
                        else:
                            # Create new metadata
                            metadata = WorkflowMetadata(
                                workflow_id=workflow_id,
                                categories=categories,
                                extracted_at=datetime.utcnow()
                            )
                            session.add(metadata)
                    
                    # Commit batch
                    session.commit()
                    
                    print(f"   ✅ Batch {batch_num} complete: {self.stats['processed']}/{self.stats['total_workflows']} workflows processed")
                    print(f"      With categories: {self.stats['with_categories']} | Without: {self.stats['without_categories']} | Errors: {self.stats['errors']}")
                    print()
                
                print()
                print("=" * 80)
                print("📊 DISCOVERY COMPLETE")
                print("=" * 80)
                print(f"Total workflows:        {self.stats['total_workflows']}")
                print(f"Successfully processed: {self.stats['processed']}")
                print(f"With categories:        {self.stats['with_categories']}")
                print(f"Without categories:     {self.stats['without_categories']}")
                print(f"Errors:                 {self.stats['errors']}")
                print()
                
                # Show discovered categories
                print("=" * 80)
                print("📂 DISCOVERED CATEGORIES")
                print("=" * 80)
                print(f"Total unique categories: {len(self.all_categories)}")
                print()
                print("Top 20 categories by workflow count:")
                for category, count in self.all_categories.most_common(20):
                    print(f"   {count:4d} workflows - {category}")
                print()
                
                if len(self.all_categories) > 20:
                    print(f"   ... and {len(self.all_categories) - 20} more categories")
                    print()
                
                # Show category coverage
                coverage_pct = (self.stats['with_categories'] / self.stats['total_workflows'] * 100) if self.stats['total_workflows'] > 0 else 0
                print(f"📈 Category Coverage: {coverage_pct:.1f}%")
                print()
                
                print("=" * 80)
                print("🎉 CATEGORY MAPPING COMPLETE!")
                print("=" * 80)
                print()
                
        finally:
            await self.extractor.cleanup()

# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main execution."""
    discovery = CategoryDiscovery()
    await discovery.run()

if __name__ == "__main__":
    asyncio.run(main())





