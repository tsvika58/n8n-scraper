#!/usr/bin/env python3
"""
Debug script to see what video content is actually on the workflow page.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def debug_video_detection():
    """Debug what video content exists on the page."""
    
    url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
    
    print("🔍 DEBUGGING VIDEO DETECTION")
    print("="*80)
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        page = await browser.new_page()
        
        try:
            # Navigate to page
            print("📄 Loading page...")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Get page HTML
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            print("🎥 SEARCHING FOR VIDEO CONTENT...")
            print()
            
            # 1. Check for iframes
            print("📺 IFRAMES:")
            iframes = soup.find_all('iframe')
            for i, iframe in enumerate(iframes):
                src = iframe.get('src', '')
                print(f"   {i+1}. src='{src}'")
            
            print()
            
            # 2. Check for video tags
            print("🎬 VIDEO TAGS:")
            videos = soup.find_all('video')
            for i, video in enumerate(videos):
                src = video.get('src', '')
                poster = video.get('poster', '')
                print(f"   {i+1}. src='{src}', poster='{poster}'")
            
            print()
            
            # 3. Check for YouTube patterns in all text
            print("🔗 YOUTUBE PATTERNS IN HTML:")
            youtube_patterns = [
                r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
                r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
                r'https?://youtu\.be/[\w-]+',
                r'youtube\.com',
                r'youtu\.be'
            ]
            
            text_content = html.lower()
            for pattern in youtube_patterns:
                matches = re.findall(pattern, text_content)
                if matches:
                    print(f"   Pattern '{pattern}': {matches}")
            
            print()
            
            # 4. Check for any video-related elements
            print("🎯 VIDEO-RELATED ELEMENTS:")
            
            # Look for elements with video-related classes/attributes
            video_elements = soup.find_all(attrs={"class": re.compile(r"video|tutorial|embed", re.I)})
            for elem in video_elements:
                print(f"   {elem.name}: {elem.get('class')}")
            
            # Look for elements with video-related text
            elements_with_video_text = soup.find_all(string=re.compile(r"video|tutorial|play|watch", re.I))
            for text in elements_with_video_text[:10]:  # Limit to first 10
                if len(text.strip()) > 0:
                    print(f"   Text: '{text.strip()[:100]}...'")
            
            print()
            
            # 5. Check JavaScript variables (might contain video URLs)
            print("📜 JAVASCRIPT CONTENT:")
            scripts = soup.find_all('script')
            for i, script in enumerate(scripts[:5]):  # Check first 5 scripts
                if script.string:
                    content = script.string.lower()
                    if any(word in content for word in ['video', 'youtube', 'embed', 'tutorial']):
                        print(f"   Script {i+1}: Contains video-related content")
                        # Look for URLs in script
                        urls = re.findall(r'https?://[^\s\'"]+', script.string)
                        for url in urls:
                            if any(word in url.lower() for word in ['video', 'youtube', 'embed']):
                                print(f"      URL: {url}")
            
            print()
            print("="*80)
            print("✅ DEBUG COMPLETE")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_video_detection())



