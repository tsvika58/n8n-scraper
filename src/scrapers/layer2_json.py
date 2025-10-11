"""
Layer 2: Workflow JSON Extractor - SCRAPE-003
Extracts complete workflow JSON structure from n8n.io using official API
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Optional, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowJSONExtractor:
    """Extracts complete workflow JSON from n8n.io using official API with fallback."""
    
    def __init__(self):
        """Initialize the JSON extractor."""
        self.api_base = "https://api.n8n.io/api/workflows/templates"
        self.fallback_api_base = "https://n8n.io/api/workflows/by-id"
        self.extraction_count = 0
        self.fallback_count = 0
        self.statistics = {
            'total': 0,
            'primary_success': 0,
            'fallback_success': 0,
            'both_failed': 0
        }
        logger.info("Layer 2 JSON Extractor initialized (with fallback support)")
    
    async def extract(self, workflow_id: str) -> Dict[str, Any]:
        """
        Extract complete workflow JSON for a given workflow ID.
        
        Args:
            workflow_id: The n8n.io workflow ID to extract
            
        Returns:
            dict with keys:
                - success: bool
                - workflow_id: str
                - data: dict (workflow JSON if successful)
                - node_count: int
                - connection_count: int
                - extraction_time: float
                - error: str or None
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Extracting workflow JSON for ID: {workflow_id}")
            
            # Construct API URL
            api_url = f"{self.api_base}/{workflow_id}"
            
            # Fetch workflow JSON from API
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        # Parse JSON response
                        workflow_data = await response.json()
                        
                        # Validate structure
                        if not self._validate_json_structure(workflow_data):
                            logger.warning(f"Invalid JSON structure for workflow {workflow_id}")
                            return {
                                'success': False,
                                'workflow_id': workflow_id,
                                'data': None,
                                'node_count': 0,
                                'connection_count': 0,
                                'extraction_time': (datetime.now() - start_time).total_seconds(),
                                'error': 'Invalid JSON structure'
                            }
                        
                        # Extract metrics
                        workflow = workflow_data.get('workflow', {})
                        nodes = workflow.get('nodes', [])
                        connections = workflow.get('connections', {})
                        
                        node_count = len(nodes)
                        connection_count = sum(len(v) for v in connections.values()) if isinstance(connections, dict) else 0
                        
                        # Track extraction
                        self.extraction_count += 1
                        self.statistics['total'] += 1
                        self.statistics['primary_success'] += 1
                        extraction_time = (datetime.now() - start_time).total_seconds()
                        
                        logger.info(f"✅ Successfully extracted workflow {workflow_id}: "
                                  f"{node_count} nodes, {connection_count} connections, "
                                  f"{extraction_time:.2f}s")
                        
                        return {
                            'success': True,
                            'workflow_id': workflow_id,
                            'data': workflow_data,
                            'node_count': node_count,
                            'connection_count': connection_count,
                            'extraction_time': extraction_time,
                            'error': None,
                            'fallback_used': False,
                            'extraction_type': 'full',
                            'source': 'primary_api'
                        }
                    
                    elif response.status == 404:
                        logger.warning(f"Primary API 404 for workflow {workflow_id}, trying fallback...")
                        
                        # Try fallback API
                        fallback_result = await self._extract_from_fallback_api(workflow_id, start_time)
                        return fallback_result
                    
                    else:
                        logger.error(f"HTTP {response.status} for workflow {workflow_id}")
                        return {
                            'success': False,
                            'workflow_id': workflow_id,
                            'data': None,
                            'node_count': 0,
                            'connection_count': 0,
                            'extraction_time': (datetime.now() - start_time).total_seconds(),
                            'error': f'HTTP {response.status}'
                        }
        
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout extracting workflow {workflow_id}: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'data': None,
                'node_count': 0,
                'connection_count': 0,
                'extraction_time': (datetime.now() - start_time).total_seconds(),
                'error': f'Timeout: {str(e)}'
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for workflow {workflow_id}: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'data': None,
                'node_count': 0,
                'connection_count': 0,
                'extraction_time': (datetime.now() - start_time).total_seconds(),
                'error': f'JSON decode error: {str(e)}'
            }
        
        except Exception as e:
            logger.error(f"Error extracting workflow {workflow_id}: {e}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'data': None,
                'node_count': 0,
                'connection_count': 0,
                'extraction_time': (datetime.now() - start_time).total_seconds(),
                'error': str(e)
            }
    
    async def _extract_from_fallback_api(self, workflow_id: str, start_time: datetime) -> Dict[str, Any]:
        """
        Extract workflow data from fallback by-id endpoint.
        
        This fallback is used when the primary API returns 404.
        Returns partial data (node types, metadata) without full configurations.
        
        Args:
            workflow_id: The n8n.io workflow ID
            start_time: Original extraction start time for metrics
            
        Returns:
            dict with workflow data (partial) or error
        """
        try:
            fallback_url = f"{self.fallback_api_base}/{workflow_id}"
            logger.info(f"Trying fallback API: {fallback_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(fallback_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        # Parse fallback API response
                        fallback_data = await response.json()
                        
                        # Transform to template format
                        transformed_data = self._transform_by_id_to_template(fallback_data)
                        
                        # Extract metrics
                        workflow = transformed_data.get('workflow', {})
                        nodes = workflow.get('nodes', [])
                        connections = workflow.get('connections', {})
                        
                        node_count = len(nodes)
                        connection_count = sum(len(v) for v in connections.values()) if isinstance(connections, dict) else 0
                        
                        extraction_time = (datetime.now() - start_time).total_seconds()
                        
                        # Update statistics
                        self.fallback_count += 1
                        self.statistics['fallback_success'] += 1
                        
                        logger.info(f"✅ Fallback succeeded for {workflow_id}: "
                                  f"{node_count} nodes (partial data), {extraction_time:.2f}s")
                        
                        return {
                            'success': True,
                            'workflow_id': workflow_id,
                            'data': transformed_data,
                            'node_count': node_count,
                            'connection_count': connection_count,
                            'extraction_time': extraction_time,
                            'error': None,
                            'fallback_used': True,
                            'extraction_type': 'partial',
                            'source': 'by_id_api'
                        }
                    
                    elif response.status == 204:
                        # No content - workflow truly unavailable
                        logger.warning(f"Fallback API: Workflow {workflow_id} returns 204 (deleted/private)")
                        extraction_time = (datetime.now() - start_time).total_seconds()
                        
                        self.statistics['both_failed'] += 1
                        
                        return {
                            'success': False,
                            'workflow_id': workflow_id,
                            'data': None,
                            'node_count': 0,
                            'connection_count': 0,
                            'extraction_time': extraction_time,
                            'error': 'Workflow unavailable (both APIs failed - HTTP 204)',
                            'fallback_used': True,
                            'fallback_status': 204
                        }
                    
                    else:
                        logger.error(f"Fallback API HTTP {response.status} for workflow {workflow_id}")
                        extraction_time = (datetime.now() - start_time).total_seconds()
                        
                        self.statistics['both_failed'] += 1
                        
                        return {
                            'success': False,
                            'workflow_id': workflow_id,
                            'data': None,
                            'node_count': 0,
                            'connection_count': 0,
                            'extraction_time': extraction_time,
                            'error': f'Both APIs failed (primary: 404, fallback: {response.status})',
                            'fallback_used': True,
                            'fallback_status': response.status
                        }
        
        except Exception as e:
            logger.error(f"Fallback API error for workflow {workflow_id}: {e}")
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            self.statistics['both_failed'] += 1
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'data': None,
                'node_count': 0,
                'connection_count': 0,
                'extraction_time': extraction_time,
                'error': f'Both APIs failed (primary: 404, fallback: {str(e)})',
                'fallback_used': True
            }
    
    def _transform_by_id_to_template(self, by_id_data: Dict) -> Dict[str, Any]:
        """
        Transform by-id API format to template API format.
        
        Creates synthetic workflow structure from node metadata.
        Note: This produces PARTIAL data - node configs and connections are not available.
        
        Args:
            by_id_data: Response from /api/workflows/by-id/{id}
            
        Returns:
            dict: Workflow data in template format with _metadata.limitations
        """
        # Extract node metadata
        node_objects = by_id_data.get('nodes', [])
        
        # Transform nodes from {id, url} to full node structure
        synthetic_nodes = []
        for i, node_obj in enumerate(node_objects):
            # Extract node type from URL
            # Example: "/integrations/if/" -> "if"
            node_url = node_obj.get('url', '')
            node_type = self._extract_node_type_from_url(node_url)
            
            # Create synthetic node
            synthetic_node = {
                'id': f"synthetic_{i}",
                'name': node_type.replace('-', ' ').title() if node_type else f"Node {i}",
                'type': f"n8n-nodes-base.{node_type}" if node_type else "unknown",
                'typeVersion': 1,
                'position': [100 + (i * 200), 100],  # Synthetic positions
                'parameters': {},  # Empty - not available from by-id API
                'synthetic': True,  # Mark as synthetic
                'original_url': node_url
            }
            synthetic_nodes.append(synthetic_node)
        
        # Build template-compatible structure
        transformed = {
            'id': by_id_data.get('id'),
            'name': by_id_data.get('name', ''),
            'workflow': {
                'nodes': synthetic_nodes,
                'connections': {},  # Empty - not available from by-id API
                'settings': {},
                'staticData': None
            },
            'description': by_id_data.get('description', ''),
            'user': by_id_data.get('user', {}),
            'categories': by_id_data.get('categories', []),
            'views': by_id_data.get('views', 0),
            'usedCredentials': by_id_data.get('usedCredentials', []),
            'communityNodes': by_id_data.get('communityNodes', []),
            '_metadata': {
                'extraction_type': 'partial',
                'source': 'by_id_api',
                'limitations': [
                    'Node configurations (parameters) unavailable',
                    'Connection mappings unavailable',
                    'Node positions are synthetic',
                    'Node IDs are synthetic',
                    'Only node types extracted from URLs'
                ],
                'transformed_at': datetime.now().isoformat(),
                'original_node_count': len(node_objects),
                'synthetic_node_count': len(synthetic_nodes)
            }
        }
        
        return transformed
    
    def _extract_node_type_from_url(self, url: str) -> Optional[str]:
        """
        Extract node type from integration URL.
        
        Examples:
            "/integrations/if/" -> "if"
            "/integrations/http-request/" -> "httpRequest"
            "/integrations/google-calendar/" -> "googleCalendar"
        
        Args:
            url: Integration URL (e.g., "/integrations/if/")
            
        Returns:
            str: Node type or None
        """
        if not url:
            return None
        
        # Extract path between /integrations/ and trailing /
        # Format: /integrations/{node-type}/
        parts = url.strip('/').split('/')
        
        if len(parts) >= 2 and parts[0] == 'integrations':
            node_slug = parts[1]
            
            # Convert kebab-case to camelCase for n8n node types
            # Example: "http-request" -> "httpRequest"
            if '-' in node_slug:
                parts = node_slug.split('-')
                camel_case = parts[0] + ''.join(p.capitalize() for p in parts[1:])
                return camel_case
            else:
                return node_slug
        
        return None
    
    def _validate_json_structure(self, data: Dict) -> bool:
        """
        Validate that extracted JSON has expected n8n workflow structure.
        
        Args:
            data: The workflow JSON data to validate
            
        Returns:
            bool: True if valid structure, False otherwise
        """
        try:
            # Must have 'workflow' key
            if 'workflow' not in data:
                logger.warning("Missing 'workflow' key")
                return False
            
            workflow = data['workflow']
            
            # Must have 'nodes' key
            if 'nodes' not in workflow:
                logger.warning("Missing 'nodes' key in workflow")
                return False
            
            # Nodes must be a list
            if not isinstance(workflow['nodes'], list):
                logger.warning("'nodes' is not a list")
                return False
            
            # Must have 'connections' key
            if 'connections' not in workflow:
                logger.warning("Missing 'connections' key in workflow")
                return False
            
            # Valid structure
            return True
            
        except Exception as e:
            logger.error(f"Error validating JSON structure: {e}")
            return False
    
    async def extract_batch(self, workflow_ids: list, rate_limit_seconds: float = 2.0) -> Dict[str, Any]:
        """
        Extract JSON for multiple workflows with rate limiting.
        
        Args:
            workflow_ids: List of workflow IDs to extract
            rate_limit_seconds: Delay between extractions (default: 2s)
            
        Returns:
            dict with:
                - total_attempted: int
                - successful: int
                - failed: int
                - success_rate: float
                - extractions: list of results
                - total_time: float
        """
        start_time = datetime.now()
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch extraction of {len(workflow_ids)} workflows")
        
        for i, workflow_id in enumerate(workflow_ids):
            # Extract workflow
            result = await self.extract(workflow_id)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
            
            # Progress logging
            if (i + 1) % 5 == 0:
                logger.info(f"Progress: {i+1}/{len(workflow_ids)} workflows extracted "
                          f"({successful} success, {failed} failed)")
            
            # Rate limiting (except for last workflow)
            if i < len(workflow_ids) - 1:
                await asyncio.sleep(rate_limit_seconds)
        
        total_time = (datetime.now() - start_time).total_seconds()
        success_rate = (successful / len(workflow_ids) * 100) if workflow_ids else 0
        
        logger.info(f"✅ Batch extraction complete: {successful}/{len(workflow_ids)} successful "
                   f"({success_rate:.1f}%), {total_time:.2f}s total")
        
        return {
            'total_attempted': len(workflow_ids),
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'extractions': results,
            'total_time': total_time,
            'average_time': total_time / len(workflow_ids) if workflow_ids else 0
        }


async def main():
    """Test extraction on a single workflow."""
    extractor = WorkflowJSONExtractor()
    
    # Test with workflow 1954
    print("\n🧪 Testing Layer 2 JSON extraction...")
    result = await extractor.extract("1954")
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Nodes: {result['node_count']}")
        print(f"Connections: {result['connection_count']}")
        print(f"Extraction Time: {result['extraction_time']:.2f}s")
        print(f"\nWorkflow Name: {result['data']['name']}")
        print(f"First node: {result['data']['workflow']['nodes'][0]['name']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())


