"""
Debug Missing Videos Script

Investigates why specific videos are not being discovered by the L3 extractor.

Author: AI Assistant
Date: October 15, 2025
"""

import asyncio
import sys
import re
from typing import List, Dict

sys.path.append('/app')

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from loguru import logger

# Missing videos to investigate
MISSING_VIDEOS = {
    '7639': ['qsrVPdo6svc'],
    '8527': ['dKTcAfBfFLU', '5CBUXMO_L2Y', 'LdE0KnhRtsY']
}

TEST_URLS = {
    '7639': 'https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/',
    '8527': 'https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/'
}

class VideoDebugger:
    """Debug missing video discovery"""
    
    def __init__(self):
        self.browser = None
        self.playwright = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)  # Headless for Docker
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def debug_workflow(self, workflow_id: str, url: str, expected_videos: List[str]):
        """Debug a specific workflow for missing videos"""
        print(f'\n🔍 DEBUGGING WORKFLOW {workflow_id}')
        print(f'URL: {url}')
        print(f'Expected videos: {expected_videos}')
        print('=' * 80)
        
        page = await self.browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, timeout=60000, wait_until='networkidle')
            await page.wait_for_timeout(3000)  # Let content load
            
            # Get main page HTML
            main_html = await page.content()
            print(f'📄 Main page HTML length: {len(main_html)} chars')
            
            # Check for videos in main page HTML
            main_videos = self._scan_html_for_videos(main_html, 'main_page')
            print(f'🎥 Videos in main page HTML: {len(main_videos)}')
            for video in main_videos:
                print(f'   - {video}')
            
            # Check iframes
            iframes = await page.query_selector_all('iframe')
            print(f'🖼️  Found {len(iframes)} iframes')
            
            for idx, iframe in enumerate(iframes):
                try:
                    src = await iframe.get_attribute('src')
                    title = await iframe.get_attribute('title') or ''
                    print(f'\n   Iframe {idx+1}: {src}')
                    print(f'   Title: {title}')
                    
                    # Try to access iframe content
                    frame_content = await iframe.content_frame()
                    
                    if frame_content:
                        print(f'   ✅ Can access iframe content')
                        iframe_html = await frame_content.content()
                        iframe_videos = self._scan_html_for_videos(iframe_html, f'iframe_{idx}')
                        print(f'   🎥 Videos in iframe: {len(iframe_videos)}')
                        for video in iframe_videos:
                            print(f'      - {video}')
                    else:
                        print(f'   ❌ Cannot access iframe content (cross-origin)')
                        
                        # Try to fetch cross-origin content
                        if src:
                            print(f'   🔄 Attempting cross-origin fetch...')
                            try:
                                context = await self.browser.new_context()
                                response = await context.request.get(src, timeout=30000)
                                if response.ok:
                                    cross_origin_html = await response.text()
                                    cross_videos = self._scan_html_for_videos(cross_origin_html, f'cross_origin_{idx}')
                                    print(f'   🎥 Videos in cross-origin content: {len(cross_videos)}')
                                    for video in cross_videos:
                                        print(f'      - {video}')
                                else:
                                    print(f'   ❌ Cross-origin fetch failed: {response.status}')
                                await context.close()
                            except Exception as e:
                                print(f'   ❌ Cross-origin fetch error: {e}')
                
                except Exception as e:
                    print(f'   ❌ Error processing iframe {idx+1}: {e}')
            
            # Check for expected videos specifically
            print(f'\n🎯 CHECKING FOR EXPECTED VIDEOS:')
            all_html = main_html
            for video_id in expected_videos:
                found = False
                
                # Check main page
                if video_id in main_html:
                    print(f'   ✅ {video_id} found in main page HTML')
                    found = True
                
                # Check iframes
                for idx, iframe in enumerate(iframes):
                    try:
                        frame_content = await iframe.content_frame()
                        if frame_content:
                            iframe_html = await frame_content.content()
                            if video_id in iframe_html:
                                print(f'   ✅ {video_id} found in iframe {idx+1}')
                                found = True
                    except:
                        pass
                
                if not found:
                    print(f'   ❌ {video_id} NOT FOUND anywhere')
            
            # Take screenshot for visual inspection
            screenshot_path = f'/app/debug_{workflow_id}.png'
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f'📸 Screenshot saved: {screenshot_path}')
            
        finally:
            await page.close()
    
    def _scan_html_for_videos(self, html: str, context: str) -> List[str]:
        """Scan HTML for YouTube video IDs"""
        videos = []
        
        # YouTube video ID patterns
        patterns = [
            r'youtube\.com/watch\?v=([\w-]{11})',
            r'youtu\.be/([\w-]{11})',
            r'youtube\.com/embed/([\w-]{11})',
            r'"videoId":"([\w-]{11})"',
            r'videoId=([\w-]{11})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for video_id in matches:
                if self._is_valid_video_id(video_id):
                    videos.append(f'https://youtu.be/{video_id}')
        
        return list(set(videos))  # Remove duplicates
    
    def _is_valid_video_id(self, video_id: str) -> bool:
        """Validate YouTube video ID"""
        if not video_id or len(video_id) != 11:
            return False
        return bool(re.match(r'^[\w-]{11}$', video_id))

async def main():
    """Debug missing videos"""
    print('🔍 MISSING VIDEO DEBUGGER')
    print('=' * 80)
    
    async with VideoDebugger() as debugger:
        for workflow_id, expected_videos in MISSING_VIDEOS.items():
            url = TEST_URLS[workflow_id]
            await debugger.debug_workflow(workflow_id, url, expected_videos)
    
    print('\n🎉 DEBUG COMPLETE!')

if __name__ == "__main__":
    asyncio.run(main())
