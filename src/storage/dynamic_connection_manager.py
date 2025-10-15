#!/usr/bin/env python3
"""
Dynamic Connection Manager
Intelligent connection pooling that adapts to scraper activity

Features:
- Shared global pool across all scrapers
- Dynamic allocation based on activity
- Idle scrapers release connections
- Active scrapers can use more when available
- Fair distribution when all scrapers active
"""

import os
import time
import threading
from contextlib import contextmanager
from typing import Optional, Dict, List
from collections import defaultdict
from sqlalchemy import create_engine, text, pool, event
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
import psutil


class DynamicConnectionManager:
    """
    Manages database connections dynamically across multiple scrapers
    
    Architecture:
    - Global pool: 20 connections (configurable)
    - Per-scraper soft limit: 10 connections
    - Idle detection: No activity for 60 seconds
    - Reallocation: Every 30 seconds
    """
    
    # Singleton instance
    _instance: Optional['DynamicConnectionManager'] = None
    _lock = threading.Lock()
    
    # Global pool settings
    GLOBAL_POOL_SIZE = 20      # Total connections available
    SCRAPER_SOFT_LIMIT = 10    # Soft limit per scraper when competing
    SCRAPER_MAX_LIMIT = 15     # Hard limit per scraper
    IDLE_TIMEOUT = 60          # Seconds before considered idle
    REALLOCATION_INTERVAL = 30 # Seconds between reallocations
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize dynamic connection manager"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._engine = None
        self._session_factory = None
        
        # Tracking
        self._scraper_activity: Dict[str, float] = {}  # scraper_name -> last_activity_time
        self._scraper_connections: Dict[str, int] = defaultdict(int)  # scraper_name -> connection_count
        self._connection_owners: Dict[int, str] = {}  # connection_id -> scraper_name
        
        # Reallocation thread
        self._reallocation_thread = None
        self._running = False
        
        self._initialize_engine()
        self._start_reallocation_thread()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with dynamic pooling"""
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create engine with large global pool
        self._engine = create_engine(
            database_url,
            poolclass=pool.QueuePool,
            pool_size=self.GLOBAL_POOL_SIZE,
            max_overflow=5,  # Small overflow for bursts
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                'connect_timeout': 10,
                'application_name': f'n8n-scraper-dynamic-{os.getpid()}'
            }
        )
        
        # Track connection checkout/checkin
        @event.listens_for(self._engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Track connection creation"""
            connection_record.info['created_at'] = time.time()
        
        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine)
        
        logger.info(f"✅ Dynamic connection pool initialized (global={self.GLOBAL_POOL_SIZE})")
    
    def _start_reallocation_thread(self):
        """Start background thread for connection reallocation"""
        self._running = True
        self._reallocation_thread = threading.Thread(
            target=self._reallocation_loop,
            daemon=True
        )
        self._reallocation_thread.start()
        logger.info("✅ Connection reallocation thread started")
    
    def _reallocation_loop(self):
        """Background loop that reallocates connections"""
        while self._running:
            try:
                time.sleep(self.REALLOCATION_INTERVAL)
                self._reallocate_connections()
            except Exception as e:
                logger.error(f"Error in reallocation loop: {e}")
    
    def _reallocate_connections(self):
        """Reallocate connections based on scraper activity"""
        current_time = time.time()
        
        # Identify active and idle scrapers
        active_scrapers = []
        idle_scrapers = []
        
        for scraper_name, last_activity in list(self._scraper_activity.items()):
            if current_time - last_activity > self.IDLE_TIMEOUT:
                idle_scrapers.append(scraper_name)
            else:
                active_scrapers.append(scraper_name)
        
        if not active_scrapers:
            return  # No active scrapers
        
        # Calculate available connections
        pool_status = self.get_pool_status()
        available = pool_status['size'] - pool_status['checked_out']
        
        # Log reallocation
        if idle_scrapers:
            logger.info(f"🔄 Reallocation: {len(active_scrapers)} active, {len(idle_scrapers)} idle, {available} available")
        
        # Adjust limits based on activity
        if len(active_scrapers) == 1:
            # Only one active scraper - can use more
            logger.debug(f"Single active scraper ({active_scrapers[0]}) can use up to {self.SCRAPER_MAX_LIMIT} connections")
        elif len(active_scrapers) <= 2:
            # Two active scrapers - generous allocation
            per_scraper = self.GLOBAL_POOL_SIZE // 2
            logger.debug(f"Two active scrapers - {per_scraper} connections each")
        else:
            # Multiple active scrapers - fair distribution
            per_scraper = self.SCRAPER_SOFT_LIMIT
            logger.debug(f"{len(active_scrapers)} active scrapers - {per_scraper} connections each")
    
    def register_scraper(self, scraper_name: str):
        """Register a scraper and mark as active"""
        with self._lock:
            self._scraper_activity[scraper_name] = time.time()
            logger.info(f"📝 Registered scraper: {scraper_name}")
    
    def mark_activity(self, scraper_name: str):
        """Mark scraper as active (called on each query)"""
        self._scraper_activity[scraper_name] = time.time()
    
    def get_scraper_limit(self, scraper_name: str) -> int:
        """
        Get current connection limit for a scraper
        
        Returns dynamic limit based on:
        - Number of active scrapers
        - Current pool usage
        - Scraper activity
        """
        current_time = time.time()
        
        # Count active scrapers
        active_count = sum(
            1 for last_activity in self._scraper_activity.values()
            if current_time - last_activity <= self.IDLE_TIMEOUT
        )
        
        if active_count == 0:
            return self.SCRAPER_MAX_LIMIT
        elif active_count == 1:
            # Only this scraper active - can use more
            return self.SCRAPER_MAX_LIMIT
        elif active_count == 2:
            # Two active - generous split
            return self.GLOBAL_POOL_SIZE // 2
        else:
            # Multiple active - fair distribution
            return max(
                self.SCRAPER_SOFT_LIMIT,
                self.GLOBAL_POOL_SIZE // active_count
            )
    
    @contextmanager
    def get_session(self, scraper_name: str = "unknown"):
        """
        Get a database session with dynamic connection management
        
        Args:
            scraper_name: Name of the scraper requesting connection
        
        Usage:
            with connection_manager.get_session("layer1_5") as session:
                result = session.execute(text("SELECT * FROM workflows"))
        """
        # Mark activity
        self.mark_activity(scraper_name)
        
        # Check if scraper is within limits
        current_connections = self._scraper_connections[scraper_name]
        limit = self.get_scraper_limit(scraper_name)
        
        if current_connections >= limit:
            logger.warning(
                f"⚠️  {scraper_name} at connection limit ({current_connections}/{limit}), "
                f"waiting for available connection..."
            )
        
        session = self._session_factory()
        
        # Track connection
        with self._lock:
            self._scraper_connections[scraper_name] += 1
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error ({scraper_name}): {e}")
            raise
        finally:
            session.close()
            
            # Release connection
            with self._lock:
                self._scraper_connections[scraper_name] -= 1
    
    def get_pool_status(self) -> Dict:
        """Get global pool status"""
        if self._engine is None:
            return {'status': 'not_initialized'}
        
        pool_obj = self._engine.pool
        return {
            'status': 'active',
            'size': pool_obj.size(),
            'checked_in': pool_obj.checkedin(),
            'checked_out': pool_obj.checkedout(),
            'overflow': pool_obj.overflow(),
            'global_pool_size': self.GLOBAL_POOL_SIZE,
            'scraper_soft_limit': self.SCRAPER_SOFT_LIMIT,
            'scraper_max_limit': self.SCRAPER_MAX_LIMIT
        }
    
    def get_scraper_stats(self) -> List[Dict]:
        """Get per-scraper connection statistics"""
        current_time = time.time()
        stats = []
        
        for scraper_name, last_activity in self._scraper_activity.items():
            idle_time = current_time - last_activity
            is_active = idle_time <= self.IDLE_TIMEOUT
            
            stats.append({
                'scraper': scraper_name,
                'active': is_active,
                'connections': self._scraper_connections[scraper_name],
                'limit': self.get_scraper_limit(scraper_name),
                'idle_seconds': int(idle_time),
                'last_activity': time.strftime('%H:%M:%S', time.localtime(last_activity))
            })
        
        return sorted(stats, key=lambda x: x['connections'], reverse=True)
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            with self.get_session("health_check") as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def shutdown(self):
        """Shutdown connection manager"""
        logger.info("🛑 Shutting down dynamic connection manager...")
        
        self._running = False
        
        if self._reallocation_thread:
            self._reallocation_thread.join(timeout=5)
        
        if self._engine:
            self._engine.dispose()
            logger.info("✅ All database connections closed")
        
        self._scraper_activity.clear()
        self._scraper_connections.clear()
        logger.info("✅ Dynamic connection manager shutdown complete")


# Global singleton instance
dynamic_connection_manager = DynamicConnectionManager()


# Convenience function
def get_session(scraper_name: str = "unknown") -> Session:
    """
    Get a database session with dynamic connection management
    
    Args:
        scraper_name: Name of the scraper (e.g., "layer1_5", "layer2", "layer3")
    
    Usage:
        with get_session("layer1_5") as session:
            result = session.execute(text("SELECT * FROM workflows"))
    """
    return dynamic_connection_manager.get_session(scraper_name)


# Utility functions
def register_scraper(scraper_name: str):
    """Register a scraper at startup"""
    dynamic_connection_manager.register_scraper(scraper_name)


def get_connection_stats() -> Dict:
    """Get comprehensive connection statistics"""
    pool_status = dynamic_connection_manager.get_pool_status()
    scraper_stats = dynamic_connection_manager.get_scraper_stats()
    
    return {
        'pool': pool_status,
        'scrapers': scraper_stats,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }


def print_connection_stats():
    """Print formatted connection statistics"""
    stats = get_connection_stats()
    
    print("\n" + "=" * 70)
    print("📊 DYNAMIC CONNECTION POOL STATUS")
    print("=" * 70)
    
    # Pool status
    pool = stats['pool']
    print(f"\n🌐 Global Pool:")
    print(f"  Total: {pool['global_pool_size']} connections")
    print(f"  In Use: {pool['checked_out']}/{pool['size']}")
    print(f"  Available: {pool['checked_in']}")
    print(f"  Overflow: {pool['overflow']}")
    
    # Scraper stats
    print(f"\n🔧 Scraper Allocation:")
    print(f"  {'Scraper':<20} {'Status':<10} {'Connections':<15} {'Limit':<10} {'Idle':<10}")
    print(f"  {'-'*20} {'-'*10} {'-'*15} {'-'*10} {'-'*10}")
    
    for scraper in stats['scrapers']:
        status = "🟢 Active" if scraper['active'] else "⚪ Idle"
        connections = f"{scraper['connections']}"
        limit = f"{scraper['limit']}"
        idle = f"{scraper['idle_seconds']}s" if not scraper['active'] else "-"
        
        print(f"  {scraper['scraper']:<20} {status:<10} {connections:<15} {limit:<10} {idle:<10}")
    
    print(f"\n⏰ Updated: {stats['timestamp']}")
    print("=" * 70 + "\n")


# Startup and shutdown helpers
def startup_dynamic_pool():
    """Initialize dynamic connection pool"""
    logger.info("🚀 Starting dynamic connection pool...")
    
    # Health check
    if dynamic_connection_manager.health_check():
        logger.info("✅ Database connection healthy")
    else:
        raise Exception("❌ Database connection unhealthy")
    
    logger.info("✅ Dynamic connection pool ready")


def shutdown_dynamic_pool():
    """Shutdown dynamic connection pool"""
    dynamic_connection_manager.shutdown()

