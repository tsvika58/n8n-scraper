"""
Test if we can extract workflow JSON from page DOM
"""
import asyncio
from playwright.async_api import async_playwright

async def check_workflow_json_in_dom(workflow_id: str):
    """Check if workflow JSON is embedded in page DOM"""
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"\n🔍 Checking workflow {workflow_id}: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Method 1: Check for JSON in script tags
            print("\n📋 Method 1: Looking for JSON in <script> tags...")
            scripts = await page.query_selector_all('script')
            workflow_json_found = False
            
            for i, script in enumerate(scripts):
                content = await script.inner_text()
                if content and ('nodes' in content or 'workflow' in content) and len(content) > 100:
                    print(f"  ✅ Found script {i+1} with potential workflow data ({len(content)} chars)")
                    # Print first 500 chars
                    print(f"     Preview: {content[:500]}...")
                    workflow_json_found = True
                    break
            
            if not workflow_json_found:
                print("  ❌ No workflow JSON found in script tags")
            
            # Method 2: Check for JSON in data attributes
            print("\n📋 Method 2: Looking for JSON in data attributes...")
            elements_with_data = await page.query_selector_all('[data-workflow], [data-json], [data-config]')
            if elements_with_data:
                print(f"  ✅ Found {len(elements_with_data)} elements with data attributes")
                for elem in elements_with_data[:3]:
                    attrs = await elem.evaluate('el => el.outerHTML')
                    print(f"     {attrs[:200]}...")
            else:
                print("  ❌ No elements with data-workflow/json/config attributes")
            
            # Method 3: Check for workflow canvas/iframe
            print("\n📋 Method 3: Looking for workflow canvas/iframe...")
            iframes = await page.query_selector_all('iframe')
            print(f"  Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes):
                src = await iframe.get_attribute('src')
                print(f"  iframe {i+1}: {src}")
            
            # Method 4: Check window object for data
            print("\n�� Method 4: Checking window object...")
            window_data = await page.evaluate('''() => {
                const keys = Object.keys(window).filter(k => 
                    k.toLowerCase().includes('workflow') || 
                    k.toLowerCase().includes('n8n') ||
                    k.toLowerCase().includes('data')
                );
                return keys;
            }''')
            
            if window_data:
                print(f"  ✅ Found window keys: {window_data}")
            else:
                print("  ❌ No relevant window properties found")
            
            # Method 5: Check for Next.js data (common pattern)
            print("\n📋 Method 5: Checking for Next.js __NEXT_DATA__...")
            next_data = await page.evaluate('''() => {
                if (window.__NEXT_DATA__) {
                    return JSON.stringify(window.__NEXT_DATA__).substring(0, 1000);
                }
                return null;
            }''')
            
            if next_data:
                print(f"  ✅ Found __NEXT_DATA__:")
                print(f"     {next_data}...")
            else:
                print("  ❌ No __NEXT_DATA__ found")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        finally:
            await browser.close()

# Test with both working and non-working API workflows
async def main():
    print("=" * 80)
    print("🔬 Testing Workflow JSON Extraction from DOM")
    print("=" * 80)
    
    # Test workflow with API (should work)
    await check_workflow_json_in_dom("2462")
    
    # Test workflow without API (404)
    await check_workflow_json_in_dom("2021")

asyncio.run(main())
