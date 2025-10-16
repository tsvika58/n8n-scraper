"""
Database connection and session management.

Provides SQLAlchemy engine, session factory, and context managers
for clean database access with connection pooling.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from loguru import logger

# Load environment variables from .env file
load_dotenv()

# Construct DATABASE_URL from individual environment variables
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if not all([db_host, db_name, db_user, db_password]):
    logger.error("❌ Database configuration not found in environment variables. Falling back to localhost.")
    DATABASE_URL = 'postgresql://scraper_user:scraper_pass@localhost:5432/n8n_scraper'
else:
    import urllib.parse
    encoded_password = urllib.parse.quote_plus(db_password)
    DATABASE_URL = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    logger.info(f"🔧 Setting up database connection to: {db_host}:{db_port}/{db_name}")

# Connection pool configuration with reserved connections for ad-hoc work
TOTAL_CONNECTIONS = 60              # Total Supabase connection limit
RESERVED_CONNECTIONS = 5            # Always keep 5 connections available for ad-hoc work
AUTOMATION_POOL_SIZE = TOTAL_CONNECTIONS - RESERVED_CONNECTIONS - 5  # 50 connections for automation
AUTOMATION_MAX_OVERFLOW = 5         # Small overflow buffer

# Create engine with connection pooling (OPTIMIZED for PRODUCTION with RESERVED CONNECTIONS)
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=AUTOMATION_POOL_SIZE,        # 50 connections (leaving 5 reserved + 5 buffer)
    max_overflow=AUTOMATION_MAX_OVERFLOW,  # 5 overflow (total max 55)
    pool_timeout=60,                       # Increased timeout for production
    pool_recycle=1800,                     # 30 minutes recycle (more frequent)
    pool_pre_ping=True,                    # Verify connections before using
    echo=False,                            # Disable SQL logging in production
    connect_args={
        "options": "-c default_transaction_isolation=read_committed"
    }
)

# Session factory for automation/scraping work
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Track connection usage for monitoring
_connection_usage = {
    'automation_requests': 0,
    'adhoc_available': RESERVED_CONNECTIONS,
    'last_check': None
}

@contextmanager
def get_session(priority: str = 'automation') -> Generator[Session, None, None]:
    """
    Context manager for database sessions with connection reservation.
    
    Args:
        priority: 'automation' (default) or 'adhoc' 
                  'automation' uses the main pool (50 connections + 5 overflow)
                  'adhoc' guaranteed to have reserved connections available
    
    Usage:
        # Automation/scraping work
        with get_session() as session:
            session.query(Workflow).all()
        
        # Ad-hoc work (always has reserved connections)
        with get_session(priority='adhoc') as session:
            session.query(Workflow).all()
    
    Automatically commits on success, rolls back on error, closes session.
    
    Note: The pool is configured to use max 55 connections (50 + 5 overflow),
          leaving 5 connections reserved for ad-hoc work out of 60 total.
    """
    _connection_usage['automation_requests'] += 1
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def init_database():
    """
    Initialize database by creating all tables.
    
    Note: In production, use Alembic migrations instead.
    This is useful for testing and development.
    """
    from n8n_shared.models import Base
    
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

def drop_all_tables():
    """
    Drop all tables from database.
    
    WARNING: This deletes all data!
    Only use in testing/development.
    """
    from n8n_shared.models import Base
    
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")

def get_database_stats() -> dict:
    """
    Get database connection pool statistics with reserved connection tracking.
    
    Returns:
        dict: Connection pool stats including reserved connections
    """
    pool = engine.pool
    automation_in_use = pool.checkedout()
    automation_available = pool.size() - automation_in_use + pool.overflow()
    
    return {
        # Pool configuration
        'total_supabase_limit': TOTAL_CONNECTIONS,
        'reserved_for_adhoc': RESERVED_CONNECTIONS,
        'automation_pool_size': AUTOMATION_POOL_SIZE,
        'automation_max_overflow': AUTOMATION_MAX_OVERFLOW,
        
        # Current usage
        'automation_in_use': automation_in_use,
        'automation_available': automation_available,
        'automation_overflow_active': pool.overflow(),
        
        # Reserved connections (always available for ad-hoc)
        'adhoc_reserved': RESERVED_CONNECTIONS,
        'adhoc_guaranteed_available': RESERVED_CONNECTIONS,
        
        # Total system
        'total_automation_capacity': AUTOMATION_POOL_SIZE + AUTOMATION_MAX_OVERFLOW,
        'total_in_use': automation_in_use,
        'total_available': RESERVED_CONNECTIONS + automation_available,
        
        # Pool internals
        'pool_checked_in': pool.checkedin(),
        'pool_checked_out': pool.checkedout(),
        
        # Usage tracking
        'automation_requests': _connection_usage['automation_requests']
    }

def print_connection_status():
    """Print a human-readable connection status report."""
    stats = get_database_stats()
    
    print("🔌 DATABASE CONNECTION STATUS")
    print("=" * 60)
    print(f"📊 Total Supabase Limit: {stats['total_supabase_limit']} connections")
    print(f"   └─ Reserved for Ad-hoc: {stats['reserved_for_adhoc']} (always available)")
    print(f"   └─ Automation Pool: {stats['automation_pool_size']} + {stats['automation_max_overflow']} overflow")
    print()
    print(f"🤖 Automation (Scraping/Monitoring):")
    print(f"   ├─ In Use: {stats['automation_in_use']}/{stats['total_automation_capacity']}")
    print(f"   ├─ Available: {stats['automation_available']}")
    print(f"   └─ Overflow Active: {stats['automation_overflow_active']}")
    print()
    print(f"👤 Ad-hoc (Development/Manual):")
    print(f"   └─ Guaranteed Available: {stats['adhoc_guaranteed_available']} connections")
    print()
    
    # Warning if automation is using too many connections
    if stats['automation_in_use'] > AUTOMATION_POOL_SIZE:
        print(f"⚠️  WARNING: Automation using overflow ({stats['automation_overflow_active']} overflow connections)")
    
    if stats['automation_in_use'] >= stats['total_automation_capacity']:
        print(f"🚨 CRITICAL: Automation pool exhausted! Ad-hoc connections still available.")
    else:
        print(f"✅ Healthy: {stats['adhoc_guaranteed_available']} connections always available for ad-hoc work")
    
    print("=" * 60)

# Test connection on import and display configuration
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    if db_host:
        logger.info(f"✅ Database connected: {db_host}:{db_port}/{db_name}")
        logger.info(f"🔌 Connection pool: {AUTOMATION_POOL_SIZE} base + {AUTOMATION_MAX_OVERFLOW} overflow (max {AUTOMATION_POOL_SIZE + AUTOMATION_MAX_OVERFLOW})")
        logger.info(f"🔒 Reserved for ad-hoc: {RESERVED_CONNECTIONS} connections (always available)")
    else:
        logger.info("✅ Database connected: localhost")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    # Don't raise to allow graceful fallback
