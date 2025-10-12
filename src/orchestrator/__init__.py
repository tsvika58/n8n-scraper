"""
Orchestration Package for N8N Workflow Scraping.

Provides production-grade orchestration with:
- WorkflowOrchestrator: Main batch processing coordinator
- RateLimiter: Token bucket rate limiting (prevents 429 errors)
- RetryHandler: Exponential backoff retry logic
- ProgressTracker: Checkpoint/resume capability
- E2EPipeline: End-to-end extraction pipeline

Author: Dev1
Task: SCRAPE-011
Date: October 11, 2025
"""

from src.orchestrator.workflow_orchestrator import WorkflowOrchestrator
from src.orchestrator.rate_limiter import RateLimiter
from src.orchestrator.retry_handler import (
    RetryHandler,
    RetryableError,
    NonRetryableError,
    CircuitBreakerOpenError
)
from src.orchestrator.progress_tracker import ProgressTracker, CheckpointData
from src.orchestrator.e2e_pipeline import E2EPipeline

__all__ = [
    # Main orchestrator
    'WorkflowOrchestrator',
    
    # Components
    'RateLimiter',
    'RetryHandler',
    'ProgressTracker',
    'E2EPipeline',
    
    # Data structures
    'CheckpointData',
    
    # Exceptions
    'RetryableError',
    'NonRetryableError',
    'CircuitBreakerOpenError',
]

__version__ = '1.0.0'
