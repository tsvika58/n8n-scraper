#!/usr/bin/env python3
"""
Manual inspection script for Layer 2 data sources.
Inspects n8n workflow pages to document all available data sources.
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

# Test workflows for inspection
TEST_WORKFLOWS = [
    {'id': '1954', 'url': 'https://n8n.io/workflows/1954'},
    {'id': '2462', 'url': 'https://n8n.io/workflows/2462'},
    {'id': '2134', 'url': 'https://n8n.io/workflows/2134'},
    {'id': '9343', 'url': 'https://n8n.io/workflows/9343'},
    {'id': '3456', 'url': 'https://n8n.io/workflows/3456'},
]


async def inspect_workflow_page(workflow):
    """Inspect a single workflow page for all data sources."""
    
    print(f"\n{'='*80}")
    print(f"🔍 INSPECTING WORKFLOW #{workflow['id']}")
    print(f"   URL: {workflow['url']}")
    print(f"{'='*80}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to workflow page
            print("📄 Loading page...")
            await page.goto(workflow['url'], wait_until='networkidle', timeout=30000)
            print("✅ Page loaded\n")
            
            # === DATA SOURCE 1: Page Title & Metadata ===
            print("📊 DATA SOURCE 1: Page Metadata")
            print("-" * 40)
            
            title = await page.title()
            print(f"Page Title: {title}")
            
            # Get meta tags
            meta_description = await page.locator('meta[name="description"]').get_attribute('content') or "N/A"
            print(f"Meta Description: {meta_description[:100]}...")
            
            # === DATA SOURCE 2: Main Content ===
            print(f"\n📊 DATA SOURCE 2: Main Content")
            print("-" * 40)
            
            # Workflow title
            workflow_title = await page.locator('h1, [class*="title"]').first.text_content() if await page.locator('h1, [class*="title"]').count() > 0 else "N/A"
            print(f"Workflow Title: {workflow_title}")
            
            # Description
            description = await page.locator('[class*="description"], p').first.text_content() if await page.locator('[class*="description"], p').count() > 0 else "N/A"
            print(f"Description: {description[:100] if description else 'N/A'}...")
            
            # === DATA SOURCE 3: Buttons & Actions ===
            print(f"\n📊 DATA SOURCE 3: Action Buttons")
            print("-" * 40)
            
            # Find "Use For Free" or similar buttons
            buttons = await page.locator('button, a[class*="button"]').all()
            button_texts = []
            for button in buttons[:10]:  # Limit to first 10
                try:
                    text = await button.text_content()
                    if text and text.strip():
                        button_texts.append(text.strip())
                except:
                    pass
            
            print(f"Found {len(button_texts)} buttons:")
            for btn_text in button_texts:
                print(f"  • {btn_text}")
            
            use_free_button = any('use' in btn.lower() and 'free' in btn.lower() for btn in button_texts)
            print(f"\n'Use For Free' button found: {use_free_button}")
            
            # === DATA SOURCE 4: Iframes ===
            print(f"\n📊 DATA SOURCE 4: Embedded Iframes")
            print("-" * 40)
            
            iframes = await page.locator('iframe').all()
            print(f"Found {len(iframes)} iframe(s)")
            
            for i, iframe in enumerate(iframes, 1):
                src = await iframe.get_attribute('src') or "N/A"
                title = await iframe.get_attribute('title') or "N/A"
                print(f"\nIframe #{i}:")
                print(f"  Source: {src}")
                print(f"  Title: {title}")
                
                # Try to access iframe content
                if 'n8n' in src.lower() or 'workflow' in src.lower():
                    print(f"  ⚠️ This appears to be an n8n workflow iframe!")
                    
                    try:
                        frame = await iframe.content_frame()
                        if frame:
                            # Try to get workflow data from iframe
                            print(f"  ✅ Iframe accessible, attempting to extract data...")
                            
                            # Check for n8n-specific elements
                            canvas = await frame.locator('[class*="canvas"], [class*="workflow"]').count()
                            nodes = await frame.locator('[class*="node"]').count()
                            
                            print(f"  Canvas elements: {canvas}")
                            print(f"  Node elements: {nodes}")
                            
                            # Try to access window.workflowData
                            try:
                                workflow_data = await frame.evaluate('''
                                    () => {
                                        // Try multiple possible locations for workflow data
                                        return {
                                            hasWindow: typeof window !== 'undefined',
                                            hasWorkflowData: typeof window.workflowData !== 'undefined',
                                            hasN8nWorkflow: typeof window.n8nWorkflow !== 'undefined',
                                            hasVueApp: typeof window.__VUE__ !== 'undefined',
                                            windowKeys: Object.keys(window).filter(k => 
                                                k.includes('workflow') || 
                                                k.includes('n8n') || 
                                                k.includes('node')
                                            )
                                        };
                                    }
                                ''')
                                print(f"  Workflow data check: {json.dumps(workflow_data, indent=4)}")
                            except Exception as e:
                                print(f"  ❌ Could not access workflow data: {e}")
                        else:
                            print(f"  ❌ Iframe not accessible (cross-origin?)")
                    except Exception as e:
                        print(f"  ❌ Error accessing iframe: {e}")
            
            # === DATA SOURCE 5: Try clicking "Use For Free" ===
            if use_free_button:
                print(f"\n📊 DATA SOURCE 5: 'Use For Free' Modal")
                print("-" * 40)
                
                try:
                    # Find and click the button
                    use_button = page.locator('button:has-text("Use"), a:has-text("Use")').first
                    
                    if await use_button.count() > 0:
                        print("Clicking 'Use For Free' button...")
                        await use_button.click()
                        
                        # Wait for modal
                        await page.wait_for_timeout(2000)
                        
                        # Look for modal
                        modal = page.locator('[role="dialog"], [class*="modal"], [class*="popup"]')
                        
                        if await modal.count() > 0:
                            print("✅ Modal appeared!")
                            
                            # Look for JSON content
                            json_content = await page.locator('textarea, pre, code').all()
                            print(f"Found {len(json_content)} potential JSON containers")
                            
                            for i, container in enumerate(json_content[:3], 1):
                                try:
                                    content = await container.text_content()
                                    if content and len(content) > 100:
                                        print(f"\nContainer #{i}:")
                                        print(f"  Length: {len(content)} chars")
                                        print(f"  Preview: {content[:100]}...")
                                        
                                        # Check if it's JSON
                                        if content.strip().startswith('{'):
                                            print(f"  ✅ Looks like JSON!")
                                            try:
                                                parsed = json.loads(content)
                                                print(f"  Keys: {list(parsed.keys())[:10]}")
                                            except:
                                                print(f"  ⚠️ Could not parse as JSON")
                                except:
                                    pass
                        else:
                            print("❌ No modal appeared")
                    else:
                        print("❌ Could not find 'Use For Free' button")
                        
                except Exception as e:
                    print(f"❌ Error with modal: {e}")
            
            # === DATA SOURCE 6: Network Requests ===
            print(f"\n📊 DATA SOURCE 6: Network Requests")
            print("-" * 40)
            
            # This would require setting up request listeners before navigation
            # For now, just note it as a data source
            print("Note: Network request monitoring requires setup before page load")
            print("Potential API endpoints:")
            print("  • https://api.n8n.io/api/workflows/templates/{id}")
            print("  • https://n8n.io/api/workflows/by-id/{id}")
            print("  • Other undocumented endpoints")
            
            # === SUMMARY ===
            print(f"\n{'='*80}")
            print(f"📊 INSPECTION SUMMARY FOR WORKFLOW #{workflow['id']}")
            print(f"{'='*80}")
            print(f"✅ Page loaded successfully")
            print(f"✅ Found {len(iframes)} iframe(s)")
            print(f"✅ Found {len(button_texts)} action buttons")
            print(f"{'✅' if use_free_button else '❌'} 'Use For Free' button present")
            print(f"\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
        
        finally:
            await browser.close()


async def main():
    """Inspect all test workflows."""
    
    print("\n" + "="*80)
    print("🔍 LAYER 2 DATA SOURCES - MANUAL INSPECTION")
    print("="*80)
    print(f"\nInspecting {len(TEST_WORKFLOWS)} workflows...")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for workflow in TEST_WORKFLOWS:
        await inspect_workflow_page(workflow)
        await asyncio.sleep(2)  # Be nice to the server
    
    print("\n" + "="*80)
    print("✅ INSPECTION COMPLETE")
    print("="*80)
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nNext steps:")
    print("  1. Review findings above")
    print("  2. Build enhanced Layer 2 scraper based on available data sources")
    print("  3. Test on sample workflows")
    print("  4. Compare API vs Iframe vs Modal data")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())





