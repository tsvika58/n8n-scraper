#!/usr/bin/env python3
"""
Direct search for the YouTube video URL we know exists.
"""

import asyncio
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def direct_video_search():
    """Directly search for the YouTube video URL."""
    
    url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
    
    print("🎯 DIRECT VIDEO URL SEARCH")
    print("="*80)
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate and wait
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(5000)
            
            # Get full page HTML
            html = await page.content()
            
            print("🔍 Searching for known YouTube video ID: 'lahizhsz12e'")
            
            # Search for the specific video ID we found earlier
            if 'lahizhsz12e' in html:
                print("✅ Found 'lahizhsz12e' in page HTML!")
                
                # Find the context around it
                lines = html.split('\n')
                for i, line in enumerate(lines):
                    if 'lahizhsz12e' in line:
                        print(f"   Line {i}: {line.strip()[:200]}...")
                        
                        # Extract the full YouTube URL
                        youtube_patterns = [
                            r'https?://(?:www\.)?youtube\.com/watch\?v=lahizhsz12e',
                            r'https?://(?:www\.)?youtube\.com/embed/lahizhsz12e',
                            r'https://youtu\.be/lahizhsz12e',
                        ]
                        
                        for pattern in youtube_patterns:
                            matches = re.findall(pattern, line)
                            if matches:
                                print(f"   ✅ Found YouTube URL: {matches[0]}")
                                return matches[0]
            else:
                print("❌ 'lahizhsz12e' not found in page HTML")
            
            print()
            print("🔍 Searching for any YouTube URLs...")
            
            # Search for any YouTube URLs
            youtube_patterns = [
                r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
                r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
                r'https://youtu\.be/[\w-]+',
            ]
            
            all_urls = []
            for pattern in youtube_patterns:
                matches = re.findall(pattern, html)
                all_urls.extend(matches)
            
            if all_urls:
                print(f"✅ Found {len(all_urls)} YouTube URLs:")
                for i, url in enumerate(all_urls):
                    print(f"   {i+1}. {url}")
                return all_urls[0]
            else:
                print("❌ No YouTube URLs found")
            
            print()
            print("🔍 Searching for video-related content...")
            
            # Look for video-related text
            soup = BeautifulSoup(html, 'html.parser')
            video_elements = soup.find_all(string=re.compile(r'AI Agent Tutorial|tutorial|video', re.I))
            
            if video_elements:
                print(f"Found {len(video_elements)} video-related text elements:")
                for i, text in enumerate(video_elements[:5]):
                    print(f"   {i+1}. {text.strip()[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()
        
        return None

if __name__ == "__main__":
    video_url = asyncio.run(direct_video_search())
    if video_url:
        print(f"\n🎯 FOUND VIDEO URL: {video_url}")
    else:
        print(f"\n❌ NO VIDEO URL FOUND")



