"""
Enhanced Database Manager
Optimized database operations with connection pooling, batch operations, and performance monitoring.

Author: Dev1
Task: Enhanced Database Manager
Date: October 16, 2025
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy import text, func, insert, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from loguru import logger

from .database import get_session, engine
from n8n_shared.models import Workflow, WorkflowNodeContext, WorkflowStandaloneDoc, WorkflowExtractionSnapshot


class EnhancedDatabaseManager:
    """Enhanced database manager with optimized operations and monitoring."""
    
    def __init__(self):
        self.connection_pool_size = 50
        self.max_overflow = 100
        self.pool_timeout = 60
        self.batch_size = 1000
        self.performance_metrics = {
            'operations_count': 0,
            'total_time': 0,
            'avg_time': 0,
            'error_count': 0
        }
    
    @asynccontextmanager
    async def get_optimized_session(self):
        """Get optimized database session with connection pooling."""
        session = None
        start_time = time.time()
        
        try:
            session = get_session()
            yield session
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            if session:
                session.close()
            
            # Update performance metrics
            operation_time = time.time() - start_time
            self._update_performance_metrics(operation_time)
    
    def _update_performance_metrics(self, operation_time: float):
        """Update performance metrics."""
        self.performance_metrics['operations_count'] += 1
        self.performance_metrics['total_time'] += operation_time
        self.performance_metrics['avg_time'] = (
            self.performance_metrics['total_time'] / 
            self.performance_metrics['operations_count']
        )
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Create a single workflow with optimized error handling."""
        try:
            async with self.get_optimized_session() as session:
                workflow = Workflow(**workflow_data)
                session.add(workflow)
                session.commit()
                logger.debug(f"Created workflow: {workflow_data.get('workflow_id')}")
                return True
        except IntegrityError as e:
            logger.warning(f"Workflow already exists: {workflow_data.get('workflow_id')}")
            return False
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            self.performance_metrics['error_count'] += 1
            return False
    
    async def batch_create_workflows(self, workflows: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Batch create workflows with optimized performance."""
        if not workflows:
            return 0, 0
        
        successful = 0
        failed = 0
        
        try:
            async with self.get_optimized_session() as session:
                # Process in batches to avoid memory issues
                for i in range(0, len(workflows), self.batch_size):
                    batch = workflows[i:i + self.batch_size]
                    
                    try:
                        # Use bulk insert for better performance
                        session.bulk_insert_mappings(Workflow, batch)
                        session.commit()
                        successful += len(batch)
                        logger.debug(f"Batch created {len(batch)} workflows")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Batch creation failed: {e}")
                        failed += len(batch)
                        self.performance_metrics['error_count'] += 1
                
                return successful, failed
                
        except Exception as e:
            logger.error(f"Batch workflow creation failed: {e}")
            self.performance_metrics['error_count'] += 1
            return 0, len(workflows)
    
    async def upsert_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Upsert workflow with conflict resolution."""
        try:
            async with self.get_optimized_session() as session:
                # Use PostgreSQL UPSERT (ON CONFLICT)
                stmt = insert(Workflow).values(workflow_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['workflow_id'],
                    set_={
                        'title': stmt.excluded.title,
                        'description': stmt.excluded.description,
                        'url': stmt.excluded.url,
                        'layer1_scraped': stmt.excluded.layer1_scraped,
                        'layer1_5_scraped': stmt.excluded.layer1_5_scraped,
                        'layer2_scraped': stmt.excluded.layer2_scraped,
                        'layer3_scraped': stmt.excluded.layer3_scraped,
                        'unified_extraction_success': stmt.excluded.unified_extraction_success,
                        'unified_extraction_at': stmt.excluded.unified_extraction_at,
                        'updated_at': func.now()
                    }
                )
                session.execute(stmt)
                session.commit()
                logger.debug(f"Upserted workflow: {workflow_data.get('workflow_id')}")
                return True
        except Exception as e:
            logger.error(f"Failed to upsert workflow: {e}")
            self.performance_metrics['error_count'] += 1
            return False
    
    async def batch_upsert_workflows(self, workflows: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Batch upsert workflows with optimized performance."""
        if not workflows:
            return 0, 0
        
        successful = 0
        failed = 0
        
        try:
            async with self.get_optimized_session() as session:
                # Process in batches
                for i in range(0, len(workflows), self.batch_size):
                    batch = workflows[i:i + self.batch_size]
                    
                    try:
                        # Use bulk upsert for better performance
                        stmt = insert(Workflow).values(batch)
                        stmt = stmt.on_conflict_do_update(
                            index_elements=['workflow_id'],
                            set_={
                                'title': stmt.excluded.title,
                                'description': stmt.excluded.description,
                                'url': stmt.excluded.url,
                                'layer1_scraped': stmt.excluded.layer1_scraped,
                                'layer1_5_scraped': stmt.excluded.layer1_5_scraped,
                                'layer2_scraped': stmt.excluded.layer2_scraped,
                                'layer3_scraped': stmt.excluded.layer3_scraped,
                                'unified_extraction_success': stmt.excluded.unified_extraction_success,
                                'unified_extraction_at': stmt.excluded.unified_extraction_at,
                                'updated_at': func.now()
                            }
                        )
                        session.execute(stmt)
                        session.commit()
                        successful += len(batch)
                        logger.debug(f"Batch upserted {len(batch)} workflows")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Batch upsert failed: {e}")
                        failed += len(batch)
                        self.performance_metrics['error_count'] += 1
                
                return successful, failed
                
        except Exception as e:
            logger.error(f"Batch workflow upsert failed: {e}")
            self.performance_metrics['error_count'] += 1
            return 0, len(workflows)
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID with optimized query."""
        try:
            async with self.get_optimized_session() as session:
                workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
                if workflow:
                    return {
                        'workflow_id': workflow.workflow_id,
                        'title': workflow.title,
                        'url': workflow.url,
                        'description': workflow.description,
                        'layer1_scraped': workflow.layer1_scraped,
                        'layer1_5_scraped': workflow.layer1_5_scraped,
                        'layer2_scraped': workflow.layer2_scraped,
                        'layer3_scraped': workflow.layer3_scraped,
                        'unified_extraction_success': workflow.unified_extraction_success,
                        'unified_extraction_at': workflow.unified_extraction_at,
                        'created_at': workflow.created_at,
                        'updated_at': workflow.updated_at
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get workflow: {e}")
            self.performance_metrics['error_count'] += 1
            return None
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow with optimized query."""
        try:
            async with self.get_optimized_session() as session:
                updates['updated_at'] = datetime.utcnow()
                session.query(Workflow).filter_by(workflow_id=workflow_id).update(updates)
                session.commit()
                logger.debug(f"Updated workflow: {workflow_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update workflow: {e}")
            self.performance_metrics['error_count'] += 1
            return False
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow with cascade cleanup."""
        try:
            async with self.get_optimized_session() as session:
                # Delete related data first (manual cascade)
                session.query(WorkflowNodeContext).filter_by(workflow_id=workflow_id).delete()
                session.query(WorkflowStandaloneDoc).filter_by(workflow_id=workflow_id).delete()
                session.query(WorkflowExtractionSnapshot).filter_by(workflow_id=workflow_id).delete()
                
                # Delete workflow
                session.query(Workflow).filter_by(workflow_id=workflow_id).delete()
                session.commit()
                logger.debug(f"Deleted workflow: {workflow_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            self.performance_metrics['error_count'] += 1
            return False
    
    async def batch_delete_workflows(self, workflow_ids: List[str]) -> Tuple[int, int]:
        """Batch delete workflows with optimized performance."""
        if not workflow_ids:
            return 0, 0
        
        successful = 0
        failed = 0
        
        try:
            async with self.get_optimized_session() as session:
                # Process in batches
                for i in range(0, len(workflow_ids), self.batch_size):
                    batch = workflow_ids[i:i + self.batch_size]
                    
                    try:
                        # Delete related data first
                        session.query(WorkflowNodeContext).filter(
                            WorkflowNodeContext.workflow_id.in_(batch)
                        ).delete(synchronize_session=False)
                        
                        session.query(WorkflowStandaloneDoc).filter(
                            WorkflowStandaloneDoc.workflow_id.in_(batch)
                        ).delete(synchronize_session=False)
                        
                        session.query(WorkflowExtractionSnapshot).filter(
                            WorkflowExtractionSnapshot.workflow_id.in_(batch)
                        ).delete(synchronize_session=False)
                        
                        # Delete workflows
                        session.query(Workflow).filter(
                            Workflow.workflow_id.in_(batch)
                        ).delete(synchronize_session=False)
                        
                        session.commit()
                        successful += len(batch)
                        logger.debug(f"Batch deleted {len(batch)} workflows")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Batch deletion failed: {e}")
                        failed += len(batch)
                        self.performance_metrics['error_count'] += 1
                
                return successful, failed
                
        except Exception as e:
            logger.error(f"Batch workflow deletion failed: {e}")
            self.performance_metrics['error_count'] += 1
            return 0, len(workflow_ids)
    
    async def save_node_contexts(self, node_contexts: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Save node contexts with batch optimization."""
        if not node_contexts:
            return 0, 0
        
        successful = 0
        failed = 0
        
        try:
            async with self.get_optimized_session() as session:
                # Process in batches
                for i in range(0, len(node_contexts), self.batch_size):
                    batch = node_contexts[i:i + self.batch_size]
                    
                    try:
                        session.bulk_insert_mappings(WorkflowNodeContext, batch)
                        session.commit()
                        successful += len(batch)
                        logger.debug(f"Saved {len(batch)} node contexts")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Node context batch save failed: {e}")
                        failed += len(batch)
                        self.performance_metrics['error_count'] += 1
                
                return successful, failed
                
        except Exception as e:
            logger.error(f"Node context save failed: {e}")
            self.performance_metrics['error_count'] += 1
            return 0, len(node_contexts)
    
    async def save_standalone_docs(self, standalone_docs: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Save standalone docs with batch optimization."""
        if not standalone_docs:
            return 0, 0
        
        successful = 0
        failed = 0
        
        try:
            async with self.get_optimized_session() as session:
                # Process in batches
                for i in range(0, len(standalone_docs), self.batch_size):
                    batch = standalone_docs[i:i + self.batch_size]
                    
                    try:
                        session.bulk_insert_mappings(WorkflowStandaloneDoc, batch)
                        session.commit()
                        successful += len(batch)
                        logger.debug(f"Saved {len(batch)} standalone docs")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Standalone doc batch save failed: {e}")
                        failed += len(batch)
                        self.performance_metrics['error_count'] += 1
                
                return successful, failed
                
        except Exception as e:
            logger.error(f"Standalone doc save failed: {e}")
            self.performance_metrics['error_count'] += 1
            return 0, len(standalone_docs)
    
    async def save_extraction_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Save extraction snapshot."""
        try:
            async with self.get_optimized_session() as session:
                snapshot_obj = WorkflowExtractionSnapshot(**snapshot)
                session.add(snapshot_obj)
                session.commit()
                logger.debug(f"Saved extraction snapshot: {snapshot.get('workflow_id')}")
                return True
        except Exception as e:
            logger.error(f"Failed to save extraction snapshot: {e}")
            self.performance_metrics['error_count'] += 1
            return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        return {
            'operations_count': self.performance_metrics['operations_count'],
            'total_time': self.performance_metrics['total_time'],
            'avg_time': self.performance_metrics['avg_time'],
            'error_count': self.performance_metrics['error_count'],
            'error_rate': (
                self.performance_metrics['error_count'] / 
                max(self.performance_metrics['operations_count'], 1)
            ) * 100
        }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            async with self.get_optimized_session() as session:
                # Get table statistics
                stats_query = """
                SELECT 
                    schemaname,
                    tablename,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                AND tablename IN ('workflows', 'workflow_node_contexts', 'workflow_standalone_docs', 'workflow_extraction_snapshots')
                ORDER BY n_live_tup DESC;
                """
                
                result = session.execute(text(stats_query))
                table_stats = result.fetchall()
                
                # Get connection pool stats
                pool_stats = {
                    'pool_size': engine.pool.size(),
                    'checked_in': engine.pool.checkedin(),
                    'checked_out': engine.pool.checkedout(),
                    'overflow': engine.pool.overflow(),
                    'invalid': engine.pool.invalid()
                }
                
                return {
                    'table_stats': [dict(row._mapping) for row in table_stats],
                    'pool_stats': pool_stats,
                    'performance_metrics': await self.get_performance_metrics()
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {'error': str(e)}
    
    async def cleanup_orphaned_data(self) -> Dict[str, int]:
        """Clean up orphaned data."""
        try:
            async with self.get_optimized_session() as session:
                # Clean up orphaned node contexts
                orphaned_contexts = session.query(WorkflowNodeContext).filter(
                    ~WorkflowNodeContext.workflow_id.in_(
                        session.query(Workflow.workflow_id)
                    )
                ).delete(synchronize_session=False)
                
                # Clean up orphaned standalone docs
                orphaned_docs = session.query(WorkflowStandaloneDoc).filter(
                    ~WorkflowStandaloneDoc.workflow_id.in_(
                        session.query(Workflow.workflow_id)
                    )
                ).delete(synchronize_session=False)
                
                # Clean up orphaned extraction snapshots
                orphaned_snapshots = session.query(WorkflowExtractionSnapshot).filter(
                    ~WorkflowExtractionSnapshot.workflow_id.in_(
                        session.query(Workflow.workflow_id)
                    )
                ).delete(synchronize_session=False)
                
                session.commit()
                
                logger.info(f"Cleaned up orphaned data: {orphaned_contexts} contexts, {orphaned_docs} docs, {orphaned_snapshots} snapshots")
                
                return {
                    'orphaned_contexts': orphaned_contexts,
                    'orphaned_docs': orphaned_docs,
                    'orphaned_snapshots': orphaned_snapshots
                }
                
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned data: {e}")
            return {'error': str(e)}
    
    async def perform_maintenance(self) -> bool:
        """Perform database maintenance."""
        try:
            async with self.get_optimized_session() as session:
                # Update statistics
                tables = ['workflows', 'workflow_node_contexts', 'workflow_standalone_docs', 'workflow_extraction_snapshots']
                for table in tables:
                    session.execute(text(f"ANALYZE {table}"))
                
                # Clean up old data
                session.execute(text("""
                    DELETE FROM workflow_extraction_snapshots 
                    WHERE created_at < NOW() - INTERVAL '6 months'
                """))
                
                # Clean up orphaned data
                await self.cleanup_orphaned_data()
                
                session.commit()
                logger.info("Database maintenance completed")
                return True
                
        except Exception as e:
            logger.error(f"Database maintenance failed: {e}")
            return False

