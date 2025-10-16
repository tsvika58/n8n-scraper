#!/usr/bin/env python3
"""
Debug Layer 1 selectors to see what's actually on the page
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_layer1_selectors():
    """Debug what selectors are finding on the n8n page."""
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("\n🔍 TESTING TITLE SELECTORS...")
        title_selectors = [
            'h1',
            '[data-test-id="workflow-title"]',
            '.workflow-title',
            'header h1',
            'main h1',
            '.n8n-markdown h1',
            'h1:not([class*="sticky"])'
        ]
        
        for selector in title_selectors:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} elements")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    text = await elem.text_content()
                    print(f"    {i+1}. '{text[:50]}...'")
            except Exception as e:
                print(f"  {selector}: ERROR - {e}")
        
        print("\n🔍 TESTING AUTHOR SELECTORS...")
        author_selectors = [
            'a[href*="/users/"]',
            '[data-test-id="workflow-author"]',
            '.author-name',
            'a.author',
            '[class*="author"]',
            'div:has-text("Created by")',
            'span:has-text("Created by")'
        ]
        
        for selector in author_selectors:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} elements")
                for i, elem in enumerate(elements[:3]):
                    text = await elem.text_content()
                    print(f"    {i+1}. '{text[:50]}...'")
            except Exception as e:
                print(f"  {selector}: ERROR - {e}")
        
        print("\n🔍 TESTING CATEGORY SELECTORS...")
        category_selectors = [
            'button:has-text("Lead Generation")',
            'button:has-text("Multimodal AI")',
            '[class*="category"]',
            '.category-badge',
            '.category',
            '[data-test-id="category"]',
            'div:has-text("Categories")',
            'span:has-text("Lead Generation")',
            'span:has-text("Multimodal AI")'
        ]
        
        for selector in category_selectors:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} elements")
                for i, elem in enumerate(elements[:3]):
                    text = await elem.text_content()
                    print(f"    {i+1}. '{text[:50]}...'")
            except Exception as e:
                print(f"  {selector}: ERROR - {e}")
        
        print("\n🔍 TESTING NODES SELECTORS...")
        nodes_selectors = [
            '#__nuxt > section > div > div.relative.z-10 > div > div.lg\\:w-4\\/12 > div > ul',
            'ul:has(li[class*="node"])',
            'div:has-text("+") ul',
            '[class*="node"]',
            'ul li img[alt*="Google Sheets"]',
            'ul li img[alt*="HTTP"]'
        ]
        
        for selector in nodes_selectors:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} elements")
                for i, elem in enumerate(elements[:3]):
                    # Check for images with alt text
                    imgs = await elem.query_selector_all('img')
                    for img in imgs[:3]:
                        alt = await img.get_attribute('alt')
                        if alt:
                            print(f"    IMG: '{alt}'")
                    # Check text content
                    text = await elem.text_content()
                    if text and len(text.strip()) > 2:
                        print(f"    TEXT: '{text[:50]}...'")
            except Exception as e:
                print(f"  {selector}: ERROR - {e}")
        
        print("\n🔍 TESTING DESCRIPTION SELECTORS...")
        desc_selectors = [
            'meta[name="description"]',
            '[data-test-id="workflow-description"]',
            '.workflow-description',
            'p.description',
            '.n8n-markdown',
            'div:has-text("Setup Guide")',
            'div:has-text("What this workflow does")',
            'div:has-text("Who this is for")',
            'h2:has-text("Setup Guide") + div',
            'h2:has-text("What this workflow does") + div'
        ]
        
        for selector in desc_selectors:
            try:
                if selector.startswith('meta'):
                    element = await page.query_selector(selector)
                    if element:
                        content = await element.get_attribute('content')
                        print(f"  {selector}: '{content[:50]}...'")
                else:
                    elements = await page.query_selector_all(selector)
                    print(f"  {selector}: {len(elements)} elements")
                    for i, elem in enumerate(elements[:2]):
                        text = await elem.text_content()
                        if text and len(text.strip()) > 10:
                            print(f"    {i+1}. '{text[:100]}...'")
            except Exception as e:
                print(f"  {selector}: ERROR - {e}")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(debug_layer1_selectors())




