"""
Storage adapter for Layer 2 Enhanced data.

Handles storing complete workflow data including iframe extraction
from all 4 phases into the workflow_structure table.

Author: Developer-2
Date: October 13, 2025
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from src.storage.database import get_session
from src.storage.models import WorkflowStructure


class Layer2EnhancedStorage:
    """
    Storage handler for Layer 2 Enhanced extraction results.
    
    Stores:
    - API data (workflow JSON, nodes, connections)
    - Phase 1: Node metadata from iframe
    - Phase 2: Visual layout (positions, canvas, spatial metrics)
    - Phase 3: Enhanced text content
    - Phase 4: Media content
    """
    
    def __init__(self, session=None):
        """Initialize storage handler."""
        self.session = session
        self._owns_session = session is None
    
    def _get_session(self):
        """Get database session."""
        if self.session:
            return self.session
        from src.storage.database import SessionLocal
        return SessionLocal()
    
    def store_extraction_result(
        self,
        workflow_id: str,
        extraction_result: Dict[str, Any]
    ) -> bool:
        """
        Store complete Layer 2 Enhanced extraction result.
        
        Args:
            workflow_id: Workflow ID
            extraction_result: Complete extraction result from EnhancedLayer2Extractor
            
        Returns:
            bool: True if successful, False otherwise
            
        Example extraction_result structure:
        {
            'workflow_id': '2462',
            'url': 'https://n8n.io/workflows/2462',
            'extraction_time': 25.04,
            'sources': {
                'api': {...},
                'iframe': {...}
            },
            'merged': {...},
            'completeness': {...}
        }
        """
        session = self._get_session()
        
        try:
            # Extract data from result
            api_data = extraction_result['sources']['api']
            iframe_data = extraction_result['sources']['iframe']
            completeness = extraction_result['completeness']
            
            # Check if structure already exists
            existing = session.query(WorkflowStructure).filter(
                WorkflowStructure.workflow_id == workflow_id
            ).first()
            
            if existing:
                # Update existing structure
                logger.info(f"Updating existing workflow_structure for {workflow_id}")
                self._update_structure(existing, api_data, iframe_data, completeness, extraction_result)
            else:
                # Create new structure
                logger.info(f"Creating new workflow_structure for {workflow_id}")
                structure = self._create_structure(workflow_id, api_data, iframe_data, completeness, extraction_result)
                session.add(structure)
            
            # Commit if we own the session
            if self._owns_session:
                session.commit()
            
            logger.info(f"✅ Stored Layer 2 Enhanced data for workflow {workflow_id}")
            return True
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"❌ Error storing Layer 2 Enhanced data for {workflow_id}: {e}")
            return False
        
        finally:
            if self._owns_session:
                session.close()
    
    def _create_structure(
        self,
        workflow_id: str,
        api_data: Dict,
        iframe_data: Dict,
        completeness: Dict,
        extraction_result: Dict
    ) -> WorkflowStructure:
        """Create new WorkflowStructure record."""
        
        return WorkflowStructure(
            workflow_id=workflow_id,
            
            # API data (existing fields)
            node_count=api_data.get('node_count'),
            connection_count=api_data.get('connection_count'),
            node_types=self._extract_node_types(api_data),
            extraction_type=api_data.get('extraction_type', 'full'),
            fallback_used=api_data.get('fallback_used', False),
            workflow_json=api_data.get('data'),
            
            # NEW: Iframe data (Phase 1-4)
            iframe_data=self._prepare_iframe_data(iframe_data),
            visual_layout=iframe_data.get('visual_layout'),
            enhanced_content=iframe_data.get('enhanced_content'),
            media_content=iframe_data.get('media_content'),
            
            # NEW: Extraction metadata
            extraction_sources=self._prepare_extraction_sources(api_data, iframe_data, extraction_result),
            completeness_metrics=completeness,
            
            # Timestamp
            extracted_at=datetime.utcnow()
        )
    
    def _update_structure(
        self,
        existing: WorkflowStructure,
        api_data: Dict,
        iframe_data: Dict,
        completeness: Dict,
        extraction_result: Dict
    ):
        """Update existing WorkflowStructure record."""
        
        # Update API data
        existing.node_count = api_data.get('node_count')
        existing.connection_count = api_data.get('connection_count')
        existing.node_types = self._extract_node_types(api_data)
        existing.extraction_type = api_data.get('extraction_type', 'full')
        existing.fallback_used = api_data.get('fallback_used', False)
        existing.workflow_json = api_data.get('data')
        
        # Update iframe data
        existing.iframe_data = self._prepare_iframe_data(iframe_data)
        existing.visual_layout = iframe_data.get('visual_layout')
        existing.enhanced_content = iframe_data.get('enhanced_content')
        existing.media_content = iframe_data.get('media_content')
        
        # Update metadata
        existing.extraction_sources = self._prepare_extraction_sources(api_data, iframe_data, extraction_result)
        existing.completeness_metrics = completeness
        existing.extracted_at = datetime.utcnow()
    
    def _prepare_iframe_data(self, iframe_data: Dict) -> Optional[Dict]:
        """
        Prepare iframe data for storage (Phase 1 data).
        
        Includes:
        - nodes (node metadata)
        - text_content (basic text)
        - images (node icons)
        """
        if not iframe_data.get('success'):
            return None
        
        return {
            'success': iframe_data.get('success'),
            'source': iframe_data.get('source'),
            'nodes': iframe_data.get('nodes', []),
            'text_content': iframe_data.get('text_content', {}),
            'images': iframe_data.get('images', []),
            'node_count': iframe_data.get('node_count', 0),
            'extraction_count': iframe_data.get('extraction_count', 0)
        }
    
    def _prepare_extraction_sources(
        self,
        api_data: Dict,
        iframe_data: Dict,
        extraction_result: Dict
    ) -> Dict:
        """Prepare extraction source tracking data."""
        
        return {
            'api': {
                'success': api_data.get('success', False),
                'extraction_time': api_data.get('extraction_time', 0),
                'source': api_data.get('source', 'primary_api'),
                'fallback_used': api_data.get('fallback_used', False)
            },
            'iframe': {
                'success': iframe_data.get('success', False),
                'extraction_time': extraction_result.get('extraction_time', 0) - api_data.get('extraction_time', 0),
                'source': 'demo_iframe'
            },
            'total_extraction_time': extraction_result.get('extraction_time', 0)
        }
    
    def _extract_node_types(self, api_data: Dict) -> list:
        """Extract list of node types from API data."""
        if not api_data.get('success') or not api_data.get('data'):
            return []
        
        workflow = api_data.get('data', {}).get('workflow', {})
        nodes = workflow.get('nodes', [])
        
        # Extract unique node types
        node_types = list(set(node.get('type') for node in nodes if node.get('type')))
        return node_types
    
    def get_workflow_structure(self, workflow_id: str) -> Optional[WorkflowStructure]:
        """
        Get workflow structure by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            WorkflowStructure or None
        """
        session = self._get_session()
        
        try:
            structure = session.query(WorkflowStructure).filter(
                WorkflowStructure.workflow_id == workflow_id
            ).first()
            
            return structure
            
        finally:
            if self._owns_session:
                session.close()
    
    def get_completeness_stats(self) -> Dict[str, Any]:
        """
        Get completeness statistics across all workflows.
        
        Returns:
            dict with completeness metrics
        """
        session = self._get_session()
        
        try:
            from sqlalchemy import func
            
            # Count workflows with each data type
            total = session.query(func.count(WorkflowStructure.id)).scalar() or 0
            
            api_only = session.query(func.count(WorkflowStructure.id)).filter(
                WorkflowStructure.workflow_json.isnot(None),
                WorkflowStructure.iframe_data.is_(None)
            ).scalar() or 0
            
            with_iframe = session.query(func.count(WorkflowStructure.id)).filter(
                WorkflowStructure.iframe_data.isnot(None)
            ).scalar() or 0
            
            complete = session.query(func.count(WorkflowStructure.id)).filter(
                WorkflowStructure.workflow_json.isnot(None),
                WorkflowStructure.iframe_data.isnot(None)
            ).scalar() or 0
            
            return {
                'total_workflows': total,
                'api_only': api_only,
                'with_iframe': with_iframe,
                'complete': complete,
                'api_only_percentage': (api_only / total * 100) if total > 0 else 0,
                'with_iframe_percentage': (with_iframe / total * 100) if total > 0 else 0,
                'complete_percentage': (complete / total * 100) if total > 0 else 0
            }
            
        finally:
            if self._owns_session:
                session.close()


# Example usage
async def example_usage():
    """Example of storing Layer 2 Enhanced data."""
    
    from src.scrapers.layer2_enhanced import EnhancedLayer2Extractor
    
    workflow_id = "2462"
    workflow_url = "https://n8n.io/workflows/2462"
    
    # Extract data
    async with EnhancedLayer2Extractor() as extractor:
        result = await extractor.extract_complete(workflow_id, workflow_url)
    
    # Store data
    storage = Layer2EnhancedStorage()
    success = storage.store_extraction_result(workflow_id, result)
    
    if success:
        print(f"✅ Stored workflow {workflow_id}")
        
        # Get completeness stats
        stats = storage.get_completeness_stats()
        print(f"📊 Completeness Stats: {stats}")
    else:
        print(f"❌ Failed to store workflow {workflow_id}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())


