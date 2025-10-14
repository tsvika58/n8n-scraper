"""
Layer 1.5 - Full Page Content Extractor

This module extracts ALL content from n8n.io workflow pages.
It's designed to capture the complete page content that Layer 1 currently misses.

Author: AI Assistant
Date: October 14, 2025
Purpose: Extract full n8n.io page content including descriptions, setup instructions, examples
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

from playwright.async_api import Page, Browser, async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from loguru import logger


class Layer1_5PageContentExtractor:
    """
    Extract ALL content from n8n.io workflow pages.
    
    This extractor captures:
    - Full page descriptions (not just meta tags)
    - Setup instructions
    - "How It Works" sections
    - Example outputs
    - Complete page HTML
    - All text content from the page body
    
    Target: Extract 3,000+ characters of content that Layer 1 currently misses
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,  # 30 seconds
        wait_for_content: int = 3000  # 3 seconds for dynamic content
    ):
        """
        Initialize the page content extractor.
        
        Args:
            headless: Run browser in headless mode
            timeout: Maximum time to wait for page load (ms)
            wait_for_content: Time to wait for dynamic content (ms)
        """
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
        logger.info("Layer 1.5 Page Content extractor initialized")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Layer 1.5 Page Content extractor cleaned up")
    
    async def extract_full_page_content(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Extract ALL content from a workflow page.
        
        Args:
            workflow_id: n8n workflow ID (e.g., "8040")
            url: Full n8n.io workflow URL
            
        Returns:
            Dictionary containing:
            - success: bool - Extraction success status
            - data: Dict - Extracted page content
            - errors: List[str] - Any errors encountered
            - extraction_time: float - Time taken in seconds
            - metadata: Dict - Extraction metadata
        """
        start_time = datetime.now()
        
        logger.info(f"Starting Layer 1.5 extraction for workflow {workflow_id}")
        
        result = {
            "success": False,
            "data": self._get_empty_structure(),
            "errors": [],
            "extraction_time": 0.0,
            "metadata": {
                "workflow_id": workflow_id,
                "url": url,
                "extracted_at": start_time.isoformat(),
                "extractor_version": "1.0.0"
            }
        }
        
        try:
            # Create new page
            page = await self.browser.new_page()
            page.set_default_timeout(self.timeout)
            
            # Navigate to workflow page
            logger.debug(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for page to stabilize
            await page.wait_for_timeout(self.wait_for_content)
            
            # Get full page HTML
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract all page content
            await self._extract_page_content(page, soup, result["data"])
            
            # Close page
            await page.close()
            
            # Mark as successful if we got meaningful content
            result["success"] = self._validate_extraction(result["data"])
            
            # Calculate extraction time
            end_time = datetime.now()
            result["extraction_time"] = (end_time - start_time).total_seconds()
            
            # Generate Markdown and metadata if successful
            if result["success"]:
                result["markdown"] = self.format_as_markdown(workflow_id, result["data"])
                result["metadata"] = self.extract_metadata(result["data"], result["extraction_time"])
            
            logger.success(
                f"Layer 1.5 extraction completed for workflow {workflow_id} "
                f"in {result['extraction_time']:.2f}s"
            )
            
        except PlaywrightTimeout as e:
            error_msg = f"Timeout extracting workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error extracting workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result
    
    async def _extract_page_content(self, page: Page, soup: BeautifulSoup, data: Dict):
        """Extract all content from the page"""
        
        # 1. Extract main description (full content, not just meta)
        await self._extract_main_description(soup, data)
        
        # 2. Extract "How It Works" section
        await self._extract_how_it_works(soup, data)
        
        # 3. Extract setup instructions
        await self._extract_setup_instructions(soup, data)
        
        # 4. Extract examples and code snippets
        await self._extract_examples(soup, data)
        
        # 5. Extract all text content
        await self._extract_all_text_content(soup, data)
        
        # 6. Store full page HTML
        data["full_page_html"] = str(soup)
        
        # 7. Extract metadata
        await self._extract_enhanced_metadata(soup, data)
        
        logger.info(f"Extracted {len(data['all_text_content'])} characters of content")
    
    async def _extract_main_description(self, soup: BeautifulSoup, data: Dict):
        """Extract the main workflow description"""
        
        # Try multiple selectors for the main description
        description_selectors = [
            'h1 + p',  # Paragraph after main title
            '.workflow-description',
            '.description',
            'article p:first-of-type',
            'main p:first-of-type',
            '[data-testid="workflow-description"]',
            'meta[name="description"]'
        ]
        
        for selector in description_selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    data["main_description"] = elem['content'].strip()
                    logger.debug(f"Found main description (meta): {len(data['main_description'])} chars")
                    break
            else:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 50:  # Only meaningful descriptions
                        data["main_description"] = text
                        logger.debug(f"Found main description: {len(text)} chars")
                        break
    
    async def _extract_how_it_works(self, soup: BeautifulSoup, data: Dict):
        """Extract the 'How It Works' section"""
        
        # Look for "How It Works" section
        how_it_works_selectors = [
            'h2:contains("How It Works")',
            'h3:contains("How It Works")',
            '.how-it-works',
            '[data-testid="how-it-works"]'
        ]
        
        how_it_works_text = []
        
        for selector in how_it_works_selectors:
            if ':contains(' in selector:
                # Handle text-based selectors
                base_selector = selector.split(':contains(')[0]
                text_pattern = selector.split(':contains(')[1].rstrip(')')
                elements = soup.select(base_selector)
                for elem in elements:
                    if text_pattern.lower() in elem.get_text().lower():
                        # Get the content after this heading
                        next_elem = elem.find_next_sibling()
                        while next_elem:
                            if next_elem.name in ['h1', 'h2', 'h3', 'h4']:
                                break
                            text = next_elem.get_text(strip=True)
                            if text:
                                how_it_works_text.append(text)
                            next_elem = next_elem.find_next_sibling()
                        break
            else:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text:
                        how_it_works_text.append(text)
        
        if how_it_works_text:
            data["how_it_works"] = "\n\n".join(how_it_works_text)
            logger.debug(f"Found 'How It Works' section: {len(data['how_it_works'])} chars")
    
    async def _extract_setup_instructions(self, soup: BeautifulSoup, data: Dict):
        """Extract setup instructions"""
        
        setup_selectors = [
            'h2:contains("Setup")',
            'h3:contains("Setup")',
            '.setup-instructions',
            '.setup-steps',
            '[data-testid="setup"]'
        ]
        
        setup_text = []
        
        for selector in setup_selectors:
            if ':contains(' in selector:
                base_selector = selector.split(':contains(')[0]
                text_pattern = selector.split(':contains(')[1].rstrip(')')
                elements = soup.select(base_selector)
                for elem in elements:
                    if text_pattern.lower() in elem.get_text().lower():
                        # Get the content after this heading
                        next_elem = elem.find_next_sibling()
                        while next_elem:
                            if next_elem.name in ['h1', 'h2', 'h3', 'h4']:
                                break
                            text = next_elem.get_text(strip=True)
                            if text:
                                setup_text.append(text)
                            next_elem = next_elem.find_next_sibling()
                        break
            else:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text:
                        setup_text.append(text)
        
        if setup_text:
            data["setup_instructions"] = "\n\n".join(setup_text)
            logger.debug(f"Found setup instructions: {len(data['setup_instructions'])} chars")
    
    async def _extract_examples(self, soup: BeautifulSoup, data: Dict):
        """Extract examples and code snippets"""
        
        # Extract code blocks
        code_blocks = soup.find_all(['pre', 'code', 'blockquote'])
        examples = []
        
        for block in code_blocks:
            text = block.get_text(strip=True)
            if text and len(text) > 20:  # Only meaningful code
                examples.append(text)
        
        if examples:
            data["examples"] = examples
            logger.debug(f"Found {len(examples)} examples/code blocks")
        
        # Look for specific example sections
        example_selectors = [
            'h2:contains("Example")',
            'h3:contains("Example")',
            '.example',
            '[data-testid="example"]'
        ]
        
        for selector in example_selectors:
            if ':contains(' in selector:
                base_selector = selector.split(':contains(')[0]
                text_pattern = selector.split(':contains(')[1].rstrip(')')
                elements = soup.select(base_selector)
                for elem in elements:
                    if text_pattern.lower() in elem.get_text().lower():
                        # Get the content after this heading
                        next_elem = elem.find_next_sibling()
                        while next_elem:
                            if next_elem.name in ['h1', 'h2', 'h3', 'h4']:
                                break
                            text = next_elem.get_text(strip=True)
                            if text:
                                examples.append(text)
                            next_elem = next_elem.find_next_sibling()
                        break
        
        if examples:
            data["example_content"] = "\n\n".join(examples)
            logger.debug(f"Found example content: {len(data['example_content'])} chars")
    
    async def _extract_all_text_content(self, soup: BeautifulSoup, data: Dict):
        """Extract all meaningful text content from the page"""
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get all text
        all_text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in all_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        data["all_text_content"] = clean_text
        logger.debug(f"Extracted {len(clean_text)} characters of clean text")
    
    async def _extract_enhanced_metadata(self, soup: BeautifulSoup, data: Dict):
        """Extract enhanced metadata"""
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            data["page_title"] = title_elem.get_text(strip=True)
        
        # Extract author
        author_selectors = [
            '[data-testid="author"]',
            '.author',
            '.creator'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                data["author"] = elem.get_text(strip=True)
                break
        
        # Extract categories/tags
        tag_selectors = [
            '.tags',
            '.categories',
            '[data-testid="tags"]'
        ]
        
        tags = []
        for selector in tag_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text:
                    tags.append(text)
        
        if tags:
            data["tags"] = tags
        
        # Extract any additional metadata
        meta_tags = soup.find_all('meta')
        metadata = {}
        
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        if metadata:
            data["meta_tags"] = metadata
    
    def _get_empty_structure(self) -> Dict:
        """Get empty data structure"""
        return {
            "main_description": "",
            "how_it_works": "",
            "setup_instructions": "",
            "examples": [],
            "example_content": "",
            "all_text_content": "",
            "full_page_html": "",
            "page_title": "",
            "author": "",
            "tags": [],
            "meta_tags": {}
        }
    
    def _validate_extraction(self, data: Dict) -> bool:
        """Validate that we extracted meaningful content"""
        
        # Check if we have substantial content
        total_content = len(data.get("all_text_content", ""))
        main_desc = len(data.get("main_description", ""))
        
        # Consider successful if we have substantial content
        success = total_content > 1000 or main_desc > 200
        
        if success:
            logger.info(f"Extraction successful: {total_content} chars total, {main_desc} chars description")
        else:
            logger.warning(f"Extraction may have failed: only {total_content} chars total")
        
        return success
    
    def format_as_markdown(self, workflow_id: str, data: Dict) -> str:
        """Convert extracted data to structured Markdown"""
        md_parts = []
        
        # Frontmatter with metadata
        md_parts.append("---")
        md_parts.append(f"workflow_id: \"{workflow_id}\"")
        if data.get("page_title"):
            md_parts.append(f"title: \"{data['page_title']}\"")
        if data.get("author"):
            md_parts.append(f"author: \"{data['author']}\"")
        md_parts.append("---\n")
        
        # Main title
        if data.get("page_title"):
            md_parts.append(f"# {data['page_title']}\n")
        
        # Author
        if data.get("author"):
            md_parts.append(f"**Author:** {data['author']}\n")
        
        # Main description
        if data.get("main_description"):
            md_parts.append("## Description\n")
            md_parts.append(f"{data['main_description']}\n")
        
        # How it works (if exists)
        if data.get("how_it_works"):
            md_parts.append("## How It Works\n")
            md_parts.append(f"{data['how_it_works']}\n")
        
        # Setup instructions (if exists)
        if data.get("setup_instructions"):
            md_parts.append("## Setup Instructions\n")
            md_parts.append(f"{data['setup_instructions']}\n")
        
        # Examples (if exist)
        if data.get("examples"):
            md_parts.append("## Examples\n")
            for i, example in enumerate(data["examples"], 1):
                md_parts.append(f"### Example {i}\n")
                md_parts.append("```")
                md_parts.append(example)
                md_parts.append("```\n")
        
        # Complete page content
        md_parts.append("## Complete Page Content\n")
        md_parts.append(data.get("all_text_content", ""))
        
        return "\n".join(md_parts)
    
    def extract_metadata(self, data: Dict, extraction_time: float) -> Dict:
        """Extract queryable metadata from raw data"""
        return {
            "extraction_time": extraction_time,
            "content_length": len(data.get("all_text_content", "")),
            "description_length": len(data.get("main_description", "")),
            "has_examples": bool(data.get("examples")),
            "examples_count": len(data.get("examples", [])),
            "has_images": bool(data.get("meta_tags", {}).get("og:image")),
            "has_code_blocks": len(data.get("examples", [])) > 0,
            "author": data.get("author", ""),
            "page_title": data.get("page_title", ""),
            "extractor_version": "1.0.0"
        }


# Test function
async def test_layer1_5_extraction():
    """Test the Layer 1.5 extractor on workflow 8040"""
    
    print("🧪 TESTING LAYER 1.5 EXTRACTION")
    print("=" * 70)
    
    async with Layer1_5PageContentExtractor() as extractor:
        result = await extractor.extract_full_page_content(
            workflow_id="8040",
            url="https://n8n.io/workflows/8040-weather-alerts-via-sms-openweather-twilio"
        )
        
        if result["success"]:
            data = result["data"]
            
            print(f"✅ EXTRACTION SUCCESSFUL!")
            print(f"   Extraction time: {result['extraction_time']:.2f}s")
            print(f"   Total content: {len(data['all_text_content'])} characters")
            print(f"   Main description: {len(data['main_description'])} characters")
            
            if data.get("how_it_works"):
                print(f"   'How It Works': {len(data['how_it_works'])} characters")
            
            if data.get("setup_instructions"):
                print(f"   Setup instructions: {len(data['setup_instructions'])} characters")
            
            if data.get("examples"):
                print(f"   Examples: {len(data['examples'])} items")
            
            print(f"\\n📝 MAIN DESCRIPTION PREVIEW:")
            print(f"   {data['main_description'][:300]}...")
            
            print(f"\\n📝 'HOW IT WORKS' PREVIEW:")
            if data.get("how_it_works"):
                print(f"   {data['how_it_works'][:300]}...")
            else:
                print("   Not found")
            
            print(f"\\n📝 SETUP INSTRUCTIONS PREVIEW:")
            if data.get("setup_instructions"):
                print(f"   {data['setup_instructions'][:300]}...")
            else:
                print("   Not found")
                
        else:
            print(f"❌ EXTRACTION FAILED!")
            print(f"   Errors: {result['errors']}")
        
        print("=" * 70)
        
        return result


if __name__ == "__main__":
    asyncio.run(test_layer1_5_extraction())
