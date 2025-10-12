"""
Workflow Orchestrator - Production-Grade Batch Processing Coordinator.

Coordinates complete workflow extraction with:
- Rate limiting (prevents 429 errors)
- Retry logic (handles transient failures)
- Progress tracking (resume capability)
- Database storage (persistence)
- Batch processing (efficiency)

This is the "brain" that brings everything together.

Author: Dev1
Task: SCRAPE-011
Date: October 11, 2025
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

from src.orchestrator.e2e_pipeline import E2EPipeline
from src.orchestrator.rate_limiter import RateLimiter
from src.orchestrator.retry_handler import RetryHandler, RetryableError, NonRetryableError
from src.orchestrator.progress_tracker import ProgressTracker
from src.storage.repository import WorkflowRepository
from src.storage.database import get_session


class WorkflowOrchestrator:
    """
    Production-grade workflow orchestrator.
    
    Coordinates all extraction layers with intelligent:
    - Rate limiting (respects n8n.io 2 req/sec limit)
    - Retry logic (exponential backoff: 1s → 2s → 4s)
    - Progress tracking (checkpoint/resume capability)
    - Batch processing (efficient large-scale processing)
    - Database storage (persistent results)
    
    Example:
        >>> orchestrator = WorkflowOrchestrator(
        ...     repository=repo,
        ...     rate_limit=2.0,
        ...     max_retries=3
        ... )
        >>> 
        >>> # Process single workflow
        >>> result = await orchestrator.process_workflow('2462', 'https://n8n.io/workflows/2462')
        >>>
        >>> # Process batch
        >>> workflows = [{'id': '2462', 'url': '...'}, ...]
        >>> results = await orchestrator.process_batch(workflows)
        >>>
        >>> # Resume from checkpoint
        >>> results = await orchestrator.process_batch(workflows, resume_from='2462')
    """
    
    def __init__(
        self,
        repository: WorkflowRepository,
        rate_limit: float = 2.0,
        max_retries: int = 3,
        batch_size: int = 20,
        checkpoint_dir: str = ".checkpoints"
    ):
        """
        Initialize workflow orchestrator.
        
        Args:
            repository: Database repository for workflow storage
            rate_limit: Requests per second (default: 2.0 for n8n.io)
            max_retries: Maximum retry attempts (default: 3)
            batch_size: Number of workflows to process concurrently (default: 20)
            checkpoint_dir: Directory for checkpoint files
        """
        self.repository = repository
        self.batch_size = batch_size
        
        # Initialize E2E pipeline (reuse from SCRAPE-007)
        self.e2e_pipeline = E2EPipeline()
        
        # Initialize orchestration components
        self.rate_limiter = RateLimiter(rate=rate_limit)
        self.retry_handler = RetryHandler(max_attempts=max_retries)
        self.progress_tracker = ProgressTracker(checkpoint_dir=checkpoint_dir)
        
        # Overall statistics
        self.stats = {
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0,
            'total_stored': 0,
            'total_skipped': 0,
        }
        
        logger.info(
            f"WorkflowOrchestrator initialized: "
            f"rate_limit={rate_limit} req/sec, "
            f"max_retries={max_retries}, "
            f"batch_size={batch_size}"
        )
    
    async def process_workflow(
        self,
        workflow_id: str,
        url: str,
        store_result: bool = True
    ) -> Dict[str, Any]:
        """
        Process single workflow through complete E2E pipeline with orchestration.
        
        Flow:
        1. Apply rate limiting (wait if needed)
        2. Extract via E2E pipeline (with retry on failure)
        3. Track progress
        4. Store in database (optional)
        5. Return result
        
        Args:
            workflow_id: n8n workflow ID
            url: Full workflow URL
            store_result: Whether to store in database (default: True)
        
        Returns:
            Processing result dictionary containing:
            - success: bool
            - workflow_id: str
            - url: str
            - layers: Dict with Layer 1/2/3 results
            - quality_score: float
            - processing_time: float
            - stored: bool
            - error: str (if failed)
        """
        start_time = datetime.now()
        
        # Set current workflow in progress tracker
        self.progress_tracker.set_current_workflow(workflow_id)
        
        try:
            # Apply rate limiting (prevents 429 errors)
            await self.rate_limiter.acquire('n8n.io')
            
            # Process workflow with retry logic
            extraction_result = await self.retry_handler.retry_with_backoff(
                func=lambda: self.e2e_pipeline.process_workflow(workflow_id, url),
                error_context=f"Workflow {workflow_id}"
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Extract quality score
            quality_score = extraction_result.get('quality_score', 0.0)
            
            # Store in database if requested
            stored = False
            if store_result:
                try:
                    stored_workflow = self.repository.create_workflow(
                        workflow_id=workflow_id,
                        url=url,
                        extraction_result=extraction_result
                    )
                    stored = True
                    self.stats['total_stored'] += 1
                    
                except Exception as store_error:
                    logger.error(f"Failed to store workflow {workflow_id}: {store_error}")
                    stored = False
            
            # Update progress tracker
            self.progress_tracker.update(
                workflow_id=workflow_id,
                status='success',
                processing_time=processing_time,
                quality_score=quality_score
            )
            
            # Update stats
            self.stats['total_processed'] += 1
            self.stats['total_successful'] += 1
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'url': url,
                'quality_score': quality_score,
                'processing_time': processing_time,
                'stored': stored,
                'extraction_result': extraction_result
            }
        
        except NonRetryableError as e:
            # Permanent failure - don't retry
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"Non-retryable error for workflow {workflow_id}: {e}")
            
            # Update progress tracker
            self.progress_tracker.update(
                workflow_id=workflow_id,
                status='failed',
                processing_time=processing_time,
                error=str(e)
            )
            
            # Update stats
            self.stats['total_processed'] += 1
            self.stats['total_failed'] += 1
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'url': url,
                'error': str(e),
                'error_type': 'non_retryable',
                'processing_time': processing_time,
                'stored': False
            }
        
        except Exception as e:
            # Retries exhausted
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"All retries exhausted for workflow {workflow_id}: {e}")
            
            # Update progress tracker
            self.progress_tracker.update(
                workflow_id=workflow_id,
                status='failed',
                processing_time=processing_time,
                error=str(e)
            )
            
            # Update stats
            self.stats['total_processed'] += 1
            self.stats['total_failed'] += 1
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'url': url,
                'error': str(e),
                'error_type': 'retries_exhausted',
                'processing_time': processing_time,
                'stored': False
            }
    
    async def process_batch(
        self,
        workflows: List[Dict[str, str]],
        resume_from: Optional[str] = None,
        concurrent_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process batch of workflows with orchestration.
        
        Features:
        - Progress tracking with ETA
        - Checkpoint/resume capability
        - Concurrent processing (controlled)
        - Rate limiting across all requests
        - Comprehensive statistics
        
        Args:
            workflows: List of {'id': workflow_id, 'url': workflow_url}
            resume_from: Optional workflow ID to resume from
            concurrent_limit: Max concurrent workflows (default: batch_size)
        
        Returns:
            Batch processing results with statistics
        """
        if concurrent_limit is None:
            concurrent_limit = self.batch_size
        
        # Start progress tracking
        self.progress_tracker.start_batch(len(workflows))
        
        # Resume support
        start_index = 0
        if resume_from:
            try:
                start_index = next(
                    i for i, w in enumerate(workflows) 
                    if w['id'] == resume_from
                )
                logger.info(
                    f"📂 Resuming from workflow '{resume_from}' "
                    f"(index {start_index}/{len(workflows)})"
                )
            except StopIteration:
                logger.warning(
                    f"Resume workflow '{resume_from}' not found, "
                    f"starting from beginning"
                )
                start_index = 0
        
        # Process workflows
        results = []
        workflows_to_process = workflows[start_index:]
        
        logger.info(
            f"🚀 Starting batch processing: {len(workflows_to_process)} workflows "
            f"(concurrent_limit: {concurrent_limit})"
        )
        
        # Process in batches to limit concurrency
        for batch_start in range(0, len(workflows_to_process), concurrent_limit):
            batch = workflows_to_process[batch_start:batch_start + concurrent_limit]
            
            # Process batch concurrently
            batch_tasks = [
                self.process_workflow(
                    workflow['id'],
                    workflow['url'],
                    store_result=True
                )
                for workflow in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    results.append({
                        'success': False,
                        'error': str(result),
                        'error_type': 'exception'
                    })
                else:
                    results.append(result)
            
            # Print progress
            self.progress_tracker.print_progress_bar()
        
        # Finish tracking
        self.progress_tracker.finish_batch()
        
        # Print final summary
        print()  # New line after progress bar
        self.progress_tracker.print_summary()
        
        # Get statistics
        progress_stats = self.progress_tracker.get_statistics()
        rate_limit_stats = self.rate_limiter.get_statistics()
        retry_stats = self.retry_handler.get_statistics()
        
        # Compile batch results
        batch_summary = {
            'total_workflows': len(workflows),
            'processed': len(results),
            'successful': sum(1 for r in results if r.get('success')),
            'failed': sum(1 for r in results if not r.get('success')),
            'success_rate': (
                sum(1 for r in results if r.get('success')) / len(results) * 100
                if results else 0.0
            ),
            'resumed_from': resume_from,
            'start_index': start_index,
            'results': results,
            'statistics': {
                'progress': progress_stats,
                'rate_limiter': rate_limit_stats,
                'retry_handler': retry_stats,
                'orchestrator': self.stats
            }
        }
        
        logger.info(
            f"✅ Batch complete: {batch_summary['successful']}/{batch_summary['processed']} successful "
            f"({batch_summary['success_rate']:.1f}%)"
        )
        
        return batch_summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive orchestrator statistics.
        
        Returns:
            Combined statistics from all components
        """
        return {
            'orchestrator': self.stats,
            'progress': self.progress_tracker.get_statistics(),
            'rate_limiter': self.rate_limiter.get_statistics(),
            'retry_handler': self.retry_handler.get_statistics(),
        }
    
    def reset_statistics(self):
        """Reset all statistics counters."""
        self.stats = {
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0,
            'total_stored': 0,
            'total_skipped': 0,
        }
        self.rate_limiter.reset_statistics()
        self.retry_handler.reset_statistics()
        
        logger.info("Orchestrator statistics reset")
    
    def save_checkpoint(self, last_workflow_id: str) -> str:
        """
        Save checkpoint for resume capability.
        
        Args:
            last_workflow_id: Last processed workflow ID
        
        Returns:
            Checkpoint file path
        """
        return self.progress_tracker.save_checkpoint(last_workflow_id)
    
    def load_checkpoint(self, checkpoint_id: Optional[str] = None):
        """
        Load checkpoint for resume.
        
        Args:
            checkpoint_id: Specific checkpoint ID, or None for latest
        
        Returns:
            Checkpoint data
        """
        return self.progress_tracker.load_checkpoint(checkpoint_id)
    
    def __repr__(self):
        """String representation."""
        return (
            f"WorkflowOrchestrator("
            f"processed={self.stats['total_processed']}, "
            f"rate_limit={self.rate_limiter.rate} req/sec"
            f")"
        )

