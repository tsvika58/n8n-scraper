# 📁 SCRAPE-002B - Complete File Locations & Access Guide

**Generated:** October 10, 2025, 17:43 PM  
**Total Workflows:** 6,022  
**Total Files Created:** 10

---

## 🗂️ ALL FILE LOCATIONS

### **1. DATABASE FILE**

**Location:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/data/workflows.db`  
**Size:** 2.7 MB  
**Contains:** 6,022 workflow records in `workflow_inventory` table

**Quick Access:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
sqlite3 data/workflows.db
```

---

### **2. EVIDENCE FILES** (All in `.coordination/testing/results/`)

#### **2.1 SCRAPE-002B-inventory-summary.json**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-inventory-summary.json`  
**Size:** 765 bytes  
**Contains:** Overall metrics, workflow counts, ID ranges

**View:**
```bash
cat .coordination/testing/results/SCRAPE-002B-inventory-summary.json
```

---

#### **2.2 SCRAPE-002B-crawl-log.txt**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-crawl-log.txt`  
**Size:** 892 bytes  
**Contains:** Complete crawl execution log

**View:**
```bash
cat .coordination/testing/results/SCRAPE-002B-crawl-log.txt
```

---

#### **2.3 SCRAPE-002B-sample-inventory.json**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-sample-inventory.json`  
**Size:** 23 KB  
**Contains:** First 100 workflows with complete data

**View:**
```bash
cat .coordination/testing/results/SCRAPE-002B-sample-inventory.json | jq .
```

---

#### **2.4 SCRAPE-002B-database-export.txt**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-database-export.txt`  
**Size:** 10 KB  
**Contains:** First 100 database records in pipe-delimited format

**View:**
```bash
cat .coordination/testing/results/SCRAPE-002B-database-export.txt
```

---

#### **2.5 SCRAPE-002B-errors.log**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-errors.log`  
**Size:** 622 bytes  
**Contains:** Error log (spoiler: zero errors!)

**View:**
```bash
cat .coordination/testing/results/SCRAPE-002B-errors.log
```

---

#### **2.6 SCRAPE-002B-all-workflow-urls.txt** ⭐ **NEW**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt`  
**Size:** 597 KB  
**Contains:** ALL 6,022 workflow URLs (one per line)

**View:**
```bash
cat .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
# or
less .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
# or open in your editor
```

---

### **3. CODE FILES**

#### **3.1 workflow_inventory_crawler.py**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/src/scrapers/workflow_inventory_crawler.py`  
**Size:** 6.4 KB  
**Contains:** Sitemap-based workflow inventory crawler

---

#### **3.2 inventory_schema.py**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/src/database/inventory_schema.py`  
**Size:** 8.1 KB  
**Contains:** Database schema and management functions

---

#### **3.3 build_workflow_inventory.py**
**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/scripts/build_workflow_inventory.py`  
**Size:** 5.4 KB  
**Contains:** Production orchestration script

---

### **4. SUBMISSION DOCUMENT**

**Full Path:** `/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/handoffs/dev1-to-rnd-SCRAPE-002B-INVENTORY-SUBMISSION.md`  
**Size:** 13 KB  
**Contains:** Complete submission document with all details

---

## 🔍 HOW TO ACCESS ALL WORKFLOW URLS

### **Option 1: View in Terminal**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
cat .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
```

### **Option 2: View with Pagination**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
less .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
# Use arrows to scroll, 'q' to quit
```

### **Option 3: Search for Specific URLs**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
grep "sales" .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
```

### **Option 4: Export Specific Range**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
sqlite3 data/workflows.db "SELECT url FROM workflow_inventory WHERE CAST(workflow_id AS INTEGER) BETWEEN 1000 AND 2000;"
```

### **Option 5: Open in Your Editor**
Just open this file in VS Code or any text editor:
```
/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/.coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
```

---

## 📊 DATABASE QUERIES

### **Count Total Workflows**
```bash
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflow_inventory;"
```
**Expected:** 6022

---

### **Get Workflow ID Range**
```bash
sqlite3 data/workflows.db "SELECT MIN(CAST(workflow_id AS INTEGER)), MAX(CAST(workflow_id AS INTEGER)) FROM workflow_inventory;"
```
**Expected:** 1|9390

---

### **Check for Duplicates**
```bash
sqlite3 data/workflows.db "SELECT workflow_id, COUNT(*) FROM workflow_inventory GROUP BY workflow_id HAVING COUNT(*) > 1;"
```
**Expected:** 0 rows (no duplicates)

---

### **Get Random 10 Workflows**
```bash
sqlite3 data/workflows.db "SELECT workflow_id, title, url FROM workflow_inventory ORDER BY RANDOM() LIMIT 10;"
```

---

### **Search by Keyword**
```bash
sqlite3 data/workflows.db "SELECT workflow_id, title, url FROM workflow_inventory WHERE title LIKE '%sales%' OR title LIKE '%email%' LIMIT 20;"
```

---

## 🌐 SAMPLE WORKFLOW URLS

Here are some example workflows from the inventory:

1. https://n8n.io/workflows/1-insert-excel-data-to-postgres
2. https://n8n.io/workflows/2-transfer-data-from-postgres-to-excel
3. https://n8n.io/workflows/4-send-selected-github-events-to-slack
4. https://n8n.io/workflows/29-send-typeform-results-to-google-sheet-slack-and-email
5. https://n8n.io/workflows/100-using-the-merge-node-merge-by-key

**All 6,022 URLs are in:** `SCRAPE-002B-all-workflow-urls.txt`

---

## ✅ VERIFICATION CHECKLIST

Run these commands to verify everything:

```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# 1. Verify database exists
ls -lh data/workflows.db

# 2. Verify all evidence files
ls -lh .coordination/testing/results/SCRAPE-002B*

# 3. Count workflows in database
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflow_inventory;"

# 4. Check for duplicates
sqlite3 data/workflows.db "SELECT workflow_id, COUNT(*) FROM workflow_inventory GROUP BY workflow_id HAVING COUNT(*) > 1;"

# 5. View first 20 URLs
head -20 .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt

# 6. Count lines in URL file (should be 6022)
wc -l .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
```

---

## 📋 FILE TREE STRUCTURE

```
/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper/
│
├── data/
│   └── workflows.db (2.7 MB) ✅
│
├── src/
│   ├── scrapers/
│   │   └── workflow_inventory_crawler.py (6.4 KB) ✅
│   └── database/
│       └── inventory_schema.py (8.1 KB) ✅
│
├── scripts/
│   └── build_workflow_inventory.py (5.4 KB) ✅
│
└── .coordination/
    ├── testing/
    │   └── results/
    │       ├── SCRAPE-002B-inventory-summary.json (765 B) ✅
    │       ├── SCRAPE-002B-crawl-log.txt (892 B) ✅
    │       ├── SCRAPE-002B-sample-inventory.json (23 KB) ✅
    │       ├── SCRAPE-002B-database-export.txt (10 KB) ✅
    │       ├── SCRAPE-002B-errors.log (622 B) ✅
    │       ├── SCRAPE-002B-all-workflow-urls.txt (597 KB) ⭐ NEW
    │       └── SCRAPE-002B-FILE-LOCATIONS.md (this file)
    │
    └── handoffs/
        └── dev1-to-rnd-SCRAPE-002B-INVENTORY-SUBMISSION.md (13 KB) ✅
```

---

## 🎯 QUICK ACCESS SUMMARY

**To see ALL workflow URLs right now:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
cat .coordination/testing/results/SCRAPE-002B-all-workflow-urls.txt
```

**Or open in your editor:**
- Navigate to: `shared-tools/n8n-scraper/.coordination/testing/results/`
- Open: `SCRAPE-002B-all-workflow-urls.txt`
- This file contains all 6,022 workflow URLs!

---

**All files validated and confirmed to exist! ✅**





