#!/usr/bin/env python3
"""
Deep investigation of n8n.io workflow JSON access
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def investigate_workflow_json():
    """Deep investigation of how to get workflow JSON."""
    
    print("=" * 80)
    print("🔍 DEEP INVESTIGATION: n8n.io Workflow JSON Access")
    print("=" * 80)
    print()
    
    workflow_id = "1954"
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Non-headless to see what happens
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track all network requests
        json_requests = []
        
        async def handle_response(response):
            """Track all responses that might contain JSON."""
            url = response.url
            content_type = response.headers.get('content-type', '')
            
            # Look for JSON responses
            if 'json' in content_type.lower() or 'json' in url.lower():
                json_requests.append({
                    'url': url,
                    'status': response.status,
                    'content_type': content_type
                })
                print(f"  📡 JSON Response: {url[:80]}...")
        
        page.on('response', handle_response)
        
        print(f"📄 Loading workflow page: {url}")
        await page.goto(url, wait_until='networkidle')
        print("✅ Page loaded")
        print()
        
        # Wait a bit for any async content
        await asyncio.sleep(2)
        
        # Check page content for embedded JSON
        print("🔍 Checking page source for embedded workflow JSON...")
        page_content = await page.content()
        
        # Look for JSON data in script tags
        scripts = await page.locator('script[type="application/json"]').all()
        print(f"Found {len(scripts)} JSON script tags")
        
        for i, script in enumerate(scripts[:5]):  # Check first 5
            try:
                script_content = await script.text_content()
                if script_content and 'nodes' in script_content:
                    print(f"  ✅ Script {i+1} contains 'nodes' (likely workflow JSON)")
                    print(f"     First 200 chars: {script_content[:200]}")
                    
                    # Try to parse it
                    try:
                        data = json.loads(script_content)
                        if 'nodes' in data:
                            print(f"     ✅ Valid workflow JSON found!")
                            print(f"     Nodes: {len(data.get('nodes', []))}")
                            print(f"     Connections: {len(data.get('connections', {}))}")
                            return data
                    except:
                        pass
            except:
                pass
        
        print()
        
        # Check for Next.js data
        print("🔍 Checking for Next.js __NEXT_DATA__...")
        next_data = await page.evaluate('() => window.__NEXT_DATA__')
        if next_data:
            print("  ✅ Found __NEXT_DATA__")
            # Try to find workflow data in it
            if 'props' in next_data:
                print("     Has props key")
                props_str = json.dumps(next_data['props'])
                if 'nodes' in props_str:
                    print("     ✅ Props contain workflow nodes!")
        
        print()
        print("🔍 Network requests captured:")
        for req in json_requests[:10]:
            print(f"  - {req['url'][:80]}... (Status: {req['status']})")
        
        # Keep browser open for manual inspection
        print()
        print("⏸️  Browser staying open for 10 seconds for manual inspection...")
        await asyncio.sleep(10)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(investigate_workflow_json())





