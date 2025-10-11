"""
N8N Workflow Scraper - Database Schema
Defines SQLite database structure for workflow storage.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()


class Workflow(Base):
    """
    Main workflow table storing all extracted data from 3 layers.
    """
    __tablename__ = 'workflows'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(50), unique=True, nullable=False, index=True)  # n8n workflow ID
    
    # Layer 1: Page Metadata
    workflow_url = Column(String(500), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(200))
    primary_category = Column(String(100), index=True)
    secondary_categories = Column(JSON)  # List of secondary categories
    node_tags = Column(JSON)  # Integration badges (e.g., ["Slack", "OpenAI"])
    general_tags = Column(JSON)  # User tags
    description = Column(Text)
    use_case = Column(Text)
    difficulty_level = Column(String(50))  # beginner, intermediate, advanced
    
    # Engagement metrics
    views = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    created_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)
    
    # Setup information
    setup_instructions = Column(Text)
    prerequisites = Column(JSON)  # List of requirements
    estimated_setup_time = Column(String(50))
    
    # Layer 2: Workflow Structure
    workflow_json = Column(JSON, nullable=True)  # Complete n8n workflow JSON
    node_count = Column(Integer, default=0)
    node_types = Column(JSON)  # List of node types used
    connections = Column(JSON)  # Connection mapping
    has_credentials = Column(Boolean, default=False)
    trigger_type = Column(String(100))  # webhook, schedule, manual, etc.
    execution_mode = Column(String(50))  # automatic, manual
    
    # Layer 3: Explainer Content
    introduction = Column(Text)  # Workflow introduction
    overview = Column(Text)  # High-level overview
    tutorial_text = Column(Text)  # Complete tutorial text (aggregated)
    tutorial_sections = Column(JSON)  # Hierarchical sections
    step_by_step = Column(JSON)  # Step-by-step guide
    best_practices = Column(JSON)  # List of best practice tips
    common_pitfalls = Column(JSON)  # Common mistakes to avoid
    
    # Multimodal Content
    image_urls = Column(JSON)  # List of image URLs
    image_local_paths = Column(JSON)  # Local file paths
    ocr_text = Column(Text)  # Aggregated OCR text from images
    video_urls = Column(JSON)  # List of video URLs
    video_transcripts = Column(JSON)  # Video transcripts
    code_snippets = Column(JSON)  # Extracted code examples
    
    # Processing Metadata
    scrape_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time = Column(Float)  # Total seconds for all 3 layers
    layer1_time = Column(Float)  # Layer 1 extraction time
    layer2_time = Column(Float)  # Layer 2 extraction time
    layer3_time = Column(Float)  # Layer 3 extraction time
    
    success = Column(Boolean, default=False)
    layer1_success = Column(Boolean, default=False)
    layer2_success = Column(Boolean, default=False)
    layer3_success = Column(Boolean, default=False)
    
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Quality Scoring
    completeness_score = Column(Float, default=0.0)  # 0-100
    quality_score = Column(Float, default=0.0)  # 0-100
    data_quality_score = Column(Float, default=0.0)  # 0-100
    consistency_score = Column(Float, default=0.0)  # 0-100
    
    def __repr__(self):
        return f"<Workflow(id={self.workflow_id}, title='{self.title[:50]}...', success={self.success})>"


class ScrapingSession(Base):
    """
    Tracks scraping sessions for monitoring and analytics.
    """
    __tablename__ = 'scraping_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_name = Column(String(200), nullable=False)
    session_type = Column(String(50))  # test, integration, production
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Workflow counts
    total_workflows = Column(Integer, default=0)
    successful_workflows = Column(Integer, default=0)
    failed_workflows = Column(Integer, default=0)
    skipped_workflows = Column(Integer, default=0)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0)  # Percentage
    average_time = Column(Float, default=0.0)  # Average seconds per workflow
    median_time = Column(Float, nullable=True)
    min_time = Column(Float, nullable=True)
    max_time = Column(Float, nullable=True)
    
    # Quality metrics
    average_completeness = Column(Float, default=0.0)
    average_quality = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default='running')  # running, completed, failed, paused
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    # Configuration
    rate_limit = Column(Float, default=2.0)  # Requests per second
    concurrent_limit = Column(Integer, default=3)  # Concurrent extractions
    
    # Notes
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Session(name='{self.session_name}', status='{self.status}', workflows={self.successful_workflows}/{self.total_workflows})>"


def init_db(database_url="sqlite:///data/workflows.db", echo=False):
    """
    Initialize database with schema.
    
    Args:
        database_url: SQLAlchemy database URL
        echo: Whether to echo SQL statements
        
    Returns:
        SQLAlchemy engine
    """
    # Ensure data directory exists
    db_path = Path(database_url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine
    engine = create_engine(
        database_url,
        echo=echo,
        connect_args={
            "check_same_thread": False,  # Allow multi-threading
            "timeout": 30  # 30-second lock timeout
        }
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    return engine


def get_session(database_url="sqlite:///data/workflows.db"):
    """
    Get database session for operations.
    
    Args:
        database_url: SQLAlchemy database URL
        
    Returns:
        SQLAlchemy session
    """
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )
    
    Session = sessionmaker(bind=engine)
    return Session()


def get_engine(database_url="sqlite:///data/workflows.db"):
    """
    Get database engine.
    
    Args:
        database_url: SQLAlchemy database URL
        
    Returns:
        SQLAlchemy engine
    """
    return create_engine(
        database_url,
        echo=False,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )




