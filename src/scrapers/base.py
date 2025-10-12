"""
Base extractor class for all scraping layers.

Provides common functionality and interface for all extractors.

Author: RND Team - Comprehensive Scraping Expansion
Date: October 12, 2025
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import time

from src.utils.logging import logger


class BaseExtractor(ABC):
    """
    Base class for all workflow extractors.
    
    Provides common functionality and enforces consistent interface
    across all extraction layers.
    """
    
    def __init__(self, layer_name: str):
        """
        Initialize the base extractor.
        
        Args:
            layer_name: Name of the extraction layer (e.g., "Layer 4")
        """
        self.layer_name = layer_name
        self.extraction_count = 0
        logger.info(f"{self.layer_name} extractor initialized")
    
    @abstractmethod
    async def extract(self, workflow_data: Dict[str, Any]) -> Dict:
        """
        Extract data for this layer.
        
        Args:
            workflow_id: The workflow ID
            workflow_data: Cumulative workflow data from previous layers
            
        Returns:
            Dict containing:
            - success: bool - Whether extraction succeeded
            - workflow_id: str - The workflow ID
            - data: Dict - Extracted data for this layer
            - extraction_time: float - Time taken for extraction
            - error: str - Error message if extraction failed
        """
        pass
    
    def _create_result(self, workflow_id: str, success: bool, data: Dict = None, 
                      extraction_time: float = 0.0, error: str = None) -> Dict:
        """
        Create a standardized result dictionary.
        
        Args:
            workflow_id: The workflow ID
            success: Whether extraction succeeded
            data: Extracted data (if successful)
            extraction_time: Time taken for extraction
            error: Error message (if failed)
            
        Returns:
            Standardized result dictionary
        """
        return {
            'success': success,
            'workflow_id': workflow_id,
            'data': data or {},
            'extraction_time': extraction_time,
            'error': error
        }
    
    def _measure_time(self, func):
        """Decorator to measure extraction time."""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                extraction_time = end_time - start_time
                
                # Add extraction time to result
                if isinstance(result, dict):
                    result['extraction_time'] = extraction_time
                
                self.extraction_count += 1
                logger.info(f"{self.layer_name} extraction completed in {extraction_time:.2f}s")
                
                return result
            except Exception as e:
                end_time = time.time()
                extraction_time = end_time - start_time
                logger.error(f"{self.layer_name} extraction failed after {extraction_time:.2f}s: {e}")
                raise
        
        return wrapper
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extractor statistics."""
        return {
            'layer_name': self.layer_name,
            'extraction_count': self.extraction_count
        }
