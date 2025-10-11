"""
Workflow Inventory Crawler - SCRAPE-002B
Builds complete inventory of all n8n.io workflows from sitemap
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
import aiohttp
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowInventoryCrawler:
    """Crawls n8n.io sitemap to build complete workflow inventory."""
    
    def __init__(self):
        self.sitemap_url = "https://n8n.io/sitemap-workflows.xml"
        self.workflows_discovered = 0
        self.errors = []
        
    async def fetch_sitemap(self) -> Optional[str]:
        """Fetch sitemap XML from n8n.io."""
        try:
            logger.info(f"Fetching sitemap from {self.sitemap_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.sitemap_url) as response:
                    if response.status == 200:
                        sitemap_xml = await response.text()
                        logger.info(f"Successfully fetched sitemap ({len(sitemap_xml)} bytes)")
                        return sitemap_xml
                    else:
                        error_msg = f"Failed to fetch sitemap: HTTP {response.status}"
                        logger.error(error_msg)
                        self.errors.append({
                            'timestamp': datetime.now().isoformat(),
                            'error': error_msg,
                            'url': self.sitemap_url
                        })
                        return None
                        
        except Exception as e:
            error_msg = f"Exception fetching sitemap: {str(e)}"
            logger.error(error_msg)
            self.errors.append({
                'timestamp': datetime.now().isoformat(),
                'error': error_msg,
                'url': self.sitemap_url
            })
            return None
    
    def parse_sitemap(self, sitemap_xml: str) -> List[Dict[str, str]]:
        """Parse sitemap XML to extract workflow information."""
        workflows = []
        
        try:
            logger.info("Parsing sitemap XML...")
            
            # Parse XML
            root = ET.fromstring(sitemap_xml)
            
            # XML namespace for sitemap
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Find all URL entries
            url_elements = root.findall('.//ns:url', namespace)
            logger.info(f"Found {len(url_elements)} URL entries in sitemap")
            
            for url_element in url_elements:
                loc = url_element.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    url = loc.text.strip()
                    
                    # Extract workflow ID and title from URL
                    # Format: https://n8n.io/workflows/1234-workflow-title-here/
                    match = re.match(r'https://n8n\.io/workflows/(\d+)-(.*?)/?$', url)
                    
                    if match:
                        workflow_id = match.group(1)
                        title_slug = match.group(2)
                        
                        # Convert slug to title (basic conversion)
                        title = title_slug.replace('-', ' ').title()
                        
                        workflows.append({
                            'workflow_id': workflow_id,
                            'title': title,
                            'url': url.rstrip('/'),  # Remove trailing slash
                            'discovered_date': datetime.now().isoformat()
                        })
            
            self.workflows_discovered = len(workflows)
            logger.info(f"Successfully parsed {self.workflows_discovered} workflows from sitemap")
            
            return workflows
            
        except Exception as e:
            error_msg = f"Error parsing sitemap: {str(e)}"
            logger.error(error_msg)
            self.errors.append({
                'timestamp': datetime.now().isoformat(),
                'error': error_msg,
                'context': 'sitemap_parsing'
            })
            return []
    
    async def build_inventory(self) -> Dict[str, any]:
        """Build complete workflow inventory from sitemap."""
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("SCRAPE-002B: Building Complete Workflow Inventory")
        logger.info(f"Start Time: {start_time.isoformat()}")
        logger.info("=" * 80)
        
        # Fetch sitemap
        sitemap_xml = await self.fetch_sitemap()
        if not sitemap_xml:
            logger.error("Failed to fetch sitemap - aborting inventory build")
            return {
                'success': False,
                'error': 'Failed to fetch sitemap',
                'workflows': [],
                'total_discovered': 0
            }
        
        # Parse sitemap to extract workflows
        workflows = self.parse_sitemap(sitemap_xml)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info(f"Inventory Build Complete!")
        logger.info(f"Total Workflows Discovered: {len(workflows)}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Errors: {len(self.errors)}")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'workflows': workflows,
            'total_discovered': len(workflows),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'errors': self.errors
        }


async def main():
    """Main function for testing."""
    crawler = WorkflowInventoryCrawler()
    result = await crawler.build_inventory()
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Discovered {result['total_discovered']} workflows")
        print(f"Duration: {result['duration_seconds']:.2f} seconds")
        
        # Show first 10 workflows
        print("\nFirst 10 workflows:")
        for wf in result['workflows'][:10]:
            print(f"  - {wf['workflow_id']}: {wf['title']}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())

