# 📋 TASK BRIEF TEMPLATE v1.0

**For:** Dev1 & RND Manager  
**Purpose:** Crystal-clear task requirements with zero ambiguity  
**Goal:** First-time approval without rejections or rework

---

## 📝 TASK INFORMATION

**Task ID:** SCRAPE-004  
**Task Name:** Data Validation & Quality Scoring System  
**Assignee:** Dev1  
**Estimated Time:** 6 hours  
**Priority:** High  
**Dependencies:** SCRAPE-002 (Complete), SCRAPE-003 (Complete)  
**Deadline:** October 11, 2025, 18:00

---

## 🎯 OBJECTIVE (WHAT TO BUILD)

### **Primary Goal:**
Build comprehensive data validation and quality scoring system to assess the quality and completeness of all extracted workflow data across all three layers.

### **Detailed Description:**
Create a complete validation framework that validates Layer 1 metadata completeness, Layer 2 JSON structure integrity, Layer 3 content quality, and generates overall quality scores (0-100) for each workflow. The system must identify data issues, flag problems for fixing, and generate comprehensive quality reports with actionable recommendations.

This is the QUALITY ASSURANCE LAYER of the three-layer scraping system. It ensures all extracted data meets quality standards, identifies gaps and issues, and provides quality metrics for the entire dataset. The system validates existing data from SCRAPE-002 (Layer 1), SCRAPE-003 (Layer 2), and SCRAPE-005 (Layer 3), providing comprehensive quality assessment and scoring.

### **User Story:**
As a data analyst, I want to validate the quality and completeness of all extracted workflow data so that I can identify issues, measure data quality, and ensure the dataset meets standards for AI training and analysis.

### **Business Value:**
Provides critical quality assurance for the entire dataset, ensuring data reliability and completeness. Quality scoring enables prioritization of workflows for AI training, identifies data gaps that need fixing, and provides confidence in the dataset's reliability for business decisions and AI model training.

---

## ✅ ACCEPTANCE CRITERIA (EXACT REQUIREMENTS)

### **Functional Requirements:**

1. [ ] **Build Layer 1 Metadata Validator**
   - **How to verify:** Check validator processes 10 workflows successfully
   - **Evidence required:** `SCRAPE-004-validation-report.json` showing layer1_validation_results
   - **Checks:** Title presence, description length, categories, tags, difficulty, author info
   - **Target:** Validate all 10 workflows with Layer 1 metadata

2. [ ] **Build Layer 2 JSON Structure Validator**
   - **How to verify:** Check validator processes 36 workflows successfully
   - **Evidence required:** `SCRAPE-004-validation-report.json` showing layer2_validation_results
   - **Checks:** Valid JSON structure, nodes array, connections, node types, parameters
   - **Target:** Validate all 36 workflows with Layer 2 JSON data

3. [ ] **Build Layer 3 Content Quality Validator**
   - **How to verify:** Check validator processes 20 workflows successfully
   - **Evidence required:** `SCRAPE-004-validation-report.json` showing layer3_validation_results
   - **Checks:** Tutorial text length, sections extracted, image URLs valid, structure complete
   - **Target:** Validate all 20 workflows with Layer 3 content

4. [ ] **Build Quality Scoring System (0-100 scale)**
   - **How to verify:** Check quality scores generated for all workflows
   - **Evidence required:** `SCRAPE-004-quality-report.md` with score distribution
   - **Algorithm:** Layer 1 (20%) + Layer 2 (30%) + Layer 3 (40%) + Consistency (10%)
   - **Classification:** Excellent (90-100), Good (75-89), Fair (60-74), Poor (0-59)

5. [ ] **Generate Comprehensive Validation Report**
   - **How to verify:** Check report contains all validation results and metrics
   - **Evidence required:** `SCRAPE-004-validation-report.json` with complete results
   - **Contents:** Validation results, quality scores, issue counts, recommendations
   - **Format:** JSON with detailed metrics and issue tracking

6. [ ] **Create Quality Analysis Report**
   - **How to verify:** Check markdown report with quality analysis
   - **Evidence required:** `SCRAPE-004-quality-report.md` with detailed analysis
   - **Contents:** Score distribution, quality trends, issue analysis, recommendations
   - **Format:** Professional markdown report with charts and insights

7. [ ] **Store Quality Scores in Database**
   - **How to verify:** Query database for quality scores
   - **Evidence required:** Database query output showing stored scores
   - **Tables:** quality_scores, validation_issues
   - **Location:** `data/workflows.db`

8. [ ] **Identify and Flag Data Issues**
   - **How to verify:** Check issue tracking in validation report
   - **Evidence required:** `SCRAPE-004-validation-report.json` with issues_count
   - **Target:** Identify specific issues per workflow with actionable fixes
   - **Categories:** Missing data, invalid formats, incomplete content

### **Quality Requirements:**

- [ ] **Test Coverage: ≥80%**
  - **How to measure:** `pytest tests/unit/test_validation.py --cov=src.validation --cov-report=term`
  - **Evidence:** `SCRAPE-004-coverage-report.txt`
  - **Minimum:** 80.0%
  - **Target:** 85%+ for excellence

- [ ] **Tests Passing: 100%**
  - **Minimum test count:** At least 20 unit tests, 5 integration tests, 25 total
  - **How to verify:** `pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py -v`
  - **Evidence:** `SCRAPE-004-test-output.txt`
  - **Required:** ALL tests passing, no failures, no skips

- [ ] **Code Quality: No linting errors**
  - **How to verify:** `ruff check src/validation/`
  - **Evidence:** Terminal output showing "All checks passed" or linting report
  - **Required:** Zero linting errors

- [ ] **Documentation: All functions documented**
  - **How to verify:** Manual review of docstrings
  - **Evidence:** Code review notes
  - **Required:** Every function has comprehensive docstring

### **Performance Requirements:**

- [ ] **Validation Speed: ≤2 seconds per workflow**
  - **How to measure:** Check processing_time in validation report
  - **Evidence:** `SCRAPE-004-validation-report.json` with avg_processing_time
  - **Target:** 2 seconds or less per workflow

- [ ] **Memory Usage: ≤200MB peak**
  - **How to measure:** Monitor memory during validation
  - **Evidence:** Memory usage logs
  - **Target:** 200MB or less peak memory

---

## 📊 DELIVERABLES CHECKLIST

### **Code Deliverables:**
- [ ] **Implementation files:** `src/validation/layer1_validator.py`, `src/validation/layer2_validator.py`, `src/validation/layer3_validator.py`, `src/validation/quality_scorer.py`
- [ ] **Test files:** `tests/unit/test_validation.py`, `tests/integration/test_validation_integration.py`
- [ ] **Database schema:** `src/database/validation_schema.py`
- [ ] **Documentation:** README updates, docstrings, etc.

### **Evidence Deliverables:**
Developer MUST create these EXACT files:

1. [ ] **`SCRAPE-004-test-output.txt`**
   - **Contents:** Complete pytest output showing all tests passing
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py -v > .coordination/testing/results/SCRAPE-004-test-output.txt`

2. [ ] **`SCRAPE-004-coverage-report.txt`**
   - **Contents:** Complete coverage report showing ≥80%
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest --cov=src.validation --cov-report=term > .coordination/testing/results/SCRAPE-004-coverage-report.txt`

3. [ ] **`SCRAPE-004-validation-report.json`**
   - **Contents:** Complete validation results with quality scores and issue tracking
   - **Location:** `.coordination/testing/results/`
   - **How to create:** Generated by validation system during execution

4. [ ] **`SCRAPE-004-evidence-summary.json`**
   - **Contents:** JSON with all key metrics and requirements status
   - **Location:** `.coordination/testing/results/`
   - **Format:** See template below

5. [ ] **`SCRAPE-004-quality-report.md`**
   - **Contents:** Professional markdown report with quality analysis and recommendations
   - **Location:** `.coordination/testing/results/`
   - **How to create:** Generated by quality analysis system

### **Evidence Summary Template:**
```json
{
  "task_id": "SCRAPE-004",
  "completion_date": "YYYY-MM-DD",
  "developer": "Dev1",
  "metrics": {
    "workflows_validated": 40,
    "layer1_validation_rate": 95.0,
    "layer2_validation_rate": 92.5,
    "layer3_validation_rate": 88.0,
    "avg_quality_score": 78.5,
    "excellent_workflows": 8,
    "good_workflows": 15,
    "fair_workflows": 12,
    "poor_workflows": 5,
    "total_issues_found": 23,
    "avg_processing_time": 1.8
  },
  "requirements": {
    "layer1_validator": "PASS",
    "layer2_validator": "PASS",
    "layer3_validator": "PASS",
    "quality_scoring": "PASS",
    "validation_report": "PASS",
    "quality_report": "PASS",
    "database_storage": "PASS",
    "issue_tracking": "PASS",
    "coverage": "PASS",
    "tests_passing": "PASS"
  },
  "test_results": {
    "total_tests": 25,
    "passing": 25,
    "failing": 0,
    "coverage_percent": 82.5
  },
  "evidence_files": [
    "SCRAPE-004-test-output.txt",
    "SCRAPE-004-coverage-report.txt",
    "SCRAPE-004-validation-report.json",
    "SCRAPE-004-evidence-summary.json",
    "SCRAPE-004-quality-report.md"
  ]
}
```

---

## 🧪 TESTING REQUIREMENTS

### **Unit Tests Required:**

1. **Test: Layer 1 metadata validation**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_layer1_metadata_validation()`
   - **Validates:** All Layer 1 validation rules work correctly
   - **Must pass:** YES

2. **Test: Layer 2 JSON structure validation**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_layer2_json_validation()`
   - **Validates:** All Layer 2 validation rules work correctly
   - **Must pass:** YES

3. **Test: Layer 3 content quality validation**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_layer3_content_validation()`
   - **Validates:** All Layer 3 validation rules work correctly
   - **Must pass:** YES

4. **Test: Quality scoring algorithm**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_quality_scoring_algorithm()`
   - **Validates:** Quality scoring produces correct 0-100 scores
   - **Must pass:** YES

5. **Test: Quality classification**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_quality_classification()`
   - **Validates:** Workflows classified correctly (Excellent/Good/Fair/Poor)
   - **Must pass:** YES

6. **Test: Issue identification and tracking**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_issue_identification()`
   - **Validates:** Issues identified and tracked correctly
   - **Must pass:** YES

7. **Test: Database storage of quality scores**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_quality_score_storage()`
   - **Validates:** Quality scores stored in database correctly
   - **Must pass:** YES

8. **Test: Validation report generation**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_validation_report_generation()`
   - **Validates:** Validation reports generated with correct format
   - **Must pass:** YES

9. **Test: Quality report generation**
   - **File:** `tests/unit/test_validation.py`
   - **Function:** `test_quality_report_generation()`
   - **Validates:** Quality reports generated with correct format
   - **Must pass:** YES

10. **Test: Cross-layer consistency validation**
    - **File:** `tests/unit/test_validation.py`
    - **Function:** `test_cross_layer_consistency()`
    - **Validates:** Consistency checks across all layers
    - **Must pass:** YES

11. **Test: Performance requirements**
    - **File:** `tests/unit/test_validation.py`
    - **Function:** `test_validation_performance()`
    - **Validates:** Validation meets performance targets
    - **Must pass:** YES

12. **Test: Error handling for invalid data**
    - **File:** `tests/unit/test_validation.py`
    - **Function:** `test_invalid_data_handling()`
    - **Validates:** Graceful handling of invalid data
    - **Must pass:** YES

13. **Test: Memory usage optimization**
    - **File:** `tests/unit/test_validation.py`
    - **Function:** `test_memory_usage()`
    - **Validates:** Memory usage within limits
    - **Must pass:** YES

14. **Test: Validation statistics calculation**
    - **File:** `tests/unit/test_validation.py`
    - **Function:** `test_validation_statistics()`
    - **Validates:** Statistics calculated correctly
    - **Must pass:** YES

15. **Test: Quality trend analysis**
    - **File:** `tests/unit/test_validation.py`
    - **Function:** `test_quality_trend_analysis()`
    - **Validates:** Quality trends analyzed correctly
    - **Must pass:** YES

### **Integration Tests Required:**

1. **Test: End-to-end validation pipeline**
   - **File:** `tests/integration/test_validation_integration.py`
   - **Function:** `test_end_to_end_validation()`
   - **Validates:** Complete validation pipeline works end-to-end
   - **Must pass:** YES

2. **Test: Multi-layer validation coordination**
   - **File:** `tests/integration/test_validation_integration.py`
   - **Function:** `test_multi_layer_coordination()`
   - **Validates:** All validators work together correctly
   - **Must pass:** YES

3. **Test: Database integration with existing data**
   - **File:** `tests/integration/test_validation_integration.py`
   - **Function:** `test_database_integration()`
   - **Validates:** Integrates with existing workflow data
   - **Must pass:** YES

4. **Test: Report generation with real data**
   - **File:** `tests/integration/test_validation_integration.py`
   - **Function:** `test_report_generation_with_real_data()`
   - **Validates:** Reports generated with actual workflow data
   - **Must pass:** YES

5. **Test: Performance with large dataset**
   - **File:** `tests/integration/test_validation_integration.py`
   - **Function:** `test_performance_with_large_dataset()`
   - **Validates:** Performance maintained with large datasets
   - **Must pass:** YES

### **Test Coverage Targets:**
- **Minimum overall:** 80%
- **Per-file minimum:** 80%
- **Critical paths:** 100%

### **How to Run All Tests:**
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run all tests with coverage
pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py --cov=src.validation --cov-report=term-missing -v

# 3. Verify all pass
# Expected: 25 passed, 0 failed

# 4. Save output
pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py -v > .coordination/testing/results/SCRAPE-004-test-output.txt
```

---

## 🔍 VALIDATION PROTOCOL

### **Developer Self-Validation (Before Submission):**

**Step 1: Verify All Code Exists**
```bash
# Check implementation files exist
ls -la src/validation/layer1_validator.py
ls -la src/validation/layer2_validator.py
ls -la src/validation/layer3_validator.py
ls -la src/validation/quality_scorer.py
ls -la tests/unit/test_validation.py

# Verify no syntax errors
python -m py_compile src/validation/layer1_validator.py
python -m py_compile src/validation/layer2_validator.py
python -m py_compile src/validation/layer3_validator.py
python -m py_compile src/validation/quality_scorer.py
```

**Step 2: Run Full Test Suite**
```bash
# Must show 100% passing
pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py -v

# Must meet coverage requirement
pytest --cov=src.validation --cov-report=term
```

**Step 3: Generate Evidence Files**
```bash
# Create all required evidence files
pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py -v > .coordination/testing/results/SCRAPE-004-test-output.txt
pytest --cov=src.validation --cov-report=term > .coordination/testing/results/SCRAPE-004-coverage-report.txt
# [Add commands for all evidence files]
```

**Step 4: Verify Evidence Files Exist**
```bash
# Check all evidence files created
ls -la .coordination/testing/results/SCRAPE-004*

# Verify files are not empty
wc -l .coordination/testing/results/SCRAPE-004*
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
ls -la .coordination/testing/results/SCRAPE-004*

# Expected: All required files present
# If missing: REJECT immediately, return to developer
```

**Step 2: Run Tests Independently (3-5 min)**
```bash
source venv/bin/activate
pytest tests/unit/test_validation.py tests/integration/test_validation_integration.py -v

# Expected: Same results as developer reported
# If different: REJECT, return to developer
```

**Step 3: Verify Coverage (1 min)**
```bash
pytest --cov=src.validation --cov-report=term

# Expected: ≥80% coverage
# If below: REJECT, return to developer
```

**Step 4: Check Evidence Summary (2 min)**
```bash
cat .coordination/testing/results/SCRAPE-004-evidence-summary.json

# Verify all metrics match requirements
# If discrepancies: REJECT, return to developer
```

**Step 5: Spot-Check Outputs (3 min)**
```bash
# Review validation report
cat .coordination/testing/results/SCRAPE-004-validation-report.json

# Review quality report
head -50 .coordination/testing/results/SCRAPE-004-quality-report.md

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
cat .coordination/testing/results/SCRAPE-004-evidence-summary.json
head -50 .coordination/testing/results/SCRAPE-004-test-output.txt

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
- [ ] Copy template: `DEV-TO-RND-[TASK-ID]-SUBMISSION.md`
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
- [ ] Create `RND-TO-PM-[TASK-ID]-APPROVAL.md`
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

## 🔧 TECHNICAL IMPLEMENTATION GUIDANCE

### **Layer 1 Validator Implementation:**
```python
# Example structure for Layer 1 validation
def validate_layer1_metadata(workflow_data):
    """
    Validate Layer 1 metadata completeness and quality.
    
    Args:
        workflow_data (dict): Layer 1 workflow data
        
    Returns:
        dict: Validation results with score and issues
    """
    score = 0
    issues = []
    
    # Check title presence and quality
    if not workflow_data.get('title') or len(workflow_data['title']) < 10:
        issues.append("Title missing or too short")
    else:
        score += 20
    
    # Check description length
    description = workflow_data.get('description', '')
    if len(description) < 50:
        issues.append("Description too short (minimum 50 characters)")
    else:
        score += 20
    
    # Check categories
    if not workflow_data.get('categories'):
        issues.append("Categories not assigned")
    else:
        score += 20
    
    # Check tags
    tags = workflow_data.get('tags', [])
    if len(tags) < 2:
        issues.append("Insufficient tags (minimum 2 required)")
    else:
        score += 20
    
    # Check difficulty
    if not workflow_data.get('difficulty'):
        issues.append("Difficulty level not set")
    else:
        score += 20
    
    return {
        'score': score,
        'issues': issues,
        'valid': score >= 80
    }
```

### **Layer 2 Validator Implementation:**
```python
# Example structure for Layer 2 validation
def validate_layer2_json_structure(workflow_json):
    """
    Validate Layer 2 JSON structure and integrity.
    
    Args:
        workflow_json (dict): Layer 2 workflow JSON data
        
    Returns:
        dict: Validation results with score and issues
    """
    score = 0
    issues = []
    
    # Check JSON structure
    if not isinstance(workflow_json, dict):
        issues.append("Invalid JSON structure")
        return {'score': 0, 'issues': issues, 'valid': False}
    else:
        score += 20
    
    # Check nodes array
    nodes = workflow_json.get('nodes', [])
    if not nodes or not isinstance(nodes, list):
        issues.append("Nodes array missing or invalid")
    else:
        score += 30
    
    # Check connections
    connections = workflow_json.get('connections', {})
    if not connections:
        issues.append("Connections not defined")
    else:
        score += 25
    
    # Check node types
    valid_node_types = ['HTTP Request', 'Set', 'Gmail', 'Schedule', 'Webhook']
    for node in nodes:
        if node.get('type') not in valid_node_types:
            issues.append(f"Invalid node type: {node.get('type')}")
        else:
            score += 25
    
    return {
        'score': min(score, 100),
        'issues': issues,
        'valid': score >= 75
    }
```

### **Layer 3 Validator Implementation:**
```python
# Example structure for Layer 3 validation
def validate_layer3_content_quality(content_data):
    """
    Validate Layer 3 content quality and completeness.
    
    Args:
        content_data (dict): Layer 3 content data
        
    Returns:
        dict: Validation results with score and issues
    """
    score = 0
    issues = []
    
    # Check tutorial text length
    tutorial_text = content_data.get('tutorial_text', '')
    if len(tutorial_text) < 200:
        issues.append("Tutorial text too short (minimum 200 characters)")
    else:
        score += 30
    
    # Check tutorial sections
    sections = content_data.get('tutorial_sections', [])
    if len(sections) < 3:
        issues.append("Insufficient tutorial sections (minimum 3)")
    else:
        score += 25
    
    # Check image URLs
    images = content_data.get('images', [])
    valid_images = 0
    for img in images:
        if img.get('url') and img['url'].startswith('http'):
            valid_images += 1
    
    if valid_images == 0:
        issues.append("No valid image URLs found")
    else:
        score += 25
    
    # Check structure completeness
    required_fields = ['title', 'description', 'steps', 'outputs']
    missing_fields = [field for field in required_fields if not content_data.get(field)]
    if missing_fields:
        issues.append(f"Missing required fields: {', '.join(missing_fields)}")
    else:
        score += 20
    
    return {
        'score': score,
        'issues': issues,
        'valid': score >= 80
    }
```

### **Quality Scorer Implementation:**
```python
# Example structure for quality scoring
def calculate_quality_score(layer1_result, layer2_result, layer3_result):
    """
    Calculate overall quality score (0-100) based on all layers.
    
    Args:
        layer1_result (dict): Layer 1 validation result
        layer2_result (dict): Layer 2 validation result
        layer3_result (dict): Layer 3 validation result
        
    Returns:
        dict: Overall quality score and classification
    """
    # Calculate weighted score
    weighted_score = (
        layer1_result['score'] * 0.20 +  # Layer 1: 20%
        layer2_result['score'] * 0.30 +  # Layer 2: 30%
        layer3_result['score'] * 0.40 +  # Layer 3: 40%
        calculate_consistency_score(layer1_result, layer2_result, layer3_result) * 0.10  # Consistency: 10%
    )
    
    # Classify quality
    if weighted_score >= 90:
        classification = "Excellent"
    elif weighted_score >= 75:
        classification = "Good"
    elif weighted_score >= 60:
        classification = "Fair"
    else:
        classification = "Poor"
    
    return {
        'score': round(weighted_score, 1),
        'classification': classification,
        'layer1_score': layer1_result['score'],
        'layer2_score': layer2_result['score'],
        'layer3_score': layer3_result['score'],
        'consistency_score': calculate_consistency_score(layer1_result, layer2_result, layer3_result)
    }

def calculate_consistency_score(layer1_result, layer2_result, layer3_result):
    """
    Calculate consistency score across layers.
    
    Args:
        layer1_result, layer2_result, layer3_result (dict): Validation results
        
    Returns:
        int: Consistency score (0-100)
    """
    # Check if all layers have data
    has_layer1 = layer1_result['score'] > 0
    has_layer2 = layer2_result['score'] > 0
    has_layer3 = layer3_result['score'] > 0
    
    # Calculate consistency based on data availability
    if has_layer1 and has_layer2 and has_layer3:
        return 100  # All layers present
    elif (has_layer1 and has_layer2) or (has_layer1 and has_layer3) or (has_layer2 and has_layer3):
        return 70   # Two layers present
    elif has_layer1 or has_layer2 or has_layer3:
        return 40   # One layer present
    else:
        return 0    # No layers present
```

### **Database Schema:**
```sql
-- Quality scores table
CREATE TABLE quality_scores (
    id INTEGER PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    overall_score REAL NOT NULL,
    classification TEXT NOT NULL,
    layer1_score REAL,
    layer2_score REAL,
    layer3_score REAL,
    consistency_score REAL,
    validation_date TEXT NOT NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);

-- Validation issues table
CREATE TABLE validation_issues (
    id INTEGER PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    layer TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    severity TEXT NOT NULL,
    validation_date TEXT NOT NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);
```

---

**This template eliminates excuses and prevents failures.**

**Use it. Follow it. Succeed.**

---

**Version:** 1.0  
**Created:** October 10, 2025  
**Author:** RND Manager  
**Status:** Active - Use for ALL future tasks

