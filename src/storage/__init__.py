"""
Storage package for n8n.io workflow data persistence.

Provides PostgreSQL database layer with SQLAlchemy ORM,
repository pattern for CRUD operations, and connection pooling.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

from src.storage.database import (
    engine,
    SessionLocal,
    get_session,
    init_database,
    drop_all_tables,
    get_database_stats
)

from src.storage.models import (
    Base,
    Workflow,
    WorkflowMetadata,
    WorkflowStructure,
    WorkflowContent,
    VideoTranscript
)

from src.storage.repository import WorkflowRepository

__all__ = [
    # Database
    'engine',
    'SessionLocal', 
    'get_session',
    'init_database',
    'drop_all_tables',
    'get_database_stats',
    
    # Models
    'Base',
    'Workflow',
    'WorkflowMetadata',
    'WorkflowStructure', 
    'WorkflowContent',
    'VideoTranscript',
    
    # Repository
    'WorkflowRepository',
]

__version__ = '1.0.0'
