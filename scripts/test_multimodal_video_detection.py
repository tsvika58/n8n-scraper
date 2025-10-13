#!/usr/bin/env python3
"""
Test the multimodal processor's video detection directly.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.multimodal_processor import MultimodalProcessor

async def test_multimodal_video_detection():
    """Test multimodal processor video detection."""
    
    workflow_id = "6270"
    workflow_url = "https://n8n.io/workflows/6270-build-your-first-ai-agent/"
    
    print("🎬 TESTING MULTIMODAL VIDEO DETECTION")
    print("="*80)
    print(f"Workflow ID: {workflow_id}")
    print(f"URL: {workflow_url}")
    print()
    
    async with MultimodalProcessor(headless=True, timeout=30000) as processor:
        try:
            # Test the video discovery method directly
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                print("📄 Loading page...")
                await page.goto(workflow_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)
                
                print("🔍 Testing main page video discovery...")
                main_page_videos = await processor.discover_videos_on_main_page(page)
                
                print(f"✅ Found {len(main_page_videos)} videos on main page:")
                for i, video_url in enumerate(main_page_videos):
                    print(f"   {i+1}. {video_url}")
                
                print()
                print("🔍 Testing iframe discovery...")
                iframes = await processor.discover_iframes(page, workflow_url)
                
                print(f"✅ Found {len(iframes)} iframes:")
                for i, iframe in enumerate(iframes):
                    print(f"   {i+1}. {iframe}")
                
                print()
                print("🔍 Testing video discovery in iframes...")
                for i, iframe in enumerate(iframes):
                    print(f"   Checking iframe {i+1}...")
                    videos_in_iframe = await processor.discover_videos_in_iframe(page, iframe)
                    print(f"      Found {len(videos_in_iframe)} videos:")
                    for j, video_url in enumerate(videos_in_iframe):
                        print(f"         {j+1}. {video_url}")
                
                await browser.close()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_multimodal_video_detection())



