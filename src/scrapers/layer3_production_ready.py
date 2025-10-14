"""
Layer 3 Production-Ready: Fast & Reliable

Simplified, optimized version that focuses on:
- Video URL extraction & storage
- Video deduplication  
- Transcript extraction
- Complete iframe content
- Fast execution (< 30s per workflow)
- Reliable database save

Author: Developer-2 (Dev2)
Task: SCRAPE-010
Date: October 14, 2025
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
from loguru import logger


class ProductionLayer3Extractor:
    """
    Production-ready Layer 3 extractor.
    
    Optimized for:
    - Speed: <30s per workflow
    - Reliability: Robust error handling
    - Completeness: All video URLs, transcripts, content
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
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
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("Production Layer 3 initialized")
        
    async def cleanup(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Production Layer 3 cleaned up")
    
    async def extract(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Extract comprehensive Layer 3 data - FAST & RELIABLE.
        
        Two-phase approach:
        1. Playwright: Navigate iframes, discover videos, get HTML
        2. BeautifulSoup: Parse HTML, extract all content
        """
        start_time = time.time()
        
        try:
            page = await self.browser.new_page()
            await page.goto(url, timeout=self.timeout)
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            await page.wait_for_timeout(2000)
            
            logger.info(f"Extracting Layer 3 for {workflow_id}")
            
            # Phase 1: Playwright - Get HTML and discover videos
            videos_raw = []
            all_html = []
            iframe_sources = []
            
            # Get main page HTML
            main_html = await page.content()
            all_html.append(('main_page', main_html))
            
            # Navigate into iframes
            iframes = await page.query_selector_all('iframe')
            for iframe in iframes:
                try:
                    src = await iframe.get_attribute('src')
                    frame = await iframe.content_frame()
                    
                    if frame:
                        # Get iframe HTML
                        iframe_html = await frame.content()
                        all_html.append((src, iframe_html))
                        iframe_sources.append(src)
                        
                        # Discover videos in iframe
                        iframe_videos = await self._discover_videos_playwright(frame)
                        videos_raw.extend(iframe_videos)
                        
                except Exception as e:
                    logger.warning(f"Error accessing iframe {src}: {e}")
            
            # Discover videos on main page
            main_videos = await self._discover_videos_playwright(page)
            videos_raw.extend(main_videos)
            
            await page.close()
            
            # Phase 2: BeautifulSoup - Parse HTML and extract content
            all_text = []
            all_links = []
            all_images = []
            
            for source, html in all_html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract text
                text = soup.get_text(separator='\n', strip=True)
                all_text.append(text)
                
                # Extract links
                for link in soup.find_all('a', href=True):
                    all_links.append(link['href'])
                
                # Extract images
                for img in soup.find_all('img', src=True):
                    all_images.append(img['src'])
                
                # Extract videos from HTML (BeautifulSoup)
                bs_videos = self._discover_videos_beautifulsoup(soup)
                videos_raw.extend(bs_videos)
            
            # Deduplicate videos
            videos_unique = self._deduplicate_videos(videos_raw)
            video_urls = [v.get('url', v.get('src', '')) for v in videos_unique if v.get('url') or v.get('src')]
            
            # Extract transcripts if enabled
            transcripts = {}
            if self.extract_transcripts:
                transcripts = await self._extract_transcripts(videos_unique)
            
            # Compile results
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'url': url,
                'data': {
                    # Videos
                    'videos': videos_unique,
                    'video_urls': video_urls,
                    'video_count': len(videos_unique),
                    'has_videos': len(videos_unique) > 0,
                    
                    # Transcripts
                    'transcripts': transcripts,
                    'transcript_count': len(transcripts),
                    'has_transcripts': len(transcripts) > 0,
                    
                    # Content
                    'content_text': '\n\n'.join(all_text),
                    'total_text_length': sum(len(t) for t in all_text),
                    
                    # Media
                    'image_urls': list(set(all_images)),
                    'image_count': len(set(all_images)),
                    'link_urls': list(set(all_links)),
                    'link_count': len(set(all_links)),
                    
                    # Iframes
                    'iframe_sources': iframe_sources,
                    'iframe_count': len(iframe_sources),
                    'has_iframes': len(iframe_sources) > 0,
                    
                    # Stats
                    'deduplication_stats': {
                        'raw_count': len(videos_raw),
                        'unique_count': len(videos_unique),
                        'duplicates_removed': len(videos_raw) - len(videos_unique)
                    }
                },
                'metadata': {
                    'extraction_time': time.time() - start_time,
                    'extractor_version': '3.1.0-production',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            }
            
            # Calculate quality score
            result['quality_score'] = self._calculate_quality(result['data'])
            
            logger.success(f"Layer 3 extraction complete for {workflow_id}: "
                          f"{result['data']['video_count']} videos, "
                          f"{result['data']['transcript_count']} transcripts, "
                          f"{result['data']['total_text_length']:,} chars, "
                          f"Q:{result['quality_score']}/100")
            
            return result
            
        except Exception as e:
            logger.error(f"Layer 3 extraction failed for {workflow_id}: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'url': url,
                'error': str(e),
                'metadata': {
                    'extraction_time': time.time() - start_time
                }
            }
    
    async def _discover_videos_playwright(self, page_or_frame) -> List[Dict]:
        """Discover videos using Playwright"""
        videos = []
        
        try:
            # YouTube/video links
            links = await page_or_frame.query_selector_all('a[href*="youtube"], a[href*="youtu.be"], a[href*="vimeo"]')
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if href:
                        videos.append({'type': 'video_link', 'url': href})
                except:
                    pass
        except:
            pass
        
        return videos
    
    def _discover_videos_beautifulsoup(self, soup: BeautifulSoup) -> List[Dict]:
        """Discover videos using BeautifulSoup (regex patterns)"""
        videos = []
        
        # Get all page content
        page_text = str(soup)
        
        # YouTube patterns
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
            r'https?://(?:www\.)?youtube\.com/embed/([\w-]+)',
            r'https?://youtu\.be/([\w-]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                videos.append({
                    'type': 'regex_discovered',
                    'url': f'https://youtu.be/{match}',
                    'youtube_id': match
                })
        
        return videos
    
    def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
        """Deduplicate videos by YouTube ID or URL"""
        seen = set()
        unique = []
        
        for video in videos:
            # Get identifier
            url = video.get('url', video.get('src', ''))
            if not url:
                continue
            
            # Extract YouTube ID
            youtube_id = self._extract_youtube_id(url)
            identifier = youtube_id if youtube_id else url.lower().strip()
            
            if identifier not in seen:
                seen.add(identifier)
                if youtube_id:
                    video['youtube_id'] = youtube_id
                unique.append(video)
        
        return unique
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID"""
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
    
    async def _extract_transcripts(self, videos: List[Dict]) -> Dict[str, str]:
        """Extract transcripts for YouTube videos"""
        from src.scrapers.transcript_extractor import TranscriptExtractor
        
        transcripts = {}
        youtube_videos = [v for v in videos if v.get('youtube_id')]
        
        if not youtube_videos:
            return transcripts
        
        logger.info(f"Extracting {len(youtube_videos)} transcripts")
        
        async with TranscriptExtractor(headless=self.headless) as extractor:
            for video in youtube_videos:
                video_url = video.get('url', '')
                video_id = video.get('youtube_id', '')
                
                try:
                    success, transcript, error = await extractor.extract_transcript(video_url, video_id)
                    
                    if success and transcript:
                        transcripts[video_url] = transcript
                        video['transcript'] = transcript
                        logger.info(f"Transcript extracted for {video_id} ({len(transcript)} chars)")
                    
                except Exception as e:
                    logger.warning(f"Transcript extraction failed for {video_id}: {e}")
        
        return transcripts
    
    def _calculate_quality(self, data: Dict) -> int:
        """Calculate quality score"""
        score = 0
        
        # Videos (40 points)
        if data['video_count'] > 0:
            score += 30
        if data['video_count'] > 1:
            score += 10
        
        # Transcripts (20 points)
        if data['transcript_count'] > 0:
            score += 20
        
        # Content (30 points)
        text_len = data['total_text_length']
        if text_len > 5000:
            score += 30
        elif text_len > 1000:
            score += 20
        elif text_len > 100:
            score += 10
        
        # Media (10 points)
        if data['image_count'] > 0:
            score += 5
        if data['link_count'] > 0:
            score += 5
        
        return min(score, 100)

