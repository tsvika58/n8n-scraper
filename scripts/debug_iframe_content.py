"""
Debug script to examine iframe content structure
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def debug_iframe_content():
    """Debug the actual structure of iframe content"""
    
    workflow_url = 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging
        page = await browser.new_page()
        
        try:
            print("🔍 Loading workflow page...")
            await page.goto(workflow_url, timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            print("🔍 Finding iframes...")
            iframes = await page.query_selector_all("iframe")
            print(f"Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes):
                print(f"\n{'='*50}")
                print(f"IFRAME {i+1}")
                print(f"{'='*50}")
                
                try:
                    frame = await iframe.content_frame()
                    if frame:
                        print(f"✅ Iframe {i+1} is accessible")
                        
                        # Get iframe URL
                        iframe_src = await iframe.get_attribute('src')
                        print(f"📍 Iframe URL: {iframe_src}")
                        
                        # Wait a bit for content to load
                        await asyncio.sleep(2)
                        
                        # Try different selectors to find text content
                        selectors_to_try = [
                            'div',
                            '[class*="text"]',
                            '[class*="content"]',
                            '[class*="hint"]',
                            '[class*="tooltip"]',
                            '[class*="instruction"]',
                            'body',
                            'main',
                            'section',
                            'article'
                        ]
                        
                        for selector in selectors_to_try:
                            try:
                                elements = await frame.locator(selector).all()
                                print(f"  {selector}: {len(elements)} elements found")
                                
                                # Get text from first few elements
                                for j, element in enumerate(elements[:3]):
                                    try:
                                        text = await element.inner_text()
                                        if text and len(text.strip()) > 10:
                                            preview = text.strip()[:100].replace('\n', ' ')
                                            print(f"    Element {j+1}: {preview}...")
                                    except:
                                        pass
                                        
                            except Exception as e:
                                print(f"  {selector}: Error - {e}")
                        
                        # Try to get all text content
                        try:
                            all_text = await frame.locator('body').inner_text()
                            if all_text:
                                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                                print(f"\n📝 All text content ({len(lines)} lines):")
                                for line in lines[:10]:  # First 10 lines
                                    print(f"  {line}")
                                if len(lines) > 10:
                                    print(f"  ... and {len(lines) - 10} more lines")
                        except Exception as e:
                            print(f"❌ Could not get all text: {e}")
                            
                    else:
                        print(f"❌ Iframe {i+1} is not accessible")
                        
                except Exception as e:
                    print(f"❌ Error accessing iframe {i+1}: {e}")
            
            # Also check for text content in main page
            print(f"\n{'='*50}")
            print("MAIN PAGE CONTENT")
            print(f"{'='*50}")
            
            main_text = await page.locator('body').inner_text()
            if main_text:
                lines = [line.strip() for line in main_text.split('\n') if line.strip()]
                print(f"Main page has {len(lines)} text lines")
                for line in lines[:5]:
                    print(f"  {line}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_iframe_content())

