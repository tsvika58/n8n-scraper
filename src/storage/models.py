"""
SQLAlchemy ORM models for workflow storage.

Defines 5 tables:
- workflows: Main workflow tracking
- workflow_metadata: Layer 1 data
- workflow_structure: Layer 2 data (JSON/nodes)
- workflow_content: Layer 3 data (explainer)
- video_transcripts: Video transcript data

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Workflow(Base):
    """
    Main workflow table.
    
    Tracks workflow processing status and serves as the root
    for all related data (metadata, structure, content, transcripts).
    """
    __tablename__ = 'workflows'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), unique=True, nullable=False, index=True)
    url = Column(Text, nullable=False)
    
    # Processing Status
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processing_time = Column(Float)  # seconds
    quality_score = Column(Float, index=True)
    
    # Layer Success Flags
    layer1_success = Column(Boolean, default=False)
    layer2_success = Column(Boolean, default=False)
    layer3_success = Column(Boolean, default=False)
    
    # Error Tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships (one-to-one for metadata/structure/content, one-to-many for transcripts)
    workflow_metadata = relationship(
        "WorkflowMetadata",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    structure = relationship(
        "WorkflowStructure",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    content = relationship(
        "WorkflowContent",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    transcripts = relationship(
        "VideoTranscript",
        back_populates="workflow",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Workflow(id={self.workflow_id}, quality={self.quality_score})>"


class WorkflowMetadata(Base):
    """
    Layer 1: Workflow metadata extracted from n8n.io listing page.
    
    Stores basic workflow information, author details, and taxonomy.
    """
    __tablename__ = 'workflow_metadata'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(
        String(50),
        ForeignKey('workflows.workflow_id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )
    
    # Basic Info
    title = Column(Text, index=True)
    description = Column(Text)
    use_case = Column(Text)
    
    # Author
    author_name = Column(String(255))
    author_url = Column(Text)
    
    # Engagement
    views = Column(Integer)
    shares = Column(Integer)
    
    # Taxonomy (JSONB arrays)
    categories = Column(JSONB)  # ["Sales", "Marketing"]
    tags = Column(JSONB)        # ["email", "automation"]
    
    # Timestamps
    workflow_created_at = Column(DateTime)
    workflow_updated_at = Column(DateTime)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Complete Layer 1 Data
    raw_metadata = Column(JSONB)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="workflow_metadata")
    
    # Indexes
    __table_args__ = (
        Index('idx_categories_gin', 'categories', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<WorkflowMetadata(workflow_id={self.workflow_id}, title={self.title})>"


class WorkflowStructure(Base):
    """
    Layer 2: Workflow structure (JSON, nodes, connections).
    
    Stores the complete n8n workflow definition with node data.
    May be missing if workflow was deleted (60% success rate).
    """
    __tablename__ = 'workflow_structure'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(
        String(50),
        ForeignKey('workflows.workflow_id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )
    
    # Structure Summary
    node_count = Column(Integer, index=True)
    connection_count = Column(Integer)
    node_types = Column(JSONB)  # ["httpRequest", "set", "if"]
    
    # Extraction Method
    extraction_type = Column(String(50))  # 'full', 'fallback', 'failed'
    fallback_used = Column(Boolean, default=False)
    
    # Complete Workflow JSON
    workflow_json = Column(JSONB)  # Full n8n workflow definition
    
    # Timestamp
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="structure")
    
    # Indexes
    __table_args__ = (
        Index('idx_node_types_gin', 'node_types', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<WorkflowStructure(workflow_id={self.workflow_id}, nodes={self.node_count})>"


class WorkflowContent(Base):
    """
    Layer 3: Workflow explainer content and instructions.
    
    Stores text extracted from the workflow detail page including
    explainer content, setup instructions, and media flags.
    """
    __tablename__ = 'workflow_content'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(
        String(50),
        ForeignKey('workflows.workflow_id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )
    
    # Explainer Content
    explainer_text = Column(Text)
    explainer_html = Column(Text)
    
    # Instructions
    setup_instructions = Column(Text)
    use_instructions = Column(Text)
    
    # Media Flags
    has_videos = Column(Boolean, default=False, index=True)
    video_count = Column(Integer, default=0)
    has_iframes = Column(Boolean, default=False)
    iframe_count = Column(Integer, default=0)
    
    # Complete Layer 3 Data
    raw_content = Column(JSONB)
    
    # Timestamp
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="content")
    
    def __repr__(self):
        return f"<WorkflowContent(workflow_id={self.workflow_id}, has_videos={self.has_videos})>"


class VideoTranscript(Base):
    """
    Video transcripts (one-to-many with workflows).
    
    A workflow can have multiple videos, each with its own transcript.
    """
    __tablename__ = 'video_transcripts'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(
        String(50),
        ForeignKey('workflows.workflow_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Video Info
    video_url = Column(Text, nullable=False)
    video_id = Column(String(100))
    platform = Column(String(50), index=True)  # 'youtube', 'vimeo'
    
    # Transcript Data
    transcript_text = Column(Text)
    transcript_json = Column(JSONB)  # Structured with timestamps
    
    # Metadata
    duration = Column(Integer)  # seconds
    language = Column(String(10))  # 'en', 'es'
    
    # Timestamp
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="transcripts")
    
    def __repr__(self):
        return f"<VideoTranscript(workflow_id={self.workflow_id}, platform={self.platform})>"
