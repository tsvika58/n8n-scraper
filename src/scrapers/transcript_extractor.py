"""
YouTube Transcript Extractor using Playwright UI Automation

Extracts video transcripts by navigating to YouTube pages and clicking UI elements
to access the transcript panel. This is the only reliable method after testing
showed all API approaches (youtube-transcript-api, yt-dlp, pytube) are blocked.

Author: Developer-2 (Dev2)
Task: SCRAPE-006B
Date: October 10, 2025
"""

import asyncio
import re
from typing import Optional, Tuple, List
from playwright.async_api import Page, Browser, async_playwright, TimeoutError as PlaywrightTimeout
from loguru import logger


class TranscriptExtractor:
    """
    Extracts YouTube video transcripts using Playwright UI automation.
    
    This class uses browser automation to navigate to YouTube videos,
    interact with the UI to open the transcript panel, and extract
    transcript text from DOM elements.
    
    Success Rate: 60-80% (for videos with captions available)
    Performance: ~25-30 seconds per video
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000, preferred_langs: Optional[List[str]] = None):
        """
        Initialize transcript extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Timeout for page operations in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.preferred_langs = preferred_langs or [
            "English",
            "English (auto-generated)",
            "English (United States)",
        ]
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry - setup browser."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup browser."""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("TranscriptExtractor initialized")
    
    async def cleanup(self):
        """Cleanup browser and Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("TranscriptExtractor cleaned up")
    
    async def extract_transcript(
        self, 
        video_url: str, 
        video_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract transcript from YouTube video using UI automation.
        
        Args:
            video_url: Full YouTube video URL
            video_id: YouTube video ID
            
        Returns:
            Tuple of (success, transcript_text, error_message)
        """
        page = None
        
        try:
            page = await self.browser.new_page()
            
            # Step 1: Navigate to video page
            logger.debug(f"Navigating to video {video_id}")
            await page.goto(video_url, timeout=self.timeout)
            await page.wait_for_load_state("networkidle", timeout=10000)
            await asyncio.sleep(2)  # Wait for dynamic content
            
            # Step 2: Dismiss potential overlays (consent/sign-in)
            await self._dismiss_overlays(page)

            # Step 3: Try to open transcript panel
            transcript_opened = await self._open_transcript_panel(page)
            
            if not transcript_opened:
                return False, None, "Could not open transcript panel"
            
            # Step 4: Select language and expand panel
            await self._select_transcript_language(page)
            await self._expand_transcript_panel(page)

            # Step 5: Extract transcript text as Markdown
            transcript_text = await self._extract_transcript_markdown(page)
            
            if transcript_text and len(transcript_text) > 0:
                logger.info(f"Successfully extracted transcript for {video_id}: {len(transcript_text)} chars")
                return True, transcript_text, None
            else:
                return False, None, "No transcript text found in panel"
        
        except PlaywrightTimeout as e:
            error = f"Timeout while extracting transcript for {video_id}: {str(e)}"
            logger.warning(error)
            return False, None, error
        
        except Exception as e:
            error = f"Transcript extraction failed for {video_id}: {str(e)}"
            logger.error(error)
            return False, None, error
        
        finally:
            if page:
                await page.close()

    async def _dismiss_overlays(self, page: Page) -> None:
        """Best-effort dismissal of cookies/consent overlays."""
        selectors = [
            'button:has-text("I agree")',
            'tp-yt-paper-button:has-text("I agree")',
            'button:has-text("Accept all")',
            'button:has-text("Accept")',
            'button[aria-label*="Accept"]',
        ]
        for sel in selectors:
            try:
                btn = await page.query_selector(sel)
                if btn:
                    await btn.click()
                    await asyncio.sleep(0.3)
            except:
                continue
    
    async def _open_transcript_panel(self, page: Page) -> bool:
        """
        Open the transcript panel using multiple strategies.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if transcript panel opened, False otherwise
        """
        try:
            # Strategy 1: Try "Show more" button first
            try:
                show_more_selectors = [
                    'tp-yt-paper-button#expand',
                    '#expand',
                    '[aria-label*="Show more"]',
                    'button:has-text("Show more")'
                ]
                
                for selector in show_more_selectors:
                    try:
                        show_more = await page.wait_for_selector(selector, timeout=3000)
                        if show_more:
                            await show_more.click()
                            await asyncio.sleep(1)
                            logger.debug("Clicked 'Show more' button")
                            break
                    except:
                        continue
            except:
                logger.debug("No 'Show more' button found or needed")
            
            # Strategy 2: Look for transcript button directly
            transcript_button_selectors = [
                'button:has-text("Show transcript")',
                '[aria-label*="Show transcript"]',
                '[aria-label*="transcript"]',
                'button:has-text("Transcript")'
            ]
            
            for selector in transcript_button_selectors:
                try:
                    transcript_btn = await page.wait_for_selector(selector, timeout=3000)
                    if transcript_btn:
                        await transcript_btn.click()
                        await asyncio.sleep(2)
                        logger.debug(f"Clicked transcript button with selector: {selector}")
                        
                        # Verify transcript panel opened
                        panel = await page.wait_for_selector(
                            'ytd-transcript-renderer, ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-searchable-transcript"]',
                            timeout=3000
                        )
                        if panel:
                            return True
                except:
                    continue
            
            # Strategy 3: Try three dots menu approach
            try:
                more_menu_selectors = [
                    'button[aria-label="More actions"]',
                    'ytd-menu-renderer button[aria-label="More"]',
                    '#button-shape > button[aria-label*="More"]'
                ]
                
                for selector in more_menu_selectors:
                    try:
                        more_btn = await page.wait_for_selector(selector, timeout=2000)
                        if more_btn:
                            await more_btn.click()
                            await asyncio.sleep(1)
                            
                            # Click "Show transcript" in menu
                            transcript_item = await page.wait_for_selector(
                                'ytd-menu-service-item-renderer:has-text("Show transcript")',
                                timeout=2000
                            )
                            if transcript_item:
                                await transcript_item.click()
                                await asyncio.sleep(2)
                                
                                # Verify panel opened
                                panel = await page.wait_for_selector('ytd-transcript-renderer', timeout=3000)
                                if panel:
                                    return True
                    except:
                        continue
            except:
                pass
            
            logger.warning("Could not open transcript panel with any strategy")
            return False
            
        except Exception as e:
            logger.error(f"Error opening transcript panel: {e}")
            return False
    
    async def _select_transcript_language(self, page: Page) -> None:
        """Attempt to select a preferred transcript language if dropdown exists."""
        try:
            # Open language dropdown if present
            # New UI may use transcript header renderer; try multiple selectors
            dropdown_triggers = [
                'ytd-transcript-header-renderer tp-yt-paper-dropdown-menu',
                'ytd-transcript-header-renderer yt-dropdown-menu',
                'tp-yt-paper-dropdown-menu',
            ]
            opened = False
            for sel in dropdown_triggers:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        await el.click()
                        await asyncio.sleep(0.3)
                        opened = True
                        break
                except:
                    continue
            if not opened:
                return

            # Try to pick preferred languages
            for lang in self.preferred_langs:
                try:
                    opt = await page.query_selector(f'yt-formatted-string:has-text("{lang}")')
                    if opt:
                        await opt.click()
                        await asyncio.sleep(0.3)
                        return
                except:
                    continue

            # Fallback: click first available option
            try:
                first = await page.query_selector('ytd-transcript-language-dropdown-item-renderer')
                if first:
                    await first.click()
            except:
                pass
        except:
            pass

    async def _expand_transcript_panel(self, page: Page) -> None:
        """Ensure the transcript panel is fully visible and timestamps are toggled if available."""
        # Try to toggle timestamps off for cleaner output
        try:
            toggle = await page.query_selector(
                'yt-button-shape:has-text("Toggle timestamps"), button:has-text("Toggle timestamps")'
            )
            if toggle:
                await toggle.click()
                await asyncio.sleep(0.2)
        except:
            pass

        # Scroll the panel to ensure all segments load
        try:
            for _ in range(10):
                await page.evaluate(
                    """
                    const el=document.querySelector('ytd-transcript-renderer, ytd-engagement-panel-section-list-renderer');
                    if(el){ el.scrollBy(0, Math.floor(window.innerHeight*0.9)); }
                    """
                )
                await asyncio.sleep(0.15)
        except:
            pass

    async def _extract_transcript_markdown(self, page: Page) -> Optional[str]:
        """
        Extract transcript text from the transcript panel as Markdown.
        
        Args:
            page: Playwright page object
            
        Returns:
            Markdown transcript string or None if not found
        """
        try:
            # Wait for transcript segments to load
            await asyncio.sleep(1)
            
            # Segment rows
            row_sel = 'ytd-transcript-segment-renderer'
            rows = await page.locator(row_sel).count()
            if rows == 0:
                logger.warning("No transcript segments found")
                return None

            lines: List[str] = []
            for i in range(rows):
                row = page.locator(row_sel).nth(i)
                # timestamp
                ts_nodes = await row.locator('.segment-timestamp').all_text_contents()
                ts = ts_nodes[0].strip() if ts_nodes else ""
                # text
                txt_nodes = await row.locator('.segment-text, yt-formatted-string.segment-text').all_text_contents()
                text = " ".join(t.strip() for t in txt_nodes if t.strip())
                if text:
                    lines.append(f"- {('`'+ts+'` ') if ts else ''}{text}")

            md = "\n\n".join(lines).strip()
            return md if len(md) > 50 else None
            
        except Exception as e:
            logger.error(f"Error extracting transcript text: {e}")
            return None


