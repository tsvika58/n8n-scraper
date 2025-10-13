#!/usr/bin/env python3
"""
Test dynamic content loading on workflow 7423
"""

import asyncio
from playwright.async_api import async_playwright


async def test_dynamic_content():
    """Test if we need to wait for dynamic content to load."""
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # Wait progressively longer
        for wait_time in [2, 5, 10, 15]:
            print(f"\n⏳ Waiting {wait_time} seconds for dynamic content...")
            await page.wait_for_timeout(wait_time * 1000)
            
            # Check for YouTube content
            youtube_links = await page.query_selector_all('a[href*="youtu.be"]')
            youtube_thumbnails = await page.query_selector_all('img[src*="img.youtube.com"]')
            
            print(f"  YouTube links: {len(youtube_links)}")
            print(f"  YouTube thumbnails: {len(youtube_thumbnails)}")
            
            if youtube_links or youtube_thumbnails:
                print("✅ Found YouTube content!")
                break
        
        # Final check with all possible selectors
        print("\n🔍 FINAL COMPREHENSIVE CHECK:")
        
        # Check for any elements containing YouTube URLs
        all_links = await page.query_selector_all('a')
        print(f"Total links on page: {len(all_links)}")
        
        youtube_found = False
        for link in all_links:
            href = await link.get_attribute('href')
            if href and 'youtu' in href:
                print(f"✅ Found YouTube link: {href}")
                youtube_found = True
        
        # Check all images
        all_images = await page.query_selector_all('img')
        print(f"Total images on page: {len(all_images)}")
        
        for img in all_images:
            src = await img.get_attribute('src')
            if src and 'youtube' in src:
                print(f"✅ Found YouTube image: {src}")
                youtube_found = True
        
        # Check page source for YouTube URLs
        page_content = await page.content()
        if 'youtu.be/3UwutV1x3mA' in page_content:
            print("✅ Found YouTube URL in page source!")
            youtube_found = True
        else:
            print("❌ YouTube URL not found in page source")
        
        if not youtube_found:
            print("\n⚠️  No YouTube content found. Possible issues:")
            print("  1. Page structure changed")
            print("  2. Content loaded via complex JavaScript")
            print("  3. Anti-bot measures blocking content")
            print("  4. Workflow is private/deleted")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(test_dynamic_content())

