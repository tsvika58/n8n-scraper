#!/usr/bin/env python3
"""
Global Connection Coordinator
Manages database connections across multiple containers and services

Architecture:
- Uses Redis for cross-container coordination
- Respects Supabase connection limits
- Dynamic allocation across all services
- Automatic cleanup of stale reservations

Supported Services:
- Scraper containers (n8n-scraper-app)
- Viewer containers (scraper-db-viewer)
- External connections (API, monitoring, etc.)
"""

import os
import time
import json
import socket
from typing import Optional, Dict, List
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using fallback mode")


@dataclass
class ConnectionReservation:
    """Represents a connection reservation"""
    service_name: str
    container_id: str
    hostname: str
    pid: int
    reserved_at: float
    count: int


class GlobalConnectionCoordinator:
    """
    Coordinates database connections across all containers
    
    Configuration via environment variables:
    - SUPABASE_MAX_CONNECTIONS: Total Supabase limit (default: 60 for free tier)
    - REDIS_URL: Redis connection URL (default: redis://localhost:6379)
    - SERVICE_NAME: Name of this service (e.g., "scraper", "viewer")
    - CONNECTION_RESERVE_TTL: Reservation timeout in seconds (default: 300)
    """
    
    # Singleton
    _instance: Optional['GlobalConnectionCoordinator'] = None
    
    # Default limits by Supabase plan
    SUPABASE_LIMITS = {
        'free': 60,
        'pro': 200,
        'team': 400,
        'enterprise': 1000
    }
    
    # Service priorities (higher = more important)
    SERVICE_PRIORITIES = {
        'scraper': 10,
        'viewer': 5,
        'api': 8,
        'monitoring': 3,
        'external': 1
    }
    
    # Minimum guaranteed connections per service
    SERVICE_MINIMUMS = {
        'scraper': 5,
        'viewer': 2,
        'api': 3,
        'monitoring': 1,
        'external': 1
    }
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize global coordinator"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Configuration
        self.supabase_plan = os.getenv('SUPABASE_PLAN', 'free')
        self.max_connections = int(os.getenv(
            'SUPABASE_MAX_CONNECTIONS',
            self.SUPABASE_LIMITS.get(self.supabase_plan, 60)
        ))
        
        # Reserve some connections for Supabase internal use
        self.reserved_for_supabase = int(self.max_connections * 0.1)  # 10%
        self.available_connections = self.max_connections - self.reserved_for_supabase
        
        # Service identification
        self.service_name = os.getenv('SERVICE_NAME', 'unknown')
        self.container_id = socket.gethostname()
        self.pid = os.getpid()
        
        # Redis connection
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = None
        self.use_redis = REDIS_AVAILABLE
        
        # Fallback tracking (when Redis unavailable)
        self._local_reservations: Dict[str, ConnectionReservation] = {}
        
        # Connection pool
        self._engine = None
        self._session_factory = None
        
        # Initialize
        self._initialize_redis()
        self._initialize_engine()
        
        logger.info(f"✅ Global Connection Coordinator initialized")
        logger.info(f"   Service: {self.service_name}")
        logger.info(f"   Container: {self.container_id}")
        logger.info(f"   Supabase Plan: {self.supabase_plan}")
        logger.info(f"   Max Connections: {self.max_connections}")
        logger.info(f"   Available: {self.available_connections}")
        logger.info(f"   Redis: {'✅ Connected' if self.use_redis else '❌ Fallback mode'}")
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            return
        
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.warning(f"⚠️  Redis unavailable, using fallback mode: {e}")
            self.use_redis = False
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with coordinator-managed pool"""
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Get initial allocation
        allocated = self._request_connections(self.SERVICE_MINIMUMS.get(self.service_name, 5))
        
        # Create engine with allocated connections
        self._engine = create_engine(
            database_url,
            poolclass=pool.QueuePool,
            pool_size=allocated,
            max_overflow=2,  # Small overflow
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                'connect_timeout': 10,
                'application_name': f'{self.service_name}-{self.container_id}'
            }
        )
        
        self._session_factory = sessionmaker(bind=self._engine)
        
        logger.info(f"✅ Database engine initialized with {allocated} connections")
    
    def _request_connections(self, count: int) -> int:
        """
        Request connection allocation from global coordinator
        
        Returns: Number of connections actually allocated
        """
        if not self.use_redis:
            # Fallback: just return requested count
            return min(count, self.SERVICE_MINIMUMS.get(self.service_name, 5))
        
        try:
            # Get current allocations
            allocations = self._get_all_allocations()
            total_allocated = sum(r.count for r in allocations.values())
            
            # Calculate available
            available = self.available_connections - total_allocated
            
            # Determine allocation
            service_min = self.SERVICE_MINIMUMS.get(self.service_name, 1)
            allocated = min(count, max(service_min, available))
            
            # Store reservation in Redis
            reservation = ConnectionReservation(
                service_name=self.service_name,
                container_id=self.container_id,
                hostname=socket.gethostname(),
                pid=self.pid,
                reserved_at=time.time(),
                count=allocated
            )
            
            key = f"connection:reservation:{self.service_name}:{self.container_id}"
            self.redis_client.setex(
                key,
                300,  # 5 minute TTL
                json.dumps(asdict(reservation))
            )
            
            logger.info(f"📝 Reserved {allocated} connections (requested: {count}, available: {available})")
            return allocated
        
        except Exception as e:
            logger.error(f"Error requesting connections: {e}")
            return self.SERVICE_MINIMUMS.get(self.service_name, 5)
    
    def _get_all_allocations(self) -> Dict[str, ConnectionReservation]:
        """Get all current connection allocations"""
        if not self.use_redis:
            return self._local_reservations
        
        try:
            allocations = {}
            pattern = "connection:reservation:*"
            
            for key in self.redis_client.scan_iter(match=pattern):
                data = self.redis_client.get(key)
                if data:
                    reservation_dict = json.loads(data)
                    reservation = ConnectionReservation(**reservation_dict)
                    allocations[key] = reservation
            
            return allocations
        
        except Exception as e:
            logger.error(f"Error getting allocations: {e}")
            return {}
    
    def get_global_status(self) -> Dict:
        """Get global connection status across all services"""
        allocations = self._get_all_allocations()
        
        # Group by service
        by_service = {}
        for reservation in allocations.values():
            service = reservation.service_name
            if service not in by_service:
                by_service[service] = {
                    'containers': [],
                    'total_connections': 0
                }
            
            by_service[service]['containers'].append({
                'container_id': reservation.container_id,
                'hostname': reservation.hostname,
                'pid': reservation.pid,
                'connections': reservation.count,
                'reserved_at': reservation.reserved_at
            })
            by_service[service]['total_connections'] += reservation.count
        
        total_allocated = sum(s['total_connections'] for s in by_service.values())
        
        return {
            'supabase_plan': self.supabase_plan,
            'max_connections': self.max_connections,
            'reserved_for_supabase': self.reserved_for_supabase,
            'available_for_apps': self.available_connections,
            'total_allocated': total_allocated,
            'remaining': self.available_connections - total_allocated,
            'utilization_pct': (total_allocated / self.available_connections * 100) if self.available_connections > 0 else 0,
            'services': by_service
        }
    
    @contextmanager
    def get_session(self):
        """Get a database session with global coordination"""
        # Refresh reservation
        if self.use_redis:
            key = f"connection:reservation:{self.service_name}:{self.container_id}"
            ttl = self.redis_client.ttl(key)
            if ttl < 60:  # Refresh if less than 1 minute left
                current_count = self._engine.pool.size()
                self._request_connections(current_count)
        
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
    
    def adjust_pool_size(self, new_size: int):
        """Dynamically adjust connection pool size"""
        allocated = self._request_connections(new_size)
        
        if allocated != self._engine.pool.size():
            logger.info(f"🔄 Adjusting pool size: {self._engine.pool.size()} → {allocated}")
            # Dispose and recreate engine
            self._engine.dispose()
            self._initialize_engine()
    
    def release_connections(self):
        """Release all connections held by this service"""
        if self.use_redis:
            key = f"connection:reservation:{self.service_name}:{self.container_id}"
            self.redis_client.delete(key)
            logger.info("✅ Released all connections")
        
        if self._engine:
            self._engine.dispose()
    
    def cleanup_stale_reservations(self):
        """Clean up stale reservations (admin function)"""
        if not self.use_redis:
            return
        
        try:
            pattern = "connection:reservation:*"
            cleaned = 0
            
            for key in self.redis_client.scan_iter(match=pattern):
                ttl = self.redis_client.ttl(key)
                if ttl < 0:  # Expired but not cleaned
                    self.redis_client.delete(key)
                    cleaned += 1
            
            if cleaned > 0:
                logger.info(f"🧹 Cleaned up {cleaned} stale reservations")
            
            return cleaned
        
        except Exception as e:
            logger.error(f"Error cleaning up reservations: {e}")
            return 0


# Global singleton
global_coordinator = GlobalConnectionCoordinator()


# Convenience functions
def get_session():
    """Get a globally coordinated database session"""
    return global_coordinator.get_session()


def get_global_status() -> Dict:
    """Get global connection status"""
    return global_coordinator.get_global_status()


def print_global_status():
    """Print formatted global connection status"""
    status = get_global_status()
    
    print("\n" + "=" * 80)
    print("🌍 GLOBAL CONNECTION STATUS (ALL CONTAINERS)")
    print("=" * 80)
    
    print(f"\n📊 Supabase Configuration:")
    print(f"  Plan: {status['supabase_plan'].upper()}")
    print(f"  Max Connections: {status['max_connections']}")
    print(f"  Reserved for Supabase: {status['reserved_for_supabase']}")
    print(f"  Available for Apps: {status['available_for_apps']}")
    
    print(f"\n📈 Current Usage:")
    print(f"  Total Allocated: {status['total_allocated']}/{status['available_for_apps']}")
    print(f"  Remaining: {status['remaining']}")
    print(f"  Utilization: {status['utilization_pct']:.1f}%")
    
    print(f"\n🔧 Services:")
    for service_name, service_data in status['services'].items():
        print(f"\n  {service_name.upper()}:")
        print(f"    Total Connections: {service_data['total_connections']}")
        print(f"    Containers: {len(service_data['containers'])}")
        
        for container in service_data['containers']:
            print(f"      - {container['container_id'][:12]}... ({container['connections']} conn)")
    
    print("\n" + "=" * 80 + "\n")


def release_all_connections():
    """Release all connections (shutdown)"""
    global_coordinator.release_connections()

