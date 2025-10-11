# N8N Workflow Scraper - Setup Guide

**Version:** 1.0  
**Status:** Foundation Setup Complete  
**Date:** October 9, 2025

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Git
- SQLite3

### Installation

```bash
# 1. Clone repository (if not already done)
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium

# 5. Initialize database
python scripts/setup_db.py

# 6. Run tests
pytest

# 7. Verify installation
python -c "import playwright; import aiohttp; import sqlalchemy; import pydantic; print('✅ All imports OK')"
```

---

## 📁 Project Structure

```
n8n-scraper/
├── src/                    # Source code
│   ├── scrapers/          # Layer 1, 2, 3 extractors
│   ├── models/            # Pydantic data models
│   ├── database/          # SQLite operations
│   ├── utils/             # Helpers (logging, config)
│   └── orchestrator/      # Pipeline coordination
├── tests/                  # Test suite
├── data/                   # Data storage
│   ├── raw/               # Scraped data
│   ├── processed/         # Validated data
│   └── exports/           # Final outputs
├── docs/                   # Documentation
├── scripts/               # Utility scripts
├── logs/                  # Log files
└── requirements.txt       # Python dependencies
```

---

## 🗄️ Database Schema

### Workflows Table
Stores all extracted workflow data from 3 layers:
- Layer 1: Page metadata (title, author, categories, tags)
- Layer 2: Workflow structure (JSON, nodes, connections)
- Layer 3: Explainer content (tutorials, images, videos)

### Scraping Sessions Table
Tracks scraping sessions for monitoring and analytics.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_database.py -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

---

## 📊 Development Workflow

### For Dev1 (Extraction Specialist)
1. Review Layer 1 interface: `src/scrapers/layer1_metadata.py`
2. Review Layer 2 interface: `src/scrapers/layer2_structure.py`
3. Start with SCRAPE-002 (Page Metadata Extractor)
4. Then SCRAPE-003 (Workflow JSON Extractor)

### For Dev2 (Content Specialist)
1. Review Layer 3 interface: `src/scrapers/layer3_explainer.py`
2. Start with SCRAPE-005 (Explainer Content Extractor)
3. Then SCRAPE-006 (OCR & Video Processing)

---

## 🔍 Logging

Logs are automatically configured:
- **Console:** Colored, structured logging
- **File:** `logs/scraper.log` with rotation

```python
from src.utils.logging import logger

logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.success("Success message")
```

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Playwright Issues
```bash
# Reinstall browsers
playwright install chromium

# Install system dependencies (Linux)
playwright install-deps chromium
```

### Database Issues
```bash
# Recreate database
rm data/workflows.db
python scripts/setup_db.py
```

### Test Failures
```bash
# Clear pytest cache
pytest --cache-clear

# Run tests verbosely
pytest -vv
```

---

## 📞 Support

**If blocked:**
1. Check this README first
2. Review error messages carefully
3. Search Stack Overflow
4. Escalate to RND Manager if >30 min blocked

---

## ✅ Validation Checklist

Before starting development, ensure:
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Playwright browsers installed
- [ ] Database initialized
- [ ] All tests passing
- [ ] Imports working
- [ ] Logging configured

---

**Setup complete! Ready for parallel development.** 🚀

**Next:** Start SCRAPE-002, SCRAPE-003, SCRAPE-005 in parallel




