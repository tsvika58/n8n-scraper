# 📋 TASK BRIEF TEMPLATE v1.0

**For:** Dev2 & RND Manager  
**Purpose:** Crystal-clear task requirements with zero ambiguity  
**Goal:** First-time approval without rejections or rework

---

## 📝 TASK INFORMATION

**Task ID:** SCRAPE-006  
**Task Name:** Layer 3 - Multimodal Content Processor (OCR + Video)  
**Assignee:** Dev2  
**Estimated Time:** 10 hours  
**Priority:** High  
**Dependencies:** SCRAPE-005 (Complete)  
**Deadline:** October 12, 2025, 15:00

---

## 🎯 OBJECTIVE (WHAT TO BUILD)

### **Primary Goal:**
Extract text from images and transcripts from videos within n8n.io workflow iframes to create comprehensive multimodal content dataset.

### **Detailed Description:**
Build a multimodal content processor that processes existing workflow data from SCRAPE-005, extracts text from workflow images using OCR, extracts transcripts from YouTube videos, and stores all content in dedicated database tables. The processor must handle iframe navigation, image downloading, OCR processing, video ID extraction, and transcript retrieval with robust error handling and comprehensive testing.

This is the THIRD LAYER of the three-layer scraping system. It processes multimodal content (images with text, videos with transcripts) from workflows that were previously extracted in SCRAPE-005, providing the rich contextual information needed for AI training and workflow understanding.

### **User Story:**
As a data analyst, I want to extract text from workflow images and video transcripts so that I can understand the complete context and instructions for each n8n workflow, enabling better AI training and workflow analysis.

### **Business Value:**
Provides the final layer of rich multimodal content that transforms basic workflow metadata into comprehensive, AI-trainable datasets. The extracted text from images and video transcripts contains crucial instructional content that explains how workflows function, making this essential for building effective AI models.

---

## ✅ ACCEPTANCE CRITERIA (EXACT REQUIREMENTS)

### **Functional Requirements:**

1. [ ] **Validate YouTube Transcript API access and functionality**
   - **How to verify:** Test API with known YouTube video ID
   - **Evidence required:** `SCRAPE-006-youtube-api-validation.txt` with successful API test
   - **Test video:** Use a known n8n tutorial video for validation
   - **Required:** API key working, transcript extraction successful

2. [ ] **Discover and extract YouTube video URLs from workflow iframes**
   - **How to verify:** Count discovered video URLs in summary JSON
   - **Evidence required:** `SCRAPE-006-processing-summary.json` with video_discovery_count
   - **Method:** Navigate iframes, find YouTube embeds, extract video URLs
   - **Target:** Find videos in 60%+ of workflows that contain iframes

3. [ ] **Process 10-15 workflows from existing SCRAPE-005 data**
   - **How to verify:** Count processed workflows in database: `sqlite3 data/workflows.db "SELECT COUNT(DISTINCT workflow_id) FROM workflow_images UNION SELECT COUNT(DISTINCT workflow_id) FROM workflow_videos;"`
   - **Evidence required:** `SCRAPE-006-processing-summary.json` showing workflow count
   - **Minimum:** 10 workflows
   - **Target:** 15 workflows for excellence

4. [ ] **Achieve ≥85% OCR success rate on workflow images**
   - **How to verify:** Check OCR success rate in summary JSON
   - **Evidence required:** `SCRAPE-006-processing-summary.json` with ocr_success_rate field
   - **Calculation:** (successful_ocr_extractions / total_images_processed) × 100
   - **Minimum:** 85.0%

5. [ ] **Achieve ≥80% video transcript success rate**
   - **How to verify:** Check video success rate in summary JSON
   - **Evidence required:** `SCRAPE-006-processing-summary.json` with video_success_rate field
   - **Calculation:** (successful_transcript_extractions / total_videos_processed) × 100
   - **Minimum:** 80.0%

6. [ ] **Extract text from workflow iframe images**
   - **Target:** Images within workflow iframes containing instructional text
   - **How to verify:** Check sample OCR extractions in evidence files
   - **Evidence required:** `SCRAPE-006-sample-outputs/` folder with 5+ OCR examples
   - **Example:** Text like "🚀🚀 Start here 🚀🚀" from workflow instruction images

7. [ ] **Extract transcripts from discovered YouTube videos**
   - **Target:** YouTube videos discovered in workflow iframes
   - **How to verify:** Check sample transcript extractions in evidence files
   - **Evidence required:** `SCRAPE-006-sample-outputs/` folder with 5+ transcript examples
   - **Format:** Full transcript text with timestamps
   - **Purpose:** Provide business and technical context for workflow understanding

8. [ ] **Store all data in dedicated database tables**
   - **Tables:** workflow_images, workflow_videos
   - **How to verify:** Query database for records
   - **Evidence required:** Database query output showing stored data
   - **Location:** `data/workflows.db`

9. [ ] **Handle iframe navigation and content extraction**
   - **Target:** Navigate to workflow iframes, extract images and videos
   - **How to verify:** Check logs for iframe navigation success
   - **Evidence required:** Code review showing iframe handling implementation
   - **Method:** Use Playwright to navigate iframes and extract content

### **Quality Requirements:**

- [ ] **Test Coverage: ≥80%**
  - **How to measure:** `pytest tests/unit/test_multimodal_processor.py --cov=src.scrapers.multimodal_processor --cov-report=term`
  - **Evidence:** `SCRAPE-006-coverage-report.txt`
  - **Minimum:** 80.0%
  - **Target:** 85%+ for excellence

- [ ] **Tests Passing: 100%**
  - **Minimum test count:** At least 25 unit tests, 5 integration tests, 30 total
  - **How to verify:** `pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py -v`
  - **Evidence:** `SCRAPE-006-test-output.txt`
  - **Required:** ALL tests passing, no failures, no skips

- [ ] **Code Quality: No linting errors**
  - **How to verify:** `ruff check src/scrapers/multimodal_processor.py`
  - **Evidence:** Terminal output showing "All checks passed" or linting report
  - **Required:** Zero linting errors

- [ ] **Documentation: All functions documented**
  - **How to verify:** Manual review of docstrings
  - **Evidence:** Code review notes
  - **Required:** Every function has comprehensive docstring

### **Performance Requirements:**

- [ ] **Processing Speed: ≤30 seconds per workflow**
  - **How to measure:** Check processing_time in summary JSON
  - **Evidence:** `SCRAPE-006-processing-summary.json` with avg_processing_time
  - **Target:** 30 seconds or less per workflow

- [ ] **Memory Usage: ≤500MB peak**
  - **How to measure:** Monitor memory during processing
  - **Evidence:** Memory usage logs
  - **Target:** 500MB or less peak memory

---

## 📊 DELIVERABLES CHECKLIST

### **Code Deliverables:**
- [ ] **Implementation file(s):** `src/scrapers/multimodal_processor.py`
- [ ] **Test file(s):** `tests/unit/test_multimodal_processor.py`, `tests/integration/test_multimodal_integration.py`
- [ ] **Database schema:** `src/database/multimodal_schema.py`
- [ ] **Documentation:** README updates, docstrings, etc.

### **Evidence Deliverables:**
Developer MUST create these EXACT files:

1. [ ] **`SCRAPE-006-youtube-api-validation.txt`**
   - **Contents:** YouTube API validation test results with successful transcript extraction
   - **Location:** `.coordination/testing/results/`
   - **How to create:** Test API with known n8n tutorial video, save output to file
   - **Required:** API key working, transcript extraction successful

2. [ ] **`SCRAPE-006-test-output.txt`**
   - **Contents:** Complete pytest output showing all tests passing
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py -v > .coordination/testing/results/SCRAPE-006-test-output.txt`

3. [ ] **`SCRAPE-006-coverage-report.txt`**
   - **Contents:** Complete coverage report showing ≥80%
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest --cov=src.scrapers.multimodal_processor --cov-report=term > .coordination/testing/results/SCRAPE-006-coverage-report.txt`

4. [ ] **`SCRAPE-006-processing-summary.json`**
   - **Contents:** JSON with OCR results, video discovery results, transcript results, and total metrics
   - **Location:** `.coordination/testing/results/`
   - **How to create:** Generated by the processor during execution
   - **Must include:** video_discovery_count, ocr_success_rate, video_success_rate

5. [ ] **`SCRAPE-006-evidence-summary.json`**
   - **Contents:** JSON with all key metrics and requirements status
   - **Location:** `.coordination/testing/results/`
   - **Format:** See template below

6. [ ] **`SCRAPE-006-sample-outputs/`** (folder)
   - **Contents:** 5+ sample OCR extractions and 5+ sample transcript extractions
   - **Location:** `.coordination/testing/results/`
   - **How to create:** Generated by the processor during execution

### **Evidence Summary Template:**
```json
{
  "task_id": "SCRAPE-006",
  "completion_date": "YYYY-MM-DD",
  "developer": "Dev2",
  "metrics": {
    "workflows_processed": 15,
    "video_discovery_count": 8,
    "ocr_success_rate": 87.5,
    "video_success_rate": 83.3,
    "avg_processing_time": 28.5,
    "total_images_processed": 45,
    "total_videos_processed": 12,
    "youtube_api_validation": "PASS"
  },
  "requirements": {
    "youtube_api_validation": "PASS",
    "video_discovery": "PASS",
    "workflow_count": "PASS",
    "ocr_success": "PASS",
    "video_success": "PASS",
    "coverage": "PASS",
    "tests_passing": "PASS"
  },
  "test_results": {
    "total_tests": 30,
    "passing": 30,
    "failing": 0,
    "coverage_percent": 82.5
  },
  "evidence_files": [
    "SCRAPE-006-youtube-api-validation.txt",
    "SCRAPE-006-test-output.txt",
    "SCRAPE-006-coverage-report.txt",
    "SCRAPE-006-processing-summary.json",
    "SCRAPE-006-evidence-summary.json",
    "SCRAPE-006-sample-outputs/"
  ]
}
```

---

## 🧪 TESTING REQUIREMENTS

### **Unit Tests Required:**

1. **Test: YouTube API validation and access**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_youtube_api_validation()`
   - **Validates:** YouTube API key works and can extract transcripts
   - **Must pass:** YES

2. **Test: YouTube video URL discovery in iframes**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_youtube_url_discovery()`
   - **Validates:** Can find YouTube video URLs in workflow iframes
   - **Must pass:** YES

3. **Test: OCR text extraction from images**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_ocr_text_extraction()`
   - **Validates:** OCR can extract text from workflow images
   - **Must pass:** YES

4. **Test: Video transcript extraction**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_video_transcript_extraction()`
   - **Validates:** Can extract transcripts from YouTube videos
   - **Must pass:** YES

5. **Test: Iframe navigation and content extraction**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_iframe_navigation()`
   - **Validates:** Can navigate to workflow iframes and extract content
   - **Must pass:** YES

6. **Test: Database storage for images and videos**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_database_storage()`
   - **Validates:** Data is properly stored in database tables
   - **Must pass:** YES

7. **Test: Error handling for failed OCR**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_ocr_error_handling()`
   - **Validates:** Graceful handling of OCR failures
   - **Must pass:** YES

8. **Test: Error handling for failed video processing**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_video_error_handling()`
   - **Validates:** Graceful handling of video processing failures
   - **Must pass:** YES

9. **Test: Rate limiting and request throttling**
   - **File:** `tests/unit/test_multimodal_processor.py`
   - **Function:** `test_rate_limiting()`
   - **Validates:** Proper rate limiting to avoid blocking
   - **Must pass:** YES

10. **Test: Image download and processing**
    - **File:** `tests/unit/test_multimodal_processor.py`
    - **Function:** `test_image_download_processing()`
    - **Validates:** Images are downloaded and processed correctly
    - **Must pass:** YES

11. **Test: Video ID extraction from URLs**
    - **File:** `tests/unit/test_multimodal_processor.py`
    - **Function:** `test_video_id_extraction()`
    - **Validates:** YouTube video IDs are extracted correctly
    - **Must pass:** YES

12. **Test: Transcript parsing and storage**
    - **File:** `tests/unit/test_multimodal_processor.py`
    - **Function:** `test_transcript_parsing()`
    - **Validates:** Transcripts are parsed and stored correctly
    - **Must pass:** YES

### **Integration Tests Required:**

1. **Test: End-to-end multimodal processing**
   - **File:** `tests/integration/test_multimodal_integration.py`
   - **Function:** `test_end_to_end_processing()`
   - **Validates:** Complete workflow from iframe to database
   - **Must pass:** YES

2. **Test: Multiple workflow processing**
   - **File:** `tests/integration/test_multimodal_integration.py`
   - **Function:** `test_multiple_workflow_processing()`
   - **Validates:** Can process multiple workflows successfully
   - **Must pass:** YES

3. **Test: Database integration with existing data**
   - **File:** `tests/integration/test_multimodal_integration.py`
   - **Function:** `test_database_integration()`
   - **Validates:** Integrates with existing SCRAPE-005 data
   - **Must pass:** YES

4. **Test: Error recovery and continuation**
   - **File:** `tests/integration/test_multimodal_integration.py`
   - **Function:** `test_error_recovery()`
   - **Validates:** Can recover from errors and continue processing
   - **Must pass:** YES

5. **Test: Performance under load**
   - **File:** `tests/integration/test_multimodal_integration.py`
   - **Function:** `test_performance_under_load()`
   - **Validates:** Maintains performance with multiple workflows
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
pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py --cov=src.scrapers.multimodal_processor --cov-report=term-missing -v

# 3. Verify all pass
# Expected: 32 passed, 0 failed (added 2 new tests)

# 4. Save output
pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py -v > .coordination/testing/results/SCRAPE-006-test-output.txt
```

---

## 🔍 VALIDATION PROTOCOL

### **Developer Self-Validation (Before Submission):**

**Step 1: Verify All Code Exists**
```bash
# Check implementation files exist
ls -la src/scrapers/multimodal_processor.py
ls -la tests/unit/test_multimodal_processor.py
ls -la tests/integration/test_multimodal_integration.py

# Verify no syntax errors
python -m py_compile src/scrapers/multimodal_processor.py
```

**Step 2: Run Full Test Suite**
```bash
# Must show 100% passing
pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py -v

# Must meet coverage requirement
pytest --cov=src.scrapers.multimodal_processor --cov-report=term
```

**Step 3: Generate Evidence Files**
```bash
# Create all required evidence files
pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py -v > .coordination/testing/results/SCRAPE-006-test-output.txt
pytest --cov=src.scrapers.multimodal_processor --cov-report=term > .coordination/testing/results/SCRAPE-006-coverage-report.txt
# [Add commands for all evidence files]
```

**Step 4: Verify Evidence Files Exist**
```bash
# Check all evidence files created
ls -la .coordination/testing/results/SCRAPE-006*

# Verify files are not empty
wc -l .coordination/testing/results/SCRAPE-006*
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
ls -la .coordination/testing/results/SCRAPE-006*

# Expected: All required files present
# If missing: REJECT immediately, return to developer
```

**Step 2: Run Tests Independently (3-5 min)**
```bash
source venv/bin/activate
pytest tests/unit/test_multimodal_processor.py tests/integration/test_multimodal_integration.py -v

# Expected: Same results as developer reported
# If different: REJECT, return to developer
```

**Step 3: Verify Coverage (1 min)**
```bash
pytest --cov=src.scrapers.multimodal_processor --cov-report=term

# Expected: ≥80% coverage
# If below: REJECT, return to developer
```

**Step 4: Check Evidence Summary (2 min)**
```bash
cat .coordination/testing/results/SCRAPE-006-evidence-summary.json

# Verify all metrics match requirements
# If discrepancies: REJECT, return to developer
```

**Step 5: Spot-Check Outputs (3 min)**
```bash
# Review 2-3 sample outputs
cat .coordination/testing/results/SCRAPE-006-sample-outputs/sample_ocr_1.json
cat .coordination/testing/results/SCRAPE-006-sample-outputs/sample_transcript_1.json

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
cat .coordination/testing/results/SCRAPE-006-evidence-summary.json
head -50 .coordination/testing/results/SCRAPE-006-test-output.txt

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

### **OCR Processor Implementation:**
```python
# Example structure for OCR processing
def extract_text_from_workflow_images(workflow_id, iframe_url):
    """
    Extract text from images within workflow iframes using OCR.
    
    Args:
        workflow_id (str): The workflow identifier
        iframe_url (str): URL of the workflow iframe
        
    Returns:
        dict: OCR results with extracted text and metadata
    """
    # Navigate to iframe
    # Extract images
    # Download images
    # Run OCR on each image
    # Store results in database
    pass
```

### **YouTube Video Discovery and Processing:**
```python
# Example structure for video discovery and processing
def discover_youtube_videos_in_iframe(page, workflow_url):
    """
    Discover YouTube video URLs within workflow iframes.
    
    Args:
        page: Playwright page object
        workflow_url (str): URL of the workflow page
        
    Returns:
        list: List of discovered YouTube video URLs
    """
    # Navigate to workflow page
    # Find iframe element
    # Switch to iframe context
    # Search for YouTube embeds
    # Extract video URLs
    # Return list of URLs
    pass

def extract_video_transcripts(workflow_id, video_urls):
    """
    Extract transcripts from discovered YouTube videos.
    
    Args:
        workflow_id (str): The workflow identifier
        video_urls (list): List of discovered YouTube video URLs
        
    Returns:
        dict: Transcript results with extracted text and metadata
    """
    # Validate YouTube API access first
    # Extract YouTube video IDs from URLs
    # Get transcripts using youtube-transcript-api
    # Store results in database
    pass
```

### **Database Schema:**
```sql
-- Images with OCR text
CREATE TABLE workflow_images (
    id INTEGER PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    image_url TEXT NOT NULL,
    ocr_text TEXT,
    text_length INTEGER,
    extraction_date TEXT,
    success BOOLEAN,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);

-- Videos with transcripts
CREATE TABLE workflow_videos (
    id INTEGER PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    video_url TEXT NOT NULL,
    video_id TEXT,
    transcript TEXT,
    transcript_length INTEGER,
    extraction_date TEXT,
    success BOOLEAN,
    FOREIGN KEY (workflow_id) REFERENCES workflow_inventory(workflow_id)
);
```

### **Iframe Navigation:**
```python
# Example iframe navigation
def navigate_to_workflow_iframe(page, workflow_url):
    """
    Navigate to workflow iframe and extract content.
    
    Args:
        page: Playwright page object
        workflow_url (str): URL of the workflow page
        
    Returns:
        dict: Extracted content from iframe
    """
    # Navigate to workflow page
    # Find iframe element
    # Switch to iframe context
    # Extract images and videos
    # Return content
    pass
```

---

**This template eliminates excuses and prevents failures.**

**Use it. Follow it. Succeed.**

---

**Version:** 1.0  
**Created:** October 10, 2025  
**Author:** RND Manager  
**Status:** Active - Use for ALL future tasks
