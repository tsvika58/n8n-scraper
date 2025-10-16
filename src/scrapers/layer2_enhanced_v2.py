"""
Layer 2 Enhanced V2: Node Context Extractor
Extracts node-specific sticky notes and contextual explanations from n8n workflow iframes.

This is a new version that focuses specifically on:
- Node-specific sticky notes
- Contextual explanations attached to nodes
- Position-based matching between nodes and stickies
- Confidence scoring for matches

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
from src.scrapers.layer2_json import WorkflowJSONExtractor
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


class NodeContextExtractor:
    """
    Extracts node-specific contexts and sticky notes from n8n workflow iframes.
    
    Features:
    - Node detection and positioning
    - Sticky note detection and content extraction
    - Position-based matching between nodes and stickies
    - Confidence scoring for matches
    - Markdown formatting of extracted content
    """
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        """
        Initialize the node context extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None
        self.json_extractor = WorkflowJSONExtractor()
        
        # Statistics tracking
        self.stats = {
            'workflows_processed': 0,
            'nodes_found': 0,
            'stickies_found': 0,
            'matches_made': 0,
            'high_confidence_matches': 0,
            'extraction_errors': 0
        }
        
        logger.info("Node Context Extractor initialized")
    
    async def __aenter__(self):
        """Initialize browser for extraction."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        logger.info("Browser initialized for node context extraction")
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
    
    async def extract_node_contexts(self, workflow_id: str, workflow_url: str) -> Dict[str, Any]:
        """
        Extract node-specific contexts from a workflow.
        
        Args:
            workflow_id: The n8n.io workflow ID
            workflow_url: The full workflow URL
            
        Returns:
            dict with extraction results and node contexts
        """
        start_time = datetime.now()
        self.stats['workflows_processed'] += 1
        
        logger.info(f"🔍 Extracting node contexts for workflow {workflow_id}")
        logger.info(f"   URL: {workflow_url}")
        
        page = await self.context.new_page()
        
        try:
            # Navigate to workflow page
            await page.goto(workflow_url, wait_until='domcontentloaded', timeout=self.timeout)
            await asyncio.sleep(3)  # Wait for iframe to load
            
            # Find and access the workflow iframe
            workflow_frame = await self._find_workflow_iframe(page)
            if not workflow_frame:
                logger.warning(f"   ❌ Workflow iframe not found for {workflow_id}")
                return {
                    'success': False,
                    'error': 'Workflow iframe not found',
                    'workflow_id': workflow_id,
                    'node_contexts': []
                }
            
            # 0) Fetch API workflow JSON (robust baseline for nodes)
            logger.info(f"   🌐 Fetching workflow JSON via API")
            api_result = await self.json_extractor.extract(workflow_id)
            api_nodes = []
            if api_result.get('success') and api_result.get('data'):
                api_nodes = api_result['data'].get('workflow', {}).get('nodes', []) or []
            
            # Use JSON as complete source of truth - separate nodes from sticky notes
            logger.info(f"   📍 Using JSON as complete source for {len(api_nodes)} total items")
            
            # Extract nodes and sticky notes from JSON
            nodes = []
            stickies = []
            
            for an in api_nodes:
                node_type = an.get('type', 'unknown')
                
                if node_type == 'n8n-nodes-base.stickyNote':
                    # This is a sticky note (annotation) - extract it
                    sticky_content = an.get('parameters', {}).get('content', '')
                    stickies.append({
                        'id': an.get('id', ''),
                        'title': an.get('name', ''),
                        'content': sticky_content,
                        'position': {
                            'x': (an.get('position') or [0, 0])[0],
                            'y': (an.get('position') or [0, 0])[1],
                            'width': an.get('parameters', {}).get('width', 0),
                            'height': an.get('parameters', {}).get('height', 0)
                        }
                    })
                else:
                    # This is an actual workflow node
                    nodes.append({
                        'node_id': an.get('id', ''),
                        'node_name': an.get('name') or an.get('id') or 'Unknown',
                        'node_type': node_type,
                        'position': {
                            'x': (an.get('position') or [0, 0])[0],
                            'y': (an.get('position') or [0, 0])[1]
                        }
                    })
            
            logger.info(f"   📍 Found {len(nodes)} actual workflow nodes")
            logger.info(f"   📝 Found {len(stickies)} sticky notes (annotations)")
            self.stats['stickies_found'] += len(stickies)
            
            # Match nodes with sticky notes using JSON coordinates
            logger.info(f"   🔗 Matching nodes with sticky notes using JSON coordinates...")
            node_contexts = await self._match_nodes_with_stickies(nodes, stickies)
            self.stats['matches_made'] += len(node_contexts)
            self.stats['high_confidence_matches'] += sum(1 for ctx in node_contexts if ctx['match_confidence'] > 0.8)
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'workflow_id': workflow_id,
                'url': workflow_url,
                'extraction_time': extraction_time,
                'node_contexts': node_contexts,
                'statistics': {
                    'nodes_found': len(nodes),
                    'stickies_found': len(stickies),
                    'matches_made': len(node_contexts),
                    'high_confidence_matches': sum(1 for ctx in node_contexts if ctx['match_confidence'] > 0.8),
                    'extraction_time': extraction_time
                }
            }
            
            logger.info(f"   ✅ Extraction complete: {len(node_contexts)} node contexts found in {extraction_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.stats['extraction_errors'] += 1
            logger.error(f"   ❌ Extraction failed for {workflow_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id,
                'node_contexts': []
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
            
            # CRITICAL: L2 V2 must ONLY work within the workflow iframe
            # If no iframe found, this is a failure - we cannot scrape main page content
            logger.error("   ❌ CRITICAL: No workflow iframe found - L2 V2 cannot operate on main page")
            return None
            
        except Exception as e:
            logger.error(f"   ❌ Error finding iframe: {e}")
            return None
    
    async def _extract_nodes(self, frame: Page) -> List[Dict[str, Any]]:
        """Extract nodes and their positions from the workflow iframe."""
        nodes = []
        
        try:
            # Use the correct selectors that actually work in n8n iframe
            node_selectors = [
                '[data-node-name]',  # This is the primary selector that works
                '[class*="node"]'    # Fallback selector
            ]
            
            node_elements = []
            for selector in node_selectors:
                try:
                    # Wait longer for iframe content to load
                    await frame.wait_for_selector(selector, timeout=15000)
                    elements = await frame.query_selector_all(selector)
                    if elements:
                        node_elements = elements
                        logger.info(f"   📍 Found {len(elements)} nodes with selector: {selector}")
                        break
                except:
                    continue
            
            if not node_elements:
                logger.warning("   ⚠️ No nodes found with any selector")
                return []
            
            for element in node_elements:
                try:
                    # Get node information (using correct attribute names)
                    node_name = await element.get_attribute('data-node-name') or 'Unknown'
                    node_type = await element.get_attribute('data-node-type') or 'Unknown'
                    node_id = await element.get_attribute('data-id') or 'Unknown'
                    
                    # Get position information
                    position = await element.evaluate('''el => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        const transform = style.transform;
                        
                        return {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height,
                            transform: transform,
                            center_x: rect.left + rect.width / 2,
                            center_y: rect.top + rect.height / 2
                        };
                    }''')
                    
                    # Get node title (display name)
                    title_element = await element.query_selector('[data-test-id="node-title"]')
                    title = await title_element.inner_text() if title_element else node_name
                    
                    nodes.append({
                        'node_id': node_id,
                        'node_name': node_name,
                        'node_type': node_type,
                        'title': title,
                        'position': position,
                        'element': element
                    })
                    
                except Exception as e:
                    logger.debug(f"   ⚠️ Error extracting node: {e}")
                    continue
            
            logger.info(f"   📍 Found {len(nodes)} nodes")
            return nodes
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting nodes: {e}")
            return []
    
    async def _extract_sticky_notes(self, frame: Page) -> List[Dict[str, Any]]:
        """Extract sticky notes and their positions from the workflow iframe."""
        stickies = []
        
        try:
            # Use the correct selectors that actually work in n8n iframe
            sticky_selectors = [
                '[class*="sticky"]',           # Primary selector that works
                '[data-test-id*="sticky"]',    # Secondary selector that works
                '[class*="note"]'              # Fallback selector
            ]
            
            sticky_elements = []
            for selector in sticky_selectors:
                try:
                    elements = await frame.query_selector_all(selector)
                    if elements:
                        sticky_elements.extend(elements)
                        logger.info(f"   📝 Found {len(elements)} sticky elements with selector: {selector}")
                except:
                    continue
            
            # Remove duplicates
            sticky_elements = list(set(sticky_elements))
            logger.info(f"   📝 Total unique sticky elements: {len(sticky_elements)}")
            
            for element in sticky_elements:
                try:
                    # Get sticky content
                    title_element = await element.query_selector('[data-test-id="sticky-title"]')
                    content_element = await element.query_selector('[data-test-id="sticky-content"]')
                    
                    title = await title_element.inner_text() if title_element else ''
                    content = await content_element.inner_text() if content_element else ''
                    
                    # If no specific title/content elements, get all text
                    if not title and not content:
                        full_text = await element.inner_text()
                        lines = full_text.strip().split('\n')
                        title = lines[0] if lines else ''
                        content = '\n'.join(lines[1:]) if len(lines) > 1 else ''
                    
                    # Get position information
                    position = await element.evaluate('''el => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        const transform = style.transform;
                        
                        return {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height,
                            transform: transform,
                            center_x: rect.left + rect.width / 2,
                            center_y: rect.top + rect.height / 2
                        };
                    }''')
                    
                    if title or content:  # Only include if there's actual content
                        stickies.append({
                            'title': title,
                            'content': content,
                            'position': position,
                            'element': element
                        })
                    
                except Exception as e:
                    logger.debug(f"   ⚠️ Error extracting sticky: {e}")
                    continue
            
            logger.info(f"   📝 Found {len(stickies)} sticky notes")
            return stickies
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting sticky notes: {e}")
            return []
    
    async def _match_nodes_with_stickies(self, nodes: List[Dict], stickies: List[Dict]) -> List[Dict[str, Any]]:
        """Match nodes with their corresponding sticky notes based on position and content."""
        node_contexts = []
        
        for node in nodes:
            best_match = None
            best_confidence = 0.0
            best_method = 'none'
            
            # Method 1: Exact name matching
            for sticky in stickies:
                confidence = self._calculate_name_match_confidence(node, sticky)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = sticky
                    best_method = 'name_exact'
            
            # Method 2: Proximity-based matching (if no good name match)
            if best_confidence < 0.7:
                for sticky in stickies:
                    confidence = self._calculate_proximity_confidence(node, sticky)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = sticky
                        best_method = 'proximity'
            
            # Method 3: Fuzzy matching (if still no good match)
            if best_confidence < 0.5:
                for sticky in stickies:
                    confidence = self._calculate_fuzzy_match_confidence(node, sticky)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = sticky
                        best_method = 'fuzzy'
            
            # Create node context if we found a match
            if best_match and best_confidence > 0.3:
                node_context = {
                    'workflow_id': '',  # Will be set by caller
                    'node_name': node['node_name'],
                    'node_type': node['node_type'],
                    'node_position': node['position'],
                    'sticky_title': best_match.get('title', ''),
                    'sticky_content': best_match.get('content', ''),
                    'sticky_markdown': self._format_as_markdown(best_match.get('title', ''), best_match.get('content', '')),
                    'match_confidence': best_confidence,
                    'extraction_method': best_method
                }
                node_contexts.append(node_context)
        
        return node_contexts
    
    def _calculate_name_match_confidence(self, node: Dict, sticky: Dict) -> float:
        """Calculate confidence based on exact name matching."""
        node_name = node['node_name'].lower()
        node_title = node.get('title', node['node_name']).lower()
        sticky_title = sticky.get('title', '').lower()
        sticky_content = sticky['content'].lower()
        
        # Check if node name appears in sticky title or content
        if node_name in sticky_title or node_name in sticky_content:
            return 0.9
        
        # Check if node title appears in sticky
        if node_title in sticky_title or node_title in sticky_content:
            return 0.8
        
        # Check if sticky title appears in node name/title
        if sticky_title and (sticky_title in node_name or sticky_title in node_title):
            return 0.7
        
        return 0.0
    
    def _calculate_proximity_confidence(self, node: Dict, sticky: Dict) -> float:
        """Calculate confidence based on proximity between node and sticky."""
        node_pos = node['position']
        sticky_pos = sticky['position']
        
        # Handle JSON nodes that don't have center_x/center_y
        if 'center_x' not in node_pos or 'center_x' not in sticky_pos:
            # For JSON nodes, use x,y coordinates directly
            node_x = node_pos.get('x', 0)
            node_y = node_pos.get('y', 0)
            sticky_x = sticky_pos.get('center_x', sticky_pos.get('x', 0))
            sticky_y = sticky_pos.get('center_y', sticky_pos.get('y', 0))
        else:
            node_x = node_pos['center_x']
            node_y = node_pos['center_y']
            sticky_x = sticky_pos['center_x']
            sticky_y = sticky_pos['center_y']
        
        # Calculate distance between centers
        distance = ((node_x - sticky_x) ** 2 + (node_y - sticky_y) ** 2) ** 0.5
        
        # Convert distance to confidence (closer = higher confidence)
        # Assume 200px is the threshold for "close"
        if distance < 50:
            return 0.8
        elif distance < 100:
            return 0.6
        elif distance < 200:
            return 0.4
        else:
            return 0.0
    
    def _calculate_fuzzy_match_confidence(self, node: Dict, sticky: Dict) -> float:
        """Calculate confidence based on fuzzy text matching."""
        node_text = f"{node['node_name']} {node.get('title', '')}".lower()
        sticky_text = f"{sticky.get('title', '')} {sticky.get('content', '')}".lower()
        
        # Simple word overlap calculation
        node_words = set(node_text.split())
        sticky_words = set(sticky_text.split())
        
        if not node_words or not sticky_words:
            return 0.0
        
        overlap = len(node_words.intersection(sticky_words))
        total = len(node_words.union(sticky_words))
        
        return overlap / total if total > 0 else 0.0
    
    def _format_as_markdown(self, title: str, content: str) -> str:
        """Format sticky note content as markdown."""
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
    
    def save_to_database(self, workflow_id: str, node_contexts: List[Dict[str, Any]]) -> bool:
        """
        Save node contexts to the database.
        
        Args:
            workflow_id: The workflow ID
            node_contexts: List of node context dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from src.storage.database import get_session
            import sys
            sys.path.append('../n8n-shared')
            from n8n_shared.models import Workflow, WorkflowNodeContext
            from sqlalchemy import text
            
            logger.info(f"💾 Saving {len(node_contexts)} node contexts for workflow {workflow_id}")
            
            with get_session() as session:
                # Update workflow table
                workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
                if workflow:
                    workflow.layer2_success = True
                    workflow.layer2_extracted_at = datetime.utcnow()
                
                # Clear existing node contexts for this workflow
                delete_sql = text("DELETE FROM workflow_node_contexts WHERE workflow_id = :workflow_id")
                session.execute(delete_sql, {'workflow_id': workflow_id})
                logger.info(f"🗑️ Cleared existing node contexts for {workflow_id}")
                
                # Save node contexts
                for ctx in node_contexts:
                    ctx['workflow_id'] = workflow_id  # Set workflow_id
                    
                    # Use raw SQL for JSONB fields
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
                    
                    params = {
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
                    }
                    
                    session.execute(insert_sql, params)

                # Save raw JSON snapshot for auditing
                snapshot_sql = text("""
                    INSERT INTO workflow_extraction_snapshots (workflow_id, layer, payload)
                    VALUES (:workflow_id, :layer, :payload)
                """)
                session.execute(snapshot_sql, {
                    'workflow_id': workflow_id,
                    'layer': 'L2V2',
                    'payload': json.dumps({'node_contexts': node_contexts})
                })
                
                session.commit()
                logger.info(f"✅ Successfully saved {len(node_contexts)} node contexts for {workflow_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save node contexts for {workflow_id}: {e}")
            return False


# Convenience function for single workflow extraction
async def extract_workflow_node_contexts(workflow_id: str, workflow_url: str, headless: bool = True, save_to_db: bool = True) -> Dict[str, Any]:
    """
    Extract node contexts for a single workflow.
    
    Args:
        workflow_id: The n8n.io workflow ID
        workflow_url: The full workflow URL
        headless: Run browser in headless mode
        save_to_db: Whether to save results to database
        
    Returns:
        dict with extraction results
    """
    async with NodeContextExtractor(headless=headless) as extractor:
        result = await extractor.extract_node_contexts(workflow_id, workflow_url)
        
        # Save to database if requested and extraction was successful
        if save_to_db and result['success'] and result['node_contexts']:
            extractor.save_to_database(workflow_id, result['node_contexts'])
        
        return result


if __name__ == "__main__":
    # Test the extractor
    async def test_extraction():
        workflow_id = "8237"
        workflow_url = "https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai"
        
        result = await extract_workflow_node_contexts(workflow_id, workflow_url, headless=False)
        
        print(f"Extraction result: {result['success']}")
        if result['success']:
            print(f"Node contexts found: {len(result['node_contexts'])}")
            for ctx in result['node_contexts']:
                print(f"  - {ctx['node_name']}: {ctx['match_confidence']:.2f} confidence")
        else:
            print(f"Error: {result['error']}")
    
    asyncio.run(test_extraction())
