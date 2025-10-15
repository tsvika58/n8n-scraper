"""
Rate Limiter using Token Bucket Algorithm.

Prevents API throttling by controlling request rate.
Configured for n8n.io (2 requests/second) to prevent 429 errors.

Algorithm:
- Token bucket with configurable rate and capacity
- Tokens refill continuously at specified rate
- Requests consume 1 token
- If no tokens available, request waits

Author: Dev1
Task: SCRAPE-011
Date: October 11, 2025
"""

import asyncio
import time
from typing import Dict, Any
from collections import defaultdict
from loguru import logger


class RateLimiter:
    """
    Token bucket rate limiter for API request throttling.
    
    Ensures compliance with API rate limits (e.g., n8n.io: 2 req/sec).
    Supports per-domain rate limiting for multiple services.
    
    Example:
        >>> limiter = RateLimiter(rate=2.0, capacity=5)
        >>> await limiter.acquire('n8n.io')  # Waits if needed
        >>> # Make API request here
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
        
        # Statistics
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
        
        # Per-domain token buckets
        self.domain_buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                'tokens': self.capacity,
                'last_update': time.time(),
                'requests': 0,
                'waits': 0
            }
        )
        
        logger.debug(f"RateLimiter initialized: {rate} req/sec, capacity={capacity}")
    
    async def acquire(self, domain: str = 'default') -> None:
        """
        Acquire token from bucket, wait if necessary.
        
        This method implements the token bucket algorithm:
        1. Refill tokens based on elapsed time
        2. If tokens available, consume one and proceed
        3. If no tokens, calculate wait time and sleep
        
        Args:
            domain: Domain name for per-domain rate limiting
                   (e.g., 'n8n.io', 'youtube.com')
        
        Raises:
            asyncio.CancelledError: If task is cancelled during wait
        """
        bucket = self.domain_buckets[domain]
        
        # Refill tokens based on elapsed time
        now = time.time()
        elapsed = now - bucket['last_update']
        
        # Add tokens at specified rate
        bucket['tokens'] = min(
            self.capacity,
            bucket['tokens'] + (elapsed * self.rate)
        )
        bucket['last_update'] = now
        
        # Track request
        bucket['requests'] += 1
        self.total_requests += 1
        
        # If insufficient tokens, wait
        if bucket['tokens'] < 1.0:
            # Calculate wait time needed
            tokens_needed = 1.0 - bucket['tokens']
            wait_time = tokens_needed / self.rate
            
            # Track wait
            bucket['waits'] += 1
            self.total_waits += 1
            self.total_wait_time += wait_time
            
            logger.debug(
                f"Rate limit: waiting {wait_time:.3f}s for '{domain}' "
                f"(tokens: {bucket['tokens']:.2f}/{self.capacity})"
            )
            
            # Wait for tokens to refill
            await asyncio.sleep(wait_time)
            
            # After waiting, set tokens to 0 (consumed the 1 we waited for)
            bucket['tokens'] = 0.0
            
        else:
            # Consume one token
            bucket['tokens'] -= 1.0
        
        logger.trace(
            f"Rate limit: acquired for '{domain}' "
            f"(tokens remaining: {bucket['tokens']:.2f})"
        )
    
    def get_statistics(self, domain: str = None) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Args:
            domain: Specific domain stats, or None for global stats
        
        Returns:
            Dictionary with rate limit statistics
        """
        if domain:
            # Domain-specific stats
            bucket = self.domain_buckets.get(domain)
            if not bucket:
                return {}
            
            return {
                'domain': domain,
                'requests': bucket['requests'],
                'waits': bucket['waits'],
                'current_tokens': bucket['tokens'],
                'capacity': self.capacity,
                'rate': self.rate,
            }
        else:
            # Global stats
            return {
                'total_requests': self.total_requests,
                'total_waits': self.total_waits,
                'total_wait_time': self.total_wait_time,
                'avg_wait_time': (
                    self.total_wait_time / self.total_waits 
                    if self.total_waits > 0 else 0.0
                ),
                'wait_percentage': (
                    self.total_waits / self.total_requests * 100
                    if self.total_requests > 0 else 0.0
                ),
                'rate': self.rate,
                'capacity': self.capacity,
                'domains': list(self.domain_buckets.keys()),
            }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
        
        for bucket in self.domain_buckets.values():
            bucket['requests'] = 0
            bucket['waits'] = 0
        
        logger.debug("RateLimiter statistics reset")
    
    def get_current_rate(self, domain: str = None) -> float:
        """
        Get current request rate.
        
        Args:
            domain: Domain to check, or None for global
        
        Returns:
            Current requests per second
        """
        if domain:
            bucket = self.domain_buckets.get(domain)
            if not bucket or bucket['requests'] == 0:
                return 0.0
            
            elapsed = time.time() - bucket['last_update']
            if elapsed == 0:
                return 0.0
            
            return bucket['requests'] / elapsed
        else:
            # Global rate (rough estimate)
            return self.rate
    
    def __repr__(self):
        """String representation."""
        return f"RateLimiter(rate={self.rate}, capacity={self.capacity}, requests={self.total_requests})"







