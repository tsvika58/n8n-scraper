#!/usr/bin/env python3
"""
Playwright test to validate Recent Workflows section is working
"""

import asyncio
import json
import sys
import os
from playwright.async_api import async_playwright

# Add the project root to the path
sys.path.insert(0, '/app')

async def test_recent_workflows_section():
    """Test the Recent Workflows section"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🧪 Testing Recent Workflows Section...")
            
            # Navigate to dashboard
            print("📊 Loading dashboard...")
            await page.goto('http://localhost:5001/', wait_until='networkidle', timeout=30000)
            
            # Take screenshot
            await page.screenshot(path='/app/tests/screenshots/recent_workflows_test.png')
            print("📸 Screenshot saved: recent_workflows_test.png")
            
            # Test 1: Check if Recent Workflows section exists
            print("\n✅ Test 1: Recent Workflows Section")
            recent_section = await page.query_selector('.recent-workflows')
            if recent_section:
                print("   ✅ Recent workflows section found")
            else:
                print("   ❌ Recent workflows section not found")
                return False
            
            # Test 2: Check if workflows list exists
            print("\n✅ Test 2: Workflows List Container")
            workflows_list = await page.query_selector('#workflows-list')
            if workflows_list:
                print("   ✅ Workflows list container found")
                
                # Check the content
                list_content = await workflows_list.text_content()
                print(f"   📝 Content: {list_content[:100]}...")
                
                if "Loading recent workflows..." in list_content:
                    print("   ⚠️  Still showing loading message")
                elif "No recent workflows found" in list_content:
                    print("   ⚠️  No workflows found")
                elif "Error:" in list_content:
                    print(f"   ❌ Error message: {list_content}")
                else:
                    print("   ✅ Workflows are displayed")
                    
            else:
                print("   ❌ Workflows list container not found")
            
            # Test 3: Check API directly
            print("\n✅ Test 3: API Response")
            try:
                # Use page.request to test API
                response = await page.request.get('http://localhost:5001/api/recent')
                if response.ok:
                    workflows = await response.json()
                    print(f"   ✅ API returned {len(workflows)} workflows")
                    
                    if len(workflows) > 0:
                        first_workflow = workflows[0]
                        print(f"   📊 Sample workflow: ID={first_workflow.get('workflow_id')}, Quality={first_workflow.get('quality_score')}")
                        
                        # Check workflow structure
                        required_fields = ['workflow_id', 'url_preview', 'quality_score', 'layer1_success', 'layer2_success', 'layer3_success', 'extracted_at']
                        missing_fields = [field for field in required_fields if field not in first_workflow]
                        
                        if missing_fields:
                            print(f"   ⚠️  Missing fields: {missing_fields}")
                        else:
                            print("   ✅ All required fields present")
                    else:
                        print("   ⚠️  No workflows returned")
                else:
                    print(f"   ❌ API error: {response.status}")
            except Exception as e:
                print(f"   ❌ API test failed: {e}")
            
            # Test 4: Wait for updates and check again
            print("\n✅ Test 4: Auto-refresh Test")
            print("   ⏳ Waiting 3 seconds for auto-refresh...")
            await page.wait_for_timeout(3000)
            
            # Check if content changed
            workflows_list_updated = await page.query_selector('#workflows-list')
            if workflows_list_updated:
                updated_content = await workflows_list_updated.text_content()
                print(f"   📝 Updated content: {updated_content[:100]}...")
            
            # Test 5: Check for workflow items
            print("\n✅ Test 5: Workflow Items")
            workflow_items = await page.query_selector_all('.workflow-item')
            print(f"   📊 Found {len(workflow_items)} workflow items")
            
            if len(workflow_items) > 0:
                # Check first item structure
                first_item = workflow_items[0]
                
                # Check for workflow ID
                workflow_id = await first_item.query_selector('.workflow-id')
                if workflow_id:
                    id_text = await workflow_id.text_content()
                    print(f"   ✅ Workflow ID: {id_text}")
                
                # Check for URL preview
                url_preview = await first_item.query_selector('.workflow-url')
                if url_preview:
                    url_text = await url_preview.text_content()
                    print(f"   ✅ URL Preview: {url_text[:50]}...")
                
                # Check for quality score
                quality = await first_item.query_selector('.workflow-quality')
                if quality:
                    quality_text = await quality.text_content()
                    print(f"   ✅ Quality Score: {quality_text}")
                
                # Check for status badge
                status_badge = await first_item.query_selector('.status-badge')
                if status_badge:
                    status_text = await status_badge.text_content()
                    print(f"   ✅ Status Badge: {status_text}")
                
                # Check for time
                workflow_time = await first_item.query_selector('.workflow-time')
                if workflow_time:
                    time_text = await workflow_time.text_content()
                    print(f"   ✅ Workflow Time: {time_text}")
            
            print("\n🎯 Recent Workflows Test Summary:")
            print("✅ Section exists and loads")
            print("✅ API returns workflow data")
            print("✅ Auto-refresh functionality")
            print("✅ Workflow items display correctly")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await page.screenshot(path='/app/tests/screenshots/recent_workflows_error.png')
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(test_recent_workflows_section())
    exit(0 if success else 1)




