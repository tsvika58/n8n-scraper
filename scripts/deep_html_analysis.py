"""
Deep HTML Analysis for Missing Videos

Analyzes the exact HTML content to understand why videos aren't being found.

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

class DeepHTMLAnalyzer:
    """Deep analysis of HTML content for missing videos"""
    
    def __init__(self):
        self.browser = None
        self.playwright = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def analyze_workflow(self, workflow_id: str, url: str, expected_videos: List[str]):
        """Deep analysis of a workflow for missing videos"""
        print(f'\n🔍 DEEP ANALYSIS: WORKFLOW {workflow_id}')
        print(f'URL: {url}')
        print(f'Expected videos: {expected_videos}')
        print('=' * 80)
        
        page = await self.browser.new_page()
        
        try:
            # Navigate and wait for full load
            await page.goto(url, timeout=60000, wait_until='networkidle')
            await page.wait_for_timeout(5000)  # Extra wait for dynamic content
            
            # Get all HTML content
            main_html = await page.content()
            
            # Save HTML to file for inspection
            html_file = f'/app/debug_{workflow_id}_full.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(main_html)
            print(f'📄 Full HTML saved to: {html_file}')
            
            # Search for each expected video ID in the HTML
            print(f'\n🎯 SEARCHING FOR EXPECTED VIDEO IDs:')
            for video_id in expected_videos:
                print(f'\n   Looking for: {video_id}')
                
                # Count occurrences
                count = main_html.count(video_id)
                print(f'   Found {count} occurrences in HTML')
                
                if count > 0:
                    # Find context around each occurrence
                    lines = main_html.split('\n')
                    for i, line in enumerate(lines):
                        if video_id in line:
                            print(f'   Line {i+1}: {line.strip()[:200]}...')
                            
                            # Look for surrounding context
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            print(f'   Context:')
                            for j in range(start, end):
                                marker = '>>> ' if j == i else '    '
                                print(f'   {marker}{j+1}: {lines[j].strip()[:150]}...')
                            print()
                
                # Try different patterns
                patterns = [
                    f'"{video_id}"',
                    f"'{video_id}'",
                    f'={video_id}',
                    f'/{video_id}',
                    f'videoId.*{video_id}',
                    f'video_id.*{video_id}',
                    f'data.*{video_id}',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, main_html, re.IGNORECASE)
                    if matches:
                        print(f'   Pattern "{pattern}": {len(matches)} matches')
                        for match in matches[:3]:  # Show first 3 matches
                            print(f'     - {match}')
            
            # Check iframes specifically
            print(f'\n🖼️  IFRAME ANALYSIS:')
            iframes = await page.query_selector_all('iframe')
            print(f'Found {len(iframes)} iframes')
            
            for idx, iframe in enumerate(iframes):
                try:
                    src = await iframe.get_attribute('src')
                    print(f'\n   Iframe {idx+1}: {src}')
                    
                    # Try to access iframe content
                    frame_content = await iframe.content_frame()
                    
                    if frame_content:
                        iframe_html = await frame_content.content()
                        print(f'   ✅ Can access iframe content ({len(iframe_html)} chars)')
                        
                        # Save iframe HTML
                        iframe_file = f'/app/debug_{workflow_id}_iframe_{idx+1}.html'
                        with open(iframe_file, 'w', encoding='utf-8') as f:
                            f.write(iframe_html)
                        print(f'   📄 Iframe HTML saved to: {iframe_file}')
                        
                        # Search for videos in iframe
                        for video_id in expected_videos:
                            iframe_count = iframe_html.count(video_id)
                            if iframe_count > 0:
                                print(f'   🎥 Found {video_id} {iframe_count} times in iframe!')
                    else:
                        print(f'   ❌ Cannot access iframe content (cross-origin)')
                        
                        # Try cross-origin fetch
                        if src:
                            try:
                                context = await self.browser.new_context()
                                response = await context.request.get(src, timeout=30000)
                                if response.ok:
                                    cross_html = await response.text()
                                    print(f'   🔄 Cross-origin fetch successful ({len(cross_html)} chars)')
                                    
                                    # Save cross-origin HTML
                                    cross_file = f'/app/debug_{workflow_id}_cross_{idx+1}.html'
                                    with open(cross_file, 'w', encoding='utf-8') as f:
                                        f.write(cross_html)
                                    print(f'   📄 Cross-origin HTML saved to: {cross_file}')
                                    
                                    # Search for videos in cross-origin content
                                    for video_id in expected_videos:
                                        cross_count = cross_html.count(video_id)
                                        if cross_count > 0:
                                            print(f'   🎥 Found {video_id} {cross_count} times in cross-origin content!')
                                else:
                                    print(f'   ❌ Cross-origin fetch failed: {response.status}')
                                await context.close()
                            except Exception as e:
                                print(f'   ❌ Cross-origin fetch error: {e}')
                
                except Exception as e:
                    print(f'   ❌ Error processing iframe {idx+1}: {e}')
            
        finally:
            await page.close()

async def main():
    """Deep analysis of missing videos"""
    print('🔍 DEEP HTML ANALYSIS FOR MISSING VIDEOS')
    print('=' * 80)
    
    async with DeepHTMLAnalyzer() as analyzer:
        for workflow_id, expected_videos in MISSING_VIDEOS.items():
            url = TEST_URLS[workflow_id]
            await analyzer.analyze_workflow(workflow_id, url, expected_videos)
    
    print('\n🎉 DEEP ANALYSIS COMPLETE!')
    print('Check the saved HTML files for detailed inspection.')

if __name__ == "__main__":
    asyncio.run(main())

