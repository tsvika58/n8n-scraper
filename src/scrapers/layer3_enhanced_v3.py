"""
Layer 3 Enhanced V3: Standalone Documentation Extractor
Extracts standalone documentation and section headers from n8n workflow pages.

This is a new version that focuses specifically on:
- Setup instructions and workflow notes
- Section headers and organizational text
- Standalone documentation not tied to specific nodes
- Content classification and confidence scoring

Author: Dev1
Task: Enhanced L2 L3 Node Context Extraction
Date: October 15, 2025
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


class StandaloneDocExtractor:
    """
    Extracts standalone documentation and section headers from n8n workflow pages.
    
    Features:
    - Setup instructions extraction
    - Section header detection
    - Workflow notes and documentation
    - Content classification and confidence scoring
    - Markdown formatting of extracted content
    """
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        """
        Initialize the standalone documentation extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None
        
        # Statistics tracking
        self.stats = {
            'workflows_processed': 0,
            'setup_instructions_found': 0,
            'section_headers_found': 0,
            'workflow_notes_found': 0,
            'videos_found': 0,
            'total_docs_extracted': 0,
            'extraction_errors': 0
        }
        
        logger.info("Standalone Documentation Extractor initialized")
    
    async def __aenter__(self):
        """Initialize browser for extraction."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        logger.info("Browser initialized for standalone documentation extraction")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser cleanup complete")
    
    async def extract_standalone_docs(self, workflow_id: str, workflow_url: str) -> Dict[str, Any]:
        """
        Extract standalone documentation from a workflow page.
        
        Args:
            workflow_id: The n8n.io workflow ID
            workflow_url: The full workflow URL
            
        Returns:
            dict with extraction results and standalone documents
        """
        start_time = datetime.now()
        self.stats['workflows_processed'] += 1
        
        logger.info(f"🔍 Extracting standalone docs for workflow {workflow_id}")
        logger.info(f"   URL: {workflow_url}")
        
        page = await self.context.new_page()
        
        try:
            # Navigate to workflow page
            await page.goto(workflow_url, wait_until='domcontentloaded', timeout=self.timeout)
            await asyncio.sleep(3)  # Wait for iframe to load
            
            # CRITICAL: L3 V3 must ONLY work within the workflow iframe
            # Find and access the workflow iframe
            workflow_frame = await self._find_workflow_iframe(page)
            if not workflow_frame:
                logger.warning(f"   ❌ Workflow iframe not found for {workflow_id}")
                return {
                    'success': False,
                    'error': 'Workflow iframe not found',
                    'workflow_id': workflow_id,
                    'standalone_docs': []
                }
            
            logger.info(f"   ✅ Found workflow iframe, extracting standalone docs...")
            
            # Extract setup instructions from iframe
            logger.info(f"   📋 Extracting setup instructions...")
            setup_instructions = await self._extract_setup_instructions(workflow_frame)
            self.stats['setup_instructions_found'] += len(setup_instructions)
            
            # Extract section headers from iframe
            logger.info(f"   📑 Extracting section headers...")
            section_headers = await self._extract_section_headers(workflow_frame)
            self.stats['section_headers_found'] += len(section_headers)
            
            # Extract workflow notes from iframe
            logger.info(f"   📝 Extracting workflow notes...")
            workflow_notes = await self._extract_workflow_notes(workflow_frame)
            self.stats['workflow_notes_found'] += len(workflow_notes)
            
            # Extract videos and transcribe them
            logger.info(f"   🎥 Extracting videos...")
            videos = await self._extract_videos(workflow_frame)
            self.stats['videos_found'] = len(videos)
            
            # Combine all documents
            all_docs = setup_instructions + section_headers + workflow_notes + videos
            self.stats['total_docs_extracted'] += len(all_docs)
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'url': workflow_url,
                'extraction_time': extraction_time,
                'standalone_docs': all_docs,
                'statistics': {
                    'setup_instructions': len(setup_instructions),
                    'section_headers': len(section_headers),
                    'workflow_notes': len(workflow_notes),
                    'total_docs': len(all_docs),
                    'extraction_time': extraction_time
                }
            }
            
            logger.info(f"   ✅ Extraction complete: {len(all_docs)} standalone docs found in {extraction_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.stats['extraction_errors'] += 1
            logger.error(f"   ❌ Extraction failed for {workflow_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id,
                'standalone_docs': []
            }
        finally:
            await page.close()
    
    async def _find_workflow_iframe(self, page: Page) -> Optional[Any]:
        """Find the workflow iframe on the page."""
        try:
            # Wait for iframe to load with multiple selectors
            iframe_selectors = [
                'iframe[src*="n8n-preview"]',
                'iframe[src*="demo"]',
                'iframe[src*="workflow"]',
                'iframe[src*="preview"]',
                'iframe'
            ]
            
            workflow_frame = None
            for selector in iframe_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    logger.info(f"   ✅ Found iframe with selector: {selector}")
                    break
                except:
                    continue
            
            # Get all frames and look for workflow iframe
            frames = page.frames
            logger.info(f"   📋 Found {len(frames)} total frames")
            
            for i, frame in enumerate(frames):
                frame_url = frame.url.lower()
                logger.info(f"   🔍 Frame {i}: {frame_url}")
                
                # Prioritize the actual demo iframe (n8n-preview-service)
                if 'n8n-preview-service' in frame_url and 'demo' in frame_url:
                    logger.info(f"   ✅ Found demo iframe: {frame.url}")
                    return frame
                
                # Check for other workflow-related keywords
                if any(keyword in frame_url for keyword in ['n8n-preview', 'demo', 'preview']):
                    logger.info(f"   ✅ Found workflow iframe: {frame.url}")
                    return frame
                
                # Also check if frame has workflow content
                try:
                    # Try to find workflow-specific elements in the frame
                    workflow_elements = await frame.query_selector_all('[data-node-name]')
                    if len(workflow_elements) > 0:
                        logger.info(f"   ✅ Found workflow iframe with {len(workflow_elements)} nodes: {frame.url}")
                        return frame
                except:
                    continue
            
            # CRITICAL: L3 V3 must ONLY work within the workflow iframe
            # If no iframe found, this is a failure - we cannot scrape main page content
            logger.error("   ❌ CRITICAL: No workflow iframe found - L3 V3 cannot operate on main page")
            return None
            
        except Exception as e:
            logger.error(f"   ❌ Error finding iframe: {e}")
            return None
    
    async def _extract_setup_instructions(self, frame: Page) -> List[Dict[str, Any]]:
        """Extract setup instructions from the workflow iframe."""
        setup_docs = []
        
        try:
            # Look for standalone documentation elements within the iframe
            setup_selectors = [
                '[class*="sticky"]',  # Standalone sticky notes
                '[data-test-id*="sticky"]',  # Sticky notes with test IDs
                'video',  # Videos for transcription
                'iframe[src*="youtube"]',  # YouTube embeds
                'iframe[src*="vimeo"]',  # Vimeo embeds
                '[class*="explanation"]',  # Explanatory text
                '[class*="description"]',  # Description text
                '[class*="note"]'  # General notes
            ]
            
            for selector in setup_selectors:
                try:
                    elements = await frame.query_selector_all(selector)
                    for element in elements:
                        # Get the content following this element
                        content = await self._extract_content_after_element(frame, element)
                        if content:
                            position = await element.evaluate('''el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: rect.left,
                                    y: rect.top,
                                    width: rect.width,
                                    height: rect.height
                                };
                            }''')
                            
                            setup_docs.append({
                                'workflow_id': '',  # Will be set by caller
                                'doc_type': 'setup_instructions',
                                'doc_title': await element.inner_text() if element else 'Setup Instructions',
                                'doc_content': content,
                                'doc_markdown': self._format_as_markdown(await element.inner_text() if element else 'Setup Instructions', content),
                                'doc_position': position,
                                'confidence_score': 0.9
                            })
                except Exception as e:
                    logger.debug(f"   ⚠️ Error with selector {selector}: {e}")
                    continue
            
            # Also look for common setup patterns in the main content
            main_content = await page.query_selector('main, .main-content, .content, .workflow-content')
            if main_content:
                setup_patterns = [
                    r'(?i)setup\s*instructions?',
                    r'(?i)how\s+to\s+use',
                    r'(?i)configuration\s+guide',
                    r'(?i)getting\s+started'
                ]
                
                content_text = await main_content.inner_text()
                for pattern in setup_patterns:
                    if re.search(pattern, content_text):
                        # Extract the section containing this pattern
                        section_content = await self._extract_section_by_pattern(main_content, pattern)
                        if section_content:
                            setup_docs.append({
                                'workflow_id': '',
                                'doc_type': 'setup_instructions',
                                'doc_title': 'Setup Instructions',
                                'doc_content': section_content,
                                'doc_markdown': self._format_as_markdown('Setup Instructions', section_content),
                                'doc_position': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                                'confidence_score': 0.7
                            })
            
            logger.info(f"   📋 Found {len(setup_docs)} setup instruction sections")
            return setup_docs
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting setup instructions: {e}")
            return []
    
    async def _extract_section_headers(self, frame: Page) -> List[Dict[str, Any]]:
        """Extract section headers and organizational text."""
        section_docs = []
        
        try:
            # Look for section headers
            header_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '[class*="section"]',
                '[class*="header"]',
                '[class*="title"]'
            ]
            
            for selector in header_selectors:
                try:
                    elements = await frame.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 0:
                            # Skip if it's just a single word or very short
                            if len(text.strip()) < 3:
                                continue
                            
                            # Get position
                            position = await element.evaluate('''el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: rect.left,
                                    y: rect.top,
                                    width: rect.width,
                                    height: rect.height
                                };
                            }''')
                            
                            # Determine confidence based on element type and content
                            confidence = 0.5
                            if selector.startswith('h'):
                                confidence = 0.8
                            elif 'section' in selector.lower():
                                confidence = 0.7
                            
                            section_docs.append({
                                'workflow_id': '',
                                'doc_type': 'section_header',
                                'doc_title': text.strip(),
                                'doc_content': text.strip(),
                                'doc_markdown': self._format_as_markdown(text.strip(), ''),
                                'doc_position': position,
                                'confidence_score': confidence
                            })
                except Exception as e:
                    logger.debug(f"   ⚠️ Error with selector {selector}: {e}")
                    continue
            
            logger.info(f"   📑 Found {len(section_docs)} section headers")
            return section_docs
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting section headers: {e}")
            return []
    
    async def _extract_workflow_notes(self, frame: Page) -> List[Dict[str, Any]]:
        """Extract workflow notes and general documentation."""
        note_docs = []
        
        try:
            # Look for note elements
            note_selectors = [
                '[data-test-id="workflow-note"]',
                '[class*="note"]',
                '[class*="description"]',
                '[class*="info"]',
                '[class*="help"]',
                '.alert', '.info', '.note', '.description'
            ]
            
            for selector in note_selectors:
                try:
                    elements = await frame.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 10:  # Only substantial content
                            # Get position
                            position = await element.evaluate('''el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: rect.left,
                                    y: rect.top,
                                    width: rect.width,
                                    height: rect.height
                                };
                            }''')
                            
                            # Determine document type based on content
                            doc_type = 'workflow_note'
                            confidence = 0.6
                            
                            if any(word in text.lower() for word in ['setup', 'configure', 'install']):
                                doc_type = 'setup_instructions'
                                confidence = 0.8
                            elif any(word in text.lower() for word in ['note', 'important', 'warning']):
                                doc_type = 'workflow_note'
                                confidence = 0.7
                            
                            note_docs.append({
                                'workflow_id': '',
                                'doc_type': doc_type,
                                'doc_title': text.strip()[:100] + '...' if len(text.strip()) > 100 else text.strip(),
                                'doc_content': text.strip(),
                                'doc_markdown': self._format_as_markdown('', text.strip()),
                                'doc_position': position,
                                'confidence_score': confidence
                            })
                except Exception as e:
                    logger.debug(f"   ⚠️ Error with selector {selector}: {e}")
                    continue
            
            logger.info(f"   📝 Found {len(note_docs)} workflow notes")
            return note_docs
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting workflow notes: {e}")
            return []
    
    async def _extract_videos(self, frame: Page) -> List[Dict[str, Any]]:
        """Extract videos and transcribe them."""
        video_docs = []
        
        try:
            # Look for video elements
            video_selectors = [
                'video',
                'iframe[src*="youtube"]',
                'iframe[src*="youtube-nocookie"]',
                'iframe[src*="vimeo"]'
            ]
            
            for selector in video_selectors:
                try:
                    elements = await frame.query_selector_all(selector)
                    for element in elements:
                        try:
                            # Get video information
                            src = await element.get_attribute('src')
                            video_type = 'youtube' if 'youtube' in (src or '') else 'vimeo' if 'vimeo' in (src or '') else 'video'
                            
                            # Extract YouTube video ID if it's a YouTube video
                            video_id = None
                            if src and 'youtube' in src:
                                import re
                                match = re.search(r'(?:embed/|v=)([a-zA-Z0-9_-]{11})', src)
                                if match:
                                    video_id = match.group(1)
                            
                            # Get position information
                            position = await element.evaluate('''el => {
                                const rect = el.getBoundingClientRect();
                                return {
                                    x: rect.left,
                                    y: rect.top,
                                    width: rect.width,
                                    height: rect.height
                                };
                            }''')
                            
                            # For now, we'll extract the video info without transcription
                            # Transcription would require additional setup with YouTube API or similar
                            video_doc = {
                                'workflow_id': self.current_workflow_id,
                                'doc_type': 'video',
                                'doc_title': f'Video: {video_type.title()}',
                                'doc_content': f'Video source: {src}\nVideo ID: {video_id or "N/A"}\nType: {video_type}',
                                'doc_markdown': f'## Video: {video_type.title()}\n\n**Source:** {src}\n\n**Video ID:** {video_id or "N/A"}\n\n**Type:** {video_type}\n\n*Note: Transcription not yet implemented*',
                                'doc_position': position,
                                'confidence_score': 0.9
                            }
                            
                            video_docs.append(video_doc)
                            logger.info(f"   🎥 Found {video_type} video: {src}")
                            
                        except Exception as e:
                            logger.error(f"   ❌ Error processing video element: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"   ❌ Error with video selector {selector}: {e}")
                    continue
            
            logger.info(f"   🎥 Found {len(video_docs)} videos")
            return video_docs
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting videos: {e}")
            return []
    
    async def _extract_content_after_element(self, page: Page, element: Any) -> str:
        """Extract content that follows a specific element."""
        try:
            # Get the next sibling elements
            next_elements = await element.evaluate_handle('''el => {
                const siblings = [];
                let next = el.nextElementSibling;
                while (next && siblings.length < 5) {  // Limit to 5 siblings
                    siblings.push(next);
                    next = next.nextElementSibling;
                }
                return siblings;
            }''')
            
            content_parts = []
            for i in range(await next_elements.count()):
                sibling = await next_elements.nth(i)
                text = await sibling.inner_text()
                if text and text.strip():
                    content_parts.append(text.strip())
            
            return '\n\n'.join(content_parts)
            
        except Exception as e:
            logger.debug(f"   ⚠️ Error extracting content after element: {e}")
            return ''
    
    async def _extract_section_by_pattern(self, element: Any, pattern: str) -> str:
        """Extract a section of content based on a text pattern."""
        try:
            # Get all text content
            full_text = await element.inner_text()
            
            # Find the pattern and extract surrounding content
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                start_pos = max(0, match.start() - 100)
                end_pos = min(len(full_text), match.end() + 500)
                return full_text[start_pos:end_pos].strip()
            
            return ''
            
        except Exception as e:
            logger.debug(f"   ⚠️ Error extracting section by pattern: {e}")
            return ''
    
    def _format_as_markdown(self, title: str, content: str) -> str:
        """Format content as markdown."""
        if not title and not content:
            return ''
        
        markdown = ''
        if title:
            markdown += f"## {title}\n\n"
        
        if content:
            # Basic markdown formatting
            content = content.strip()
            
            # Convert line breaks to markdown
            content = content.replace('\n\n', '\n\n')
            
            # Add to markdown
            markdown += content
            
            # Ensure proper spacing
            if not markdown.endswith('\n'):
                markdown += '\n'
        
        return markdown
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        return self.stats.copy()
    
    def save_to_database(self, workflow_id: str, standalone_docs: List[Dict[str, Any]]) -> bool:
        """
        Save standalone documents to the database.
        
        Args:
            workflow_id: The workflow ID
            standalone_docs: List of standalone document dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from src.storage.database import get_session
            from n8n_shared.models import Workflow, WorkflowStandaloneDoc
            from sqlalchemy import text
            
            logger.info(f"💾 Saving {len(standalone_docs)} standalone docs for workflow {workflow_id}")
            
            with get_session() as session:
                # Update workflow table
                workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
                if workflow:
                    workflow.layer3_success = True
                    workflow.layer3_extracted_at = datetime.utcnow()
                
                # Save standalone documents
                for doc in standalone_docs:
                    doc['workflow_id'] = workflow_id  # Set workflow_id
                    
                    # Use raw SQL for JSONB fields
                    insert_sql = text("""
                        INSERT INTO workflow_standalone_docs (
                            workflow_id, doc_type, doc_title, doc_content, doc_markdown,
                            doc_position, confidence_score, extracted_at
                        ) VALUES (
                            :workflow_id, :doc_type, :doc_title, :doc_content, :doc_markdown,
                            :doc_position, :confidence_score, :extracted_at
                        )
                    """)
                    
                    params = {
                        'workflow_id': doc['workflow_id'],
                        'doc_type': doc['doc_type'],
                        'doc_title': doc['doc_title'][:500] if doc['doc_title'] else '',  # Truncate to 500 chars
                        'doc_content': doc['doc_content'],
                        'doc_markdown': doc['doc_markdown'],
                        'doc_position': json.dumps(doc['doc_position']),
                        'confidence_score': doc['confidence_score'],
                        'extracted_at': datetime.utcnow()
                    }
                    
                    session.execute(insert_sql, params)

                # Save raw JSON snapshot for auditing
                snapshot_sql = text("""
                    INSERT INTO workflow_extraction_snapshots (workflow_id, layer, payload)
                    VALUES (:workflow_id, :layer, :payload)
                """)
                session.execute(snapshot_sql, {
                    'workflow_id': workflow_id,
                    'layer': 'L3V3',
                    'payload': json.dumps({'standalone_docs': standalone_docs})
                })
                
                session.commit()
                logger.info(f"✅ Successfully saved {len(standalone_docs)} standalone docs for {workflow_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save standalone docs for {workflow_id}: {e}")
            return False


# Convenience function for single workflow extraction
async def extract_workflow_standalone_docs(workflow_id: str, workflow_url: str, headless: bool = True, save_to_db: bool = True) -> Dict[str, Any]:
    """
    Extract standalone documentation for a single workflow.
    
    Args:
        workflow_id: The n8n.io workflow ID
        workflow_url: The full workflow URL
        headless: Run browser in headless mode
        save_to_db: Whether to save results to database
        
    Returns:
        dict with extraction results
    """
    async with StandaloneDocExtractor(headless=headless) as extractor:
        result = await extractor.extract_standalone_docs(workflow_id, workflow_url)
        
        # Save to database if requested and extraction was successful
        if save_to_db and result['success'] and result['standalone_docs']:
            extractor.save_to_database(workflow_id, result['standalone_docs'])
        
        return result


if __name__ == "__main__":
    # Test the extractor
    async def test_extraction():
        workflow_id = "8237"
        workflow_url = "https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai"
        
        result = await extract_workflow_standalone_docs(workflow_id, workflow_url, headless=False)
        
        print(f"Extraction result: {result['success']}")
        if result['success']:
            print(f"Standalone docs found: {len(result['standalone_docs'])}")
            for doc in result['standalone_docs']:
                print(f"  - {doc['doc_type']}: {doc['confidence_score']:.2f} confidence")
        else:
            print(f"Error: {result['error']}")
    
    asyncio.run(test_extraction())
