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
from typing import Optional, Tuple
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
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize transcript extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Timeout for page operations in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
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
            
            # Step 2: Try to open transcript panel
            transcript_opened = await self._open_transcript_panel(page)
            
            if not transcript_opened:
                return False, None, "Could not open transcript panel"
            
            # Step 3: Extract transcript text
            transcript_text = await self._extract_transcript_text(page)
            
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
    
    async def _extract_transcript_text(self, page: Page) -> Optional[str]:
        """
        Extract transcript text from the transcript panel.
        
        Args:
            page: Playwright page object
            
        Returns:
            Transcript text or None if not found
        """
        try:
            # Wait for transcript segments to load
            await asyncio.sleep(1)
            
            # Try multiple selectors for transcript segments
            segment_selectors = [
                'ytd-transcript-segment-renderer .segment-text',
                '.ytd-transcript-segment-renderer',
                '[class*="segment-text"]',
                'yt-formatted-string.segment-text'
            ]
            
            for selector in segment_selectors:
                try:
                    segments = await page.locator(selector).all_text_contents()
                    
                    if segments and len(segments) > 0:
                        # Clean and join segments
                        clean_segments = [seg.strip() for seg in segments if seg.strip()]
                        full_text = ' '.join(clean_segments)
                        
                        if len(full_text) > 50:  # Reasonable minimum length
                            logger.debug(f"Extracted {len(segments)} segments with selector: {selector}")
                            return full_text
                except:
                    continue
            
            logger.warning("No transcript segments found with any selector")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting transcript text: {e}")
            return None


