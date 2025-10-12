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
    VideoTranscript,
    WorkflowBusinessIntelligence,
    WorkflowCommunityData,
    WorkflowTechnicalDetails,
    WorkflowPerformanceAnalytics,
    WorkflowRelationships,
    WorkflowEnhancedContent
)


class WorkflowRepository:
    """
    Repository for workflow CRUD operations.
    
    Encapsulates all database access for workflows, providing
    a clean API for creating, reading, updating, and deleting
    workflow data across all 11 tables.
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
            # Extract layers data once for use throughout method
            layers_data = extraction_result.get('layers', {})
            quality_data = extraction_result.get('quality') or {}
            
            # Check if workflow already exists
            existing_workflow = session.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
            
            if existing_workflow:
                # Update existing workflow
                existing_workflow.url = url
                existing_workflow.processing_time = extraction_result.get('extraction_time')  # Fixed: was 'processing_time'
                existing_workflow.quality_score = quality_data.get('overall_score')  # Fixed: was 'quality_score'
                existing_workflow.layer1_success = (layers_data.get('layer1') or {}).get('success', False)
                existing_workflow.layer2_success = (layers_data.get('layer2') or {}).get('success', False)
                existing_workflow.layer3_success = (layers_data.get('layer3') or {}).get('success', False)
                existing_workflow.layer4_success = (layers_data.get('layer4') or {}).get('success', False)
                existing_workflow.layer5_success = (layers_data.get('layer5') or {}).get('success', False)
                existing_workflow.layer6_success = (layers_data.get('layer6') or {}).get('success', False)
                existing_workflow.layer7_success = (layers_data.get('layer7') or {}).get('success', False)
                existing_workflow.last_scraped_at = extraction_result.get('extracted_at')
                workflow = existing_workflow
                logger.info(f"Updated existing workflow: {workflow_id}")
            else:
                # Create new workflow record
                workflow = Workflow(
                    workflow_id=workflow_id,
                    url=url,
                    processing_time=extraction_result.get('extraction_time'),  # Fixed: was 'processing_time'
                    quality_score=quality_data.get('overall_score'),  # Fixed: was 'quality_score'
                    layer1_success=(layers_data.get('layer1') or {}).get('success', False),
                    layer2_success=(layers_data.get('layer2') or {}).get('success', False),
                    layer3_success=(layers_data.get('layer3') or {}).get('success', False),
                    layer4_success=(layers_data.get('layer4') or {}).get('success', False),
                    layer5_success=(layers_data.get('layer5') or {}).get('success', False),
                    layer6_success=(layers_data.get('layer6') or {}).get('success', False),
                    layer7_success=(layers_data.get('layer7') or {}).get('success', False),
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
                    # Extract categories and tags from raw_metadata
                    raw_data = layer1_data.get('data', {})
                    existing_metadata.categories = self._extract_categories(raw_data)
                    existing_metadata.tags = self._extract_tags(raw_data)
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
                        categories=self._extract_categories(layer1_data.get('data', {})),
                        tags=self._extract_tags(layer1_data.get('data', {})),
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
            
            # Add Layer 4 (Business Intelligence)
            layer4_data = layers_data.get('layer4') or {}
            if layer4_data.get('success'):
                # Check if business intelligence already exists
                existing_bi = session.query(WorkflowBusinessIntelligence).filter(WorkflowBusinessIntelligence.workflow_id == workflow_id).first()
                if existing_bi:
                    # Update existing business intelligence
                    self._update_business_intelligence(existing_bi, layer4_data)
                else:
                    # Create new business intelligence
                    bi = self._create_business_intelligence(workflow_id, layer4_data)
                    session.add(bi)
            
            # Add Layer 5 (Community Data)
            layer5_data = layers_data.get('layer5') or {}
            if layer5_data.get('success'):
                # Check if community data already exists
                existing_community = session.query(WorkflowCommunityData).filter(WorkflowCommunityData.workflow_id == workflow_id).first()
                if existing_community:
                    # Update existing community data
                    self._update_community_data(existing_community, layer5_data)
                else:
                    # Create new community data
                    community = self._create_community_data(workflow_id, layer5_data)
                    session.add(community)
            
            # Add Layer 6 (Technical Details)
            layer6_data = layers_data.get('layer6') or {}
            if layer6_data.get('success'):
                # Check if technical details already exists
                existing_technical = session.query(WorkflowTechnicalDetails).filter(WorkflowTechnicalDetails.workflow_id == workflow_id).first()
                if existing_technical:
                    # Update existing technical details
                    self._update_technical_details(existing_technical, layer6_data)
                else:
                    # Create new technical details
                    technical = self._create_technical_details(workflow_id, layer6_data)
                    session.add(technical)
            
            # Add Layer 7 (Performance Analytics)
            layer7_data = layers_data.get('layer7') or {}
            if layer7_data.get('success'):
                # Check if performance analytics already exists
                existing_performance = session.query(WorkflowPerformanceAnalytics).filter(WorkflowPerformanceAnalytics.workflow_id == workflow_id).first()
                if existing_performance:
                    # Update existing performance analytics
                    self._update_performance_analytics(existing_performance, layer7_data)
                else:
                    # Create new performance analytics
                    performance = self._create_performance_analytics(workflow_id, layer7_data)
                    session.add(performance)
            
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
                    joinedload(Workflow.transcripts),
                    joinedload(Workflow.business_intelligence),
                    joinedload(Workflow.community_data),
                    joinedload(Workflow.technical_details),
                    joinedload(Workflow.performance_analytics),
                    joinedload(Workflow.relationships),
                    joinedload(Workflow.enhanced_content)
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
            
            layer4_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer4_success == True
            ).scalar()
            
            layer5_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer5_success == True
            ).scalar()
            
            layer6_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer6_success == True
            ).scalar()
            
            layer7_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer7_success == True
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
                'layer4_success_count': layer4_success,
                'layer4_success_rate': (layer4_success / total * 100) if total > 0 else 0,
                'layer5_success_count': layer5_success,
                'layer5_success_rate': (layer5_success / total * 100) if total > 0 else 0,
                'layer6_success_count': layer6_success,
                'layer6_success_rate': (layer6_success / total * 100) if total > 0 else 0,
                'layer7_success_count': layer7_success,
                'layer7_success_rate': (layer7_success / total * 100) if total > 0 else 0,
                'avg_quality_score': round(avg_quality, 2),
                'avg_processing_time': round(avg_processing_time, 2)
            }
            
        finally:
            if self._owns_session:
                session.close()
    
    def _create_business_intelligence(self, workflow_id: str, layer4_data: Dict[str, Any]) -> WorkflowBusinessIntelligence:
        """Create new business intelligence record from layer 4 data."""
        data = layer4_data.get('data', {})
        return WorkflowBusinessIntelligence(
            workflow_id=workflow_id,
            revenue_impact=data.get('revenue_impact'),
            cost_savings=data.get('cost_savings'),
            efficiency_gains=data.get('efficiency_gains'),
            time_savings=data.get('time_savings'),
            resource_savings=data.get('resource_savings'),
            error_reduction=data.get('error_reduction'),
            productivity_gains=data.get('productivity_gains'),
            quality_improvements=data.get('quality_improvements'),
            customer_satisfaction=data.get('customer_satisfaction'),
            business_value_score=data.get('business_value_score'),
            roi_estimate=data.get('roi_estimate'),
            payback_period=data.get('payback_period'),
            implementation_cost=data.get('implementation_cost'),
            maintenance_cost=data.get('maintenance_cost'),
            support_cost=data.get('support_cost'),
            training_cost=data.get('training_cost'),
            customization_cost=data.get('customization_cost'),
            integration_cost=data.get('integration_cost'),
            business_function=data.get('business_function'),
            business_process=data.get('business_process'),
            business_outcome=data.get('business_outcome'),
            business_metric=data.get('business_metric'),
            business_kpi=data.get('business_kpi'),
            business_goal=data.get('business_goal'),
            business_requirement=data.get('business_requirement'),
            business_constraint=data.get('business_constraint'),
            business_risk=data.get('business_risk'),
            business_opportunity=data.get('business_opportunity'),
            business_challenge=data.get('business_challenge'),
            business_solution=data.get('business_solution'),
            business_benefit=data.get('business_benefit'),
            business_advantage=data.get('business_advantage'),
            business_competitive_advantage=data.get('business_competitive_advantage'),
            business_innovation=data.get('business_innovation'),
            business_transformation=data.get('business_transformation'),
            business_digitalization=data.get('business_digitalization'),
            business_automation=data.get('business_automation'),
            business_optimization=data.get('business_optimization'),
            business_standardization=data.get('business_standardization'),
            business_compliance=data.get('business_compliance'),
            business_governance=data.get('business_governance'),
            business_audit=data.get('business_audit'),
            business_security=data.get('business_security'),
            business_privacy=data.get('business_privacy'),
            business_ethics=data.get('business_ethics')
        )
    
    def _update_business_intelligence(self, existing_bi: WorkflowBusinessIntelligence, layer4_data: Dict[str, Any]):
        """Update existing business intelligence record with new layer 4 data."""
        data = layer4_data.get('data', {})
        for field, value in data.items():
            if hasattr(existing_bi, field):
                setattr(existing_bi, field, value)
    
    def _create_community_data(self, workflow_id: str, layer5_data: Dict[str, Any]) -> WorkflowCommunityData:
        """Create new community data record from layer 5 data."""
        data = layer5_data.get('data', {})
        return WorkflowCommunityData(
            workflow_id=workflow_id,
            comments_count=data.get('comments_count', 0),
            reviews_count=data.get('reviews_count', 0),
            questions_count=data.get('questions_count', 0),
            answers_count=data.get('answers_count', 0),
            discussions_count=data.get('discussions_count', 0),
            mentions_count=data.get('mentions_count', 0),
            bookmarks_count=data.get('bookmarks_count', 0),
            favorites_count=data.get('favorites_count', 0),
            follows_count=data.get('follows_count', 0),
            forks_count=data.get('forks_count', 0),
            clones_count=data.get('clones_count', 0),
            remixes_count=data.get('remixes_count', 0),
            downloads_count=data.get('downloads_count', 0),
            installs_count=data.get('installs_count', 0),
            usage_count=data.get('usage_count', 0),
            community_rating=data.get('community_rating'),
            community_rating_count=data.get('community_rating_count', 0),
            community_engagement_score=data.get('community_engagement_score'),
            community_activity_score=data.get('community_activity_score'),
            community_growth_rate=data.get('community_growth_rate'),
            community_retention_rate=data.get('community_retention_rate'),
            community_sentiment_score=data.get('community_sentiment_score'),
            community_satisfaction_score=data.get('community_satisfaction_score')
        )
    
    def _update_community_data(self, existing_community: WorkflowCommunityData, layer5_data: Dict[str, Any]):
        """Update existing community data record with new layer 5 data."""
        data = layer5_data.get('data', {})
        for field, value in data.items():
            if hasattr(existing_community, field):
                setattr(existing_community, field, value)
    
    def _create_technical_details(self, workflow_id: str, layer6_data: Dict[str, Any]) -> WorkflowTechnicalDetails:
        """Create new technical details record from layer 6 data."""
        data = layer6_data.get('data', {})
        return WorkflowTechnicalDetails(
            workflow_id=workflow_id,
            api_endpoints=data.get('api_endpoints'),
            api_authentication_types=data.get('api_authentication_types'),
            api_rate_limits=data.get('api_rate_limits'),
            credential_requirements=data.get('credential_requirements'),
            credential_types=data.get('credential_types'),
            security_requirements=data.get('security_requirements'),
            performance_metrics=data.get('performance_metrics'),
            execution_time=data.get('execution_time'),
            memory_usage=data.get('memory_usage'),
            cpu_usage=data.get('cpu_usage'),
            error_handling_patterns=data.get('error_handling_patterns'),
            retry_mechanisms=data.get('retry_mechanisms'),
            fallback_strategies=data.get('fallback_strategies'),
            data_validation_rules=data.get('data_validation_rules'),
            data_transformation_rules=data.get('data_transformation_rules'),
            workflow_triggers=data.get('workflow_triggers'),
            workflow_conditions=data.get('workflow_conditions'),
            workflow_actions=data.get('workflow_actions'),
            workflow_branches=data.get('workflow_branches'),
            workflow_loops=data.get('workflow_loops'),
            workflow_parallelism=data.get('workflow_parallelism'),
            workflow_error_handling=data.get('workflow_error_handling'),
            workflow_logging=data.get('workflow_logging'),
            workflow_monitoring=data.get('workflow_monitoring'),
            workflow_backup_strategies=data.get('workflow_backup_strategies'),
            workflow_recovery_strategies=data.get('workflow_recovery_strategies'),
            workflow_scaling_strategies=data.get('workflow_scaling_strategies'),
            workflow_optimization_strategies=data.get('workflow_optimization_strategies'),
            workflow_testing_strategies=data.get('workflow_testing_strategies'),
            workflow_deployment_strategies=data.get('workflow_deployment_strategies'),
            workflow_maintenance_strategies=data.get('workflow_maintenance_strategies'),
            workflow_support_strategies=data.get('workflow_support_strategies'),
            workflow_documentation_level=data.get('workflow_documentation_level'),
            workflow_tutorial_level=data.get('workflow_tutorial_level'),
            workflow_example_count=data.get('workflow_example_count', 0),
            workflow_template_count=data.get('workflow_template_count', 0),
            workflow_customization_level=data.get('workflow_customization_level'),
            workflow_configuration_level=data.get('workflow_configuration_level'),
            workflow_integration_level=data.get('workflow_integration_level'),
            workflow_extension_level=data.get('workflow_extension_level'),
            workflow_automation_level=data.get('workflow_automation_level'),
            workflow_intelligence_level=data.get('workflow_intelligence_level')
        )
    
    def _update_technical_details(self, existing_technical: WorkflowTechnicalDetails, layer6_data: Dict[str, Any]):
        """Update existing technical details record with new layer 6 data."""
        data = layer6_data.get('data', {})
        for field, value in data.items():
            if hasattr(existing_technical, field):
                setattr(existing_technical, field, value)
    
    def _create_performance_analytics(self, workflow_id: str, layer7_data: Dict[str, Any]) -> WorkflowPerformanceAnalytics:
        """Create new performance analytics record from layer 7 data."""
        data = layer7_data.get('data', {})
        return WorkflowPerformanceAnalytics(
            workflow_id=workflow_id,
            execution_success_rate=data.get('execution_success_rate'),
            execution_failure_rate=data.get('execution_failure_rate'),
            execution_error_rate=data.get('execution_error_rate'),
            performance_benchmarks=data.get('performance_benchmarks'),
            performance_metrics=data.get('performance_metrics'),
            performance_trends=data.get('performance_trends'),
            usage_statistics=data.get('usage_statistics'),
            usage_patterns=data.get('usage_patterns'),
            usage_analytics=data.get('usage_analytics'),
            error_analytics=data.get('error_analytics'),
            error_patterns=data.get('error_patterns'),
            error_trends=data.get('error_trends'),
            optimization_opportunities=data.get('optimization_opportunities'),
            optimization_recommendations=data.get('optimization_recommendations'),
            scaling_requirements=data.get('scaling_requirements'),
            scaling_limitations=data.get('scaling_limitations'),
            scaling_recommendations=data.get('scaling_recommendations'),
            monitoring_requirements=data.get('monitoring_requirements'),
            monitoring_metrics=data.get('monitoring_metrics'),
            monitoring_alerts=data.get('monitoring_alerts'),
            maintenance_cost=data.get('maintenance_cost'),
            support_cost=data.get('support_cost'),
            training_cost=data.get('training_cost'),
            documentation_cost=data.get('documentation_cost'),
            testing_cost=data.get('testing_cost'),
            deployment_cost=data.get('deployment_cost'),
            integration_cost=data.get('integration_cost'),
            customization_cost=data.get('customization_cost'),
            security_cost=data.get('security_cost'),
            compliance_cost=data.get('compliance_cost'),
            governance_cost=data.get('governance_cost'),
            audit_cost=data.get('audit_cost'),
            backup_cost=data.get('backup_cost'),
            maintenance_requirements=data.get('maintenance_requirements'),
            support_requirements=data.get('support_requirements'),
            training_requirements=data.get('training_requirements'),
            documentation_requirements=data.get('documentation_requirements'),
            testing_requirements=data.get('testing_requirements'),
            deployment_requirements=data.get('deployment_requirements'),
            integration_requirements=data.get('integration_requirements'),
            customization_requirements=data.get('customization_requirements'),
            security_requirements=data.get('security_requirements'),
            compliance_requirements=data.get('compliance_requirements'),
            governance_requirements=data.get('governance_requirements'),
            audit_requirements=data.get('audit_requirements'),
            backup_requirements=data.get('backup_requirements'),
            support_level=data.get('support_level'),
            training_level=data.get('training_level'),
            documentation_level=data.get('documentation_level'),
            testing_level=data.get('testing_level'),
            deployment_level=data.get('deployment_level'),
            integration_level=data.get('integration_level'),
            customization_level=data.get('customization_level'),
            security_level=data.get('security_level'),
            compliance_level=data.get('compliance_level'),
            governance_level=data.get('governance_level'),
            audit_level=data.get('audit_level'),
            backup_level=data.get('backup_level'),
            maintenance_schedule=data.get('maintenance_schedule')
        )
    
    def _update_performance_analytics(self, existing_performance: WorkflowPerformanceAnalytics, layer7_data: Dict[str, Any]):
        """Update existing performance analytics record with new layer 7 data."""
        data = layer7_data.get('data', {})
        for field, value in data.items():
            if hasattr(existing_performance, field):
                setattr(existing_performance, field, value)
    
    def _extract_categories(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Extract categories from raw metadata.
        
        Args:
            raw_data: Raw metadata dictionary
            
        Returns:
            List of category strings
        """
        categories = []
        
        # Extract primary category
        primary_category = raw_data.get('primary_category')
        if primary_category:
            categories.append(primary_category)
        
        # Extract secondary categories
        secondary_categories = raw_data.get('secondary_categories', [])
        if isinstance(secondary_categories, list):
            categories.extend(secondary_categories)
        
        # Extract industry categories
        industry = raw_data.get('industry', [])
        if isinstance(industry, list):
            categories.extend(industry)
        elif isinstance(industry, str):
            categories.append(industry)
        
        # Extract general tags as potential categories
        general_tags = raw_data.get('general_tags', [])
        if isinstance(general_tags, list):
            # Filter tags that look like categories (capitalized, single words)
            category_tags = [tag for tag in general_tags if tag and len(tag.split()) <= 2 and tag[0].isupper()]
            categories.extend(category_tags)
        
        # Remove duplicates and empty values
        return list(set([cat for cat in categories if cat and isinstance(cat, str)]))
    
    def _extract_tags(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Extract tags from raw metadata.
        
        Args:
            raw_data: Raw metadata dictionary
            
        Returns:
            List of tag strings
        """
        tags = []
        
        # Extract general tags
        general_tags = raw_data.get('general_tags', [])
        if isinstance(general_tags, list):
            tags.extend(general_tags)
        
        # Extract node tags
        node_tags = raw_data.get('node_tags', [])
        if isinstance(node_tags, list):
            tags.extend(node_tags)
        
        # Extract difficulty level as a tag
        difficulty = raw_data.get('difficulty_level')
        if difficulty:
            tags.append(f"difficulty:{difficulty}")
        
        # Remove duplicates and empty values
        return list(set([tag for tag in tags if tag and isinstance(tag, str)]))
    
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
