#!/usr/bin/env python3
"""
Test n8n iframe detection and YouTube video extraction
"""

import asyncio
from playwright.async_api import async_playwright


async def test_n8n_iframe():
    """Test if we can find the n8n workflow iframe and YouTube content."""
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Look for ALL iframes
        print("\n🔍 SEARCHING FOR ALL IFRAMES...")
        all_iframes = await page.query_selector_all('iframe')
        print(f"Found {len(all_iframes)} total iframes")
        
        for i, iframe in enumerate(all_iframes):
            src = await iframe.get_attribute('src')
            title = await iframe.get_attribute('title')
            name = await iframe.get_attribute('name')
            class_name = await iframe.get_attribute('class')
            
            print(f"\n  Iframe {i+1}:")
            print(f"    src: {src}")
            print(f"    title: {title}")
            print(f"    name: {name}")
            print(f"    class: {class_name}")
            
            # Try to access iframe content
            try:
                frame = await iframe.content_frame()
                if frame:
                    print(f"    ✅ Can access iframe content")
                    
                    # Look for YouTube content in this iframe
                    youtube_links = await frame.query_selector_all('a[href*="youtu.be"]')
                    youtube_images = await frame.query_selector_all('img[src*="youtube"]')
                    
                    if youtube_links or youtube_images:
                        print(f"    🎬 FOUND YOUTUBE CONTENT!")
                        for link in youtube_links:
                            href = await link.get_attribute('href')
                            print(f"      Link: {href}")
                        for img in youtube_images:
                            src_img = await img.get_attribute('src')
                            alt = await img.get_attribute('alt')
                            print(f"      Image: {src_img}")
                            print(f"      Alt: {alt}")
                    else:
                        print(f"    ❌ No YouTube content in this iframe")
                        
                    # Check iframe content for text
                    body_text = await frame.inner_text('body')
                    if 'Lead Generation' in body_text or 'YouTube' in body_text:
                        print(f"    📝 Contains relevant text (length: {len(body_text)})")
                        
                else:
                    print(f"    ❌ Cannot access iframe content")
                    
            except Exception as e:
                print(f"    ❌ Error accessing iframe: {e}")
        
        # Also check for n8n-specific elements
        print("\n🔍 SEARCHING FOR N8N-SPECIFIC ELEMENTS...")
        
        # Look for vue-flow elements (n8n workflow editor)
        vue_flow_elements = await page.query_selector_all('[class*="vue-flow"]')
        print(f"Found {len(vue_flow_elements)} vue-flow elements")
        
        # Look for n8n sticky notes
        sticky_elements = await page.query_selector_all('[class*="n8n-sticky"]')
        print(f"Found {len(sticky_elements)} n8n-sticky elements")
        
        for i, sticky in enumerate(sticky_elements):
            text = await sticky.inner_text()
            if 'YouTube' in text or 'youtu.be' in text:
                print(f"  Sticky {i+1} contains YouTube content:")
                print(f"    Text: {text[:200]}...")
        
        # Look for canvas elements (workflow canvas)
        canvas_elements = await page.query_selector_all('canvas, [class*="canvas"]')
        print(f"Found {len(canvas_elements)} canvas elements")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(test_n8n_iframe())

