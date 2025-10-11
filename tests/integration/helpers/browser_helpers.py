"""
Browser automation helpers for integration testing.

Provides utilities for browser setup, teardown, and common operations.

Author: Developer-2 (Dev2)
Task: SCRAPE-006-REWORK
Date: October 10, 2025
"""

import asyncio
from playwright.async_api import async_playwright, Browser, Page


class BrowserTestHelper:
    """Helper for browser automation in integration tests."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize browser helper.
        
        Args:
            headless: Run browser in headless mode
            timeout: Default timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser: Browser = None
    
    async def setup_browser(self) -> Browser:
        """
        Setup browser for integration tests.
        
        Returns:
            Browser instance
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self.browser
    
    async def cleanup_browser(self):
        """Cleanup browser after tests."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def wait_for_iframe_load(self, page: Page, timeout: int = 10000):
        """
        Wait for iframe content to load.
        
        Args:
            page: Playwright page object
            timeout: Wait timeout in milliseconds
        """
        await page.wait_for_load_state('networkidle', timeout=timeout)
        await asyncio.sleep(2)  # Additional wait for dynamic content
    
    async def navigate_to_workflow(self, workflow_url: str) -> Page:
        """
        Navigate to workflow page and wait for load.
        
        Args:
            workflow_url: n8n.io workflow URL
            
        Returns:
            Loaded page object
        """
        page = await self.browser.new_page()
        await page.goto(workflow_url, timeout=self.timeout)
        await page.wait_for_load_state('networkidle', timeout=self.timeout)
        return page
    
    async def get_iframe_elements(self, page: Page):
        """
        Get all iframe elements from page.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of iframe element handles
        """
        iframe_selectors = [
            'iframe[title*="explainer"]',
            'iframe[title*="tutorial"]',
            'iframe[title*="guide"]',
            'iframe'  # Fallback
        ]
        
        for selector in iframe_selectors:
            try:
                iframes = await page.query_selector_all(selector)
                if iframes:
                    return iframes
            except:
                continue
        
        return []
    
    async def extract_iframe_text(self, iframe_element):
        """
        Extract text from iframe element.
        
        Args:
            iframe_element: Iframe element handle
            
        Returns:
            List of text content from iframe
        """
        try:
            frame = await iframe_element.content_frame()
            if not frame:
                return []
            
            await frame.wait_for_load_state("networkidle", timeout=5000)
            await asyncio.sleep(2)
            
            text_elements = []
            text_selectors = ['div[class*="text"]', 'div[class*="content"]', 'div[class*="tooltip"]']
            
            for selector in text_selectors:
                try:
                    elements = await frame.locator(selector).all()
                    for element in elements:
                        try:
                            text = await element.inner_text()
                            if text and len(text.strip()) > 20:
                                text_elements.append(text.strip())
                        except:
                            continue
                except:
                    continue
            
            return text_elements
        except Exception as e:
            return []


