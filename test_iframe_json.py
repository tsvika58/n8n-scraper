"""
Test extracting workflow JSON from iframe
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def check_iframe_for_json(workflow_id: str):
    """Check if workflow JSON is in iframe"""
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"\n🔍 Checking iframe for workflow {workflow_id}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Find iframes
            iframes = page.frames
            print(f"  Total frames: {len(iframes)}")
            
            for i, frame in enumerate(iframes):
                frame_url = frame.url
                print(f"\n  Frame {i}: {frame_url}")
                
                if 'n8n-preview' in frame_url or 'demo' in frame_url:
                    print(f"    🎯 This looks like workflow preview iframe!")
                    
                    try:
                        # Try to access frame content
                        frame_content = await frame.content()
                        
                        # Look for window.__workflow or similar
                        workflow_data = await frame.evaluate('''() => {
                            // Try different window properties
                            if (window.__workflow) return window.__workflow;
                            if (window.workflow) return window.workflow;
                            if (window.workflowData) return window.workflowData;
                            if (window.n8nWorkflow) return window.n8nWorkflow;
                            
                            // Check for data in various formats
                            const keys = Object.keys(window);
                            for (const key of keys) {
                                if (key.includes('workflow') || key.includes('n8n')) {
                                    return {found_key: key, value: window[key]};
                                }
                            }
                            
                            return null;
                        }''')
                        
                        if workflow_data:
                            print(f"    ✅ FOUND WORKFLOW DATA IN IFRAME!")
                            print(f"       Type: {type(workflow_data)}")
                            print(f"       Keys: {workflow_data.keys() if isinstance(workflow_data, dict) else 'N/A'}")
                            if isinstance(workflow_data, dict) and 'nodes' in workflow_data:
                                print(f"       ✅ Has 'nodes' key with {len(workflow_data['nodes'])} nodes!")
                            print(f"       Preview: {str(workflow_data)[:300]}...")
                        else:
                            print(f"    ❌ No workflow data found in iframe window object")
                        
                        # Check for script tags in iframe
                        scripts_in_iframe = await frame.query_selector_all('script')
                        print(f"    Scripts in iframe: {len(scripts_in_iframe)}")
                        
                    except Exception as e:
                        print(f"    ⚠️ Could not access iframe: {str(e)}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        finally:
            await browser.close()

async def main():
    print("=" * 80)
    print("🔬 Testing Workflow JSON Extraction from Iframe")
    print("=" * 80)
    
    # Test workflow with API
    await check_iframe_for_json("2462")
    
    # Test workflow without API  
    await check_iframe_for_json("2021")

asyncio.run(main())
