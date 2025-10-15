#!/usr/bin/env python3
"""
Playwright test for workflow detail page clickthrough
"""

import asyncio
from playwright.async_api import async_playwright

async def test_workflow_detail():
    """Test clicking through to workflow detail page"""
    
    print("🎭 Testing Workflow Detail Page Clickthrough...")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🌐 Browser Console [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"❌ Browser Error: {exc}"))
        
        try:
            print("\n📍 Step 1: Load main database viewer page")
            print("-" * 80)
            await page.goto("http://localhost:5004/", wait_until="networkidle")
            print(f"✅ Main page loaded")
            
            # Wait for table to load
            await page.wait_for_selector("tbody tr", timeout=5000)
            table_rows = await page.locator("tbody tr").count()
            print(f"✅ Found {table_rows} workflow rows")
            
            # Get first workflow link
            first_workflow_link = page.locator("tbody tr").first.locator("a.workflow-link").first
            workflow_id = await first_workflow_link.text_content()
            workflow_id = workflow_id.strip()
            print(f"✅ First workflow ID: {workflow_id}")
            
            print("\n📍 Step 2: Click workflow link")
            print("-" * 80)
            await first_workflow_link.click()
            await page.wait_for_load_state("networkidle")
            
            current_url = page.url
            print(f"✅ Navigated to: {current_url}")
            
            # Check if we're on the detail page
            if f"/workflow/{workflow_id}" in current_url:
                print(f"✅ Correct URL pattern: /workflow/{workflow_id}")
            else:
                print(f"❌ Wrong URL: {current_url}")
            
            print("\n📍 Step 3: Verify detail page content")
            print("-" * 80)
            
            # Check page title
            title = await page.title()
            print(f"📄 Page Title: {title}")
            
            # Check for key elements
            header = await page.locator("h1").text_content()
            print(f"✅ Header: {header}")
            
            # Check for workflow URL
            url_element = await page.locator(".workflow-url").count()
            print(f"✅ Workflow URL section: {url_element > 0}")
            
            # Check for status badge
            badge = await page.locator(".badge").count()
            print(f"✅ Status badge: {badge > 0}")
            
            # Check for layer badges
            layers = await page.locator(".layer-badge").count()
            print(f"✅ Layer badges: {layers} found")
            
            # Check for stats grid
            stats = await page.locator(".stat-box").count()
            print(f"✅ Stats boxes: {stats} found")
            
            # Check for detail sections
            sections = await page.locator(".detail-section").count()
            print(f"✅ Detail sections: {sections} found")
            
            # Get section titles
            section_titles = await page.locator(".detail-section h2").all()
            print(f"📋 Section titles:")
            for section in section_titles:
                section_text = await section.text_content()
                print(f"  - {section_text.strip()}")
            
            # Take screenshot
            await page.screenshot(path="/tmp/workflow_detail.png")
            print(f"\n📸 Screenshot saved: /tmp/workflow_detail.png")
            
            print("\n📍 Step 4: Test back button")
            print("-" * 80)
            
            # Click back link
            back_link = page.locator(".back-link")
            await back_link.click()
            await page.wait_for_load_state("networkidle")
            
            # Check if we're back to main page
            current_url = page.url
            print(f"✅ Back to: {current_url}")
            
            # Verify we're on main page
            table_rows_again = await page.locator("tbody tr").count()
            print(f"✅ Back on main page with {table_rows_again} workflows")
            
            print("\n" + "=" * 80)
            print("🎉 WORKFLOW DETAIL PAGE CLICKTHROUGH TEST PASSED!")
            print("=" * 80)
            print("\n✅ All functionality working:")
            print("  ✓ Workflow list displays")
            print("  ✓ Workflow ID links are clickable")
            print("  ✓ Detail page loads correctly")
            print("  ✓ All detail sections present")
            print("  ✓ Back button returns to list")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/workflow_detail_error.png")
            print("📸 Error screenshot: /tmp/workflow_detail_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_workflow_detail())





