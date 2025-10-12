"""
Progress Tracker with Checkpoint/Resume Capability.

Tracks real-time progress and enables resume after interruption.
Provides statistics, ETA calculation, and checkpoint persistence.

Author: Dev1
Task: SCRAPE-011
Date: October 11, 2025
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict, field
from loguru import logger


@dataclass
class CheckpointData:
    """Checkpoint data structure for resume capability."""
    checkpoint_id: str
    timestamp: str
    total_workflows: int
    processed: int
    successful: int
    failed: int
    remaining: int
    last_workflow_id: str
    avg_processing_time: float
    eta_seconds: float
    success_rate: float
    workflows_per_minute: float


class ProgressTracker:
    """
    Track processing progress with checkpoint/resume capability.
    
    Features:
    - Real-time progress updates
    - Statistics calculation (success rate, ETA, throughput)
    - Checkpoint save/load for resume
    - ETA estimation based on average processing time
    - Detailed logging
    
    Example:
        >>> tracker = ProgressTracker()
        >>> tracker.start_batch(500)
        >>> tracker.update('2462', 'success', processing_time=25.3)
        >>> checkpoint = tracker.save_checkpoint('2462')
        >>> # Later: tracker.load_checkpoint(checkpoint_id)
    """
    
    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        """
        Initialize progress tracker.
        
        Args:
            checkpoint_dir: Directory for checkpoint files (default: .checkpoints)
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress data
        self.total_workflows = 0
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        
        # Timing data
        self.processing_times: List[float] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Workflow tracking
        self.last_workflow_id: Optional[str] = None
        self.current_workflow_id: Optional[str] = None
        
        # Current checkpoint
        self.current_checkpoint: Optional[CheckpointData] = None
        
        # Quality tracking
        self.quality_scores: List[float] = []
        
        logger.debug(f"ProgressTracker initialized (checkpoint_dir: {checkpoint_dir})")
    
    def start_batch(self, total: int):
        """
        Start tracking a batch of workflows.
        
        Args:
            total: Total number of workflows in batch
        """
        self.total_workflows = total
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        self.processing_times = []
        self.quality_scores = []
        self.start_time = time.time()
        self.end_time = None
        
        logger.info(f"📊 Progress tracking started: {total} workflows")
    
    def update(
        self,
        workflow_id: str,
        status: str,
        processing_time: Optional[float] = None,
        quality_score: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        Update progress for a workflow.
        
        Args:
            workflow_id: Workflow ID being processed
            status: 'success', 'failed', or 'skipped'
            processing_time: Time taken to process (seconds)
            quality_score: Quality score (0-100) if successful
            error: Error message if failed
        """
        self.processed += 1
        self.last_workflow_id = workflow_id
        self.current_workflow_id = None
        
        # Update counts
        if status == 'success':
            self.successful += 1
        elif status == 'failed':
            self.failed += 1
        elif status == 'skipped':
            self.skipped += 1
        
        # Track metrics
        if processing_time is not None:
            self.processing_times.append(processing_time)
        
        if quality_score is not None:
            self.quality_scores.append(quality_score)
        
        # Log progress periodically
        if self.processed % 10 == 0:
            self._log_progress()
        
        # Auto-checkpoint every 50 workflows
        if self.processed % 50 == 0:
            self.save_checkpoint(workflow_id)
    
    def set_current_workflow(self, workflow_id: str):
        """
        Set currently processing workflow.
        
        Args:
            workflow_id: Workflow ID being processed
        """
        self.current_workflow_id = workflow_id
    
    def _log_progress(self):
        """Log current progress with statistics."""
        stats = self.get_statistics()
        
        logger.info(
            f"Progress: {stats['processed']}/{stats['total_workflows']} "
            f"({stats['progress_percentage']:.1f}%) | "
            f"Success: {stats['success_rate']:.1f}% | "
            f"Rate: {stats['workflows_per_minute']:.1f}/min | "
            f"ETA: {stats['eta_minutes']:.1f} min"
        )
    
    def save_checkpoint(self, last_workflow_id: str) -> str:
        """
        Save checkpoint for resume capability.
        
        Args:
            last_workflow_id: Last successfully processed workflow ID
        
        Returns:
            Checkpoint file path
        """
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        stats = self.get_statistics()
        
        checkpoint = CheckpointData(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            total_workflows=self.total_workflows,
            processed=self.processed,
            successful=self.successful,
            failed=self.failed,
            remaining=stats['remaining'],
            last_workflow_id=last_workflow_id,
            avg_processing_time=stats['avg_time_per_workflow'],
            eta_seconds=stats['eta_seconds'],
            success_rate=stats['success_rate'],
            workflows_per_minute=stats['workflows_per_minute']
        )
        
        # Save to file
        checkpoint_path = self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)
        
        self.current_checkpoint = checkpoint
        
        logger.info(f"💾 Checkpoint saved: {checkpoint_path.name}")
        logger.debug(f"   Processed: {checkpoint.processed}/{checkpoint.total_workflows}")
        logger.debug(f"   Success rate: {checkpoint.success_rate:.1f}%")
        
        return str(checkpoint_path)
    
    def load_checkpoint(self, checkpoint_id: Optional[str] = None) -> CheckpointData:
        """
        Load checkpoint for resume capability.
        
        Args:
            checkpoint_id: Specific checkpoint ID (YYYYMMDD_HHMMSS),
                          or None to load latest checkpoint
        
        Returns:
            CheckpointData object
        
        Raises:
            FileNotFoundError: If no checkpoints found
        """
        if checkpoint_id:
            checkpoint_path = self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"
            
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        else:
            # Find latest checkpoint
            checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"))
            
            if not checkpoints:
                raise FileNotFoundError(f"No checkpoints found in {self.checkpoint_dir}")
            
            checkpoint_path = checkpoints[-1]
        
        # Load checkpoint data
        with open(checkpoint_path) as f:
            data = json.load(f)
        
        checkpoint = CheckpointData(**data)
        self.current_checkpoint = checkpoint
        
        logger.info(f"📂 Checkpoint loaded: {checkpoint_path.name}")
        logger.info(f"   Resuming from workflow: {checkpoint.last_workflow_id}")
        logger.info(f"   Progress: {checkpoint.processed}/{checkpoint.total_workflows} ({checkpoint.success_rate:.1f}%)")
        logger.info(f"   ETA: {checkpoint.eta_seconds / 60:.1f} minutes remaining")
        
        return checkpoint
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint summaries
        """
        checkpoints = []
        
        for checkpoint_path in sorted(self.checkpoint_dir.glob("checkpoint_*.json")):
            with open(checkpoint_path) as f:
                data = json.load(f)
            
            checkpoints.append({
                'checkpoint_id': data['checkpoint_id'],
                'timestamp': data['timestamp'],
                'processed': data['processed'],
                'total': data['total_workflows'],
                'progress': f"{data['processed']}/{data['total_workflows']}",
                'success_rate': f"{data['success_rate']:.1f}%",
                'file': checkpoint_path.name
            })
        
        return checkpoints
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current progress statistics.
        
        Returns:
            Dictionary with comprehensive statistics:
            - Basic counts (total, processed, successful, failed)
            - Rates (success rate, workflows/minute)
            - Timing (elapsed, average, ETA)
            - Quality (average quality score)
        """
        if not self.start_time:
            return {
                'total_workflows': self.total_workflows,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'remaining': self.total_workflows,
                'progress_percentage': 0.0,
            }
        
        # Calculate timing
        elapsed = (self.end_time or time.time()) - self.start_time
        
        avg_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0.0
        )
        
        remaining = self.total_workflows - self.processed
        eta_seconds = remaining * avg_time if avg_time > 0 else 0.0
        
        workflows_per_minute = (
            (self.processed / elapsed) * 60 
            if elapsed > 0 else 0.0
        )
        
        # Calculate quality
        avg_quality = (
            sum(self.quality_scores) / len(self.quality_scores)
            if self.quality_scores else 0.0
        )
        
        return {
            # Counts
            'total_workflows': self.total_workflows,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'skipped': self.skipped,
            'remaining': remaining,
            
            # Rates
            'success_rate': (
                self.successful / self.processed * 100 
                if self.processed > 0 else 0.0
            ),
            'failure_rate': (
                self.failed / self.processed * 100 
                if self.processed > 0 else 0.0
            ),
            'progress_percentage': (
                self.processed / self.total_workflows * 100
                if self.total_workflows > 0 else 0.0
            ),
            
            # Timing
            'elapsed_seconds': elapsed,
            'elapsed_minutes': elapsed / 60,
            'avg_time_per_workflow': avg_time,
            'eta_seconds': eta_seconds,
            'eta_minutes': eta_seconds / 60,
            'workflows_per_minute': workflows_per_minute,
            'workflows_per_hour': workflows_per_minute * 60,
            
            # Quality
            'avg_quality_score': avg_quality,
            'total_samples': len(self.quality_scores),
            
            # State
            'is_complete': self.processed >= self.total_workflows,
            'last_workflow_id': self.last_workflow_id,
            'current_workflow_id': self.current_workflow_id,
        }
    
    def finish_batch(self):
        """Mark batch as complete."""
        self.end_time = time.time()
        logger.info("📊 Batch processing complete")
    
    def print_summary(self):
        """Print comprehensive summary."""
        stats = self.get_statistics()
        
        print("\n" + "=" * 70)
        print("📊 ORCHESTRATION PROGRESS SUMMARY")
        print("=" * 70)
        
        print(f"\n📈 Progress:")
        print(f"  Total Workflows: {stats['total_workflows']}")
        print(f"  Processed: {stats['processed']} ({stats['progress_percentage']:.1f}%)")
        print(f"  Successful: {stats['successful']} ({stats['success_rate']:.1f}%)")
        print(f"  Failed: {stats['failed']} ({stats['failure_rate']:.1f}%)")
        if stats['skipped'] > 0:
            print(f"  Skipped: {stats['skipped']}")
        print(f"  Remaining: {stats['remaining']}")
        
        print(f"\n⏱️  Timing:")
        print(f"  Elapsed: {stats['elapsed_minutes']:.1f} min")
        print(f"  Avg per workflow: {stats['avg_time_per_workflow']:.2f}s")
        print(f"  Throughput: {stats['workflows_per_minute']:.1f} workflows/min")
        print(f"  ETA: {stats['eta_minutes']:.1f} min")
        
        if stats['avg_quality_score'] > 0:
            print(f"\n⭐ Quality:")
            print(f"  Average Quality Score: {stats['avg_quality_score']:.2f}/100")
            print(f"  Samples: {stats['total_samples']}")
        
        print("\n" + "=" * 70 + "\n")
    
    def print_progress_bar(self, width: int = 50):
        """
        Print ASCII progress bar.
        
        Args:
            width: Width of progress bar in characters
        """
        stats = self.get_statistics()
        
        progress = stats['progress_percentage'] / 100
        filled = int(width * progress)
        bar = '█' * filled + '░' * (width - filled)
        
        print(
            f"\r[{bar}] {stats['progress_percentage']:.1f}% | "
            f"{stats['processed']}/{stats['total_workflows']} | "
            f"✓{stats['successful']} ✗{stats['failed']} | "
            f"ETA: {stats['eta_minutes']:.1f}min",
            end='',
            flush=True
        )
    
    def get_failure_details(self) -> List[Dict[str, str]]:
        """
        Get details of failed workflows.
        
        Returns:
            List of failure details (if tracking enabled)
        """
        # This would require storing failure details
        # For now, return empty list
        # Can be enhanced later to track individual failures
        return []
    
    def estimate_completion_time(self) -> str:
        """
        Estimate completion time as formatted string.
        
        Returns:
            Estimated completion time (e.g., "2025-10-11 20:30:45")
        """
        stats = self.get_statistics()
        
        if stats['eta_seconds'] <= 0:
            return "Complete"
        
        completion_timestamp = time.time() + stats['eta_seconds']
        completion_datetime = datetime.fromtimestamp(completion_timestamp)
        
        return completion_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    def __repr__(self):
        """String representation."""
        if self.total_workflows == 0:
            return "ProgressTracker(not started)"
        
        return (
            f"ProgressTracker("
            f"processed={self.processed}/{self.total_workflows}, "
            f"success_rate={self.successful/self.processed*100 if self.processed > 0 else 0:.1f}%"
            f")"
        )

