#!/usr/bin/env python3
"""
Test Categories Column Display
"""

import asyncio
from playwright.async_api import async_playwright

async def test_categories():
    """Test that categories column is displaying correctly"""
    
    print("🎭 Testing Categories Column...")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("\n📍 Loading database viewer...")
            await page.goto("http://localhost:5004/", wait_until="networkidle")
            
            # Check for Categories header
            headers = await page.locator("th").all()
            header_texts = []
            for header in headers:
                text = await header.text_content()
                header_texts.append(text.strip())
            
            print(f"✅ Table Headers: {header_texts}")
            
            if "Categories" in str(header_texts):
                print("✅ Categories column header found!")
            else:
                print("❌ Categories column header NOT found!")
            
            # Check for category badges in first row
            first_row = page.locator("tbody tr").first
            row_html = await first_row.inner_html()
            
            if "category-badge" in row_html:
                print("✅ Category badges found in table rows!")
                
                # Extract category text
                badges = await first_row.locator(".category-badge").all()
                print(f"📊 Found {len(badges)} category badges in first row")
                for i, badge in enumerate(badges):
                    text = await badge.text_content()
                    print(f"  {i+1}. {text}")
            elif "Uncategorized" in row_html:
                print("✅ 'Uncategorized' text found for workflows without categories")
            else:
                print("❌ No category badges or 'Uncategorized' text found!")
            
            # Take screenshot
            await page.screenshot(path="/tmp/categories_column.png")
            print(f"\n📸 Screenshot saved: /tmp/categories_column.png")
            
            print("\n" + "=" * 80)
            print("🎉 CATEGORIES COLUMN TEST COMPLETE!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/categories_error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_categories())



