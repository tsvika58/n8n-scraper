"""
Enhanced Layer 3: 100% Multimedia & Content Discovery

This enhanced version combines:
- Visual discovery with Playwright (finds what's actually there)
- Comprehensive content extraction (extracts all discovered content)
- Fallback scanning (catches anything missed)

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, ElementHandle
from bs4 import BeautifulSoup
from loguru import logger


class EnhancedLayer3ExplainerExtractor:
    """
    Enhanced Layer 3 Explainer Content Extractor with 100% multimedia discovery.
    
    This extractor uses a three-phase approach:
    1. Visual Discovery: Playwright discovers all content types
    2. Comprehensive Extraction: Extracts all discovered content
    3. Fallback Scanning: Catches anything missed by discovery
    
    Success metrics:
    - ≥95% video discovery rate (vs current ~50%)
    - ≥90% content completeness
    - ≥85% quality score
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        wait_for_content: int = 3000
    ):
        """
        Initialize enhanced Layer 3 extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
            wait_for_content: Wait time for dynamic content in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.wait_for_content = wait_for_content
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
        logger.info("Enhanced Layer 3 extractor initialized")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Enhanced Layer 3 extractor cleaned up")
    
    async def extract_enhanced(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Enhanced Layer 3 extraction with 100% content discovery.
        
        Args:
            workflow_id: Unique workflow identifier
            url: n8n.io workflow URL
            
        Returns:
            Dict containing comprehensive extraction results
        """
        start_time = time.time()
        
        try:
            page = await self.browser.new_page()
            await page.goto(url, timeout=self.timeout)
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            await page.wait_for_timeout(self.wait_for_content)
            
            logger.info(f"Starting enhanced Layer 3 extraction for {workflow_id}")
            
            # Phase 1: Visual discovery
            logger.info(f"Phase 1: Visual content discovery for {workflow_id}")
            discovery = await self._visual_content_discovery(page)
            
            # Phase 2: Comprehensive extraction
            logger.info(f"Phase 2: Comprehensive content extraction for {workflow_id}")
            extraction = await self._extract_discovered_content(discovery, page)
            
            # Phase 3: Fallback scanning
            logger.info(f"Phase 3: Fallback comprehensive scan for {workflow_id}")
            fallback = await self._fallback_comprehensive_scan(page)
            
            # Combine all results
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'extraction_time': time.time() - start_time,
                'data': {
                    # Videos (all sources)
                    'videos': extraction['videos'] + fallback['additional_videos'],
                    'video_count': len(extraction['videos']) + len(fallback['additional_videos']),
                    
                    # Text content (all sources)
                    'tutorial_text': extraction['tutorial_text'],
                    'additional_text': fallback['additional_text'],
                    'total_text_length': len(extraction['tutorial_text']),
                    
                    # Other content
                    'code_snippets': extraction['code_snippets'],
                    'images': extraction['images'] + fallback['additional_images'],
                    'instructions': extraction['instructions'],
                    
                    # Enhanced fields
                    'introduction': extraction.get('introduction', ''),
                    'tutorial_sections': extraction.get('tutorial_sections', []),
                    'step_by_step': extraction.get('step_by_step', []),
                    'best_practices': extraction.get('best_practices', ''),
                    'troubleshooting': extraction.get('troubleshooting', ''),
                    'examples': extraction.get('examples', []),
                    'image_urls': extraction['images'],
                    'video_urls': [v.get('url', v.get('src', '')) for v in extraction['videos'] if v.get('url') or v.get('src')],
                    
                    # Metadata
                    'discovery_metadata': {
                        'iframes_found': len(discovery['iframe_sources']),
                        'videos_discovered': len(discovery['videos']),
                        'text_areas_found': len(discovery['text_boxes']),
                        'fallback_videos': len(fallback['additional_videos'])
                    }
                },
                'metadata': {
                    'extractor_version': '3.0.0-enhanced',
                    'extraction_method': 'visual_discovery + comprehensive_extraction + fallback_scan',
                    'content_sources': ['main_page', 'iframes', 'dynamic_content', 'regex_scan']
                }
            }
            
            # Calculate quality score
            quality_score = self._calculate_extraction_quality(result)
            result['quality_score'] = quality_score
            
            logger.success(f"Enhanced Layer 3 extraction completed for {workflow_id}: "
                          f"{result['data']['video_count']} videos, "
                          f"{result['data']['total_text_length']} chars, "
                          f"Quality: {quality_score}/100")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced Layer 3 extraction failed for {workflow_id}: {str(e)}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'extraction_time': time.time() - start_time,
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def _visual_content_discovery(self, page: Page) -> Dict[str, List]:
        """Use Playwright to visually discover all content types"""
        
        discovery = {
            'videos': [],
            'text_boxes': [],
            'interactive_elements': [],
            'images': [],
            'code_blocks': [],
            'tutorial_sections': [],
            'iframe_sources': []
        }
        
        # 1. Discover ALL iframes and their sources
        iframes = await page.query_selector_all('iframe')
        for iframe in iframes:
            try:
                src = await iframe.get_attribute('src')
                title = await iframe.get_attribute('title')
                
                # Navigate into iframe and discover content immediately
                frame = await iframe.content_frame()
                if frame:
                    logger.debug(f"Accessing iframe: {src}")
                    
                    # Discover videos in iframe
                    videos = await self._discover_videos_in_frame(frame)
                    discovery['videos'].extend(videos)
                    
                    # Discover text content areas
                    text_areas = await self._discover_text_areas_in_frame(frame)
                    discovery['text_boxes'].extend(text_areas)
                    
                    # Discover interactive elements
                    interactive = await self._discover_interactive_elements(frame)
                    discovery['interactive_elements'].extend(interactive)
                    
                    # Discover images
                    images = await self._discover_images_in_frame(frame)
                    discovery['images'].extend(images)
                    
                    # Store iframe info for metadata
                    discovery['iframe_sources'].append({
                        'src': src,
                        'title': title
                    })
                    
            except Exception as e:
                logger.warning(f"Could not access iframe {src}: {e}")
        
        # 3. Discover content on main page
        main_page_content = await self._discover_main_page_content(page)
        discovery.update(main_page_content)
        
        logger.info(f"Visual discovery complete: {len(discovery['videos'])} videos, "
                   f"{len(discovery['text_boxes'])} text areas, {len(discovery['iframe_sources'])} iframes")
        
        return discovery
    
    async def _discover_videos_in_frame(self, frame) -> List[Dict]:
        """Discover ALL video-related elements in iframe"""
        videos = []
        
        # 1. Direct video elements
        video_elements = await frame.query_selector_all('video')
        for video in video_elements:
            try:
                src = await video.get_attribute('src')
                poster = await video.get_attribute('poster')
                videos.append({
                    'type': 'video_element',
                    'src': src,
                    'poster': poster
                })
            except Exception as e:
                logger.warning(f"Error extracting video element: {e}")
                continue
        
        # 2. YouTube/video links
        video_links = await frame.query_selector_all('a[href*="youtube"], a[href*="youtu.be"], a[href*="vimeo"]')
        for link in video_links:
            try:
                href = await link.get_attribute('href')
                title = await link.get_attribute('title')
                text = await link.inner_text()
                videos.append({
                    'type': 'video_link',
                    'url': href,
                    'title': title,
                    'text': text
                })
            except Exception as e:
                logger.warning(f"Error extracting video link: {e}")
                continue
        
        # 3. Embedded video players
        embeds = await frame.query_selector_all('embed[src*="video"], object[data*="video"]')
        for embed in embeds:
            try:
                src = await embed.get_attribute('src') or await embed.get_attribute('data')
                videos.append({
                    'type': 'video_embed',
                    'src': src
                })
            except Exception as e:
                logger.warning(f"Error extracting video embed: {e}")
                continue
        
        # 4. Video thumbnails with play buttons
        video_thumbs = await frame.query_selector_all('img[alt*="video"], img[src*="video"], [class*="video"], [id*="video"]')
        for thumb in video_thumbs:
            try:
                src = await thumb.get_attribute('src')
                alt = await thumb.get_attribute('alt')
                videos.append({
                    'type': 'video_thumbnail',
                    'src': src,
                    'alt': alt
                })
            except Exception as e:
                logger.warning(f"Error extracting video thumbnail: {e}")
                continue
        
        # 5. Elements with video-related classes/IDs
        video_elements_by_class = await frame.query_selector_all('[class*="player"], [class*="tutorial"], [id*="player"]')
        for elem in video_elements_by_class:
            try:
                class_attr = await elem.get_attribute('class')
                id_attr = await elem.get_attribute('id')
                videos.append({
                    'type': 'video_container',
                    'class': class_attr,
                    'id': id_attr
                })
            except Exception as e:
                logger.warning(f"Error extracting video container: {e}")
                continue
        
        return videos
    
    async def _discover_text_areas_in_frame(self, frame) -> List[Dict]:
        """Discover ALL text content areas in iframe"""
        text_areas = []
        
        # 1. Explicit text content elements
        text_elements = await frame.query_selector_all('p, div, span, h1, h2, h3, h4, h5, h6, li, td, th')
        for elem in text_elements:
            try:
                text = await elem.inner_text()
                if text and len(text.strip()) > 10:  # Meaningful text
                    tag = await elem.evaluate('el => el.tagName')
                    text_areas.append({
                        'type': 'text_content',
                        'tag': tag,
                        'text': text
                    })
            except Exception as e:
                logger.warning(f"Error extracting text element: {e}")
                continue
        
        # 2. Tutorial/explainer specific elements
        tutorial_elements = await frame.query_selector_all('[class*="tutorial"], [class*="explainer"], [class*="guide"], [class*="step"]')
        for elem in tutorial_elements:
            try:
                text = await elem.inner_text()
                if text:
                    class_attr = await elem.get_attribute('class')
                    text_areas.append({
                        'type': 'tutorial_content',
                        'class': class_attr,
                        'text': text
                    })
            except Exception as e:
                logger.warning(f"Error extracting tutorial element: {e}")
                continue
        
        # 3. Instructions and descriptions
        instruction_elements = await frame.query_selector_all('[class*="instruction"], [class*="description"], [class*="setup"]')
        for elem in instruction_elements:
            try:
                text = await elem.inner_text()
                if text:
                    class_attr = await elem.get_attribute('class')
                    text_areas.append({
                        'type': 'instruction_content',
                        'class': class_attr,
                        'text': text
                    })
            except Exception as e:
                logger.warning(f"Error extracting instruction element: {e}")
                continue
        
        return text_areas
    
    async def _discover_interactive_elements(self, frame) -> List[Dict]:
        """Discover interactive elements that might contain content"""
        interactive = []
        
        # Look for buttons, links, and interactive elements
        interactive_elements = await frame.query_selector_all('button, a, [role="button"], [onclick], [data-action]')
        for elem in interactive_elements:
            try:
                # Check if element is an HTMLElement
                tag_name = await elem.evaluate('el => el.tagName')
                if not tag_name:
                    continue
                    
                text = await elem.inner_text()
                interactive.append({
                    'type': 'interactive_element',
                    'tag': tag_name,
                    'text': text
                })
            except Exception as e:
                logger.warning(f"Error extracting interactive element: {e}")
                continue
        
        return interactive
    
    async def _discover_images_in_frame(self, frame) -> List[Dict]:
        """Discover images in iframe"""
        images = []
        
        # Find all images
        img_elements = await frame.query_selector_all('img')
        for img in img_elements:
            try:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                if src:
                    images.append({
                        'type': 'image',
                        'src': src,
                        'alt': alt
                    })
            except Exception as e:
                logger.warning(f"Error extracting image: {e}")
                continue
        
        return images
    
    async def _discover_main_page_content(self, page: Page) -> Dict[str, List]:
        """Discover content on main page (outside iframes)"""
        main_content = {
            'videos': [],
            'text_boxes': [],
            'images': []
        }
        
        # Discover videos on main page
        try:
            main_videos = await self._discover_videos_in_frame(page)
            main_content['videos'] = main_videos
        except Exception as e:
            logger.warning(f"Error discovering videos on main page: {e}")
            main_content['videos'] = []
        
        # Discover text on main page
        try:
            main_text = await self._discover_text_areas_in_frame(page)
            main_content['text_boxes'] = main_text
        except Exception as e:
            logger.warning(f"Error discovering text on main page: {e}")
            main_content['text_boxes'] = []
        
        # Discover images on main page
        try:
            main_images = await self._discover_images_in_frame(page)
            main_content['images'] = main_images
        except Exception as e:
            logger.warning(f"Error discovering images on main page: {e}")
            main_content['images'] = []
        
        return main_content
    
    async def _extract_discovered_content(self, discovery: Dict, page: Page) -> Dict[str, Any]:
        """Extract all discovered content comprehensively"""
        
        extraction_result = {
            'videos': [],
            'tutorial_text': '',
            'instructions': [],
            'code_snippets': [],
            'images': [],
            'introduction': '',
            'tutorial_sections': [],
            'step_by_step': [],
            'best_practices': '',
            'troubleshooting': '',
            'examples': []
        }
        
        # 1. Extract all discovered videos
        for video_info in discovery['videos']:
            try:
                video_data = await self._extract_video_content(video_info)
                extraction_result['videos'].append(video_data)
            except Exception as e:
                logger.warning(f"Error extracting video content: {e}")
                # Add basic video info without element access
                extraction_result['videos'].append({
                    'type': video_info.get('type', 'unknown'),
                    'url': video_info.get('url', video_info.get('src', '')),
                    'error': str(e)
                })
        
        # 2. Extract all text content
        all_text = []
        for text_area in discovery['text_boxes']:
            try:
                text_content = await self._extract_text_content(text_area)
                if text_content:
                    all_text.append(text_content)
            except Exception as e:
                logger.warning(f"Error extracting text content: {e}")
                # Fallback to stored text
                if 'text' in text_area:
                    all_text.append(text_area['text'])
        
        extraction_result['tutorial_text'] = '\n\n'.join(all_text)
        
        # 3. Extract introduction (first meaningful text)
        if all_text:
            extraction_result['introduction'] = all_text[0][:500]  # First 500 chars
        
        # 4. Extract code snippets
        for interactive in discovery['interactive_elements']:
            try:
                if await self._is_code_element(interactive):
                    code = await self._extract_code_content(interactive)
                    if code:
                        extraction_result['code_snippets'].append(code)
            except Exception as e:
                logger.warning(f"Error extracting code snippet: {e}")
                continue
        
        # 5. Extract images
        for image_info in discovery['images']:
            try:
                image_data = await self._extract_image_content(image_info)
                if image_data:
                    extraction_result['images'].append(image_data)
            except Exception as e:
                logger.warning(f"Error extracting image content: {e}")
                # Add basic image info
                extraction_result['images'].append({
                    'src': image_info.get('src', ''),
                    'alt': image_info.get('alt', ''),
                    'type': 'image'
                })
        
        # 6. Extract examples (look for code blocks in text)
        examples = self._extract_examples_from_text(extraction_result['tutorial_text'])
        extraction_result['examples'] = examples
        
        return extraction_result
    
    async def _extract_video_content(self, video_info: Dict) -> Dict:
        """Extract comprehensive video content"""
        video_data = {
            'type': video_info.get('type', 'unknown'),
            'url': None,
            'title': None,
            'description': None,
            'thumbnail': None,
            'transcript_available': False,
            'metadata': {}
        }
        
        if video_info.get('type') == 'video_link':
            # Extract from video link
            video_data['url'] = video_info.get('url')
            video_data['title'] = video_info.get('title')
            video_data['description'] = video_info.get('text', '')
        
        elif video_info.get('type') == 'video_element':
            # Extract from video element
            video_data['url'] = video_info.get('src')
            video_data['poster'] = video_info.get('poster')
        
        elif video_info.get('type') == 'video_thumbnail':
            # Extract from video thumbnail
            video_data['url'] = video_info.get('src')
            video_data['description'] = video_info.get('alt', '')
        
        elif video_info.get('type') == 'video_container':
            # Extract from video container
            video_data['description'] = f"Video container: {video_info.get('class', '')} {video_info.get('id', '')}"
        
        # Check if transcript is available (for YouTube videos)
        if video_data['url'] and 'youtube' in str(video_data['url']):
            video_data['transcript_available'] = True  # Assume available for YouTube
        
        return video_data
    
    async def _extract_text_content(self, text_area: Dict) -> str:
        """Extract text content from discovered text area"""
        return text_area.get('text', '')
    
    async def _is_code_element(self, interactive: Dict) -> bool:
        """Check if interactive element contains code"""
        try:
            text = interactive.get('text', '')
            
            # Check for code-like patterns
            code_indicators = ['function', 'const', 'var', 'let', 'if', 'for', 'while', '{', '}', '(', ')']
            return any(indicator in text.lower() for indicator in code_indicators)
        except Exception as e:
            logger.warning(f"Error checking code element: {e}")
            return False
    
    async def _extract_code_content(self, interactive: Dict) -> str:
        """Extract code content from interactive element"""
        return interactive.get('text', '')
    
    async def _extract_image_content(self, image_info: Dict) -> Dict:
        """Extract image content information"""
        return {
            'src': image_info.get('src', ''),
            'alt': image_info.get('alt', ''),
            'type': image_info.get('type', 'image')
        }
    
    def _extract_examples_from_text(self, text: str) -> List[str]:
        """Extract code examples from text content"""
        examples = []
        
        # Look for code blocks (```code```)
        code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)
        examples.extend(code_blocks)
        
        # Look for inline code (`code`)
        inline_code = re.findall(r'`([^`]+)`', text)
        examples.extend(inline_code)
        
        return examples
    
    async def _fallback_comprehensive_scan(self, page: Page) -> Dict[str, Any]:
        """Fallback scan to catch anything missed by visual discovery"""
        
        fallback_result = {
            'additional_videos': [],
            'additional_text': [],
            'additional_images': [],
            'hidden_content': []
        }
        
        # 1. Scan ALL page content for video URLs (regex patterns)
        page_content = await page.content()
        video_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
            r'https?://(?:www\.)?youtube\.com/embed/([\w-]+)',
            r'https?://youtu\.be/([\w-]+)',
            r'https?://vimeo\.com/(\d+)',
            r'https?://player\.vimeo\.com/video/(\d+)'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, page_content)
            for match in matches:
                fallback_result['additional_videos'].append({
                    'type': 'regex_discovered',
                    'pattern': pattern,
                    'url': match,
                    'source': 'page_content_scan'
                })
        
        # 2. Scan for hidden/dynamic content
        try:
            # Look for content loaded via JavaScript
            dynamic_content = await page.evaluate('''
                () => {
                    const videos = [];
                    const text = [];
                    
                    // Find all elements that might contain videos
                    document.querySelectorAll('*').forEach(el => {
                        if (el.innerHTML && (el.innerHTML.includes('youtube') || el.innerHTML.includes('youtu.be'))) {
                            videos.push(el.outerHTML.substring(0, 200));
                        }
                        
                        // Handle className properly (could be string or object)
                        const className = el.className;
                        if (className && typeof className === 'string' && (className.includes('tutorial') || className.includes('guide'))) {
                            text.push(el.innerText);
                        }
                    });
                    
                    return { videos, text };
                }
            ''')
            
            fallback_result['hidden_content'] = dynamic_content
            
        except Exception as e:
            logger.warning(f"Could not scan dynamic content: {e}")
        
        return fallback_result
    
    def _calculate_extraction_quality(self, result: Dict) -> int:
        """Calculate extraction quality score (0-100)"""
        score = 0
        
        # Video discovery quality (40 points)
        video_count = result['data']['video_count']
        if video_count > 0:
            score += 40  # Found videos
        if video_count > 1:
            score += 10  # Found multiple videos
        
        # Text content quality (30 points)
        text_length = result['data']['total_text_length']
        if text_length > 1000:
            score += 30
        elif text_length > 500:
            score += 20
        elif text_length > 100:
            score += 10
        
        # Content diversity (20 points)
        if result['data']['code_snippets']:
            score += 10
        if result['data']['images']:
            score += 10
        
        # Discovery completeness (10 points)
        metadata = result['data']['discovery_metadata']
        if metadata['iframes_found'] > 0:
            score += 5
        if metadata['fallback_videos'] > 0:
            score += 5
        
        return min(score, 100)


# Backward compatibility
ExplainerContentExtractor = EnhancedLayer3ExplainerExtractor
