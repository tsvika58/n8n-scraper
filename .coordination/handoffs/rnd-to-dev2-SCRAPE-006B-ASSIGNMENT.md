# 📋 TASK ASSIGNMENT: SCRAPE-006B v1.0

**For:** Dev2  
**Purpose:** Implement YouTube transcript extraction with hybrid API + UI automation approach  
**Goal:** Enable extraction of video transcripts from n8n workflow pages with 80%+ success rate

---

## 📝 TASK INFORMATION

**Task ID:** SCRAPE-006B  
**Task Name:** YouTube Transcript Extraction  
**Assignee:** Dev2  
**Estimated Time:** 8 hours (3 days at 2-3 hours/day)  
**Priority:** High  
**Dependencies:** 
- SCRAPE-006 Complete ✅ (video URLs captured)
- SCRAPE-006-REWORK Complete ✅ (integration testing validated)
**Deadline:** October 13, 2025, 18:00 (Day 5)

**Brief Version:** 1.0  
**Last Updated:** October 10, 2025  
**Changes from v0.0:** Initial creation based on PM brief

---

## 🎯 OBJECTIVE (WHAT TO BUILD)

### **Primary Goal:**
Implement a hybrid YouTube transcript extraction system that combines YouTube Transcript API with Playwright UI automation fallback to achieve 80%+ success rate on video transcripts from n8n workflow pages.

### **Detailed Description:**
Build a robust transcript extraction system that first attempts to extract transcripts via the official `youtube-transcript-api`, then falls back to Playwright UI automation if the API fails. The system must handle various edge cases (no captions, private videos, rate limits), integrate seamlessly with the existing `multimodal_processor.py`, store results in the database, and achieve production-ready reliability.

This completes the LAYER 3 multimodal content extraction by adding the final missing piece: video transcript data. This data is critical for NLP training and provides rich context about workflow functionality that isn't available from metadata or JSON structure alone.

### **User Story:**
As a data scientist, I want transcripts from YouTube tutorial videos embedded in n8n workflows so that I can train NLP models on natural language explanations of workflow functionality.

### **Business Value:**
Provides the final piece of Layer 3 content extraction, enabling complete multimodal data capture (text + images + video transcripts) from n8n workflows. This completes the "deep content" layer that provides 80% of NLP training value and enables comprehensive workflow understanding.

---

## ✅ ACCEPTANCE CRITERIA (EXACT REQUIREMENTS)

### **Functional Requirements:**

1. [ ] **YouTube Transcript API implementation working**
   - **How to verify:** Test with 10 known captioned videos
   - **Evidence required:** `SCRAPE-006B-api-test-results.json` showing successful extractions
   - **Success rate:** ≥70% for API method alone
   - **Performance:** <10 seconds per video

2. [ ] **Playwright UI automation fallback working**
   - **How to verify:** Test with 10 videos (mix of API failures and successes)
   - **Evidence required:** `SCRAPE-006B-ui-test-results.json` showing successful fallback
   - **Success rate:** ≥50% for videos where API fails
   - **Performance:** <30 seconds per video

3. [ ] **Hybrid system achieving 80%+ success rate**
   - **How to verify:** Test with 20 real YouTube videos from n8n workflows
   - **Evidence required:** `SCRAPE-006B-hybrid-test-results.json` with success_rate ≥80%
   - **Calculation:** (successful_extractions / total_videos) × 100 ≥ 80%
   - **Minimum:** 16/20 successful

4. [ ] **Integration with multimodal_processor.py complete**
   - **How to verify:** Replace stub code in lines 372-459 with new implementation
   - **Evidence required:** Git diff showing integration + working tests
   - **Method:** Call new `TranscriptExtractor` class from `multimodal_processor.py`
   - **Database storage:** Use existing `store_video_data()` method

5. [ ] **Error handling for all edge cases**
   - **Edge cases:** No captions, private videos, age-restricted, rate limits, network errors
   - **How to verify:** Test with specific edge case videos
   - **Evidence required:** `SCRAPE-006B-edge-case-tests.json` showing graceful failures
   - **Requirement:** No crashes, all errors logged with clear messages

6. [ ] **Database storage working correctly**
   - **How to verify:** Check database after test runs
   - **Evidence required:** SQL query output showing stored transcripts
   - **Fields:** workflow_id, video_url, video_id, success, transcript_text, error
   - **Verification:** `SELECT * FROM multimodal_data WHERE video_id IS NOT NULL LIMIT 5;`

7. [ ] **Performance targets met**
   - **API method:** <10 seconds per video
   - **UI fallback:** <30 seconds per video
   - **How to verify:** Test with timing measurements
   - **Evidence required:** `SCRAPE-006B-performance-results.json` with timing data

8. [ ] **Test coverage ≥85%**
   - **How to measure:** `pytest tests/unit/test_transcript_extractor.py --cov=src.scrapers.transcript_extractor --cov-report=term`
   - **Evidence:** `SCRAPE-006B-coverage-report.txt`
   - **Minimum:** 85.0%
   - **Target:** 90%+ for excellence

### **Quality Requirements:**

- [ ] **Unit Tests: 10-15 passing**
  - **How to verify:** `pytest tests/unit/test_transcript_extractor.py -v`
  - **Evidence:** `SCRAPE-006B-unit-test-output.txt`
  - **Required:** ALL tests passing, no failures, no skips
  - **Coverage:** API method, UI method, hybrid method, error handling

- [ ] **Integration Tests: 5-8 passing**
  - **How to verify:** `pytest tests/integration/test_transcript_extraction_real.py -v`
  - **Evidence:** `SCRAPE-006B-integration-test-output.txt`
  - **Required:** ALL tests passing with real YouTube videos
  - **Tests:** Real videos from workflows 6270, 8527, 8237

- [ ] **Code Quality: No linting errors**
  - **How to verify:** `ruff check src/scrapers/transcript_extractor.py`
  - **Evidence:** Terminal output showing "All checks passed"
  - **Required:** Zero linting errors, proper docstrings, type hints

### **Performance Requirements:**

- [ ] **API method speed: <10 seconds**
  - **How to measure:** Time API-based extractions
  - **Evidence:** Performance test results
  - **Target:** 8 seconds average

- [ ] **UI fallback speed: <30 seconds**
  - **How to measure:** Time Playwright-based extractions
  - **Evidence:** Performance test results
  - **Target:** 25 seconds average

- [ ] **Memory usage: <500MB per extraction**
  - **How to measure:** Monitor memory during extraction
  - **Evidence:** Memory usage logs
  - **Target:** 300-400MB typical

---

## 📊 DELIVERABLES CHECKLIST

### **Code Deliverables:**
- [ ] **`src/scrapers/transcript_extractor.py`** - Main transcript extraction class
- [ ] **Integration updates to `src/scrapers/multimodal_processor.py`** - Replace lines 372-459
- [ ] **`tests/unit/test_transcript_extractor.py`** - Unit tests (10-15 tests)
- [ ] **`tests/integration/test_transcript_extraction_real.py`** - Integration tests (5-8 tests)
- [ ] **`requirements.txt`** - Add `youtube-transcript-api` dependency

### **Evidence Deliverables:**
Developer MUST create these EXACT files:

1. [ ] **`SCRAPE-006B-phase1-research-report.md`**
   - **Contents:** Research findings on API vs UI approaches, recommendations
   - **Location:** `.coordination/deliverables/`
   - **How to create:** Test both approaches with sample videos, document findings
   - **Required:** API success rate, UI success rate, hybrid approach recommendation

2. [ ] **`SCRAPE-006B-api-test-results.json`**
   - **Contents:** Results from testing YouTube Transcript API with 10 videos
   - **Location:** `.coordination/testing/results/`
   - **Format:** `{"total": 10, "successful": 7, "failed": 3, "success_rate": 70.0, "videos": [...]}`

3. [ ] **`SCRAPE-006B-ui-test-results.json`**
   - **Contents:** Results from testing Playwright UI automation with 10 videos
   - **Location:** `.coordination/testing/results/`
   - **Format:** `{"total": 10, "successful": 5, "failed": 5, "success_rate": 50.0, "videos": [...]}`

4. [ ] **`SCRAPE-006B-hybrid-test-results.json`**
   - **Contents:** Results from testing hybrid approach with 20 videos
   - **Location:** `.coordination/testing/results/`
   - **Format:** `{"total": 20, "successful": 17, "failed": 3, "success_rate": 85.0, "api_used": 14, "ui_used": 6}`

5. [ ] **`SCRAPE-006B-edge-case-tests.json`**
   - **Contents:** Results from testing edge cases (no captions, private, etc.)
   - **Location:** `.coordination/testing/results/`
   - **Format:** `{"no_captions": "handled", "private_video": "handled", "rate_limit": "handled", ...}`

6. [ ] **`SCRAPE-006B-unit-test-output.txt`**
   - **Contents:** Complete pytest output for unit tests
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest tests/unit/test_transcript_extractor.py -v > SCRAPE-006B-unit-test-output.txt`

7. [ ] **`SCRAPE-006B-integration-test-output.txt`**
   - **Contents:** Complete pytest output for integration tests
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest tests/integration/test_transcript_extraction_real.py -v > SCRAPE-006B-integration-test-output.txt`

8. [ ] **`SCRAPE-006B-coverage-report.txt`**
   - **Contents:** Coverage report for transcript_extractor.py
   - **Location:** `.coordination/testing/results/`
   - **How to create:** `pytest --cov=src.scrapers.transcript_extractor --cov-report=term > SCRAPE-006B-coverage-report.txt`

9. [ ] **`SCRAPE-006B-performance-results.json`**
   - **Contents:** Performance metrics (timing, memory usage)
   - **Location:** `.coordination/testing/results/`
   - **Format:** `{"api_avg_time": 8.2, "ui_avg_time": 24.5, "memory_peak_mb": 350}`

10. [ ] **`SCRAPE-006B-evidence-summary.json`**
    - **Contents:** Summary of all metrics and requirements status
    - **Location:** `.coordination/testing/results/`
    - **Format:** See template below

### **Evidence Summary Template:**
```json
{
  "task_id": "SCRAPE-006B",
  "completion_date": "YYYY-MM-DD",
  "developer": "Dev2",
  "phase": "3-complete",
  "metrics": {
    "api_success_rate": 70.0,
    "ui_success_rate": 50.0,
    "hybrid_success_rate": 85.0,
    "total_videos_tested": 20,
    "successful_extractions": 17,
    "failed_extractions": 3,
    "unit_tests": 12,
    "integration_tests": 6,
    "tests_passing": 18,
    "coverage_percent": 88.5,
    "api_avg_time": 8.2,
    "ui_avg_time": 24.5
  },
  "requirements": {
    "api_implementation": "PASS",
    "ui_fallback": "PASS",
    "hybrid_success_rate": "PASS",
    "integration": "PASS",
    "error_handling": "PASS",
    "database_storage": "PASS",
    "performance": "PASS",
    "test_coverage": "PASS"
  },
  "evidence_files": [
    "SCRAPE-006B-phase1-research-report.md",
    "SCRAPE-006B-api-test-results.json",
    "SCRAPE-006B-ui-test-results.json",
    "SCRAPE-006B-hybrid-test-results.json",
    "SCRAPE-006B-edge-case-tests.json",
    "SCRAPE-006B-unit-test-output.txt",
    "SCRAPE-006B-integration-test-output.txt",
    "SCRAPE-006B-coverage-report.txt",
    "SCRAPE-006B-performance-results.json",
    "SCRAPE-006B-evidence-summary.json"
  ]
}
```

---

## 🔧 TECHNICAL IMPLEMENTATION GUIDANCE

### **Phase 1: Research & Evaluation (Day 1 - 4 hours)**

**Goal:** Understand YouTube Transcript API and UI automation approaches

**Tasks:**
1. Install and test `youtube-transcript-api` library
2. Test API with 10 sample videos from SCRAPE-006 results
3. Document API success rate and failure modes
4. Test Playwright UI automation for transcript extraction
5. Document UI success rate and complexity
6. Write research report with recommendations

**Deliverables:**
- `SCRAPE-006B-phase1-research-report.md`
- `SCRAPE-006B-api-test-results.json`
- `SCRAPE-006B-ui-test-results.json`

---

### **Phase 2: Implementation (Day 2 - 2 hours)**

**Goal:** Build working transcript extractor with hybrid approach

**Implementation Structure:**
```python
# src/scrapers/transcript_extractor.py

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from playwright.async_api import async_playwright
import asyncio
import logging

logger = logging.getLogger(__name__)

class TranscriptExtractor:
    """
    Extracts YouTube video transcripts using hybrid API + UI automation.
    
    Approach:
    1. Try YouTube Transcript API first (fast, reliable when captions exist)
    2. Fall back to Playwright UI automation if API fails
    3. Handle all edge cases gracefully (no captions, private videos, etc.)
    """
    
    def __init__(self, use_ui_fallback=True, timeout=30000):
        """
        Initialize transcript extractor.
        
        Args:
            use_ui_fallback: Whether to use Playwright fallback if API fails
            timeout: Timeout for UI automation in milliseconds
        """
        self.use_ui_fallback = use_ui_fallback
        self.timeout = timeout
        self.browser = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry - setup browser if UI fallback enabled."""
        if self.use_ui_fallback:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def extract_with_api(self, video_id: str) -> tuple[bool, str, str]:
        """
        Extract transcript using YouTube Transcript API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            (success, transcript_text, error_message)
        """
        try:
            # Try to get transcript (prefers English, falls back to any language)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try manual captions first (higher quality)
            try:
                transcript = transcript_list.find_manually_created_transcript(['en', 'en-US'])
            except:
                # Fall back to auto-generated captions
                transcript = transcript_list.find_generated_transcript(['en', 'en-US'])
            
            # Get transcript segments
            segments = transcript.fetch()
            
            # Combine all text segments
            full_text = ' '.join([segment['text'] for segment in segments])
            
            logger.info(f"API extraction successful for {video_id}: {len(full_text)} chars")
            return True, full_text.strip(), None
            
        except TranscriptsDisabled:
            error = f"Transcripts disabled for video {video_id}"
            logger.warning(error)
            return False, "", error
            
        except NoTranscriptFound:
            error = f"No transcript found for video {video_id}"
            logger.warning(error)
            return False, "", error
            
        except Exception as e:
            error = f"API extraction failed for {video_id}: {str(e)}"
            logger.error(error)
            return False, "", error
    
    async def extract_with_ui(self, video_url: str) -> tuple[bool, str, str]:
        """
        Extract transcript using Playwright UI automation.
        
        Args:
            video_url: Full YouTube video URL
            
        Returns:
            (success, transcript_text, error_message)
        """
        if not self.browser:
            return False, "", "UI fallback not enabled (no browser initialized)"
        
        try:
            page = await self.browser.new_page()
            
            try:
                # Navigate to video
                await page.goto(video_url, timeout=self.timeout)
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                # Click "Show more" if present
                try:
                    show_more = await page.wait_for_selector('[aria-label*="Show more"]', timeout=5000)
                    if show_more:
                        await show_more.click()
                        await asyncio.sleep(2)
                except:
                    pass
                
                # Click three dots menu
                more_button = await page.wait_for_selector(
                    'button[aria-label="More actions"]',
                    timeout=5000
                )
                await more_button.click()
                await asyncio.sleep(1)
                
                # Click "Show transcript"
                transcript_option = await page.wait_for_selector(
                    'button:has-text("Show transcript")',
                    timeout=3000
                )
                await transcript_option.click()
                await asyncio.sleep(3)
                
                # Wait for transcript panel
                await page.wait_for_selector('ytd-transcript-renderer', timeout=5000)
                
                # Extract transcript segments
                segments = await page.locator('ytd-transcript-segment-renderer .segment-text').all_text_contents()
                
                if segments:
                    full_text = ' '.join(segments)
                    logger.info(f"UI extraction successful: {len(full_text)} chars")
                    return True, full_text.strip(), None
                else:
                    return False, "", "No transcript segments found"
                    
            finally:
                await page.close()
                
        except Exception as e:
            error = f"UI extraction failed: {str(e)}"
            logger.error(error)
            return False, "", error
    
    async def extract_transcript(self, video_url: str, video_id: str) -> tuple[bool, str, str]:
        """
        Extract transcript using hybrid approach: API first, UI fallback.
        
        Args:
            video_url: Full YouTube video URL
            video_id: YouTube video ID
            
        Returns:
            (success, transcript_text, error_message)
        """
        # Try API first
        success, text, error = self.extract_with_api(video_id)
        
        if success:
            return True, text, None
        
        logger.info(f"API failed for {video_id}, trying UI fallback")
        
        # Try UI fallback if enabled
        if self.use_ui_fallback:
            success, text, error = await self.extract_with_ui(video_url)
            
            if success:
                return True, text, None
        
        # Both methods failed
        return False, "", error if error else "All extraction methods failed"
```

**Integration with multimodal_processor.py:**
```python
# In multimodal_processor.py, replace lines 372-459:

from src.scrapers.transcript_extractor import TranscriptExtractor

async def extract_video_transcript(self, video_url: str) -> tuple[bool, str, str]:
    """
    Extract video transcript using hybrid API + UI automation.
    
    Args:
        video_url: YouTube video URL
        
    Returns:
        (success, transcript_text, error_message)
    """
    try:
        video_id = self.extract_video_id_from_url(video_url)
        if not video_id:
            return False, "", "Could not extract video ID from URL"
        
        # Use TranscriptExtractor with hybrid approach
        async with TranscriptExtractor(use_ui_fallback=True) as extractor:
            success, transcript, error = await extractor.extract_transcript(video_url, video_id)
            return success, transcript, error
            
    except Exception as e:
        logger.error(f"Transcript extraction failed for {video_url}: {e}")
        return False, "", str(e)
```

---

### **Phase 3: Testing & Validation (Day 3 - 2 hours)**

**Goal:** Comprehensive testing to validate 80%+ success rate

**Unit Tests:**
```python
# tests/unit/test_transcript_extractor.py

import pytest
from src.scrapers.transcript_extractor import TranscriptExtractor

class TestTranscriptExtractor:
    """Unit tests for TranscriptExtractor."""
    
    def test_extractor_initialization(self):
        """Test extractor initializes with correct defaults."""
        extractor = TranscriptExtractor()
        assert extractor.use_ui_fallback == True
        assert extractor.timeout == 30000
    
    def test_extract_with_api_success(self):
        """Test API extraction with valid video ID."""
        extractor = TranscriptExtractor(use_ui_fallback=False)
        # Use known video with captions
        success, text, error = extractor.extract_with_api("dQw4w9WgXcQ")
        assert success == True
        assert len(text) > 0
        assert error is None
    
    def test_extract_with_api_no_captions(self):
        """Test API extraction handles videos without captions."""
        extractor = TranscriptExtractor(use_ui_fallback=False)
        # Use video known to have no captions
        success, text, error = extractor.extract_with_api("XXXXXX")
        assert success == False
        assert text == ""
        assert error is not None
    
    @pytest.mark.asyncio
    async def test_extract_with_ui_success(self):
        """Test UI extraction with valid video URL."""
        async with TranscriptExtractor() as extractor:
            url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            success, text, error = await extractor.extract_with_ui(url)
            # May succeed or fail depending on UI availability
            assert isinstance(success, bool)
    
    @pytest.mark.asyncio
    async def test_hybrid_approach_success(self):
        """Test hybrid approach with valid video."""
        async with TranscriptExtractor() as extractor:
            url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            video_id = "dQw4w9WgXcQ"
            success, text, error = await extractor.extract_transcript(url, video_id)
            assert success == True
            assert len(text) > 0
```

**Integration Tests:**
```python
# tests/integration/test_transcript_extraction_real.py

import pytest
from src.scrapers.transcript_extractor import TranscriptExtractor
from src.scrapers.multimodal_processor import MultimodalProcessor

class TestTranscriptExtractionIntegration:
    """Integration tests with real YouTube videos from workflows."""
    
    @pytest.mark.asyncio
    async def test_extract_from_workflow_6270(self):
        """Test transcript extraction from workflow 6270 video."""
        async with TranscriptExtractor() as extractor:
            # Real video from workflow 6270
            url = "https://www.youtube.com/watch?v=XXXXX"  # Replace with actual
            video_id = "XXXXX"
            success, text, error = await extractor.extract_transcript(url, video_id)
            assert success == True
            assert len(text) > 100  # Should have substantial content
    
    @pytest.mark.asyncio
    async def test_multimodal_processor_integration(self):
        """Test transcript extraction integrated with multimodal processor."""
        async with MultimodalProcessor(headless=True) as processor:
            url = "https://www.youtube.com/watch?v=XXXXX"
            success, text, error = await processor.extract_video_transcript(url)
            assert success == True or success == False  # Either outcome is valid
            if success:
                assert len(text) > 0
    
    @pytest.mark.asyncio
    async def test_hybrid_success_rate(self):
        """Test hybrid approach achieves 80%+ success rate."""
        test_videos = [
            # List of 20 real video URLs from SCRAPE-006 results
            "https://www.youtube.com/watch?v=VIDEO1",
            "https://www.youtube.com/watch?v=VIDEO2",
            # ... 18 more
        ]
        
        async with TranscriptExtractor() as extractor:
            successful = 0
            for url in test_videos:
                video_id = url.split("v=")[1]
                success, text, error = await extractor.extract_transcript(url, video_id)
                if success:
                    successful += 1
            
            success_rate = (successful / len(test_videos)) * 100
            assert success_rate >= 80.0, f"Success rate {success_rate}% below 80% target"
```

**Deliverables:**
- `SCRAPE-006B-hybrid-test-results.json`
- `SCRAPE-006B-edge-case-tests.json`
- `SCRAPE-006B-unit-test-output.txt`
- `SCRAPE-006B-integration-test-output.txt`
- `SCRAPE-006B-coverage-report.txt`
- `SCRAPE-006B-performance-results.json`
- `SCRAPE-006B-evidence-summary.json`

---

## 🔍 VALIDATION PROTOCOL

### **Developer Self-Validation (Before Submission):**

**Step 1: Verify API Implementation**
```bash
# Test API with sample videos
python -c "from src.scrapers.transcript_extractor import TranscriptExtractor; \
extractor = TranscriptExtractor(use_ui_fallback=False); \
success, text, error = extractor.extract_with_api('dQw4w9WgXcQ'); \
print(f'Success: {success}, Length: {len(text)}')"
```

**Step 2: Run Unit Tests**
```bash
# Must show 100% passing
pytest tests/unit/test_transcript_extractor.py -v
# Expected: 10-15 tests passing
```

**Step 3: Run Integration Tests**
```bash
# Must show ≥80% success rate
pytest tests/integration/test_transcript_extraction_real.py -v
# Expected: 5-8 tests passing
```

**Step 4: Check Coverage**
```bash
# Must show ≥85% coverage
pytest tests/unit/test_transcript_extractor.py --cov=src.scrapers.transcript_extractor --cov-report=term
```

**Step 5: Generate Evidence Files**
```bash
# Create all required evidence files
pytest tests/unit/test_transcript_extractor.py -v > .coordination/testing/results/SCRAPE-006B-unit-test-output.txt
pytest tests/integration/test_transcript_extraction_real.py -v > .coordination/testing/results/SCRAPE-006B-integration-test-output.txt
pytest --cov=src.scrapers.transcript_extractor --cov-report=term > .coordination/testing/results/SCRAPE-006B-coverage-report.txt
```

**Step 6: Verify Evidence Files Exist**
```bash
# Check all 10 evidence files created
ls -la .coordination/testing/results/SCRAPE-006B*
ls -la .coordination/deliverables/SCRAPE-006B*
# Expected: 10 files total
```

---

### **RND Manager Validation (Before PM Review):**

**Step 1: Verify Evidence Files (2 min)**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
ls -la .coordination/testing/results/SCRAPE-006B*
ls -la .coordination/deliverables/SCRAPE-006B*
# Expected: All 10 files present
# If missing: REJECT immediately
```

**Step 2: Run Tests Independently (5 min)**
```bash
source venv/bin/activate
pytest tests/unit/test_transcript_extractor.py tests/integration/test_transcript_extraction_real.py -v
# Expected: Same results as developer reported
# If different: REJECT
```

**Step 3: Verify Success Rate (2 min)**
```bash
cat .coordination/testing/results/SCRAPE-006B-hybrid-test-results.json
# Expected: success_rate ≥ 80.0
# If below: REJECT
```

**Step 4: Verify Coverage (2 min)**
```bash
pytest --cov=src.scrapers.transcript_extractor --cov-report=term
# Expected: ≥85% coverage
# If below: REJECT
```

**Step 5: Check Integration (3 min)**
```bash
# Verify lines 372-459 in multimodal_processor.py replaced
grep -A 10 "extract_video_transcript" src/scrapers/multimodal_processor.py
# Expected: New TranscriptExtractor integration
# If old code: REJECT
```

**RND Decision:**
- ✅ **APPROVE:** All checks pass → Forward to PM
- ❌ **REJECT:** Any check fails → Return to developer with specific issues

---

## 🚨 COMMON FAILURE MODES & PREVENTION

### **Failure Mode 1: "YouTube API rate limiting"**
**Prevention:** 
- Implement exponential backoff
- Use UI fallback when rate limited
- Test with reasonable request rate

### **Failure Mode 2: "UI automation brittle to YouTube changes"**
**Prevention:**
- Use multiple selector strategies
- Implement robust error handling
- Log all UI interaction failures
- Fall back gracefully

### **Failure Mode 3: "Success rate below 80%"**
**Prevention:**
- Test with diverse video set (captions vs no captions)
- Ensure both API and UI methods work
- Handle all edge cases gracefully
- Use realistic test videos from SCRAPE-006

### **Failure Mode 4: "Integration breaks multimodal_processor"**
**Prevention:**
- Test multimodal_processor after integration
- Maintain existing interface
- Don't break existing tests
- Run full test suite before submission

### **Failure Mode 5: "Tests pass but production fails"**
**Prevention:**
- Test with REAL videos from workflows
- Don't mock YouTube responses in integration tests
- Test edge cases (no captions, private, etc.)
- Validate performance under realistic conditions

---

## 💡 SUCCESS CRITERIA CHECKLIST

**Before marking ANY task as complete, verify:**

- [ ] YouTube Transcript API working (70%+ success rate)
- [ ] Playwright UI fallback working (50%+ success rate on API failures)
- [ ] Hybrid approach achieving 80%+ overall success rate
- [ ] Integration with multimodal_processor.py complete
- [ ] All edge cases handled gracefully
- [ ] Database storage working correctly
- [ ] Performance targets met (<10s API, <30s UI)
- [ ] Test coverage ≥85%
- [ ] Unit tests: 10-15 passing (100%)
- [ ] Integration tests: 5-8 passing (100%)
- [ ] All 10 evidence files created and verified
- [ ] RND independently verified (not just trusted developer)
- [ ] PM spot-checked (not just trusted RND)

**If ANY checkbox is unchecked → TASK NOT COMPLETE**

---

## 📅 3-PHASE DELIVERY SCHEDULE

### **Phase 1: Research & Evaluation (Day 1 - October 10, 2025)**
**Time:** 4 hours  
**Goal:** Understand approaches and recommend strategy

**Deliverables:**
- Research report with findings
- API test results (10 videos)
- UI test results (10 videos)
- Hybrid approach recommendation

**Exit Criteria:**
- Research report complete
- Both approaches tested
- Clear recommendation documented

---

### **Phase 2: Implementation (Day 2 - October 11, 2025)**
**Time:** 2 hours  
**Goal:** Build working transcript extractor

**Deliverables:**
- `transcript_extractor.py` complete
- Integration with `multimodal_processor.py`
- Basic tests passing
- `youtube-transcript-api` added to requirements

**Exit Criteria:**
- Code complete and working
- Integration functional
- Basic validation successful

---

### **Phase 3: Testing & Validation (Day 3 - October 13, 2025)**
**Time:** 2 hours  
**Goal:** Comprehensive testing and evidence generation

**Deliverables:**
- All 10 evidence files
- Hybrid test results (20 videos, 80%+ success)
- Unit + integration tests passing
- Coverage ≥85%
- Performance validation

**Exit Criteria:**
- 80%+ success rate achieved
- All tests passing
- All evidence files created
- Ready for RND validation

---

**This task assignment provides complete guidance for implementing YouTube transcript extraction.**

**Use it. Follow it. Achieve 80%+ success rate.**

---

**Version:** 1.0  
**Created:** October 10, 2025  
**Author:** RND Manager  
**Status:** Active - Awaiting Dev2 Start

