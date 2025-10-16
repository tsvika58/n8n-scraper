"""
Layer 1 Enhanced Clean Scraper - Complete Workflow Page Content Extractor

This scraper extracts ALL relevant content from n8n workflow pages while excluding
navigation, footers, testimonials, and other non-workflow content.

Responsibilities:
1. Structured metadata (title, author, categories, tags, engagement metrics)
2. Brief description (summary)
3. Complete general content (node explanations, setup instructions, examples, images, videos)
   - Markdown formatted
   - Includes hyperlinks, images, videos
   - Handles zero content to unlimited content
   - Stops at content boundaries (before testimonials/footer)

Author: AI Assistant
Date: October 16, 2025
Version: 2.0.0 (Clean Edition)
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

from playwright.async_api import Page, Browser, async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup, Tag, NavigableString
from loguru import logger


class Layer1EnhancedCleanScraper:
    """
    Enhanced Layer 1 scraper that extracts complete workflow page content
    while filtering out navigation, footers, and other non-workflow content.
    """
    
    # Content boundaries - stop extraction when we hit these
    CONTENT_STOP_MARKERS = [
        "There's nothing you can't automate",
        "More templates by",
        "Stars",
        "Popular integrations",
        "Trending combinations",
        "Top integration categories",
        "Trending templates",
        "Top guides",
        "Imprint | Security | Privacy",
        "© 2025 n8n",
        "© 2024 n8n",
        "Our customer's words",
        "Skeptical? Try it out",
        "Start building",
        "Show more integrations",
        "Explore more categories",
        "Show guides",
    ]
    
    # Navigation/header sections to skip
    SKIP_SECTIONS = [
        "Product overview",
        "Use cases",
        "Docs",
        "Community",
        "Enterprise",
        "Pricing",
        "Sign in",
        "Get Started",
        "GitHub",
        "Back to Templates",
    ]
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 60000,  # Increased to 60 seconds
        wait_for_content: int = 5000  # Increased to 5 seconds
    ):
        """Initialize the enhanced clean scraper."""
        self.headless = headless
        self.timeout = timeout
        self.wait_for_content = wait_for_content
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize the browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("Layer 1 Enhanced Clean scraper initialized")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Layer 1 Enhanced Clean scraper cleaned up")
    
    async def extract(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Extract complete, clean workflow content.
        
        Args:
            workflow_id: n8n workflow ID
            url: Full workflow URL
            
        Returns:
            Dictionary with:
            - success: bool
            - metadata: Structured data (title, author, categories, etc.)
            - content: Unstructured markdown content
            - errors: List of errors
        """
        start_time = datetime.now()
        
        result = {
            "success": False,
            "metadata": {},
            "content": {
                "description_brief": "",
                "full_content_markdown": "",
                "images": [],
                "videos": [],
                "hyperlinks": [],
                "code_snippets": [],
            },
            "errors": [],
            "extraction_time": 0.0
        }
        
        try:
            page = await self.browser.new_page()
            page.set_default_timeout(self.timeout)
            
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=self.timeout)
            await page.wait_for_timeout(self.wait_for_content)
            
            # Get page HTML
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract structured metadata
            result["metadata"] = await self._extract_metadata(page, soup)
            
            # Extract unstructured content (the main work!)
            result["content"] = await self._extract_clean_content(page, soup)
            
            await page.close()
            
            # Validate extraction
            result["success"] = self._validate_extraction(result)
            
            # Calculate time
            result["extraction_time"] = (datetime.now() - start_time).total_seconds()
            
            logger.success(
                f"Layer 1 Enhanced extraction for {workflow_id}: "
                f"{len(result['content']['full_content_markdown'])} chars, "
                f"{len(result['content']['images'])} images, "
                f"{len(result['content']['videos'])} videos"
            )
            
        except PlaywrightTimeout as e:
            error_msg = f"Timeout: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result
    
    async def _extract_metadata(self, page: Page, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured metadata fields."""
        
        metadata = {
            "workflow_id": "",
            "title": "",
            "author_name": "",
            "author_url": "",
            "categories": [],
            "tags": [],
            "views": 0,
            "shares": 0,
            "last_updated": None,
            "n8n_url": await page.url if page else "",
        }
        
        # Extract title
        title_selectors = ['h1', 'title', 'meta[property="og:title"]']
        for selector in title_selectors:
            try:
                if selector.startswith('meta'):
                    element = soup.find('meta', attrs={'property': 'og:title'})
                    if element and element.get('content'):
                        metadata["title"] = element.get('content').strip()
                        break
                else:
                    element = soup.find(selector)
                    if element:
                        text = element.get_text().strip()
                        # Clean title (remove navigation text)
                        if text and not any(skip in text for skip in self.SKIP_SECTIONS):
                            metadata["title"] = text
                            break
            except:
                continue
        
        # Extract author
        author_patterns = [
            ('a', {'href': lambda x: x and 'creators' in x}),
            ('span', {'class': lambda x: x and 'author' in str(x).lower()}),
            ('div', {'class': lambda x: x and 'creator' in str(x).lower()}),
        ]
        
        for tag, attrs in author_patterns:
            try:
                element = soup.find(tag, attrs)
                if element:
                    metadata["author_name"] = element.get_text().strip()
                    if element.name == 'a':
                        metadata["author_url"] = element.get('href', '')
                    break
            except:
                continue
        
        # Extract categories - look for badges/pills
        try:
            category_elements = soup.find_all(['span', 'a'], class_=lambda x: x and any(
                cat in str(x).lower() for cat in ['category', 'tag', 'badge', 'pill']
            ))
            
            categories = set()
            for elem in category_elements:
                text = elem.get_text().strip()
                # Filter out common non-category text
                if text and len(text) < 50 and text not in self.SKIP_SECTIONS:
                    categories.add(text)
            
            metadata["categories"] = list(categories)[:10]  # Max 10 categories
        except Exception as e:
            logger.warning(f"Error extracting categories: {e}")
        
        # Extract views (if available)
        try:
            views_patterns = [
                soup.find('span', string=re.compile(r'\d+\s*views?', re.I)),
                soup.find('div', string=re.compile(r'\d+\s*views?', re.I)),
            ]
            
            for elem in views_patterns:
                if elem:
                    match = re.search(r'(\d+)', elem.get_text())
                    if match:
                        metadata["views"] = int(match.group(1))
                        break
        except:
            pass
        
        return metadata
    
    async def _extract_clean_content(self, page: Page, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract clean, relevant workflow content.
        
        Strategy:
        1. Find the main content area
        2. Extract text, preserving structure
        3. Stop at content boundaries
        4. Format as clean markdown
        5. Extract images, videos, code snippets
        """
        
        content = {
            "description_brief": "",
            "full_content_markdown": "",
            "images": [],
            "videos": [],
            "hyperlinks": [],
            "code_snippets": [],
        }
        
        try:
            # Find main content container
            main_content = self._find_main_content(soup)
            
            if not main_content:
                logger.warning("Could not find main content container")
                return content
            
            # Extract description brief (first paragraph)
            content["description_brief"] = self._extract_brief_description(main_content)
            
            # Extract full content as markdown
            markdown_parts = []
            images = []
            videos = []
            hyperlinks = []
            code_snippets = []
            
            # Process each child element
            for element in main_content.children:
                if isinstance(element, NavigableString):
                    text = str(element).strip()
                    if text:
                        markdown_parts.append(text)
                    continue
                
                if not isinstance(element, Tag):
                    continue
                
                # Check if we hit a stop marker
                element_text = element.get_text()
                if self._should_stop_extraction(element_text):
                    logger.debug(f"Hit stop marker in: {element_text[:50]}")
                    break
                
                # Process different element types
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(element.name[1])
                    text = element.get_text().strip()
                    if text and not self._is_navigation_text(text):
                        markdown_parts.append(f"\n{'#' * level} {text}\n")
                
                elif element.name == 'p':
                    text = self._process_paragraph(element, hyperlinks)
                    if text and not self._is_navigation_text(text):
                        markdown_parts.append(f"\n{text}\n")
                
                elif element.name in ['ul', 'ol']:
                    list_md = self._process_list(element, hyperlinks)
                    if list_md:
                        markdown_parts.append(f"\n{list_md}\n")
                
                elif element.name == 'pre' or (element.name == 'code' and element.parent.name != 'pre'):
                    code = element.get_text().strip()
                    if code:
                        code_snippets.append(code)
                        markdown_parts.append(f"\n```\n{code}\n```\n")
                
                elif element.name == 'img':
                    img_data = self._process_image(element)
                    if img_data:
                        images.append(img_data)
                        markdown_parts.append(f"\n![{img_data['alt']}]({img_data['src']})\n")
                
                elif element.name == 'iframe':
                    video_data = self._process_video_iframe(element)
                    if video_data:
                        videos.append(video_data)
                        markdown_parts.append(f"\n[🎬 Video: {video_data['platform']}]({video_data['url']})\n")
                
                elif element.name == 'blockquote':
                    text = element.get_text().strip()
                    if text and not self._is_navigation_text(text):
                        markdown_parts.append(f"\n> {text}\n")
                
                elif element.name == 'div':
                    # Process div content recursively
                    div_content = self._process_div(element, images, videos, hyperlinks, code_snippets)
                    if div_content:
                        markdown_parts.append(div_content)
            
            # Combine all parts
            content["full_content_markdown"] = "\n".join(markdown_parts).strip()
            content["images"] = images
            content["videos"] = videos
            content["hyperlinks"] = hyperlinks
            content["code_snippets"] = code_snippets
            
            logger.info(
                f"Extracted {len(content['full_content_markdown'])} chars, "
                f"{len(images)} images, {len(videos)} videos"
            )
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
        
        return content
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the main content container."""
        
        # Try multiple selectors for main content
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.workflow-content',
            '.template-content',
            '#content',
            '.main-content',
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element
        
        # Fallback: find the largest div with meaningful content
        all_divs = soup.find_all('div')
        max_content_length = 0
        main_div = None
        
        for div in all_divs:
            text = div.get_text()
            # Skip if it's navigation or footer
            if self._is_navigation_text(text):
                continue
            
            if len(text) > max_content_length and len(text) > 500:
                max_content_length = len(text)
                main_div = div
        
        return main_div or soup.body
    
    def _extract_brief_description(self, main_content: Tag) -> str:
        """Extract the first meaningful paragraph as brief description."""
        
        # Find first substantial paragraph
        for p in main_content.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 50 and not self._is_navigation_text(text):
                return text
        
        return ""
    
    def _should_stop_extraction(self, text: str) -> bool:
        """Check if we've hit a content boundary marker."""
        text_lower = text.lower()
        return any(marker.lower() in text_lower for marker in self.CONTENT_STOP_MARKERS)
    
    def _is_navigation_text(self, text: str) -> bool:
        """Check if text is likely navigation/header/footer content."""
        text_clean = text.strip()
        
        # Too short
        if len(text_clean) < 3:
            return True
        
        # Common navigation patterns
        if any(skip in text_clean for skip in self.SKIP_SECTIONS):
            return True
        
        # All caps (likely navigation)
        if text_clean.isupper() and len(text_clean) < 30:
            return True
        
        return False
    
    def _process_paragraph(self, p_elem: Tag, hyperlinks: List[Dict]) -> str:
        """Process paragraph with inline formatting."""
        
        markdown = ""
        
        for child in p_elem.children:
            if isinstance(child, NavigableString):
                markdown += str(child)
            elif isinstance(child, Tag):
                if child.name == 'strong' or child.name == 'b':
                    markdown += f"**{child.get_text()}**"
                elif child.name == 'em' or child.name == 'i':
                    markdown += f"*{child.get_text()}*"
                elif child.name == 'code':
                    markdown += f"`{child.get_text()}`"
                elif child.name == 'a':
                    link_text = child.get_text()
                    link_url = child.get('href', '')
                    if link_url:
                        hyperlinks.append({"text": link_text, "url": link_url})
                        markdown += f"[{link_text}]({link_url})"
                    else:
                        markdown += link_text
                else:
                    markdown += child.get_text()
        
        return markdown.strip()
    
    def _process_list(self, list_elem: Tag, hyperlinks: List[Dict]) -> str:
        """Process ordered or unordered list."""
        
        markdown_lines = []
        is_ordered = list_elem.name == 'ol'
        
        items = list_elem.find_all('li', recursive=False)
        
        for idx, li in enumerate(items, 1):
            text = self._process_paragraph(li, hyperlinks)
            if text and not self._is_navigation_text(text):
                prefix = f"{idx}." if is_ordered else "-"
                markdown_lines.append(f"{prefix} {text}")
        
        return "\n".join(markdown_lines)
    
    def _process_image(self, img_elem: Tag) -> Optional[Dict[str, Any]]:
        """Process image element."""
        
        src = img_elem.get('src', '')
        
        # Skip icons, SVGs, and data URIs
        if not src or src.startswith('data:') or '/icons/' in src or src.endswith('.svg'):
            return None
        
        # Make absolute URL if relative
        if src.startswith('/'):
            src = f"https://n8n.io{src}"
        
        return {
            "src": src,
            "alt": img_elem.get('alt', ''),
            "width": img_elem.get('width'),
            "height": img_elem.get('height'),
        }
    
    def _process_video_iframe(self, iframe_elem: Tag) -> Optional[Dict[str, Any]]:
        """Process video iframe element."""
        
        src = iframe_elem.get('src', '')
        
        if not src:
            return None
        
        # Detect platform
        platform = "unknown"
        video_id = ""
        
        if 'youtube.com' in src or 'youtu.be' in src:
            platform = "youtube"
            match = re.search(r'/embed/([a-zA-Z0-9_-]+)', src)
            if match:
                video_id = match.group(1)
        elif 'vimeo.com' in src:
            platform = "vimeo"
            match = re.search(r'/video/(\d+)', src)
            if match:
                video_id = match.group(1)
        elif 'n8n.io' in src:
            platform = "n8n_workflow"
        
        return {
            "platform": platform,
            "url": src,
            "video_id": video_id,
        }
    
    def _process_div(
        self, 
        div_elem: Tag, 
        images: List[Dict], 
        videos: List[Dict], 
        hyperlinks: List[Dict],
        code_snippets: List[str]
    ) -> str:
        """Process div element recursively."""
        
        # Check if this div contains workflow content
        text = div_elem.get_text().strip()
        
        # Skip if navigation or should stop
        if self._is_navigation_text(text) or self._should_stop_extraction(text):
            return ""
        
        markdown_parts = []
        
        # Look for special content
        for child in div_elem.children:
            if isinstance(child, Tag):
                if child.name == 'img':
                    img_data = self._process_image(child)
                    if img_data:
                        images.append(img_data)
                        markdown_parts.append(f"![{img_data['alt']}]({img_data['src']})")
                
                elif child.name == 'iframe':
                    video_data = self._process_video_iframe(child)
                    if video_data:
                        videos.append(video_data)
                        markdown_parts.append(f"[🎬 Video: {video_data['platform']}]({video_data['url']})")
                
                elif child.name == 'pre' or child.name == 'code':
                    code = child.get_text().strip()
                    if code:
                        code_snippets.append(code)
                        markdown_parts.append(f"```\n{code}\n```")
                
                elif child.name == 'p':
                    text = self._process_paragraph(child, hyperlinks)
                    if text:
                        markdown_parts.append(text)
        
        return "\n".join(markdown_parts)
    
    def _validate_extraction(self, result: Dict[str, Any]) -> bool:
        """Validate that we extracted meaningful content."""
        
        # Must have title
        if not result["metadata"].get("title"):
            return False
        
        # Must have some content (at least description)
        if not result["content"]["description_brief"] and not result["content"]["full_content_markdown"]:
            return False
        
        # Content should not be just navigation junk
        content = result["content"]["full_content_markdown"]
        if self._should_stop_extraction(content):
            return False
        
        return True
    
    def format_for_database(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format extraction result for database storage.
        
        Returns:
            Dictionary matching WorkflowMetadata schema
        """
        
        if not result["success"]:
            return {}
        
        metadata = result["metadata"]
        content = result["content"]
        
        return {
            # Structured metadata
            "title": metadata.get("title", ""),
            "author_name": metadata.get("author_name", ""),
            "author_url": metadata.get("author_url", ""),
            "categories": metadata.get("categories", []),
            "tags": metadata.get("tags", []),
            "views": metadata.get("views", 0),
            "shares": metadata.get("shares", 0),
            
            # Content fields
            "description": content.get("description_brief", ""),
            "use_case": content.get("description_brief", ""),  # Can be same or extracted separately
            
            # NEW: Full page content (clean, markdown formatted)
            "page_content_markdown": content.get("full_content_markdown", ""),
            
            # Media assets
            "images_data": content.get("images", []),
            "videos_data": content.get("videos", []),
            "hyperlinks_data": content.get("hyperlinks", []),
            "code_snippets_data": content.get("code_snippets", []),
        }


# Test function
async def test_scraper(workflow_ids: List[str]):
    """Test the scraper on multiple workflows."""
    
    async with Layer1EnhancedCleanScraper(headless=True) as scraper:
        for wf_id in workflow_ids:
            url = f"https://n8n.io/workflows/{wf_id}"
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Testing workflow {wf_id}")
            logger.info(f"{'='*80}")
            
            result = await scraper.extract(wf_id, url)
            
            if result["success"]:
                logger.success(f"✅ Successfully extracted workflow {wf_id}")
                logger.info(f"   Title: {result['metadata'].get('title', 'N/A')}")
                logger.info(f"   Author: {result['metadata'].get('author_name', 'N/A')}")
                logger.info(f"   Content length: {len(result['content']['full_content_markdown'])} chars")
                logger.info(f"   Images: {len(result['content']['images'])}")
                logger.info(f"   Videos: {len(result['content']['videos'])}")
                logger.info(f"   Hyperlinks: {len(result['content']['hyperlinks'])}")
            else:
                logger.error(f"❌ Failed to extract workflow {wf_id}")
                logger.error(f"   Errors: {result['errors']}")
            
            # Small delay between requests
            await asyncio.sleep(2)


if __name__ == "__main__":
    # Test on diverse workflows
    test_workflows = [
        "694",    # Medium content (Google Sheets example)
        "1381",   # Most content (75KB)
        "418",    # Minimal content (4KB)
        "2462",   # Has video
        "3725",   # Complex workflow (159 nodes)
    ]
    
    asyncio.run(test_scraper(test_workflows))

