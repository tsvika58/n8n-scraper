#!/usr/bin/env python3
"""
Test YouTube video detection on workflow 7423
"""

import asyncio
from playwright.async_api import async_playwright


async def test_youtube_detection():
    """Test if we can find the YouTube video on workflow 7423."""
    
    url = "https://n8n.io/workflows/7423-lead-generation-agent/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Check page content first
        body_text = await page.inner_text('body')
        print(f"Page loaded. Body text length: {len(body_text)}")
        print(f"Contains 'Lead Generation Agent': {'Lead Generation Agent' in body_text}")
        print(f"Contains 'YouTube': {'YouTube' in body_text}")
        print(f"Contains 'youtu.be': {'youtu.be' in body_text}")
        
        # Look for the specific YouTube link from the HTML
        youtube_link = await page.query_selector('a[href="https://youtu.be/3UwutV1x3mA?si=FtH1dNr5dtnOFedD"]')
        if youtube_link:
            print("✅ Found the specific YouTube link!")
        else:
            print("❌ Could not find the specific YouTube link")
        
        # Look for any YouTube links
        youtube_links = await page.query_selector_all('a[href*="youtu.be"]')
        print(f"Found {len(youtube_links)} YouTube links total")
        
        for i, link in enumerate(youtube_links):
            href = await link.get_attribute('href')
            print(f"  {i+1}. {href}")
        
        # Look for YouTube thumbnails
        youtube_thumbnails = await page.query_selector_all('img[src*="img.youtube.com"]')
        print(f"Found {len(youtube_thumbnails)} YouTube thumbnails")
        
        for i, img in enumerate(youtube_thumbnails):
            src = await img.get_attribute('src')
            alt = await img.get_attribute('alt')
            print(f"  {i+1}. src: {src}")
            print(f"     alt: {alt}")
        
        # Check if page is blocked or redirected
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if current_url != url:
            print("⚠️  Page was redirected!")
        
        # Check for any error messages
        error_selectors = [
            '.error',
            '.not-found',
            '[data-test-id="error"]',
            'h1:has-text("404")',
            'h1:has-text("Not Found")'
        ]
        
        for selector in error_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"Found error element: {selector}")
                for elem in elements:
                    text = await elem.inner_text()
                    if text:
                        print(f"  Error text: {text}")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(test_youtube_detection())




