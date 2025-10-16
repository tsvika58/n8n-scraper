"""
Comprehensive Video Search

Searches EVERYWHERE for video ID: laHIzhsz12E

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import asyncio
import sys

sys.path.append('/app')

from playwright.async_api import async_playwright


async def comprehensive_search():
    """Search everywhere for the video"""
    
    url = 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'
    video_id = 'laHIzhsz12E'
    
    print(f'🔍 COMPREHENSIVE VIDEO SEARCH')
    print('=' * 80)
    print(f'URL: {url}')
    print(f'Looking for video ID: {video_id}')
    print()
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(5000)  # Wait longer
        
        # Scroll through entire page
        print('Scrolling through page...')
        for i in range(5):
            await page.evaluate(f'window.scrollTo(0, {i * 1000})')
            await page.wait_for_timeout(1000)
        
        # Get final HTML
        page_html = await page.content()
        
        print(f'Total page HTML length: {len(page_html):,} characters')
        print()
        
        # Search for video ID
        if video_id in page_html:
            print(f'✅ FOUND "{video_id}" in page HTML!')
            
            # Find all occurrences
            count = page_html.count(video_id)
            print(f'   Appears {count} times in HTML')
            
            # Get context
            idx = page_html.find(video_id)
            context = page_html[max(0, idx-300):min(len(page_html), idx+300)]
            
            print()
            print('Context around first occurrence:')
            print('-' * 80)
            print(context)
            print('-' * 80)
        else:
            print(f'❌ "{video_id}" NOT FOUND in page HTML')
        
        print()
        
        # Search for ANY 11-character YouTube IDs
        import re
        youtube_patterns = [
            r'youtu\.be/([\w-]{11})',
            r'youtube\.com/watch\?v=([\w-]{11})',
            r'youtube\.com/embed/([\w-]{11})',
        ]
        
        all_video_ids = []
        for pattern in youtube_patterns:
            matches = re.findall(pattern, page_html)
            all_video_ids.extend(matches)
        
        unique_ids = list(set(all_video_ids))
        
        print(f'Found {len(unique_ids)} unique 11-char video IDs:')
        for vid_id in unique_ids:
            print(f'  - https://youtu.be/{vid_id}')
            if vid_id == video_id:
                print(f'    ✅ THIS IS THE ONE WE\'RE LOOKING FOR!')
        
        print()
        
        # Check if video is in an iframe with different source
        print('Checking all iframes...')
        iframes = await page.query_selector_all('iframe')
        print(f'Found {len(iframes)} iframes')
        
        for i, iframe in enumerate(iframes, 1):
            src = await iframe.get_attribute('src')
            print(f'  iframe {i}: {src or "no src"}')
        
        await page.close()
        await browser.close()
    
    print()
    print('🎯 URLS TO CHECK MANUALLY:')
    print(f'1. {url}')
    print(f'2. Expected video: https://youtu.be/{video_id}')


if __name__ == "__main__":
    asyncio.run(comprehensive_search())




