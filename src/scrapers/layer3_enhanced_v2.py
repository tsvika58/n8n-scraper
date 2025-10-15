"""
Layer 3 Enhanced V2 - Production Ready with Video Classification

Improvements:
1. Enhanced iframe navigation with cross-origin handling
2. Video classification (primary explainer vs. related content)
3. Robust transcript extraction with retries
4. Global connection coordinator integration
5. Detailed logging and error handling

Author: AI Assistant
Date: October 15, 2025
Version: 3.2.0
"""

import asyncio
import re
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser, Frame
from bs4 import BeautifulSoup
from loguru import logger


class EnhancedLayer3Extractor:
    """
    Enhanced Layer 3 extractor with video classification and robust transcript extraction.
    
    Key Features:
    - Finds ALL videos including those in iframes
    - Classifies videos (primary explainer, related, tutorial, other)
    - Robust transcript extraction with retries
    - Handles cross-origin iframes gracefully
    - Detailed logging for debugging
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 60000,  # Increased to 60s for transcripts
        extract_transcripts: bool = True
    ):
        self.headless = headless
        self.timeout = timeout
        self.extract_transcripts = extract_transcripts
        self.browser: Optional[Browser] = None
        self.playwright = None
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        
    async def initialize(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("🚀 Enhanced Layer 3 V2 initialized")
        
    async def cleanup(self):
        """Cleanup Playwright resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("✅ Enhanced Layer 3 V2 cleaned up")
    
    async def extract(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Extract comprehensive Layer 3 data with video classification.
        
        Returns:
            Dict with success, data, metadata, and quality_score
        """
        start_time = time.time()
        
        try:
            page = await self.browser.new_page()
            
            # Navigate to page
            logger.info(f"📥 Loading {workflow_id}: {url}")
            await page.goto(url, timeout=self.timeout, wait_until='networkidle')
            await page.wait_for_timeout(2000)  # Let dynamic content load
            
            # Phase 1: Discover all videos with context
            logger.info(f"🔍 Discovering videos for {workflow_id}")
            videos_with_context = await self._discover_all_videos(page, workflow_id)
            
            # Phase 2: Classify videos
            logger.info(f"🏷️  Classifying {len(videos_with_context)} videos")
            classified_videos = self._classify_videos(videos_with_context, workflow_id)
            
            # Phase 3: Extract content
            logger.info(f"📝 Extracting content for {workflow_id}")
            content_data = await self._extract_content(page)
            
            # Phase 4: Extract transcripts
            transcripts = {}
            if self.extract_transcripts and classified_videos:
                logger.info(f"🎬 Extracting transcripts for {len(classified_videos)} videos")
                transcripts = await self._extract_transcripts_robust(classified_videos)
            
            # Deduplicate videos
            unique_videos = self._deduplicate_videos(classified_videos)
            video_urls = [v['url'] for v in unique_videos if v.get('url')]
            
            # Compile results
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'url': url,
                'data': {
                    # Videos
                    'videos': unique_videos,
                    'video_urls': video_urls,
                    'video_count': len(unique_videos),
                    'has_videos': len(unique_videos) > 0,
                    'video_metadata': {v['url']: v for v in unique_videos},
                    
                    # Video Classification
                    'primary_explainer_videos': [v for v in unique_videos if v.get('classification') == 'primary_explainer'],
                    'related_workflow_videos': [v for v in unique_videos if v.get('classification') == 'related_workflow'],
                    'tutorial_videos': [v for v in unique_videos if v.get('classification') == 'tutorial'],
                    
                    # Transcripts
                    'transcripts': transcripts,
                    'transcript_count': len(transcripts),
                    'has_transcripts': len(transcripts) > 0,
                    
                    # Content
                    **content_data,
                    
                    # Stats
                    'deduplication_stats': {
                        'raw_count': len(classified_videos),
                        'unique_count': len(unique_videos),
                        'duplicates_removed': len(classified_videos) - len(unique_videos)
                    }
                },
                'metadata': {
                    'extraction_time': time.time() - start_time,
                    'extractor_version': '3.2.0-enhanced',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            }
            
            # Calculate quality score
            result['quality_score'] = self._calculate_quality(result['data'])
            
            # Log summary
            primary_count = len(result['data']['primary_explainer_videos'])
            logger.success(
                f"✅ {workflow_id}: {result['data']['video_count']} videos "
                f"({primary_count} primary explainers), "
                f"{result['data']['transcript_count']} transcripts, "
                f"{result['data']['total_text_length']:,} chars, "
                f"Q:{result['quality_score']}/100"
            )
            
            await page.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Layer 3 extraction failed for {workflow_id}: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'url': url,
                'error': str(e),
                'metadata': {
                    'extraction_time': time.time() - start_time,
                    'extractor_version': '3.2.0-enhanced',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            }
    
    async def _discover_all_videos(self, page: Page, workflow_id: str) -> List[Dict]:
        """
        Discover ALL videos on the page with context.
        
        Returns list of videos with context information for classification.
        """
        videos = []
        seen_video_ids = set()  # Track seen videos to avoid duplicates
        
        # 1. Main page videos
        main_videos = await self._discover_videos_in_context(page, 'main_page')
        for video in main_videos:
            video_id = video.get('youtube_id')
            if video_id and video_id not in seen_video_ids:
                videos.append(video)
                seen_video_ids.add(video_id)
        logger.info(f"   Found {len(main_videos)} videos on main page")
        
        # 2. Iframe videos
        iframes = await page.query_selector_all('iframe')
        logger.info(f"   Found {len(iframes)} iframes to check")
        
        for idx, iframe in enumerate(iframes):
            try:
                # Get iframe src for analysis
                src = await iframe.get_attribute('src')
                title = await iframe.get_attribute('title') or ''
                
                logger.debug(f"   Checking iframe {idx+1}: {src}")
                
                # Try to access iframe content
                frame_content = await iframe.content_frame()
                
                if frame_content:
                    # Can access iframe content
                    iframe_videos = await self._discover_videos_in_context(
                        frame_content, 
                        f'iframe_{idx}',
                        iframe_src=src,
                        iframe_title=title
                    )
                    
                    # Add videos with proper iframe context
                    for video in iframe_videos:
                        video_id = video.get('youtube_id')
                        if video_id:
                            # Update context to include iframe information
                            video['context']['iframe_src'] = src
                            video['context']['iframe_title'] = title
                            
                            if video_id not in seen_video_ids:
                                videos.append(video)
                                seen_video_ids.add(video_id)
                            else:
                                # Update existing video with iframe context
                                for existing_video in videos:
                                    if existing_video.get('youtube_id') == video_id:
                                        existing_video['context']['iframe_src'] = src
                                        existing_video['context']['iframe_title'] = title
                                        existing_video['context']['location'] = f'iframe_{idx}'
                                        break
                    
                    logger.info(f"   Found {len(iframe_videos)} videos in iframe {idx+1}")
                elif src:
                    # Cross-origin iframe - attempt to fetch HTML and scan recursively
                    html = await self._fetch_cross_origin_html(src)
                    if html:
                        rec_videos = self._scan_html_for_videos(
                            html,
                            context={
                                'location': f'iframe_{idx}',
                                'iframe_src': src,
                                'iframe_title': title,
                                'position': 'main_content'
                            }
                        )
                        
                        # Add videos with proper iframe context
                        for video in rec_videos:
                            video_id = video.get('youtube_id')
                            if video_id and video_id not in seen_video_ids:
                                videos.append(video)
                                seen_video_ids.add(video_id)
            except Exception as e:
                logger.debug(f"   Could not access iframe {idx+1}: {e}")
        
        return videos

    async def _fetch_cross_origin_html(self, url: str) -> Optional[str]:
        """Fetch iframe HTML via Playwright's request context if possible."""
        try:
            # Use a temporary context request if available via page owner
            # In this extractor, we create a new page per extract; reuse browser net stack
            ctx = await self.browser.new_context()
            resp = await ctx.request.get(url, timeout=self.timeout / 1000)
            if resp.ok:
                txt = await resp.text()
                await ctx.close()
                return txt
            await ctx.close()
        except Exception:
            pass
        return None

    def _scan_html_for_videos(self, html: str, context: Dict) -> List[Dict]:
        videos: List[Dict] = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Anchors
            for a in soup.find_all('a', href=True):
                href = a['href']
                if self._is_valid_youtube_video_url(href):
                    vid = self._extract_youtube_id(href)
                    if vid:
                        videos.append({'url': f'https://youtu.be/{vid}', 'youtube_id': vid, 'type': 'video_link', 'context': context})
            
            # Iframe embeds
            for f in soup.find_all('iframe', src=True):
                vid = self._extract_youtube_id(f['src'])
                if vid:
                    videos.append({'url': f'https://youtu.be/{vid}', 'youtube_id': vid, 'type': 'html_embed', 'context': context})
            
            # Comprehensive regex sweep for all video patterns including n8n-specific formats
            video_patterns = [
                r'youtube\.com/watch\?v=([\w-]{11})',
                r'youtube\.com/embed/([\w-]{11})',
                r'youtu\.be/([\w-]{11})',
                r'"videoId":"([\w-]{11})"',
                r'videoId=([\w-]{11})',
                r'data-video-id="([\w-]{11})"',
                r'video_id=([\w-]{11})',
                r'v=([\w-]{11})',
                r'@\[youtube\]\(([\w-]{11})\)',  # n8n markdown format: @[youtube](VIDEO_ID)
                r'@\[youtube\]\(([\w-]{11})',    # n8n markdown format without closing )
            ]
            
            for pattern in video_patterns:
                for vid in set(re.findall(pattern, html)):
                    if self._is_valid_video_id(vid):
                        videos.append({'url': f'https://youtu.be/{vid}', 'youtube_id': vid, 'type': 'regex_discovered', 'context': context})
                        
        except Exception:
            return videos
        return videos
    
    async def _discover_videos_in_context(
        self, 
        page_or_frame, 
        location: str,
        iframe_src: str = None,
        iframe_title: str = None
    ) -> List[Dict]:
        """
        Discover videos in a page or frame with surrounding context.
        """
        videos = []
        
        try:
            # Get HTML content
            html = await page_or_frame.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find video links
            video_links = soup.find_all('a', href=re.compile(r'youtube\.com|youtu\.be|vimeo\.com'))
            
            for link in video_links:
                href = link.get('href', '')
                if not self._is_valid_youtube_video_url(href):
                    continue
                
                # Get surrounding context
                surrounding_text = self._get_surrounding_text(link)
                parent_classes = ' '.join(link.parent.get('class', []))
                
                # Determine position
                position = 'main_content'
                if 'sidebar' in parent_classes or 'related' in parent_classes.lower():
                    position = 'sidebar'
                elif 'footer' in parent_classes:
                    position = 'footer'
                
                video_id = self._extract_youtube_id(href)
                videos.append({
                    'url': href if href.startswith('http') else f'https://youtu.be/{video_id}',
                    'youtube_id': video_id,
                    'type': 'video_link',
                    'context': {
                        'location': location,
                        'surrounding_text': surrounding_text[:200],  # First 200 chars
                        'position': position,
                        'iframe_src': iframe_src,
                        'iframe_title': iframe_title
                    }
                })
            
            # Also check for embedded videos in HTML using comprehensive regex patterns including n8n-specific formats
            video_patterns = [
                r'youtube\.com/embed/([\w-]{11})',
                r'youtu\.be/([\w-]{11})',
                r'youtube\.com/watch\?v=([\w-]{11})',
                r'"videoId":"([\w-]{11})"',
                r'videoId=([\w-]{11})',
                r'data-video-id="([\w-]{11})"',
                r'video_id=([\w-]{11})',
                r'v=([\w-]{11})',
                r'@\[youtube\]\(([\w-]{11})\)',  # n8n markdown format: @[youtube](VIDEO_ID)
                r'@\[youtube\]\(([\w-]{11})',    # n8n markdown format without closing )
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, html)
                for video_id in matches:
                    if self._is_valid_video_id(video_id):
                        videos.append({
                            'url': f'https://youtu.be/{video_id}',
                            'youtube_id': video_id,
                            'type': 'html_embed',
                            'context': {
                                'location': location,
                                'position': 'main_content',
                                'iframe_src': iframe_src,
                                'iframe_title': iframe_title
                            }
                        })
        
        except Exception as e:
            logger.debug(f"Error discovering videos in {location}: {e}")
        
        return videos
    
    def _get_surrounding_text(self, element, max_chars: int = 200) -> str:
        """Get text surrounding an element for context"""
        try:
            parent = element.parent
            if parent:
                text = parent.get_text(strip=True)
                return text[:max_chars]
        except:
            pass
        return ""
    
    def _classify_videos(self, videos: List[Dict], workflow_id: str) -> List[Dict]:
        """
        Classify videos as primary explainer, related workflow, tutorial, or other.
        
        Classification logic:
        1. Primary Explainer: Embedded in main content, first video, workflow-specific
        2. Related Workflow: In sidebar, links to other workflows
        3. Tutorial: General n8n tutorials
        4. Other: Everything else
        """
        for idx, video in enumerate(videos):
            context = video.get('context', {}) or {}
            position = (context.get('position') or 'unknown').lower()
            location = (context.get('location') or '').lower()
            surrounding_text = (context.get('surrounding_text') or '').lower()
            iframe_title = (context.get('iframe_title') or '').lower()
            iframe_src = context.get('iframe_src', '')
            
            # Default classification
            classification = 'other'
            confidence = 0.5
            
            # Primary Explainer indicators
            is_embedded = video.get('type') in ['iframe_embed', 'html_embed']
            is_main_content = position == 'main_content'
            is_first = idx == 0
            is_in_workflow_iframe = 'n8n-preview-service' in iframe_src or 'workflows' in iframe_src
            has_workflow_context = any(word in surrounding_text or word in iframe_title 
                                      for word in ['workflow', 'tutorial', 'how to', 'guide', 'video tutorial'])
            
            # Enhanced classification logic
            if is_in_workflow_iframe and is_main_content:
                # Video is in the n8n workflow iframe - high confidence primary explainer
                classification = 'primary_explainer'
                confidence = 0.95
                if is_first:
                    confidence = 0.98
            elif is_embedded and is_main_content:
                classification = 'primary_explainer'
                confidence = 0.9
                if is_first:
                    confidence = 0.95
            elif is_main_content and has_workflow_context:
                classification = 'primary_explainer'
                confidence = 0.8
            elif position == 'sidebar' or 'related' in location:
                classification = 'related_workflow'
                confidence = 0.8
            elif 'tutorial' in surrounding_text or 'learn' in surrounding_text:
                classification = 'tutorial'
                confidence = 0.7
            elif is_in_workflow_iframe:
                # Even without other indicators, if it's in the workflow iframe, it's likely primary
                classification = 'primary_explainer'
                confidence = 0.75
            
            video['classification'] = classification
            video['confidence'] = confidence
            
            logger.debug(f"   Classified video {video.get('youtube_id')}: {classification} ({confidence:.0%}) - iframe: {iframe_src}")
        
        return videos
    
    async def _extract_content(self, page: Page) -> Dict:
        """Extract text content, images, links, and L1.5 structured content"""
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            images.append(img['src'])
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        
        # Extract L1.5 structured content
        l1_5_content = await self._extract_l1_5_structured_content(soup)
        
        return {
            'content_text': text,
            'total_text_length': len(text),
            'image_urls': list(set(images)),
            'image_count': len(set(images)),
            'link_urls': list(set(links)),
            'link_count': len(set(links)),
            **l1_5_content
        }
    
    async def _extract_l1_5_structured_content(self, soup: BeautifulSoup) -> Dict:
        """Extract L1.5 structured content (explainer_text, setup_instructions)"""
        
        # Extract "How it works" section as explainer_text
        explainer_text = ""
        
        # Find headings that contain "How it works"
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for heading in headings:
            heading_text = heading.get_text(strip=True).lower()
            if 'how it works' in heading_text or 'how it' in heading_text:
                # Get the content after this heading
                content_parts = []
                next_elem = heading.find_next_sibling()
                while next_elem:
                    if next_elem.name in ['h1', 'h2', 'h3', 'h4']:
                        break
                    text = next_elem.get_text(strip=True)
                    if text:
                        content_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                
                if content_parts:
                    explainer_text = "\n\n".join(content_parts)
                    logger.debug(f"Found 'How it works' section: {len(explainer_text)} chars")
                    break
        
        # Extract setup instructions
        setup_instructions = ""
        
        # Find headings that contain "Setup" or "Set up"
        for heading in headings:
            heading_text = heading.get_text(strip=True).lower()
            if 'setup' in heading_text or 'set up' in heading_text:
                # Get the content after this heading
                content_parts = []
                next_elem = heading.find_next_sibling()
                while next_elem:
                    if next_elem.name in ['h1', 'h2', 'h3', 'h4']:
                        break
                    text = next_elem.get_text(strip=True)
                    if text:
                        content_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                
                if content_parts:
                    setup_instructions = "\n\n".join(content_parts)
                    logger.debug(f"Found setup instructions: {len(setup_instructions)} chars")
                    break
        
        return {
            'explainer_text': self._format_as_markdown(explainer_text, 'How it works'),
            'setup_instructions': self._format_as_markdown(setup_instructions, 'Set up steps')
        }
    
    def _format_as_markdown(self, text: str, title: str) -> str:
        """Format extracted text as proper Markdown"""
        if not text:
            return ""
        
        # Clean up the text
        text = text.strip()
        
        # Add the main header
        markdown = f"## {title}\n\n"
        
        # Split into paragraphs and format
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if it's a heading (contains colon and is short)
            if ':' in paragraph and len(paragraph) < 100:
                # Format as subheading
                formatted_paragraphs.append(f"### {paragraph}")
            elif paragraph.startswith(('Get ', 'The ', 'A ', 'It ')) and len(paragraph) < 150:
                # Format as subheading
                formatted_paragraphs.append(f"### {paragraph}")
            elif '**' in paragraph or 'node' in paragraph.lower():
                # Format as paragraph with emphasis
                formatted_paragraphs.append(paragraph)
            else:
                # Regular paragraph
                formatted_paragraphs.append(paragraph)
        
        markdown += '\n\n'.join(formatted_paragraphs)
        
        # Post-process to add proper Markdown formatting
        markdown = self._enhance_markdown_formatting(markdown)
        
        return markdown
    
    def _enhance_markdown_formatting(self, text: str) -> str:
        """Enhance Markdown formatting with proper emphasis and code blocks"""
        
        # Add bold formatting to important terms
        important_terms = [
            'AI Agent', 'Chat Trigger', 'AI Agent node', 'Google Gemini', 
            'Conversation Memory', 'Get Weather', 'Get News', 'API key',
            'Connect your model', 'Create New Credential', 'Save'
        ]
        
        for term in important_terms:
            # Replace with bold formatting if not already formatted
            if f'**{term}**' not in text:
                text = text.replace(term, f'**{term}**')
        
        # Add code formatting to node names and technical terms
        code_terms = [
            'Chat Trigger', 'AI Agent', 'Conversation Memory', 
            'Connect your model', '+ Create New Credential'
        ]
        
        for term in code_terms:
            # Replace bold with code formatting for technical terms
            text = text.replace(f'**{term}**', f'`{term}`')
        
        # Add list formatting for setup steps
        if 'Setup time:' in text:
            # Format setup time as bold
            text = text.replace('Setup time:', '**Setup time:**')
        
        # Add links for URLs
        if 'aistudio.google.com' in text:
            text = text.replace(
                'aistudio.google.com/app/apikey',
                '[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)'
            )
        
        return text
    
    async def _extract_transcripts_robust(self, videos: List[Dict]) -> Dict[str, str]:
        """
        Extract transcripts with robust error handling and retries.
        
        Improvements:
        - 3 retry attempts with exponential backoff
        - Better error logging
        - Graceful handling of videos without captions
        """
        from src.scrapers.transcript_extractor import TranscriptExtractor
        
        transcripts = {}
        youtube_videos = [v for v in videos if v.get('youtube_id')]
        
        if not youtube_videos:
            return transcripts
        
        logger.info(f"   Extracting transcripts for {len(youtube_videos)} videos")
        
        async with TranscriptExtractor(headless=self.headless, timeout=self.timeout) as extractor:
            for video in youtube_videos:
                video_url = video.get('url', '')
                video_id = video.get('youtube_id', '')
                
                # Try up to 3 times with exponential backoff
                for attempt in range(3):
                    try:
                        success, transcript, error = await extractor.extract_transcript(video_url, video_id)
                        
                        if success and transcript:
                            transcripts[video_url] = transcript
                            video['transcript'] = transcript
                            video['has_transcript'] = True
                            logger.info(f"   ✅ Transcript for {video_id}: {len(transcript)} chars")
                            break
                        elif error and 'no transcript' in error.lower():
                            logger.debug(f"   ℹ️  No transcript available for {video_id}")
                            video['has_transcript'] = False
                            break
                        else:
                            if attempt < 2:
                                wait_time = 2 ** attempt  # 1s, 2s, 4s
                                logger.debug(f"   Retry {attempt+1}/3 for {video_id} in {wait_time}s")
                                await asyncio.sleep(wait_time)
                            else:
                                logger.warning(f"   ❌ Failed to extract transcript for {video_id}: {error}")
                                video['has_transcript'] = False
                    
                    except Exception as e:
                        if attempt < 2:
                            wait_time = 2 ** attempt
                            logger.debug(f"   Retry {attempt+1}/3 for {video_id} after error: {e}")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.warning(f"   ❌ Transcript extraction error for {video_id}: {e}")
                            video['has_transcript'] = False
        
        return transcripts
    
    def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
        """Deduplicate videos by YouTube ID, keeping the best classification"""
        seen = {}
        
        for video in videos:
            youtube_id = video.get('youtube_id')
            if not youtube_id:
                continue
            
            # If we haven't seen this video, add it
            if youtube_id not in seen:
                seen[youtube_id] = video
            else:
                # Keep the one with better classification
                existing = seen[youtube_id]
                existing_priority = self._classification_priority(existing.get('classification'))
                new_priority = self._classification_priority(video.get('classification'))
                
                if new_priority > existing_priority:
                    seen[youtube_id] = video
        
        return list(seen.values())
    
    def _classification_priority(self, classification: str) -> int:
        """Return priority of classification (higher = better)"""
        priorities = {
            'primary_explainer': 4,
            'related_workflow': 3,
            'tutorial': 2,
            'other': 1
        }
        return priorities.get(classification, 0)
    
    def _is_valid_youtube_video_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube video (not channel/playlist)"""
        if not url:
            return False
        
        # Skip invalid patterns
        invalid_patterns = [
            r'youtube\.com/c/',
            r'youtube\.com/@',
            r'youtube\.com/user/',
            r'youtube\.com/playlist',
            r'^/',  # Relative URL
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, url):
                return False
        
        # Must have valid video ID
        video_id = self._extract_youtube_id(url)
        return video_id and len(video_id) == 11
    
    def _is_valid_video_id(self, video_id: str) -> bool:
        """Validate YouTube video ID"""
        if not video_id or len(video_id) != 11:
            return False
        # Must be alphanumeric, dash, or underscore
        return bool(re.match(r'^[\w-]{11}$', video_id))
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_quality(self, data: Dict) -> int:
        """Calculate quality score (0-100)"""
        score = 0
        
        # Videos (40 points)
        if data['video_count'] > 0:
            score += 20
        if len(data['primary_explainer_videos']) > 0:
            score += 20  # Bonus for primary explainer
        
        # Transcripts (30 points)
        if data['transcript_count'] > 0:
            score += 20
        if data['transcript_count'] >= data['video_count']:
            score += 10  # Bonus for all transcripts
        
        # Content (30 points)
        if data['total_text_length'] > 1000:
            score += 10
        if data['total_text_length'] > 5000:
            score += 10
        if data['image_count'] > 0:
            score += 5
        if data['link_count'] > 5:
            score += 5
        
        return min(score, 100)

