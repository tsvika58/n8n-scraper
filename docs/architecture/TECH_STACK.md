# N8N Workflow Scraper - Tech Stack v2.0 (Final)

**Version:** 2.0 - Post-RND Feedback  
**Date:** October 9, 2025  
**Status:** Approved and Ready for Implementation  
**Rating:** ⭐⭐⭐⭐⭐ (5/5 after optimizations)

---

## 📊 **EXECUTIVE SUMMARY**

### **Changes from v1.0 → v2.0**

| Category | v1.0 | v2.0 | Change |
|----------|------|------|--------|
| **Total Packages** | 37 | 27 | -27% ✅ |
| **Database** | PostgreSQL + SQLite | SQLite only | Simpler ✅ |
| **Image Processing** | Pillow + OpenCV | Pillow only | Leaner ✅ |
| **Cloud Storage** | boto3 included | Local only | Simpler ✅ |
| **Monitoring** | Prometheus + Sentry | Loguru + Rich | Appropriate ✅ |
| **Docker** | ❌ Missing | ✅ Included | Critical fix ✅ |
| **Install Time** | ~10 minutes | ~3-5 minutes | Faster ✅ |
| **Total Size** | ~800MB | ~400MB | Smaller ✅ |

**Result:** Leaner, faster, simpler while maintaining all core functionality.

---

## 🎯 **CORE TECHNOLOGY DECISIONS**

### **1. Language: Python 3.11+**

**Why Python:**
- ✅ Best web scraping ecosystem
- ✅ Excellent async support
- ✅ Rich ML/data science libraries
- ✅ Type safety with Pydantic
- ✅ Easy future model training

**Confirmed by RND:** ⭐⭐⭐⭐⭐ Perfect choice

---

### **2. Web Scraping: Playwright**

**Why Playwright over alternatives:**

| Feature | Playwright | Puppeteer | Selenium |
|---------|-----------|-----------|----------|
| **Iframe Handling** | Excellent ✅ | Good | Poor |
| **Auto-waiting** | Built-in ✅ | Manual | Manual |
| **Speed** | Fast ✅ | Fast | Slow |
| **Python Native** | Yes ✅ | No | Yes |
| **Modern** | Yes ✅ | Yes | Legacy |
| **Network Control** | Excellent ✅ | Good | Poor |

**Confirmed by RND:** ⭐⭐⭐⭐⭐ "Perfect for n8n's iframe-heavy structure"

```python
# Example: Playwright iframe handling
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    
    # Layer 1: Main page
    await page.goto('https://n8n.io/workflows/2462')
    
    # Layer 2: Workflow iframe (easy!)
    workflow_frame = page.frame_locator('iframe#workflow')
    workflow_data = await workflow_frame.evaluate('window.workflowData')
    
    # Layer 3: Explainer iframe (easy!)
    explainer_frame = page.frame_locator('iframe#explainer')
    explainer_text = await explainer_frame.inner_text('body')
```

---

### **3. Data Validation: Pydantic**

**Why Pydantic:**
- ✅ TypeScript-like type safety in Python
- ✅ Matches dataset schema perfectly
- ✅ Auto-validation saves development time
- ✅ Excellent error messages

**Confirmed by RND:** ⭐⭐⭐⭐⭐ "Brilliant choice"

```python
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class WorkflowData(BaseModel):
    id: str = Field(..., pattern=r'^\d+$')
    url: HttpUrl
    scraped_at: datetime
    basic_metadata: BasicMetadata
    workflow_content: WorkflowContent
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Auto-validation on creation
workflow = WorkflowData(
    id="2462",
    url="https://n8n.io/workflows/2462",
    scraped_at=datetime.now(),
    # ...
)  # Raises ValidationError if invalid
```

---

### **4. Database: SQLite (Only)**

**Decision:** Start with SQLite, skip PostgreSQL

**Why SQLite for this project:**
- ✅ Handles billions of rows (tested)
- ✅ Perfect for 2,100 workflows
- ✅ No server management
- ✅ Faster for read-heavy workloads
- ✅ Easy dataset distribution
- ✅ Zero configuration

**When to upgrade to PostgreSQL:**
- Dataset exceeds 100GB
- Need multi-user concurrent writes
- Building web API service
- Need advanced query features

**RND Feedback:** "Unless you need multi-user writes, SQLite is perfect"

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Simple SQLite setup
engine = create_engine('sqlite:///data/n8n_workflows.db')
Session = sessionmaker(bind=engine)

# PostgreSQL upgrade path (if needed later)
# engine = create_engine('postgresql://user:pass@localhost/n8n')
```

---

### **5. Async Architecture: asyncio + aiolimiter**

**Why async:**
- ✅ Scrape 100+ workflows concurrently
- ✅ Respectful rate limiting
- ✅ Efficient resource usage
- ✅ Easy to scale

**Confirmed by RND:** ⭐⭐⭐⭐⭐ "Essential for performance"

```python
import asyncio
from aiolimiter import AsyncLimiter

# Rate limiter: 2 requests per second
rate_limiter = AsyncLimiter(max_rate=2, time_period=1)

async def scrape_workflow(workflow_id: str):
    async with rate_limiter:  # Automatic rate limiting
        # Scraping logic here
        return workflow_data

# Scrape 100 workflows concurrently
async def scrape_batch(workflow_ids: List[str]):
    tasks = [scrape_workflow(wid) for wid in workflow_ids]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Run
results = asyncio.run(scrape_batch(workflow_ids))
```

---

### **6. OCR: Pillow + Tesseract (No OpenCV)**

**Decision:** Skip OpenCV for initial version

**Why Pillow is sufficient:**
- ✅ Basic image preprocessing (resize, crop, enhance)
- ✅ Compatible with Tesseract
- ✅ 60MB+ smaller than OpenCV
- ✅ Easier installation

**Add OpenCV later if you need:**
- Advanced preprocessing (denoising, skew correction)
- Face detection
- Complex image transformations

**RND Feedback:** "OpenCV adds 60MB+. Start with Pillow."

```python
from PIL import Image, ImageEnhance
import pytesseract

def extract_text_from_image(image_path: str) -> dict:
    # Open and preprocess with Pillow
    image = Image.open(image_path)
    
    # Enhance contrast for better OCR
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Convert to grayscale
    image = image.convert('L')
    
    # OCR with Tesseract
    text = pytesseract.image_to_string(image)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    return {
        'text': text,
        'confidence': sum(data['conf']) / len(data['conf']),
        'word_count': len([w for w in data['text'] if w.strip()])
    }
```

---

### **7. Storage: Local Files (No S3)**

**Decision:** Start with local storage

**Why local storage:**
- ✅ Simpler deployment
- ✅ ~2-5GB total (manageable)
- ✅ Include in dataset distribution
- ✅ Faster access
- ✅ No cloud costs

**Add boto3/S3 later if:**
- Dataset exceeds 50GB
- Need remote collaboration
- Building API service
- Want cloud backups

**RND Feedback:** "Do you actually need cloud storage?"

```python
# Local storage structure
media/
├── images/
│   ├── 2462_setup.png
│   ├── 2462_diagram.jpg
│   └── ...
└── videos/
    ├── 2462_tutorial.json  # Metadata + transcript
    └── ...

# S3 upgrade path (if needed)
# import boto3
# s3 = boto3.client('s3')
# s3.upload_file('local.png', 'bucket', 'workflows/2462.png')
```

---

### **8. Monitoring: Loguru + Rich (No Prometheus)**

**Decision:** Skip enterprise monitoring for CLI tool

**Why Loguru + Rich:**
- ✅ Beautiful terminal output
- ✅ Progress bars and tables
- ✅ Sufficient for 2-week sprint
- ✅ Easy debugging

**Add Prometheus/Sentry later if:**
- Building long-running service
- Need centralized monitoring
- Production deployment at scale

**RND Feedback:** "For CLI tool, Loguru + Rich is perfect"

```python
from loguru import logger
from rich.progress import Progress, BarColumn, TextColumn

# Beautiful logging
logger.add("scraper_{time}.log", rotation="1 day", level="INFO")
logger.info("Starting scraper...")
logger.success("Workflow 2462 scraped successfully!")
logger.error("Failed to scrape workflow 8237")

# Rich progress bars
with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
) as progress:
    task = progress.add_task("Scraping workflows...", total=2100)
    
    for workflow_id in workflow_ids:
        result = await scrape_workflow(workflow_id)
        progress.update(task, advance=1)
        logger.info(f"Scraped {workflow_id}: {result.completeness_score}%")
```

---

### **9. Containerization: Docker + Docker Compose**

**NEW ADDITION:** Critical improvement from RND feedback

**Why Docker:**
- ✅ Consistent environment across machines
- ✅ Easy dependency management
- ✅ Reproducible builds
- ✅ Team collaboration
- ✅ Production deployment

**Confirmed by RND:** "Add Docker - critical omission!"

```bash
# Build and run with Docker Compose
docker-compose up scraper

# Run specific task
docker-compose run --rm scraper scripts/scrape.py --workflows 100

# With database viewer for development
docker-compose --profile dev up

# Production deployment
docker-compose up -d scraper
```

---

## 📦 **COMPLETE PACKAGE LIST (27 Core)**

### **Core Scraping (6)**
```
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

### **Async & Concurrency (4)**
```
aiohttp==3.9.1
aiofiles==23.2.1
aiolimiter==1.1.0
tenacity==8.2.3
```

### **Data Processing (4)**
```
pandas==2.1.4
numpy==1.26.2
pydantic==2.5.2
orjson==3.9.10
```

### **Multimodal Processing (4)**
```
Pillow==10.1.0
pytesseract==0.3.10
youtube-transcript-api==0.6.1
yt-dlp==2023.12.30
```

### **Database (2)**
```
sqlalchemy==2.0.23
alembic==1.13.1
```

### **Monitoring (2)**
```
loguru==0.7.2
rich==13.7.0
```

### **Testing (4)**
```
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

### **Export (2)**
```
pyarrow==14.0.1
zstandard==0.22.0
```

### **Configuration (3)**
```
python-dotenv==1.0.0
pyyaml==6.0.1
click==8.1.7
```

### **Development (3)**
```
black==23.12.1
ruff==0.1.8
mypy==1.7.1
```

**Total: 27 packages** (down from 37)

---

## 📊 **PERFORMANCE PROJECTIONS**

### **With Optimized Stack**

```python
# Configuration
total_workflows = 2100
concurrent_scrapers = 3
rate_limit = 2  # req/sec
avg_scrape_time = 35  # seconds/workflow

# Timeline Estimates
best_case = 18  # hours (perfect conditions)
realistic = 24  # hours (with retries)
conservative = 30  # hours (with issues)

# Quality Targets
completeness_target = 95  # percent
success_rate_target = 95  # percent
```

**Expected Results:**
- ✅ Scrape 2,100 workflows in 24-30 hours
- ✅ 95%+ completeness score
- ✅ 95%+ success rate
- ✅ All multimodal content extracted

---

## 🎯 **IMPLEMENTATION PHASES**

### **Phase 1: Setup (Day 1)**
- Install dependencies
- Setup Docker environment
- Initialize database
- Test with 5 workflows

### **Phase 2: Core Development (Days 2-5)**
- Implement 3-layer extractors
- Add OCR and video processing
- Write unit tests
- Test with 50 workflows

### **Phase 3: Integration (Days 6-10)**
- Build orchestrator
- Add rate limiting and retry
- Implement validation
- Integration tests
- Test with 500 workflows

### **Phase 4: Production (Days 11-14)**
- Export functionality
- Quality analysis
- Full scrape (2,100 workflows)
- Documentation
- Dataset delivery

---

## ✅ **QUALITY GATES**

### **Gate 1: Basic Functionality**
- [ ] Can scrape 1 workflow successfully
- [ ] All 3 layers extracting data
- [ ] Data validates against schema

### **Gate 2: Reliability**
- [ ] 10 workflows with 90%+ success
- [ ] OCR processing images correctly
- [ ] Video transcripts extracted

### **Gate 3: Scale**
- [ ] 100 workflows with 95%+ success
- [ ] Rate limiting working
- [ ] Retry logic handling failures

### **Gate 4: Production Ready**
- [ ] 2,100 workflows scraped
- [ ] 95%+ completeness scores
- [ ] All export formats working
- [ ] Docker deployment tested

---

## 🚀 **QUICK START**

### **Local Development**

```bash
# 1. Clone and setup
git clone <repo>
cd n8n-scraper
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies (~3-5 minutes)
pip install -r requirements.txt
playwright install chromium

# 3. Configure
cp .env.example .env
# Edit .env with your settings

# 4. Initialize
python scripts/init_db.py

# 5. Test scrape (10 workflows)
python scripts/scrape.py --workflows 10

# 6. Validate
python scripts/validate.py

# 7. Export
python scripts/export.py --format jsonl
```

### **Docker (Recommended)**

```bash
# 1. Clone
git clone <repo>
cd n8n-scraper

# 2. Configure
cp .env.example .env

# 3. Build and run
docker-compose up scraper

# Or run specific tasks
docker-compose run --rm scraper scripts/scrape.py --workflows 100
docker-compose run --rm scraper scripts/validate.py
docker-compose run --rm scraper scripts/export.py --format json
```

---

## 🎯 **SUCCESS METRICS**

### **Development Metrics**
- Setup time: <30 minutes
- First successful scrape: Day 1
- 100 workflows scraped: Day 5
- Full dataset: Day 13

### **Quality Metrics**
- Completeness score: 95%+
- Success rate: 95%+
- Test coverage: 80%+
- Data validation: 100%

### **Performance Metrics**
- Scrape time: 24-30 hours total
- Rate: ~70-90 workflows/hour
- Retry overhead: <10%
- Storage: ~3-5GB total

---

## 🏆 **FINAL VERDICT**

### **RND Rating: ⭐⭐⭐⭐⭐ (5/5)**

**Strengths:**
- ✅ Excellent core technology choices
- ✅ Optimized for 2-week sprint
- ✅ Production-ready from start
- ✅ Easy to expand later
- ✅ Docker added for consistency

**Previous Concerns Addressed:**
- ✅ Removed unnecessary packages (37 → 27)
- ✅ Simplified database (SQLite only)
- ✅ Removed premature optimization (OpenCV, boto3, Prometheus)
- ✅ Added Docker for reproducibility

**Result:** "Lean, mean, scraping machine!" 🚀

---

## 📋 **DELIVERABLES**

With this stack, you will deliver:

1. **Complete Dataset**
   - 2,100+ workflows with 95%+ completeness
   - JSON, JSONL, CSV, Parquet formats
   - ~3-5GB total size

2. **Production Code**
   - Well-tested (80%+ coverage)
   - Type-safe (Pydantic + mypy)
   - Documented (inline + docs/)
   - Containerized (Docker)

3. **Documentation**
   - Project brief
   - Technical guide
   - API documentation
   - Dataset schema
   - Setup instructions

4. **Quality Assurance**
   - Validation reports
   - Quality metrics
   - Pattern analysis
   - Completeness scores

---

## 🎯 **READY FOR IMPLEMENTATION**

**Status:** ✅ Approved by RND  
**Timeline:** 2 weeks with 1 developer  
**Success Rate:** 95%+ with this stack  
**Next Step:** Create project skeleton and begin development  

---

**This is a production-ready tech stack optimized for your specific needs. Let's build! 🚀**

**Version:** 2.0 Final  
**Status:** Approved and Ready  
**Date:** October 9, 2025