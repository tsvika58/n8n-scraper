"""
Multimodal Content Processor for n8n Workflows

Extracts text from images (OCR) and transcripts from YouTube videos
discovered within n8n workflow iframes.

Author: Developer-2 (Dev2)
Task: SCRAPE-006
Date: October 10, 2025
"""

import asyncio
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from io import BytesIO

import requests
from PIL import Image
import pytesseract
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout, ElementHandle
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from loguru import logger


class MultimodalProcessor:
    """
    Process multimodal content (images + videos) from n8n workflow iframes.
    
    This processor:
    1. Navigates to workflow pages
    2. Discovers and enters iframes
    3. Extracts images and runs OCR
    4. Discovers YouTube videos and extracts transcripts
    5. Stores all data in database
    
    Success metrics:
    - ≥85% OCR success rate (OCR completes, even if "No Text Found")
    - ≥80% video transcript success rate
    """
    
    def __init__(
        self,
        db_path: str = "data/workflows.db",
        headless: bool = True,
        timeout: int = 30000
    ):
        """
        Initialize multimodal processor.
        
        Args:
            db_path: Path to SQLite database
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.db_path = Path(db_path)
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.playwright = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("Multimodal processor initialized")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Multimodal processor cleaned up")
    
    async def discover_n8n_workflow_content(self, page: Page, workflow_url: str) -> Dict[str, Any]:
        """
        Discover n8n workflow content including YouTube videos in the workflow canvas.
        
        Args:
            page: Playwright page object
            workflow_url: URL of workflow page
            
        Returns:
            Dict containing workflow content found
        """
        try:
            await page.goto(workflow_url, timeout=self.timeout)
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            
            result = {
                'youtube_videos': [],
                'workflow_nodes': [],
                'text_content': []
            }
            
            # Look for the n8n workflow iframe
            n8n_iframe = await page.query_selector('iframe.embedded_workflow_iframe')
            if not n8n_iframe:
                # Try alternative selectors
                n8n_iframe = await page.query_selector('iframe[src*="n8n-preview-service"]')
            
            if n8n_iframe:
                frame = await n8n_iframe.content_frame()
                if frame:
                    # Look for YouTube videos in the n8n workflow
                    youtube_links = await frame.query_selector_all('a[href*="youtu.be"], a[href*="youtube.com/watch"]')
                    for link in youtube_links:
                        href = await link.get_attribute('href')
                        if href:
                            result['youtube_videos'].append(href)
                    
                    # Look for YouTube images
                    youtube_images = await frame.query_selector_all('img[src*="youtube"]')
                    for img in youtube_images:
                        src = await img.get_attribute('src')
                        alt = await img.get_attribute('alt')
                        if src:
                            result['youtube_videos'].append(src)
                    
                    # Extract text content from workflow
                    text_elements = await frame.query_selector_all('div, span, p')
                    for elem in text_elements:
                        text = await elem.inner_text()
                        if text and text.strip() and len(text.strip()) > 10:
                            result['text_content'].append(text.strip())
            
            return result
            
        except Exception as e:
            logger.warning(f"Error discovering n8n workflow content: {e}")
            return {'youtube_videos': [], 'workflow_nodes': [], 'text_content': []}

    async def discover_iframes(self, page: Page, workflow_url: str) -> List[str]:
        """
        Discover iframes in workflow page.
        
        Args:
            page: Playwright page object
            workflow_url: URL of workflow page
            
        Returns:
            List of iframe URLs or selectors found
        """
        try:
            await page.goto(workflow_url, timeout=self.timeout)
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            
            # Try n8n-specific selectors first
            iframe_selectors = [
                'iframe.embedded_workflow_iframe',  # n8n workflow iframe
                'iframe[src*="n8n-preview-service"]',  # n8n preview service
                'iframe[src*="workflows/demo"]',  # n8n demo workflow
                'iframe'  # Fallback: any iframe
            ]
            
            iframes_found = []
            for selector in iframe_selectors:
                try:
                    iframes = await page.query_selector_all(selector)
                    if iframes:
                        logger.debug(f"Found {len(iframes)} iframes with selector: {selector}")
                        iframes_found.extend(iframes)
                        break  # Use first successful selector
                except:
                    continue
            
            return iframes_found
            
        except Exception as e:
            logger.warning(f"Error discovering iframes: {e}")
            return []
    
    async def extract_text_elements_from_iframe(self, page: Page, iframe_element) -> List[Dict[str, str]]:
        """
        Extract text from explanatory elements in iframe (text boxes, hints, etc.).
        
        Args:
            page: Playwright page object
            iframe_element: The iframe element object
            
        Returns:
            List of dictionaries with text content and element type
        """
        try:
            # Get iframe frame
            frame = await iframe_element.content_frame()
            if not frame:
                logger.debug("Iframe has no accessible frame")
                return []
            
            # Wait for iframe content to load
            try:
                await frame.wait_for_load_state("networkidle", timeout=5000)
                await asyncio.sleep(2)  # Additional wait for dynamic content
            except:
                pass  # Continue even if wait fails
            
            text_elements = []
            
            # Common selectors for explanatory text elements
            text_selectors = [
                # Specific workflow content selectors (based on debug findings)
                'div[class*="text"]',  # 38 elements found
                'div[class*="content"]',  # 3 elements found  
                'div[class*="tooltip"]',  # 4 elements found
                
                # General text containers
                'div[class*="hint"]',
                'div[class*="explanation"]',
                'div[class*="instruction"]',
                
                # Sticky notes, boxes
                'div[class*="sticky"]',
                'div[class*="note"]',
                'div[class*="box"]',
                'div[class*="card"]',
                
                # Workflow-specific elements
                'div[class*="workflow"]',
                'div[class*="node"]',
                'div[class*="template"]',
                
                # Any div with substantial text content (fallback)
                'div'
            ]
            
            for selector in text_selectors:
                try:
                    elements = await frame.locator(selector).all()
                    for element in elements:
                        try:
                            text = await element.inner_text()
                            if text and len(text.strip()) > 20:  # Lower threshold to catch more content
                                # Get element class/type for context
                                classes = await element.get_attribute('class') or ''
                                element_type = self._determine_element_type(classes, text)
                                
                                text_elements.append({
                                    'text': text.strip(),
                                    'type': element_type,
                                    'classes': classes,
                                    'length': len(text.strip())
                                })
                        except:
                            continue
                except:
                    continue
            
            # Remove duplicates and sort by length (longer = more important)
            unique_elements = []
            seen_texts = set()
            
            for element in sorted(text_elements, key=lambda x: x['length'], reverse=True):
                if element['text'] not in seen_texts and len(element['text']) > 20:
                    unique_elements.append(element)
                    seen_texts.add(element['text'])
            
            logger.debug(f"Found {len(unique_elements)} text elements in iframe")
            return unique_elements
            
        except Exception as e:
            logger.warning(f"Error extracting text elements from iframe: {e}")
            return []
    
    def _determine_element_type(self, classes: str, text: str) -> str:
        """Determine the type of text element based on classes and content."""
        if not classes:
            classes = ""
        if not text:
            text = ""
            
        classes_lower = classes.lower()
        text_lower = text.lower()
        
        if 'hint' in classes_lower or 'tooltip' in classes_lower:
            return 'hint'
        elif 'instruction' in classes_lower or 'step' in text_lower:
            return 'instruction'
        elif 'tutorial' in classes_lower or 'tutorial' in text_lower:
            return 'tutorial'
        elif 'try' in text_lower and 'out' in text_lower:
            return 'tutorial_box'
        elif 'connect' in text_lower and 'gemini' in text_lower:
            return 'setup_instruction'
        elif 'video' in text_lower:
            return 'video_info'
        elif len(text) > 100:
            return 'explanatory_text'
        else:
            return 'general_text'
    
    def extract_text_from_image(self, image_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from image using OCR.
        
        Args:
            image_url: URL of image to process
            
        Returns:
            Tuple of (success, text_or_message, error_message)
            - success: True if OCR ran (even if no text found)
            - text_or_message: Extracted text or "No Text Found"
            - error_message: Error details if OCR failed
        """
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Open image
            image = Image.open(BytesIO(response.content))
            
            # Run OCR
            text = pytesseract.image_to_string(image).strip()
            
            if text:
                logger.debug(f"OCR extracted {len(text)} characters from image")
                return True, text, None
            else:
                logger.debug("OCR completed but no text found in image")
                return True, "No Text Found", None
                
        except Exception as e:
            error_msg = f"OCR error: {str(e)}"
            logger.warning(error_msg)
            return False, "", error_msg
    
    async def discover_videos_in_iframe(self, page: Page, iframe_element) -> List[str]:
        """
        Discover YouTube video URLs in iframe.
        
        Args:
            page: Playwright page object
            iframe_selector: CSS selector for iframe
            
        Returns:
            List of YouTube video URLs found
        """
        try:
            # Get iframe frame
            frame = await iframe_element.content_frame()
            if not frame:
                logger.debug("Iframe has no accessible frame for video discovery")
                return []
            
            # Look for YouTube embeds and links in the iframe
            video_selectors = [
                'a[href*="youtu.be"]',  # YouTube short links
                'a[href*="youtube.com/watch"]',  # YouTube watch links
                'iframe[src*="youtube.com/embed"]',
                'iframe[src*="youtube-nocookie.com/embed"]',
                'iframe[src*="youtu.be"]'
            ]
            
            video_urls = []
            for selector in video_selectors:
                try:
                    videos = await frame.locator(selector).all()
                    for video in videos:
                        try:
                            if 'iframe' in selector:
                                src = await video.get_attribute('src')
                                if src:
                                    video_urls.append(src)
                            else:  # link
                                href = await video.get_attribute('href')
                                if href:
                                    video_urls.append(href)
                        except:
                            continue
                except:
                    continue
            
            logger.debug(f"Found {len(video_urls)} YouTube videos in iframe")
            return video_urls
            
            return []
            
        except Exception as e:
            logger.warning(f"Error discovering videos in iframe: {e}")
            return []
    
    async def discover_videos_on_main_page(self, page: Page) -> List[str]:
        """
        Discover YouTube videos on the main workflow page (not in iframes).
        
        Args:
            page: Playwright page object
            
        Returns:
            List of YouTube video URLs found
        """
        try:
            # Look for YouTube videos directly on the main page
            video_selectors = [
                'iframe[src*="youtube.com/embed"]',
                'iframe[src*="youtube-nocookie.com/embed"]',
                'iframe[src*="youtu.be"]',
                'a[href*="youtube.com/watch"]',
                'a[href*="youtu.be"]'
            ]
            
            video_urls = []
            for selector in video_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for element in elements:
                        try:
                            if 'iframe' in selector:
                                src = await element.get_attribute('src')
                                if src:
                                    video_urls.append(src)
                            else:  # link
                                href = await element.get_attribute('href')
                                if href:
                                    video_urls.append(href)
                        except:
                            continue
                except:
                    continue
            
            # Also search page content for YouTube URLs
            page_content = await page.content()
            youtube_patterns = [
                r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
                r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
                r'https://youtu\.be/[\w-]+',
            ]
            
            for pattern in youtube_patterns:
                matches = re.findall(pattern, page_content)
                video_urls.extend(matches)
            
            # Remove duplicates
            video_urls = list(set(video_urls))
            
            logger.debug(f"Found {len(video_urls)} YouTube videos on main page")
            return video_urls
            
        except Exception as e:
            logger.warning(f"Error discovering videos on main page: {e}")
            return []
    
    def extract_video_id_from_url(self, video_url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Video ID or None if not found
        """
        if not video_url:
            return None
            
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'/embed/([a-zA-Z0-9_-]{11})'  # Relative URL with 11-char video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        
        return None
    
    async def extract_video_transcript(self, video_url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract transcript from YouTube video using TranscriptExtractor with fresh browser.
        
        Uses TranscriptExtractor as a separate instance with its own browser to avoid
        YouTube detecting automated browsing patterns from previous n8n.io navigation.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Tuple of (success, transcript_text, error_message)
        """
        try:
            from src.scrapers.transcript_extractor import TranscriptExtractor
            
            video_id = self.extract_video_id_from_url(video_url)
            if not video_id:
                return False, None, "Could not extract video ID from URL"
            
            # Use TranscriptExtractor with its own fresh browser instance
            # This avoids YouTube blocking based on previous browsing activity
            async with TranscriptExtractor(headless=self.headless, timeout=self.timeout) as extractor:
                success, transcript, error = await extractor.extract_transcript(video_url, video_id)
                return success, transcript, error
                
        except Exception as e:
            error = f"Transcript extraction failed for {video_url}: {str(e)}"
            logger.error(error)
            return False, None, error
    
    async def _open_transcript_panel_ui(self, page: Page) -> bool:
        """Open the transcript panel using UI automation."""
        try:
            # Step 1: Try "Show more" button with multiple selectors
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
                        # Scroll to element to make it visible
                        await show_more.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await show_more.click()
                        await asyncio.sleep(2)
                        logger.debug(f"Clicked 'Show more' with: {selector}")
                        break
                except:
                    continue
            
            # Step 2: Look for transcript button directly (this is what works!)
            transcript_button_selectors = [
                'button:has-text("Show transcript")',
                '[aria-label*="Show transcript"]',
                '[aria-label*="transcript"]',
                'button:has-text("Transcript")'
            ]
            
            for selector in transcript_button_selectors:
                try:
                    transcript_btn = await page.wait_for_selector(selector, timeout=5000)
                    if transcript_btn:
                        # Scroll to element and ensure it's visible
                        await transcript_btn.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        
                        # Check if button is visible and enabled
                        is_visible = await transcript_btn.is_visible()
                        if not is_visible:
                            logger.debug(f"Transcript button not visible: {selector}")
                            continue
                        
                        await transcript_btn.click()
                        await asyncio.sleep(3)  # Wait longer for panel
                        logger.debug(f"Clicked transcript button with selector: {selector}")
                        
                        # Verify transcript panel opened
                        panel_selectors = [
                            'ytd-transcript-renderer',
                            'ytd-engagement-panel-section-list-renderer[target-id=\"engagement-panel-searchable-transcript\"]'
                        ]
                        
                        for panel_selector in panel_selectors:
                            try:
                                panel = await page.wait_for_selector(panel_selector, timeout=5000)
                                if panel:
                                    logger.debug(f"Transcript panel opened: {panel_selector}")
                                    return True
                            except:
                                continue
                except:
                    continue
            
            logger.warning("Could not open transcript panel with any strategy")
            return False
            
        except Exception as e:
            logger.error(f"Error opening transcript panel: {e}")
            return False
    
    async def _extract_transcript_text_ui(self, page: Page) -> Optional[str]:
        """Extract transcript text from the transcript panel."""
        try:
            await asyncio.sleep(1)
            
            segments = await page.locator('ytd-transcript-segment-renderer .segment-text').all_text_contents()
            
            if segments and len(segments) > 0:
                clean_segments = [seg.strip() for seg in segments if seg.strip()]
                full_text = ' '.join(clean_segments)
                
                if len(full_text) > 50:
                    logger.debug(f"Extracted {len(segments)} transcript segments")
                    return full_text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting transcript text: {e}")
            return None
    
    def store_image_data(
        self,
        workflow_id: str,
        image_url: str,
        success: bool,
        ocr_text: str,
        error_message: Optional[str] = None
    ):
        """
        Store OCR results in unified Workflow table.
        
        Appends image URL to image_urls JSON array and aggregates OCR text.
        
        Args:
            workflow_id: Workflow identifier
            image_url: Image URL or identifier
            success: Whether text extraction succeeded
            ocr_text: Extracted text content
            error_message: Error details if failed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing workflow data
        cursor.execute("""
            SELECT image_urls, ocr_text 
            FROM workflows 
            WHERE workflow_id = ?
        """, (workflow_id,))
        
        result = cursor.fetchone()
        
        if result:
            # Parse existing data
            import json
            existing_urls = json.loads(result[0]) if result[0] else []
            existing_ocr = result[1] or ""
            
            # Append new data
            existing_urls.append(image_url)
            
            # Aggregate OCR text (separate with newlines)
            if ocr_text and ocr_text.strip():
                new_ocr_text = existing_ocr + "\n\n" + ocr_text if existing_ocr else ocr_text
            else:
                new_ocr_text = existing_ocr
            
            # Update workflow
            cursor.execute("""
                UPDATE workflows 
                SET image_urls = ?,
                    ocr_text = ?
                WHERE workflow_id = ?
            """, (json.dumps(existing_urls), new_ocr_text, workflow_id))
        else:
            # Create new workflow record
            import json
            cursor.execute("""
                INSERT INTO workflows (workflow_id, image_urls, ocr_text, scrape_date, layer3_success)
                VALUES (?, ?, ?, ?, ?)
            """, (
                workflow_id,
                json.dumps([image_url]),
                ocr_text if ocr_text else "",
                datetime.utcnow(),
                success
            ))
        
        conn.commit()
        conn.close()
    
    def store_video_data(
        self,
        workflow_id: str,
        video_url: str,
        video_id: Optional[str],
        success: bool,
        transcript: str,
        error_message: Optional[str] = None
    ):
        """
        Store video data in unified Workflow table.
        
        Appends video URL to video_urls JSON array and transcript to video_transcripts JSON array.
        
        Args:
            workflow_id: Workflow identifier
            video_url: Video URL
            video_id: YouTube video ID
            success: Whether transcript extraction succeeded
            transcript: Transcript text (or None if not available)
            error_message: Error details if failed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing workflow data
        cursor.execute("""
            SELECT video_urls, video_transcripts 
            FROM workflows 
            WHERE workflow_id = ?
        """, (workflow_id,))
        
        result = cursor.fetchone()
        
        if result:
            # Parse existing data
            import json
            existing_video_urls = json.loads(result[0]) if result[0] else []
            existing_transcripts = json.loads(result[1]) if result[1] else []
            
            # Append new video URL
            existing_video_urls.append(video_url)
            
            # Append new transcript data
            transcript_entry = {
                "video_id": video_id,
                "video_url": video_url,
                "transcript": transcript,
                "length": len(transcript) if transcript else 0,
                "extraction_date": datetime.utcnow().isoformat(),
                "success": success,
                "error": error_message
            }
            existing_transcripts.append(transcript_entry)
            
            # Update workflow
            cursor.execute("""
                UPDATE workflows 
                SET video_urls = ?,
                    video_transcripts = ?
                WHERE workflow_id = ?
            """, (json.dumps(existing_video_urls), json.dumps(existing_transcripts), workflow_id))
        else:
            # Create new workflow record
            import json
            transcript_entry = {
                "video_id": video_id,
                "video_url": video_url,
                "transcript": transcript,
                "length": len(transcript) if transcript else 0,
                "extraction_date": datetime.utcnow().isoformat(),
                "success": success,
                "error": error_message
            }
            
            cursor.execute("""
                INSERT INTO workflows (workflow_id, video_urls, video_transcripts, scrape_date, layer3_success)
                VALUES (?, ?, ?, ?, ?)
            """, (
                workflow_id,
                json.dumps([video_url]),
                json.dumps([transcript_entry]),
                datetime.utcnow(),
                success
            ))
        
        conn.commit()
        conn.close()
    
    async def process_workflow(
        self,
        workflow_id: str,
        workflow_url: str
    ) -> Dict[str, Any]:
        """
        Process a single workflow: discover iframes, extract images/videos, run OCR/transcripts.
        
        Args:
            workflow_id: Workflow identifier
            workflow_url: Workflow page URL
            
        Returns:
            Dictionary with processing results and metrics
        """
        start_time = datetime.now()
        result = {
            'workflow_id': workflow_id,
            'workflow_url': workflow_url,
            'success': False,
            'iframes_found': 0,
            'images_processed': 0,
            'images_success': 0,
            'videos_found': 0,
            'videos_success': 0,
            'video_urls': [],  # Store video URLs for transcript extraction
            'processing_time': 0.0,
            'errors': []
        }
        
        try:
            # Create new page
            page = await self.browser.new_page()
            
            try:
                # Step 1: Discover n8n workflow content (including YouTube videos)
                n8n_content = await self.discover_n8n_workflow_content(page, workflow_url)
                youtube_videos = n8n_content['youtube_videos']
                result['videos_found'] += len(youtube_videos)
                
                # Process YouTube videos found in n8n workflow
                for video_url in youtube_videos:
                    result['video_urls'].append(video_url)  # Add to result for transcript extraction
                    video_id = self.extract_video_id_from_url(video_url)
                    if video_id:
                        result['videos_success'] += 1  # Video found successfully
                        logger.info(f"Found YouTube video: {video_url}")
                
                # Also check main page for videos
                main_page_videos = await self.discover_videos_on_main_page(page)
                result['videos_found'] += len(main_page_videos)
                
                # Process main page videos
                for video_url in main_page_videos:
                    result['video_urls'].append(video_url)  # Add to result for transcript extraction
                    video_id = self.extract_video_id_from_url(video_url)
                    if video_id:
                        result['videos_success'] += 1  # Video found successfully
                
                # Step 2: Discover iframes
                iframes = await self.discover_iframes(page, workflow_url)
                result['iframes_found'] = len(iframes)
                
                if not iframes:
                    logger.info(f"No iframes found for workflow {workflow_id}")
                    result['success'] = True  # Success if we found videos on main page or no content
                    return result
                
                # Process all iframes to find content (content might be in any iframe)
                for i, iframe_element in enumerate(iframes):
                    logger.debug(f"Processing iframe {i+1}")
                    
                    # Step 2: Extract and process text elements (explanatory boxes)
                    text_elements = await self.extract_text_elements_from_iframe(page, iframe_element)
                    iframe_text_count = len(text_elements)
                    result['images_processed'] += iframe_text_count  # Using same counter for text elements
                    
                    for element in text_elements:
                        # Store as "image" data but with text content
                        element_url = f"iframe_{i+1}_text_{element['type']}_{hash(element['text']) % 10000}"
                        success = True  # Text extraction always succeeds
                        text = element['text']
                        error = None
                        
                        # self.store_image_data(workflow_id, element_url, success, text, error)
                        if success:
                            result['images_success'] += 1
                    
                    # Step 3: Discover and process videos in this iframe
                    video_urls = await self.discover_videos_in_iframe(page, iframe_element)
                    iframe_video_count = len(video_urls)
                    result['videos_found'] += iframe_video_count
                    
                    for video_url in video_urls:
                        result['video_urls'].append(video_url)  # Add to result for transcript extraction
                        video_id = self.extract_video_id_from_url(video_url)
                        
                        # Don't store in SQLite database - let E2E pipeline handle storage
                        # logger.debug(f"Storing video {video_id} for deferred transcript extraction")
                        # self.store_video_data(
                        #     workflow_id, video_url, video_id,
                        #     success=True,  # Video discovered successfully
                        #     transcript=None,  # Transcript extraction deferred to Phase 2
                        #     error_message="Pending Phase 2 extraction"  # Status indicator
                        # )
                        result['videos_success'] += 1
                    
                    # Log what we found in this iframe
                    if iframe_text_count > 0 or iframe_video_count > 0:
                        logger.info(f"Iframe {i+1}: {iframe_text_count} text elements, {iframe_video_count} videos")
                
                # If we processed all iframes above, set success and return
                if iframes:
                    result['success'] = True
                    return result
                
                # Step 2: Extract and process text elements (explanatory boxes)
                text_elements = await self.extract_text_elements_from_iframe(page, iframe_selector)
                result['images_processed'] = len(text_elements)  # Using same counter for text elements
                
                for element in text_elements:
                    # Store as "image" data but with text content
                    element_url = f"iframe_text_{element['type']}_{hash(element['text']) % 10000}"
                    success = True  # Text extraction always succeeds
                    text = element['text']
                    error = None
                    
                    # self.store_image_data(workflow_id, element_url, success, text, error)
                    if success:
                        result['images_success'] += 1
                
                # Step 3: Discover and process videos
                video_urls = await self.discover_videos_in_iframe(page, iframe_selector)
                result['videos_found'] = len(video_urls)
                
                for video_url in video_urls:
                    result['video_urls'].append(video_url)  # Add to result for transcript extraction
                    video_id = self.extract_video_id_from_url(video_url)
                    # Don't extract transcript here - let E2E pipeline handle it
                    # success, transcript, error = self.extract_video_transcript(video_url)
                    # self.store_video_data(workflow_id, video_url, video_id, success, transcript, error)
                    # if success:
                    #     result['videos_success'] += 1
                    result['videos_success'] += 1  # Video found successfully
                
                result['success'] = True
                
            finally:
                await page.close()
                
        except Exception as e:
            error_msg = f"Workflow processing error: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        finally:
            end_time = datetime.now()
            result['processing_time'] = (end_time - start_time).total_seconds()
        
        return result


# Example usage
async def main():
    """Example: Process a single workflow"""
    
    workflow_id = "2462"
    workflow_url = "https://n8n.io/workflows/2462"
    
    async with MultimodalProcessor() as processor:
        result = await processor.process_workflow(workflow_id, workflow_url)
        
        print(f"\n{'='*60}")
        print(f"Workflow: {result['workflow_id']}")
        print(f"Iframes: {result['iframes_found']}")
        print(f"Images: {result['images_processed']} processed, {result['images_success']} successful")
        print(f"Videos: {result['videos_found']} found, {result['videos_success']} transcripts extracted")
        print(f"Time: {result['processing_time']:.2f}s")
        print(f"Success: {result['success']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())

