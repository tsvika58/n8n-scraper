# N8N Workflow Scraper - Project Structure v2.0

**Version:** 2.0 (Post-RND Feedback)  
**Date:** October 9, 2025  
**Status:** Optimized for 2-Week Sprint

---

## 📁 **COMPLETE PROJECT STRUCTURE**

```
n8n-scraper/
│
├── 📄 README.md                      # Project overview and quick start
├── 📄 requirements.txt               # Python dependencies (27 packages)
├── 📄 pyproject.toml                 # Python project configuration
├── 📄 .env.example                   # Environment variables template
├── 📄 .gitignore                     # Git ignore patterns
├── 🐳 Dockerfile                     # Container definition
├── 🐳 docker-compose.yml             # Docker orchestration
│
├── 📂 src/                           # Source code
│   ├── __init__.py
│   │
│   ├── 📂 scraper/                   # Core scraping logic
│   │   ├── __init__.py
│   │   ├── base.py                   # Base scraper class
│   │   ├── page_extractor.py        # Layer 1: Page metadata
│   │   ├── workflow_extractor.py    # Layer 2: Workflow iframe
│   │   ├── explainer_extractor.py   # Layer 3: Explainer iframe
│   │   └── orchestrator.py          # Main scraping orchestrator
│   │
│   ├── 📂 processors/                # Data processing
│   │   ├── __init__.py
│   │   ├── ocr.py                    # Image OCR processing
│   │   ├── video.py                  # Video transcript extraction
│   │   ├── validator.py              # Data validation
│   │   └── transformer.py            # Data transformations
│   │
│   ├── 📂 storage/                   # Data persistence
│   │   ├── __init__.py
│   │   ├── database.py               # SQLite operations
│   │   ├── exporter.py               # Data export (JSON, JSONL, CSV)
│   │   ├── media.py                  # Media file management
│   │   └── cache.py                  # Caching layer
│   │
│   ├── 📂 models/                    # Data models
│   │   ├── __init__.py
│   │   ├── schema.py                 # Pydantic models
│   │   ├── enums.py                  # Enumerations
│   │   └── validators.py             # Custom validators
│   │
│   └── 📂 utils/                     # Utilities
│       ├── __init__.py
│       ├── config.py                 # Configuration management
│       ├── logger.py                 # Logging setup
│       ├── rate_limiter.py           # Rate limiting
│       └── retry.py                  # Retry logic
│
├── 📂 scripts/                       # Executable scripts
│   ├── scrape.py                     # Main scraping script
│   ├── validate.py                   # Validation script
│   ├── export.py                     # Export script
│   ├── analyze.py                    # Dataset analysis
│   ├── init_db.py                    # Database initialization
│   └── cleanup.py                    # Cleanup utilities
│
├── 📂 tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── test_scraper.py               # Scraper tests
│   ├── test_processors.py            # Processor tests
│   ├── test_storage.py               # Storage tests
│   ├── test_models.py                # Model validation tests
│   │
│   └── 📂 fixtures/                  # Test fixtures
│       ├── sample_workflow.json      # Sample workflow data
│       ├── sample_page.html          # Sample HTML page
│       └── sample_image.png          # Sample image
│
├── 📂 config/                        # Configuration files
│   ├── config.yaml                   # Main configuration
│   ├── config.dev.yaml               # Development config
│   ├── config.prod.yaml              # Production config
│   └── logging.yaml                  # Logging configuration
│
├── 📂 data/                          # Data directory (gitignored)
│   ├── 📂 raw/                       # Raw scraped data
│   │   └── workflows/                # Individual workflow JSON files
│   ├── 📂 processed/                 # Validated and processed data
│   │   └── workflows/
│   ├── 📂 exports/                   # Final datasets
│   │   ├── dataset.json              # Complete JSON export
│   │   ├── dataset.jsonl             # Training-optimized
│   │   ├── dataset.csv               # Metadata summary
│   │   └── dataset.parquet           # Columnar format
│   └── 📂 database/                  # SQLite database
│       └── n8n_workflows.db
│
├── 📂 media/                         # Media files (gitignored)
│   ├── 📂 images/                    # Downloaded images
│   │   ├── 2462_setup.png
│   │   └── ...
│   └── 📂 videos/                    # Video metadata & transcripts
│       ├── 2462_tutorial.json
│       └── ...
│
├── 📂 logs/                          # Log files (gitignored)
│   ├── scraper.log                   # Main scraper logs
│   ├── errors.log                    # Error logs
│   └── performance.log               # Performance metrics
│
├── 📂 docs/                          # Documentation
│   ├── project-brief.md              # Project overview
│   ├── technical-guide.md            # Implementation guide
│   ├── api-docs.md                   # API documentation
│   ├── dataset-schema.md             # Dataset structure
│   ├── setup-guide.md                # Setup instructions
│   └── troubleshooting.md            # Common issues
│
├── 📂 notebooks/                     # Jupyter notebooks (optional)
│   ├── data-exploration.ipynb        # Dataset exploration
│   ├── quality-analysis.ipynb        # Quality metrics
│   └── pattern-analysis.ipynb        # Workflow pattern analysis
│
└── 📂 .github/                       # GitHub configuration (optional)
    └── workflows/
        ├── test.yml                  # CI: Run tests
        └── lint.yml                  # CI: Linting
```

---

## 📊 **DIRECTORY PURPOSES**

### **Source Code (`src/`)**

**`scraper/`** - Core scraping logic
- `base.py`: Abstract base scraper with common functionality
- `page_extractor.py`: Extract metadata from main page (Layer 1)
- `workflow_extractor.py`: Extract workflow JSON from iframe (Layer 2)
- `explainer_extractor.py`: Extract tutorials and media (Layer 3)
- `orchestrator.py`: Coordinates all extractors with rate limiting

**`processors/`** - Data processing
- `ocr.py`: Image text extraction using Tesseract
- `video.py`: Video transcript extraction
- `validator.py`: Pydantic-based data validation
- `transformer.py`: Data normalization and transformation

**`storage/`** - Data persistence
- `database.py`: SQLite operations with SQLAlchemy ORM
- `exporter.py`: Export to JSON, JSONL, CSV, Parquet
- `media.py`: Download and manage media files
- `cache.py`: Caching layer to avoid re-scraping

**`models/`** - Data structures
- `schema.py`: Pydantic models matching dataset schema
- `enums.py`: Enumerations (difficulty, categories, etc.)
- `validators.py`: Custom validation logic

**`utils/`** - Shared utilities
- `config.py`: Configuration management
- `logger.py`: Loguru setup
- `rate_limiter.py`: Rate limiting with aiolimiter
- `retry.py`: Retry logic with tenacity

---

### **Scripts (`scripts/`)**

**Main Scripts:**
- `scrape.py`: Main scraping orchestrator (CLI)
- `validate.py`: Validate scraped data quality
- `export.py`: Export dataset to various formats
- `analyze.py`: Generate quality reports

**Utility Scripts:**
- `init_db.py`: Initialize SQLite database
- `cleanup.py`: Clean up temp files and logs

---

### **Testing (`tests/`)**

**Test Structure:**
- Unit tests for each module
- Integration tests for scraping workflow
- Fixtures for consistent test data
- 80%+ code coverage target

**Key Test Files:**
- `test_scraper.py`: Test scraping logic
- `test_processors.py`: Test OCR, video processing
- `test_storage.py`: Test database and export
- `test_models.py`: Test Pydantic validation

---

### **Configuration (`config/`)**

**Config Files:**
- `config.yaml`: Main configuration (rates, limits, paths)
- `config.dev.yaml`: Development overrides
- `config.prod.yaml`: Production settings
- `logging.yaml`: Logging configuration

**Example Structure:**
```yaml
scraper:
  max_concurrent: 3
  rate_limit: 2  # requests per second
  timeout: 30
  headless: true

storage:
  images_dir: "./media/images"
  database: "sqlite:///data/database/n8n_workflows.db"

quality:
  min_completeness_score: 90
  require_explainer: true
```

---

### **Data (`data/`)**

**`raw/`** - Unprocessed scraped data
- Individual workflow JSON files
- Timestamped for tracking

**`processed/`** - Validated data
- Validated workflows meeting quality criteria
- Ready for training

**`exports/`** - Final datasets
- Multiple formats for different use cases
- Versioned exports

**`database/`** - SQLite database
- Queryable workflow data
- Supports complex queries

---

### **Media (`media/`)**

**`images/`** - Downloaded images
- Original images from workflows
- Named by workflow ID + sequence
- OCR text extracted and stored in database

**`videos/`** - Video metadata
- YouTube video metadata
- Transcripts in JSON format
- Links to original videos

---

## 🚀 **QUICK START COMMANDS**

### **Local Development**

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env

# Initialize database
python scripts/init_db.py

# Run scraper (10 workflows test)
python scripts/scrape.py --workflows 10

# Validate data
python scripts/validate.py

# Export dataset
python scripts/export.py --format jsonl

# Run tests
pytest tests/ -v --cov=src
```

### **Docker Development**

```bash
# Build image
docker-compose build

# Run scraper
docker-compose up scraper

# Run with database viewer
docker-compose --profile dev up

# Run specific task
docker-compose run --rm scraper scripts/scrape.py --workflows 100

# Export data
docker-compose run --rm scraper scripts/export.py --format json

# Stop all
docker-compose down
```

---

## 📦 **FILE SIZE ESTIMATES**

```
Source Code:        ~50 KB
Dependencies:       ~400 MB (27 packages)
Data (2,100 workflows):
  - Raw JSON:       ~50 MB
  - Database:       ~75 MB
  - Media:          ~2-5 GB (images + videos)
  - Exports:        ~100 MB (all formats)
Total Project:      ~3-5 GB
```

---

## 🎯 **DEVELOPMENT WORKFLOW**

### **Day 1: Setup**
1. Clone repository
2. Install dependencies
3. Setup Docker environment
4. Initialize database
5. Test with 5 workflows

### **Days 2-5: Core Development**
1. Implement page extractor
2. Implement workflow extractor
3. Implement explainer extractor
4. Add OCR and video processing
5. Write unit tests

### **Days 6-10: Integration**
1. Build orchestrator
2. Add rate limiting
3. Implement retry logic
4. Add validation
5. Integration tests

### **Days 11-14: Polish**
1. Export functionality
2. Quality analysis
3. Documentation
4. Production testing
5. Dataset delivery

---

## ✅ **SUCCESS CHECKLIST**

Before considering the project complete:

- [ ] All 27 dependencies installed
- [ ] Playwright browser installed
- [ ] Database initialized
- [ ] Can scrape 1 workflow successfully
- [ ] Can scrape 10 workflows with 95%+ success
- [ ] All 3 layers extracting data
- [ ] OCR processing images
- [ ] Video transcripts extracted
- [ ] Data validation passing
- [ ] Export to all formats working
- [ ] Tests passing (80%+ coverage)
- [ ] Docker setup working
- [ ] Documentation complete

---

**This structure is optimized for:**
- ✅ Clear separation of concerns
- ✅ Easy testing and maintenance
- ✅ Scalable architecture
- ✅ Professional development practices
- ✅ 2-week sprint timeline

**Ready for implementation!** 🚀