# 📋 **RND TASK ASSIGNMENT: SCRAPE-002 v2.1**

**RND Task ID:** RND-SCRAPE-002-v2.1  
**PM Task Reference:** PM Task Brief v2.1 - SCRAPE-002 (10 Sales Workflows)  
**Assigned To:** Developer-1 (Dev1)  
**From:** RND Manager  
**Issued Date:** October 10, 2025, 02:10 AM  
**Expected Completion:** October 11, 2025, 18:00  
**Estimated Effort:** 6-8 hours

---

## 🎯 **YOUR MISSION**

**Extract complete metadata from 10 specific n8n.io sales/lead generation workflows, store in database with 90%+ success rate, 80%+ test coverage, and provide complete evidence package.**

---

## 📚 **CONTEXT & REFERENCE**

### **Original PM Task Brief:**
- **Version:** PM Brief v2.1 (received from Master Orchestrator)
- **Scope Change:** Reduced from 50 → 10 workflows (strategic decision)
- **Focus:** Sales and lead generation workflows only
- **Read this:** For complete business context and requirements

### **What PM Wants:**
PM needs metadata extracted from 10 pre-selected sales/lead gen workflows to validate the Layer 1 extractor on business-critical workflows before scaling to full production. This is a focused validation phase - full production scraping will happen in SCRAPE-002B after workflow inventory is built.

### **What I Need From You:**
I need ACTUAL evidence of completion on these 10 SPECIFIC workflows:
- 10/10 workflow extractions (I'll verify in database)
- 90%+ success rate (9/10 minimum, 10/10 preferred)
- 80%+ coverage (I'll run pytest --cov myself)
- 35+ tests passing (I'll run pytest -v myself)
- All 6 evidence files exist (I'll check with ls)
- All numbers match (I'll compare your claims vs my verification)

### **Why This Matters:**
This validates your extractor on business-critical sales workflows before production scale. Success here means SCRAPE-002B (full production) will use your proven extractor on hundreds/thousands of workflows.

---

## 🎯 **THE 10 TARGET WORKFLOWS**

Extract metadata from these EXACT 10 workflows (all sales/lead gen focused):

| # | Workflow ID | Category | URL |
|---|-------------|----------|-----|
| 1 | **2462** | Lead Scoring & Qualification | https://n8n.io/workflows/2462 |
| 2 | **1954** | Sales Email Automation | https://n8n.io/workflows/1954 |
| 3 | **2103** | CRM Data Sync (Slack) | https://n8n.io/workflows/2103 |
| 4 | **2234** | Email Campaign Management | https://n8n.io/workflows/2234 |
| 5 | **1756** | Lead Enrichment Pipeline | https://n8n.io/workflows/1756 |
| 6 | **1832** | Customer Feedback Collection | https://n8n.io/workflows/1832 |
| 7 | **2156** | Social Media Lead Gen | https://n8n.io/workflows/2156 |
| 8 | **1923** | Sales Invoice Processing | https://n8n.io/workflows/1923 |
| 9 | **2087** | Automated Lead Scoring | https://n8n.io/workflows/2087 |
| 10 | **2145** | Sales Notification System | https://n8n.io/workflows/2145 |

**Note:** All 10 were validated by Dev2 in SCRAPE-005 - they definitely exist and are accessible.

**Your extraction script should target ONLY these 10 specific workflow IDs.**

---

## ✅ **YOUR DELIVERABLES CHECKLIST**

### **Code Deliverables:**

- [ ] **Implementation:** `src/scrapers/layer1_metadata.py`
  - Must contain: `PageMetadataExtractor` class
  - Must do: Extract metadata from workflow detail pages, handle errors, respect rate limits, store in database
  - Must handle: The 10 specific workflow IDs listed above
  
- [ ] **Unit Tests:** `tests/unit/test_layer1_metadata.py`
  - Minimum: 30 unit tests
  - Must test: All extraction methods, error handling, edge cases
  - All must pass: 100%

- [ ] **Integration Tests:** `tests/integration/test_layer1_integration.py`
  - Minimum: 5 integration tests
  - Must test: End-to-end extraction with 3-5 of the 10 target workflows
  - All must pass: 100%

- [ ] **Documentation:**
  - [ ] All functions have docstrings
  - [ ] README updated with usage examples
  - [ ] Inline comments for complex logic

---

### **Evidence Files You MUST Create:**

**Location for ALL files:** `.coordination/testing/results/`

---

#### **1. `SCRAPE-002-test-output.txt`** ⭐ **REQUIRED**

**What it is:** Complete pytest output showing all tests passing

**How to create:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate

# FIRST: Run and WATCH tests (don't save yet)
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v

# ONLY AFTER seeing them all pass, save to file:
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v > .coordination/testing/results/SCRAPE-002-test-output.txt 2>&1
```

**Must show:**
- At least 35 tests with PASSED status
- Final summary: `XX passed, 0 failed` where XX ≥ 35
- No errors, no failures, no skips

**I will verify by:**
- Running same command myself
- Counting tests
- Comparing results
- **If different → INSTANT REJECT**

---

#### **2. `SCRAPE-002-coverage-report.txt`** ⭐ **REQUIRED**

**What it is:** Complete coverage report showing ≥80% coverage

**How to create:**
```bash
# FIRST: Run and WATCH coverage (don't save yet)
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing

# ONLY AFTER seeing ≥80%, save to file:
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing > .coordination/testing/results/SCRAPE-002-coverage-report.txt 2>&1
```

**Must show:**
- Line: `src/scrapers/layer1_metadata.py  XXX  YYY  ZZ.ZZ%`
- ZZ.ZZ must be ≥ 80.00
- List of covered/missed line numbers

**I will verify by:**
- Running same command myself
- Checking percentage
- **If <80% or doesn't match → INSTANT REJECT**

---

#### **3. `SCRAPE-002-10-workflow-summary.json`** ⭐ **REQUIRED**

**What it is:** Overall metrics for all 10 workflows extracted

**How to create:**
After running your extraction on the 10 target workflows, create this JSON with ACTUAL numbers:

```json
{
  "task_id": "SCRAPE-002",
  "total_workflows_attempted": 10,
  "successful_extractions": 10,
  "failed_extractions": 0,
  "partial_extractions": 0,
  "success_rate": 100.0,
  "average_extraction_time": "3.2s",
  "min_time": "2.1s",
  "max_time": "4.8s",
  "total_time": "32s",
  "extraction_date": "2025-10-11",
  "workflow_focus": "sales_lead_generation",
  "target_workflows": [
    "2462", "1954", "2103", "2234", "1756",
    "1832", "2156", "1923", "2087", "2145"
  ]
}
```

**All numbers must be ACTUAL.**

**I will verify by:**
- Querying database for these 10 workflow IDs
- Verifying success_rate ≥ 90.0
- **If database count ≠ your claim → INSTANT REJECT**

---

#### **4. `SCRAPE-002-sample-extractions/` folder** ⭐ **REQUIRED**

**What it is:** Folder with ALL 10 workflow extraction JSONs

**How to create:**
```bash
# Create folder
mkdir -p .coordination/testing/results/SCRAPE-002-sample-extractions

# Save ALL 10 extractions as individual JSON files
# Files: workflow_2462.json, workflow_1954.json, workflow_2103.json, etc.
```

**Each file format:**
```json
{
  "workflow_id": "2462",
  "title": "Lead Scoring & Qualification",
  "url": "https://n8n.io/workflows/2462",
  "author": "Igor Fediczko",
  "views": 1523,
  "created_date": "2024-03-15",
  "category": ["Sales", "Lead Gen"],
  "tags": ["crm", "scoring", "qualification"],
  "description": "Automated lead scoring system...",
  "extraction_time": "3.2s",
  "extraction_status": "complete"
}
```

**Must have:** ALL 10 workflow files (not 5, not 8, but 10)

**I will verify by:**
```bash
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l
# Must show exactly 10
```
- Opening 3-4 random samples
- Checking all required fields present
- Verifying real n8n.io URLs
- **If ≠10 files or missing fields → INSTANT REJECT**

---

#### **5. `SCRAPE-002-database-query.txt`** ⭐ **REQUIRED**

**What it is:** Database query showing all 10 records stored

**How to create:**
```bash
sqlite3 data/workflows.db "SELECT workflow_id, title, author, created_date FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');" > .coordination/testing/results/SCRAPE-002-database-query.txt
```

**Must show:** All 10 workflow records

**I will verify by:**
- Running same query myself
- Counting rows
- **If ≠10 rows → INSTANT REJECT**

---

#### **6. `SCRAPE-002-evidence-summary.json`** ⭐ **REQUIRED**

**What it is:** JSON with all key metrics

**How to create:**
Create manually with ACTUAL numbers from your test runs:

```json
{
  "task_id": "SCRAPE-002",
  "completion_date": "2025-10-11 17:00",
  "developer": "Dev1",
  "pm_task_reference": "SCRAPE-002-v2.1",
  "rnd_task_reference": "RND-SCRAPE-002-v2.1",
  "scope": "10 sales/lead generation workflows",
  "test_results": {
    "total_tests": 38,
    "passing_tests": 38,
    "failing_tests": 0,
    "pass_rate_percent": 100.0
  },
  "coverage": {
    "target_percent": 80.0,
    "actual_percent": 84.2,
    "meets_requirement": true
  },
  "extraction_results": {
    "total_workflows": 10,
    "successful": 10,
    "failed": 0,
    "success_rate": 100.0
  },
  "deliverables": {
    "implementation_file": "src/scrapers/layer1_metadata.py",
    "test_file_unit": "tests/unit/test_layer1_metadata.py",
    "test_file_integration": "tests/integration/test_layer1_integration.py",
    "evidence_files_created": [
      "SCRAPE-002-test-output.txt",
      "SCRAPE-002-coverage-report.txt",
      "SCRAPE-002-10-workflow-summary.json",
      "SCRAPE-002-sample-extractions/ (10 files)",
      "SCRAPE-002-database-query.txt",
      "SCRAPE-002-evidence-summary.json"
    ]
  },
  "requirements_checklist": {
    "extract_10_workflows": "PASS",
    "success_rate_90_percent": "PASS",
    "zero_failures": "PASS",
    "coverage_80_percent": "PASS",
    "tests_35_minimum": "PASS",
    "tests_100_percent_pass": "PASS",
    "all_required_fields": "PASS",
    "rate_limiting_2sec": "PASS",
    "database_storage": "PASS"
  },
  "self_validation": {
    "all_tests_run_and_watched": true,
    "coverage_verified_actual": true,
    "evidence_files_exist_all": true,
    "database_verified_10_workflows": true,
    "ready_for_rnd": true
  }
}
```

**CRITICAL:** All numbers must match actual outputs. I will compare this to my verification.

---

## 🎯 **SPECIFIC REQUIREMENTS**

### **Requirement #1: Extract All 10 Target Workflows** ⭐ **CRITICAL**

**What you must do:**
Extract metadata from these EXACT 10 workflow IDs:
```
2462, 1954, 2103, 2234, 1756, 1832, 2156, 1923, 2087, 2145
```

**How I will verify it:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');"
```

**Evidence needed:**
- [ ] `SCRAPE-002-10-workflow-summary.json` showing all 10 attempted
- [ ] `SCRAPE-002-sample-extractions/` with ALL 10 workflow JSON files
- [ ] `SCRAPE-002-database-query.txt` showing all 10 records

**Pass criteria:** Database shows all 10 workflow IDs  
**Fail criteria:** Database has <10 of these specific IDs = **INSTANT REJECT**

---

### **Requirement #2: Achieve 90%+ Success Rate** ⭐ **CRITICAL**

**What you must do:**
Successfully extract at least 9 out of 10 workflows (10/10 = 100% is preferred).

**How I will verify it:**
```bash
cat .coordination/testing/results/SCRAPE-002-10-workflow-summary.json | grep "success_rate"
```

**Evidence needed:**
- [ ] `SCRAPE-002-10-workflow-summary.json` with `"success_rate": 90.0` or higher

**Pass criteria:** success_rate ≥ 90.0 (9/10 or 10/10)  
**Fail criteria:** success_rate < 90.0 (≤8/10) = **INSTANT REJECT**

---

### **Requirement #3: Zero Complete Failures** ⭐ **CRITICAL**

**What you must do:**
Handle errors gracefully. All 10 workflows should extract successfully or with partial data (no complete crashes).

**How I will verify it:**
```bash
cat .coordination/testing/results/SCRAPE-002-10-workflow-summary.json | grep "failed_extractions"
```

**Evidence needed:**
- [ ] `SCRAPE-002-10-workflow-summary.json` with `"failed_extractions": 0` or very low

**Pass criteria:** failed_extractions = 0  
**Fail criteria:** failed_extractions > 1 = **REVIEW** (may reject)

---

### **Requirement #4: Test Coverage ≥80%** ⭐ **CRITICAL**

**What you must do:**
Write comprehensive tests that cover at least 80% of `layer1_metadata.py`.

**Your current status:** 77.17% (need +2.83% = ~10 more lines)

**How I will verify it:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing
```

**Evidence needed:**
- [ ] `SCRAPE-002-coverage-report.txt` showing ≥80%
- [ ] When I run same command, get ≥80%

**Pass criteria:** Coverage ≥ 80.00%  
**Fail criteria:** Coverage < 80.00% = **INSTANT REJECT**

**How to increase from 77% to 80%+:**
1. Run: `pytest --cov=src.scrapers.layer1_metadata --cov-report=html`
2. Open: `htmlcov/index.html`
3. Find uncovered lines (lines 195-197, 220-222, 229-231, etc.)
4. Write tests that execute those lines
5. Repeat until ≥80%

---

### **Requirement #5: 35+ Tests, 100% Passing** ⭐ **CRITICAL**

**What you must do:**
Write at least 35 tests (30 unit + 5 integration) and ALL must pass.

**Your current status:** 34 tests passing (need 1+ more)

**How I will verify it:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v
```

**Evidence needed:**
- [ ] `SCRAPE-002-test-output.txt` showing 35+ passed, 0 failed
- [ ] When I run same command, get 35+ passed

**Pass criteria:** Tests ≥ 35 AND all passing (100%)  
**Fail criteria:** Tests < 35 OR any failures = **INSTANT REJECT**

**Suggested additional tests:**
```python
# Add to tests/integration/test_layer1_integration.py
def test_extract_all_10_target_workflows():
    """Test extraction of all 10 specific target workflows."""
    target_ids = ['2462', '1954', '2103', '2234', '1756',
                  '1832', '2156', '1923', '2087', '2145']
    # Test your extractor can handle all 10
```

---

### **Requirement #6: Extract All Required Fields** ⭐ **REQUIRED**

**What you must do:**
Extract these fields from each of the 10 workflows:

**REQUIRED (must have in every workflow):**
1. workflow_id
2. title
3. url
4. author
5. created_date
6. category

**OPTIONAL (best effort):**
7. views
8. tags
9. description
10. difficulty_level

**How I will verify it:**
```bash
# Check all 10 sample files
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_2462.json
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_1954.json
# ... check all 10
```

**Evidence needed:**
- [ ] All 10 sample JSONs showing all 6 required fields present

**Pass criteria:** All 6 required fields in all 10 samples  
**Fail criteria:** Any required field missing in any sample = **INSTANT REJECT**

---

### **Requirement #7: Respect Rate Limiting** ⭐ **REQUIRED**

**What you must do:**
Implement 2-second delay between requests.

**How I will verify it:**
- Review code for `time.sleep(2)` or similar
- Check total extraction time (10 workflows × 2s = ~20s minimum)

**Evidence needed:**
- [ ] Code showing rate limiting
- [ ] Summary JSON shows total_time ≥ 20s (proves delays happened)

**Pass criteria:** Code has rate limiting AND total time proves it  
**Fail criteria:** No rate limiting or suspiciously fast = **REJECT**

---

### **Requirement #8: Store in Database** ⭐ **REQUIRED**

**What you must do:**
Store all 10 extracted workflows in SQLite database.

**How I will verify it:**
```bash
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');"
```

**Evidence needed:**
- [ ] `SCRAPE-002-database-query.txt` showing all 10 records
- [ ] When I query, see all 10 records

**Pass criteria:** Database has all 10 workflow IDs  
**Fail criteria:** Database missing any of the 10 = **INSTANT REJECT**

---

### **Requirement #9: Reference Notion Task** 📖 **INFORMATIONAL**

**What you must do:**
Reference the original task at https://www.notion.so/287d7960213a81778c49fe83794cad14 for business context.

**Note:** You do NOT update Notion. Only read it for task context. Master Orchestrator/PM manage Notion updates.

**How I will verify it:**
- Not applicable - Notion managed by Master Orchestrator/PM

**Pass criteria:** N/A - informational only  
**Fail criteria:** N/A

---

## 📊 **QUALITY TARGETS**

### **Test Coverage:**
- **Minimum Required:** 80.0%
- **Your current:** 77.17% (need +2.83%)
- **Target for excellence:** 85-90%

**How to increase:**
1. Run: `pytest --cov-report=html`
2. Open: `htmlcov/index.html`
3. Find red lines (uncovered)
4. Write tests for ~10 lines
5. Reach 80%+

---

### **Test Count:**
- **Minimum Required:** 35 tests
- **Your current:** 34 tests
- **Need:** 1+ more test

**Suggested:**
```python
# Add to tests/integration/test_layer1_integration.py
def test_extract_all_target_workflows():
    """Test extraction of all 10 target workflows."""
    # This gives you the 35th test
```

---

### **Success Rate:**
- **Minimum:** 90% (9/10 workflows)
- **Target:** 100% (10/10 workflows)
- **All 10 workflow IDs are known valid** (verified by Dev2)

---

## 🧪 **TESTING PROTOCOL**

### **How to Run Tests (Step by Step):**

```bash
# Step 1: Navigate to project
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Step 2: Activate environment
source venv/bin/activate

# Step 3: Run tests and WATCH them (don't pipe yet!)
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v

# You should SEE each test execute:
# test_extractor_initialization PASSED
# test_extract_basic_metadata PASSED
# ... etc ...

# Step 4: Check coverage and WATCH output
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing

# You should SEE coverage percentage display
# Must be ≥ 80.00%

# Step 5: ONLY AFTER seeing everything pass, save to files
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v > .coordination/testing/results/SCRAPE-002-test-output.txt 2>&1
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing > .coordination/testing/results/SCRAPE-002-coverage-report.txt 2>&1
```

**CRITICAL:** Always watch tests run live first. Never pipe to file without seeing them pass first.

---

## 🔍 **YOUR SELF-VALIDATION (Before Submitting to RND)**

### **Step 1: Code Exists (2 min)**
```bash
ls -la src/scrapers/layer1_metadata.py
ls -la tests/unit/test_layer1_metadata.py
ls -la tests/integration/test_layer1_integration.py
python -m py_compile src/scrapers/layer1_metadata.py
```
- [ ] All files exist
- [ ] No syntax errors

---

### **Step 2: Tests Pass (5-10 min)**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v
```
- [ ] Watched all tests run
- [ ] All 35+ tests passed
- [ ] No failures, no errors
- [ ] Final line: `XX passed, 0 failed` where XX ≥ 35

---

### **Step 3: Coverage Meets Target (3-5 min)**
```bash
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing
```
- [ ] Watched coverage display
- [ ] Coverage ≥ 80.00%
- [ ] Wrote down actual: _____%

---

### **Step 4: Extract 10 Target Workflows (5 min)**
```bash
# Run your extraction on the 10 specific workflow IDs
python scripts/extract_workflows.py --ids 2462,1954,2103,2234,1756,1832,2156,1923,2087,2145
# OR however your script runs

# Verify database has all 10
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');"
# Must show: 10
```
- [ ] Extraction completed successfully
- [ ] No crashes
- [ ] Database shows 10 records

---

### **Step 5: Create ALL Evidence Files (5-10 min)**
```bash
mkdir -p .coordination/testing/results/SCRAPE-002-sample-extractions

# 1. Test output
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v > .coordination/testing/results/SCRAPE-002-test-output.txt 2>&1

# 2. Coverage report
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing > .coordination/testing/results/SCRAPE-002-coverage-report.txt 2>&1

# 3. Database query
sqlite3 data/workflows.db "SELECT workflow_id, title, author, created_date FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');" > .coordination/testing/results/SCRAPE-002-database-query.txt

# 4. Save all 10 workflow JSONs to sample-extractions folder
# 5. Create 10-workflow-summary.json
# 6. Create evidence-summary.json

# Verify all exist
ls -la .coordination/testing/results/SCRAPE-002*
ls -la .coordination/testing/results/SCRAPE-002-sample-extractions/
```
- [ ] All 6 files/folders created
- [ ] Sample-extractions has ALL 10 workflow files
- [ ] All files not empty

---

### **Step 6: Verify Numbers Match (5 min)**
```bash
# Count tests
grep "passed" .coordination/testing/results/SCRAPE-002-test-output.txt

# Check coverage
grep "layer1_metadata.py" .coordination/testing/results/SCRAPE-002-coverage-report.txt

# Count workflows in folder
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l
# Must show: 10

# Check evidence summary
cat .coordination/testing/results/SCRAPE-002-evidence-summary.json
```
- [ ] Test count matches (35+)
- [ ] Coverage matches (≥80%)
- [ ] Workflow count = 10
- [ ] All numbers consistent

---

### **Step 7: Final Check (5 min)**
- [ ] Read PM's original brief again
- [ ] All 10 specific workflow IDs extracted
- [ ] ALL checkboxes above checked
- [ ] No "almost done" - 100% complete
- [ ] Ready for brutal RND validation
- [ ] Can reproduce all results

---

## 📝 **SUBMISSION PROCESS**

### **When Self-Validation Complete:**

Create: `.coordination/handoffs/dev1-to-rnd-SCRAPE-002-v2.1-SUBMISSION.md`

```markdown
# SCRAPE-002 v2.1 Submission

**Developer:** Dev1  
**Date:** [YYYY-MM-DD HH:MM]  
**Status:** Complete - Ready for RND validation

## Scope:
10 specific sales/lead gen workflows (v2.1 update)

## Deliverables:
- [x] All 10 target workflows extracted
- [x] 35+ tests passing (actual: XX)
- [x] 80%+ coverage (actual: XX.X%)
- [x] All 6 evidence files created
- [x] All 10 workflow JSONs in sample folder

## Requirements:
- [x] Extract 10 workflows (10/10 = 100%)
- [x] Success rate ≥90% (actual: 100%)
- [x] Zero failures
- [x] Coverage ≥80% (actual: XX.X%)
- [x] Tests ≥35 passing (actual: XX)
- [x] All required fields in samples
- [x] Rate limiting implemented
- [x] Database storage working

## Evidence Files:
1. SCRAPE-002-test-output.txt (exists, XX lines)
2. SCRAPE-002-coverage-report.txt (exists, XX lines)
3. SCRAPE-002-10-workflow-summary.json (exists, complete)
4. SCRAPE-002-sample-extractions/ (exists, 10 files)
5. SCRAPE-002-database-query.txt (exists, 10 rows)
6. SCRAPE-002-evidence-summary.json (exists, complete)

All verified to exist and accurate.

## Self-Validation:
- [x] All tests run and watched
- [x] Coverage verified
- [x] All 10 workflows in database
- [x] All evidence files created
- [x] Numbers match outputs
- [x] Ready for RND validation

**Ready for review.**
```

---

## 🚨 **WHAT WILL CAUSE INSTANT REJECTION**

❌ **Missing ANY of 10 Workflows**
- Must have ALL 10 specific IDs: 2462, 1954, 2103, 2234, 1756, 1832, 2156, 1923, 2087, 2145
- Even 9/10 with wrong ID = REJECTED

❌ **Sample Folder Has ≠10 Files**
- Must be exactly 10 workflow JSON files
- Less than 10 OR more than 10 = REJECTED

❌ **Numbers Don't Match**
- Test count, coverage %, workflow count must match between files

❌ **Tests < 35 or Any Failing**
- Need 35+ and 100% pass rate

❌ **Coverage < 80%**
- Must meet 80.00% minimum

❌ **Can't Reproduce**
- If my test run differs from yours

---

## ✅ **WHAT WILL CAUSE APPROVAL**

✅ **All 10 Specific Workflows**
- Database query shows all 10 IDs
- Sample folder has all 10 files
- Summary shows 10/10 success

✅ **All Evidence Exists**
- All 6 files/folders present

✅ **Numbers Match**
- Evidence summary = test output = coverage report = database

✅ **Tests Pass**
- 35+ tests, all passing when I run

✅ **Coverage Meets**
- ≥80% when I run

✅ **Reproducible**
- I get same results as you

---

## 📞 **COMMUNICATION**

### **Questions to Ask:**

**Good:**
- "Should extraction script take workflow IDs as parameter or hardcode the 10?"
- "If workflow 2145 returns 404, should I retry or fail gracefully?"
- "Should I clear database before extraction or append?"

**You Already Asked (Answered):**
- ✅ PM's brief location - See Master Orchestrator's message
- ✅ Listing vs detail pages - Detail pages (individual workflows)
- ✅ Real vs mocked tests - Mix (mostly mocked, 3-5 real)
- ✅ How to get IDs - Use the provided list of 10
- ✅ Database state - Append (don't clear)

---

## 🎯 **SUCCESS METRICS**

**Complete when:**
- [ ] All 10 target workflows extracted
- [ ] 90%+ success rate (9/10 or 10/10)
- [ ] 35+ tests, all passing
- [ ] 80%+ coverage
- [ ] All 6 evidence files exist
- [ ] All 10 workflow files in samples folder
- [ ] Numbers match between files
- [ ] Self-validation complete
- [ ] **RND APPROVED**

---

## ⏱️ **TIMELINE**

**Task Issued:** October 10, 2025, 02:10 AM  
**Deadline:** October 11, 2025, 18:00  
**Time Available:** 40 hours  
**Work Needed:** 6-8 hours

**Breakdown:**
- Hours 1-2: Add 1-2 tests, increase coverage 77% → 82%
- Hours 3-5: Extract 10 target workflows
- Hours 6-7: Create evidence files, verify
- Hour 8: Buffer/verification

---

## 💡 **TIPS FOR SUCCESS**

**Do:**
✅ Extract ONLY the 10 specific workflow IDs listed  
✅ Watch tests run live before saving  
✅ Verify ALL 10 in database before claiming  
✅ Create ALL 10 sample JSONs  
✅ Double-check numbers match  

**Don't:**
❌ Extract random workflows (use the 10 specified)  
❌ Claim 10/10 if database shows 9  
❌ Skip any evidence files  
❌ Exaggerate metrics  

---

**This is your official task assignment from RND Manager.**  
**10 specific workflows. 6-8 hours. Sales focus. Clear requirements.**  
**You've got this, Dev1!** 💪

---

**RND Manager**  
**Task Assignment Version:** 2.1 (Updated scope)  
**Status:** Active - Execute immediately  
**Deadline:** October 11, 2025, 18:00 (40 hours)

