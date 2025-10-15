"""
Find Dynamically Loaded Videos

Scrolls through page, waits for dynamic content, and searches for videos.

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import asyncio
import sys
import re

sys.path.append('/app')

from playwright.async_api import async_playwright


async def find_dynamic_videos():
    """Find videos after scrolling and dynamic content loading"""
    
    url = 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'
    
    print('🎥 FINDING DYNAMICALLY LOADED VIDEOS')
    print('=' * 80)
    print(f'URL: {url}')
    print()
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print('Step 1: Loading page...')
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state('networkidle')
        
        print('Step 2: Scrolling through page...')
        # Scroll to bottom
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(2000)
        
        # Scroll back to top
        await page.evaluate('window.scrollTo(0, 0)')
        await page.wait_for_timeout(2000)
        
        print('Step 3: Checking for videos...')
        
        # Get HTML after scrolling
        page_html = await page.content()
        
        # Search for video ID
        video_id = 'laHIzhsz12E'
        
        if video_id in page_html:
            print(f'✅ Found video ID after scrolling!')
        else:
            print(f'❌ Still no video ID in HTML')
        
        print()
        print('Step 4: Checking all iframes...')
        
        iframes = await page.query_selector_all('iframe')
        print(f'Found {len(iframes)} iframes')
        print()
        
        for i, iframe in enumerate(iframes, 1):
            src = await iframe.get_attribute('src')
            title = await iframe.get_attribute('title')
            
            print(f'iframe {i}:')
            print(f'  src: {src}')
            print(f'  title: {title}')
            
            try:
                frame = await iframe.content_frame()
                if frame:
                    # Scroll in iframe
                    try:
                        await frame.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        await frame.wait_for_timeout(1000)
                    except:
                        pass
                    
                    iframe_html = await frame.content()
                    
                    if video_id in iframe_html:
                        print(f'  ✅ FOUND VIDEO ID IN THIS IFRAME!')
                        
                        # Search for actual video URL
                        patterns = [
                            r'https?://youtu\.be/laHIzhsz12E[^"\'\s]*',
                            r'https?://(?:www\.)?youtube\.com/watch\?v=laHIzhsz12E[^"\'\s]*',
                            r'https?://(?:www\.)?youtube\.com/embed/laHIzhsz12E[^"\'\s]*',
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, iframe_html)
                            if matches:
                                print(f'  Found URLs:')
                                for url in set(matches):
                                    print(f'    - {url}')
                    else:
                        # Check for any YouTube video IDs (11 char alphanumeric)
                        all_youtube_ids = re.findall(r'youtu(?:\.be/|be\.com/(?:watch\?v=|embed/))([\w-]{11})', iframe_html)
                        if all_youtube_ids:
                            unique_ids = list(set(all_youtube_ids))
                            print(f'  Found {len(unique_ids)} other YouTube video IDs:')
                            for vid_id in unique_ids[:3]:
                                print(f'    - https://youtu.be/{vid_id}')
                        else:
                            print(f'  ❌ No video ID in iframe')
            except Exception as e:
                print(f'  Error: {e}')
            
            print()
        
        await page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(find_dynamic_videos())

