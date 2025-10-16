"""
Debug Video Discovery with Playwright

Investigate what videos are actually on the page and in iframes.

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import asyncio
import sys
import re

sys.path.append('/app')

from playwright.async_api import async_playwright


async def debug_video_discovery():
    """Debug video discovery on known video workflows"""
    
    test_workflows = [
        ('6270', 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'),
        ('8527', 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'),
    ]
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        
        for wf_id, url in test_workflows:
            print(f'\n🔍 DEBUGGING WORKFLOW {wf_id}')
            print(f'URL: {url}')
            print('=' * 80)
            
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            
            # 1. Check main page for video links
            print('\n📄 MAIN PAGE VIDEO LINKS:')
            print('-' * 80)
            
            # All links with youtube/youtu.be
            links = await page.query_selector_all('a[href*="youtube"], a[href*="youtu.be"]')
            for i, link in enumerate(links[:5], 1):
                href = await link.get_attribute('href')
                text = await link.inner_text()
                print(f'{i}. {href}')
                print(f'   Text: {text[:50]}...')
                
                # Check if it's a video URL
                if re.search(r'watch\?v=|youtu\.be/[\w-]+', href):
                    print(f'   ✅ ACTUAL VIDEO URL')
                elif 'youtube.com/c/' in href or 'youtube.com/@' in href:
                    print(f'   ❌ CHANNEL URL (not a video)')
                else:
                    print(f'   ⚠️  OTHER YOUTUBE URL')
            
            # 2. Check iframes
            print('\n🖼️  IFRAME CONTENT:')
            print('-' * 80)
            
            iframes = await page.query_selector_all('iframe')
            print(f'Found {len(iframes)} iframes')
            
            for i, iframe in enumerate(iframes, 1):
                src = await iframe.get_attribute('src')
                print(f'\niframe {i}: {src}')
                
                try:
                    frame = await iframe.content_frame()
                    if frame:
                        # Check for YouTube links in iframe
                        iframe_links = await frame.query_selector_all('a[href*="youtube"], a[href*="youtu.be"]')
                        print(f'  YouTube links in iframe: {len(iframe_links)}')
                        
                        for j, link in enumerate(iframe_links[:3], 1):
                            href = await link.get_attribute('href')
                            print(f'    {j}. {href}')
                            
                            if re.search(r'watch\?v=|youtu\.be/[\w-]+', href):
                                print(f'       ✅ ACTUAL VIDEO URL')
                            elif 'youtube.com/c/' in href or 'youtube.com/@' in href:
                                print(f'       ❌ CHANNEL URL')
                        
                        # Check for video elements
                        video_elements = await frame.query_selector_all('video')
                        print(f'  <video> elements: {len(video_elements)}')
                        
                        # Check page content for embedded YouTube
                        iframe_html = await frame.content()
                        youtube_matches = re.findall(r'https?://(?:www\.)?youtu(?:\.be|be\.com)/(?:watch\?v=|embed/)?([\w-]+)', iframe_html)
                        print(f'  YouTube IDs in HTML: {len(set(youtube_matches))}')
                        if youtube_matches:
                            unique_ids = list(set(youtube_matches))[:3]
                            for video_id in unique_ids:
                                print(f'    https://youtu.be/{video_id}')
                        
                except Exception as e:
                    print(f'  Error accessing iframe: {e}')
            
            # 3. Check page HTML for all YouTube patterns
            print('\n🔍 REGEX SCAN OF FULL PAGE HTML:')
            print('-' * 80)
            
            page_html = await page.content()
            
            # All YouTube patterns
            patterns = {
                'watch?v=': r'youtube\.com/watch\?v=([\w-]+)',
                'youtu.be/': r'youtu\.be/([\w-]+)',
                'embed/': r'youtube\.com/embed/([\w-]+)',
                'channel': r'youtube\.com/c/([\w-]+)',
            }
            
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, page_html)
                unique = list(set(matches))
                print(f'{pattern_name}: {len(unique)} unique matches')
                if unique and pattern_name != 'channel':
                    for match in unique[:3]:
                        if pattern_name in ['watch?v=', 'youtu.be/', 'embed/']:
                            print(f'  ✅ https://youtu.be/{match}')
            
            await page.close()
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_video_discovery())




