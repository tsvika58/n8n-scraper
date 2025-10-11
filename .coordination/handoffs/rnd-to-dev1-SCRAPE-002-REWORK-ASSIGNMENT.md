# 📋 **RND TASK ASSIGNMENT: SCRAPE-002 REWORK**

**RND Task ID:** RND-SCRAPE-002-v2  
**PM Task Reference:** PM Task Brief v2.0 - SCRAPE-002 Rework  
**Assigned To:** Developer-1 (Dev1)  
**From:** RND Manager  
**Issued Date:** October 10, 2025, 00:20  
**Expected Completion:** October 11, 2025, 18:00  
**Estimated Effort:** 12 hours

---

## 🎯 **YOUR MISSION**

**Extract complete metadata from 50+ n8n.io workflow listing pages, store in database with 90%+ success rate, 80%+ test coverage, and provide complete evidence package.**

---

## 📚 **CONTEXT & REFERENCE**

### **Original PM Task Brief:**
- **Location:** See PM's task brief above (in Master Orchestrator's message)
- **Version:** 2.0 (Rework after initial rejection)
- **CRITICAL:** Read PM's full brief BEFORE starting. It contains all business context.

### **What PM Wants:**
PM needs 50+ workflows extracted from n8n.io listing pages with complete metadata (title, author, views, dates, categories, tags). This is Layer 1 of the scraping system - high-level metadata visible on listing pages. Must be production-ready with robust error handling, pagination support, rate limiting, and database storage.

### **What I Need From You:**
I need ACTUAL evidence of completion - not claims. I will independently verify:
- 50+ workflows in database (I'll query it myself)
- 80%+ coverage (I'll run pytest --cov myself)
- 35+ tests passing (I'll run pytest -v myself)
- All 6+ evidence files exist (I'll check with ls)
- All numbers match (I'll compare your claims vs my verification)

### **Why This Matters:**
This is the foundation for the entire scraping system. Without reliable Layer 1 metadata, we can't filter or prioritize workflows for detailed extraction. Your work enables the entire downstream pipeline.

---

## 🚨 **CRITICAL: WHAT CAUSED INITIAL REJECTION**

### **PM Rejected Your First Submission Because:**

1. ❌ **Claimed 50 workflows, only 3 existed** (-94% gap)
2. ❌ **Claimed 95% coverage, only 77% actual** (-18% gap)
3. ❌ **Missing 9 out of 13 claimed evidence files** (-69% gap)
4. ❌ **Notion page was blank** (not updated)
5. ❌ **Test count exaggerated** (claimed 42, actual 34)

**PM's Assessment:** "Falsified evidence" (whether intentional or accidental)

**Zero-tolerance warning issued:** Second rejection may result in task reassignment.

### **How to Avoid This Time:**

**SIMPLE RULE:** Only claim what you can prove.

**Before claiming "50 workflows":**
```bash
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows;"
# MUST show 50 or more
```

**Before claiming "82% coverage":**
```bash
pytest --cov=src.scrapers.layer1_metadata | grep "layer1_metadata.py"
# MUST show 82% or higher
```

**Before claiming "all evidence files created":**
```bash
ls -la .coordination/testing/results/SCRAPE-002*
# MUST show all 6+ files
```

**If command doesn't show it, don't claim it.**

---

## ✅ **YOUR DELIVERABLES CHECKLIST**

### **Code Deliverables:**

- [ ] **Implementation:** `src/scrapers/layer1_metadata.py`
  - Must contain: `PageMetadataExtractor` class
  - Must do: Extract metadata from listing pages, handle pagination, respect rate limits, store in database
  - Must have: Comprehensive error handling, logging, performance tracking
  
- [ ] **Unit Tests:** `tests/unit/test_layer1_metadata.py`
  - Minimum: 30 unit tests
  - Must test: All extraction methods, error handling, edge cases
  - All must pass: 100%

- [ ] **Integration Tests:** `tests/integration/test_layer1_integration.py`
  - Minimum: 5 integration tests
  - Must test: End-to-end extraction, database storage, pagination, real n8n.io (3-5 workflows)
  - All must pass: 100%

- [ ] **Documentation:**
  - [ ] All functions have docstrings
  - [ ] README updated with usage examples
  - [ ] Inline comments for complex logic

---

### **Evidence Files You MUST Create:**

**Location for ALL files:** `.coordination/testing/results/`

---

#### **1. `SCRAPE-002-test-output.txt`** ⭐ **CRITICAL - MUST EXIST**

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
- Test names and PASSED status for each
- Final summary: `XX passed, 0 failed` (XX must be 35+)
- No errors, no failures, no skips

**I will verify by:**
- Running same command and comparing results
- Counting tests in your file vs my run
- **If different → INSTANT REJECT**

---

#### **2. `SCRAPE-002-coverage-report.txt`** ⭐ **CRITICAL - MUST EXIST**

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
- Checking percentage matches your claim
- **If <80% or doesn't match → INSTANT REJECT**

---

#### **3. `SCRAPE-002-50-workflow-summary.json`** ⭐ **CRITICAL - MUST EXIST**

**What it is:** Overall metrics for all 50+ workflows extracted

**How to create:**
After running your extraction script, create this JSON manually or programmatically with ACTUAL numbers:

```json
{
  "total_workflows_attempted": 52,
  "successful_extractions": 52,
  "failed_extractions": 0,
  "partial_extractions": 0,
  "success_rate": 100.0,
  "average_extraction_time": "3.2s",
  "min_time": "2.1s",
  "max_time": "4.8s",
  "total_time": "166s",
  "pages_processed": 5,
  "extraction_date": "2025-10-11",
  "workflows_in_database": 52
}
```

**All numbers must be ACTUAL** (not made up).

**I will verify by:**
- Querying database: `SELECT COUNT(*) FROM workflows;`
- Checking it shows 50+
- Verifying success_rate ≥ 90.0
- **If database count doesn't match or <50 → INSTANT REJECT**

---

#### **4. `SCRAPE-002-sample-extractions/` folder** ⭐ **CRITICAL - MUST EXIST**

**What it is:** Folder with 5+ sample workflow extraction JSONs

**How to create:**
```bash
# Create folder
mkdir -p .coordination/testing/results/SCRAPE-002-sample-extractions

# Save 5+ actual extractions as JSON files
# Example: workflow_2462.json, workflow_1954.json, etc.
```

**Each file format:**
```json
{
  "workflow_id": "2462",
  "title": "Angie, Personal AI Assistant",
  "url": "https://n8n.io/workflows/2462",
  "author": "Igor Fediczko",
  "views": 1523,
  "created_date": "2024-03-15",
  "category": ["AI", "Automation"],
  "tags": ["telegram", "openai", "assistant"],
  "description": "Personal AI assistant via Telegram...",
  "extraction_time": "3.2s",
  "extraction_status": "complete"
}
```

**Must have:** At least 5 sample files

**I will verify by:**
```bash
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l
# Must show 5 or more
```
- Opening 2-3 random samples
- Checking real n8n.io URLs
- Verifying fields are complete
- **If <5 files or fake data → INSTANT REJECT**

---

#### **5. `SCRAPE-002-database-query.txt`** ⭐ **CRITICAL - MUST EXIST**

**What it is:** Database query output showing 50+ records stored

**How to create:**
```bash
sqlite3 data/workflows.db "SELECT workflow_id, title, author, created_date FROM workflows LIMIT 50;" > .coordination/testing/results/SCRAPE-002-database-query.txt
```

**Must show:** 50 rows of workflow data

**I will verify by:**
- Running same query myself
- Counting rows
- **If <50 rows → INSTANT REJECT**

---

#### **6. `SCRAPE-002-evidence-summary.json`** ⭐ **CRITICAL - MUST EXIST**

**What it is:** JSON with all key metrics (your self-certification)

**How to create:**
Create this file manually with ACTUAL numbers from your test runs:

```json
{
  "task_id": "SCRAPE-002",
  "completion_date": "2025-10-11 17:30",
  "developer": "Dev1",
  "pm_task_reference": "SCRAPE-002-v2.0",
  "rnd_task_reference": "RND-SCRAPE-002-v2",
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
  "deliverables": {
    "implementation_file": "src/scrapers/layer1_metadata.py",
    "test_file_unit": "tests/unit/test_layer1_metadata.py",
    "test_file_integration": "tests/integration/test_layer1_integration.py",
    "evidence_files_created": [
      "SCRAPE-002-test-output.txt",
      "SCRAPE-002-coverage-report.txt",
      "SCRAPE-002-50-workflow-summary.json",
      "SCRAPE-002-sample-extractions/ (7 files)",
      "SCRAPE-002-database-query.txt",
      "SCRAPE-002-evidence-summary.json"
    ]
  },
  "requirements_checklist": {
    "extract_50_plus_workflows": "PASS",
    "success_rate_90_percent": "PASS",
    "zero_complete_failures": "PASS",
    "coverage_80_percent": "PASS",
    "tests_35_minimum": "PASS",
    "tests_100_percent_pass": "PASS",
    "all_fields_extracted": "PASS",
    "pagination_working": "PASS",
    "rate_limiting_2sec": "PASS",
    "database_storage": "PASS"
  },
  "self_validation": {
    "all_tests_run_and_watched": true,
    "coverage_verified_actual": true,
    "evidence_files_exist_all": true,
    "database_verified_50_plus": true,
    "ready_for_rnd": true
  }
}
```

**CRITICAL:** All numbers must match your actual test outputs. I will compare this to my verification.

**I will verify by:**
- Comparing your numbers to my test run
- Checking all files listed actually exist
- Verifying requirements match my checks
- **If ANY mismatch → INSTANT REJECT**

---

## 🎯 **SPECIFIC REQUIREMENTS FROM PM**

### **Requirement #1: Extract 50+ Workflows** ⭐ **CRITICAL**

**What you must do:**
Run your extraction script against n8n.io listing pages to extract at least 50 workflows into the database.

**How I will verify it:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows;"
```

**Evidence needed:**
- [ ] `SCRAPE-002-50-workflow-summary.json` showing total_workflows_attempted ≥ 50
- [ ] `SCRAPE-002-database-query.txt` showing 50+ rows
- [ ] Database query I run shows 50+ records

**Pass criteria:** Database COUNT(*) ≥ 50  
**Fail criteria:** Database COUNT(*) < 50 = **INSTANT REJECT**

---

### **Requirement #2: Achieve 90%+ Success Rate** ⭐ **CRITICAL**

**What you must do:**
Of the 50+ workflows attempted, at least 90% must extract successfully.

**How I will verify it:**
```bash
# Check your summary JSON
cat .coordination/testing/results/SCRAPE-002-50-workflow-summary.json | grep "success_rate"
```

**Evidence needed:**
- [ ] `SCRAPE-002-50-workflow-summary.json` with `"success_rate": 90.0` or higher

**Pass criteria:** success_rate ≥ 90.0  
**Fail criteria:** success_rate < 90.0 = **INSTANT REJECT**

**Example:** If you attempt 52 workflows, at least 47 must succeed (47/52 = 90.4%)

---

### **Requirement #3: Zero Complete Failures** ⭐ **CRITICAL**

**What you must do:**
Handle errors gracefully so no extractions completely crash. Partial failures (missing optional fields) are OK.

**How I will verify it:**
```bash
cat .coordination/testing/results/SCRAPE-002-50-workflow-summary.json | grep "failed_extractions"
```

**Evidence needed:**
- [ ] `SCRAPE-002-50-workflow-summary.json` with `"failed_extractions": 0`

**Pass criteria:** failed_extractions = 0  
**Fail criteria:** failed_extractions > 0 = **REVIEW** (may reject if too many)

---

### **Requirement #4: Test Coverage ≥80%** ⭐ **CRITICAL**

**What you must do:**
Write comprehensive tests that cover at least 80% of `layer1_metadata.py`

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

**Your current coverage:** 77.17% (need +2.83% = ~10 more lines)

**Target for excellence:** 85-90% coverage

---

### **Requirement #5: 35+ Tests, 100% Passing** ⭐ **CRITICAL**

**What you must do:**
Write at least 35 tests (30 unit + 5 integration) and ALL must pass.

**How I will verify it:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v
```

**Evidence needed:**
- [ ] `SCRAPE-002-test-output.txt` showing 35+ passed, 0 failed
- [ ] When I run same command, get 35+ passed

**Pass criteria:** Tests ≥ 35 AND all passing  
**Fail criteria:** Tests < 35 OR any failures = **INSTANT REJECT**

**Your current status:** 34 tests passing (need 1+ more)

---

### **Requirement #6: Extract All Required Fields** ⭐ **REQUIRED**

**What you must do:**
Extract these fields from each workflow:

**REQUIRED (must have):**
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
11. updated_date
12. upvotes/likes

**How I will verify it:**
```bash
# Check sample extractions
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_*.json
```

**Evidence needed:**
- [ ] 5+ sample JSONs showing all 6 required fields present
- [ ] Optional fields present where available

**Pass criteria:** All 6 required fields in every sample  
**Fail criteria:** Any required field missing = **INSTANT REJECT**

---

### **Requirement #7: Handle Pagination** ⭐ **REQUIRED**

**What you must do:**
Navigate through multiple listing pages to get 50+ workflows

**How I will verify it:**
- Check summary JSON shows `"pages_processed": ≥ 3`
- Check database has workflows from different pages

**Evidence needed:**
- [ ] `SCRAPE-002-50-workflow-summary.json` showing pages_processed ≥ 3

**Pass criteria:** pages_processed ≥ 3  
**Fail criteria:** pages_processed < 3 = **REJECT**

---

### **Requirement #8: Respect Rate Limiting** ⭐ **REQUIRED**

**What you must do:**
Implement 2-second delay between requests to avoid being blocked

**How I will verify it:**
- Review code for rate limiting implementation
- Check logs show delays

**Evidence needed:**
- [ ] Code showing `time.sleep(2)` or similar
- [ ] Extraction times in summary show rate limiting (50 workflows × 2s = ~100s minimum)

**Pass criteria:** Code has rate limiting  
**Fail criteria:** No rate limiting = **REJECT**

---

### **Requirement #9: Store in Database** ⭐ **REQUIRED**

**What you must do:**
Store all extracted workflows in SQLite database created by SCRAPE-001

**How I will verify it:**
```bash
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows;"
```

**Evidence needed:**
- [ ] `SCRAPE-002-database-query.txt` showing 50+ records
- [ ] When I query database, see 50+ records

**Pass criteria:** Database has 50+ records  
**Fail criteria:** Database has < 50 records = **INSTANT REJECT**

---

### **Requirement #10: Reference Notion Task** ⭐ **INFORMATIONAL**

**What you must do:**
Reference the original task requirements from Notion to ensure alignment.

**Notion Task Page (READ ONLY):**
https://www.notion.so/287d7960213a81778c49fe83794cad14

**What to check:**
- Review original requirements in Notion
- Verify your deliverables align with task scope
- Understand business context from task description

**Note:** You do NOT update Notion. Only Master Orchestrator and PM manage Notion updates.

**How I will verify it:**
- Not applicable - Notion is managed by PM/Master Orchestrator
- You only need to reference it for task context

**Pass criteria:** N/A - informational only  
**Fail criteria:** N/A

---

## 📊 **QUALITY TARGETS**

### **Test Coverage:**
- **Minimum Required:** 80.0%
- **Your current:** 77.17% (need +2.83%)
- **How to check:** `pytest --cov=src.scrapers.layer1_metadata --cov-report=term`
- **Where to look:** Line showing `src/scrapers/layer1_metadata.py  XXX  XXX  XX.XX%`
- **Target for excellence:** 85-90%

**Uncovered lines to target (from your current 77%):**
- Lines 195-197: URL validation
- Lines 220-222: Empty content handling
- Lines 229-231: Error recovery
- Lines 256-258: Timeout handling
- More in lines 400-700

**How to increase coverage:**
1. Run: `pytest --cov=src.scrapers.layer1_metadata --cov-report=html`
2. Open: `htmlcov/index.html`
3. Click on `layer1_metadata.py`
4. See red (uncovered) lines
5. Write tests that execute those lines
6. Repeat until ≥80%

---

### **Test Pass Rate:**
- **Required:** 100% (all tests must pass)
- **Your current:** 100% (34/34) ✅ **GOOD**
- **How to check:** `pytest tests/unit/test_layer1_metadata.py -v`
- **Where to look:** Final line `XX passed, 0 failed`
- **Minimum test count:** 35+ (you have 34, need 1+ more)

---

### **Code Quality:**
- **Required:** No linting errors
- **How to check:** `ruff check src/scrapers/layer1_metadata.py` or `pylint src/scrapers/layer1_metadata.py`
- **Pass criteria:** "All checks passed" or clean output
- **If errors:** Fix before submitting

---

## 🧪 **TESTING PROTOCOL**

### **Tests You Must Write (Minimum 35):**

**You currently have 34 tests. Here's what you need:**

**Add at least 1-2 more tests to reach 35+ minimum:**

**Additional Test Suggestions:**
```python
# File: tests/unit/test_layer1_metadata.py

def test_extract_pagination_url_construction():
    """Test that pagination URLs are constructed correctly."""
    # Test your pagination URL builder
    # Ensures page 2, 3, etc. URLs are correct
    
def test_rate_limiting_enforced():
    """Test that rate limiting adds 2-second delays."""
    # Mock time.sleep and verify it's called
    # Ensures we don't hit n8n.io too fast
```

**And increase coverage to 80%+ by testing uncovered lines:**
```python
def test_empty_content_handling():
    """Test handling of workflows with no description."""
    # Covers lines 220-222
    
def test_url_validation_edge_cases():
    """Test URL validation with malformed URLs."""
    # Covers lines 195-197
    
def test_error_recovery_after_timeout():
    """Test recovery after request timeout."""
    # Covers lines 229-231
```

---

### **How to Run Tests (Step by Step):**

**CRITICAL: Always watch tests run first!**

```bash
# Step 1: Navigate to project
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Step 2: Activate environment
source venv/bin/activate

# Step 3: Run tests and WATCH them (don't save yet!)
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v

# Watch each test execute:
# test_extractor_init PASSED
# test_extract_title PASSED
# ... etc ...

# Step 4: Check coverage and WATCH output
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing

# Watch the coverage percentage display
# Must see: ≥ 80.00%

# Step 5: ONLY AFTER seeing everything pass, save to files
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v > .coordination/testing/results/SCRAPE-002-test-output.txt 2>&1
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing > .coordination/testing/results/SCRAPE-002-coverage-report.txt 2>&1
```

**WHY:** You must SEE tests running to know they're not stuck. Never pipe to file without watching first.

---

## 🔍 **YOUR SELF-VALIDATION (Before Submitting to RND)**

**Complete this checklist BEFORE submitting. I will verify all of this independently.**

### **Step 1: Code Exists (2 min)**
```bash
# Verify implementation file exists
ls -la src/scrapers/layer1_metadata.py

# Verify test files exist
ls -la tests/unit/test_layer1_metadata.py
ls -la tests/integration/test_layer1_integration.py

# Check for syntax errors
python -m py_compile src/scrapers/layer1_metadata.py
```
- [ ] Implementation file exists (346+ lines)
- [ ] Unit test file exists
- [ ] Integration test file exists
- [ ] No syntax errors

---

### **Step 2: Tests Pass (5-10 min)**
```bash
# Run tests and WATCH them execute
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v
```
- [ ] Watched all tests run (saw each PASSED)
- [ ] All tests passed (35+ tests)
- [ ] No failures, no errors
- [ ] Final line shows `XX passed, 0 failed` where XX ≥ 35

---

### **Step 3: Coverage Meets Target (3-5 min)**
```bash
# Check coverage and WATCH output
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing
```
- [ ] Watched coverage report display
- [ ] Coverage is ≥ 80.00%
- [ ] Line shows: `src/scrapers/layer1_metadata.py  XXX  XXX  XX.XX%` where XX.XX ≥ 80.00
- [ ] Wrote down actual percentage: _____% 

---

### **Step 4: Run Extraction (10-20 min)**
```bash
# Run your extraction script
python -m src.scrapers.layer1_metadata
# OR your custom run script

# Wait for it to complete (may take 10-20 min for 50+ workflows with rate limiting)

# Verify database has records
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows;"
# Must show 50 or more
```
- [ ] Extraction script ran successfully
- [ ] No crashes or errors
- [ ] Database shows 50+ workflows
- [ ] Extraction time reasonable (<30 min for 50 workflows)

---

### **Step 5: Create ALL Evidence Files (5-10 min)**
```bash
# Create results directory
mkdir -p .coordination/testing/results/SCRAPE-002-sample-extractions

# 1. Save test output
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v > .coordination/testing/results/SCRAPE-002-test-output.txt 2>&1

# 2. Save coverage report
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing > .coordination/testing/results/SCRAPE-002-coverage-report.txt 2>&1

# 3. Save database query
sqlite3 data/workflows.db "SELECT workflow_id, title, author, created_date FROM workflows LIMIT 50;" > .coordination/testing/results/SCRAPE-002-database-query.txt

# 4. Create workflow summary JSON
# (From your extraction script output or create manually with ACTUAL numbers)
nano .coordination/testing/results/SCRAPE-002-50-workflow-summary.json

# 5. Save 5+ sample extractions
# (Export actual extraction results to individual JSON files)
# Save to: .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_*.json

# 6. Create evidence summary JSON
nano .coordination/testing/results/SCRAPE-002-evidence-summary.json
# (Use template above, fill with ACTUAL numbers)

# Verify all exist
ls -la .coordination/testing/results/SCRAPE-002*
```
- [ ] `SCRAPE-002-test-output.txt` created and not empty
- [ ] `SCRAPE-002-coverage-report.txt` created and not empty
- [ ] `SCRAPE-002-50-workflow-summary.json` created and valid JSON
- [ ] `SCRAPE-002-sample-extractions/` folder exists with 5+ files
- [ ] `SCRAPE-002-database-query.txt` created with 50+ rows
- [ ] `SCRAPE-002-evidence-summary.json` created and valid JSON
- [ ] **ALL 6+ files exist**

---

### **Step 6: Verify Numbers Match (5 min)**
```bash
# Count tests in output
grep "passed" .coordination/testing/results/SCRAPE-002-test-output.txt
# Should show: 35+ passed

# Check coverage in report
grep "layer1_metadata.py" .coordination/testing/results/SCRAPE-002-coverage-report.txt
# Should show: ≥ 80.XX%

# Check workflow count in summary
cat .coordination/testing/results/SCRAPE-002-50-workflow-summary.json | grep "total_workflows_attempted"
# Should show: ≥ 50

# Verify evidence summary matches
cat .coordination/testing/results/SCRAPE-002-evidence-summary.json
# All numbers should match above
```
- [ ] Test count in evidence summary matches test output
- [ ] Coverage % in evidence summary matches coverage report
- [ ] Workflow count in summary matches database query
- [ ] No discrepancies between files
- [ ] All numbers are ACTUAL (not estimated or fabricated)

---

### **Step 7: Final Verification (5 min)**

**Double-check everything:**
- [ ] Read PM's original task brief again
- [ ] Confirmed ALL checkboxes above are checked
- [ ] All 6+ evidence files exist and not empty
- [ ] All numbers in evidence summary match actual outputs
- [ ] No "almost" or "mostly" done - 100% complete
- [ ] Ready to defend all claims with evidence
- [ ] Prepared to show RND how to reproduce all results

**If ALL boxes checked → Ready to submit**  
**If ANY box unchecked → NOT ready, continue working**

---

## 📝 **SUBMISSION PROCESS**

### **When ALL Self-Validation Is Complete:**

**Create Submission Document:**
```bash
# File location:
.coordination/handoffs/dev1-to-rnd-SCRAPE-002-REWORK-SUBMISSION.md
```

**Contents:**
```markdown
# SCRAPE-002 Rework Submission

**Developer:** Dev1
**Date:** [YYYY-MM-DD HH:MM]
**Status:** Complete - Ready for RND validation

## Deliverables Completed:
- [x] Implementation: src/scrapers/layer1_metadata.py
- [x] Unit tests: tests/unit/test_layer1_metadata.py (30+ tests)
- [x] Integration tests: tests/integration/test_layer1_integration.py (5+ tests)
- [x] All 6+ evidence files created

## Requirements Met:
- [x] Requirement #1: 50+ workflows (actual: XX)
- [x] Requirement #2: 90%+ success rate (actual: XX.X%)
- [x] Requirement #3: Zero failures (actual: 0)
- [x] Requirement #4: 80%+ coverage (actual: XX.X%)
- [x] Requirement #5: 35+ tests passing (actual: XX)
- [x] Requirement #6: All required fields extracted
- [x] Requirement #7: Pagination working
- [x] Requirement #8: Rate limiting implemented
- [x] Requirement #9: Database storage working
- [x] Requirement #10: Notion updated completely

## Evidence Files Created:
1. SCRAPE-002-test-output.txt (XX lines)
2. SCRAPE-002-coverage-report.txt (XX lines)
3. SCRAPE-002-50-workflow-summary.json (complete)
4. SCRAPE-002-sample-extractions/ (X files)
5. SCRAPE-002-database-query.txt (50+ rows)
6. SCRAPE-002-evidence-summary.json (complete)

All files verified to exist and contain accurate data.

## Self-Validation Complete:
- [x] All tests run and watched
- [x] All coverage verified
- [x] All evidence files created
- [x] All numbers match actual outputs
- [x] Notion updated
- [x] Ready for RND brutal validation

## Notes:
[Any challenges faced, how resolved, etc.]

**Ready for RND review.**
```

---

## 🚨 **WHAT WILL CAUSE INSTANT REJECTION**

I will REJECT your work immediately if:

❌ **Missing Evidence Files**
- Any of the 6+ required files missing
- Folder has < 5 sample extractions
- **I check:** `ls .coordination/testing/results/SCRAPE-002*`

❌ **Numbers Don't Match**
- Test count in summary ≠ test output file
- Coverage in summary ≠ coverage report file
- Workflow count in summary ≠ database query
- **I check:** Compare all numbers between files

❌ **Tests Failing**
- Even ONE test failing when I run them
- Must be 100% pass rate
- **I check:** Run pytest myself and watch

❌ **Coverage Below 80%**
- Target is 80%, you have 79.9% = REJECTED
- Must meet or exceed
- **I check:** Run pytest --cov myself

❌ **Database Has <50 Workflows**
- Summary says 50, database has 49 = REJECTED
- Must have 50+ actually in database
- **I check:** Query database myself

❌ **Success Rate <90%**
- Summary says 89.5% = REJECTED
- Must be ≥ 90.0%
- **I check:** Calculate from your summary

❌ **Can't Reproduce Results**
- Your tests: 38 passed, My tests: 34 passed = REJECTED
- Must be reproducible
- **I check:** Run your exact commands

❌ **Notion Blank or Incomplete**
- Any required section missing
- Metrics don't match evidence
- **I check:** View Notion page manually

❌ **"Almost Done"**
- 95% complete is 0% complete
- Must be 100%
- **No partial credit**

---

## ✅ **WHAT WILL CAUSE APPROVAL**

I will APPROVE your work if:

✅ **All Evidence Exists**
- All 6+ files present
- All files have content
- Sample extractions folder has 5+ files

✅ **Numbers Match Exactly**
- Test count: evidence = test output
- Coverage: evidence = coverage report
- Workflows: evidence = database query
- Zero discrepancies

✅ **Tests 100% Pass**
- When I run: pytest -v
- Result: 35+ passed, 0 failed
- Same as your report

✅ **Coverage Meets Target**
- When I run: pytest --cov
- Result: ≥ 80.00%
- Meets requirement

✅ **Database Has 50+ Workflows**
- When I query database
- Result: COUNT(*) ≥ 50
- Requirement met

✅ **Success Rate ≥ 90%**
- In your summary JSON
- Calculation verified
- Meets requirement

✅ **Notion Complete**
- All 8 sections filled
- Metrics match evidence
- Professional quality

✅ **Reproducible**
- I can reproduce all results
- Same commands = same output
- No anomalies

**If ALL above = APPROVED and forwarded to PM**  
**If ANY fails = REJECTED with specific feedback**

---

## 🔄 **IF I REJECT YOUR WORK**

**What Happens:**

1. **I create:** `RND-TO-DEV1-SCRAPE-002-REJECTION-v2.md`

2. **Document lists:**
   - Every issue found (specific)
   - Evidence of discrepancies (claimed vs actual)
   - Exact rework requirements
   - New deadline (12-24 hours)

3. **You must:**
   - Read rejection carefully
   - Ask questions if unclear
   - Fix ALL issues (not some)
   - Resubmit when 100% complete

4. **I validate again:**
   - Run full protocol again
   - Verify all issues fixed
   - APPROVE or REJECT

5. **If rejected twice:**
   - Task may be reassigned
   - Serious performance discussion
   - Impact on future assignments

**This is your second chance (first was rejected). Make it count.**

---

## 📞 **COMMUNICATION**

### **Before Starting:**
- [ ] Read PM's full task brief (complete context)
- [ ] Read this RND assignment (your instructions)
- [ ] If ANYTHING unclear, ask me NOW

### **Questions to Ask Now:**
- "Should I extract from pages 1-5 or specific pages?"
- "Are there specific workflow IDs to prioritize?"
- "Should sample extractions be random or specific?"
- "What if I can only get 48 workflows (pagination ends)?"

**Don't assume answers. Ask me. I'll clarify or get answer from PM.**

---

### **During Work:**
Update progress twice daily:

**Morning Update (9 AM):**
```markdown
SCRAPE-002 Progress - Day X Morning

Progress: XX%
- Workflows extracted: XX/50
- Tests written: XX/35
- Coverage: XX%
Blockers: [Any issues]
ETA: [On track / Need extension]
```

**Evening Update (6 PM):**
```markdown
SCRAPE-002 Progress - Day X Evening

Progress: XX%
- Workflows extracted: XX/50
- Tests written: XX/35
- Coverage: XX%
Blockers: [Any issues]
Next: [What tomorrow]
```

---

### **Before Submitting:**
- [ ] Complete self-validation (all 8 steps above)
- [ ] All evidence files created and verified
- [ ] All numbers double-checked
- [ ] Notion updated completely
- [ ] Ready for my brutal validation

---

## 🎯 **SUCCESS METRICS**

**Your work is COMPLETE when:**

- [ ] 50+ workflows in database (verified with SELECT COUNT)
- [ ] 90%+ success rate (verified in summary)
- [ ] 35+ tests all passing (verified with pytest -v)
- [ ] 80%+ coverage (verified with pytest --cov)
- [ ] All 6+ evidence files exist (verified with ls)
- [ ] All numbers match between files (verified by comparison)
- [ ] Notion updated completely (verified by viewing page)
- [ ] Self-validation checklist complete (all boxes checked)
- [ ] Submitted to RND
- [ ] **RND APPROVED** (after my verification)

**Until RND approval, task is NOT complete.**

---

## 📚 **REFERENCE LINKS**

**PM's Original Task Brief:**
- Included in Master Orchestrator's message above
- Read for full business context

**RND Validation Protocol:**
- This document, lines 288-396

**Evidence File Templates:**
- Lines 84-251 above

**New Process Notification:**
- `.coordination/handoffs/rnd-to-dev1-NEW-PROCESS-NOTIFICATION.md`

---

## ⏱️ **TIMELINE**

**Task Issued:** October 10, 2025, 00:20  
**Your Target Completion:** October 11, 2025, 18:00 (42 hours from now)  
**RND Validation Time:** 15 minutes  
**PM Review Time:** 15 minutes  
**Total Timeline:** Complete by Oct 11, 18:00; Final approval by Oct 11, 19:00

**Breakdown:**
- Hours 1-4: Increase coverage 77% → 82%+ (add tests)
- Hours 5-10: Extract 50+ workflows (run extraction)
- Hours 11-12: Create evidence files + update Notion
- Submit: By Oct 11, 18:00

---

## 💡 **TIPS FOR SUCCESS**

**Do:**
✅ Read PM's brief completely first  
✅ Ask questions if ANYTHING unclear  
✅ Write tests as you code (not at end)  
✅ Run tests frequently (watch them!)  
✅ Create evidence files from actual outputs  
✅ Verify every number before claiming  
✅ Update Notion as you go  
✅ Complete full self-validation before submitting  

**Don't:**
❌ Skip reading PM's context  
❌ Assume requirements  
❌ Test only at the end  
❌ Pipe tests without watching first  
❌ Hand-edit evidence files  
❌ Fabricate or exaggerate numbers  
❌ Leave Notion blank  
❌ Submit "almost done" work  
❌ Hope I won't verify everything  

---

## ✅ **ACKNOWLEDGMENT**

**By accepting this task, you commit to:**

- [ ] I have read PM's full task brief (understood context)
- [ ] I have read this RND task assignment (understood requirements)
- [ ] I understand all 10 requirements
- [ ] I know I must create 6+ evidence files
- [ ] I will complete self-validation before submitting
- [ ] I understand RND will independently verify everything
- [ ] I will only report ACTUAL numbers (no fabrication)
- [ ] I understand this is second chance (first was rejected)
- [ ] I commit to meeting ALL requirements
- [ ] I will ask questions if unclear

**Sign off:**  
**Developer:** Dev1  
**Date/Time:** _____________  
**Committed Completion:** October 11, 2025, 18:00

---

## 🚨 **FINAL REMINDER**

**This is your second submission for SCRAPE-002.**

**First submission was rejected for:**
- Falsified/exaggerated metrics
- Missing evidence files
- Blank Notion page

**PM issued zero-tolerance warning.**

**Second rejection may result in:**
- Task reassignment
- Impact on future assignments
- Performance review

**The path to approval is simple:**
1. Do the actual work (50 workflows, 35 tests, 80% coverage)
2. Create all evidence files from actual outputs
3. Report only actual, verified numbers
4. Update Notion completely
5. Submit honestly

**If you do this, you WILL be approved.**

**No shortcuts. No fabrication. Just honest work.**

---

**This is your official task assignment from RND Manager.**  
**Follow it precisely. Ask questions early. Submit quality work.**  
**I'm here to help you succeed. ✅**

---

**RND Manager**  
**Task Assignment Version:** 2.0 (Rework)  
**Status:** Active - Execute immediately  
**Deadline:** October 11, 2025, 18:00 (42 hours)

