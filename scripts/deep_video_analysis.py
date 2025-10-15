"""
Deep Video Analysis with Playwright

Manually analyze workflow 6270 to find how the video is embedded.

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import asyncio
import sys
import re

sys.path.append('/app')

from playwright.async_api import async_playwright


async def analyze_workflow_6270():
    """Deep analysis of workflow 6270 where we know there's a video"""
    
    print('🔍 DEEP VIDEO ANALYSIS - Workflow 6270')
    print('=' * 80)
    print('URL: https://n8n.io/workflows/6270-build-your-first-ai-agent/')
    print()
    print('We KNOW this workflow has video https://youtu.be/laHIzhsz12E')
    print('Let\'s find WHERE and HOW it\'s embedded...')
    print()
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto('https://n8n.io/workflows/6270-build-your-first-ai-agent/', timeout=30000)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)
        
        # Get full page HTML
        page_html = await page.content()
        
        # Search for the video ID in HTML
        video_id = 'laHIzhsz12E'
        
        print(f'🔍 Searching for video ID "{video_id}" in page HTML...')
        print()
        
        if video_id in page_html:
            print(f'✅ FOUND video ID in page HTML!')
            print()
            
            # Find context around the video ID
            idx = page_html.find(video_id)
            context_start = max(0, idx - 200)
            context_end = min(len(page_html), idx + 200)
            context = page_html[context_start:context_end]
            
            print('📄 HTML CONTEXT (200 chars before/after):')
            print('-' * 80)
            print(context)
            print('-' * 80)
            print()
            
            # Extract the full URL
            url_patterns = [
                r'https?://(?:www\.)?youtube\.com/watch\?v=' + video_id + r'[^"\'>\s]*',
                r'https?://youtu\.be/' + video_id + r'[^"\'>\s]*',
                r'https?://(?:www\.)?youtube\.com/embed/' + video_id + r'[^"\'>\s]*',
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, page_html)
                if match:
                    full_url = match.group(0)
                    print(f'✅ FOUND FULL URL: {full_url}')
                    print(f'   Pattern: {pattern}')
                    print()
        else:
            print(f'❌ Video ID NOT found in main page HTML')
            print('   Checking iframes...')
            print()
        
        # Check iframes
        iframes = await page.query_selector_all('iframe')
        print(f'📦 Found {len(iframes)} iframes')
        print()
        
        for i, iframe in enumerate(iframes, 1):
            src = await iframe.get_attribute('src')
            print(f'iframe {i}: {src}')
            
            try:
                frame = await iframe.content_frame()
                if frame:
                    iframe_html = await frame.content()
                    
                    if video_id in iframe_html:
                        print(f'  ✅ FOUND video ID in THIS iframe!')
                        
                        # Find context
                        idx = iframe_html.find(video_id)
                        context_start = max(0, idx - 200)
                        context_end = min(len(iframe_html), idx + 200)
                        context = iframe_html[context_start:context_end]
                        
                        print('  📄 IFRAME HTML CONTEXT:')
                        print('  ' + '-' * 76)
                        print('  ' + context[:200])
                        print('  ' + '-' * 76)
                        print()
                        
                        # Extract full URL from iframe
                        for pattern in url_patterns:
                            match = re.search(pattern, iframe_html)
                            if match:
                                full_url = match.group(0)
                                print(f'  ✅ FULL URL IN IFRAME: {full_url}')
                                print()
                    else:
                        print(f'  ❌ Video ID not in this iframe')
            except Exception as e:
                print(f'  Error: {e}')
            
            print()
        
        # Check all YouTube patterns in page
        print('🔍 ALL YOUTUBE PATTERNS IN PAGE:')
        print('-' * 80)
        
        all_patterns = {
            'youtu.be/': r'youtu\.be/([\w-]+)',
            'watch?v=': r'watch\?v=([\w-]+)',
            'embed/': r'embed/([\w-]+)',
            'channel /c/': r'youtube\.com/c/([\w-]+)',
        }
        
        for name, pattern in all_patterns.items():
            matches = re.findall(pattern, page_html)
            unique = list(set(matches))
            print(f'{name}: {len(unique)} unique')
            if unique:
                for match in unique[:3]:
                    if len(match) == 11:  # Valid video ID
                        print(f'  ✅ https://youtu.be/{match}')
                    else:
                        print(f'  ⚠️  {match} (length: {len(match)})')
        
        await page.close()
        await browser.close()
    
    print()
    print('=' * 80)
    print('Analysis complete!')


if __name__ == "__main__":
    asyncio.run(analyze_workflow_6270())



