#!/usr/bin/env python3
"""
Debug workflow 7423 scraping
Run with headless=False to see what the browser actually loads
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_workflow_7423():
    """Debug workflow 7423 to see what's actually on the page."""
    
    print("🔍 DEBUGGING WORKFLOW 7423")
    print("=" * 80)
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode so we can see what's happening
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        print("⏳ Waiting for page to load...")
        await page.wait_for_timeout(5000)
        
        # Check for the YouTube video link
        print("\n🔍 SEARCHING FOR YOUTUBE VIDEO...")
        youtube_links = await page.query_selector_all('a[href*="youtu.be"]')
        print(f"Found {len(youtube_links)} YouTube links")
        
        for i, link in enumerate(youtube_links):
            href = await link.get_attribute('href')
            print(f"  {i+1}. {href}")
        
        # Check for the video thumbnail
        print("\n🔍 SEARCHING FOR YOUTUBE THUMBNAILS...")
        youtube_thumbnails = await page.query_selector_all('img[src*="img.youtube.com"]')
        print(f"Found {len(youtube_thumbnails)} YouTube thumbnails")
        
        for i, img in enumerate(youtube_thumbnails):
            src = await img.get_attribute('src')
            alt = await img.get_attribute('alt')
            print(f"  {i+1}. src: {src}")
            print(f"     alt: {alt}")
        
        # Check for the title
        print("\n🔍 SEARCHING FOR TITLE...")
        title_selectors = [
            'h1',
            '[data-test-id="workflow-title"]',
            '.workflow-title',
            'title'
        ]
        
        for selector in title_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements):
                    text = await elem.inner_text()
                    if text and text.strip():
                        print(f"  {i+1}. {text[:100]}...")
        
        # Check for author
        print("\n🔍 SEARCHING FOR AUTHOR...")
        author_selectors = [
            '[data-test-id="workflow-author"]',
            '.author',
            '.creator',
            'a[href*="/users/"]'
        ]
        
        for selector in author_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements):
                    text = await elem.inner_text()
                    if text and text.strip():
                        print(f"  {i+1}. {text}")
        
        # Check page content
        print("\n🔍 CHECKING PAGE CONTENT...")
        body_text = await page.inner_text('body')
        print(f"Body text length: {len(body_text)} characters")
        print(f"Contains 'Lead Generation Agent': {'Lead Generation Agent' in body_text}")
        print(f"Contains 'YouTube': {'YouTube' in body_text}")
        print(f"Contains 'youtu.be': {'youtu.be' in body_text}")
        
        # Take a screenshot
        print("\n📸 Taking screenshot...")
        await page.screenshot(path='/app/debug_workflow_7423.png')
        print("Screenshot saved to /app/debug_workflow_7423.png")
        
        print("\n⏳ Keeping browser open for 30 seconds to inspect manually...")
        await page.wait_for_timeout(30000)
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(debug_workflow_7423())

