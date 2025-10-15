"""
Basic models for n8n workflow scraping
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    layer2_success = Column(Boolean, default=False)

class WorkflowMetadata(Base):
    __tablename__ = "workflow_metadata"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(255), unique=True, nullable=False)
    layer1_5_extracted_at = Column(DateTime)
    layer1_5_metadata = Column(JSON)
    content_length = Column(Integer)

class WorkflowContent(Base):
    __tablename__ = "workflow_content"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(255), unique=True, nullable=False)
    layer3_success = Column(Boolean, default=False)
    layer3_extracted_at = Column(DateTime)
    video_count = Column(Integer, default=0)
    transcript_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)

# Additional models as needed
WorkflowStructure = Workflow
VideoTranscript = WorkflowContent
WorkflowBusinessIntelligence = Workflow
WorkflowCommunityData = Workflow
WorkflowTechnicalDetails = Workflow
