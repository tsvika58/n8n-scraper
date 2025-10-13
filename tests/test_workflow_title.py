#!/usr/bin/env python3
"""
Test workflow title display on detail page
"""

import asyncio
from playwright.async_api import async_playwright

async def test_workflow_title():
    """Test that workflow title is displayed prominently at the top"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to workflow detail page
            await page.goto('http://localhost:5004/workflow/9390', timeout=10000)
            
            # Wait for the page to load
            await page.wait_for_selector('.header', timeout=5000)
            
            # Check that workflow ID is displayed
            workflow_id = await page.locator('.header h1').text_content()
            print(f"✅ Workflow ID: {workflow_id}")
            assert 'Workflow 9390' in workflow_id
            
            # Check that workflow title is displayed
            title_element = page.locator('.workflow-title h2')
            await title_element.wait_for(timeout=5000)
            
            title_text = await title_element.text_content()
            print(f"✅ Workflow Title: {title_text}")
            
            # Verify the title contains expected content
            assert 'Enhance Product Photos' in title_text
            assert 'Google Gemini AI' in title_text
            assert 'E-commerce Catalog' in title_text
            
            # Check that title is properly styled and visible
            title_style = await title_element.evaluate('el => getComputedStyle(el)')
            assert title_style['color'] == 'rgb(45, 55, 72)'  # #2d3748
            assert title_style['font-size'] == '28.8px'  # 1.8em
            
            print("✅ Workflow title is properly displayed and styled")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_workflow_title())

