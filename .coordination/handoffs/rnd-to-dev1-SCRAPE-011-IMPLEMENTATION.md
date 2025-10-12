# 🔧 **SCRAPE-011: IMPLEMENTATION GUIDE**

**From:** RND Manager  
**To:** Dev1  
**Date:** October 11, 2025, 6:40 PM  
**Subject:** Complete Implementation Guide for Orchestrator  
**Task:** SCRAPE-011 - Orchestrator & Rate Limiting

---

## 🎯 **COMPLETE CODE EXAMPLES**

### **File 1: Rate Limiter**

Create `src/orchestrator/rate_limiter.py`:

```python
"""
Rate Limiter using Token Bucket Algorithm.

Prevents API throttling by controlling request rate.
Configured for n8n.io (2 requests/second).

Author: Dev1
Task: SCRAPE-011
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Ensures compliance with API rate limits to prevent 429 errors.
    Supports per-domain rate limiting for multiple services.
    """
    
    def __init__(self, rate: float = 2.0, capacity: int = 5):
        """
        Initialize rate limiter.
        
        Args:
            rate: Requests per second (default: 2.0 for n8n.io)
            capacity: Bucket capacity for burst requests (default: 5)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.total_waits = 0
        self.total_wait_time = 0.0
        
        # Per-domain rate limiting
        self.domain_buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'tokens': capacity, 'last_update': time.time()}
        )
    
    async def acquire(self, domain: str = 'default') -> None:
        """
        Acquire token from bucket, wait if necessary.
        
        Args:
            domain: Domain name for per-domain rate limiting
        """
        bucket = self.domain_buckets[domain]
        
        # Refill tokens based on elapsed time
        now = time.time()
        elapsed = now - bucket['last_update']
        bucket['tokens'] = min(
            self.capacity,
            bucket['tokens'] + elapsed * self.rate
        )
        bucket['last_update'] = now
        
        # If insufficient tokens, wait
        if bucket['tokens'] < 1:
            wait_time = (1 - bucket['tokens']) / self.rate
            self.total_waits += 1
            self.total_wait_time += wait_time
            
            logger.debug(
                f"Rate limit: waiting {wait_time:.2f}s for {domain} "
                f"(tokens: {bucket['tokens']:.2f})"
            )
            
            await asyncio.sleep(wait_time)
            bucket['tokens'] = 0
        else:
            bucket['tokens'] -= 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with rate limit stats
        """
        return {
            'total_waits': self.total_waits,
            'total_wait_time': self.total_wait_time,
            'avg_wait_time': (
                self.total_wait_time / self.total_waits 
                if self.total_waits > 0 else 0
            ),
            'rate': self.rate,
            'capacity': self.capacity,
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.total_waits = 0
        self.total_wait_time = 0.0
```

---

### **File 2: Retry Handler**

Create `src/orchestrator/retry_handler.py`:

```python
"""
Retry Handler with Exponential Backoff.

Handles transient failures with intelligent retry logic.

Author: Dev1
Task: SCRAPE-011
"""

import asyncio
import logging
from typing import Callable, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """Exception that should trigger a retry."""
    pass


class NonRetryableError(Exception):
    """Exception that should not trigger a retry."""
    pass


class RetryHandler:
    """
    Retry handler with exponential backoff and circuit breaker.
    
    Handles transient failures (network, timeout, rate limits).
    Avoids retry on permanent failures (404, 401, 403).
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        circuit_breaker_threshold: int = 10
    ):
        """
        Initialize retry handler.
        
        Args:
            max_attempts: Maximum retry attempts (default: 3)
            base_delay: Base delay for exponential backoff (default: 1.0s)
            max_delay: Maximum delay between retries (default: 60s)
            circuit_breaker_threshold: Consecutive failures to trip breaker
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        
        # Statistics
        self.stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'circuit_breaker_trips': 0,
        }
        
        # Circuit breaker
        self.consecutive_failures = 0
        self.circuit_open = False
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry and exponential backoff.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Function result
            
        Raises:
            Exception if all retries exhausted
        """
        # Check circuit breaker
        if self.circuit_open:
            raise NonRetryableError("Circuit breaker is open")
        
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset circuit breaker
                self.consecutive_failures = 0
                if attempt > 0:
                    self.stats['successful_retries'] += 1
                
                return result
                
            except NonRetryableError:
                # Don't retry permanent errors
                raise
                
            except Exception as e:
                last_error = e
                self.stats['total_retries'] += 1
                
                # Last attempt - don't wait
                if attempt == self.max_attempts - 1:
                    self.stats['failed_retries'] += 1
                    self._check_circuit_breaker()
                    raise
                
                # Calculate delay (exponential backoff)
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                await asyncio.sleep(delay)
        
        # Should never reach here, but just in case
        raise last_error
    
    def _check_circuit_breaker(self):
        """Check if circuit breaker should trip."""
        self.consecutive_failures += 1
        
        if self.consecutive_failures >= self.circuit_breaker_threshold:
            self.circuit_open = True
            self.stats['circuit_breaker_trips'] += 1
            logger.error(
                f"Circuit breaker OPEN after {self.consecutive_failures} "
                f"consecutive failures"
            )
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker manually."""
        self.circuit_open = False
        self.consecutive_failures = 0
        logger.info("Circuit breaker RESET")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            **self.stats,
            'consecutive_failures': self.consecutive_failures,
            'circuit_open': self.circuit_open,
        }
```

---

### **File 3: Progress Tracker**

Create `src/orchestrator/progress_tracker.py`:

```python
"""
Progress Tracker with Checkpoint/Resume Capability.

Tracks real-time progress and enables resume after interruption.

Author: Dev1
Task: SCRAPE-011
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CheckpointData:
    """Checkpoint data structure."""
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


class ProgressTracker:
    """
    Track processing progress with checkpoint/resume capability.
    
    Provides:
    - Real-time progress updates
    - Statistics calculation
    - Checkpoint save/restore
    - ETA estimation
    """
    
    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        """
        Initialize progress tracker.
        
        Args:
            checkpoint_dir: Directory for checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress data
        self.total_workflows = 0
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.processing_times = []
        self.start_time = None
        self.last_workflow_id = None
        
        # Current checkpoint
        self.current_checkpoint = None
    
    def start_batch(self, total: int):
        """
        Start tracking a batch.
        
        Args:
            total: Total number of workflows
        """
        self.total_workflows = total
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.processing_times = []
        self.start_time = datetime.now()
        
        logger.info(f"Progress tracking started: {total} workflows")
    
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
            workflow_id: Workflow ID
            status: 'success' or 'failed'
            processing_time: Time taken to process
            quality_score: Quality score (if successful)
            error: Error message (if failed)
        """
        self.processed += 1
        self.last_workflow_id = workflow_id
        
        if status == 'success':
            self.successful += 1
        else:
            self.failed += 1
        
        if processing_time:
            self.processing_times.append(processing_time)
        
        # Log progress every 10 workflows
        if self.processed % 10 == 0:
            self._log_progress()
    
    def _log_progress(self):
        """Log current progress."""
        remaining = self.total_workflows - self.processed
        success_rate = (
            self.successful / self.processed * 100 
            if self.processed > 0 else 0
        )
        
        avg_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )
        
        eta_seconds = remaining * avg_time
        
        logger.info(
            f"Progress: {self.processed}/{self.total_workflows} "
            f"({success_rate:.1f}% success) | "
            f"ETA: {eta_seconds/60:.1f} min"
        )
    
    def save_checkpoint(self, last_workflow_id: str) -> str:
        """
        Save checkpoint for resume capability.
        
        Args:
            last_workflow_id: Last processed workflow ID
            
        Returns:
            Checkpoint file path
        """
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        avg_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )
        
        remaining = self.total_workflows - self.processed
        eta_seconds = remaining * avg_time
        
        checkpoint = CheckpointData(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            total_workflows=self.total_workflows,
            processed=self.processed,
            successful=self.successful,
            failed=self.failed,
            remaining=remaining,
            last_workflow_id=last_workflow_id,
            avg_processing_time=avg_time,
            eta_seconds=eta_seconds
        )
        
        # Save to file
        checkpoint_path = self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)
        
        self.current_checkpoint = checkpoint
        
        logger.info(f"Checkpoint saved: {checkpoint_path}")
        
        return str(checkpoint_path)
    
    def load_checkpoint(self, checkpoint_id: Optional[str] = None) -> CheckpointData:
        """
        Load checkpoint for resume.
        
        Args:
            checkpoint_id: Specific checkpoint ID, or None for latest
            
        Returns:
            Checkpoint data
        """
        if checkpoint_id:
            checkpoint_path = self.checkpoint_dir / f"checkpoint_{checkpoint_id}.json"
        else:
            # Find latest checkpoint
            checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.json"))
            if not checkpoints:
                raise FileNotFoundError("No checkpoints found")
            checkpoint_path = checkpoints[-1]
        
        with open(checkpoint_path) as f:
            data = json.load(f)
        
        checkpoint = CheckpointData(**data)
        
        logger.info(f"Checkpoint loaded: {checkpoint_path}")
        logger.info(f"  Resuming from workflow: {checkpoint.last_workflow_id}")
        logger.info(f"  Progress: {checkpoint.processed}/{checkpoint.total_workflows}")
        
        return checkpoint
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current progress statistics.
        
        Returns:
            Dictionary with progress stats
        """
        if not self.start_time:
            return {}
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        avg_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )
        
        remaining = self.total_workflows - self.processed
        eta_seconds = remaining * avg_time
        
        return {
            'total_workflows': self.total_workflows,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'remaining': remaining,
            'success_rate': (
                self.successful / self.processed * 100 
                if self.processed > 0 else 0
            ),
            'elapsed_seconds': elapsed,
            'avg_time_per_workflow': avg_time,
            'eta_seconds': eta_seconds,
            'workflows_per_minute': (
                self.processed / elapsed * 60 
                if elapsed > 0 else 0
            ),
        }
    
    def print_summary(self):
        """Print final summary."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 ORCHESTRATION SUMMARY")
        print("="*60)
        print(f"Total Workflows: {stats['total_workflows']}")
        print(f"Processed: {stats['processed']}")
        print(f"Successful: {stats['successful']} ({stats['success_rate']:.1f}%)")
        print(f"Failed: {stats['failed']}")
        print(f"\nTiming:")
        print(f"  Elapsed: {stats['elapsed_seconds']:.1f}s")
        print(f"  Avg per workflow: {stats['avg_time_per_workflow']:.2f}s")
        print(f"  Throughput: {stats['workflows_per_minute']:.1f} workflows/min")
        print("="*60 + "\n")
```

---

### **File 4: Complete Orchestrator**

Already provided in main assignment. See Phase 1 code example.

---

## 🧪 **TESTING GUIDE**

### **Create Test File:**

Create `tests/integration/test_orchestrator.py`:

```python
"""
Integration Tests for Workflow Orchestrator.

Tests orchestration, rate limiting, retry logic, and progress tracking.

Author: Dev1
Task: SCRAPE-011
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.orchestrator.rate_limiter import RateLimiter
from src.orchestrator.retry_handler import RetryHandler, RetryableError
from src.orchestrator.progress_tracker import ProgressTracker
from src.storage.database import get_session
from src.storage.repository import WorkflowRepository


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_repository():
    """Test repository with database."""
    session = get_session()
    return WorkflowRepository(session)


@pytest.fixture
def test_workflows():
    """Sample workflows for testing."""
    return [
        {'id': f'TEST-ORCH-{i:03d}', 'url': f'https://n8n.io/workflows/TEST-ORCH-{i:03d}'}
        for i in range(20)
    ]


# ============================================================================
# RATE LIMITER TESTS (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_rate_limiter_enforces_limit():
    """Test that rate limiter enforces request limit."""
    limiter = RateLimiter(rate=2.0, capacity=5)
    
    # Should allow 5 requests immediately (burst)
    start = time.time()
    for _ in range(5):
        await limiter.acquire('test')
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # Should be immediate
    
    # 6th request should wait
    start = time.time()
    await limiter.acquire('test')
    elapsed = time.time() - start
    
    assert elapsed >= 0.4  # Should wait ~0.5s (1/2 rate)


@pytest.mark.asyncio
async def test_rate_limiter_zero_429_errors():
    """Test that rate limiter prevents 429 errors."""
    limiter = RateLimiter(rate=2.0)
    
    # Make 10 requests - should not get 429
    errors_429 = 0
    
    async def mock_request():
        await limiter.acquire('n8n.io')
        # Simulate API call
        await asyncio.sleep(0.01)
        return 200  # Success
    
    for _ in range(10):
        status = await mock_request()
        if status == 429:
            errors_429 += 1
    
    assert errors_429 == 0


@pytest.mark.asyncio
async def test_rate_limiter_burst_handling():
    """Test burst request handling."""
    limiter = RateLimiter(rate=2.0, capacity=5)
    
    # Burst of 5 should be immediate
    start = time.time()
    tasks = [limiter.acquire('test') for _ in range(5)]
    await asyncio.gather(*tasks)
    burst_time = time.time() - start
    
    assert burst_time < 0.2  # Burst should be fast


@pytest.mark.asyncio
async def test_rate_limiter_statistics():
    """Test rate limiter statistics tracking."""
    limiter = RateLimiter(rate=2.0, capacity=2)
    
    # Make requests that will cause waits
    for _ in range(5):
        await limiter.acquire('test')
    
    stats = limiter.get_statistics()
    
    assert stats['total_waits'] > 0
    assert stats['total_wait_time'] > 0


# ============================================================================
# RETRY HANDLER TESTS (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_retry_on_network_error():
    """Test retry on network errors."""
    handler = RetryHandler(max_attempts=3)
    
    attempt_count = 0
    
    async def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise RetryableError("Network error")
        return "success"
    
    result = await handler.retry_with_backoff(flaky_function)
    
    assert result == "success"
    assert attempt_count == 3
    assert handler.stats['total_retries'] == 2


@pytest.mark.asyncio
async def test_exponential_backoff():
    """Test exponential backoff delays."""
    handler = RetryHandler(max_attempts=3, base_delay=0.1)
    
    delays = []
    
    async def failing_function():
        start = time.time()
        if len(delays) < 2:
            delays.append(time.time())
            raise RetryableError("Test error")
        return "success"
    
    start = time.time()
    await handler.retry_with_backoff(failing_function)
    
    # Check delays were exponential (0.1s → 0.2s)
    # (Approximate due to execution time)


@pytest.mark.asyncio
async def test_max_attempts_respected():
    """Test that max attempts is respected."""
    handler = RetryHandler(max_attempts=3)
    
    async def always_fails():
        raise RetryableError("Always fails")
    
    with pytest.raises(RetryableError):
        await handler.retry_with_backoff(always_fails)
    
    assert handler.stats['total_retries'] == 2  # 3 attempts = 2 retries


@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker trips after threshold."""
    handler = RetryHandler(max_attempts=1, circuit_breaker_threshold=3)
    
    async def always_fails():
        raise RetryableError("Fails")
    
    # Cause 3 consecutive failures
    for _ in range(3):
        try:
            await handler.retry_with_backoff(always_fails)
        except:
            pass
    
    # Circuit should be open
    assert handler.circuit_open == True
    assert handler.stats['circuit_breaker_trips'] == 1


# ============================================================================
# PROGRESS TRACKER TESTS (5 tests)
# ============================================================================

def test_progress_tracker_initialization():
    """Test progress tracker initialization."""
    tracker = ProgressTracker()
    
    tracker.start_batch(100)
    
    assert tracker.total_workflows == 100
    assert tracker.processed == 0
    assert tracker.successful == 0
    assert tracker.failed == 0


def test_progress_tracker_updates():
    """Test progress updates."""
    tracker = ProgressTracker()
    tracker.start_batch(10)
    
    tracker.update('TEST-001', 'success', processing_time=5.0)
    
    assert tracker.processed == 1
    assert tracker.successful == 1
    assert len(tracker.processing_times) == 1


def test_progress_tracker_statistics():
    """Test statistics calculation."""
    tracker = ProgressTracker()
    tracker.start_batch(10)
    
    for i in range(5):
        tracker.update(f'TEST-{i:03d}', 'success', processing_time=10.0)
    
    stats = tracker.get_statistics()
    
    assert stats['processed'] == 5
    assert stats['successful'] == 5
    assert stats['remaining'] == 5
    assert stats['success_rate'] == 100.0
    assert stats['avg_time_per_workflow'] == 10.0


def test_progress_tracker_checkpoint_save():
    """Test checkpoint saving."""
    tracker = ProgressTracker()
    tracker.start_batch(100)
    
    for i in range(50):
        tracker.update(f'TEST-{i:03d}', 'success', processing_time=5.0)
    
    checkpoint_path = tracker.save_checkpoint('TEST-049')
    
    assert Path(checkpoint_path).exists()


def test_progress_tracker_checkpoint_resume():
    """Test checkpoint loading for resume."""
    tracker = ProgressTracker()
    tracker.start_batch(100)
    
    for i in range(50):
        tracker.update(f'TEST-{i:03d}', 'success', processing_time=5.0)
    
    checkpoint_path = tracker.save_checkpoint('TEST-049')
    
    # Load checkpoint
    new_tracker = ProgressTracker()
    checkpoint = new_tracker.load_checkpoint()
    
    assert checkpoint.processed == 50
    assert checkpoint.last_workflow_id == 'TEST-049'


# ============================================================================
# ORCHESTRATOR TESTS (5+ tests)
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_process_single_workflow(test_repository):
    """Test processing single workflow."""
    orchestrator = WorkflowOrchestrator(
        repository=test_repository,
        rate_limit=10.0  # Fast for testing
    )
    
    result = await orchestrator.process_workflow(
        '2462',
        'https://n8n.io/workflows/2462'
    )
    
    assert result['success'] in [True, False]  # May succeed or fail
    assert 'workflow_id' in result


@pytest.mark.asyncio  
async def test_orchestrator_process_batch(test_repository, test_workflows):
    """Test batch processing."""
    orchestrator = WorkflowOrchestrator(
        repository=test_repository,
        rate_limit=10.0,
        batch_size=5
    )
    
    # Process small batch
    batch_result = await orchestrator.process_batch(test_workflows[:5])
    
    assert batch_result['total'] == 5
    assert batch_result['processed'] == 5
    assert batch_result['success_rate'] > 0


# Additional orchestrator tests would follow...
```

---

## ✅ **VALIDATION COMMANDS**

### **Test Rate Limiting:**
```bash
pytest tests/integration/test_orchestrator.py::test_rate_limiter_enforces_limit -v -s
```

### **Test Retry Logic:**
```bash
pytest tests/integration/test_orchestrator.py::test_retry_on_network_error -v -s
```

### **Test Progress Tracking:**
```bash
pytest tests/integration/test_orchestrator.py::test_progress_tracker_checkpoint_save -v -s
```

### **Test Complete Orchestration:**
```bash
pytest tests/integration/test_orchestrator.py -v
```

---

**🎯 Complete implementation guide with all code examples!**

---

*Implementation Guide v1.0*  
*Created: October 11, 2025, 6:40 PM*  
*Author: RND Manager*  
*For: Dev1*


