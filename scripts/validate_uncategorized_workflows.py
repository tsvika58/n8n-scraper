#!/usr/bin/env python3
"""
Validate Uncategorized Workflows

Investigates the 54 workflows that have no categories to determine:
1. Are they valid workflow pages?
2. Do they have useful content?
3. Should they be marked as invalid/NAN?
4. What patterns/issues exist?

Uses Playwright to visually inspect page content and classify page types.

Author: N8N Scraper System
Date: October 13, 2025
"""

import sys
from pathlib import Path
import asyncio
from typing import Dict, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import get_session
from src.storage.models import Workflow, WorkflowMetadata
from playwright.async_api import async_playwright

# ============================================================================
# Page Type Classifier
# ============================================================================

class PageValidator:
    """Validates workflow pages using Playwright."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        
    async def initialize(self):
        """Initialize Playwright browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
    
    async def cleanup(self):
        """Close browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def validate_page(self, workflow_id: str, url: str) -> Dict:
        """
        Validate a workflow page and classify its type.
        
        Returns:
        {
            'workflow_id': '1234',
            'url': 'https://...',
            'page_type': 'valid_workflow' | '404_not_found' | 'redirect' | 'private' | 'deleted' | 'empty',
            'has_iframe': True/False,
            'has_categories': True/False,
            'has_description': True/False,
            'has_use_button': True/False,
            'title': 'Page title',
            'error_message': 'Error message if any',
            'should_keep': True/False
        }
        """
        result = {
            'workflow_id': workflow_id,
            'url': url,
            'page_type': 'unknown',
            'has_iframe': False,
            'has_categories': False,
            'has_description': False,
            'has_use_button': False,
            'title': None,
            'error_message': None,
            'should_keep': False,
            'notes': []
        }
        
        page = await self.context.new_page()
        
        try:
            # Navigate to page
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Check HTTP status
            if response.status == 404:
                result['page_type'] = '404_not_found'
                result['error_message'] = 'Page not found (404)'
                result['notes'].append('Workflow deleted or never existed')
                return result
            
            if response.status >= 400:
                result['page_type'] = 'http_error'
                result['error_message'] = f'HTTP {response.status}'
                result['notes'].append(f'Server returned error code {response.status}')
                return result
            
            # Wait a bit for dynamic content
            await page.wait_for_timeout(2000)
            
            # Extract page title
            title_element = await page.query_selector('h1')
            if title_element:
                result['title'] = await title_element.inner_text()
            
            # Check for error messages or "not found" indicators
            page_text = await page.inner_text('body')
            
            if 'page not found' in page_text.lower() or 'not found' in page_text.lower():
                result['page_type'] = 'not_found_page'
                result['error_message'] = 'Page shows "not found" message'
                result['notes'].append('Soft 404 - page exists but shows not found message')
                return result
            
            if 'private' in page_text.lower() and 'workflow' in page_text.lower():
                result['page_type'] = 'private_workflow'
                result['error_message'] = 'Workflow is private'
                result['notes'].append('Workflow exists but is private/restricted')
                result['should_keep'] = True  # Might become public later
                return result
            
            # Check for workflow iframe (main indicator of valid workflow)
            iframe = await page.query_selector('iframe.embedded_workflow_iframe')
            if iframe:
                result['has_iframe'] = True
                result['notes'].append('Has workflow iframe - likely valid')
            
            # Check for "Use for free" button
            use_button = await page.query_selector('button:has-text("Use for free")')
            if use_button:
                result['has_use_button'] = True
                result['notes'].append('Has "Use for free" button')
            
            # Check for categories section
            category_links = await page.query_selector_all('a[href*="/workflows/categories/"]')
            if category_links:
                result['has_categories'] = True
                result['notes'].append(f'Found {len(category_links)} category links')
            
            # Check for description/content
            description = await page.query_selector('.workflow-description, .n8n-markdown, div:has-text("What this workflow does")')
            if description:
                result['has_description'] = True
                result['notes'].append('Has workflow description')
            
            # Check if page is just a redirect or placeholder
            if len(page_text.strip()) < 100:
                result['page_type'] = 'empty_page'
                result['error_message'] = 'Page has very little content'
                result['notes'].append('Page exists but has minimal content')
                return result
            
            # Classify based on findings
            if result['has_iframe'] and result['has_use_button']:
                result['page_type'] = 'valid_workflow'
                result['should_keep'] = True
                result['notes'].append('✅ Valid workflow page with iframe and button')
            elif result['has_iframe']:
                result['page_type'] = 'valid_workflow_no_button'
                result['should_keep'] = True
                result['notes'].append('✅ Valid workflow page with iframe (no button)')
            elif result['has_description'] and result['has_use_button']:
                result['page_type'] = 'valid_no_iframe'
                result['should_keep'] = True
                result['notes'].append('⚠️ Has content but no iframe - might be loading issue')
            else:
                result['page_type'] = 'incomplete_page'
                result['error_message'] = 'Missing expected workflow elements'
                result['notes'].append('⚠️ Page exists but missing key workflow components')
            
        except Exception as e:
            result['page_type'] = 'validation_error'
            result['error_message'] = str(e)
            result['notes'].append(f'Error during validation: {str(e)[:100]}')
            
        finally:
            await page.close()
        
        return result

# ============================================================================
# Main Validation
# ============================================================================

async def main():
    """Main validation logic."""
    
    print("=" * 80)
    print("🔍 VALIDATING UNCATEGORIZED WORKFLOWS")
    print("=" * 80)
    print()
    
    # Get uncategorized workflows
    print("📊 Loading uncategorized workflows...")
    
    with get_session() as session:
        # Get workflows with empty or null categories
        uncategorized = session.query(Workflow, WorkflowMetadata).outerjoin(
            WorkflowMetadata,
            Workflow.workflow_id == WorkflowMetadata.workflow_id
        ).filter(
            (WorkflowMetadata.categories.is_(None)) | 
            (WorkflowMetadata.categories == [])
        ).all()
        
        print(f"✅ Found {len(uncategorized)} uncategorized workflows")
        print()
        
        if not uncategorized:
            print("🎉 All workflows have categories!")
            return
        
        # Initialize validator
        print("🚀 Initializing Playwright browser...")
        validator = PageValidator()
        await validator.initialize()
        
        try:
            print("✅ Browser ready")
            print()
            
            results = []
            
            print(f"🔍 Validating {len(uncategorized)} workflows...")
            print()
            
            for i, (workflow, metadata) in enumerate(uncategorized, 1):
                print(f"[{i}/{len(uncategorized)}] Validating workflow {workflow.workflow_id}...")
                
                result = await validator.validate_page(workflow.workflow_id, workflow.url)
                results.append(result)
                
                # Show result
                print(f"    Type: {result['page_type']}")
                print(f"    Title: {result['title']}")
                print(f"    Should keep: {'✅ YES' if result['should_keep'] else '❌ NO'}")
                if result['error_message']:
                    print(f"    Error: {result['error_message']}")
                print(f"    Notes: {'; '.join(result['notes'])}")
                print()
                
                # Small delay between requests
                await asyncio.sleep(0.5)
            
            # Summary
            print()
            print("=" * 80)
            print("📊 VALIDATION SUMMARY")
            print("=" * 80)
            print()
            
            # Count by page type
            from collections import Counter
            page_types = Counter([r['page_type'] for r in results])
            
            print("Page Type Distribution:")
            for page_type, count in page_types.most_common():
                print(f"   {count:3d} - {page_type}")
            
            print()
            
            # Count recommendations
            should_keep = sum(1 for r in results if r['should_keep'])
            should_remove = len(results) - should_keep
            
            print("Recommendations:")
            print(f"   ✅ Keep:   {should_keep} workflows (have useful content)")
            print(f"   ❌ Remove: {should_remove} workflows (404, deleted, empty)")
            print()
            
            # Show workflows to remove
            if should_remove > 0:
                print("❌ Workflows to mark as INVALID:")
                print()
                for r in results:
                    if not r['should_keep']:
                        print(f"   • {r['workflow_id']}: {r['page_type']} - {r['error_message']}")
                print()
            
            # Show workflows to keep
            if should_keep > 0:
                print("✅ Workflows to KEEP (have useful content):")
                print()
                for r in results:
                    if r['should_keep']:
                        print(f"   • {r['workflow_id']}: {r['page_type']} - {r['title']}")
                print()
            
            print("=" * 80)
            print("🎉 VALIDATION COMPLETE!")
            print("=" * 80)
            print()
            
        finally:
            await validator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())





