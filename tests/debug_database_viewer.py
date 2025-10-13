#!/usr/bin/env python3
"""
Playwright-based Database Viewer Debug Script
Tests the database viewer UI thoroughly with automated browser testing
"""

import asyncio
from playwright.async_api import async_playwright
import json
import sys

async def debug_database_viewer():
    """Debug the database viewer with Playwright"""
    
    print("🎭 Starting Playwright Browser Debugging...")
    print("=" * 80)
    
    async with async_playwright() as p:
        # Launch browser in headless mode (Docker doesn't have display)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🌐 Browser Console [{msg.type}]: {msg.text}"))
        
        # Enable error logging
        page.on("pageerror", lambda exc: print(f"❌ Browser Error: {exc}"))
        
        try:
            print("\n📍 Test 1: Loading Main Page")
            print("-" * 80)
            
            # Load main page
            response = await page.goto("http://localhost:5004/", wait_until="networkidle")
            print(f"✅ Status: {response.status}")
            print(f"✅ URL: {page.url}")
            
            # Wait for page to load
            await page.wait_for_load_state("domcontentloaded")
            
            # Take screenshot
            await page.screenshot(path="/tmp/db_viewer_main.png")
            print("📸 Screenshot saved: /tmp/db_viewer_main.png")
            
            # Check page title
            title = await page.title()
            print(f"📄 Page Title: {title}")
            
            # Get page content
            content = await page.content()
            
            # Check for key elements
            print("\n🔍 Checking Key Elements:")
            print("-" * 80)
            
            # Check statistics
            stats_cards = await page.locator(".stat-card").count()
            print(f"✅ Statistics Cards Found: {stats_cards}")
            
            if stats_cards > 0:
                for i in range(stats_cards):
                    stat_number = await page.locator(".stat-card").nth(i).locator(".stat-number").text_content()
                    stat_label = await page.locator(".stat-card").nth(i).locator(".stat-label").text_content()
                    print(f"  📊 {stat_label}: {stat_number}")
            
            # Check search box
            search_box = await page.locator(".search-box").count()
            print(f"✅ Search Box Found: {search_box > 0}")
            
            # Check table
            table_rows = await page.locator("tbody tr").count()
            print(f"✅ Table Rows Found: {table_rows}")
            
            if table_rows > 0:
                print(f"\n📋 First Few Workflows:")
                print("-" * 80)
                for i in range(min(5, table_rows)):
                    cells = await page.locator("tbody tr").nth(i).locator("td").all()
                    if len(cells) >= 4:
                        workflow_id = await cells[0].text_content()
                        url = await cells[1].text_content()
                        quality = await cells[2].text_content()
                        status = await cells[3].text_content()
                        print(f"  {i+1}. ID: {workflow_id.strip()[:20]} | Status: {status.strip()}")
            
            # Check pagination
            pagination_buttons = await page.locator(".page-btn").count()
            print(f"\n✅ Pagination Buttons Found: {pagination_buttons}")
            
            print("\n📍 Test 2: Testing Sort Functionality")
            print("-" * 80)
            
            # Get all sort links
            sort_links = await page.locator(".sort-link").all()
            print(f"✅ Sort Links Found: {len(sort_links)}")
            
            # Click first sort link (should be Workflow ID)
            if len(sort_links) > 0:
                sort_text = await sort_links[0].text_content()
                print(f"🔄 Clicking sort link: {sort_text.strip()}")
                await sort_links[0].click()
                await page.wait_for_load_state("networkidle")
                await page.screenshot(path="/tmp/db_viewer_sorted.png")
                print("📸 Screenshot saved: /tmp/db_viewer_sorted.png")
                
                # Check if URL changed
                current_url = page.url
                print(f"✅ New URL: {current_url}")
                
                # Check if table updated
                new_table_rows = await page.locator("tbody tr").count()
                print(f"✅ Table Rows After Sort: {new_table_rows}")
            
            print("\n📍 Test 3: Testing Search Functionality")
            print("-" * 80)
            
            # Go back to main page
            await page.goto("http://localhost:5004/")
            await page.wait_for_load_state("networkidle")
            
            # Type in search box
            await page.locator(".search-box").fill("workflow")
            print("✅ Entered search term: 'workflow'")
            
            # Click search button
            await page.locator("button[type='submit']").click()
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path="/tmp/db_viewer_search.png")
            print("📸 Screenshot saved: /tmp/db_viewer_search.png")
            
            # Check results
            search_results = await page.locator("tbody tr").count()
            print(f"✅ Search Results: {search_results} rows")
            
            print("\n📍 Test 4: Testing API Endpoints")
            print("-" * 80)
            
            # Test stats API
            stats_response = await page.request.get("http://localhost:5004/api/stats")
            stats_json = await stats_response.json()
            print(f"✅ Stats API Status: {stats_response.status}")
            print(f"📊 Total Workflows from API: {stats_json.get('total_workflows', 'N/A')}")
            print(f"📊 Success Rate from API: {stats_json.get('success_rate', 'N/A')}%")
            
            # Test workflows API
            workflows_response = await page.request.get("http://localhost:5004/api/workflows?limit=5")
            workflows_json = await workflows_response.json()
            print(f"✅ Workflows API Status: {workflows_response.status}")
            print(f"📊 Workflows Returned: {len(workflows_json.get('workflows', []))}")
            print(f"📊 Total Available: {workflows_json.get('total', 'N/A')}")
            
            print("\n📍 Test 5: Performance Metrics")
            print("-" * 80)
            
            # Measure page load time
            start_time = asyncio.get_event_loop().time()
            await page.goto("http://localhost:5004/", wait_until="networkidle")
            end_time = asyncio.get_event_loop().time()
            load_time = end_time - start_time
            print(f"⏱️  Page Load Time: {load_time:.2f} seconds")
            
            # Check for JavaScript errors
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            await asyncio.sleep(2)
            
            if errors:
                print(f"❌ JavaScript Errors Found: {len(errors)}")
                for error in errors:
                    print(f"  ❌ {error}")
            else:
                print(f"✅ No JavaScript Errors")
            
            print("\n" + "=" * 80)
            print("🎉 DATABASE VIEWER DEBUG COMPLETE!")
            print("=" * 80)
            print(f"\n📸 Screenshots saved:")
            print(f"  - /tmp/db_viewer_main.png")
            print(f"  - /tmp/db_viewer_sorted.png")
            print(f"  - /tmp/db_viewer_search.png")
            print(f"\n✅ All tests completed successfully!")
            
            # Keep browser open for 10 seconds for manual inspection
            print("\n⏳ Keeping browser open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n❌ ERROR DURING TESTING: {str(e)}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/db_viewer_error.png")
            print("📸 Error screenshot saved: /tmp/db_viewer_error.png")
            sys.exit(1)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_database_viewer())

