# 🗄️ **TASK BRIEF: SCRAPE-008 - PostgreSQL Storage Layer**

**TASK BRIEF TEMPLATE v1.0 - RND to Developer**

---

## 📋 **TASK HEADER**

| Field | Value |
|-------|-------|
| **Task ID** | SCRAPE-008 |
| **Task Name** | Storage Layer (PostgreSQL Database) |
| **Sprint** | Sprint 2 - Core Development |
| **Assignee** | Dev1 |
| **Priority** | 🔴 Critical (blocks Phase 2) |
| **Estimated** | 6 hours (1 day) |
| **Due Date** | October 12, 2025 (Day 5) |
| **Dependencies** | None (can start immediately) ✅ |
| **Notion URL** | https://www.notion.so/289d7960213a813f89a8eae1d858e80c |
| **Created** | October 11, 2025, 12:15 PM |
| **Created By** | RND Manager |

---

## 📊 **1. STATUS**

### **Sprint Context:**
- **Sprint:** Sprint 2 - Core Development (Days 4-10)
- **Phase:** Phase 1 - Foundation (Parallel Track A)
- **Current Day:** Day 4 (October 11, 2025)
- **Sprint Progress:** 48% complete (10/21 tasks overall)

### **Task Health:**
- **Status:** 🟢 Ready to Start
- **Blockers:** None
- **Dependencies Met:** Yes (Sprint 1 complete)
- **Resources:** All available

### **Progress Tracking:**
- **Phase 1:** Not started (0%)
- **Phase 2:** Not started (0%)
- **Phase 3:** Not started (0%)
- **Overall:** 0% complete

### **Parallel Execution:**
- **Your Track (A):** SCRAPE-008 - Storage Layer
- **Track B:** Dev2 working on SCRAPE-009 (Unit Testing)
- **Track C:** RND working on SCRAPE-012 (Export Pipeline)
- **All 3 tracks run in parallel!** No waiting needed.

---

## 🎯 **2. PRIORITIES**

### **Mission:**
Build production-grade PostgreSQL database layer to store workflow data from all 3 extraction layers (Layer 1 metadata, Layer 2 JSON/nodes, Layer 3 content).

### **Three Implementation Phases:**

#### **Phase 1: Schema Design & Setup (1.5 hours)**
**Objective:** Design database schema and set up PostgreSQL infrastructure.

**Tasks:**
1. Install PostgreSQL locally (if needed)
2. Create `n8n_scraper` database
3. Design 5-table schema (workflows, metadata, structure, content, transcripts)
4. Set up Alembic for migrations
5. Create initial migration
6. Document schema decisions

**Deliverables:**
- PostgreSQL database running
- Alembic configured (`alembic/` directory)
- Initial migration created
- Schema diagram/documentation

**Success Check:**
- [ ] PostgreSQL accessible
- [ ] Database `n8n_scraper` created
- [ ] `alembic init alembic` completed
- [ ] Can run `alembic upgrade head`

---

#### **Phase 2: Implementation (3 hours)**
**Objective:** Build SQLAlchemy ORM models and repository pattern for CRUD operations.

**Tasks:**
1. Create database connection management (`src/storage/database.py`)
2. Build 5 SQLAlchemy models (`src/storage/models.py`)
3. Implement repository pattern (`src/storage/repository.py`)
4. Add connection pooling configuration
5. Create package exports (`src/storage/__init__.py`)

**Deliverables:**
- `src/storage/database.py` - Engine, session management
- `src/storage/models.py` - 5 ORM models with relationships
- `src/storage/repository.py` - WorkflowRepository with CRUD
- Connection pooling working (10 connections)

**Success Check:**
- [ ] Can create engine and sessions
- [ ] All 5 models defined with relationships
- [ ] Repository has 5+ CRUD methods
- [ ] Can insert and query workflows

---

#### **Phase 3: Testing & Validation (1.5 hours)**
**Objective:** Validate implementation with comprehensive tests.

**Tasks:**
1. Write 10+ unit tests for models and repository
2. Create integration test (store 100 workflows)
3. Run performance validation (<100ms queries)
4. Test with real Sprint 1 E2E pipeline data
5. Document repository API

**Deliverables:**
- `tests/unit/test_storage.py` - 10+ unit tests
- `tests/integration/test_storage_integration.py` - Integration test
- Performance validation results
- Repository API documentation

**Success Check:**
- [ ] 10+ unit tests passing
- [ ] 100 workflows stored successfully
- [ ] Query performance <100ms
- [ ] Integration with E2E pipeline working

---

## 💻 **3. CURSOR HANDOFF**

### **What You're Building:**

A production-grade PostgreSQL storage layer that persists all workflow extraction data (Layers 1, 2, 3) with:
- 5-table normalized schema
- SQLAlchemy ORM models
- Repository pattern for clean data access
- Connection pooling for performance
- Alembic migrations for schema management

### **Key Files to Create:**

**1. Database Infrastructure:**
- `src/storage/__init__.py` - Package exports
- `src/storage/database.py` - Connection management (150 lines)
- `src/storage/models.py` - 5 SQLAlchemy models (300 lines)
- `src/storage/repository.py` - CRUD operations (250 lines)

**2. Migrations:**
- `alembic/` - Alembic directory structure
- `alembic/versions/001_initial_schema.py` - Initial migration

**3. Tests:**
- `tests/unit/test_storage.py` - Unit tests (200 lines)
- `tests/integration/test_storage_integration.py` - Integration test (100 lines)

**4. Configuration:**
- `alembic.ini` - Alembic configuration
- `.env` update - Add `DATABASE_URL`

### **Critical Actions:**

**DO:**
- ✅ Use PostgreSQL (not SQLite)
- ✅ Use JSONB for flexible fields (categories, node_types, etc.)
- ✅ Implement repository pattern (not direct ORM usage)
- ✅ Add connection pooling (10 connections)
- ✅ Use Alembic for migrations
- ✅ Store ALL extraction data (no data loss)
- ✅ Add indexes on frequently queried columns
- ✅ Use foreign keys with cascade delete

**DON'T:**
- ❌ Use SQLite (not production-ready)
- ❌ Expose ORM models directly (use repository)
- ❌ Store JSON as strings (use JSONB)
- ❌ Skip migrations (use Alembic)
- ❌ Forget connection pooling
- ❌ Lose any extraction data

### **Success Criteria:**

**Must Have (Blocking):**
- [ ] PostgreSQL database `n8n_scraper` created
- [ ] 5 tables defined with proper relationships
- [ ] SQLAlchemy models for all tables
- [ ] Repository with CRUD operations
- [ ] Store 100 workflows successfully
- [ ] Query performance <100ms
- [ ] 10+ unit tests passing
- [ ] Integration test successful
- [ ] Alembic migrations working

**Performance Targets:**
- Single workflow query: <100ms
- Bulk insert: 100+ workflows/minute
- Memory usage: <500MB for 1,000 workflows

---

## 🧪 **4. TESTING**

### **Testing Strategy:**

#### **Level 1: Unit Tests (10+ tests)**

**Test:** `tests/unit/test_storage.py`

**What to Test:**
1. **Model Creation:**
   - Create workflow with all fields
   - Verify relationships work
   - Test JSONB field storage

2. **Repository CRUD:**
   - `create_workflow()` stores all data
   - `get_workflow()` retrieves correctly
   - `list_workflows()` paginates properly
   - `delete_workflow()` removes with cascade

3. **Data Integrity:**
   - Foreign keys enforced
   - Unique constraints work
   - Timestamps auto-populate

4. **Session Management:**
   - Context managers work
   - Sessions rollback on error
   - No connection leaks

**Example Test:**
```python
def test_create_workflow(db_session):
    """Test creating a complete workflow with all layers."""
    repo = WorkflowRepository(db_session)
    
    result = repo.create_workflow(
        workflow_id='2462',
        url='https://n8n.io/workflows/2462',
        extraction_result={
            'quality_score': 85.5,
            'processing_time': 14.62,
            'layers': {
                'layer1': {'success': True, 'title': 'Test'},
                'layer2': {'success': True, 'node_count': 5},
                'layer3': {'success': True, 'explainer_text': 'Test'}
            }
        }
    )
    
    assert result.workflow_id == '2462'
    assert result.metadata.title == 'Test'
    assert result.structure.node_count == 5
    assert result.quality_score == 85.5
```

---

#### **Level 2: Integration Tests (1 comprehensive test)**

**Test:** `tests/integration/test_storage_integration.py`

**What to Test:**
1. Store 100 workflows from Sprint 1 test results
2. Verify all data persisted correctly
3. Query performance under load
4. Memory usage stays stable
5. Statistics calculation accurate

**Example Test:**
```python
@pytest.mark.asyncio
async def test_store_100_workflows():
    """Integration test: Store 100 workflows from E2E pipeline."""
    
    # Load Sprint 1 test results
    with open('.coordination/testing/results/SCRAPE-007-test-results.json') as f:
        test_data = json.load(f)
    
    repo = WorkflowRepository()
    pipeline = E2EPipeline()
    
    # Store first 100 workflows
    workflows = test_data['individual_results'][:100] if len(test_data['individual_results']) >= 100 else test_data['individual_results']
    
    start_time = time.time()
    
    for workflow_data in workflows:
        workflow_id = workflow_data['workflow_id']
        url = workflow_data['url']
        
        # Store in database
        repo.create_workflow(
            workflow_id=workflow_id,
            url=url,
            extraction_result=workflow_data
        )
    
    duration = time.time() - start_time
    
    # Verify
    stats = repo.get_statistics()
    assert stats['total_workflows'] >= len(workflows)
    assert stats['layer1_success_rate'] == 100.0  # Sprint 1 had 100%
    assert stats['layer2_success_rate'] == 60.0   # Sprint 1 had 60%
    
    # Performance
    assert duration / len(workflows) < 0.6  # <0.6s per workflow (100/min)
    
    print(f"✅ Stored {len(workflows)} workflows in {duration:.2f}s")
    print(f"📊 Average: {duration/len(workflows):.3f}s per workflow")
```

---

### **Validation Checklist:**

**Before Submitting:**
- [ ] All unit tests pass
- [ ] Integration test passes
- [ ] 100 workflows stored successfully
- [ ] Query performance <100ms verified
- [ ] Memory usage reasonable (<500MB)
- [ ] No SQL injection vulnerabilities
- [ ] Connection pooling working
- [ ] Alembic migrations work
- [ ] Documentation complete

---

## 📝 **5. NOTION**

### **Task Already Created:**
- **URL:** https://www.notion.so/289d7960213a813f89a8eae1d858e80c
- **Status:** Backlog → In Progress (when you start)
- **Assignee:** Dev1
- **Sprint:** Sprint 2 - Core Development

### **What to Update in Notion:**

**When Starting:**
- Change status to "In Progress"
- Add start date
- Note any setup issues

**Daily Progress:**
- Update % complete
- Note which phase you're in
- Flag any blockers

**When Complete:**
- Change status to "Complete"
- Add completion date
- Link to completion report

---

## 📁 **6. FILES**

### **Files to Create:**

#### **Storage Package:**
```
src/storage/
├── __init__.py          # Package exports
├── database.py          # Database connection management
├── models.py            # SQLAlchemy ORM models
└── repository.py        # Repository pattern (CRUD)
```

#### **Migrations:**
```
alembic/
├── versions/
│   └── 001_initial_schema.py  # Initial schema migration
├── env.py               # Alembic environment
└── script.py.mako       # Migration template
```

#### **Tests:**
```
tests/
├── unit/
│   └── test_storage.py           # Unit tests for storage
└── integration/
    └── test_storage_integration.py  # Integration test
```

#### **Configuration:**
```
alembic.ini              # Alembic configuration
.env                     # Add DATABASE_URL
```

### **Files to Reference:**

**Sprint 1 E2E Pipeline:**
- `src/orchestrator/e2e_pipeline.py` - See output format
- `.coordination/testing/results/SCRAPE-007-test-results.json` - Test data

**For Testing:**
- Use Sprint 1 test results for realistic data
- 50 workflows available with complete structure

---

## ✅ **7. CHECKPOINT**

### **Definition of Done:**

**Phase 1 Complete When:**
- [ ] PostgreSQL running with `n8n_scraper` database
- [ ] Alembic configured and initial migration created
- [ ] Schema documented

**Phase 2 Complete When:**
- [ ] All 5 SQLAlchemy models implemented
- [ ] Repository with 5+ CRUD methods working
- [ ] Connection pooling configured
- [ ] Can insert and query workflows

**Phase 3 Complete When:**
- [ ] 10+ unit tests passing
- [ ] Integration test with 100 workflows passing
- [ ] Query performance <100ms verified
- [ ] Documentation complete

### **Next Steps After Completion:**

1. Create completion report (dev1-to-rnd-SCRAPE-008-COMPLETION.md)
2. Include test results and performance metrics
3. Submit for RND validation
4. After approval, move to SCRAPE-011 (Orchestrator) in Phase 2

### **Unblocks:**
- **SCRAPE-011:** Orchestrator (needs storage to persist progress)
- **SCRAPE-012:** Export Pipeline (needs storage to read data)
- **SCRAPE-013:** Scale Testing (needs storage for 1,000 workflows)

---

## 🎯 **8. OBJECTIVE**

### **Why This Task Matters:**

**Problem:**
Currently, all workflow data exists only in memory during extraction and is saved as JSON files. We need a production-grade database to:
- Persist all extraction data permanently
- Enable efficient querying and filtering
- Support batch processing with resume capability
- Provide foundation for scale testing (1,000+ workflows)
- Enable export pipeline to read data

**Solution:**
PostgreSQL database with:
- Normalized schema (5 tables)
- JSONB for flexible fields
- Repository pattern for clean access
- Connection pooling for performance
- Migrations for schema evolution

**Impact:**
- **Phase 2 Tasks:** Orchestrator can persist progress, resume after failures
- **Phase 3 Tasks:** Scale testing can process 1,000+ workflows
- **Export Pipeline:** Can generate 4 export formats from stored data
- **Future:** Analytics, search, API endpoints all enabled

### **Success Means:**
- ✅ Store 100 workflows in <60 seconds (Phase 3 test)
- ✅ Query any workflow in <100ms
- ✅ No data loss from any extraction layer
- ✅ Ready for 1,000+ workflow scale testing
- ✅ Foundation for all Sprint 2 tasks complete

---

## 🗄️ **9. DATABASE SCHEMA DESIGN**

### **Schema Overview:**

**5 Tables with Relationships:**
```
workflows (main)
  ├── workflow_metadata (1:1)
  ├── workflow_structure (1:1)
  ├── workflow_content (1:1)
  └── video_transcripts (1:N)
```

### **Table 1: workflows (Main Table)**

**Purpose:** Core workflow tracking and status.

**Schema:**
```sql
CREATE TABLE workflows (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    
    -- Processing Status
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processing_time FLOAT,
    quality_score FLOAT,
    
    -- Layer Success Flags
    layer1_success BOOLEAN DEFAULT FALSE,
    layer2_success BOOLEAN DEFAULT FALSE,
    layer3_success BOOLEAN DEFAULT FALSE,
    
    -- Error Tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Indexes
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_quality_score (quality_score),
    INDEX idx_extracted_at (extracted_at)
);
```

**SQLAlchemy Model:**
```python
class Workflow(Base):
    __tablename__ = 'workflows'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), unique=True, nullable=False, index=True)
    url = Column(Text, nullable=False)
    
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processing_time = Column(Float)
    quality_score = Column(Float, index=True)
    
    layer1_success = Column(Boolean, default=False)
    layer2_success = Column(Boolean, default=False)
    layer3_success = Column(Boolean, default=False)
    
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    metadata = relationship("WorkflowMetadata", back_populates="workflow", uselist=False, cascade="all, delete-orphan")
    structure = relationship("WorkflowStructure", back_populates="workflow", uselist=False, cascade="all, delete-orphan")
    content = relationship("WorkflowContent", back_populates="workflow", uselist=False, cascade="all, delete-orphan")
    transcripts = relationship("VideoTranscript", back_populates="workflow", cascade="all, delete-orphan")
```

---

### **Table 2: workflow_metadata (Layer 1 Data)**

**Purpose:** Store Layer 1 metadata extraction results.

**Schema:**
```sql
CREATE TABLE workflow_metadata (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Basic Info
    title TEXT,
    description TEXT,
    use_case TEXT,
    
    -- Author
    author_name VARCHAR(255),
    author_url TEXT,
    
    -- Engagement
    views INTEGER,
    shares INTEGER,
    
    -- Taxonomy (JSONB arrays)
    categories JSONB,  -- ["Sales", "Marketing"]
    tags JSONB,        -- ["email", "automation"]
    
    -- Timestamps
    workflow_created_at TIMESTAMP,
    workflow_updated_at TIMESTAMP,
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Complete Layer 1 Data
    raw_metadata JSONB,
    
    -- Foreign Key
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    INDEX idx_title (title),
    INDEX idx_categories (categories) USING GIN
);
```

**SQLAlchemy Model:**
```python
class WorkflowMetadata(Base):
    __tablename__ = 'workflow_metadata'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), unique=True, nullable=False)
    
    title = Column(Text, index=True)
    description = Column(Text)
    use_case = Column(Text)
    
    author_name = Column(String(255))
    author_url = Column(Text)
    
    views = Column(Integer)
    shares = Column(Integer)
    
    categories = Column(JSONB)  # Array: ["Sales", "Marketing"]
    tags = Column(JSONB)        # Array: ["email", "automation"]
    
    workflow_created_at = Column(DateTime)
    workflow_updated_at = Column(DateTime)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    raw_metadata = Column(JSONB)  # Complete Layer 1 data
    
    # Relationship
    workflow = relationship("Workflow", back_populates="metadata")
```

---

### **Table 3: workflow_structure (Layer 2 Data)**

**Purpose:** Store Layer 2 workflow JSON and node data.

**Schema:**
```sql
CREATE TABLE workflow_structure (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Structure Summary
    node_count INTEGER,
    connection_count INTEGER,
    node_types JSONB,  -- ["httpRequest", "set", "if"]
    
    -- Extraction Method
    extraction_type VARCHAR(50),  -- 'full', 'fallback', 'failed'
    fallback_used BOOLEAN DEFAULT FALSE,
    
    -- Complete Workflow JSON
    workflow_json JSONB,  -- Full n8n workflow definition
    
    -- Timestamp
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Foreign Key
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    INDEX idx_node_count (node_count),
    INDEX idx_node_types (node_types) USING GIN
);
```

**SQLAlchemy Model:**
```python
class WorkflowStructure(Base):
    __tablename__ = 'workflow_structure'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), unique=True, nullable=False)
    
    node_count = Column(Integer, index=True)
    connection_count = Column(Integer)
    node_types = Column(JSONB)  # Array: ["httpRequest", "set"]
    
    extraction_type = Column(String(50))  # 'full', 'fallback', 'failed'
    fallback_used = Column(Boolean, default=False)
    
    workflow_json = Column(JSONB)  # Complete workflow definition
    
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="structure")
```

---

### **Table 4: workflow_content (Layer 3 Data)**

**Purpose:** Store Layer 3 explainer content and media info.

**Schema:**
```sql
CREATE TABLE workflow_content (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Explainer Content
    explainer_text TEXT,
    explainer_html TEXT,
    
    -- Instructions
    setup_instructions TEXT,
    use_instructions TEXT,
    
    -- Media Flags
    has_videos BOOLEAN DEFAULT FALSE,
    video_count INTEGER DEFAULT 0,
    has_iframes BOOLEAN DEFAULT FALSE,
    iframe_count INTEGER DEFAULT 0,
    
    -- Complete Layer 3 Data
    raw_content JSONB,
    
    -- Timestamp
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Foreign Key
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    INDEX idx_has_videos (has_videos)
);
```

**SQLAlchemy Model:**
```python
class WorkflowContent(Base):
    __tablename__ = 'workflow_content'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), unique=True, nullable=False)
    
    explainer_text = Column(Text)
    explainer_html = Column(Text)
    
    setup_instructions = Column(Text)
    use_instructions = Column(Text)
    
    has_videos = Column(Boolean, default=False, index=True)
    video_count = Column(Integer, default=0)
    has_iframes = Column(Boolean, default=False)
    iframe_count = Column(Integer, default=0)
    
    raw_content = Column(JSONB)  # Complete Layer 3 data
    
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="content")
```

---

### **Table 5: video_transcripts**

**Purpose:** Store video transcripts (one-to-many relationship).

**Schema:**
```sql
CREATE TABLE video_transcripts (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL,
    
    -- Video Info
    video_url TEXT NOT NULL,
    video_id VARCHAR(100),
    platform VARCHAR(50),  -- 'youtube', 'vimeo', etc.
    
    -- Transcript Data
    transcript_text TEXT,
    transcript_json JSONB,  -- Structured transcript with timestamps
    
    -- Metadata
    duration INTEGER,  -- seconds
    language VARCHAR(10),  -- 'en', 'es', etc.
    
    -- Timestamp
    extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Foreign Key
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_platform (platform)
);
```

**SQLAlchemy Model:**
```python
class VideoTranscript(Base):
    __tablename__ = 'video_transcripts'
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.workflow_id', ondelete='CASCADE'), nullable=False, index=True)
    
    video_url = Column(Text, nullable=False)
    video_id = Column(String(100))
    platform = Column(String(50), index=True)  # 'youtube', 'vimeo'
    
    transcript_text = Column(Text)
    transcript_json = Column(JSONB)  # Structured with timestamps
    
    duration = Column(Integer)  # seconds
    language = Column(String(10))  # 'en', 'es'
    
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="transcripts")
```

---

## 🔧 **10. IMPLEMENTATION PLAN**

### **Phase 1: Schema Design & Setup (1.5 hours)**

#### **Step 1: Install PostgreSQL (15 minutes)**

**If PostgreSQL not installed:**
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb n8n_scraper

# Verify
psql n8n_scraper -c "SELECT version();"
```

**Create `.env` file:**
```bash
# Add to .env
DATABASE_URL=postgresql://localhost:5432/n8n_scraper
```

---

#### **Step 2: Set Up Alembic (20 minutes)**

**Install Alembic:**
```bash
pip install alembic psycopg2-binary
```

**Initialize Alembic:**
```bash
alembic init alembic
```

**Configure `alembic.ini`:**
```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://localhost:5432/n8n_scraper

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Update `alembic/env.py`:**
```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv

# Import your models
from src.storage.models import Base

# Load environment variables
load_dotenv()

# this is the Alembic Config object
config = context.config

# Set sqlalchemy.url from environment
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

#### **Step 3: Create Database Connection Module (30 minutes)**

**Create `src/storage/database.py`:**
```python
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
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from loguru import logger

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/n8n_scraper')

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # Maximum connections in pool
    max_overflow=20,           # Extra connections beyond pool_size
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

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite (if used for testing)."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
    from src.storage.models import Base
    
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

def drop_all_tables():
    """
    Drop all tables from database.
    
    WARNING: This deletes all data!
    Only use in testing/development.
    """
    from src.storage.models import Base
    
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
        logger.info(f"Database connected: {DATABASE_URL.split('@')[-1]}")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    raise
```

---

#### **Step 4: Document Schema (25 minutes)**

Create schema documentation showing:
- Table relationships diagram
- Field descriptions
- Indexing strategy
- JSONB field structures

---

### **Phase 2: Implementation (3 hours)**

#### **Step 1: Build SQLAlchemy Models (1 hour)**

**Create `src/storage/models.py`:**
```python
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
    metadata = relationship(
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
    workflow = relationship("Workflow", back_populates="metadata")
    
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
```

---

#### **Step 2: Implement Repository Pattern (1.5 hours)**

**Create `src/storage/repository.py`:**
```python
"""
Repository pattern for workflow data access.

Provides clean CRUD operations for workflows, abstracting
database implementation details from business logic.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from loguru import logger

from src.storage.database import get_session
from src.storage.models import (
    Workflow,
    WorkflowMetadata,
    WorkflowStructure,
    WorkflowContent,
    VideoTranscript
)


class WorkflowRepository:
    """
    Repository for workflow CRUD operations.
    
    Encapsulates all database access for workflows, providing
    a clean API for creating, reading, updating, and deleting
    workflow data across all 5 tables.
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy session (if None, creates new session per operation)
        """
        self.session = session
        self._owns_session = session is None
    
    def _get_session(self) -> Session:
        """Get session (provided or create new)."""
        if self.session:
            return self.session
        return next(get_session())
    
    def create_workflow(
        self,
        workflow_id: str,
        url: str,
        extraction_result: Dict[str, Any]
    ) -> Workflow:
        """
        Create a complete workflow entry with all extracted data.
        
        Args:
            workflow_id: Unique n8n.io workflow ID
            url: Workflow URL
            extraction_result: Complete E2E pipeline result
        
        Returns:
            Workflow: Created workflow object with all relationships
        
        Example:
            result = await pipeline.process_workflow('2462', 'https://n8n.io/workflows/2462')
            workflow = repo.create_workflow('2462', result['url'], result)
        """
        session = self._get_session()
        
        try:
            # Create main workflow record
            workflow = Workflow(
                workflow_id=workflow_id,
                url=url,
                processing_time=extraction_result.get('processing_time'),
                quality_score=extraction_result.get('quality_score'),
                layer1_success=extraction_result.get('layers', {}).get('layer1', {}).get('success', False),
                layer2_success=extraction_result.get('layers', {}).get('layer2', {}).get('success', False),
                layer3_success=extraction_result.get('layers', {}).get('layer3', {}).get('success', False),
            )
            
            session.add(workflow)
            
            # Add Layer 1 (Metadata)
            layer1_data = extraction_result.get('layers', {}).get('layer1', {})
            if layer1_data.get('success'):
                metadata = WorkflowMetadata(
                    workflow_id=workflow_id,
                    title=layer1_data.get('title'),
                    description=layer1_data.get('description'),
                    use_case=layer1_data.get('use_case'),
                    author_name=layer1_data.get('author', {}).get('name'),
                    author_url=layer1_data.get('author', {}).get('url'),
                    views=layer1_data.get('views'),
                    shares=layer1_data.get('shares'),
                    categories=layer1_data.get('categories', []),
                    tags=layer1_data.get('tags', []),
                    workflow_created_at=layer1_data.get('created_at'),
                    workflow_updated_at=layer1_data.get('updated_at'),
                    raw_metadata=layer1_data
                )
                session.add(metadata)
            
            # Add Layer 2 (Structure)
            layer2_data = extraction_result.get('layers', {}).get('layer2', {})
            if layer2_data.get('success'):
                structure = WorkflowStructure(
                    workflow_id=workflow_id,
                    node_count=layer2_data.get('node_count'),
                    connection_count=layer2_data.get('connection_count'),
                    node_types=layer2_data.get('node_types', []),
                    extraction_type=layer2_data.get('extraction_type', 'full'),
                    fallback_used=layer2_data.get('fallback_used', False),
                    workflow_json=layer2_data.get('data')
                )
                session.add(structure)
            
            # Add Layer 3 (Content)
            layer3_data = extraction_result.get('layers', {}).get('layer3', {})
            if layer3_data.get('success'):
                content = WorkflowContent(
                    workflow_id=workflow_id,
                    explainer_text=layer3_data.get('explainer_text'),
                    explainer_html=layer3_data.get('explainer_html'),
                    setup_instructions=layer3_data.get('setup_instructions'),
                    use_instructions=layer3_data.get('use_instructions'),
                    has_videos=layer3_data.get('has_videos', False),
                    video_count=len(layer3_data.get('videos', [])),
                    has_iframes=layer3_data.get('has_iframes', False),
                    iframe_count=layer3_data.get('iframe_count', 0),
                    raw_content=layer3_data
                )
                session.add(content)
                
                # Add video transcripts
                for video in layer3_data.get('videos', []):
                    if video.get('transcript'):
                        transcript = VideoTranscript(
                            workflow_id=workflow_id,
                            video_url=video.get('url'),
                            video_id=video.get('video_id'),
                            platform=video.get('platform', 'youtube'),
                            transcript_text=video.get('transcript', {}).get('text'),
                            transcript_json=video.get('transcript'),
                            duration=video.get('transcript', {}).get('duration'),
                            language=video.get('transcript', {}).get('language', 'en')
                        )
                        session.add(transcript)
            
            # Commit if we own the session
            if self._owns_session:
                session.commit()
                session.refresh(workflow)
            
            logger.info(f"Created workflow: {workflow_id}")
            return workflow
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"Error creating workflow {workflow_id}: {e}")
            raise
        finally:
            if self._owns_session:
                session.close()
    
    def get_workflow(
        self,
        workflow_id: str,
        include_relationships: bool = True
    ) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: Workflow ID to retrieve
            include_relationships: If True, eagerly load all relationships
        
        Returns:
            Workflow object or None if not found
        """
        session = self._get_session()
        
        try:
            query = session.query(Workflow).filter(Workflow.workflow_id == workflow_id)
            
            if include_relationships:
                query = query.options(
                    joinedload(Workflow.metadata),
                    joinedload(Workflow.structure),
                    joinedload(Workflow.content),
                    joinedload(Workflow.transcripts)
                )
            
            workflow = query.first()
            return workflow
            
        finally:
            if self._owns_session:
                session.close()
    
    def list_workflows(
        self,
        offset: int = 0,
        limit: int = 100,
        order_by: str = 'extracted_at',
        order_desc: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Workflow]:
        """
        List workflows with pagination and filtering.
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by ('extracted_at', 'quality_score', 'workflow_id')
            order_desc: If True, order descending
            filters: Optional filters (layer2_success=True, min_quality=50, etc.)
        
        Returns:
            List of workflows
        """
        session = self._get_session()
        
        try:
            query = session.query(Workflow)
            
            # Apply filters
            if filters:
                if 'layer1_success' in filters:
                    query = query.filter(Workflow.layer1_success == filters['layer1_success'])
                if 'layer2_success' in filters:
                    query = query.filter(Workflow.layer2_success == filters['layer2_success'])
                if 'layer3_success' in filters:
                    query = query.filter(Workflow.layer3_success == filters['layer3_success'])
                if 'min_quality' in filters:
                    query = query.filter(Workflow.quality_score >= filters['min_quality'])
                if 'max_quality' in filters:
                    query = query.filter(Workflow.quality_score <= filters['max_quality'])
            
            # Apply ordering
            order_field = getattr(Workflow, order_by, Workflow.extracted_at)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())
            
            # Apply pagination
            workflows = query.offset(offset).limit(limit).all()
            
            return workflows
            
        finally:
            if self._owns_session:
                session.close()
    
    def update_workflow(
        self,
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Workflow]:
        """
        Update workflow fields.
        
        Args:
            workflow_id: Workflow ID to update
            updates: Dictionary of fields to update
        
        Returns:
            Updated workflow or None if not found
        """
        session = self._get_session()
        
        try:
            workflow = session.query(Workflow).filter(
                Workflow.workflow_id == workflow_id
            ).first()
            
            if not workflow:
                return None
            
            # Update fields
            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
            
            workflow.updated_at = datetime.utcnow()
            
            if self._owns_session:
                session.commit()
                session.refresh(workflow)
            
            logger.info(f"Updated workflow: {workflow_id}")
            return workflow
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"Error updating workflow {workflow_id}: {e}")
            raise
        finally:
            if self._owns_session:
                session.close()
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow and all related data.
        
        Args:
            workflow_id: Workflow ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        session = self._get_session()
        
        try:
            workflow = session.query(Workflow).filter(
                Workflow.workflow_id == workflow_id
            ).first()
            
            if not workflow:
                return False
            
            session.delete(workflow)
            
            if self._owns_session:
                session.commit()
            
            logger.info(f"Deleted workflow: {workflow_id}")
            return True
            
        except Exception as e:
            if self._owns_session:
                session.rollback()
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise
        finally:
            if self._owns_session:
                session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts, success rates, and other metrics
        """
        session = self._get_session()
        
        try:
            total = session.query(func.count(Workflow.id)).scalar()
            
            layer1_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer1_success == True
            ).scalar()
            
            layer2_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer2_success == True
            ).scalar()
            
            layer3_success = session.query(func.count(Workflow.id)).filter(
                Workflow.layer3_success == True
            ).scalar()
            
            avg_quality = session.query(func.avg(Workflow.quality_score)).scalar() or 0
            avg_processing_time = session.query(func.avg(Workflow.processing_time)).scalar() or 0
            
            return {
                'total_workflows': total,
                'layer1_success_count': layer1_success,
                'layer1_success_rate': (layer1_success / total * 100) if total > 0 else 0,
                'layer2_success_count': layer2_success,
                'layer2_success_rate': (layer2_success / total * 100) if total > 0 else 0,
                'layer3_success_count': layer3_success,
                'layer3_success_rate': (layer3_success / total * 100) if total > 0 else 0,
                'avg_quality_score': round(avg_quality, 2),
                'avg_processing_time': round(avg_processing_time, 2)
            }
            
        finally:
            if self._owns_session:
                session.close()
    
    def search_workflows(
        self,
        search_term: str,
        search_fields: List[str] = ['title', 'description'],
        limit: int = 50
    ) -> List[Workflow]:
        """
        Search workflows by text.
        
        Args:
            search_term: Text to search for
            search_fields: Fields to search in ('title', 'description', 'use_case')
            limit: Maximum results
        
        Returns:
            List of matching workflows
        """
        session = self._get_session()
        
        try:
            query = session.query(Workflow).join(WorkflowMetadata)
            
            # Build search conditions
            conditions = []
            search_term_lower = search_term.lower()
            
            if 'title' in search_fields:
                conditions.append(func.lower(WorkflowMetadata.title).contains(search_term_lower))
            if 'description' in search_fields:
                conditions.append(func.lower(WorkflowMetadata.description).contains(search_term_lower))
            if 'use_case' in search_fields:
                conditions.append(func.lower(WorkflowMetadata.use_case).contains(search_term_lower))
            
            if conditions:
                query = query.filter(or_(*conditions))
            
            workflows = query.limit(limit).all()
            return workflows
            
        finally:
            if self._owns_session:
                session.close()
```

---

#### **Step 3: Create Package Exports (15 minutes)**

**Create `src/storage/__init__.py`:**
```python
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
```

---

#### **Step 4: Create Initial Migration (30 minutes)**

**Generate migration:**
```bash
# After creating models, generate migration
alembic revision --autogenerate -m "initial schema"

# Review generated migration in alembic/versions/
# Then apply it
alembic upgrade head
```

---

### **Phase 3: Testing & Validation (1.5 hours)**

#### **Step 1: Unit Tests (45 minutes)**

**Create `tests/unit/test_storage.py`:**
```python
"""
Unit tests for storage layer.

Tests SQLAlchemy models, repository CRUD operations,
and database session management.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

import pytest
from datetime import datetime

from src.storage.database import get_session, init_database
from src.storage.models import Workflow, WorkflowMetadata, WorkflowStructure
from src.storage.repository import WorkflowRepository


@pytest.fixture(scope="function")
def db_session():
    """Provide a database session for testing."""
    init_database()  # Create tables
    session = next(get_session())
    yield session
    session.close()


@pytest.fixture
def sample_extraction_result():
    """Sample E2E pipeline extraction result."""
    return {
        'workflow_id': 'TEST-001',
        'url': 'https://n8n.io/workflows/TEST-001',
        'processing_time': 14.5,
        'quality_score': 85.3,
        'layers': {
            'layer1': {
                'success': True,
                'title': 'Test Workflow',
                'description': 'Test description',
                'author': {'name': 'Test Author', 'url': 'https://example.com'},
                'categories': ['Sales', 'Marketing'],
                'tags': ['email', 'automation'],
                'views': 100,
                'shares': 10
            },
            'layer2': {
                'success': True,
                'node_count': 5,
                'connection_count': 4,
                'node_types': ['start', 'httpRequest', 'set'],
                'extraction_type': 'full',
                'fallback_used': False,
                'data': {'nodes': [], 'connections': {}}
            },
            'layer3': {
                'success': True,
                'explainer_text': 'Test explainer',
                'setup_instructions': 'Test setup',
                'has_videos': True,
                'videos': [
                    {
                        'url': 'https://youtube.com/watch?v=test',
                        'video_id': 'test',
                        'platform': 'youtube',
                        'transcript': {
                            'text': 'Test transcript',
                            'duration': 300,
                            'language': 'en'
                        }
                    }
                ]
            }
        }
    }


class TestWorkflowModel:
    """Tests for Workflow model."""
    
    def test_create_workflow(self, db_session):
        """Test creating a workflow."""
        workflow = Workflow(
            workflow_id='TEST-001',
            url='https://n8n.io/workflows/TEST-001',
            quality_score=85.5,
            layer1_success=True
        )
        
        db_session.add(workflow)
        db_session.commit()
        
        assert workflow.id is not None
        assert workflow.workflow_id == 'TEST-001'
        assert workflow.quality_score == 85.5
    
    def test_workflow_relationships(self, db_session):
        """Test workflow relationships."""
        workflow = Workflow(workflow_id='TEST-002', url='https://example.com')
        metadata = WorkflowMetadata(workflow_id='TEST-002', title='Test')
        
        db_session.add(workflow)
        db_session.add(metadata)
        db_session.commit()
        
        assert workflow.metadata is not None
        assert workflow.metadata.title == 'Test'


class TestWorkflowRepository:
    """Tests for WorkflowRepository."""
    
    def test_create_workflow_complete(self, db_session, sample_extraction_result):
        """Test creating a complete workflow with all data."""
        repo = WorkflowRepository(db_session)
        
        workflow = repo.create_workflow(
            workflow_id='TEST-001',
            url=sample_extraction_result['url'],
            extraction_result=sample_extraction_result
        )
        
        assert workflow.workflow_id == 'TEST-001'
        assert workflow.quality_score == 85.3
        assert workflow.layer1_success == True
        assert workflow.layer2_success == True
        assert workflow.layer3_success == True
        assert workflow.metadata is not None
        assert workflow.metadata.title == 'Test Workflow'
        assert workflow.structure is not None
        assert workflow.structure.node_count == 5
        assert workflow.content is not None
        assert len(workflow.transcripts) == 1
    
    def test_get_workflow(self, db_session, sample_extraction_result):
        """Test retrieving a workflow."""
        repo = WorkflowRepository(db_session)
        
        # Create workflow
        repo.create_workflow('TEST-002', sample_extraction_result['url'], sample_extraction_result)
        
        # Retrieve workflow
        workflow = repo.get_workflow('TEST-002')
        
        assert workflow is not None
        assert workflow.workflow_id == 'TEST-002'
        assert workflow.metadata.title == 'Test Workflow'
    
    def test_list_workflows_pagination(self, db_session, sample_extraction_result):
        """Test paginated workflow listing."""
        repo = WorkflowRepository(db_session)
        
        # Create 5 workflows
        for i in range(5):
            result = sample_extraction_result.copy()
            result['workflow_id'] = f'TEST-{i:03d}'
            repo.create_workflow(f'TEST-{i:03d}', result['url'], result)
        
        # List first 3
        workflows = repo.list_workflows(offset=0, limit=3)
        
        assert len(workflows) == 3
    
    def test_delete_workflow_cascade(self, db_session, sample_extraction_result):
        """Test workflow deletion with cascade."""
        repo = WorkflowRepository(db_session)
        
        # Create workflow
        repo.create_workflow('TEST-003', sample_extraction_result['url'], sample_extraction_result)
        
        # Delete workflow
        deleted = repo.delete_workflow('TEST-003')
        
        assert deleted == True
        assert repo.get_workflow('TEST-003') is None
    
    def test_get_statistics(self, db_session, sample_extraction_result):
        """Test statistics calculation."""
        repo = WorkflowRepository(db_session)
        
        # Create workflows
        for i in range(10):
            result = sample_extraction_result.copy()
            result['workflow_id'] = f'STAT-{i:03d}'
            
            # Make some fail Layer 2 (60% success rate)
            if i >= 6:
                result['layers']['layer2']['success'] = False
            
            repo.create_workflow(f'STAT-{i:03d}', result['url'], result)
        
        # Get statistics
        stats = repo.get_statistics()
        
        assert stats['total_workflows'] == 10
        assert stats['layer1_success_rate'] == 100.0
        assert stats['layer2_success_rate'] == 60.0  # 6/10
        assert stats['layer3_success_rate'] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
```

---

#### **Step 2: Integration Test (45 minutes)**

**Create `tests/integration/test_storage_integration.py`:**
```python
"""
Integration test for storage layer.

Tests storing 100 workflows from Sprint 1 E2E pipeline results,
validating performance and data integrity at scale.

Author: Dev1
Task: SCRAPE-008
Date: October 11, 2025
"""

import json
import time
import pytest

from src.storage.database import init_database, drop_all_tables
from src.storage.repository import WorkflowRepository


@pytest.mark.integration
def test_store_100_workflows_from_sprint1():
    """
    Integration test: Store 100 workflows from Sprint 1 test results.
    
    Success Criteria:
    - Store 100 workflows successfully
    - Query performance <100ms per workflow
    - Memory usage reasonable
    - Statistics accurate
    """
    
    # Initialize database
    init_database()
    
    try:
        # Load Sprint 1 test results
        with open('.coordination/testing/results/SCRAPE-007-test-results.json') as f:
            test_data = json.load(f)
        
        workflows = test_data['individual_results']
        
        # Limit to 100 workflows (or all if < 100)
        test_workflows = workflows[:100] if len(workflows) >= 100 else workflows
        
        print(f"\n📊 Testing storage with {len(test_workflows)} workflows...")
        
        # Store workflows
        repo = WorkflowRepository()
        start_time = time.time()
        
        for i, workflow_data in enumerate(test_workflows):
            workflow_id = workflow_data['workflow_id']
            url = workflow_data['url']
            
            # Store in database
            repo.create_workflow(
                workflow_id=workflow_id,
                url=url,
                extraction_result=workflow_data
            )
            
            if (i + 1) % 10 == 0:
                print(f"   Stored {i + 1}/{len(test_workflows)} workflows...")
        
        duration = time.time() - start_time
        
        print(f"\n✅ Storage Complete:")
        print(f"   Total Workflows: {len(test_workflows)}")
        print(f"   Total Time: {duration:.2f}s")
        print(f"   Average Time: {duration/len(test_workflows):.3f}s per workflow")
        print(f"   Rate: {len(test_workflows)/duration:.1f} workflows/second")
        
        # Verify statistics
        stats = repo.get_statistics()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total Workflows: {stats['total_workflows']}")
        print(f"   Layer 1 Success: {stats['layer1_success_rate']:.1f}%")
        print(f"   Layer 2 Success: {stats['layer2_success_rate']:.1f}%")
        print(f"   Layer 3 Success: {stats['layer3_success_rate']:.1f}%")
        print(f"   Avg Quality Score: {stats['avg_quality_score']:.2f}")
        print(f"   Avg Processing Time: {stats['avg_processing_time']:.2f}s")
        
        # Test query performance
        print(f"\n⚡ Query Performance Test:")
        
        query_times = []
        for i in range(10):
            workflow_id = test_workflows[i]['workflow_id']
            
            query_start = time.time()
            workflow = repo.get_workflow(workflow_id)
            query_time = (time.time() - query_start) * 1000  # ms
            
            query_times.append(query_time)
            
            assert workflow is not None
            assert workflow.workflow_id == workflow_id
        
        avg_query_time = sum(query_times) / len(query_times)
        
        print(f"   10 Query Average: {avg_query_time:.2f}ms")
        print(f"   Min Query Time: {min(query_times):.2f}ms")
        print(f"   Max Query Time: {max(query_times):.2f}ms")
        
        # Assertions
        assert stats['total_workflows'] == len(test_workflows)
        assert stats['layer1_success_rate'] == 100.0  # Sprint 1 had 100%
        assert stats['layer2_success_rate'] == 60.0   # Sprint 1 had 60%
        assert stats['layer3_success_rate'] == 100.0  # Sprint 1 had 100%
        assert duration / len(test_workflows) < 0.6  # <0.6s per workflow (100/min)
        assert avg_query_time < 100  # <100ms query time
        
        print(f"\n✅ All Integration Tests Passed!")
        print(f"   ✅ Stored {len(test_workflows)} workflows")
        print(f"   ✅ Performance: {duration/len(test_workflows):.3f}s per workflow")
        print(f"   ✅ Query speed: {avg_query_time:.2f}ms average")
        print(f"   ✅ Statistics accurate")
        
    finally:
        # Cleanup (optional - comment out to keep data)
        # drop_all_tables()
        pass


if __name__ == "__main__":
    test_store_100_workflows_from_sprint1()
```

---

## 📋 **11. SUCCESS CRITERIA**

### **Must Have (Blocking):**

**Database Infrastructure:**
- [ ] PostgreSQL database `n8n_scraper` created and accessible
- [ ] Alembic configured with initial migration
- [ ] Connection pooling working (10 connections)
- [ ] Can connect and query database

**Schema:**
- [ ] 5 tables created (`workflows`, `workflow_metadata`, `workflow_structure`, `workflow_content`, `video_transcripts`)
- [ ] Foreign keys with CASCADE delete working
- [ ] JSONB fields working for flexible data
- [ ] Indexes on key columns

**Models:**
- [ ] All 5 SQLAlchemy models defined
- [ ] Relationships configured (one-to-one, one-to-many)
- [ ] Cascade delete working
- [ ] Timestamps auto-populate

**Repository:**
- [ ] `create_workflow()` stores complete data
- [ ] `get_workflow()` retrieves with relationships
- [ ] `list_workflows()` paginates correctly
- [ ] `delete_workflow()` cascades properly
- [ ] `get_statistics()` calculates accurately

**Testing:**
- [ ] 10+ unit tests passing
- [ ] Integration test stores 100 workflows
- [ ] All tests pass
- [ ] Coverage >80% on storage code

**Performance:**
- [ ] Single workflow query <100ms
- [ ] Bulk insert rate >100 workflows/minute
- [ ] Memory usage <500MB for 1,000 workflows
- [ ] No connection leaks

**Documentation:**
- [ ] Schema documented with descriptions
- [ ] Repository API documented
- [ ] Setup instructions provided
- [ ] Example usage included

---

### **Should Have (Important):**

- [ ] Database connection retry logic
- [ ] Query optimization with indexes
- [ ] Batch insert support
- [ ] Statistics caching
- [ ] Search functionality working

---

### **Nice to Have (Optional):**

- [ ] Database backup script
- [ ] Admin queries/reports
- [ ] Performance profiling
- [ ] Schema visualization diagram

---

## 🎯 **12. EXPECTED RESULTS**

### **What Good Looks Like:**

**After Phase 1 (Schema Setup):**
```bash
# Can connect to PostgreSQL
psql n8n_scraper -c "\dt"

# Shows 5 tables:
# - workflows
# - workflow_metadata
# - workflow_structure
# - workflow_content
# - video_transcripts

# Alembic working
alembic current  # Shows current migration
```

**After Phase 2 (Implementation):**
```python
# Can use repository
from src.storage.repository import WorkflowRepository

repo = WorkflowRepository()

# Store workflow
workflow = repo.create_workflow(
    workflow_id='2462',
    url='https://n8n.io/workflows/2462',
    extraction_result=extraction_data
)

# Query workflow
workflow = repo.get_workflow('2462')
print(f"Title: {workflow.metadata.title}")
print(f"Nodes: {workflow.structure.node_count}")

# Get statistics
stats = repo.get_statistics()
print(f"Total: {stats['total_workflows']}")
print(f"Layer 2 Success: {stats['layer2_success_rate']}%")
```

**After Phase 3 (Testing):**
```bash
# All unit tests pass
pytest tests/unit/test_storage.py -v

# Integration test passes
pytest tests/integration/test_storage_integration.py -v

# Example output:
# ✅ Stored 100 workflows in 45.23s
# ✅ Average: 0.452s per workflow
# ✅ Query performance: 32.5ms average
# ✅ Layer 2 success rate: 60.0%
```

---

## 📦 **13. DELIVERABLES CHECKLIST**

### **Code Files:**

**Storage Package:**
- [ ] `src/storage/__init__.py` - Package exports
- [ ] `src/storage/database.py` - Connection management (150 lines)
- [ ] `src/storage/models.py` - 5 SQLAlchemy models (300 lines)
- [ ] `src/storage/repository.py` - Repository pattern (250 lines)

**Migrations:**
- [ ] `alembic/` - Alembic directory structure
- [ ] `alembic.ini` - Configuration file
- [ ] `alembic/versions/001_*.py` - Initial schema migration

**Tests:**
- [ ] `tests/unit/test_storage.py` - 10+ unit tests (200 lines)
- [ ] `tests/integration/test_storage_integration.py` - Integration test (100 lines)

**Configuration:**
- [ ] `.env` - Updated with `DATABASE_URL`

---

### **Documentation:**

- [ ] Schema documentation (tables, relationships, indexes)
- [ ] Repository API documentation
- [ ] Setup instructions (PostgreSQL, Alembic)
- [ ] Example usage code
- [ ] Performance benchmarks

---

### **Evidence:**

- [ ] Unit test results (10+ tests passing)
- [ ] Integration test results (100 workflows stored)
- [ ] Performance metrics (<100ms queries, >100/min inserts)
- [ ] Statistics validation (60% Layer 2, 100% Layer 1/3)

---

### **Completion Report:**

- [ ] `dev1-to-rnd-SCRAPE-008-COMPLETION.md`
  - Task summary
  - All deliverables completed
  - Test results
  - Performance metrics
  - Known limitations
  - Next steps

---

## 🔄 **14. WHY THIS CAN RUN IN PARALLEL**

### **Independence from Other Tasks:**

**No Dependencies:**
- ✅ Does not depend on SCRAPE-009 (Unit Testing)
- ✅ Does not depend on SCRAPE-012 (Export Pipeline)
- ✅ Only depends on Sprint 1 E2E output format (already complete)

**Provides Foundation For:**
- SCRAPE-011: Orchestrator (needs storage for progress tracking)
- SCRAPE-012: Export Pipeline (needs storage to read data)
- SCRAPE-013: Scale Testing (needs storage for 1,000 workflows)

**Parallel Work:**
```
Your Track (Dev1):
  SCRAPE-008: Build PostgreSQL database
  ↓
  No waiting needed!
  ↓
  Start immediately

Track B (Dev2):
  SCRAPE-009: Build unit tests
  (Independent - tests different code)

Track C (RND):
  SCRAPE-012: Build export formats
  (Independent - uses E2E output, not DB yet)
```

**No Conflicts:**
- Different code directories (`src/storage/` vs `tests/` vs exports)
- Different responsibilities (database vs testing vs export)
- Can work simultaneously without coordination

---

## 🚀 **15. GETTING STARTED**

### **First Steps (Right Now):**

1. **Set Up Environment:**
   ```bash
   # Install PostgreSQL (if needed)
   brew install postgresql@15
   brew services start postgresql@15
   
   # Create database
   createdb n8n_scraper
   
   # Install Python dependencies
   pip install sqlalchemy alembic psycopg2-binary python-dotenv
   ```

2. **Create `.env` File:**
   ```bash
   echo "DATABASE_URL=postgresql://localhost:5432/n8n_scraper" > .env
   ```

3. **Initialize Alembic:**
   ```bash
   alembic init alembic
   ```

4. **Start Phase 1:**
   - Create `src/storage/database.py`
   - Test database connection
   - Design schema

### **Questions? Blockers?**

**Contact RND Manager immediately if:**
- PostgreSQL installation issues
- Database connection problems
- Schema design questions
- Unclear E2E output format
- Any technical blockers

**No blocking issues expected** - This task is well-defined and independent!

---

## ✅ **16. READY TO START**

### **You Have Everything You Need:**

**Technical Specs:** ✅ Complete schema design  
**Code Examples:** ✅ All files with full implementations  
**Testing Approach:** ✅ Unit + integration tests defined  
**Success Criteria:** ✅ Clear performance targets  
**Timeline:** ✅ 6 hours (1 day)  

**No Blockers:** ✅ Can start immediately  
**No Dependencies:** ✅ Sprint 1 complete, E2E output available  
**Clear Deliverables:** ✅ 5 tables, repository, tests  

---

## 🎯 **FINAL CHECKLIST**

**Before Starting:**
- [ ] PostgreSQL installed and running
- [ ] Database `n8n_scraper` created
- [ ] `.env` file with `DATABASE_URL`
- [ ] Task brief read and understood
- [ ] Notion task updated to "In Progress"

**During Work:**
- [ ] Update Notion progress regularly
- [ ] Flag blockers immediately
- [ ] Run tests frequently
- [ ] Document as you go

**Before Submitting:**
- [ ] All unit tests pass (10+)
- [ ] Integration test passes (100 workflows)
- [ ] Performance validated (<100ms queries)
- [ ] Documentation complete
- [ ] Completion report created

---

## 🚀 **START BUILDING!**

**Good luck, Dev1!**

This storage layer is the foundation for all of Sprint 2. Once you complete this:
- SCRAPE-011 (Orchestrator) can persist progress
- SCRAPE-012 (Export) can read stored data
- SCRAPE-013 (Scale Testing) can handle 1,000+ workflows

**You're building the data backbone of the entire system!**

---

**Expected Completion:** October 12, 2025 (Day 5)  
**Next Task:** SCRAPE-011 - Orchestrator & Rate Limiting  
**Contact:** RND Manager for any questions or blockers

---

**🎯 SCRAPE-008: STORAGE LAYER - LET'S BUILD IT!**

---

*Task Brief v1.0*  
*Created: October 11, 2025, 12:15 PM*  
*Author: RND Manager*  
*Assignee: Dev1*  
*Sprint: Sprint 2 - Core Development*





