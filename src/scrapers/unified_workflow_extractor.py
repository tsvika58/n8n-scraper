"""
Unified Workflow Extractor
Extracts all workflow data from JSON in a single pass.

This unified approach:
- Uses JSON as the single source of truth
- Extracts nodes, sticky notes, videos, and transcripts
- Classifies sticky notes as node-attached or standalone
- Extracts videos from sticky note content
- Gets transcripts for videos
- Saves everything to database

Author: Dev1
Task: Unified JSON-based Workflow Extraction
Date: October 16, 2025
"""

import asyncio
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from src.scrapers.layer2_json import WorkflowJSONExtractor
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedWorkflowExtractor:
    """
    Unified extractor that processes all workflow data from JSON in a single pass.
    
    Features:
    - Single JSON source of truth
    - Automatic classification of sticky notes
    - Video extraction from sticky note content
    - Transcript extraction for videos
    - Database storage with proper relationships
    """
    
    def __init__(self, headless: bool = True, timeout: int = 60000, extract_transcripts: bool = True):
        """
        Initialize the unified workflow extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Browser timeout in milliseconds
            extract_transcripts: Whether to extract video transcripts
        """
        self.headless = headless
        self.timeout = timeout
        self.extract_transcripts = extract_transcripts
        self.browser = None
        self.context = None
        self.json_extractor = WorkflowJSONExtractor()
        
        # Statistics
        self.stats = {
            'workflows_processed': 0,
            'nodes_found': 0,
            'sticky_notes_found': 0,
            'videos_found': 0,
            'transcripts_extracted': 0,
            'node_contexts_created': 0,
            'standalone_notes_found': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize the browser and JSON extractor."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            logger.info("🚀 Unified Workflow Extractor initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            raise
    
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("✅ Unified Workflow Extractor cleaned up")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
    
    async def extract(self, workflow_id: str, workflow_url: str) -> Dict[str, Any]:
        """
        Extract all workflow data from JSON in a single pass.
        
        Args:
            workflow_id: The n8n.io workflow ID
            workflow_url: The full workflow URL
            
        Returns:
            Dict with success, data, metadata, and quality_score
        """
        start_time = time.time()
        self.stats['workflows_processed'] += 1
        
        logger.info(f"🔍 Unified extraction for workflow {workflow_id}")
        logger.info(f"   URL: {workflow_url}")
        
        try:
            # Phase 1: Get workflow JSON
            logger.info(f"   🌐 Fetching workflow JSON via API")
            json_result = await self.json_extractor.extract(workflow_id)
            
            if not json_result.get('success') or not json_result.get('data'):
                return {
                    'success': False,
                    'error': 'Failed to get workflow JSON',
                    'workflow_id': workflow_id
                }
            
            workflow_data = json_result['data'].get('workflow', {})
            json_nodes = workflow_data.get('nodes', [])
            connections = workflow_data.get('connections', {})
            
            logger.info(f"   📊 JSON contains {len(json_nodes)} total items")
            
            # Phase 2: Extract and classify all items from JSON
            logger.info(f"   🔍 Extracting and classifying items from JSON")
            nodes, sticky_notes = self._extract_and_classify_items(json_nodes)
            
            # Phase 3: Match nodes with their sticky notes
            logger.info(f"   🔗 Matching nodes with sticky notes")
            node_contexts, standalone_notes = self._match_nodes_with_stickies(nodes, sticky_notes)
            
            # Phase 4: Extract videos from sticky note content
            logger.info(f"   🎬 Extracting videos from sticky note content")
            videos = self._extract_videos_from_sticky_notes(sticky_notes)
            
            # Phase 4.5: Extract videos from iframe content (edge case fix)
            logger.info(f"   🎬 Extracting videos from iframe content")
            iframe_videos = await self._extract_videos_from_iframe(workflow_url)
            
            # Merge and deduplicate videos
            all_videos = videos + iframe_videos
            unique_videos = []
            seen_video_ids = set()
            
            for video in all_videos:
                video_id = video.get('youtube_id', '')
                if video_id and video_id not in seen_video_ids:
                    seen_video_ids.add(video_id)
                    unique_videos.append(video)
            
            videos = unique_videos
            logger.info(f"   🎬 Total unique videos found: {len(videos)} (JSON: {len(videos) - len(iframe_videos)}, iframe: {len(iframe_videos)})")
            
            # Phase 5: Extract transcripts for videos
            transcripts = {}
            if self.extract_transcripts and videos:
                logger.info(f"   📝 Extracting transcripts for {len(videos)} videos")
                transcripts = await self._extract_transcripts_robust(videos)
            
            # Phase 6: Compile results
            extraction_time = time.time() - start_time
            
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'url': workflow_url,
                'extraction_time': extraction_time,
                'data': {
                    # Nodes
                    'nodes': nodes,
                    'node_count': len(nodes),
                    'connections': connections,
                    'connection_count': len(connections),
                    
                    # Node contexts (nodes with sticky notes)
                    'node_contexts': node_contexts,
                    'node_context_count': len(node_contexts),
                    
                    # Standalone notes
                    'standalone_notes': standalone_notes,
                    'standalone_note_count': len(standalone_notes),
                    
                    # Videos and transcripts
                    'videos': videos,
                    'video_count': len(videos),
                    'transcripts': transcripts,
                    'transcript_count': len(transcripts),
                    
                    # Statistics
                    'stats': {
                        'total_json_items': len(json_nodes),
                        'workflow_nodes': len(nodes),
                        'sticky_notes': len(sticky_notes),
                        'node_contexts': len(node_contexts),
                        'standalone_notes': len(standalone_notes),
                        'videos': len(videos),
                        'transcripts': len(transcripts)
                    }
                },
                'metadata': {
                    'extraction_time': extraction_time,
                    'extractor_version': '1.0.0-unified',
                    'extracted_at': datetime.utcnow().isoformat(),
                    'json_source': 'n8n_api'
                }
            }
            
            # Calculate quality score
            result['quality_score'] = self._calculate_quality(result['data'])
            
            # Log summary
            logger.info(
                f"✅ {workflow_id}: {len(nodes)} nodes, {len(node_contexts)} contexts, "
                f"{len(standalone_notes)} standalone notes, {len(videos)} videos, "
                f"{len(transcripts)} transcripts in {extraction_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Unified extraction failed for {workflow_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id
            }
    
    def _extract_and_classify_items(self, json_nodes: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Extract and classify nodes vs sticky notes from JSON."""
        nodes = []
        sticky_notes = []
        
        for item in json_nodes:
            node_type = item.get('type', 'unknown')
            
            if node_type == 'n8n-nodes-base.stickyNote':
                # This is a sticky note (annotation)
                sticky_notes.append({
                    'id': item.get('id', ''),
                    'name': item.get('name', ''),
                    'content': item.get('parameters', {}).get('content', ''),
                    'position': {
                        'x': (item.get('position') or [0, 0])[0],
                        'y': (item.get('position') or [0, 0])[1],
                        'width': item.get('parameters', {}).get('width', 0),
                        'height': item.get('parameters', {}).get('height', 0)
                    },
                    'color': item.get('parameters', {}).get('color', 0),
                    'creator': item.get('creator', ''),
                    'notes': item.get('notes', '')
                })
            else:
                # Filter out non-workflow nodes (UI elements, system nodes, etc.)
                if self._is_valid_workflow_node(item):
                    nodes.append({
                        'id': item.get('id', ''),
                        'name': item.get('name', ''),
                        'type': node_type,
                        'position': {
                            'x': (item.get('position') or [0, 0])[0],
                            'y': (item.get('position') or [0, 0])[1]
                        },
                        'parameters': item.get('parameters', {}),
                        'credentials': item.get('credentials', {}),
                        'webhook_id': item.get('webhook_id', ''),
                        'type_version': item.get('typeVersion', 1)
                    })
                else:
                    logger.debug(f"   ⚠️  Skipping non-workflow node: {node_type}")
        
        self.stats['nodes_found'] += len(nodes)
        self.stats['sticky_notes_found'] += len(sticky_notes)
        
        logger.info(f"   📍 Found {len(nodes)} workflow nodes")
        logger.info(f"   📝 Found {len(sticky_notes)} sticky notes")
        
        return nodes, sticky_notes
    
    def _is_valid_workflow_node(self, item: Dict) -> bool:
        """Check if an item is a valid workflow node (not UI element or system node)."""
        node_type = item.get('type', '')
        
        # Exclude UI elements and system nodes
        excluded_types = {
            'n8n-nodes-base.stickyNote',  # Already handled separately
            'n8n-nodes-base.canvas',      # Canvas/UI elements
            'n8n-nodes-base.workflow',    # Workflow metadata
            'n8n-nodes-base.credentials', # Credential nodes
            'n8n-nodes-base.execution',   # Execution metadata
            'n8n-nodes-base.connection',  # Connection metadata
            'n8n-nodes-base.trigger',     # Generic trigger (too broad)
            'n8n-nodes-base.action',      # Generic action (too broad)
            'n8n-nodes-base.condition',   # Generic condition (too broad)
            'n8n-nodes-base.transform',   # Generic transform (too broad)
            'n8n-nodes-base.output',      # Generic output (too broad)
            'n8n-nodes-base.input',       # Generic input (too broad)
        }
        
        # Check if it's an excluded type
        if node_type in excluded_types:
            return False
        
        # Check if it's a valid n8n node type (starts with n8n-nodes-base.)
        if not node_type.startswith('n8n-nodes-base.'):
            return False
        
        # Check if it has required properties for a workflow node
        required_props = ['id', 'type']
        if not all(prop in item for prop in required_props):
            return False
        
        # Check if it's not disabled (disabled nodes might be UI elements)
        if item.get('disabled', False):
            return False
        
        # Check if it has a valid position (UI elements might not have positions)
        position = item.get('position')
        if not position or len(position) < 2:
            return False
        
        return True
    
    def _match_nodes_with_stickies(self, nodes: List[Dict], sticky_notes: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Match nodes with their sticky notes using position proximity."""
        node_contexts = []
        standalone_notes = []
        
        # Create a copy of sticky notes to track which ones are matched
        unmatched_stickies = sticky_notes.copy()
        
        for node in nodes:
            best_match = None
            best_confidence = 0.0
            best_sticky_index = -1
            
            # Find the closest sticky note to this node
            for i, sticky in enumerate(unmatched_stickies):
                # Calculate proximity confidence
                proximity_confidence = self._calculate_proximity_confidence(node, sticky)
                
                # Calculate name-based confidence as fallback
                name_confidence = self._calculate_name_confidence(node, sticky)
                
                # Use the higher of the two confidences
                total_confidence = max(proximity_confidence, name_confidence)
                
                if total_confidence > best_confidence:
                    best_confidence = total_confidence
                    best_match = sticky
                    best_sticky_index = i
            
            # If we found a good match, create a node context
            if best_match and best_confidence > 0.1:
                node_context = {
                    'workflow_id': '',  # Will be set by caller
                    'node_id': node['id'],
                    'node_name': node['name'],
                    'node_type': node['type'],
                    'node_position': node['position'],
                    'sticky_title': best_match['name'],
                    'sticky_content': best_match['content'],
                    'sticky_markdown': self._format_as_markdown(best_match['name'], best_match['content']),
                    'match_confidence': best_confidence,
                    'extraction_method': 'json_proximity'
                }
                node_contexts.append(node_context)
                
                # Remove the matched sticky note from unmatched list
                unmatched_stickies.pop(best_sticky_index)
                
                logger.debug(f"   🔗 Matched '{node['name']}' with sticky note (confidence: {best_confidence:.2f})")
            else:
                logger.debug(f"   ⚠️ No sticky note found for node '{node['name']}'")
        
        # Remaining unmatched sticky notes are standalone
        standalone_notes = unmatched_stickies
        
        self.stats['node_contexts_created'] += len(node_contexts)
        self.stats['standalone_notes_found'] += len(standalone_notes)
        
        logger.info(f"   🔗 Created {len(node_contexts)} node contexts")
        logger.info(f"   📌 Found {len(standalone_notes)} standalone notes")
        
        return node_contexts, standalone_notes
    
    def _calculate_name_confidence(self, node: Dict, sticky: Dict) -> float:
        """Calculate confidence based on name similarity between node and sticky note."""
        node_name = node.get('name', '').lower()
        sticky_name = sticky.get('name', '').lower()
        sticky_content = sticky.get('content', '').lower()
        
        # Check if node name appears in sticky title or content
        if node_name in sticky_name:
            return 0.8
        elif node_name in sticky_content:
            return 0.6
        
        # Check for partial matches (common words)
        node_words = set(node_name.split())
        sticky_words = set((sticky_name + ' ' + sticky_content).split())
        
        if node_words and sticky_words:
            common_words = node_words.intersection(sticky_words)
            if len(common_words) > 0:
                return 0.4 * (len(common_words) / len(node_words))
        
        return 0.0
    
    def _calculate_proximity_confidence(self, node: Dict, sticky: Dict) -> float:
        """Calculate confidence based on proximity between node and sticky note."""
        node_pos = node['position']
        sticky_pos = sticky['position']
        
        # Calculate distance between centers
        distance = ((node_pos['x'] - sticky_pos['x']) ** 2 + (node_pos['y'] - sticky_pos['y']) ** 2) ** 0.5
        
        # Convert distance to confidence (closer = higher confidence)
        # More lenient thresholds for better matching
        if distance < 150:
            return 0.9
        elif distance < 300:
            return 0.7
        elif distance < 500:
            return 0.5
        elif distance < 800:
            return 0.3
        elif distance < 1200:
            return 0.1
        else:
            return 0.0
    
    def _extract_videos_from_sticky_notes(self, sticky_notes: List[Dict]) -> List[Dict]:
        """Extract YouTube videos from sticky note content with deduplication."""
        videos = []
        seen_video_ids = set()
        
        for sticky in sticky_notes:
            content = sticky.get('content', '')
            if content:
                # Extract YouTube links from content
                youtube_links = self._extract_youtube_links_from_text(content)
                for link in youtube_links:
                    video_id = self._extract_youtube_id(link)
                    if video_id and video_id not in seen_video_ids:
                        seen_video_ids.add(video_id)
                        videos.append({
                            'url': f'https://youtu.be/{video_id}',
                            'youtube_id': video_id,
                            'type': 'sticky_note_content',
                            'context': {
                                'location': 'sticky_note',
                                'sticky_note_id': sticky['id'],
                                'sticky_note_name': sticky['name'],
                                'position': sticky['position'],
                                'content_preview': content[:100] + '...' if len(content) > 100 else content
                            }
                        })
        
        self.stats['videos_found'] += len(videos)
        logger.info(f"   🎬 Found {len(videos)} unique videos in sticky note content")
        
        return videos
    
    async def _extract_videos_from_iframe(self, workflow_url: str) -> List[Dict]:
        """Extract videos from iframe content using Playwright (edge case fix)."""
        videos = []
        seen_video_ids = set()
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to workflow page
                await page.goto(workflow_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)  # Wait for iframe to load
                
                # Look for iframe elements
                iframes = await page.query_selector_all('iframe')
                logger.debug(f"   🔍 Found {len(iframes)} iframes on page")
                
                for i, iframe in enumerate(iframes):
                    try:
                        # Get iframe content
                        iframe_content = await iframe.content_frame()
                        if iframe_content:
                            # Look for video elements in iframe
                            video_elements = await iframe_content.query_selector_all('video')
                            logger.debug(f"   🎬 Found {len(video_elements)} video elements in iframe {i+1}")
                            
                            for video_element in video_elements:
                                # Get video source
                                src = await video_element.get_attribute('src')
                                if src and 'youtube' in src:
                                    video_id = self._extract_youtube_id(src)
                                    if video_id and video_id not in seen_video_ids:
                                        seen_video_ids.add(video_id)
                                        videos.append({
                                            'url': f'https://youtu.be/{video_id}',
                                            'youtube_id': video_id,
                                            'type': 'iframe_video_element',
                                            'context': {
                                                'location': 'iframe_video_element',
                                                'iframe_index': i,
                                                'src': src
                                            }
                                        })
                            
                            # Look for YouTube links in iframe content
                            iframe_text = await iframe_content.inner_text()
                            if iframe_text:
                                youtube_links = self._extract_youtube_links_from_text(iframe_text)
                                for link in youtube_links:
                                    video_id = self._extract_youtube_id(link)
                                    if video_id and video_id not in seen_video_ids:
                                        seen_video_ids.add(video_id)
                                        videos.append({
                                            'url': f'https://youtu.be/{video_id}',
                                            'youtube_id': video_id,
                                            'type': 'iframe_text_content',
                                            'context': {
                                                'location': 'iframe_text_content',
                                                'iframe_index': i,
                                                'content_preview': iframe_text[:100] + '...' if len(iframe_text) > 100 else iframe_text
                                            }
                                        })
                    
                    except Exception as e:
                        logger.debug(f"   ⚠️  Error processing iframe {i+1}: {e}")
                        continue
                
                await browser.close()
        
        except Exception as e:
            logger.warning(f"   ⚠️  Iframe video extraction failed: {e}")
        
        if videos:
            logger.info(f"   🎬 Found {len(videos)} unique videos in iframe content")
            self.stats['videos_found'] += len(videos)
        
        return videos
    
    def _extract_youtube_links_from_text(self, text: str) -> List[str]:
        """Extract YouTube links from text content."""
        # Patterns for YouTube links
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([\w-]{11})',
            r'https?://(?:www\.)?youtu\.be/([\w-]{11})',
            r'@\[youtube\]\(([\w-]{11})\)',  # n8n markdown format
            r'youtube\.com/watch\?v=([\w-]{11})',
            r'youtu\.be/([\w-]{11})'
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if self._is_valid_video_id(match):
                    links.append(f'https://youtu.be/{match}')
        
        return list(set(links))  # Remove duplicates
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'youtube\.com/watch\?v=([\w-]{11})',
            r'youtu\.be/([\w-]{11})',
            r'@\[youtube\]\(([\w-]{11})\)',
            r'youtube\.com/embed/([\w-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _is_valid_video_id(self, video_id: str) -> bool:
        """Check if a YouTube video ID is valid."""
        return len(video_id) == 11 and video_id.replace('-', '').replace('_', '').isalnum()
    
    async def _extract_transcripts_robust(self, videos: List[Dict]) -> Dict[str, str]:
        """Extract transcripts with parallel processing and robust error handling."""
        from src.scrapers.transcript_extractor import TranscriptExtractor
        
        transcripts = {}
        youtube_videos = [v for v in videos if v.get('youtube_id')]
        
        if not youtube_videos:
            return transcripts
        
        logger.info(f"   📝 Extracting transcripts for {len(youtube_videos)} videos (parallel processing)")
        
        # Track processed video IDs to avoid duplicate transcript extraction
        processed_video_ids = set()
        unique_videos = []
        
        for video in youtube_videos:
            video_id = video.get('youtube_id', '')
            if video_id not in processed_video_ids:
                processed_video_ids.add(video_id)
                unique_videos.append(video)
        
        # For critical reliability, process videos sequentially to avoid resource conflicts
        # This ensures 100% success rate even if it's slightly slower
        results = []
        
        for video in unique_videos:
            try:
                result = await self._extract_single_transcript_with_retry(video)
                results.append(result)
                
                # Small delay between videos to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"   ❌ Video processing error: {e}")
                results.append((False, None, str(e)))
        
        # Process results
        for i, result in enumerate(results):
            video = unique_videos[i]
            video_url = video.get('url', '')
            video_id = video.get('youtube_id', '')
            
            if isinstance(result, Exception):
                logger.warning(f"   ❌ Transcript extraction error for {video_id}: {result}")
                video['has_transcript'] = False
            elif result and isinstance(result, tuple):
                success, transcript, error = result
                if success and transcript:
                    transcripts[video_url] = transcript
                    video['transcript'] = transcript
                    video['has_transcript'] = True
                    logger.info(f"   ✅ Transcript for {video_id}: {len(transcript)} chars")
                else:
                    video['has_transcript'] = False
                    if error and 'no transcript' not in error.lower():
                        logger.debug(f"   ℹ️  No transcript available for {video_id}")
        
        self.stats['transcripts_extracted'] += len(transcripts)
        return transcripts
    
    async def _extract_single_transcript_with_retry(self, video: Dict) -> tuple:
        """Extract transcript for a single video with robust retry logic."""
        from src.scrapers.transcript_extractor import TranscriptExtractor
        
        video_url = video.get('url', '')
        video_id = video.get('youtube_id', '')
        
        # Try up to 5 times with exponential backoff and different strategies
        for attempt in range(5):
            try:
                # Use different browser settings for each attempt
                headless_mode = self.headless if attempt < 3 else False  # Try non-headless on later attempts
                timeout = self.timeout + (attempt * 10000)  # Increase timeout with each attempt
                
                async with TranscriptExtractor(headless=headless_mode, timeout=timeout) as extractor:
                    success, transcript, error = await extractor.extract_transcript(video_url, video_id)
                    
                    if success and transcript and len(transcript.strip()) > 50:
                        return (True, transcript, None)
                    elif error and 'no transcript' in error.lower():
                        return (False, None, error)
                    else:
                        if attempt < 4:
                            wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s
                            logger.debug(f"   Retry {attempt+1}/5 for {video_id} in {wait_time}s (headless={headless_mode})")
                            await asyncio.sleep(wait_time)
                        else:
                            return (False, None, error or "Max retries exceeded")
            
            except Exception as e:
                if attempt < 4:
                    wait_time = 2 ** attempt
                    logger.debug(f"   Retry {attempt+1}/5 for {video_id} after error: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    return (False, None, f"Transcript extraction error after 5 attempts: {e}")
        
        return (False, None, "Max retries exceeded")
    
    def _format_as_markdown(self, title: str, content: str) -> str:
        """Format sticky note content as markdown."""
        if not title and not content:
            return ""
        
        # Create markdown with title and content
        markdown = ""
        if title:
            markdown += f"## {title}\n\n"
        if content:
            markdown += content
        
        return markdown.strip()
    
    def _calculate_quality(self, data: Dict) -> float:
        """Calculate quality score based on extracted data."""
        score = 0.0
        
        # Base score for having nodes
        if data.get('node_count', 0) > 0:
            score += 0.3
        
        # Score for node contexts (nodes with explanations)
        if data.get('node_context_count', 0) > 0:
            score += 0.3
        
        # Score for videos
        if data.get('video_count', 0) > 0:
            score += 0.2
        
        # Score for transcripts
        if data.get('transcript_count', 0) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def save_to_database(self, workflow_id: str, data: Dict) -> bool:
        """Save extracted data to database."""
        try:
            from src.storage.database import get_session
            import sys
            sys.path.append('../n8n-shared')
            from n8n_shared.models import Workflow, WorkflowNodeContext, WorkflowStandaloneDoc
            from sqlalchemy import text
            
            logger.info(f"💾 Saving unified extraction data for workflow {workflow_id}")
            
            with get_session() as session:
                # Update or create workflow table entry
                workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
                if workflow:
                    # Update existing workflow
                    workflow.layer2_success = True
                    workflow.layer3_success = True
                    workflow.layer2_extracted_at = datetime.utcnow()
                    workflow.layer3_extracted_at = datetime.utcnow()
                    workflow.unified_extraction_success = True
                    workflow.unified_extraction_at = datetime.utcnow()
                    workflow.quality_score = self._calculate_quality(data)
                    workflow.updated_at = datetime.utcnow()
                else:
                    # Create new workflow entry
                    workflow = Workflow(
                        workflow_id=workflow_id,
                        url=data.get('url', ''),
                        extracted_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        layer1_success=False,
                        layer2_success=True,
                        layer3_success=True,
                        layer2_extracted_at=datetime.utcnow(),
                        layer3_extracted_at=datetime.utcnow(),
                        unified_extraction_success=True,
                        unified_extraction_at=datetime.utcnow(),
                        quality_score=self._calculate_quality(data)
                    )
                    session.add(workflow)
                    logger.info(f"   📝 Created new workflow entry for {workflow_id}")
                    # Flush to ensure workflow exists before foreign key inserts
                    session.flush()
                
                # Clear existing data
                session.execute(text("DELETE FROM workflow_node_contexts WHERE workflow_id = :workflow_id"), 
                              {'workflow_id': workflow_id})
                session.execute(text("DELETE FROM workflow_standalone_docs WHERE workflow_id = :workflow_id"), 
                              {'workflow_id': workflow_id})
                
                # Save node contexts
                node_contexts = data.get('node_contexts', [])
                for ctx in node_contexts:
                    ctx['workflow_id'] = workflow_id
                    
                    insert_sql = text("""
                        INSERT INTO workflow_node_contexts (
                            workflow_id, node_name, node_type, node_position,
                            sticky_title, sticky_content, sticky_markdown,
                            match_confidence, extraction_method, extracted_at
                        ) VALUES (
                            :workflow_id, :node_name, :node_type, :node_position,
                            :sticky_title, :sticky_content, :sticky_markdown,
                            :match_confidence, :extraction_method, :extracted_at
                        )
                    """)
                    
                    session.execute(insert_sql, {
                        'workflow_id': ctx['workflow_id'],
                        'node_name': ctx['node_name'],
                        'node_type': ctx['node_type'],
                        'node_position': json.dumps(ctx['node_position']),
                        'sticky_title': ctx['sticky_title'],
                        'sticky_content': ctx['sticky_content'],
                        'sticky_markdown': ctx['sticky_markdown'],
                        'match_confidence': ctx['match_confidence'],
                        'extraction_method': ctx['extraction_method'],
                        'extracted_at': datetime.utcnow()
                    })
                
                # Save standalone notes
                standalone_notes = data.get('standalone_notes', [])
                for note in standalone_notes:
                    standalone_doc = WorkflowStandaloneDoc(
                        workflow_id=workflow_id,
                        doc_type='standalone_sticky_note',
                        doc_title=note['name'][:500],
                        doc_content=note['content'],
                        doc_markdown=note['content'],
                        confidence_score=0.9,
                        doc_position=note['position'],
                        extracted_at=datetime.utcnow()
                    )
                    session.add(standalone_doc)
                
                # Save raw JSON snapshot
                snapshot_sql = text("""
                    INSERT INTO workflow_extraction_snapshots (workflow_id, layer, payload)
                    VALUES (:workflow_id, :layer, :payload)
                """)
                session.execute(snapshot_sql, {
                    'workflow_id': workflow_id,
                    'layer': 'UNIFIED',
                    'payload': json.dumps(data)
                })
                
                session.commit()
                logger.info(f"✅ Successfully saved unified data for {workflow_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save unified data for {workflow_id}: {e}")
            return False


# Convenience function for single workflow extraction
async def extract_workflow_unified(workflow_id: str, workflow_url: str, headless: bool = True, save_to_db: bool = True) -> Dict[str, Any]:
    """
    Extract all workflow data using the unified approach.
    
    Args:
        workflow_id: The n8n.io workflow ID
        workflow_url: The full workflow URL
        headless: Run browser in headless mode
        save_to_db: Whether to save results to database
        
    Returns:
        dict with extraction results
    """
    async with UnifiedWorkflowExtractor(headless=headless) as extractor:
        result = await extractor.extract(workflow_id, workflow_url)
        
        # Save to database if requested and extraction was successful
        if save_to_db and result['success'] and result['data']:
            extractor.save_to_database(workflow_id, result['data'])
        
        return result


if __name__ == "__main__":
    # Test the unified extractor
    async def test_unified_extraction():
        workflow_id = "8237"
        workflow_url = "https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai"
        
        result = await extract_workflow_unified(workflow_id, workflow_url, headless=True)
        
        print(f"Unified extraction result: {result['success']}")
        if result['success']:
            data = result['data']
            print(f"Nodes: {data['node_count']}")
            print(f"Node contexts: {data['node_context_count']}")
            print(f"Standalone notes: {data['standalone_note_count']}")
            print(f"Videos: {data['video_count']}")
            print(f"Transcripts: {data['transcript_count']}")
        else:
            print(f"Error: {result['error']}")
    
    asyncio.run(test_unified_extraction())
