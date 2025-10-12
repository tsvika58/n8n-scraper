# SCRAPE-005: EVIDENCE INDEX

**Quick Reference Guide to All Evidence Files**

---

## 📁 EVIDENCE FILE LOCATIONS

All evidence stored in: `.coordination/testing/results/`

### **1. Test Results**
```
SCRAPE-005-test-results.txt
```
- **Content:** Complete pytest output
- **Shows:** 29/29 tests passing (100%)
- **Size:** ~8 KB

### **2. Coverage Report**
```
SCRAPE-005-coverage-report.txt
```
- **Content:** Detailed coverage analysis
- **Shows:** 58.33% coverage on layer3_explainer.py
- **Includes:** Missing line numbers

### **3. Dependencies Verification**
```
SCRAPE-005-dependencies.txt
```
- **Content:** All installed packages
- **Shows:** beautifulsoup4, lxml, Pillow, pytesseract, youtube-transcript-api, yt-dlp, playwright

### **4. Real Workflow Test Log**
```
SCRAPE-005-real-workflow-test.txt
```
- **Content:** Complete extraction log from real workflow
- **Shows:** 5.56s extraction time, 1,131 chars text, 23 images
- **Workflow:** n8n.io/workflows/2462 (Angie AI Assistant)

### **5. Real Extraction JSON**
```
SCRAPE-005-explainer-samples/workflow_2462_extraction.json
```
- **Content:** Complete extraction data structure
- **Size:** 5.2 KB
- **Shows:** All 13 Layer 3 fields populated

### **6. Validation Report**
```
../.coordination/deliverables/SCRAPE-005-VALIDATION-REPORT-TO-RND.md
```
- **Content:** Comprehensive validation with evidence cross-references
- **Size:** ~20 KB
- **Purpose:** Official submission to RND Manager

---

## 🔐 FILE INTEGRITY CHECKSUMS

**Production Code:**
```
MD5 (src/scrapers/layer3_explainer.py) = e276ba02e410dd3df65978148f06888c
```

**Test Code:**
```
MD5 (tests/unit/test_layer3_explainer.py) = 01aad6ec6fabced9397267b59dba5d64
```

---

## 📊 QUICK FACTS

**Production Code:** 586 lines  
**Test Code:** 614 lines  
**Total Tests:** 29 (100% passing)  
**Real Workflow:** Successfully extracted  
**Extraction Time:** 5.56 seconds  
**Text Extracted:** 1,131 characters  
**Images Collected:** 23 URLs  
**Dependencies:** All installed  

---

## ✅ VERIFICATION COMMANDS

**Re-verify line counts:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
wc -l src/scrapers/layer3_explainer.py tests/unit/test_layer3_explainer.py
```

**Re-run tests:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate
pytest tests/unit/test_layer3_explainer.py -v
```

**Re-verify checksums:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
md5 src/scrapers/layer3_explainer.py tests/unit/test_layer3_explainer.py
```

**View real extraction:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
cat .coordination/testing/results/SCRAPE-005-explainer-samples/workflow_2462_extraction.json
```

---

**All evidence is real, verifiable, and reproducible.**










