#!/usr/bin/env python3
"""
Investigation script to understand n8n.io JSON download feature
"""

import asyncio
from playwright.async_api import async_playwright


async def investigate_json_download():
    """Investigate how to download workflow JSON from n8n.io."""
    
    print("=" * 80)
    print("🔍 INVESTIGATING n8n.io JSON DOWNLOAD FEATURE")
    print("=" * 80)
    print()
    
    # Test with a known workflow
    workflow_id = "1954"
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    print(f"Testing with workflow: {workflow_id}")
    print(f"URL: {url}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("📄 Loading workflow page...")
        await page.goto(url, wait_until='networkidle')
        print("✅ Page loaded")
        print()
        
        # Look for download buttons or links
        print("🔍 Looking for download/JSON buttons...")
        
        # Check for various download-related selectors
        selectors_to_try = [
            'button:has-text("Download")',
            'a:has-text("Download")',
            'button:has-text("JSON")',
            'a:has-text("JSON")',
            '[data-test-id*="download"]',
            '[class*="download"]',
            'button:has-text("Export")',
            'a[download]',
            'button[aria-label*="download"]'
        ]
        
        for selector in selectors_to_try:
            try:
                element = page.locator(selector).first
                count = await element.count()
                if count > 0:
                    text = await element.text_content()
                    print(f"  ✅ Found: '{selector}' → Text: '{text}'")
            except:
                pass
        
        print()
        
        # Look for any links or buttons
        print("🔍 All buttons on page:")
        buttons = await page.locator('button').all()
        for i, btn in enumerate(buttons[:20]):  # First 20 buttons
            try:
                text = await btn.text_content()
                if text and text.strip():
                    print(f"  Button {i+1}: {text.strip()}")
            except:
                pass
        
        print()
        
        # Check if there's a direct JSON URL pattern
        print("🔍 Checking for direct JSON URL...")
        json_url_patterns = [
            f"https://n8n.io/workflows/{workflow_id}.json",
            f"https://n8n.io/workflows/{workflow_id}/json",
            f"https://n8n.io/workflows/{workflow_id}/download",
            f"https://n8n.io/api/workflows/{workflow_id}/json",
        ]
        
        for json_url in json_url_patterns:
            try:
                print(f"  Testing: {json_url}")
                response = await page.goto(json_url)
                if response and response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"    ✅ SUCCESS! Status: {response.status}, Type: {content_type}")
                    
                    # Try to get the content
                    content = await page.content()
                    if 'nodes' in content or 'connections' in content:
                        print(f"    ✅ Contains workflow JSON data!")
                        print(f"    First 200 chars: {content[:200]}")
                        break
                else:
                    print(f"    ❌ Status: {response.status if response else 'N/A'}")
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        await browser.close()
    
    print()
    print("=" * 80)
    print("Investigation complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(investigate_json_download())





