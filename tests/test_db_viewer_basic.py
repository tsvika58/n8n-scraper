#!/usr/bin/env python3
"""
Test basic database viewer functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_db_viewer_basic():
    """Test basic functionality in database viewer"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to main page
            await page.goto('http://localhost:5004/', timeout=10000)
            
            # Wait for page to load
            await page.wait_for_selector('.filter-form', timeout=5000)
            
            # Test that filter form is present
            filter_form = page.locator('.filter-form')
            assert await filter_form.is_visible()
            print("✅ Filter form is visible")
            
            # Test search input
            search_input = page.locator('#search')
            assert await search_input.is_visible()
            print("✅ Search input is visible")
            
            # Test category dropdown
            category_select = page.locator('#category')
            assert await category_select.is_visible()
            options = await category_select.locator('option').all()
            print(f"✅ Category dropdown has {len(options)} options")
            
            # Test status dropdown
            status_select = page.locator('#status')
            assert await status_select.is_visible()
            status_options = await status_select.locator('option').all()
            print(f"✅ Status dropdown has {len(status_options)} options")
            
            # Test that Title column is present instead of URL
            table_headers = page.locator('th')
            headers_text = await table_headers.all_text_contents()
            assert 'Title' in headers_text
            assert 'URL' not in headers_text
            print("✅ Title column replaced URL column")
            
            # Check if there are any workflow rows
            workflow_rows = page.locator('tbody tr')
            row_count = await workflow_rows.count()
            print(f"✅ Found {row_count} workflow rows")
            
            if row_count > 0:
                # Test that title is displayed in first row
                first_title = page.locator('tbody tr:first-child .title-cell')
                if await first_title.count() > 0:
                    title_text = await first_title.text_content()
                    print(f"✅ First workflow title: {title_text}")
                else:
                    print("⚠️  No title cell found in first row")
            else:
                print("⚠️  No workflow rows found - this might be expected if database is empty")
            
            # Test clear all button
            clear_button = page.locator('a[href="/"]')
            assert await clear_button.is_visible()
            print("✅ Clear all button is visible")
            
            print("✅ All basic tests passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_db_viewer_basic())

