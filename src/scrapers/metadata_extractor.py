"""
Metadata-Only Extractor for Phase 1 Smart Filtering

This module provides fast metadata extraction (Layers 1-2 only) for intelligent
workflow prioritization. Extracts essential data in ~0.5 seconds per workflow.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .layer1_metadata import PageMetadataExtractor
from .layer2_json import WorkflowJSONExtractor
from .value_scorer import WorkflowValueScorer


logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Fast metadata-only extractor for Phase 1 smart filtering.
    
    Extracts only essential metadata (Layers 1-2) to enable rapid
    value scoring and prioritization of all 6,022 workflows.
    """
    
    def __init__(self):
        self.layer1_extractor = PageMetadataExtractor()
        self.layer2_extractor = WorkflowJSONExtractor()
        self.value_scorer = WorkflowValueScorer()
    
    async def extract_metadata(self, workflow_id: str, url: str) -> Dict[str, Any]:
        """
        Extract essential metadata for a workflow (Layers 1-2 only).
        
        Args:
            workflow_id: Unique workflow identifier
            url: Workflow URL to extract from
            
        Returns:
            Dictionary containing metadata and value score
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🔍 Extracting metadata for workflow {workflow_id}")
            
            # Initialize result structure
            result = {
                'workflow_id': workflow_id,
                'url': url,
                'extraction_mode': 'metadata_only',
                'layers': {},
                'value_score': None,
                'extraction_time': 0.0,
                'success': False,
                'error': None
            }
            
            # LAYER 1: Extract basic metadata
            logger.debug(f"Phase 1: Extracting Layer 1 metadata for {workflow_id}")
            layer1_result = await self.layer1_extractor.extract(workflow_id, url)
            result['layers']['layer1'] = layer1_result
            
            if not layer1_result.get('success'):
                result['error'] = f"Layer 1 failed: {layer1_result.get('error')}"
                return result
            
            # LAYER 2: Extract structure (node count for complexity scoring)
            logger.debug(f"Phase 2: Extracting Layer 2 structure for {workflow_id}")
            layer2_result = await self.layer2_extractor.extract(workflow_id)
            result['layers']['layer2'] = layer2_result
            
            if not layer2_result.get('success'):
                logger.warning(f"Layer 2 failed for {workflow_id}, continuing with Layer 1 data")
                # Layer 2 failure is not critical for metadata extraction
            
            # Combine data for value scoring
            metadata_data = self._combine_metadata(layer1_result, layer2_result)
            
            # Calculate value score
            logger.debug(f"Calculating value score for {workflow_id}")
            value_score = self.value_scorer.calculate_score(metadata_data)
            result['value_score'] = value_score
            
            # Calculate extraction time
            extraction_time = (datetime.now() - start_time).total_seconds()
            result['extraction_time'] = round(extraction_time, 2)
            result['success'] = True
            
            logger.info(f"✅ Metadata extraction complete for {workflow_id}: {extraction_time:.2f}s, Score: {value_score['total_score']}")
            
            return result
            
        except Exception as e:
            extraction_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Metadata extraction failed for {workflow_id}: {e}")
            
            return {
                'workflow_id': workflow_id,
                'url': url,
                'extraction_mode': 'metadata_only',
                'layers': {},
                'value_score': None,
                'extraction_time': round(extraction_time, 2),
                'success': False,
                'error': str(e)
            }
    
    def _combine_metadata(self, layer1_result: Dict[str, Any], layer2_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine Layer 1 and Layer 2 results into a unified metadata structure.
        
        Args:
            layer1_result: Layer 1 extraction result
            layer2_result: Layer 2 extraction result
            
        Returns:
            Combined metadata dictionary for value scoring
        """
        try:
            # Start with Layer 1 data
            metadata = layer1_result.get('data', {}).copy()
            
            # Add Layer 2 data if available
            if layer2_result.get('success'):
                layer2_data = layer2_result.get('data', {})
                
                # Extract node count for complexity scoring
                nodes = layer2_data.get('nodes', [])
                metadata['node_count'] = len(nodes) if isinstance(nodes, list) else 0
                
                # Extract workflow structure info
                metadata['workflow_type'] = layer2_data.get('workflow_type', 'unknown')
                metadata['has_connections'] = len(layer2_data.get('connections', [])) > 0
            
            # Ensure required fields exist
            metadata.setdefault('views', 0)
            metadata.setdefault('shares', 0)
            metadata.setdefault('upvotes', 0)
            metadata.setdefault('node_count', 0)
            metadata.setdefault('categories', [])
            metadata.setdefault('title', '')
            metadata.setdefault('description', '')
            metadata.setdefault('use_case', '')
            metadata.setdefault('author_name', '')
            metadata.setdefault('workflow_created_at', None)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error combining metadata: {e}")
            return {
                'views': 0,
                'shares': 0,
                'upvotes': 0,
                'node_count': 0,
                'categories': [],
                'title': '',
                'description': '',
                'use_case': '',
                'author_name': '',
                'workflow_created_at': None
            }
    
    async def batch_extract_metadata(self, workflows: list, batch_size: int = 10) -> list:
        """
        Extract metadata for a batch of workflows with concurrency control.
        
        Args:
            workflows: List of workflow dictionaries with 'workflow_id' and 'url'
            batch_size: Number of concurrent extractions
            
        Returns:
            List of extraction results
        """
        try:
            logger.info(f"🚀 Starting batch metadata extraction for {len(workflows)} workflows")
            
            results = []
            
            # Process in batches to avoid overwhelming the system
            for i in range(0, len(workflows), batch_size):
                batch = workflows[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: workflows {i+1}-{min(i+batch_size, len(workflows))}")
                
                # Create tasks for concurrent execution
                tasks = [
                    self.extract_metadata(wf['workflow_id'], wf['url'])
                    for wf in batch
                ]
                
                # Execute batch concurrently
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch extraction error: {result}")
                        results.append({
                            'workflow_id': 'unknown',
                            'url': 'unknown',
                            'extraction_mode': 'metadata_only',
                            'success': False,
                            'error': str(result),
                            'extraction_time': 0.0
                        })
                    else:
                        results.append(result)
                
                # Small delay between batches to be respectful
                await asyncio.sleep(0.1)
            
            successful = sum(1 for r in results if r.get('success'))
            logger.info(f"✅ Batch metadata extraction complete: {successful}/{len(workflows)} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch metadata extraction failed: {e}")
            return []
    
    def rank_extraction_results(self, results: list) -> list:
        """
        Rank extraction results by value score.
        
        Args:
            results: List of extraction results with value scores
            
        Returns:
            List of results ranked by value score (highest first)
        """
        try:
            # Filter successful extractions
            successful_results = [r for r in results if r.get('success') and r.get('value_score')]
            
            # Sort by total value score
            ranked_results = sorted(
                successful_results,
                key=lambda x: x['value_score']['total_score'],
                reverse=True
            )
            
            logger.info(f"📊 Ranked {len(ranked_results)} workflows by value score")
            
            return ranked_results
            
        except Exception as e:
            logger.error(f"Error ranking results: {e}")
            return results
    
    def get_top_workflows(self, results: list, top_n: int = 100) -> list:
        """
        Get top N highest-value workflows from extraction results.
        
        Args:
            results: List of extraction results
            top_n: Number of top workflows to return
            
        Returns:
            List of top N workflows by value score
        """
        ranked_results = self.rank_extraction_results(results)
        return ranked_results[:top_n]
