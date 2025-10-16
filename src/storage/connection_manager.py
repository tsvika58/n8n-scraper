#!/usr/bin/env python3
"""
Database Connection Manager
Prevents redundant connections and ensures proper cleanup

Features:
- Connection pooling with limits
- Automatic cleanup of idle connections
- Process tracking to prevent duplicates
- Health checks and monitoring
"""

import os
import time
import psutil
from contextlib import contextmanager
from typing import Optional, Dict, List
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger


class ConnectionManager:
    """Manages database connections with pooling and cleanup"""
    
    # Singleton instance
    _instance: Optional['ConnectionManager'] = None
    _engine = None
    _session_factory = None
    
    # Connection pool settings
    MAX_CONNECTIONS = 10  # Maximum connections per container
    MAX_OVERFLOW = 5      # Additional connections during peak
    POOL_TIMEOUT = 30     # Seconds to wait for connection
    POOL_RECYCLE = 3600   # Recycle connections after 1 hour
    
    # Process tracking
    _active_processes: Dict[int, str] = {}
    
    def __new__(cls):
        """Singleton pattern - only one instance per process"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection manager"""
        if self._engine is None:
            self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with connection pooling"""
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create engine with connection pooling
        self._engine = create_engine(
            database_url,
            poolclass=pool.QueuePool,
            pool_size=self.MAX_CONNECTIONS,
            max_overflow=self.MAX_OVERFLOW,
            pool_timeout=self.POOL_TIMEOUT,
            pool_recycle=self.POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,
            connect_args={
                'connect_timeout': 10,
                'application_name': f'n8n-scraper-{os.getpid()}'
            }
        )
        
        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine)
        
        logger.info(f"✅ Database connection pool initialized (max={self.MAX_CONNECTIONS})")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session with automatic cleanup
        
        Usage:
            with connection_manager.get_session() as session:
                result = session.execute(text("SELECT * FROM workflows"))
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def register_process(self, process_name: str):
        """Register a process as using the database"""
        pid = os.getpid()
        self._active_processes[pid] = process_name
        logger.info(f"📝 Registered process: {process_name} (PID: {pid})")
    
    def unregister_process(self):
        """Unregister current process"""
        pid = os.getpid()
        if pid in self._active_processes:
            process_name = self._active_processes.pop(pid)
            logger.info(f"📝 Unregistered process: {process_name} (PID: {pid})")
    
    def get_active_processes(self) -> List[Dict]:
        """Get list of active processes using database"""
        active = []
        for pid, name in list(self._active_processes.items()):
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    active.append({
                        'pid': pid,
                        'name': name,
                        'status': proc.status(),
                        'cpu_percent': proc.cpu_percent(),
                        'memory_mb': proc.memory_info().rss / 1024 / 1024
                    })
                else:
                    # Process no longer running, remove it
                    self._active_processes.pop(pid, None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process died, remove it
                self._active_processes.pop(pid, None)
        
        return active
    
    def get_pool_status(self) -> Dict:
        """Get connection pool status"""
        if self._engine is None:
            return {'status': 'not_initialized'}
        
        pool = self._engine.pool
        return {
            'status': 'active',
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'max_connections': self.MAX_CONNECTIONS,
            'max_overflow': self.MAX_OVERFLOW
        }
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def cleanup_idle_connections(self):
        """Clean up idle connections in the pool"""
        if self._engine:
            logger.info("🧹 Cleaning up idle database connections...")
            self._engine.dispose()
            self._initialize_engine()
            logger.info("✅ Connection pool refreshed")
    
    def shutdown(self):
        """Shutdown connection manager and cleanup"""
        logger.info("🛑 Shutting down connection manager...")
        
        if self._engine:
            self._engine.dispose()
            logger.info("✅ All database connections closed")
        
        self._active_processes.clear()
        logger.info("✅ Connection manager shutdown complete")


# Global singleton instance
connection_manager = ConnectionManager()


# Convenience function for backward compatibility
def get_session() -> Session:
    """Get a database session (backward compatible)"""
    return connection_manager.get_session()


# Process management utilities
def prevent_duplicate_process(process_name: str, force: bool = False) -> bool:
    """
    Prevent duplicate processes from running
    
    Args:
        process_name: Name of the process to check
        force: If True, kill existing process and continue
    
    Returns:
        True if safe to proceed, False if duplicate exists
    """
    current_pid = os.getpid()
    
    # Check for existing processes with same name
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if process_name in cmdline:
                if force:
                    logger.warning(f"⚠️  Killing duplicate process: {process_name} (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=5)
                else:
                    logger.error(f"❌ Duplicate process already running: {process_name} (PID: {proc.info['pid']})")
                    return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return True


def cleanup_zombie_processes():
    """Clean up zombie processes"""
    zombie_count = 0
    
    for proc in psutil.process_iter(['pid', 'status']):
        try:
            if proc.info['status'] == psutil.STATUS_ZOMBIE:
                zombie_count += 1
                try:
                    os.waitpid(proc.info['pid'], os.WNOHANG)
                except:
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if zombie_count > 0:
        logger.info(f"🧹 Cleaned up {zombie_count} zombie processes")
    
    return zombie_count


def get_database_connection_count() -> int:
    """Get total number of database connections from this container"""
    try:
        with connection_manager.get_session() as session:
            result = session.execute(text("""
                SELECT COUNT(*) 
                FROM pg_stat_activity 
                WHERE application_name LIKE 'n8n-scraper-%'
            """))
            return result.scalar()
    except Exception as e:
        logger.error(f"Failed to get connection count: {e}")
        return -1


# Startup cleanup function
def startup_cleanup():
    """Run cleanup before starting any scraper"""
    logger.info("🚀 Running startup cleanup...")
    
    # Clean up zombies
    zombie_count = cleanup_zombie_processes()
    
    # Check connection pool
    pool_status = connection_manager.get_pool_status()
    logger.info(f"📊 Connection pool: {pool_status}")
    
    # Health check
    if connection_manager.health_check():
        logger.info("✅ Database health check passed")
    else:
        logger.error("❌ Database health check failed")
        raise Exception("Database connection unhealthy")
    
    logger.info("✅ Startup cleanup complete")


# Shutdown cleanup function
def shutdown_cleanup():
    """Run cleanup when shutting down"""
    logger.info("🛑 Running shutdown cleanup...")
    connection_manager.shutdown()
    cleanup_zombie_processes()
    logger.info("✅ Shutdown cleanup complete")


