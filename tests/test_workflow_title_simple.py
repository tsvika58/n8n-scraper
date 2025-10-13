#!/usr/bin/env python3
"""
Simple test for workflow title display
"""

import asyncio
from playwright.async_api import async_playwright

async def test_workflow_title_simple():
    """Test that workflow title is displayed"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to workflow detail page
            await page.goto('http://localhost:5004/workflow/9390', timeout=10000)
            
            # Wait for the page to load
            await page.wait_for_selector('.header', timeout=5000)
            
            # Check that workflow title is displayed
            title_element = page.locator('.workflow-title h2')
            await title_element.wait_for(timeout=5000)
            
            title_text = await title_element.text_content()
            print(f"✅ Workflow Title: {title_text}")
            
            # Verify the title contains expected content
            assert 'Enhance Product Photos' in title_text
            assert 'Google Gemini AI' in title_text
            
            print("✅ Workflow title is properly displayed")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_workflow_title_simple())

