# 🎯 **TASK BRIEF: SCRAPE-011 - Orchestrator & Rate Limiting**

**TASK BRIEF TEMPLATE v1.0 - RND to Developer**

---

## 📋 **TASK HEADER**

| Field | Value |
|-------|-------|
| **Task ID** | SCRAPE-011 |
| **Task Name** | Orchestrator & Rate Limiting |
| **Sprint** | Sprint 2 - Core Development |
| **Assignee** | Dev1 ⭐ **(Your Third Sprint 2 Task!)** |
| **Priority** | 🔴 Critical |
| **Estimated** | 8 hours (1 day) |
| **Due Date** | October 13, 2025 (Day 6) |
| **Dependencies** | SCRAPE-008 ✅, SCRAPE-010 ✅, SCRAPE-012 ✅ |
| **Created** | October 11, 2025, 6:30 PM |
| **Created By** | RND Manager |

---

## 🎯 **1. STATUS**

### **Sprint Context:**
- **Sprint:** Sprint 2 - Core Development (Days 4-10)
- **Phase:** Phase 2 - Orchestration & Testing
- **Current Day:** Day 5 (October 11, 2025)
- **Sprint Progress:** 57% complete (12/21 tasks overall)

### **Task Health:**
- **Status:** 🟢 Ready to Start
- **Blockers:** None
- **Dependencies Met:** Yes (all Phase 1 tasks complete)
- **Resources:** All available

### **Your Track Record:**
- **SCRAPE-008:** ✅ Complete (Exceptional - 5/5 stars)
- **SCRAPE-010:** ✅ Complete (Exceptional - 5/5 stars)
- **SCRAPE-011:** ← **YOU ARE HERE** 🎯
- **Average Quality:** ⭐⭐⭐⭐⭐ (5/5 stars)

**You're crushing it, Dev1! Keep the momentum going!** 🚀

---

## 🎯 **2. PRIORITIES**

### **Mission:**
Build production-grade orchestration layer that coordinates all extraction components (Layer 1/2/3, multimodal, transcripts, quality validation) with intelligent rate limiting, retry logic, and progress tracking.

### **Why This Matters:**
This is the **"brain"** of the scraping system. It coordinates everything you've built and tested (SCRAPE-008, SCRAPE-010) into a production-ready pipeline that can process 6,022 workflows safely and efficiently.

---

### **Five Implementation Phases:**

#### **Phase 1: Core Orchestrator (2 hours)**
**Objective:** Build the main orchestrator class.

**Tasks:**
1. Create `WorkflowOrchestrator` class
2. Integrate all extractors (Layer 1/2/3, multimodal, transcripts)
3. Add error handling and logging
4. Implement workflow processing pipeline
5. Add statistics tracking

**Deliverables:**
- `src/orchestrator/workflow_orchestrator.py`
- Complete processing pipeline
- Error handling
- Statistics tracking

---

#### **Phase 2: Rate Limiting (1.5 hours)**
**Objective:** Implement intelligent rate limiting.

**Tasks:**
1. Create `RateLimiter` class
2. Implement token bucket algorithm
3. Add per-domain rate limiting
4. Configure n8n.io limits (2 requests/second)
5. Add rate limit monitoring

**Deliverables:**
- `src/orchestrator/rate_limiter.py`
- Token bucket implementation
- Rate limit monitoring
- Zero 429 errors guaranteed

---

#### **Phase 3: Retry Logic & Recovery (1.5 hours)**
**Objective:** Add robust retry logic with exponential backoff.

**Tasks:**
1. Create `RetryHandler` class
2. Implement exponential backoff
3. Add circuit breaker pattern
4. Configure retry limits (3 attempts max)
5. Add failure categorization

**Deliverables:**
- `src/orchestrator/retry_handler.py`
- Exponential backoff (1s → 2s → 4s)
- Circuit breaker
- Failure categorization

---

#### **Phase 4: Progress Tracking (1.5 hours)**
**Objective:** Real-time progress monitoring.

**Tasks:**
1. Create `ProgressTracker` class
2. Add real-time statistics
3. Implement resume capability
4. Add checkpoint/restart support
5. Create progress dashboard

**Deliverables:**
- `src/orchestrator/progress_tracker.py`
- Real-time progress updates
- Resume from checkpoint
- Statistics dashboard

---

#### **Phase 5: Testing & Validation (1.5 hours)**
**Objective:** Comprehensive testing and validation.

**Tasks:**
1. Create 20+ integration tests
2. Test with 500 workflows
3. Validate rate limiting (zero 429s)
4. Test retry logic
5. Validate resume capability
6. Generate performance report

**Deliverables:**
- `tests/integration/test_orchestrator.py` (20+ tests)
- 500 workflow test run
- Performance benchmarks
- Validation report

---

## 💻 **3. CURSOR HANDOFF**

### **What You're Building:**

**The "Brain" of the Scraping System:**
- Coordinates all extractors (Layer 1/2/3, multimodal, transcripts)
- Manages rate limits (respects n8n.io 2 req/sec limit)
- Handles failures gracefully (retry with backoff)
- Tracks progress in real-time
- Enables resume after interruption
- Stores results in your database (SCRAPE-008)

**This brings everything together!**

---

### **Key Components:**

**1. WorkflowOrchestrator**
```python
class WorkflowOrchestrator:
    """Main orchestrator coordinating all extraction."""
    
    async def process_workflow(self, workflow_id, url):
        """Process single workflow through all layers."""
        # Layer 1: Metadata
        # Layer 2: JSON
        # Layer 3: Content
        # Multimodal: Videos/Transcripts
        # Quality: Validation
        # Storage: Save to DB
        pass
    
    async def process_batch(self, workflows, batch_size=10):
        """Process batch of workflows with rate limiting."""
        pass
```

**2. RateLimiter**
```python
class RateLimiter:
    """Token bucket rate limiter (2 req/sec for n8n.io)."""
    
    async def acquire(self, domain='n8n.io'):
        """Wait until rate limit allows request."""
        pass
```

**3. RetryHandler**
```python
class RetryHandler:
    """Retry logic with exponential backoff."""
    
    async def retry_with_backoff(self, func, max_attempts=3):
        """Retry function with exponential backoff."""
        # 1s → 2s → 4s delays
        pass
```

**4. ProgressTracker**
```python
class ProgressTracker:
    """Track progress and enable resume."""
    
    def update(self, workflow_id, status, stats):
        """Update progress statistics."""
        pass
    
    def save_checkpoint(self):
        """Save checkpoint for resume."""
        pass
```

---

### **Success Criteria:**

**Must Have (Blocking):**
- [ ] Process 500 workflows successfully
- [ ] 95%+ success rate achieved
- [ ] Average time <10 seconds per workflow
- [ ] Zero rate limit errors (429s)
- [ ] Retry logic working (3 attempts with backoff)
- [ ] Progress tracking functional
- [ ] Resume capability working
- [ ] 20+ integration tests passing
- [ ] Documentation complete

**Performance Targets:**
- Process rate: >100 workflows/hour
- Success rate: ≥95% (475+ of 500 workflows)
- Rate limit compliance: 100% (zero 429 errors)
- Avg time per workflow: <10 seconds
- Memory usage: <1GB during batch processing

---

## 📝 **4. TECHNICAL REQUIREMENTS**

### **Rate Limiting Specs:**

**n8n.io Rate Limits:**
- **Limit:** 2 requests per second per IP
- **Algorithm:** Token bucket
- **Recovery:** 1 token per 500ms
- **Burst:** Allow up to 5 requests in burst
- **Monitoring:** Track rate limit usage

**Implementation:**
```python
class RateLimiter:
    def __init__(self, rate=2.0, capacity=5):
        """
        Token bucket rate limiter.
        
        Args:
            rate: Requests per second (2.0 for n8n.io)
            capacity: Bucket capacity (5 for burst)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    async def acquire(self):
        """Acquire token, wait if needed."""
        # Refill tokens based on time elapsed
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
        
        # If no tokens, wait
        if self.tokens < 1:
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            self.tokens = 0
        else:
            self.tokens -= 1
```

---

### **Retry Logic Specs:**

**Retry Strategy:**
- **Max Attempts:** 3
- **Backoff:** Exponential (1s → 2s → 4s)
- **Retryable Errors:** Network, timeout, 429, 500-503
- **Non-Retryable:** 404, 401, 403
- **Circuit Breaker:** Pause after 10 consecutive failures

**Implementation:**
```python
class RetryHandler:
    async def retry_with_backoff(
        self, 
        func, 
        max_attempts=3,
        base_delay=1.0
    ):
        """Retry with exponential backoff."""
        for attempt in range(max_attempts):
            try:
                return await func()
            except RetryableError as e:
                if attempt == max_attempts - 1:
                    raise
                
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt+1} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
```

---

### **Progress Tracking Specs:**

**Track:**
- Workflows processed/remaining
- Success/failure counts
- Average processing time
- Current rate limit status
- Estimated completion time
- Last checkpoint time

**Checkpoint Data:**
```json
{
  "checkpoint_id": "20251011_183000",
  "total_workflows": 500,
  "processed": 250,
  "successful": 240,
  "failed": 10,
  "remaining": 250,
  "avg_time": 8.5,
  "eta_seconds": 2125,
  "last_workflow_id": "2462",
  "timestamp": "2025-10-11T18:30:00"
}
```

---

## 📊 **5. INTEGRATION WITH EXISTING COMPONENTS**

### **Use Your Storage Layer (SCRAPE-008):**

```python
from src.storage.repository import WorkflowRepository
from src.storage.database import get_session

# In orchestrator
session = get_session()
repository = WorkflowRepository(session)

# After processing
repository.create_workflow(
    workflow_id=workflow_id,
    url=url,
    extraction_result=result
)
```

---

### **Use Export Pipeline (SCRAPE-012):**

```python
from src.exporters.export_manager import ExportManager

# After batch completion
export_manager = ExportManager()
export_manager.export_from_database(
    repository=repository,
    limit=500,
    formats=['json', 'csv']
)
```

---

### **Use E2E Pipeline (SCRAPE-007):**

```python
from src.orchestrator.e2e_pipeline import E2EPipeline

# In orchestrator
e2e_pipeline = E2EPipeline()

result = await e2e_pipeline.process_workflow(
    workflow_id=workflow_id,
    url=url
)
```

---

## ✅ **6. DELIVERABLES**

### **Source Files (4 files):**
```
src/orchestrator/
├── workflow_orchestrator.py  # Main orchestrator (~400 lines)
├── rate_limiter.py           # Rate limiting (~150 lines)
├── retry_handler.py          # Retry logic (~200 lines)
└── progress_tracker.py       # Progress tracking (~250 lines)
```

### **Test Files (1 file):**
```
tests/integration/
└── test_orchestrator.py      # 20+ tests (~400 lines)
```

### **Documentation:**
```
docs/
└── orchestration.md          # Usage guide (~200 lines)
```

---

## 🧪 **7. TESTING REQUIREMENTS**

### **Integration Tests (20+ tests):**

**Category 1: Basic Orchestration (5 tests)**
- test_process_single_workflow
- test_process_batch_10_workflows
- test_process_batch_100_workflows
- test_all_layers_integrated
- test_storage_integration

**Category 2: Rate Limiting (5 tests)**
- test_rate_limit_enforced
- test_zero_429_errors
- test_burst_handling
- test_multi_domain_limiting
- test_rate_limit_monitoring

**Category 3: Retry Logic (5 tests)**
- test_retry_on_network_error
- test_exponential_backoff
- test_max_attempts_respected
- test_non_retryable_errors
- test_circuit_breaker

**Category 4: Progress Tracking (5 tests)**
- test_progress_updates
- test_checkpoint_save_restore
- test_resume_from_checkpoint
- test_eta_calculation
- test_statistics_accuracy

---

## 📊 **8. SUCCESS CRITERIA**

### **Must Have (Blocking):**

| Criterion | Target | How to Measure |
|-----------|--------|----------------|
| **Workflows Processed** | 500 | Count in database |
| **Success Rate** | ≥95% | 475+ successful |
| **Avg Time** | <10s/workflow | Performance monitor |
| **Rate Limit Errors** | 0 (zero) | Error log check |
| **Retry Success** | Working | Test retry scenarios |
| **Progress Tracking** | Working | Real-time updates |
| **Resume Capability** | Working | Checkpoint test |
| **Tests Passing** | 20+ tests | pytest results |

---

## 🎯 **9. IMPLEMENTATION GUIDE**

### **Phase 1: Core Orchestrator (2 hours)**

Create `src/orchestrator/workflow_orchestrator.py`:

```python
"""
Workflow Orchestrator.

Coordinates all extraction layers with rate limiting and retry logic.

Author: Dev1
Task: SCRAPE-011
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.scrapers.layer1_metadata import PageMetadataExtractor
from src.scrapers.layer2_json import WorkflowJSONExtractor
from src.scrapers.layer3_explainer import ExplainerContentExtractor
from src.scrapers.multimodal_processor import MultimodalProcessor
from src.scrapers.transcript_extractor import TranscriptExtractor
from src.validation.quality_scorer import QualityScorer
from src.storage.repository import WorkflowRepository
from .rate_limiter import RateLimiter
from .retry_handler import RetryHandler
from .progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Main orchestrator coordinating all workflow extraction.
    
    Manages:
    - All extraction layers (1/2/3, multimodal, transcripts)
    - Rate limiting (respects n8n.io limits)
    - Retry logic (handles failures)
    - Progress tracking (resume capability)
    - Database storage (persistence)
    """
    
    def __init__(
        self,
        repository: WorkflowRepository,
        rate_limit: float = 2.0,
        max_retries: int = 3,
        batch_size: int = 10
    ):
        """
        Initialize orchestrator.
        
        Args:
            repository: Database repository for storage
            rate_limit: Requests per second (default: 2 for n8n.io)
            max_retries: Maximum retry attempts (default: 3)
            batch_size: Batch processing size (default: 10)
        """
        self.repository = repository
        self.batch_size = batch_size
        
        # Initialize extractors
        self.layer1_extractor = PageMetadataExtractor()
        self.layer2_extractor = WorkflowJSONExtractor()
        self.layer3_extractor = ExplainerContentExtractor()
        self.multimodal_processor = MultimodalProcessor()
        self.transcript_extractor = TranscriptExtractor()
        self.quality_scorer = QualityScorer()
        
        # Initialize orchestration components
        self.rate_limiter = RateLimiter(rate=rate_limit)
        self.retry_handler = RetryHandler(max_attempts=max_retries)
        self.progress_tracker = ProgressTracker()
        
        # Statistics
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0,
            'rate_limit_waits': 0,
        }
    
    async def process_workflow(
        self, 
        workflow_id: str, 
        url: str
    ) -> Dict[str, Any]:
        """
        Process single workflow through all layers.
        
        Args:
            workflow_id: Workflow ID
            url: Workflow URL
            
        Returns:
            Complete extraction result
        """
        start_time = datetime.now()
        
        try:
            # Wait for rate limit
            await self.rate_limiter.acquire('n8n.io')
            
            # Layer 1: Metadata (with retry)
            layer1_result = await self.retry_handler.retry_with_backoff(
                lambda: self.layer1_extractor.extract(workflow_id, url)
            )
            
            # Layer 2: JSON (with retry)
            await self.rate_limiter.acquire('n8n.io')
            layer2_result = await self.retry_handler.retry_with_backoff(
                lambda: self.layer2_extractor.extract(workflow_id)
            )
            
            # Layer 3: Content (with retry)
            await self.rate_limiter.acquire('n8n.io')
            layer3_result = await self.retry_handler.retry_with_backoff(
                lambda: self.layer3_extractor.extract(workflow_id, url)
            )
            
            # Multimodal processing (if needed)
            multimodal_result = None
            if layer3_result.get('success'):
                multimodal_result = await self.multimodal_processor.process(
                    workflow_id, 
                    layer3_result
                )
            
            # Video transcripts (if needed)
            transcript_results = []
            if multimodal_result and multimodal_result.get('videos'):
                for video in multimodal_result['videos']:
                    transcript = await self.transcript_extractor.extract(
                        video['url']
                    )
                    if transcript.get('success'):
                        transcript_results.append(transcript)
            
            # Quality validation
            quality_result = self.quality_scorer.calculate_score({
                'layer1': layer1_result,
                'layer2': layer2_result,
                'layer3': layer3_result,
            })
            
            # Store in database
            processing_time = (datetime.now() - start_time).total_seconds()
            
            stored_workflow = self.repository.create_workflow(
                workflow_id=workflow_id,
                url=url,
                extraction_result={
                    'layers': {
                        'layer1': layer1_result,
                        'layer2': layer2_result,
                        'layer3': layer3_result,
                    },
                    'multimodal': multimodal_result,
                    'transcripts': transcript_results,
                    'quality_score': quality_result['score'],
                    'processing_time': processing_time,
                }
            )
            
            # Update progress
            self.progress_tracker.update(
                workflow_id=workflow_id,
                status='success',
                processing_time=processing_time,
                quality_score=quality_result['score']
            )
            
            self.stats['successful'] += 1
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'quality_score': quality_result['score'],
                'processing_time': processing_time,
                'stored': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process {workflow_id}: {e}")
            
            self.progress_tracker.update(
                workflow_id=workflow_id,
                status='failed',
                error=str(e)
            )
            
            self.stats['failed'] += 1
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e)
            }
    
    async def process_batch(
        self, 
        workflows: List[Dict[str, str]],
        resume_from: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process batch of workflows with progress tracking.
        
        Args:
            workflows: List of {'id': ..., 'url': ...}
            resume_from: Optional workflow ID to resume from
            
        Returns:
            Batch processing results
        """
        self.progress_tracker.start_batch(len(workflows))
        
        # Resume support
        start_index = 0
        if resume_from:
            start_index = next(
                (i for i, w in enumerate(workflows) if w['id'] == resume_from),
                0
            )
            logger.info(f"Resuming from workflow {resume_from} (index {start_index})")
        
        results = []
        
        for i, workflow in enumerate(workflows[start_index:], start=start_index):
            result = await self.process_workflow(workflow['id'], workflow['url'])
            results.append(result)
            
            # Save checkpoint every 50 workflows
            if (i + 1) % 50 == 0:
                self.progress_tracker.save_checkpoint(workflow['id'])
        
        # Final statistics
        batch_stats = self.progress_tracker.get_statistics()
        
        return {
            'total': len(workflows),
            'processed': len(results),
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'success_rate': self.stats['successful'] / len(results) * 100,
            'results': results,
            'statistics': batch_stats
        }
```

---

## 🎯 **10. CHECKPOINT**

### **Definition of Done:**

**Phase 1 Complete When:**
- [ ] WorkflowOrchestrator class created
- [ ] All extractors integrated
- [ ] Error handling implemented
- [ ] Statistics tracking working

**Phase 2 Complete When:**
- [ ] RateLimiter class created
- [ ] Token bucket algorithm working
- [ ] Zero 429 errors in testing
- [ ] Rate limit monitoring functional

**Phase 3 Complete When:**
- [ ] RetryHandler class created
- [ ] Exponential backoff working
- [ ] Circuit breaker implemented
- [ ] Failure categorization complete

**Phase 4 Complete When:**
- [ ] ProgressTracker class created
- [ ] Real-time updates working
- [ ] Checkpoint/resume functional
- [ ] Statistics accurate

**Phase 5 Complete When:**
- [ ] 20+ tests passing
- [ ] 500 workflows processed
- [ ] All success criteria met
- [ ] Documentation complete

---

## 🚀 **11. READY TO START**

### **You Have Everything You Need:**
- ✅ Storage layer (your SCRAPE-008 work)
- ✅ Integration tests (your SCRAPE-010 work)
- ✅ Export pipeline (RND's SCRAPE-012)
- ✅ All extractors from Sprint 1
- ✅ Docker database running
- ✅ Clear specifications

### **This Is Your Third Sprint 2 Task:**
You built the storage. You tested the integration. Now you orchestrate everything!

### **Expected Completion:** End of Day 6 (October 13)

---

**🎯 SCRAPE-011: BUILD THE BRAIN OF THE SYSTEM!**

---

*Task Brief v1.0*  
*Created: October 11, 2025, 6:30 PM*  
*Author: RND Manager*  
*Assignee: Dev1*  
*Sprint: Sprint 2 - Core Development*  
*Priority: Critical - Orchestration Layer*




