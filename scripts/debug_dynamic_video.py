#!/usr/bin/env python3
"""
Debug dynamic video content that might be loaded by JavaScript.
"""

import asyncio
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def debug_dynamic_video():
    """Debug video content after JavaScript execution."""
    
    url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
    
    print("🔄 DEBUGGING DYNAMIC VIDEO CONTENT")
    print("="*80)
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser
        page = await browser.new_page()
        
        try:
            # Navigate and wait for full load
            print("📄 Loading page and waiting for JavaScript...")
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(5000)  # Extra wait for dynamic content
            
            print("🔍 Searching for video elements in DOM...")
            
            # Look for video elements in the DOM
            video_elements = await page.query_selector_all('video, iframe[src*="youtube"], iframe[src*="youtu.be"], a[href*="youtube"], a[href*="youtu.be"]')
            
            print(f"Found {len(video_elements)} potential video elements")
            
            for i, element in enumerate(video_elements):
                tag_name = await element.evaluate('el => el.tagName')
                
                if tag_name == 'IFRAME':
                    src = await element.get_attribute('src')
                    print(f"   {i+1}. IFRAME src='{src}'")
                    
                elif tag_name == 'VIDEO':
                    src = await element.get_attribute('src')
                    poster = await element.get_attribute('poster')
                    print(f"   {i+1}. VIDEO src='{src}', poster='{poster}'")
                    
                elif tag_name == 'A':
                    href = await element.get_attribute('href')
                    text = await element.inner_text()
                    print(f"   {i+1}. LINK href='{href}', text='{text[:50]}...'")
            
            print()
            print("🔍 Searching for video-related text content...")
            
            # Get all text content and search for video URLs
            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Search for YouTube URLs in all text
            youtube_patterns = [
                r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
                r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
                r'https?://youtu\.be/[\w-]+',
            ]
            
            all_text = soup.get_text()
            for pattern in youtube_patterns:
                matches = re.findall(pattern, all_text)
                if matches:
                    print(f"   Pattern '{pattern}': {matches}")
            
            print()
            print("🔍 Checking for data attributes and JSON...")
            
            # Look for data attributes that might contain video URLs
            elements_with_data = await page.query_selector_all('[data-*]')
            for element in elements_with_data[:20]:  # Check first 20 elements
                attributes = await element.evaluate('el => Array.from(el.attributes).map(attr => `${attr.name}="${attr.value}"`)')
                for attr in attributes:
                    if any(word in attr.lower() for word in ['video', 'youtube', 'embed', 'tutorial']):
                        print(f"   Data attribute: {attr}")
            
            print()
            print("🔍 Looking for the specific video we saw...")
            
            # Search for the specific video ID we found earlier
            if 'lahizhsz12e' in page_content:
                print("   ✅ Found 'lahizhsz12e' in page content!")
                
                # Find the context around it
                lines = page_content.split('\n')
                for i, line in enumerate(lines):
                    if 'lahizhsz12e' in line:
                        print(f"   Line {i}: {line.strip()}")
            else:
                print("   ❌ 'lahizhsz12e' not found in current page content")
            
            print()
            print("="*80)
            print("✅ DYNAMIC DEBUG COMPLETE")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_dynamic_video())





