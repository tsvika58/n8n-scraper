#!/usr/bin/env python3
"""
Detailed Layer 2 inspection - Focus on iframe and modal data extraction.
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def deep_inspect_workflow(workflow_id='1954'):
    """Deep inspection of a single workflow to understand all data sources."""
    
    url = f'https://n8n.io/workflows/{workflow_id}'
    
    print(f"\n{'='*80}")
    print(f"🔬 DEEP INSPECTION: Workflow #{workflow_id}")
    print(f"{'='*80}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track network requests
        api_requests = []
        
        page.on('request', lambda req: api_requests.append({
            'url': req.url,
            'method': req.method,
            'type': req.resource_type
        }) if 'api' in req.url or 'workflow' in req.url else None)
        
        try:
            print("📄 Loading page...")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            print("✅ Page loaded\n")
            
            # === INSPECT IFRAME ===
            print("🔍 INSPECTING IFRAME")
            print("-" * 80)
            
            # Wait for page to be fully loaded
            await asyncio.sleep(3)
            
            # Get all iframes
            iframes = page.frames
            print(f"Total frames: {len(iframes)}")
            
            for i, frame in enumerate(iframes):
                print(f"\nFrame #{i}:")
                print(f"  URL: {frame.url}")
                print(f"  Name: {frame.name}")
                
                # Check if it's the n8n workflow frame
                if 'n8n-preview' in frame.url or 'demo' in frame.url:
                    print(f"  ⚠️ This is the n8n workflow iframe!")
                    
                    # Wait for content to load
                    await asyncio.sleep(3)
                    
                    # Try to extract workflow data
                    print(f"\n  Attempting to extract workflow data...")
                    
                    try:
                        # Get page HTML
                        html = await frame.content()
                        print(f"  HTML length: {len(html)} chars")
                        
                        # Look for workflow data in various places
                        workflow_data = await frame.evaluate('''
                            () => {
                                // Try to find workflow data
                                const results = {
                                    timestamp: new Date().toISOString(),
                                    windowKeys: Object.keys(window).filter(k => 
                                        k.toLowerCase().includes('workflow') || 
                                        k.toLowerCase().includes('n8n') ||
                                        k.toLowerCase().includes('node') ||
                                        k.toLowerCase().includes('canvas')
                                    ),
                                    documentKeys: Object.keys(document).filter(k => 
                                        k.toLowerCase().includes('workflow') || 
                                        k.toLowerCase().includes('n8n')
                                    ),
                                    hasVue: typeof window.__VUE__ !== 'undefined',
                                    hasReact: typeof window.React !== 'undefined',
                                    dataAttributes: []
                                };
                                
                                // Check for data attributes
                                const allElements = document.querySelectorAll('[data-*]');
                                const dataAttrs = new Set();
                                allElements.forEach(el => {
                                    Array.from(el.attributes).forEach(attr => {
                                        if (attr.name.startsWith('data-')) {
                                            dataAttrs.add(attr.name);
                                        }
                                    });
                                });
                                results.dataAttributes = Array.from(dataAttrs);
                                
                                // Try to find canvas or workflow container
                                const canvas = document.querySelector('canvas, [class*="canvas"], [class*="workflow"]');
                                if (canvas) {
                                    results.canvasFound = true;
                                    results.canvasClasses = canvas.className;
                                }
                                
                                // Look for nodes
                                const nodes = document.querySelectorAll('[class*="node"], [data-node]');
                                results.nodeCount = nodes.length;
                                
                                // Try to access any global workflow object
                                if (window.workflowData) {
                                    results.workflowData = 'FOUND';
                                }
                                
                                return results;
                            }
                        ''')
                        
                        print(f"\n  Workflow Data Extraction Results:")
                        print(json.dumps(workflow_data, indent=4))
                        
                    except Exception as e:
                        print(f"  ❌ Error extracting from iframe: {e}")
            
            # === INSPECT MODAL ===
            print(f"\n\n🔍 INSPECTING 'USE FOR FREE' MODAL")
            print("-" * 80)
            
            # Find and click the button
            try:
                use_button = page.locator('button:has-text("Use for free")').first
                
                if await use_button.count() > 0:
                    print("Clicking 'Use for free' button...")
                    await use_button.click()
                    
                    # Wait for modal
                    await asyncio.sleep(2)
                    
                    # Take screenshot
                    await page.screenshot(path=f'modal_screenshot_{workflow_id}.png')
                    print(f"📸 Screenshot saved: modal_screenshot_{workflow_id}.png")
                    
                    # Get modal HTML
                    modal_html = await page.content()
                    
                    # Look for JSON or workflow data
                    print("\nSearching for workflow JSON in modal...")
                    
                    # Try multiple selectors
                    selectors = [
                        'textarea',
                        'pre',
                        'code',
                        '[class*="json"]',
                        '[class*="code"]',
                        '[data-workflow]'
                    ]
                    
                    for selector in selectors:
                        elements = await page.locator(selector).all()
                        if elements:
                            print(f"\nFound {len(elements)} elements matching '{selector}':")
                            for i, el in enumerate(elements[:3], 1):
                                try:
                                    content = await el.text_content()
                                    if content and len(content) > 50:
                                        print(f"  Element #{i}:")
                                        print(f"    Length: {len(content)} chars")
                                        print(f"    Preview: {content[:100]}...")
                                        
                                        # Check if JSON
                                        if content.strip().startswith('{') or content.strip().startswith('['):
                                            try:
                                                parsed = json.loads(content)
                                                print(f"    ✅ Valid JSON!")
                                                print(f"    Type: {type(parsed)}")
                                                if isinstance(parsed, dict):
                                                    print(f"    Keys: {list(parsed.keys())[:10]}")
                                                    
                                                    # Save to file
                                                    with open(f'modal_json_{workflow_id}.json', 'w') as f:
                                                        json.dump(parsed, f, indent=2)
                                                    print(f"    💾 Saved to: modal_json_{workflow_id}.json")
                                            except:
                                                print(f"    ⚠️ Looks like JSON but failed to parse")
                                except Exception as e:
                                    print(f"  Error: {e}")
                    
                    # Look for copy buttons
                    copy_buttons = await page.locator('button:has-text("Copy"), button:has-text("copy")').all()
                    print(f"\nFound {len(copy_buttons)} copy buttons")
                    
            except Exception as e:
                print(f"❌ Error with modal: {e}")
            
            # === NETWORK REQUESTS ===
            print(f"\n\n🔍 NETWORK REQUESTS ANALYSIS")
            print("-" * 80)
            
            print(f"Captured {len(api_requests)} API/workflow requests:")
            for req in api_requests[:20]:  # Show first 20
                print(f"  {req['method']} {req['url']}")
            
            # === FINAL WAIT ===
            print(f"\n\n⏸️  Keeping browser open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
        
        finally:
            await browser.close()
    
    print(f"\n{'='*80}")
    print(f"✅ DEEP INSPECTION COMPLETE")
    print(f"{'='*80}\n")


async def main():
    """Run deep inspection."""
    
    print("\n" + "="*80)
    print("🔬 LAYER 2 DEEP INSPECTION")
    print("="*80)
    print("\nThis will:")
    print("  1. Open browser (visible)")
    print("  2. Navigate to workflow page")
    print("  3. Inspect iframe structure")
    print("  4. Click 'Use for free' and inspect modal")
    print("  5. Capture network requests")
    print("  6. Save screenshots and JSON files")
    print("  7. Keep browser open for 10s for manual inspection")
    print("\n")
    
    await deep_inspect_workflow('1954')
    
    print("\nFiles created:")
    print("  • modal_screenshot_1954.png")
    print("  • modal_json_1954.json (if JSON found)")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())

