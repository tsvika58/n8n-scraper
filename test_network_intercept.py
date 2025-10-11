"""
Test intercepting network requests for workflow JSON
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def intercept_workflow_requests(workflow_id: str):
    """Intercept all network requests to find workflow JSON"""
    url = f"https://n8n.io/workflows/{workflow_id}"
    
    captured_workflow_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Capture all network requests
        async def handle_request(request):
            req_url = request.url
            if any(keyword in req_url.lower() for keyword in ['workflow', 'template', 'api', 'json', workflow_id]):
                print(f"  📡 Request: {req_url}")
        
        async def handle_response(response):
            resp_url = response.url
            if any(keyword in resp_url.lower() for keyword in ['workflow', 'template', 'api', workflow_id]):
                status = response.status
                print(f"  📥 Response [{status}]: {resp_url}")
                
                # Try to get JSON body
                if status == 200:
                    try:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            json_data = await response.json()
                            if isinstance(json_data, dict) and ('workflow' in json_data or 'nodes' in json_data):
                                print(f"      ✅ FOUND WORKFLOW JSON!")
                                print(f"         Keys: {list(json_data.keys())[:10]}")
                                if 'workflow' in json_data and 'nodes' in json_data.get('workflow', {}):
                                    nodes = json_data['workflow']['nodes']
                                    print(f"         ✅ Has workflow.nodes with {len(nodes)} nodes!")
                                captured_workflow_data.append({
                                    'url': resp_url,
                                    'data': json_data
                                })
                    except Exception as e:
                        pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        print(f"\n🔍 Intercepting requests for workflow {workflow_id}: {url}")
        print(f"   Waiting for page load...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(5000)
            
            if captured_workflow_data:
                print(f"\n✅ CAPTURED {len(captured_workflow_data)} workflow JSON responses!")
                for i, item in enumerate(captured_workflow_data):
                    print(f"\n   Response {i+1}: {item['url']}")
                    print(f"   Data keys: {list(item['data'].keys())}")
            else:
                print(f"\n❌ No workflow JSON found in network requests")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        finally:
            await browser.close()
    
    return captured_workflow_data

async def main():
    print("=" * 80)
    print("🔬 Testing Network Request Interception for Workflow JSON")
    print("=" * 80)
    
    # Test workflow with API
    print("\n" + "=" * 80)
    print("TEST 1: Workflow 2462 (Has API)")
    print("=" * 80)
    data1 = await intercept_workflow_requests("2462")
    
    # Test workflow without API
    print("\n" + "=" * 80)
    print("TEST 2: Workflow 2021 (No API)")
    print("=" * 80)
    data2 = await intercept_workflow_requests("2021")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Workflow 2462: {len(data1)} JSON responses captured")
    print(f"Workflow 2021: {len(data2)} JSON responses captured")

asyncio.run(main())
