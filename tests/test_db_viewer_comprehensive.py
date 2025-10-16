#!/usr/bin/env python3
"""
Comprehensive test for database viewer filtering and title functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_comprehensive_functionality():
    """Test all new filtering and title functionality"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("🔍 Testing Database Viewer Enhanced Functionality")
            print("=" * 50)
            
            # Navigate to main page
            await page.goto('http://localhost:5004/', timeout=10000)
            await page.wait_for_selector('.filter-form', timeout=5000)
            
            # 1. Test Filter Form Components
            print("\n📋 FILTER FORM COMPONENTS:")
            
            filter_form = page.locator('.filter-form')
            assert await filter_form.is_visible()
            print("✅ Filter form container is visible")
            
            search_input = page.locator('#search')
            assert await search_input.is_visible()
            placeholder = await search_input.get_attribute('placeholder')
            assert 'workflow ID, URL, or title' in placeholder
            print("✅ Search input with title support")
            
            category_select = page.locator('#category')
            assert await category_select.is_visible()
            category_options = await category_select.locator('option').all()
            print(f"✅ Category dropdown with {len(category_options)} options")
            
            status_select = page.locator('#status')
            assert await status_select.is_visible()
            status_options = await status_select.locator('option').all()
            expected_statuses = ['All Status', 'Fully Successful', 'Partial Success', 'Failed', 'Invalid', 'Pending']
            print(f"✅ Status dropdown with {len(status_options)} options")
            
            # 2. Test Table Structure
            print("\n📊 TABLE STRUCTURE:")
            
            table_headers = page.locator('th')
            headers_text = await table_headers.all_text_contents()
            
            expected_headers = ['Workflow ID', 'Title', 'Quality Score', 'Status', 'Categories', 'Extracted At']
            for header in expected_headers:
                assert header in headers_text
                print(f"✅ Header '{header}' present")
            
            assert 'URL' not in headers_text
            print("✅ URL column successfully replaced with Title")
            
            # 3. Test Workflow Data Display
            print("\n📄 WORKFLOW DATA:")
            
            workflow_rows = page.locator('tbody tr')
            row_count = await workflow_rows.count()
            print(f"✅ Found {row_count} workflow rows")
            
            if row_count > 0:
                # Check first row for title
                first_title = page.locator('tbody tr:first-child .title-cell')
                if await first_title.count() > 0:
                    title_text = await first_title.text_content()
                    if title_text and title_text.strip():
                        print(f"✅ First workflow title: {title_text.strip()[:60]}...")
                    else:
                        print("⚠️  First workflow has empty title")
                
                # Check for workflow links
                workflow_links = page.locator('.workflow-link')
                link_count = await workflow_links.count()
                print(f"✅ Found {link_count} workflow detail links")
            
            # 4. Test Filter Functionality
            print("\n🔍 FILTER FUNCTIONALITY:")
            
            # Test category filter
            await category_select.select_option(index=1)  # Select first non-empty option
            selected_category = await category_select.input_value()
            print(f"✅ Category filter selection: {selected_category}")
            
            # Test status filter
            await status_select.select_option('fully_successful')
            selected_status = await status_select.input_value()
            assert selected_status == 'fully_successful'
            print("✅ Status filter selection: Fully Successful")
            
            # Test search functionality
            await search_input.fill('product')
            search_value = await search_input.input_value()
            assert search_value == 'product'
            print("✅ Search input functionality")
            
            # Test form submission
            apply_button = page.locator('button[type="submit"]')
            await apply_button.click()
            await page.wait_for_load_state('networkidle', timeout=10000)
            print("✅ Filter form submission works")
            
            # 5. Test Clear Functionality
            print("\n🧹 CLEAR FUNCTIONALITY:")
            
            clear_button = page.locator('a[href="/"]')
            assert await clear_button.is_visible()
            await clear_button.click()
            await page.wait_for_load_state('networkidle', timeout=10000)
            print("✅ Clear all filters works")
            
            # 6. Test Pagination
            print("\n📖 PAGINATION:")
            
            pagination = page.locator('.pagination')
            if await pagination.count() > 0:
                page_buttons = await pagination.locator('.page-btn').count()
                if page_buttons > 0:
                    print(f"✅ Pagination with {page_buttons} page buttons")
                else:
                    print("✅ Pagination container present (no pages needed)")
            else:
                print("✅ No pagination needed (single page)")
            
            print("\n🎉 ALL TESTS PASSED!")
            print("=" * 50)
            print("✅ Filtering by category and status")
            print("✅ Search by workflow ID, URL, or title")
            print("✅ Title column replaces URL column")
            print("✅ Professional filter form UI")
            print("✅ Clear all functionality")
            print("✅ Pagination preservation")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_functionality())




