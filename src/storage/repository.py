"""
Repository pattern for workflow data access.

Provides clean CRUD operations for workflows, abstracting
database implementation details from business logic.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from loguru import logger

from src.storage.database import get_session
from src.storage.models import (
    Workflow,
    WorkflowMetadata,
    WorkflowStructure,
    WorkflowContent,
    VideoTranscript
)


class WorkflowRepository:
    """
    Repository for workflow CRUD operations.
    
    Encapsulates all database access for workflows, providing
    a clean API for creating, reading, updating, and deleting
    workflow data across all 5 tables.
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy session (if None, creates new session per operation)
        """
        self.session = session
        self._owns_session = session is None
    
    def _get_session(self) -> Session:
        """Get session (provided or create new)."""
        if self.session:
            return self.session
        # Create a new session directly from SessionLocal
        from src.storage.database import SessionLocal
        return SessionLocal()
    
    def create_workflow(
        self,
        workflow_id: str,
        url: str,
        extraction_result: Dict[str, Any]
    ) -> Workflow:
        """
        Create a complete workflow entry with all extracted data.
        
        Args:
            workflow_id: Unique n8n.io workflow ID
            url: Workflow URL
            extraction_result: Complete E2E pipeline result
        
        Returns:
            Workflow: Created workflow object with all relationships
        
        Example:
            result = await pipeline.process_workflow('2462', 'https://n8n.io/workflows/2462')
            workflow = repo.create_workflow('2462', result['url'], result)
        """
        session = self._get_session()
        
        try:
            # Check if workflow already exists
            existing_workflow = session.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
            
            if existing_workflow:
                # Update existing workflow
                existing_workflow.url = url
                existing_workflow.processing_time = extraction_result.get('extraction_time')  # Fixed: was 'processing_time'
                existing_workflow.quality_score = extraction_result.get('quality', {}).get('overall_score')  # Fixed: was 'quality_score'
                existing_workflow.layer1_success = extraction_result.get('layers', {}).get('layer1', {}).get('success', False)
                existing_workflow.layer2_success = extraction_result.get('layers', {}).get('layer2', {}).get('success', False)
                existing_workflow.layer3_success = extraction_result.get('layers', {}).get('layer3', {}).get('success', False)
                existing_workflow.last_scraped_at = extraction_result.get('extracted_at')
                workflow = existing_workflow
                logger.info(f"Updated existing workflow: {workflow_id}")
            else:
                # Create new workflow record
                workflow = Workflow(
                    workflow_id=workflow_id,
                    url=url,
                    processing_time=extraction_result.get('extraction_time'),  # Fixed: was 'processing_time'
                    quality_score=extraction_result.get('quality', {}).get('overall_score'),  # Fixed: was 'quality_score'
                    layer1_success=extraction_result.get('layers', {}).get('layer1', {}).get('success', False),
                    layer2_success=extraction_result.get('layers', {}).get('layer2', {}).get('success', False),
                    layer3_success=extraction_result.get('layers', {}).get('layer3', {}).get('success', False),
                )
                session.add(workflow)
                logger.info(f"Created new workflow: {workflow_id}")
            
            # Add Layer 1 (Metadata)
            layer1_data = extraction_result.get('layers', {}).get('layer1', {})
            if layer1_data.get('success'):
                # Check if metadata already exists
                existing_metadata = session.query(WorkflowMetadata).filter(WorkflowMetadata.workflow_id == workflow_id).first()
                if existing_metadata:
                    # Update existing metadata
                    existing_metadata.title = layer1_data.get('title')
                    existing_metadata.description = layer1_data.get('description')
                    existing_metadata.use_case = layer1_data.get('use_case')
                    existing_metadata.author_name = layer1_data.get('author', {}).get('name')
                    existing_metadata.author_url = layer1_data.get('author', {}).get('url')
                    existing_metadata.views = layer1_data.get('views')
                    existing_metadata.shares = layer1_data.get('shares')
                    existing_metadata.categories = layer1_data.get('categories', [])
                    existing_metadata.tags = layer1_data.get('tags', [])
                    existing_metadata.workflow_created_at = layer1_data.get('created_at')
                    existing_metadata.workflow_updated_at = layer1_data.get('updated_at')
                    existing_metadata.raw_metadata = layer1_data
                else:
                    # Create new metadata
                    metadata = WorkflowMetadata(
                        workflow_id=workflow_id,
                        title=layer1_data.get('title'),
                        description=layer1_data.get('description'),
                        use_case=layer1_data.get('use_case'),
                        author_name=layer1_data.get('author', {}).get('name'),
                        author_url=layer1_data.get('author', {}).get('url'),
                        views=layer1_data.get('views'),
                        shares=layer1_data.get('shares'),
                        categories=layer1_data.get('categories', []),
                        tags=layer1_data.get('tags', []),
                        workflow_created_at=layer1_data.get('created_at'),
                        workflow_updated_at=layer1_data.get('updated_at'),
                        raw_metadata=layer1_data
                    )
                    session.add(metadata)
            
            # Add Layer 2 (Structure)
            layer2_data = extraction_result.get('layers', {}).get('layer2', {})
            if layer2_data.get('success'):
                # Check if structure already exists
                existing_structure = session.query(WorkflowStructure).filter(WorkflowStructure.workflow_id == workflow_id).first()
                if existing_structure:
                    # Update existing structure
                    existing_structure.node_count = layer2_data.get('node_count')
                    existing_structure.connection_count = layer2_data.get('connection_count')
                    existing_structure.node_types = layer2_data.get('node_types', [])
                    existing_structure.extraction_type = layer2_data.get('extraction_type', 'full')
                    existing_structure.fallback_used = layer2_data.get('fallback_used', False)
                    existing_structure.workflow_json = layer2_data.get('data')
                else:
                    # Create new structure
                    structure = WorkflowStructure(
                        workflow_id=workflow_id,
                        node_count=layer2_data.get('node_count'),
                        connection_count=layer2_data.get('connection_count'),
                        node_types=layer2_data.get('node_types', []),
                        extraction_type=layer2_data.get('extraction_type', 'full'),
                        fallback_used=layer2_data.get('fallback_used', False),
                        workflow_json=layer2_data.get('data')
                    )
                    session.add(structure)
            
            # Add Layer 3 (Content)
            layer3_data = extraction_result.get('layers', {}).get('layer3', {})
            if layer3_data.get('success'):
                # Check if content already exists
                existing_content = session.query(WorkflowContent).filter(WorkflowContent.workflow_id == workflow_id).first()
                if existing_content:
                    # Update existing content
                    existing_content.explainer_text = layer3_data.get('explainer_text')
                    existing_content.explainer_html = layer3_data.get('explainer_html')
                    existing_content.setup_instructions = layer3_data.get('setup_instructions')
                    existing_content.use_instructions = layer3_data.get('use_instructions')
                    existing_content.has_videos = layer3_data.get('has_videos', False)
                    existing_content.video_count = len(layer3_data.get('videos', []))
                    existing_content.has_iframes = layer3_data.get('has_iframes', False)
                    existing_content.iframe_count = layer3_data.get('iframe_count', 0)
                    existing_content.raw_content = layer3_data
                else:
                    # Create new content
                    content = WorkflowContent(
                        workflow_id=workflow_id,
                        explainer_text=layer3_data.get('explainer_text'),
                        explainer_html=layer3_data.get('explainer_html'),
                        setup_instructions=layer3_data.get('setup_instructions'),
                        use_instructions=layer3_data.get('use_instructions'),
                        has_videos=layer3_data.get('has_videos', False),
                        video_count=len(layer3_data.get('videos', [])),
                        has_iframes=layer3_data.get('has_iframes', False),
                        iframe_count=layer3_data.get('iframe_count', 0),
                        raw_content=layer3_data
                    )
                    session.add(content)
                
                # Add video transcripts
                for video in layer3_data.get('videos', []):
                    if video.get('transcript'):
                        video_url = video.get('url')
                        # Check if transcript already exists
                        existing_transcript = session.query(VideoTranscript).filter(
                            VideoTranscript.workflow_id == workflow_id,
                            VideoTranscript.video_url == video_url
                        ).first()
                        
                        if existing_transcript:
                            # Update existing transcript
                            existing_transcript.video_id = video.get('video_id')
                            existing_transcript.platform = video.get('platform', 'youtube')
                            existing_transcript.transcript_text = video.get('transcript', {}).get('text')
                            existing_transcript.transcript_json = video.get('transcript')
                            existing_transcript.duration = video.get('transcript', {}).get('duration')
                            existing_transcript.language = video.get('transcript', {}).get('language', 'en')
                        else:
                            # Create new transcript
                            transcript = VideoTranscript(
                                workflow_id=workflow_id,
                                video_url=video.get('url'),
                                video_id=video.get('video_id'),
                                platform=video.get('platform', 'youtube'),
                                transcript_text=video.get('transcript', {}).get('text'),
                                transcript_json=video.get('transcript'),
                                duration=video.get('transcript', {}).get('duration'),
                                language=video.get('transcript', {}).get('language', 'en')
                            )
                            session.add(transcript)
            
            # Commit if we own the session
            if self._owns_session:
                session.commit()
                session.refresh(workflow)
            
            logger.info(f"Created workflow: {workflow_id}")
            return workflow
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"Error creating workflow {workflow_id}: {e}")
            raise
        finally:
            if self._owns_session:
                session.close()
    
    def get_workflow(
        self,
        workflow_id: str,
        include_relationships: bool = True
    ) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: Workflow ID to retrieve
            include_relationships: If True, eagerly load all relationships
        
        Returns:
            Workflow object or None if not found
        """
        session = self._get_session()
        
        try:
            query = session.query(Workflow).filter(Workflow.workflow_id == workflow_id)
            
            if include_relationships:
                from sqlalchemy.orm import joinedload
                query = query.options(
                    joinedload(Workflow.workflow_metadata),
                    joinedload(Workflow.structure),
                    joinedload(Workflow.content),
                    joinedload(Workflow.transcripts)
                )
            
            workflow = query.first()
            return workflow
            
        finally:
            if self._owns_session:
                session.close()
    
    def list_workflows(
        self,
        offset: int = 0,
        limit: int = 100,
        order_by: str = 'extracted_at',
        order_desc: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Workflow]:
        """
        List workflows with pagination and filtering.
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by ('extracted_at', 'quality_score', 'workflow_id')
            order_desc: If True, order descending
            filters: Optional filters (layer2_success=True, min_quality=50, etc.)
        
        Returns:
            List of workflows
        """
        session = self._get_session()
        
        try:
            query = session.query(Workflow)
            
            # Apply filters
            if filters:
                if 'layer1_success' in filters:
                    query = query.filter(Workflow.layer1_success == filters['layer1_success'])
                if 'layer2_success' in filters:
                    query = query.filter(Workflow.layer2_success == filters['layer2_success'])
                if 'layer3_success' in filters:
                    query = query.filter(Workflow.layer3_success == filters['layer3_success'])
                if 'min_quality' in filters:
                    query = query.filter(Workflow.quality_score >= filters['min_quality'])
                if 'max_quality' in filters:
                    query = query.filter(Workflow.quality_score <= filters['max_quality'])
            
            # Apply ordering
            order_field = getattr(Workflow, order_by, Workflow.extracted_at)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())
            
            # Apply pagination
            workflows = query.offset(offset).limit(limit).all()
            
            return workflows
            
        finally:
            if self._owns_session:
                session.close()
    
    def update_workflow(
        self,
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Workflow]:
        """
        Update workflow fields.
        
        Args:
            workflow_id: Workflow ID to update
            updates: Dictionary of fields to update
        
        Returns:
            Updated workflow or None if not found
        """
        session = self._get_session()
        
        try:
            workflow = session.query(Workflow).filter(
                Workflow.workflow_id == workflow_id
            ).first()
            
            if not workflow:
                return None
            
            # Update fields
            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
            
            workflow.updated_at = datetime.utcnow()
            
            if self._owns_session:
                session.commit()
                session.refresh(workflow)
            
            logger.info(f"Updated workflow: {workflow_id}")
            return workflow
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"Error updating workflow {workflow_id}: {e}")
            raise
        finally:
            if self._owns_session:
                session.close()
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow and all related data.
        
        Args:
            workflow_id: Workflow ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        session = self._get_session()
        
        try:
            workflow = session.query(Workflow).filter(
                Workflow.workflow_id == workflow_id
            ).first()
            
            if not workflow:
                return False
            
            session.delete(workflow)
            
            if self._owns_session:
                session.commit()
            
            logger.info(f"Deleted workflow: {workflow_id}")
            return True
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise
        finally:
            if self._owns_session:
                session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts, success rates, and other metrics
        """
        session = self._get_session()
        
        try:
            total = session.query(func.count(Workflow.id)).scalar()
            
            layer1_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer1_success == True
            ).scalar()
            
            layer2_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer2_success == True
            ).scalar()
            
            layer3_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer3_success == True
            ).scalar()
            
            avg_quality = session.query(func.avg(Workflow.quality_score)).scalar() or 0
            avg_processing_time = session.query(func.avg(Workflow.processing_time)).scalar() or 0
            
            return {
                'total_workflows': total,
                'layer1_success_count': layer1_success,
                'layer1_success_rate': (layer1_success / total * 100) if total > 0 else 0,
                'layer2_success_count': layer2_success,
                'layer2_success_rate': (layer2_success / total * 100) if total > 0 else 0,
                'layer3_success_count': layer3_success,
                'layer3_success_rate': (layer3_success / total * 100) if total > 0 else 0,
                'avg_quality_score': round(avg_quality, 2),
                'avg_processing_time': round(avg_processing_time, 2)
            }
            
        finally:
            if self._owns_session:
                session.close()
    
    def search_workflows(
        self,
        search_term: str,
        search_fields: List[str] = ['title', 'description'],
        limit: int = 50
    ) -> List[Workflow]:
        """
        Search workflows by text.
        
        Args:
            search_term: Text to search for
            search_fields: Fields to search in ('title', 'description', 'use_case')
            limit: Maximum results
        
        Returns:
            List of matching workflows
        """
        session = self._get_session()
        
        try:
            query = session.query(Workflow).join(WorkflowMetadata)
            
            # Build search conditions
            conditions = []
            search_term_lower = search_term.lower()
            
            if 'title' in search_fields:
                conditions.append(func.lower(WorkflowMetadata.title).contains(search_term_lower))
            if 'description' in search_fields:
                conditions.append(func.lower(WorkflowMetadata.description).contains(search_term_lower))
            if 'use_case' in search_fields:
                conditions.append(func.lower(WorkflowMetadata.use_case).contains(search_term_lower))
            
            if conditions:
                query = query.filter(or_(*conditions))
            
            workflows = query.limit(limit).all()
            return workflows
            
        finally:
            if self._owns_session:
                session.close()
