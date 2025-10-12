"""
SQLAlchemy ORM models for workflow storage.

Defines 11 tables:
- workflows: Main workflow tracking
- workflow_metadata: Layer 1 data
- workflow_structure: Layer 2 data (JSON/nodes)
- workflow_content: Layer 3 data (explainer)
- video_transcripts: Video transcript data
- workflow_business_intelligence: Layer 4 data (business intelligence)
- workflow_community_data: Layer 5 data (community engagement)
- workflow_technical_details: Layer 6 data (technical specifications)
- workflow_performance_analytics: Layer 7 data (performance metrics)
- workflow_relationships: Layer 8 data (workflow relationships)
- workflow_enhanced_content: Layer 9 data (enhanced content)

Author: Dev1
Task: SCRAPE-008 + Comprehensive Expansion
Date: October 11, 2025 + October 12, 2025
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
    layer4_success = Column(Boolean, default=False)
    layer5_success = Column(Boolean, default=False)
    layer6_success = Column(Boolean, default=False)
    layer7_success = Column(Boolean, default=False)
    
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
    business_intelligence = relationship(
        "WorkflowBusinessIntelligence",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    community_data = relationship(
        "WorkflowCommunityData",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    technical_details = relationship(
        "WorkflowTechnicalDetails",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    performance_analytics = relationship(
        "WorkflowPerformanceAnalytics",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    relationships = relationship(
        "WorkflowRelationships",
        back_populates="workflow",
        uselist=False,
        cascade="all, delete-orphan"
    )
    enhanced_content = relationship(
        "WorkflowEnhancedContent",
        back_populates="workflow",
        uselist=False,
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


class WorkflowBusinessIntelligence(Base):
    """
    Business intelligence data for workflows (Layer 4).
    
    Stores revenue impact, cost savings, ROI estimates, business context,
    compliance, and governance information.
    """
    __tablename__ = 'workflow_business_intelligence'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False)
    
    # Revenue & Cost Metrics
    revenue_impact = Column(Float)
    cost_savings = Column(Float)
    efficiency_gains = Column(Float)
    time_savings = Column(Integer)
    resource_savings = Column(Float)
    error_reduction = Column(Float)
    productivity_gains = Column(Float)
    quality_improvements = Column(Float)
    customer_satisfaction = Column(Float)
    
    # Business Value Metrics
    business_value_score = Column(Float)
    roi_estimate = Column(Float)
    payback_period = Column(Integer)
    
    # Cost Breakdown
    implementation_cost = Column(Float)
    maintenance_cost = Column(Float)
    support_cost = Column(Float)
    training_cost = Column(Float)
    customization_cost = Column(Float)
    integration_cost = Column(Float)
    
    # Business Context
    business_function = Column(String(100))
    business_process = Column(String(100))
    business_outcome = Column(String(100))
    business_metric = Column(String(100))
    business_kpi = Column(String(100))
    business_goal = Column(String(100))
    
    # Business Details
    business_requirement = Column(Text)
    business_constraint = Column(Text)
    business_risk = Column(Text)
    business_opportunity = Column(Text)
    business_challenge = Column(Text)
    business_solution = Column(Text)
    business_benefit = Column(Text)
    business_advantage = Column(Text)
    business_competitive_advantage = Column(Text)
    
    # Business Transformation
    business_innovation = Column(Text)
    business_transformation = Column(Text)
    business_digitalization = Column(Text)
    business_automation = Column(Text)
    business_optimization = Column(Text)
    business_standardization = Column(Text)
    
    # Compliance & Governance
    business_compliance = Column(Text)
    business_governance = Column(Text)
    business_audit = Column(Text)
    business_security = Column(Text)
    business_privacy = Column(Text)
    business_ethics = Column(Text)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowBusinessIntelligence(workflow_id={self.workflow_id})>"


class WorkflowCommunityData(Base):
    """
    Community engagement data for workflows (Layer 5).
    
    Stores social metrics, engagement analytics, community ratings,
    and community growth data.
    """
    __tablename__ = 'workflow_community_data'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False)
    
    # Engagement Metrics
    comments_count = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    questions_count = Column(Integer, default=0)
    answers_count = Column(Integer, default=0)
    discussions_count = Column(Integer, default=0)
    mentions_count = Column(Integer, default=0)
    
    # Social Metrics
    bookmarks_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)
    follows_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    clones_count = Column(Integer, default=0)
    remixes_count = Column(Integer, default=0)
    
    # Usage Metrics
    downloads_count = Column(Integer, default=0)
    installs_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    
    # Community Ratings
    community_rating = Column(Float)
    community_rating_count = Column(Integer, default=0)
    
    # Community Analytics
    community_engagement_score = Column(Float)
    community_activity_score = Column(Float)
    community_growth_rate = Column(Float)
    community_retention_rate = Column(Float)
    community_sentiment_score = Column(Float)
    community_satisfaction_score = Column(Float)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowCommunityData(workflow_id={self.workflow_id})>"


class WorkflowTechnicalDetails(Base):
    """
    Technical specifications and details for workflows (Layer 6).
    
    Stores API information, security requirements, performance metrics,
    error handling patterns, and technical capabilities.
    """
    __tablename__ = 'workflow_technical_details'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False)
    
    # API Information
    api_endpoints = Column(JSONB)
    api_authentication_types = Column(JSONB)
    api_rate_limits = Column(JSONB)
    
    # Security & Credentials
    credential_requirements = Column(JSONB)
    credential_types = Column(JSONB)
    security_requirements = Column(JSONB)
    
    # Performance Metrics
    performance_metrics = Column(JSONB)
    execution_time = Column(Float)
    memory_usage = Column(Float)
    cpu_usage = Column(Float)
    
    # Error Handling
    error_handling_patterns = Column(JSONB)
    retry_mechanisms = Column(JSONB)
    fallback_strategies = Column(JSONB)
    
    # Data Processing
    data_validation_rules = Column(JSONB)
    data_transformation_rules = Column(JSONB)
    
    # Workflow Structure
    workflow_triggers = Column(JSONB)
    workflow_conditions = Column(JSONB)
    workflow_actions = Column(JSONB)
    workflow_branches = Column(JSONB)
    workflow_loops = Column(JSONB)
    workflow_parallelism = Column(JSONB)
    
    # Workflow Management
    workflow_error_handling = Column(JSONB)
    workflow_logging = Column(JSONB)
    workflow_monitoring = Column(JSONB)
    workflow_backup_strategies = Column(JSONB)
    workflow_recovery_strategies = Column(JSONB)
    workflow_scaling_strategies = Column(JSONB)
    workflow_optimization_strategies = Column(JSONB)
    
    # Development & Deployment
    workflow_testing_strategies = Column(JSONB)
    workflow_deployment_strategies = Column(JSONB)
    workflow_maintenance_strategies = Column(JSONB)
    workflow_support_strategies = Column(JSONB)
    
    # Documentation & Examples
    workflow_documentation_level = Column(String(50))
    workflow_tutorial_level = Column(String(50))
    workflow_example_count = Column(Integer, default=0)
    workflow_template_count = Column(Integer, default=0)
    
    # Capability Levels
    workflow_customization_level = Column(String(50))
    workflow_configuration_level = Column(String(50))
    workflow_integration_level = Column(String(50))
    workflow_extension_level = Column(String(50))
    workflow_automation_level = Column(String(50))
    workflow_intelligence_level = Column(String(50))
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowTechnicalDetails(workflow_id={self.workflow_id})>"


class WorkflowPerformanceAnalytics(Base):
    """
    Performance analytics and metrics for workflows (Layer 7).
    
    Stores execution metrics, performance data, usage analytics,
    error analytics, and optimization recommendations.
    """
    __tablename__ = 'workflow_performance_analytics'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False)
    
    # Execution Metrics
    execution_success_rate = Column(Float)
    execution_failure_rate = Column(Float)
    execution_error_rate = Column(Float)
    
    # Performance Data
    performance_benchmarks = Column(JSONB)
    performance_metrics = Column(JSONB)
    performance_trends = Column(JSONB)
    
    # Usage Analytics
    usage_statistics = Column(JSONB)
    usage_patterns = Column(JSONB)
    usage_analytics = Column(JSONB)
    
    # Error Analytics
    error_analytics = Column(JSONB)
    error_patterns = Column(JSONB)
    error_trends = Column(JSONB)
    
    # Optimization
    optimization_opportunities = Column(JSONB)
    optimization_recommendations = Column(JSONB)
    
    # Scaling
    scaling_requirements = Column(JSONB)
    scaling_limitations = Column(JSONB)
    scaling_recommendations = Column(JSONB)
    
    # Monitoring
    monitoring_requirements = Column(JSONB)
    monitoring_metrics = Column(JSONB)
    monitoring_alerts = Column(JSONB)
    
    # Cost Analysis
    maintenance_cost = Column(Float)
    support_cost = Column(Float)
    training_cost = Column(Float)
    documentation_cost = Column(Float)
    testing_cost = Column(Float)
    deployment_cost = Column(Float)
    integration_cost = Column(Float)
    customization_cost = Column(Float)
    security_cost = Column(Float)
    compliance_cost = Column(Float)
    governance_cost = Column(Float)
    audit_cost = Column(Float)
    backup_cost = Column(Float)
    
    # Requirements
    maintenance_requirements = Column(JSONB)
    support_requirements = Column(JSONB)
    training_requirements = Column(JSONB)
    documentation_requirements = Column(JSONB)
    testing_requirements = Column(JSONB)
    deployment_requirements = Column(JSONB)
    integration_requirements = Column(JSONB)
    customization_requirements = Column(JSONB)
    security_requirements = Column(JSONB)
    compliance_requirements = Column(JSONB)
    governance_requirements = Column(JSONB)
    audit_requirements = Column(JSONB)
    backup_requirements = Column(JSONB)
    
    # Levels
    support_level = Column(String(50))
    training_level = Column(String(50))
    documentation_level = Column(String(50))
    testing_level = Column(String(50))
    deployment_level = Column(String(50))
    integration_level = Column(String(50))
    customization_level = Column(String(50))
    security_level = Column(String(50))
    compliance_level = Column(String(50))
    governance_level = Column(String(50))
    audit_level = Column(String(50))
    backup_level = Column(String(50))
    
    # Schedules
    maintenance_schedule = Column(JSONB)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowPerformanceAnalytics(workflow_id={self.workflow_id})>"


class WorkflowRelationships(Base):
    """
    Workflow relationships and dependencies (Layer 8).
    
    Stores family relationships, dependencies, similarities,
    versions, and collaboration data.
    """
    __tablename__ = 'workflow_relationships'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False)
    
    # Family Relationships
    parent_workflows = Column(JSONB)
    child_workflows = Column(JSONB)
    sibling_workflows = Column(JSONB)
    
    # Dependencies
    dependent_workflows = Column(JSONB)
    dependency_workflows = Column(JSONB)
    prerequisite_workflows = Column(JSONB)
    
    # Similarity & Alternatives
    related_workflows = Column(JSONB)
    similar_workflows = Column(JSONB)
    alternative_workflows = Column(JSONB)
    
    # Version Control
    workflow_versions = Column(JSONB)
    workflow_branches = Column(JSONB)
    workflow_forks = Column(JSONB)
    
    # Derivative Works
    workflow_clones = Column(JSONB)
    workflow_remixes = Column(JSONB)
    workflow_adaptations = Column(JSONB)
    
    # Extensions & Integrations
    workflow_integrations = Column(JSONB)
    workflow_extensions = Column(JSONB)
    workflow_plugins = Column(JSONB)
    
    # Support Materials
    workflow_templates = Column(JSONB)
    workflow_examples = Column(JSONB)
    workflow_tutorials = Column(JSONB)
    workflow_documentation = Column(JSONB)
    workflow_guides = Column(JSONB)
    workflow_manuals = Column(JSONB)
    
    # Community & Support
    workflow_support = Column(JSONB)
    workflow_community = Column(JSONB)
    workflow_forums = Column(JSONB)
    
    # Updates & Maintenance
    workflow_updates = Column(JSONB)
    workflow_patches = Column(JSONB)
    workflow_fixes = Column(JSONB)
    workflow_migrations = Column(JSONB)
    workflow_upgrades = Column(JSONB)
    workflow_downgrades = Column(JSONB)
    
    # Lifecycle
    workflow_retirements = Column(JSONB)
    workflow_deprecations = Column(JSONB)
    workflow_archivals = Column(JSONB)
    
    # Legal & Attribution
    workflow_licenses = Column(JSONB)
    workflow_permissions = Column(JSONB)
    workflow_restrictions = Column(JSONB)
    workflow_ownership = Column(JSONB)
    workflow_attribution = Column(JSONB)
    workflow_credits = Column(JSONB)
    
    # Collaboration
    workflow_collaboration = Column(JSONB)
    workflow_contributors = Column(JSONB)
    workflow_maintainers = Column(JSONB)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowRelationships(workflow_id={self.workflow_id})>"


class WorkflowEnhancedContent(Base):
    """
    Enhanced content and media for workflows (Layer 9).
    
    Stores tutorial content, documentation, videos, images,
    diagrams, and example content.
    """
    __tablename__ = 'workflow_enhanced_content'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False)
    
    # Enhanced Content
    tutorial_content = Column(Text)
    documentation_content = Column(Text)
    faq_content = Column(Text)
    troubleshooting_content = Column(Text)
    best_practices_content = Column(Text)
    
    # Video Content
    video_count = Column(Integer, default=0)
    video_duration = Column(Integer, default=0)
    video_quality = Column(String(50))
    video_views = Column(Integer, default=0)
    
    # Image Content
    image_count = Column(Integer, default=0)
    image_types = Column(JSONB)
    image_quality = Column(String(50))
    image_alt_text = Column(JSONB)
    
    # Diagram Content
    diagram_count = Column(Integer, default=0)
    flowchart_count = Column(Integer, default=0)
    architecture_count = Column(Integer, default=0)
    
    # Example Content
    code_example_count = Column(Integer, default=0)
    configuration_example_count = Column(Integer, default=0)
    use_case_example_count = Column(Integer, default=0)
    business_case_example_count = Column(Integer, default=0)
    integration_example_count = Column(Integer, default=0)
    customization_example_count = Column(Integer, default=0)
    performance_example_count = Column(Integer, default=0)
    security_example_count = Column(Integer, default=0)
    maintenance_example_count = Column(Integer, default=0)
    support_example_count = Column(Integer, default=0)
    community_example_count = Column(Integer, default=0)
    feedback_example_count = Column(Integer, default=0)
    update_example_count = Column(Integer, default=0)
    version_example_count = Column(Integer, default=0)
    migration_example_count = Column(Integer, default=0)
    upgrade_example_count = Column(Integer, default=0)
    troubleshooting_example_count = Column(Integer, default=0)
    debugging_example_count = Column(Integer, default=0)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowEnhancedContent(workflow_id={self.workflow_id})>"
