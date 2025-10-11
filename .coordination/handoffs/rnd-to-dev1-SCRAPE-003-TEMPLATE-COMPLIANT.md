# 📋 TASK BRIEF TEMPLATE v1.0

**For:** All Developers & RND Manager  
**Purpose:** Crystal-clear task requirements with zero ambiguity  
**Goal:** First-time approval without rejections or rework

---

## 📝 TASK INFORMATION

**Task ID:** SCRAPE-003  
**Task Name:** Layer 2 Workflow JSON Extractor  
**Assignee:** Developer-1 (Dev1)  
**Estimated Time:** 4 hours  
**Priority:** Critical  
**Dependencies:** SCRAPE-001 (Complete), SCRAPE-002 (Complete), SCRAPE-002B (Complete)  
**Deadline:** October 11, 2025, 14:00

---

## 🎯 OBJECTIVE (WHAT TO BUILD)

### **Primary Goal:**
Extract complete workflow JSON data from n8n.io workflows using the official JSON download feature and store in database for analysis.

### **Detailed Description:**
Build a JSON extractor that navigates to individual n8n.io workflow pages and uses the official "Download as JSON" feature to extract complete workflow structure data. The extractor must handle 20-30 workflows for validation, store all data in a dedicated database table, and provide comprehensive evidence of successful extraction. This is Layer 2 of the three-layer scraping system, focusing on workflow structure (nodes, connections, settings) rather than metadata or content.

The extractor must be robust, handle errors gracefully, implement proper rate limiting, achieve high test coverage, and provide complete evidence package. This validation phase proves the extractor works before scaling to the full 6,022 workflow inventory.

### **User Story:**
As a workflow analyst, I want complete JSON structure data from n8n.io workflows so that I can understand how workflows are built, analyze patterns, and enable automated workflow analysis.

### **Business Value:**
Provides the foundation for workflow analysis and pattern recognition. Without complete JSON structure data, we cannot understand how workflows are constructed, identify common patterns, or enable advanced workflow analysis features. This data is essential for the project's goal of comprehensive n8n.io workflow understanding.

---

## ✅ ACCEPTANCE CRITERIA (EXACT REQUIREMENTS)

### **Functional Requirements:**
1. [ ] **Extract JSON for 20-30 workflows:** Use official "Download as JSON" feature to extract complete workflow structure
   - **How to verify:** `sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflow_json;"`
   - **Evidence required:** `SCRAPE-003-extraction-summary.json` showing total ≥20

2. [ ] **Achieve ≥90% success rate:** Of all workflows attempted, at least 90% must extract successfully
   - **How to verify:** Check success_rate in extraction summary JSON
   - **Evidence required:** `SCRAPE-003-extraction-summary.json` with success_rate ≥90.0

3. [ ] **Store complete workflow data:** All nodes with full parameters, all connections mapped, all settings captured
   - **How to verify:** Review sample JSON files for completeness
   - **Evidence required:** `SCRAPE-003-sample-jsons/` folder with 5-10 complete JSONs

4. [ ] **Database integration:** Store in `workflow_json` table linked to inventory via workflow_id
   - **How to verify:** `sqlite3 data/workflows.db "SELECT workflow_id, node_count FROM workflow_json LIMIT 10;"`
   - **Evidence required:** `SCRAPE-003-database-export.txt` showing stored records

5. [ ] **Use official JSON download:** Navigate to workflow page and use n8n.io's "Download as JSON" feature
   - **How to verify:** Code review showing official download method implementation
   - **Evidence required:** Code implementation using official download

6. [ ] **Quality validation:** Verify JSON structure is valid and data is complete
   - **How to verify:** Review sample JSONs for valid structure and completeness
   - **Evidence required:** Sample JSONs showing valid, complete workflow structure

### **Quality Requirements:**
- [ ] **Test Coverage:** ≥80% (minimum acceptable)
  - **How to measure:** `pytest tests/unit/test_layer2_json.py --cov=src.scrapers.layer2_json --cov-report=term`
  - **Evidence:** `SCRAPE-003-coverage-report.txt`
  
- [ ] **Tests Passing:** 100% (all tests must pass)
  - **How to verify:** `pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py -v`
  - **Evidence:** `SCRAPE-003-test-output.txt`
  
- [ ] **Code Quality:** No linting errors
  - **How to verify:** `ruff check src/scrapers/layer2_json.py`
  - **Evidence:** Linting output or "no issues" confirmation
  
- [ ] **Documentation:** All functions documented
  - **How to verify:** Manual review of docstrings
  - **Evidence:** Code review notes

### **Performance Requirements:**
- [ ] **Average extraction time:** <10s per workflow (including rate limiting)
  - **How to measure:** Calculate from extraction summary timing data
  - **Evidence:** `SCRAPE-003-extraction-summary.json` with timing metrics

---

## 📊 DELIVERABLES CHECKLIST

### **Code Deliverables:**
- [ ] **Implementation file(s):** `src/scrapers/layer2_json.py`
- [ ] **Test file(s):** `tests/unit/test_layer2_json.py`, `tests/integration/test_layer2_integration.py`
- [ ] **Database schema:** `src/database/json_schema.py`
- [ ] **Documentation:** README updates, docstrings, etc.

### **Evidence Deliverables:**
Developer MUST create these EXACT files:

1. [ ] **`SCRAPE-003-test-output.txt`**
   - **Contents:** Complete pytest output showing all tests passing
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py -v > .coordination/testing/results/SCRAPE-003-test-output.txt 2>&1`

2. [ ] **`SCRAPE-003-coverage-report.txt`**
   - **Contents:** Complete coverage report showing ≥80%
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest tests/unit/test_layer2_json.py --cov=src.scrapers.layer2_json --cov-report=term > .coordination/testing/results/SCRAPE-003-coverage-report.txt 2>&1`

3. [ ] **`SCRAPE-003-sample-jsons/`** (folder)
   - **Contents:** 5-10 sample workflow JSONs showing complete structure
   - **Location:** `.coordination/testing/results/SCRAPE-003-sample-jsons/`
   - **How to create:** Save 5-10 extracted JSON files to this folder

4. [ ] **`SCRAPE-003-database-export.txt`**
   - **Contents:** Database query showing stored workflow JSONs
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `sqlite3 data/workflows.db "SELECT workflow_id, node_count, extraction_date FROM workflow_json ORDER BY workflow_id LIMIT 20;" > .coordination/testing/results/SCRAPE-003-database-export.txt`

5. [ ] **`SCRAPE-003-evidence-summary.json`**
   - **Contents:** JSON with all key metrics and requirements status
   - **Location:** `.coordination/testing/results/`
   - **Format:** See template below

### **Evidence Summary Template:**
```json
{
  "task_id": "SCRAPE-003",
  "completion_date": "2025-10-11",
  "developer": "Dev1",
  "metrics": {
    "workflows_attempted": 25,
    "workflows_successful": 24,
    "success_rate": 96.0,
    "average_extraction_time": "8.5s",
    "total_time": "3h 15m"
  },
  "requirements": {
    "workflows_20_plus": "PASS",
    "success_rate_90_percent": "PASS",
    "official_json_download": "PASS",
    "database_integration": "PASS",
    "quality_validation": "PASS",
    "test_coverage_80_percent": "PASS",
    "tests_100_percent_pass": "PASS",
    "code_quality": "PASS",
    "documentation": "PASS",
    "performance_10s": "PASS"
  },
  "test_results": {
    "total_tests": 25,
    "passing": 25,
    "failing": 0,
    "coverage_percent": 82.5
  },
  "evidence_files": [
    "SCRAPE-003-test-output.txt",
    "SCRAPE-003-coverage-report.txt",
    "SCRAPE-003-sample-jsons/ (5 files)",
    "SCRAPE-003-database-export.txt",
    "SCRAPE-003-evidence-summary.json"
  ]
}
```

---

## 🧪 TESTING REQUIREMENTS

### **Unit Tests Required:**
1. **Test: JSON extractor initialization**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_extractor_init()`
   - **Validates:** Extractor initializes correctly with proper configuration
   - **Must pass:** YES

2. **Test: Official JSON download method**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_official_json_download()`
   - **Validates:** Can successfully download JSON using official method
   - **Must pass:** YES

3. **Test: JSON structure validation**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_json_structure_validation()`
   - **Validates:** Extracted JSON has required structure (nodes, connections, settings)
   - **Must pass:** YES

4. **Test: Database storage**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_database_storage()`
   - **Validates:** JSON data is properly stored in workflow_json table
   - **Must pass:** YES

5. **Test: Error handling for invalid workflows**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_error_handling_invalid_workflow()`
   - **Validates:** Gracefully handles workflows without JSON download
   - **Must pass:** YES

6. **Test: Rate limiting implementation**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_rate_limiting()`
   - **Validates:** 2-second delays are implemented between extractions
   - **Must pass:** YES

7. **Test: JSON parsing and validation**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_json_parsing()`
   - **Validates:** Extracted JSON can be parsed and validated
   - **Must pass:** YES

8. **Test: Node count extraction**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_node_count_extraction()`
   - **Validates:** Correctly counts nodes in workflow JSON
   - **Must pass:** YES

9. **Test: Workflow ID validation**
   - **File:** `tests/unit/test_layer2_json.py`
   - **Function:** `test_workflow_id_validation()`
   - **Validates:** Workflow ID is properly extracted and validated
   - **Must pass:** YES

10. **Test: Database schema creation**
    - **File:** `tests/unit/test_layer2_json.py`
    - **Function:** `test_database_schema()`
    - **Validates:** workflow_json table is created with correct schema
    - **Must pass:** YES

[Add 10+ more unit tests covering all functions]

### **Integration Tests Required:**
1. **Test: End-to-end single workflow extraction**
   - **File:** `tests/integration/test_layer2_integration.py`
   - **Function:** `test_single_workflow_extraction()`
   - **Validates:** Complete extraction process works for one workflow
   - **Must pass:** YES

2. **Test: Multiple workflow extraction**
   - **File:** `tests/integration/test_layer2_integration.py`
   - **Function:** `test_multiple_workflow_extraction()`
   - **Validates:** Can extract multiple workflows in sequence
   - **Must pass:** YES

3. **Test: Database integration**
   - **File:** `tests/integration/test_layer2_integration.py`
   - **Function:** `test_database_integration()`
   - **Validates:** All extracted data is properly stored in database
   - **Must pass:** YES

4. **Test: Real workflow extraction (3-5 workflows)**
   - **File:** `tests/integration/test_layer2_integration.py`
   - **Function:** `test_real_workflow_extraction()`
   - **Validates:** Works with real n8n.io workflows
   - **Must pass:** YES

5. **Test: Error recovery and retry logic**
   - **File:** `tests/integration/test_layer2_integration.py`
   - **Function:** `test_error_recovery()`
   - **Validates:** Handles errors gracefully and continues processing
   - **Must pass:** YES

### **Test Coverage Targets:**
- **Minimum overall:** 80%
- **Per-file minimum:** 80% for layer2_json.py
- **Critical paths:** 100% (main extraction logic)

### **How to Run All Tests:**
```bash
# 1. Activate environment
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate

# 2. Run all tests with coverage
pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py --cov=src.scrapers.layer2_json --cov-report=term-missing -v

# 3. Verify all pass
# Expected: 25+ passed, 0 failed

# 4. Save output
pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py -v > .coordination/testing/results/SCRAPE-003-test-output.txt 2>&1
```

---

## 🔍 VALIDATION PROTOCOL

### **Developer Self-Validation (Before Submission):**

**Step 1: Verify All Code Exists**
```bash
# Check implementation files exist
ls -la src/scrapers/layer2_json.py
ls -la tests/unit/test_layer2_json.py
ls -la tests/integration/test_layer2_integration.py

# Verify no syntax errors
python -m py_compile src/scrapers/layer2_json.py
```

**Step 2: Run Full Test Suite**
```bash
# Must show 100% passing
pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py -v

# Must meet coverage requirement
pytest tests/unit/test_layer2_json.py --cov=src.scrapers.layer2_json --cov-report=term
```

**Step 3: Generate Evidence Files**
```bash
# Create all required evidence files
pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py -v > .coordination/testing/results/SCRAPE-003-test-output.txt 2>&1
pytest tests/unit/test_layer2_json.py --cov=src.scrapers.layer2_json --cov-report=term > .coordination/testing/results/SCRAPE-003-coverage-report.txt 2>&1
mkdir -p .coordination/testing/results/SCRAPE-003-sample-jsons
# [Save 5-10 sample JSONs to sample-jsons folder]
sqlite3 data/workflows.db "SELECT workflow_id, node_count, extraction_date FROM workflow_json ORDER BY workflow_id LIMIT 20;" > .coordination/testing/results/SCRAPE-003-database-export.txt
# [Create SCRAPE-003-evidence-summary.json]
```

**Step 4: Verify Evidence Files Exist**
```bash
# Check all evidence files created
ls -la .coordination/testing/results/SCRAPE-003*

# Verify files are not empty
wc -l .coordination/testing/results/SCRAPE-003*
```

**Step 5: Double-Check Numbers**
- [ ] Count tests in output (must match requirement)
- [ ] Check coverage percentage (must be ≥80%)
- [ ] Verify all metrics in evidence summary
- [ ] Confirm no "FAIL" or "ERROR" in outputs

**Step 6: Update Notion Task**
```bash
# Update Notion page with:
# - Current progress
# - Actual metrics
# - Evidence file locations
# - Completion status
```

### **RND Manager Validation (Before PM Review):**

**Step 1: Verify Evidence Files Exist (2 min)**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
ls -la .coordination/testing/results/SCRAPE-003*

# Expected: All required files present
# If missing: REJECT immediately, return to developer
```

**Step 2: Run Tests Independently (3-5 min)**
```bash
source venv/bin/activate
pytest tests/unit/test_layer2_json.py tests/integration/test_layer2_integration.py -v

# Expected: Same results as developer reported
# If different: REJECT, return to developer
```

**Step 3: Verify Coverage (1 min)**
```bash
pytest tests/unit/test_layer2_json.py --cov=src.scrapers.layer2_json --cov-report=term

# Expected: ≥80% coverage
# If below: REJECT, return to developer
```

**Step 4: Check Evidence Summary (2 min)**
```bash
cat .coordination/testing/results/SCRAPE-003-evidence-summary.json

# Verify all metrics match requirements
# If discrepancies: REJECT, return to developer
```

**Step 5: Spot-Check Outputs (3 min)**
```bash
# Review 2-3 sample outputs
cat .coordination/testing/results/SCRAPE-003-sample-jsons/workflow_*.json

# Verify quality and format
# If issues: REJECT, return to developer
```

**Step 6: Notion Task Check (1 min)**
- [ ] Task page has content (not blank)
- [ ] Progress documented
- [ ] Metrics match evidence
- [ ] Completion marked

**RND Decision:**
- ✅ **APPROVE:** All checks pass → Forward to PM
- ❌ **REJECT:** Any check fails → Return to developer with specific issues

### **PM Final Validation (Before Approval):**

**Step 1: Review RND Report (2 min)**
- [ ] RND explicitly confirms all checks passed
- [ ] Evidence files verified by RND
- [ ] Independent test run successful
- [ ] Coverage verified

**Step 2: Spot-Verify Evidence (5 min)**
```bash
# Random sample of evidence
cat .coordination/testing/results/SCRAPE-003-evidence-summary.json
head -50 .coordination/testing/results/SCRAPE-003-test-output.txt

# Verify matches RND report
```

**Step 3: Check Notion (2 min)**
- [ ] Task page has complete documentation
- [ ] Metrics match evidence
- [ ] Progress properly tracked

**Step 4: Requirements Review (3 min)**
- [ ] Go through checklist item by item
- [ ] Each requirement has clear evidence
- [ ] All deliverables present

**PM Decision:**
- ✅ **APPROVE:** All verified → Mark task complete
- ❌ **REJECT:** Issues found → Return to RND/Developer with specific reasons

---

## 📝 SUBMISSION PROCESS

### **Developer Submission:**

**Step 1: Complete Self-Validation**
- [ ] Run through entire validation protocol above
- [ ] Create ALL required evidence files
- [ ] Update Notion task page

**Step 2: Create Submission Document**
- [ ] Copy template: `DEV-TO-RND-SCRAPE-003-SUBMISSION.md`
- [ ] Fill in all sections
- [ ] Include evidence file paths
- [ ] Add any notes or challenges

**Step 3: Submit to RND Manager**
- [ ] Place submission doc in `.coordination/handoffs/`
- [ ] Notify RND Manager
- [ ] Respond to questions promptly

### **RND Manager Review:**

**Step 1: Run Validation Protocol**
- [ ] Follow RND validation steps above
- [ ] Document results of each check

**Step 2: Make Decision**
- ✅ **APPROVE:** Create RND-TO-PM submission
- ❌ **REJECT:** Document specific issues, return to developer

**Step 3: Submit to PM (if approved)**
- [ ] Create `RND-TO-PM-SCRAPE-003-APPROVAL.md`
- [ ] Include RND verification results
- [ ] Place in `.coordination/handoffs/`
- [ ] Notify PM

### **PM Final Review:**

**Step 1: Validate RND Report**
- [ ] Follow PM validation protocol
- [ ] Spot-check evidence

**Step 2: Make Final Decision**
- ✅ **APPROVE:** Update Notion, mark complete, celebrate
- ❌ **REJECT:** Document reasons, return to RND/Developer

---

## 🚨 COMMON FAILURE MODES & PREVENTION

### **Failure Mode 1: "Works on my machine"**
**Prevention:** 
- Test in Docker container
- Provide exact environment setup
- RND runs independent validation

### **Failure Mode 2: Inflated metrics**
**Prevention:**
- Evidence files must be generated by commands, not hand-edited
- RND independently runs same commands
- PM spot-checks random samples

### **Failure Mode 3: Missing evidence**
**Prevention:**
- Explicit checklist of ALL required files
- Developer verifies file existence before submission
- RND checks file existence as first step

### **Failure Mode 4: Blank Notion pages**
**Prevention:**
- Notion update is part of acceptance criteria
- RND verifies Notion before approval
- PM checks Notion as part of review

### **Failure Mode 5: Partial work claimed as complete**
**Prevention:**
- Specific, measurable acceptance criteria
- Each criterion has verification method
- No subjective "mostly done" allowed

---

## 💡 SUCCESS CRITERIA CHECKLIST

**Before marking ANY task as complete, verify:**

- [ ] ALL acceptance criteria met (not some, ALL)
- [ ] ALL evidence files created and verified
- [ ] ALL tests passing (100%, not "most")
- [ ] Coverage ≥80% (not "close to")
- [ ] Notion task updated (not blank)
- [ ] RND independently verified (not just trusted developer)
- [ ] PM spot-checked (not just trusted RND)

**If ANY checkbox is unchecked → TASK NOT COMPLETE**

---

**This template eliminates excuses and prevents failures.**

**Use it. Follow it. Succeed.**

---

**Version:** 1.0  
**Created:** October 10, 2025  
**Author:** RND Manager  
**Status:** Active - Use for ALL future tasks

