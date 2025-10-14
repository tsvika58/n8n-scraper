"""
Comprehensive Layer 3: Complete Multimedia & Content Extraction

This comprehensive version includes:
- Video URL extraction and storage
- Video deduplication
- Transcript extraction
- Complete iframe crawling (not just visual)
- Systematic multi-pass extraction
- Validation and quality scoring

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import re
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, ElementHandle
from bs4 import BeautifulSoup
from loguru import logger


class ComprehensiveLayer3Extractor:
    """
    Comprehensive Layer 3 Extractor with complete content discovery.
    
    Multi-pass extraction approach:
    1. Visual Discovery: Playwright discovers visible content
    2. DOM Traversal: Complete HTML parsing for ALL content
    3. Dynamic Content: Scroll, lazy-load, AJAX content
    4. Transcript Extraction: Extract video transcripts
    5. Validation: Screenshot comparison, content hashing
    
    Key Features:
    - ✅ Video URL extraction and storage
    - ✅ Video deduplication
    - ✅ Transcript extraction
    - ✅ Complete iframe crawling
    - ✅ Systematic processes
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        wait_for_content: int = 3000,
        extract_transcripts: bool = True
    ):
        """
        Initialize comprehensive Layer 3 extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
            wait_for_content: Wait time for dynamic content in milliseconds
            extract_transcripts: Whether to extract video transcripts
        """
        self.headless = headless
        self.timeout = timeout
        self.wait_for_content = wait_for_content
        self.extract_transcripts = extract_transcripts
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
        logger.info("Comprehensive Layer 3 extractor initialized")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Comprehensive Layer 3 extractor cleaned up")
    
    async def extract_comprehensive(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Comprehensive multi-pass extraction.
        
        Args:
            workflow_id: Unique workflow identifier
            url: n8n.io workflow URL
            
        Returns:
            Dict containing comprehensive extraction results with ALL features
        """
        start_time = time.time()
        
        try:
            page = await self.browser.new_page()
            await page.goto(url, timeout=self.timeout)
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            await page.wait_for_timeout(self.wait_for_content)
            
            logger.info(f"Starting comprehensive Layer 3 extraction for {workflow_id}")
            
            result = {
                'workflow_id': workflow_id,
                'url': url,
                'extraction_passes': {},
                'final_data': {},
                'metadata': {}
            }
            
            # PASS 1: Visual Discovery
            logger.info(f"Pass 1/5: Visual content discovery for {workflow_id}")
            result['extraction_passes']['pass1_visual'] = await self._pass1_visual_discovery(page)
            
            # PASS 2: DOM Traversal
            logger.info(f"Pass 2/5: Complete DOM traversal for {workflow_id}")
            result['extraction_passes']['pass2_dom'] = await self._pass2_dom_traversal(page)
            
            # PASS 3: Dynamic Content
            logger.info(f"Pass 3/5: Dynamic content extraction for {workflow_id}")
            result['extraction_passes']['pass3_dynamic'] = await self._pass3_dynamic_content(page)
            
            # PASS 4: Video Processing
            logger.info(f"Pass 4/5: Video deduplication and transcript extraction for {workflow_id}")
            result['extraction_passes']['pass4_videos'] = await self._pass4_video_processing(
                result['extraction_passes']
            )
            
            # PASS 5: Validation
            logger.info(f"Pass 5/5: Validation and quality scoring for {workflow_id}")
            result['extraction_passes']['pass5_validation'] = await self._pass5_validation(
                page, workflow_id
            )
            
            # Merge all passes into final data
            result['final_data'] = self._merge_all_passes(result['extraction_passes'])
            
            # Calculate metadata
            result['metadata'] = {
                'extraction_time': time.time() - start_time,
                'extractor_version': '3.0.0-comprehensive',
                'passes_completed': 5,
                'extraction_method': 'multi_pass_comprehensive',
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(result)
            result['quality_score'] = quality_score
            result['success'] = True
            
            logger.success(f"Comprehensive Layer 3 extraction completed for {workflow_id}: "
                          f"{len(result['final_data']['videos'])} videos, "
                          f"{len(result['final_data'].get('transcripts', {}))} transcripts, "
                          f"{result['final_data']['total_text_length']:,} chars, "
                          f"Quality: {quality_score}/100")
            
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive Layer 3 extraction failed for {workflow_id}: {str(e)}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'url': url,
                'extraction_time': time.time() - start_time,
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def _pass1_visual_discovery(self, page: Page) -> Dict:
        """
        Pass 1: Visual content discovery.
        
        Discovers content that is visually present on the page.
        """
        discovery = {
            'videos': [],
            'text_content': [],
            'images': [],
            'iframes': [],
            'interactive_elements': []
        }
        
        # Discover iframes and navigate into them
        iframes = await page.query_selector_all('iframe')
        for iframe in iframes:
            try:
                src = await iframe.get_attribute('src')
                title = await iframe.get_attribute('title')
                
                discovery['iframes'].append({
                    'src': src,
                    'title': title
                })
                
                # Navigate into iframe
                frame = await iframe.content_frame()
                if frame:
                    # Discover videos in iframe
                    iframe_videos = await self._discover_videos_in_frame(frame)
                    discovery['videos'].extend(iframe_videos)
                    
                    # Discover text in iframe
                    iframe_text = await self._discover_text_in_frame(frame)
                    discovery['text_content'].extend(iframe_text)
                    
                    # Discover images in iframe
                    iframe_images = await self._discover_images_in_frame(frame)
                    discovery['images'].extend(iframe_images)
                    
            except Exception as e:
                logger.warning(f"Error in visual discovery for iframe {src}: {e}")
        
        # Discover content on main page
        main_videos = await self._discover_videos_in_frame(page)
        discovery['videos'].extend(main_videos)
        
        main_text = await self._discover_text_in_frame(page)
        discovery['text_content'].extend(main_text)
        
        main_images = await self._discover_images_in_frame(page)
        discovery['images'].extend(main_images)
        
        logger.info(f"Visual discovery: {len(discovery['videos'])} videos, "
                   f"{len(discovery['text_content'])} text elements, "
                   f"{len(discovery['iframes'])} iframes")
        
        return discovery
    
    async def _pass2_dom_traversal(self, page: Page) -> Dict:
        """
        Pass 2: Complete DOM traversal.
        
        Extracts ALL content from DOM, not just visible elements.
        Includes hidden content, data attributes, scripts, etc.
        """
        dom_content = {
            'complete_html': '',
            'all_text': '',
            'all_links': [],
            'all_media': [],
            'data_attributes': [],
            'meta_tags': {},
            'iframes_complete': []
        }
        
        # Get complete page HTML
        dom_content['complete_html'] = await page.content()
        
        # Parse with BeautifulSoup for comprehensive extraction
        soup = BeautifulSoup(dom_content['complete_html'], 'html.parser')
        
        # Extract ALL text (including hidden)
        dom_content['all_text'] = soup.get_text(separator='\n', strip=True)
        
        # Extract ALL links
        for link in soup.find_all('a', href=True):
            dom_content['all_links'].append({
                'href': link['href'],
                'text': link.get_text(strip=True),
                'title': link.get('title', '')
            })
        
        # Extract ALL media
        for media in soup.find_all(['img', 'video', 'audio', 'source', 'iframe']):
            dom_content['all_media'].append({
                'tag': media.name,
                'src': media.get('src', ''),
                'alt': media.get('alt', ''),
                'data_src': media.get('data-src', ''),
                'poster': media.get('poster', ''),
                'type': media.get('type', '')
            })
        
        # Extract data attributes
        for elem in soup.find_all(attrs={'data-src': True}):
            dom_content['data_attributes'].append({
                'tag': elem.name,
                'data_src': elem.get('data-src', ''),
                'data_content': elem.get('data-content', ''),
                'data_video': elem.get('data-video', '')
            })
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property', '')
            content = meta.get('content', '')
            if name and content:
                dom_content['meta_tags'][name] = content
        
        # Process iframes comprehensively
        iframes = await page.query_selector_all('iframe')
        for iframe in iframes:
            try:
                src = await iframe.get_attribute('src')
                frame = await iframe.content_frame()
                
                if frame:
                    # Get complete iframe content
                    iframe_html = await frame.content()
                    iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
                    
                    dom_content['iframes_complete'].append({
                        'src': src,
                        'html': iframe_html,
                        'all_text': iframe_soup.get_text(separator='\n', strip=True),
                        'all_links': [link['href'] for link in iframe_soup.find_all('a', href=True)],
                        'all_media': [{
                            'tag': media.name,
                            'src': media.get('src', ''),
                            'alt': media.get('alt', '')
                        } for media in iframe_soup.find_all(['img', 'video', 'audio'])]
                    })
                    
            except Exception as e:
                logger.warning(f"Error in DOM traversal for iframe {src}: {e}")
        
        logger.info(f"DOM traversal: {len(dom_content['all_text'])} chars text, "
                   f"{len(dom_content['all_links'])} links, "
                   f"{len(dom_content['all_media'])} media elements")
        
        return dom_content
    
    async def _pass3_dynamic_content(self, page: Page) -> Dict:
        """
        Pass 3: Dynamic content extraction.
        
        Scrolls through page, triggers lazy loading, waits for AJAX.
        """
        dynamic = {
            'lazy_loaded_content': [],
            'ajax_content': '',
            'scroll_triggered_content': []
        }
        
        # Scroll through page to trigger lazy loading
        await self._scroll_through_page(page)
        
        # Wait for network idle (AJAX/fetch requests)
        try:
            await page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass  # Continue even if network doesn't idle
        
        # Re-scan for new content
        dynamic['ajax_content'] = await page.content()
        
        # Check for lazy-loaded videos
        new_videos = await self._discover_videos_in_frame(page)
        dynamic['lazy_loaded_content'] = new_videos
        
        # Process iframes after scrolling
        iframes = await page.query_selector_all('iframe')
        for iframe in iframes:
            try:
                frame = await iframe.content_frame()
                if frame:
                    # Scroll through iframe
                    await self._scroll_through_page(frame)
                    
                    # Get new content
                    iframe_videos = await self._discover_videos_in_frame(frame)
                    dynamic['scroll_triggered_content'].extend(iframe_videos)
                    
            except Exception as e:
                logger.warning(f"Error scrolling iframe: {e}")
        
        logger.info(f"Dynamic content: {len(dynamic['lazy_loaded_content'])} lazy-loaded videos, "
                   f"{len(dynamic['scroll_triggered_content'])} scroll-triggered videos")
        
        return dynamic
    
    async def _pass4_video_processing(self, passes: Dict) -> Dict:
        """
        Pass 4: Video deduplication and transcript extraction.
        
        Processes all discovered videos:
        1. Collect all videos from all passes
        2. Deduplicate videos
        3. Extract transcripts for YouTube videos
        4. Store video URLs
        """
        video_processing = {
            'all_videos_raw': [],
            'deduplicated_videos': [],
            'video_urls': [],
            'transcripts': {},
            'deduplication_stats': {}
        }
        
        # Collect all videos from all passes
        for pass_name, pass_data in passes.items():
            if 'videos' in pass_data:
                video_processing['all_videos_raw'].extend(pass_data['videos'])
            if 'lazy_loaded_content' in pass_data:
                video_processing['all_videos_raw'].extend(pass_data['lazy_loaded_content'])
            if 'scroll_triggered_content' in pass_data:
                video_processing['all_videos_raw'].extend(pass_data['scroll_triggered_content'])
        
        logger.info(f"Collected {len(video_processing['all_videos_raw'])} videos from all passes")
        
        # Deduplicate videos
        video_processing['deduplicated_videos'] = self._deduplicate_videos(
            video_processing['all_videos_raw']
        )
        
        video_processing['deduplication_stats'] = {
            'raw_count': len(video_processing['all_videos_raw']),
            'deduplicated_count': len(video_processing['deduplicated_videos']),
            'duplicates_removed': len(video_processing['all_videos_raw']) - len(video_processing['deduplicated_videos'])
        }
        
        logger.info(f"Deduplication: {video_processing['deduplication_stats']['raw_count']} → "
                   f"{video_processing['deduplication_stats']['deduplicated_count']} videos "
                   f"({video_processing['deduplication_stats']['duplicates_removed']} duplicates removed)")
        
        # Extract and store video URLs
        for video in video_processing['deduplicated_videos']:
            video_url = video.get('url') or video.get('src', '')
            if video_url:
                video_processing['video_urls'].append(video_url)
                video['stored_url'] = video_url  # Ensure URL is stored
        
        # Extract transcripts if enabled
        if self.extract_transcripts:
            video_processing['transcripts'] = await self._extract_video_transcripts(
                video_processing['deduplicated_videos']
            )
            
            logger.info(f"Extracted {len(video_processing['transcripts'])} video transcripts")
        
        return video_processing
    
    async def _pass5_validation(self, page: Page, workflow_id: str) -> Dict:
        """
        Pass 5: Validation and quality checks.
        
        Takes screenshots, calculates hashes, validates completeness.
        """
        validation = {
            'screenshot_path': '',
            'content_hash': '',
            'page_height': 0,
            'iframe_count': 0,
            'completeness_checks': {}
        }
        
        # Take screenshot for validation
        try:
            screenshot_path = f'/tmp/layer3_validation_{workflow_id}.png'
            await page.screenshot(path=screenshot_path, full_page=True)
            validation['screenshot_path'] = screenshot_path
        except Exception as e:
            logger.warning(f"Could not take screenshot: {e}")
        
        # Calculate content hash
        content = await page.content()
        validation['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
        
        # Get page metrics
        try:
            validation['page_height'] = await page.evaluate('() => document.body.scrollHeight')
        except:
            validation['page_height'] = 0
        
        # Count iframes
        iframes = await page.query_selector_all('iframe')
        validation['iframe_count'] = len(iframes)
        
        # Completeness checks
        validation['completeness_checks'] = {
            'has_iframes': validation['iframe_count'] > 0,
            'has_content': len(content) > 1000,
            'has_hash': bool(validation['content_hash'])
        }
        
        return validation
    
    def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
        """
        Deduplicate videos by:
        1. YouTube video ID
        2. URL normalization
        3. Source URL comparison
        """
        seen_ids = set()
        seen_urls = set()
        unique_videos = []
        
        for video in videos:
            # Get video URL
            video_url = video.get('url') or video.get('src', '')
            
            if not video_url:
                continue
            
            # Extract YouTube video ID
            video_id = self._extract_youtube_video_id(video_url)
            
            # Check if we've seen this video
            if video_id:
                if video_id in seen_ids:
                    continue  # Skip duplicate
                seen_ids.add(video_id)
                video['youtube_id'] = video_id
            else:
                # Not a YouTube video, check by URL
                normalized_url = video_url.lower().strip()
                if normalized_url in seen_urls:
                    continue  # Skip duplicate
                seen_urls.add(normalized_url)
            
            unique_videos.append(video)
        
        return unique_videos
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        if not url:
            return None
        
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)',
            r'youtube\.com/v/([^?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _extract_video_transcripts(self, videos: List[Dict]) -> Dict[str, str]:
        """
        Extract transcripts for all YouTube videos.
        
        Uses TranscriptExtractor to get video transcripts.
        """
        from src.scrapers.transcript_extractor import TranscriptExtractor
        
        transcripts = {}
        youtube_videos = [v for v in videos if v.get('youtube_id')]
        
        if not youtube_videos:
            logger.info("No YouTube videos found for transcript extraction")
            return transcripts
        
        logger.info(f"Extracting transcripts for {len(youtube_videos)} YouTube videos")
        
        async with TranscriptExtractor(headless=self.headless, timeout=self.timeout) as extractor:
            for video in youtube_videos:
                video_url = video.get('url') or video.get('src', '')
                video_id = video.get('youtube_id', '')
                
                try:
                    success, transcript, error = await extractor.extract_transcript(
                        video_url,
                        video_id
                    )
                    
                    if success and transcript:
                        transcripts[video_url] = transcript
                        video['transcript'] = transcript
                        video['has_transcript'] = True
                        logger.info(f"Extracted transcript for video {video_id} ({len(transcript)} chars)")
                    else:
                        video['has_transcript'] = False
                        video['transcript_error'] = error
                        logger.warning(f"Could not extract transcript for {video_id}: {error}")
                        
                except Exception as e:
                    logger.warning(f"Error extracting transcript for {video_url}: {e}")
                    video['has_transcript'] = False
                    video['transcript_error'] = str(e)
        
        return transcripts
    
    async def _discover_videos_in_frame(self, frame) -> List[Dict]:
        """Discover videos in a frame (page or iframe)"""
        videos = []
        
        # 1. Direct video elements
        try:
            video_elements = await frame.query_selector_all('video')
            for video in video_elements:
                try:
                    src = await video.get_attribute('src')
                    poster = await video.get_attribute('poster')
                    videos.append({
                        'type': 'video_element',
                        'src': src,
                        'poster': poster,
                        'url': src  # Store URL
                    })
                except Exception as e:
                    logger.warning(f"Error extracting video element: {e}")
        except Exception as e:
            logger.warning(f"Error querying video elements: {e}")
        
        # 2. YouTube/video links
        try:
            video_links = await frame.query_selector_all('a[href*="youtube"], a[href*="youtu.be"], a[href*="vimeo"]')
            for link in video_links:
                try:
                    href = await link.get_attribute('href')
                    title = await link.get_attribute('title')
                    text = await link.inner_text()
                    videos.append({
                        'type': 'video_link',
                        'url': href,  # Store URL
                        'title': title,
                        'text': text
                    })
                except Exception as e:
                    logger.warning(f"Error extracting video link: {e}")
        except Exception as e:
            logger.warning(f"Error querying video links: {e}")
        
        # 3. Video thumbnails
        try:
            video_thumbs = await frame.query_selector_all('img[alt*="video"], img[src*="video"]')
            for thumb in video_thumbs:
                try:
                    src = await thumb.get_attribute('src')
                    alt = await thumb.get_attribute('alt')
                    videos.append({
                        'type': 'video_thumbnail',
                        'src': src,
                        'url': src,  # Store URL
                        'alt': alt
                    })
                except Exception as e:
                    logger.warning(f"Error extracting video thumbnail: {e}")
        except Exception as e:
            logger.warning(f"Error querying video thumbnails: {e}")
        
        return videos
    
    async def _discover_text_in_frame(self, frame) -> List[str]:
        """Discover text content in a frame"""
        text_content = []
        
        try:
            text_elements = await frame.query_selector_all('p, div, span, h1, h2, h3, h4, h5, h6, li')
            for elem in text_elements:
                try:
                    text = await elem.inner_text()
                    if text and len(text.strip()) > 10:
                        text_content.append(text.strip())
                except Exception as e:
                    logger.warning(f"Error extracting text: {e}")
        except Exception as e:
            logger.warning(f"Error querying text elements: {e}")
        
        return text_content
    
    async def _discover_images_in_frame(self, frame) -> List[Dict]:
        """Discover images in a frame"""
        images = []
        
        try:
            img_elements = await frame.query_selector_all('img')
            for img in img_elements:
                try:
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    if src:
                        images.append({
                            'src': src,
                            'alt': alt
                        })
                except Exception as e:
                    logger.warning(f"Error extracting image: {e}")
        except Exception as e:
            logger.warning(f"Error querying images: {e}")
        
        return images
    
    async def _scroll_through_page(self, page_or_frame):
        """Scroll through page/frame to trigger lazy loading"""
        try:
            # Get height
            height = await page_or_frame.evaluate('() => document.body.scrollHeight')
            
            # Scroll down in steps
            scroll_step = 500
            current_position = 0
            
            while current_position < height:
                await page_or_frame.evaluate(f'() => window.scrollTo(0, {current_position})')
                await page_or_frame.wait_for_timeout(500)  # Wait for content to load
                current_position += scroll_step
            
            # Scroll back to top
            await page_or_frame.evaluate('() => window.scrollTo(0, 0)')
            
        except Exception as e:
            logger.warning(f"Error scrolling: {e}")
    
    def _merge_all_passes(self, passes: Dict) -> Dict:
        """Merge results from all passes into final data"""
        merged = {
            'videos': [],
            'video_urls': [],
            'transcripts': {},
            'text_content': '',
            'total_text_length': 0,
            'images': [],
            'all_links': [],
            'meta_tags': {},
            'iframes': []
        }
        
        # Get deduplicated videos from pass 4
        if 'pass4_videos' in passes:
            merged['videos'] = passes['pass4_videos'].get('deduplicated_videos', [])
            merged['video_urls'] = passes['pass4_videos'].get('video_urls', [])
            merged['transcripts'] = passes['pass4_videos'].get('transcripts', {})
        
        # Get text from DOM traversal
        if 'pass2_dom' in passes:
            merged['text_content'] = passes['pass2_dom'].get('all_text', '')
            merged['total_text_length'] = len(merged['text_content'])
            merged['all_links'] = passes['pass2_dom'].get('all_links', [])
            merged['meta_tags'] = passes['pass2_dom'].get('meta_tags', {})
        
        # Get images from visual discovery
        if 'pass1_visual' in passes:
            merged['images'] = passes['pass1_visual'].get('images', [])
            merged['iframes'] = passes['pass1_visual'].get('iframes', [])
        
        return merged
    
    def _calculate_quality_score(self, result: Dict) -> int:
        """Calculate quality score (0-100)"""
        score = 0
        final_data = result['final_data']
        
        # Video discovery (30 points)
        video_count = len(final_data.get('videos', []))
        if video_count > 0:
            score += 20
        if video_count > 1:
            score += 10
        
        # Transcript extraction (20 points)
        transcript_count = len(final_data.get('transcripts', {}))
        if transcript_count > 0:
            score += 15
        if transcript_count == video_count and video_count > 0:
            score += 5  # Bonus for complete transcript coverage
        
        # Text content (25 points)
        text_length = final_data.get('total_text_length', 0)
        if text_length > 5000:
            score += 25
        elif text_length > 1000:
            score += 15
        elif text_length > 100:
            score += 5
        
        # Video URLs stored (10 points)
        video_urls = final_data.get('video_urls', [])
        if len(video_urls) > 0:
            score += 10
        
        # Content diversity (15 points)
        if len(final_data.get('images', [])) > 0:
            score += 5
        if len(final_data.get('all_links', [])) > 0:
            score += 5
        if len(final_data.get('iframes', [])) > 0:
            score += 5
        
        return min(score, 100)


# Backward compatibility
ExplainerContentExtractor = ComprehensiveLayer3Extractor
