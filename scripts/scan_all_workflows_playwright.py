#!/usr/bin/env python3
"""
Scan All Workflows with Playwright - Complete Validation

Validates ALL 6,022 workflows in the database to understand:
1. Which pages actually exist on n8n.io
2. What content/data is available on each page
3. Which workflows are deleted/private/broken
4. What useful information can be extracted

Uses Playwright for accurate page rendering and content detection.

Classification Types:
- VALID_FULL: Has iframe, button, categories, description (complete workflow)
- VALID_PARTIAL: Missing some elements but has core content
- PRIVATE: Workflow exists but is restricted/private
- DELETED: 404 or "not found" message
- REDIRECT: Redirects to another page
- ERROR: Page error or timeout
- EMPTY: Page exists but no useful content

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
import asyncio
from typing import Dict, List
from datetime import datetime
from collections import Counter
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from playwright.async_api import async_playwright

# ============================================================================
# Configuration
# ============================================================================

BATCH_SIZE = 50  # Process 50 workflows at a time
CONCURRENT_BROWSERS = 5  # 5 browser contexts simultaneously
PAGE_TIMEOUT = 20000  # 20 second timeout per page
SAVE_INTERVAL = 100  # Save progress every 100 workflows

# ============================================================================
# Workflow Page Validator
# ============================================================================

class WorkflowValidator:
    """Validates workflow pages and classifies their status."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        
    async def initialize(self):
        """Initialize Playwright."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
    
    async def cleanup(self):
        """Close browser and playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def validate_workflow(self, workflow_id: str, url: str) -> Dict:
        """
        Validate a single workflow page.
        
        Returns comprehensive page analysis.
        """
        result = {
            'workflow_id': workflow_id,
            'url': url,
            'validation_time': datetime.utcnow().isoformat(),
            
            # Page Status
            'http_status': None,
            'page_type': 'UNKNOWN',
            'is_valid': False,
            'error_message': None,
            
            # Content Detection
            'has_iframe': False,
            'has_use_button': False,
            'has_categories': False,
            'has_description': False,
            'has_author': False,
            'has_title': False,
            
            # Extracted Data
            'title': None,
            'author': None,
            'categories': [],
            'category_count': 0,
            
            # Page Analysis
            'page_text_length': 0,
            'has_error_message': False,
            'redirect_url': None,
            
            # Recommendation
            'should_keep': False,
            'recommendation': None
        }
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            # Navigate to page
            response = await page.goto(url, wait_until='domcontentloaded', timeout=PAGE_TIMEOUT)
            
            result['http_status'] = response.status
            
            # Check for redirects
            if response.url != url:
                result['redirect_url'] = response.url
                result['page_type'] = 'REDIRECT'
                result['error_message'] = f'Redirects to {response.url}'
            
            # Check HTTP status
            if response.status == 404:
                result['page_type'] = 'DELETED_404'
                result['error_message'] = 'HTTP 404 Not Found'
                result['recommendation'] = 'Mark as deleted - remove from active inventory'
                return result
            
            if response.status >= 400:
                result['page_type'] = 'HTTP_ERROR'
                result['error_message'] = f'HTTP {response.status}'
                result['recommendation'] = 'Investigate error - might be temporary'
                return result
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Extract page text
            page_text = await page.inner_text('body')
            result['page_text_length'] = len(page_text)
            
            # Check for "not found" or error messages
            if 'page not found' in page_text.lower():
                result['page_type'] = 'DELETED_SOFT_404'
                result['error_message'] = 'Page shows "not found" message'
                result['has_error_message'] = True
                result['recommendation'] = 'Mark as deleted - soft 404'
                return result
            
            if 'private workflow' in page_text.lower() or 'restricted' in page_text.lower():
                result['page_type'] = 'PRIVATE'
                result['error_message'] = 'Workflow is private/restricted'
                result['should_keep'] = True
                result['recommendation'] = 'Keep - might become public later'
                return result
            
            # Extract title
            title_elem = await page.query_selector('h1, .title, [class*="headline"]')
            if title_elem:
                result['has_title'] = True
                result['title'] = (await title_elem.inner_text()).strip()
            
            # Check for workflow iframe
            iframe = await page.query_selector('iframe.embedded_workflow_iframe, iframe[src*="n8n"], iframe[src*="workflow"]')
            if iframe:
                result['has_iframe'] = True
            
            # Check for "Use for free" button
            use_button = await page.query_selector('button:has-text("Use for free"), button:has-text("Use template")')
            if use_button:
                result['has_use_button'] = True
            
            # Extract categories
            category_links = await page.query_selector_all('a[href*="/workflows/categories/"]')
            if category_links:
                result['has_categories'] = True
                result['category_count'] = len(category_links)
                
                # Extract category names
                for link in category_links[:10]:  # Limit to first 10
                    href = await link.get_attribute('href')
                    if href:
                        # Extract category slug from href
                        slug = href.split('/categories/')[-1].rstrip('/')
                        category_name = slug.replace('-', ' ').title()
                        if category_name not in result['categories']:
                            result['categories'].append(category_name)
            
            # Check for author
            author_elem = await page.query_selector('[class*="author"], a[href*="/creators/"]')
            if author_elem:
                result['has_author'] = True
                result['author'] = (await author_elem.inner_text()).strip()
            
            # Check for description
            description = await page.query_selector('.workflow-description, .n8n-markdown, div:has-text("What this workflow does")')
            if description:
                result['has_description'] = True
            
            # Classify page type based on findings
            if result['has_iframe'] and result['has_use_button'] and result['has_categories']:
                result['page_type'] = 'VALID_FULL'
                result['is_valid'] = True
                result['should_keep'] = True
                result['recommendation'] = 'Valid complete workflow - keep and scrape'
                
            elif result['has_iframe'] and result['has_use_button']:
                result['page_type'] = 'VALID_NO_CATEGORIES'
                result['is_valid'] = True
                result['should_keep'] = True
                result['recommendation'] = 'Valid workflow but missing category tags'
                
            elif result['has_iframe']:
                result['page_type'] = 'VALID_PARTIAL'
                result['is_valid'] = True
                result['should_keep'] = True
                result['recommendation'] = 'Valid workflow with some missing elements'
                
            elif result['has_use_button'] or result['has_description']:
                result['page_type'] = 'VALID_NO_IFRAME'
                result['is_valid'] = True
                result['should_keep'] = True
                result['recommendation'] = 'Has content but iframe not detected - may need investigation'
                
            elif result['page_text_length'] < 100:
                result['page_type'] = 'EMPTY'
                result['error_message'] = 'Page has minimal content'
                result['recommendation'] = 'Investigate further - might be loading issue'
                
            else:
                result['page_type'] = 'INCOMPLETE'
                result['error_message'] = 'Missing expected workflow elements'
                result['recommendation'] = 'Investigate - page exists but missing key components'
            
        except asyncio.TimeoutError:
            result['page_type'] = 'TIMEOUT'
            result['error_message'] = 'Page load timeout'
            result['recommendation'] = 'Retry later - might be temporary network issue'
            
        except Exception as e:
            result['page_type'] = 'ERROR'
            result['error_message'] = str(e)[:200]
            result['recommendation'] = 'Investigate error'
            
        finally:
            await page.close()
            await context.close()
        
        return result

# ============================================================================
# Batch Validator
# ============================================================================

async def validate_batch(validator: WorkflowValidator, workflows: List) -> List[Dict]:
    """Validate a batch of workflows concurrently."""
    
    semaphore = asyncio.Semaphore(CONCURRENT_BROWSERS)
    
    async def bounded_validate(workflow):
        async with semaphore:
            return await validator.validate_workflow(workflow.workflow_id, workflow.url)
    
    tasks = [bounded_validate(wf) for wf in workflows]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                'workflow_id': workflows[i].workflow_id,
                'page_type': 'ERROR',
                'error_message': str(result)[:200],
                'is_valid': False
            })
        else:
            processed_results.append(result)
    
    return processed_results

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main validation logic."""
    
    print("=" * 80)
    print("🔍 COMPREHENSIVE WORKFLOW VALIDATION")
    print("=" * 80)
    print()
    print("This will scan ALL 6,022 workflows to understand:")
    print("  • Which pages actually exist")
    print("  • What content is available")
    print("  • Which workflows should be marked invalid")
    print()
    
    # Load workflows
    print("📊 Loading workflows from database...")
    
    with get_session() as session:
        workflows = session.query(Workflow).all()
        total_workflows = len(workflows)
        
        print(f"✅ Found {total_workflows} workflows to validate")
        print()
    
    # Initialize validator
    print("🚀 Initializing Playwright...")
    validator = WorkflowValidator()
    await validator.initialize()
    print("✅ Browser ready")
    print()
    
    try:
        all_results = []
        total_batches = (total_workflows + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"🔍 Validating {total_workflows} workflows in {total_batches} batches")
        print(f"   Batch size: {BATCH_SIZE}")
        print(f"   Concurrent browsers: {CONCURRENT_BROWSERS}")
        print()
        
        for i in range(0, total_workflows, BATCH_SIZE):
            batch = workflows[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            print(f"📦 Batch {batch_num}/{total_batches}: Validating {len(batch)} workflows...")
            
            # Validate batch
            batch_results = await validate_batch(validator, batch)
            all_results.extend(batch_results)
            
            # Show batch summary
            batch_types = Counter([r['page_type'] for r in batch_results])
            valid_count = sum(1 for r in batch_results if r.get('is_valid', False))
            
            print(f"   ✅ Batch complete: {valid_count}/{len(batch)} valid")
            print(f"      Types: {dict(batch_types)}")
            print()
            
            # Save progress periodically
            if (i + BATCH_SIZE) % (SAVE_INTERVAL * BATCH_SIZE) == 0 or batch_num == total_batches:
                print("💾 Saving progress...")
                save_results_to_file(all_results, f"validation_progress_{batch_num}.json")
                print(f"   ✅ Saved {len(all_results)} results")
                print()
        
        # Final summary
        print()
        print("=" * 80)
        print("📊 VALIDATION COMPLETE - COMPREHENSIVE SUMMARY")
        print("=" * 80)
        print()
        
        # Overall statistics
        print("🎯 OVERALL STATISTICS:")
        print(f"   Total workflows validated: {len(all_results)}")
        print()
        
        # Count by page type
        page_types = Counter([r['page_type'] for r in all_results])
        print("📂 PAGE TYPE DISTRIBUTION:")
        for page_type, count in sorted(page_types.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(all_results) * 100) if all_results else 0
            print(f"   {count:5d} ({pct:5.1f}%) - {page_type}")
        print()
        
        # Validity summary
        valid_count = sum(1 for r in all_results if r.get('is_valid', False))
        invalid_count = len(all_results) - valid_count
        
        print("✅ VALIDITY SUMMARY:")
        print(f"   Valid workflows:   {valid_count:5d} ({valid_count/len(all_results)*100:.1f}%)")
        print(f"   Invalid workflows: {invalid_count:5d} ({invalid_count/len(all_results)*100:.1f}%)")
        print()
        
        # Content availability
        has_iframe = sum(1 for r in all_results if r.get('has_iframe', False))
        has_categories = sum(1 for r in all_results if r.get('has_categories', False))
        has_description = sum(1 for r in all_results if r.get('has_description', False))
        
        print("📊 CONTENT AVAILABILITY:")
        print(f"   Has workflow iframe: {has_iframe:5d} ({has_iframe/len(all_results)*100:.1f}%)")
        print(f"   Has categories:      {has_categories:5d} ({has_categories/len(all_results)*100:.1f}%)")
        print(f"   Has description:     {has_description:5d} ({has_description/len(all_results)*100:.1f}%)")
        print()
        
        # Category statistics
        category_counts = Counter()
        for r in all_results:
            for cat in r.get('categories', []):
                category_counts[cat] += 1
        
        if category_counts:
            print("📂 TOP 15 CATEGORIES DISCOVERED:")
            for category, count in category_counts.most_common(15):
                print(f"   {count:5d} - {category}")
            print()
        
        # Recommendations
        should_delete = [r for r in all_results if r['page_type'] in ['DELETED_404', 'DELETED_SOFT_404']]
        should_investigate = [r for r in all_results if r['page_type'] in ['ERROR', 'TIMEOUT', 'EMPTY', 'INCOMPLETE']]
        
        print("🎯 RECOMMENDATIONS:")
        print(f"   ❌ Delete (404/deleted):     {len(should_delete)} workflows")
        print(f"   ⚠️  Investigate (errors):     {len(should_investigate)} workflows")
        print(f"   ✅ Keep (valid):              {valid_count} workflows")
        print()
        
        # Save final results
        print("💾 Saving final results...")
        output_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_results_to_file(all_results, output_file)
        print(f"   ✅ Results saved to: {output_file}")
        print()
        
        # Show workflows to delete
        if should_delete:
            print("❌ WORKFLOWS TO MARK AS DELETED:")
            print()
            for r in should_delete[:20]:
                print(f"   • {r['workflow_id']}: {r['error_message']}")
            if len(should_delete) > 20:
                print(f"   ... and {len(should_delete) - 20} more")
            print()
        
        # Show workflows needing investigation
        if should_investigate and len(should_investigate) <= 20:
            print("⚠️  WORKFLOWS NEEDING INVESTIGATION:")
            print()
            for r in should_investigate:
                print(f"   • {r['workflow_id']}: {r['page_type']} - {r.get('error_message', 'No error message')}")
            print()
        
        print("=" * 80)
        print("🎉 VALIDATION SCAN COMPLETE!")
        print("=" * 80)
        print()
        
    finally:
        await validator.cleanup()

def save_results_to_file(results: List[Dict], filename: str):
    """Save validation results to JSON file."""
    output_path = Path(filename)
    with open(output_path, 'w') as f:
        json.dump({
            'validation_date': datetime.now().isoformat(),
            'total_workflows': len(results),
            'results': results
        }, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())


