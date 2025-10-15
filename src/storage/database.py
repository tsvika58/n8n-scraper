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

# Create engine with connection pooling (OPTIMIZED for SCRAPE-014)
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=30,              # Increased from 10 (3x capacity)
    max_overflow=40,           # Increased from 20 (2x overflow)
    pool_timeout=30,           # Seconds to wait for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connections before using
    echo=False,                # Set True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_session() as session:
            session.query(Workflow).all()
    
    Automatically commits on success, rolls back on error, closes session.
    """
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
    Get database connection pool statistics.
    
    Returns:
        dict: Connection pool stats (size, checked_in, checked_out, overflow)
    """
    pool = engine.pool
    return {
        'pool_size': pool.size(),
        'checked_in': pool.checkedin(),
        'checked_out': pool.checkedout(),
        'overflow': pool.overflow(),
        'total_connections': pool.size() + pool.overflow()
    }

# Test connection on import
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    if db_host:
        logger.info(f"✅ Database connected: {db_host}:{db_port}/{db_name}")
    else:
        logger.info("✅ Database connected: localhost")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    # Don't raise to allow graceful fallback
