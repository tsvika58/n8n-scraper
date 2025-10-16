"""
Retry Handler with Exponential Backoff and Circuit Breaker.

Handles transient failures with intelligent retry logic:
- Exponential backoff: 1s → 2s → 4s
- Circuit breaker: Stops after too many consecutive failures
- Error categorization: Retryable vs non-retryable

Author: Dev1
Task: SCRAPE-011
Date: October 11, 2025
"""

import asyncio
import time
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime
from loguru import logger


class RetryableError(Exception):
    """Exception that should trigger a retry (network, timeout, 429, 500-503)."""
    pass


class NonRetryableError(Exception):
    """Exception that should NOT trigger a retry (404, 401, 403)."""
    pass


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class RetryHandler:
    """
    Retry handler with exponential backoff and circuit breaker.
    
    Handles transient failures gracefully with configurable retry strategy.
    Implements circuit breaker pattern to prevent cascade failures.
    
    Example:
        >>> handler = RetryHandler(max_attempts=3, base_delay=1.0)
        >>> result = await handler.retry_with_backoff(
        ...     lambda: some_async_function()
        ... )
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        circuit_breaker_threshold: int = 10,
        circuit_breaker_timeout: float = 300.0  # 5 minutes
    ):
        """
        Initialize retry handler.
        
        Args:
            max_attempts: Maximum retry attempts (default: 3)
            base_delay: Base delay for exponential backoff (default: 1.0s)
            max_delay: Maximum delay between retries (default: 60s)
            circuit_breaker_threshold: Consecutive failures to trip breaker (default: 10)
            circuit_breaker_timeout: Time before circuit breaker auto-resets (default: 300s)
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # Circuit breaker state
        self.consecutive_failures = 0
        self.circuit_open = False
        self.circuit_opened_at: Optional[float] = None
        
        # Statistics
        self.stats = {
            'total_attempts': 0,
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'circuit_breaker_trips': 0,
            'circuit_breaker_resets': 0,
            'errors_by_type': {},
        }
        
        logger.debug(
            f"RetryHandler initialized: max_attempts={max_attempts}, "
            f"base_delay={base_delay}s, circuit_threshold={circuit_breaker_threshold}"
        )
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        error_context: str = "operation",
        **kwargs
    ) -> Any:
        """
        Execute function with retry and exponential backoff.
        
        Retry strategy:
        - Attempt 1: Immediate
        - Attempt 2: Wait 1s (base_delay)
        - Attempt 3: Wait 2s (base_delay * 2)
        - Attempt 4: Wait 4s (base_delay * 4)
        - etc.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            error_context: Context for error messages
            **kwargs: Keyword arguments for func
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            NonRetryableError: For permanent errors
            Exception: If all retries exhausted
        """
        # Check circuit breaker
        self._check_circuit_breaker_timeout()
        
        if self.circuit_open:
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN (consecutive failures: {self.consecutive_failures})"
            )
        
        last_error = None
        
        for attempt in range(self.max_attempts):
            self.stats['total_attempts'] += 1
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Success - reset consecutive failures
                if self.consecutive_failures > 0:
                    logger.info(f"Success after {self.consecutive_failures} previous failures - resetting counter")
                
                self.consecutive_failures = 0
                
                # Track successful retry
                if attempt > 0:
                    self.stats['successful_retries'] += 1
                    logger.info(f"{error_context}: succeeded on attempt {attempt + 1}")
                
                return result
            
            except NonRetryableError as e:
                # Permanent error - don't retry
                logger.error(f"{error_context}: non-retryable error: {e}")
                self._track_error(type(e).__name__)
                self._increment_failures()
                raise
            
            except Exception as e:
                last_error = e
                self._track_error(type(e).__name__)
                
                # Log the error
                logger.warning(
                    f"{error_context}: attempt {attempt + 1}/{self.max_attempts} failed: "
                    f"{type(e).__name__}: {str(e)[:100]}"
                )
                
                # Last attempt - don't wait, just fail
                if attempt == self.max_attempts - 1:
                    self.stats['failed_retries'] += 1
                    self._increment_failures()
                    logger.error(
                        f"{error_context}: all {self.max_attempts} attempts failed"
                    )
                    raise
                
                # Calculate exponential backoff delay
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                
                # Track retry
                self.stats['total_retries'] += 1
                
                logger.info(
                    f"{error_context}: retrying in {delay:.1f}s "
                    f"(attempt {attempt + 2}/{self.max_attempts})..."
                )
                
                await asyncio.sleep(delay)
        
        # Should never reach here, but just in case
        raise last_error
    
    def _increment_failures(self):
        """Increment consecutive failures and check circuit breaker."""
        self.consecutive_failures += 1
        
        if self.consecutive_failures >= self.circuit_breaker_threshold:
            self._trip_circuit_breaker()
    
    def _trip_circuit_breaker(self):
        """Trip the circuit breaker."""
        if not self.circuit_open:
            self.circuit_open = True
            self.circuit_opened_at = time.time()
            self.stats['circuit_breaker_trips'] += 1
            
            logger.error(
                f"🔴 CIRCUIT BREAKER TRIPPED! "
                f"({self.consecutive_failures} consecutive failures) "
                f"Will auto-reset in {self.circuit_breaker_timeout}s"
            )
    
    def _check_circuit_breaker_timeout(self):
        """Check if circuit breaker should auto-reset."""
        if self.circuit_open and self.circuit_opened_at:
            elapsed = time.time() - self.circuit_opened_at
            
            if elapsed >= self.circuit_breaker_timeout:
                self.reset_circuit_breaker(auto=True)
    
    def reset_circuit_breaker(self, auto: bool = False):
        """
        Reset circuit breaker manually or automatically.
        
        Args:
            auto: True if auto-reset after timeout
        """
        if self.circuit_open:
            self.circuit_open = False
            self.consecutive_failures = 0
            self.circuit_opened_at = None
            self.stats['circuit_breaker_resets'] += 1
            
            reset_type = "AUTO" if auto else "MANUAL"
            logger.info(f"🟢 CIRCUIT BREAKER RESET ({reset_type})")
    
    def _track_error(self, error_type: str):
        """Track error by type."""
        if error_type not in self.stats['errors_by_type']:
            self.stats['errors_by_type'][error_type] = 0
        self.stats['errors_by_type'][error_type] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get retry handler statistics.
        
        Returns:
            Dictionary with retry statistics including:
            - total_attempts: Total function execution attempts
            - total_retries: Number of retry attempts
            - successful_retries: Retries that succeeded
            - failed_retries: Retries that failed
            - circuit_breaker_trips: Times circuit breaker opened
            - errors_by_type: Error counts by exception type
        """
        return {
            **self.stats,
            'consecutive_failures': self.consecutive_failures,
            'circuit_open': self.circuit_open,
            'circuit_breaker_threshold': self.circuit_breaker_threshold,
            'success_rate': (
                (self.stats['total_attempts'] - self.stats['failed_retries']) /
                self.stats['total_attempts'] * 100
                if self.stats['total_attempts'] > 0 else 0.0
            ),
        }
    
    def reset_statistics(self):
        """Reset statistics counters (keeps circuit breaker state)."""
        self.stats = {
            'total_attempts': 0,
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'circuit_breaker_trips': 0,
            'circuit_breaker_resets': 0,
            'errors_by_type': {},
        }
        logger.debug("RetryHandler statistics reset")
    
    def is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry.
        
        Retryable errors:
        - Network errors (ConnectionError, TimeoutError)
        - Rate limit errors (429)
        - Server errors (500-503)
        - RetryableError exceptions
        
        Non-retryable errors:
        - Not found (404)
        - Unauthorized (401, 403)
        - Client errors (400)
        - NonRetryableError exceptions
        
        Args:
            error: Exception to check
        
        Returns:
            True if error should trigger retry
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Explicit non-retryable
        if isinstance(error, NonRetryableError):
            return False
        
        # Explicit retryable
        if isinstance(error, RetryableError):
            return True
        
        # Network/connection errors - retryable
        if isinstance(error, (ConnectionError, TimeoutError, asyncio.TimeoutError)):
            return True
        
        # Rate limit - retryable
        if '429' in error_str or 'rate limit' in error_str:
            return True
        
        # Server errors - retryable
        if any(code in error_str for code in ['500', '502', '503']):
            return True
        
        # Client errors - not retryable
        if any(code in error_str for code in ['400', '401', '403', '404']):
            return False
        
        # Default: retryable (be conservative)
        return True
    
    def __repr__(self):
        """String representation."""
        return (
            f"RetryHandler(max_attempts={self.max_attempts}, "
            f"consecutive_failures={self.consecutive_failures}, "
            f"circuit_open={self.circuit_open})"
        )








