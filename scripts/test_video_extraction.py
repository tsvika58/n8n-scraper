#!/usr/bin/env python3
"""
Test the Layer 3 video extraction logic on the actual page content.
"""

import asyncio
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_video_extraction():
    """Test the actual Layer 3 video extraction logic."""
    
    url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
    
    print("🧪 TESTING LAYER 3 VIDEO EXTRACTION")
    print("="*80)
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # Get page HTML
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            print("🔍 TESTING LAYER 3 EXTRACTION LOGIC...")
            print()
            
            # Test the exact logic from Layer 3
            video_urls = []
            
            # YouTube patterns (from layer3_explainer.py)
            youtube_patterns = [
                r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
                r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
                r'https?://youtu\.be/[\w-]+',
            ]
            
            print("📺 CHECKING IFRAMES:")
            iframes = soup.find_all('iframe')
            for i, iframe in enumerate(iframes):
                src = iframe.get('src', '')
                print(f"   {i+1}. src='{src}'")
                for pattern in youtube_patterns:
                    matches = re.findall(pattern, src)
                    if matches:
                        video_urls.extend(matches)
                        print(f"      ✅ Found: {matches}")
            
            print()
            print("🔗 CHECKING LINKS:")
            links = soup.find_all('a')
            youtube_links = []
            for link in links:
                href = link.get('href', '')
                for pattern in youtube_patterns:
                    matches = re.findall(pattern, href)
                    if matches:
                        youtube_links.extend(matches)
                        print(f"   Found in link: {matches}")
            
            video_urls.extend(youtube_links)
            
            print()
            print("📄 CHECKING ALL TEXT CONTENT:")
            # Also check the full page text for YouTube URLs
            page_text = soup.get_text()
            for pattern in youtube_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    print(f"   Pattern '{pattern}': {matches}")
                    video_urls.extend(matches)
            
            # Remove duplicates
            video_urls = list(set(video_urls))
            
            print()
            print("🎯 FINAL RESULTS:")
            print(f"   Total video URLs found: {len(video_urls)}")
            for i, url in enumerate(video_urls):
                print(f"   {i+1}. {url}")
            
            print()
            print("="*80)
            if video_urls:
                print("✅ VIDEO DETECTION WORKING!")
                print("❓ Why didn't Layer 3 catch this?")
            else:
                print("❌ NO VIDEOS FOUND - Layer 3 logic is correct")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_video_extraction())






