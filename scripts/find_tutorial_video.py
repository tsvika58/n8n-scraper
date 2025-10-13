#!/usr/bin/env python3
"""
Find the specific "AI Agent Tutorial for Beginners!" video.
"""

import asyncio
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def find_tutorial_video():
    """Find the tutorial video on the workflow page."""
    
    url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
    
    print("🎬 FINDING TUTORIAL VIDEO")
    print("="*80)
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate and wait
            print("📄 Loading page...")
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(5000)
            
            print("🔍 Looking for tutorial video elements...")
            
            # Look for elements containing "tutorial" text
            tutorial_elements = await page.query_selector_all('text=*tutorial*')
            print(f"Found {len(tutorial_elements)} elements containing 'tutorial'")
            
            for i, element in enumerate(tutorial_elements):
                text = await element.inner_text()
                print(f"   {i+1}. Text: '{text}'")
            
            print()
            print("🔍 Looking for 'AI Agent Tutorial for Beginners!'...")
            
            # Look for the specific tutorial title
            tutorial_title = await page.query_selector('text=AI Agent Tutorial for Beginners!')
            if tutorial_title:
                print("   ✅ Found tutorial title element!")
                
                # Find the parent container
                parent = await tutorial_title.query_selector('xpath=..')
                if parent:
                    parent_html = await parent.inner_html()
                    print(f"   Parent HTML: {parent_html[:200]}...")
                    
                    # Look for video-related elements in parent
                    video_in_parent = await parent.query_selector('video, iframe, [data-video], [data-youtube]')
                    if video_in_parent:
                        print("   ✅ Found video element in parent!")
                    else:
                        print("   ❌ No video element found in parent")
            else:
                print("   ❌ Tutorial title not found")
            
            print()
            print("🔍 Looking for play buttons...")
            
            # Look for play button elements
            play_buttons = await page.query_selector_all('[class*="play"], [data-play], button[aria-label*="play"], button[title*="play"]')
            print(f"Found {len(play_buttons)} play button elements")
            
            for i, button in enumerate(play_buttons):
                text = await button.inner_text()
                aria_label = await button.get_attribute('aria-label')
                title = await button.get_attribute('title')
                print(f"   {i+1}. Text: '{text}', Aria: '{aria_label}', Title: '{title}'")
            
            print()
            print("🔍 Looking for video thumbnails...")
            
            # Look for images that might be video thumbnails
            images = await page.query_selector_all('img')
            video_thumbnails = []
            
            for img in images:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                title = await img.get_attribute('title')
                
                # Check if it looks like a video thumbnail
                if any(word in (alt or '').lower() for word in ['video', 'tutorial', 'play', 'youtube']):
                    video_thumbnails.append((src, alt, title))
            
            print(f"Found {len(video_thumbnails)} potential video thumbnails")
            for i, (src, alt, title) in enumerate(video_thumbnails):
                print(f"   {i+1}. src='{src}', alt='{alt}', title='{title}'")
            
            print()
            print("🔍 Checking workflow diagram area...")
            
            # Look for the workflow diagram container
            diagram_containers = await page.query_selector_all('[class*="workflow"], [class*="diagram"], [class*="canvas"]')
            print(f"Found {len(diagram_containers)} diagram containers")
            
            for i, container in enumerate(diagram_containers):
                # Look for video elements inside each container
                videos_in_container = await container.query_selector_all('video, iframe, [data-video]')
                if videos_in_container:
                    print(f"   Container {i+1}: Found {len(videos_in_container)} video elements")
                    
                    for j, video in enumerate(videos_in_container):
                        tag_name = await video.evaluate('el => el.tagName')
                        src = await video.get_attribute('src')
                        print(f"      {j+1}. {tag_name} src='{src}'")
            
            print()
            print("="*80)
            print("✅ VIDEO SEARCH COMPLETE")
            
            # Wait for user to see the page
            print("\n👀 Check the browser window for the video...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(find_tutorial_video())



