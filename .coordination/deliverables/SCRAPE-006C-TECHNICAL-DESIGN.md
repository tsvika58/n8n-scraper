# 📋 **SCRAPE-006C: TECHNICAL DESIGN DOCUMENT**

**Task:** SCRAPE-006C - Layer 2 Fallback Extractor (by-id API)  
**Author:** RND Manager  
**Date:** October 11, 2025  
**Status:** Design Complete - Awaiting PM Approval

---

## 🎯 **OBJECTIVE**

Implement fallback mechanism for Layer 2 JSON extraction using alternative n8n.io endpoint (`/api/workflows/by-id/{id}`) when primary API (`api.n8n.io/api/workflows/templates/{id}`) returns 404.

**Goal:** Increase Layer 2 success rate from 62% to ~90%.

---

## 📊 **SUCCESS CRITERIA**

### **Primary Success Criteria:**

| Criterion | Target | How to Measure |
|-----------|--------|----------------|
| **1. Fallback Success Rate** | ≥75% of failed workflows | Test on 19 workflows that currently fail |
| **2. Data Quality** | ≥80% of primary API data | Compare node counts, metadata completeness |
| **3. Performance** | <5s per workflow | Measure extraction time for fallback |
| **4. Integration** | 100% E2E compatible | Runs without breaking existing pipeline |
| **5. Test Coverage** | ≥85% code coverage | Unit + integration tests |

### **Secondary Success Criteria:**

| Criterion | Target | How to Measure |
|-----------|--------|----------------|
| **6. Documentation** | Complete | All methods documented, usage guide exists |
| **7. Error Handling** | Graceful degradation | No crashes on edge cases |
| **8. Data Marking** | Clear partial flag | Can distinguish full vs partial data |
| **9. Logging** | Comprehensive | All fallback attempts logged |
| **10. Backwards Compatible** | 100% | Existing Layer 2 extractions still work |

---

## 🏗️ **TECHNICAL ARCHITECTURE**

### **Current Architecture (SCRAPE-003):**

```
WorkflowJSONExtractor.extract(workflow_id)
    ↓
Try: api.n8n.io/api/workflows/templates/{id}
    ↓
Success? → Return full JSON
    ↓
Failure? → Return error (404)
```

### **Enhanced Architecture (SCRAPE-006C):**

```
WorkflowJSONExtractor.extract(workflow_id)
    ↓
[PRIMARY] Try: api.n8n.io/api/workflows/templates/{id}
    ↓
Success? → Return full JSON (type: "full")
    ↓
Failure (404)?
    ↓
[FALLBACK] Try: n8n.io/api/workflows/by-id/{id}
    ↓
Success? → Transform & Return partial JSON (type: "partial")
    ↓
Failure? → Return error (both methods failed)
```

---

## 📁 **FILE STRUCTURE**

### **Files to Modify:**

1. **`src/scrapers/layer2_json.py`** (Main implementation)
   - Add fallback logic
   - Add data transformation
   - Add type marking

2. **`tests/unit/test_layer2_json.py`** (Unit tests)
   - Test fallback logic
   - Test data transformation
   - Test error handling

3. **`tests/integration/test_layer2_json_real.py`** (NEW - Integration tests)
   - Test with real failed workflows
   - Test fallback success rate
   - Test data quality

### **Files to Create:**

4. **`docs/LAYER2_FALLBACK_DESIGN.md`** (Design documentation)
   - Architecture explanation
   - Data format comparison
   - Usage examples

5. **`.coordination/testing/results/SCRAPE-006C-test-results.json`** (Evidence)
   - Test results
   - Success metrics
   - Before/after comparison

---

## 🔧 **DETAILED IMPLEMENTATION DESIGN**

### **1. Enhanced WorkflowJSONExtractor Class**

```python
class WorkflowJSONExtractor:
    """
    Extracts complete workflow JSON from n8n.io using official API
    with fallback to by-id endpoint for unavailable templates.
    """
    
    def __init__(self):
        self.primary_api_base = "https://api.n8n.io/api/workflows/templates"
        self.fallback_api_base = "https://n8n.io/api/workflows/by-id"
        self.extraction_count = 0
        self.fallback_count = 0
        logger.info("Layer 2 JSON Extractor initialized with fallback support")
    
    async def extract(self, workflow_id: str) -> Dict[str, Any]:
        """
        Extract workflow JSON with automatic fallback.
        
        Returns:
            dict with keys:
                - success: bool
                - workflow_id: str
                - data: dict (workflow JSON if successful)
                - extraction_type: str ("full" | "partial" | "none")
                - node_count: int
                - connection_count: int
                - extraction_time: float
                - error: str or None
                - fallback_used: bool
        """
        start_time = datetime.now()
        
        # Try primary API first
        primary_result = await self._extract_from_primary_api(workflow_id)
        
        if primary_result['success']:
            primary_result['fallback_used'] = False
            primary_result['extraction_type'] = 'full'
            return primary_result
        
        # Primary failed, try fallback
        logger.info(f"Primary API failed for {workflow_id}, trying fallback...")
        fallback_result = await self._extract_from_fallback_api(workflow_id)
        
        if fallback_result['success']:
            self.fallback_count += 1
            fallback_result['fallback_used'] = True
            fallback_result['extraction_type'] = 'partial'
            logger.info(f"Fallback succeeded for {workflow_id}")
            return fallback_result
        
        # Both failed
        logger.warning(f"Both APIs failed for {workflow_id}")
        return {
            'success': False,
            'workflow_id': workflow_id,
            'data': None,
            'extraction_type': 'none',
            'node_count': 0,
            'connection_count': 0,
            'extraction_time': (datetime.now() - start_time).total_seconds(),
            'error': f"Primary: {primary_result['error']}, Fallback: {fallback_result['error']}",
            'fallback_used': True
        }
```

---

### **2. Fallback API Method**

```python
async def _extract_from_fallback_api(self, workflow_id: str) -> Dict[str, Any]:
    """
    Extract workflow data from fallback by-id endpoint.
    
    Returns partial data (node list, metadata) when primary API unavailable.
    """
    start_time = datetime.now()
    
    try:
        api_url = f"{self.fallback_api_base}/{workflow_id}"
        logger.debug(f"Trying fallback API: {api_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    by_id_data = await response.json()
                    
                    # Transform by-id format to template format
                    transformed_data = self._transform_by_id_to_template(by_id_data)
                    
                    extraction_time = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"✅ Fallback API succeeded for {workflow_id}: "
                              f"{len(by_id_data.get('nodes', []))} nodes, "
                              f"{extraction_time:.2f}s")
                    
                    return {
                        'success': True,
                        'workflow_id': workflow_id,
                        'data': transformed_data,
                        'node_count': len(by_id_data.get('nodes', [])),
                        'connection_count': 0,  # Not available in by-id
                        'extraction_time': extraction_time,
                        'error': None,
                        'source': 'fallback_by_id'
                    }
                
                elif response.status == 404:
                    logger.warning(f"Fallback API: Workflow {workflow_id} not found (404)")
                    return {
                        'success': False,
                        'workflow_id': workflow_id,
                        'data': None,
                        'node_count': 0,
                        'connection_count': 0,
                        'extraction_time': (datetime.now() - start_time).total_seconds(),
                        'error': 'Workflow not found in fallback API (404)',
                        'source': 'fallback_by_id'
                    }
                
                else:
                    logger.error(f"Fallback API error: HTTP {response.status}")
                    return {
                        'success': False,
                        'workflow_id': workflow_id,
                        'data': None,
                        'node_count': 0,
                        'connection_count': 0,
                        'extraction_time': (datetime.now() - start_time).total_seconds(),
                        'error': f'HTTP {response.status}',
                        'source': 'fallback_by_id'
                    }
    
    except asyncio.TimeoutError:
        return {
            'success': False,
            'workflow_id': workflow_id,
            'data': None,
            'node_count': 0,
            'connection_count': 0,
            'extraction_time': (datetime.now() - start_time).total_seconds(),
            'error': 'Timeout accessing fallback API',
            'source': 'fallback_by_id'
        }
    
    except Exception as e:
        return {
            'success': False,
            'workflow_id': workflow_id,
            'data': None,
            'node_count': 0,
            'connection_count': 0,
            'extraction_time': (datetime.now() - start_time).total_seconds(),
            'error': f'Exception: {str(e)}',
            'source': 'fallback_by_id'
        }
```

---

### **3. Data Transformation Method**

```python
def _transform_by_id_to_template(self, by_id_data: Dict) -> Dict:
    """
    Transform by-id API format to template API format.
    
    by-id format:
    {
        "id": 2462,
        "name": "...",
        "nodes": ["nodeType1", "nodeType2", ...],  // Just type strings
        "description": "...",
        ...
    }
    
    template format:
    {
        "id": 2462,
        "name": "...",
        "workflow": {
            "nodes": [
                {"id": "...", "name": "...", "type": "nodeType1", ...}
            ],
            "connections": {...}
        }
    }
    """
    
    # Extract node types from by-id format
    node_types = by_id_data.get('nodes', [])
    
    # Create synthetic workflow structure
    synthetic_nodes = []
    for i, node_type in enumerate(node_types):
        synthetic_nodes.append({
            "id": f"synthetic_{i}",
            "name": node_type.split('.')[-1],  # Extract node name
            "type": node_type,
            "position": [100 * i, 100],  # Dummy positions
            "parameters": {},  # Empty (not available)
            "synthetic": True  # Mark as synthetic
        })
    
    # Create transformed structure matching template format
    transformed = {
        "id": by_id_data.get('id'),
        "name": by_id_data.get('name'),
        "description": by_id_data.get('description', ''),
        "workflow": {
            "meta": {
                "instanceId": "fallback",
                "templateId": str(by_id_data.get('id'))
            },
            "nodes": synthetic_nodes,
            "connections": {},  # Empty (not available in by-id)
            "settings": {},
            "staticData": None
        },
        # Additional by-id specific data
        "views": by_id_data.get('views', 0),
        "recentViews": by_id_data.get('recentViews', 0),
        "categories": by_id_data.get('categories', []),
        "usedCredentials": by_id_data.get('usedCredentials', []),
        "communityNodes": by_id_data.get('communityNodes', []),
        "nonNativeNodes": by_id_data.get('nonNativeNodes', []),
        "user": by_id_data.get('user', {}),
        
        # Metadata about extraction
        "_metadata": {
            "extraction_type": "partial",
            "source": "by_id_api",
            "limitations": [
                "Node parameters not available",
                "Connections not available",
                "Node positions synthetic",
                "Node configurations missing"
            ]
        }
    }
    
    return transformed
```

---

### **4. Statistics Tracking**

```python
def get_statistics(self) -> Dict[str, Any]:
    """Get extraction statistics including fallback usage."""
    return {
        'total_extractions': self.extraction_count,
        'fallback_used_count': self.fallback_count,
        'fallback_usage_rate': (self.fallback_count / self.extraction_count * 100) 
                                if self.extraction_count > 0 else 0,
        'primary_api_base': self.primary_api_base,
        'fallback_api_base': self.fallback_api_base
    }
```

---

## 🧪 **TESTING STRATEGY**

### **Phase 1: Unit Tests** (15 tests minimum)

**File:** `tests/unit/test_layer2_json.py`

#### **Test Suite 1: Fallback Logic (5 tests)**
1. `test_primary_success_no_fallback()` - Primary succeeds, fallback not called
2. `test_primary_404_fallback_called()` - Primary fails, fallback attempted
3. `test_primary_404_fallback_success()` - Primary fails, fallback succeeds
4. `test_both_fail()` - Both APIs fail, proper error returned
5. `test_fallback_timeout()` - Fallback times out gracefully

#### **Test Suite 2: Data Transformation (5 tests)**
6. `test_transform_by_id_to_template()` - Correct structure transformation
7. `test_transform_preserves_metadata()` - Metadata preserved
8. `test_transform_creates_synthetic_nodes()` - Synthetic nodes created
9. `test_transform_marks_limitations()` - Limitations documented
10. `test_transform_handles_empty_nodes()` - Empty node list handled

#### **Test Suite 3: Error Handling (5 tests)**
11. `test_fallback_network_error()` - Network errors handled
12. `test_fallback_invalid_json()` - Invalid JSON handled
13. `test_fallback_missing_fields()` - Missing fields handled
14. `test_fallback_malformed_response()` - Malformed responses handled
15. `test_statistics_tracking()` - Statistics tracked correctly

---

### **Phase 2: Integration Tests** (10 workflows minimum)

**File:** `tests/integration/test_layer2_json_real.py`

#### **Test Suite 1: Real Failed Workflows (5-10 workflows)**

Test with actual workflows that currently return 404 from primary API:

```python
FAILED_WORKFLOWS = [
    '2021', '1847', '2091', '1925', '2134', 
    '1912', '1865', '1948', '1834', '1974'
]

@pytest.mark.asyncio
async def test_fallback_on_real_failed_workflows():
    """Test fallback on workflows that fail primary API."""
    extractor = WorkflowJSONExtractor()
    
    results = []
    for workflow_id in FAILED_WORKFLOWS:
        result = await extractor.extract(workflow_id)
        results.append(result)
    
    # Calculate success rate
    successful = sum(1 for r in results if r['success'])
    success_rate = successful / len(results) * 100
    
    # Should achieve ≥75% success with fallback
    assert success_rate >= 75, f"Fallback success rate {success_rate}% below 75% target"
```

#### **Test Suite 2: Data Quality Comparison (3 tests)**

16. `test_fallback_data_completeness()` - Fallback data has required fields
17. `test_fallback_vs_primary_comparison()` - Compare when both available
18. `test_fallback_node_count_accuracy()` - Node counts match

#### **Test Suite 3: E2E Integration (2 tests)**

19. `test_e2e_pipeline_with_fallback()` - Works in E2E pipeline
20. `test_e2e_improved_success_rate()` - Success rate improved

---

### **Phase 3: Performance Tests** (3 tests)

**File:** `tests/performance/test_layer2_performance.py`

21. `test_fallback_performance()` - Fallback completes in <5s
22. `test_fallback_memory_usage()` - No memory leaks
23. `test_batch_processing_with_fallback()` - Batch processing works

---

## 📊 **VALIDATION METRICS**

### **Before SCRAPE-006C (Baseline):**

| Metric | Value | Source |
|--------|-------|--------|
| Layer 2 Success Rate | 62% (31/50) | SCRAPE-007 test results |
| Failed Workflows | 19/50 (38%) | SCRAPE-007 test results |
| Node Data Coverage | 31 workflows | SCRAPE-007 test results |
| Avg Extraction Time | 0.35s | SCRAPE-007 test results |

---

### **After SCRAPE-006C (Target):**

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Layer 2 Success Rate | **≥90%** (45/50) | Rerun same 50 workflows |
| Failed Workflows | **≤5** (10%) | Count failures in rerun |
| Node Data Coverage | **≥45** workflows | Count successful extractions |
| Fallback Success Rate | **≥75%** of failed | 14+ of 19 previously failed |
| Avg Extraction Time | **<1s** | Should stay fast |
| Fallback Avg Time | **<5s** | Measure fallback only |

---

### **Success Validation Checklist:**

- [ ] **Fallback Logic:** ≥75% of previously failed workflows now succeed
- [ ] **Data Quality:** Transformed data has all required fields
- [ ] **Performance:** Fallback completes in <5s per workflow
- [ ] **Integration:** E2E pipeline Layer 2 success rate ≥90%
- [ ] **Test Coverage:** ≥85% code coverage achieved
- [ ] **Documentation:** Complete usage guide and API docs
- [ ] **Error Handling:** No crashes on any test cases
- [ ] **Backwards Compatibility:** Existing extractions still work

---

## 🔄 **INTEGRATION PLAN**

### **Step 1: Code Integration** (0.5 hours)

1. **Update `layer2_json.py`:**
   - Add fallback methods
   - Add transformation logic
   - Add statistics tracking
   - Maintain backwards compatibility

2. **Version Control:**
   ```bash
   git checkout -b feature/scrape-006c-layer2-fallback
   git add src/scrapers/layer2_json.py
   git commit -m "Add Layer 2 fallback extractor (SCRAPE-006C)"
   ```

3. **Code Review:**
   - RND Manager reviews implementation
   - Check against design doc
   - Verify all methods implemented

---

### **Step 2: Testing Integration** (1 hour)

1. **Run Unit Tests:**
   ```bash
   pytest tests/unit/test_layer2_json.py -v
   # Expected: 15/15 tests passing
   ```

2. **Run Integration Tests:**
   ```bash
   pytest tests/integration/test_layer2_json_real.py -v
   # Expected: ≥75% fallback success rate
   ```

3. **Generate Coverage Report:**
   ```bash
   pytest tests/unit/test_layer2_json.py --cov=src.scrapers.layer2_json --cov-report=term
   # Expected: ≥85% coverage
   ```

---

### **Step 3: E2E Pipeline Integration** (0.5 hours)

1. **Update E2E Pipeline:**
   - No changes needed (uses existing Layer 2 interface)
   - Fallback is transparent to pipeline

2. **Validate E2E Compatibility:**
   ```bash
   python -c "from src.orchestrator.e2e_pipeline import E2EPipeline; \
              from src.scrapers.layer2_json import WorkflowJSONExtractor; \
              print('✅ Integration successful')"
   ```

3. **Test Single Workflow:**
   ```python
   # Test with previously failed workflow
   pipeline = E2EPipeline()
   result = await pipeline.process_workflow("2021", "https://n8n.io/workflows/2021")
   
   # Should now succeed with fallback
   assert result['layers']['layer2']['success'] == True
   assert result['layers']['layer2']['fallback_used'] == True
   ```

---

### **Step 4: Rerun SCRAPE-007** (0.5 hours)

1. **Execute Full E2E Test:**
   ```bash
   python test_e2e_50workflows.py
   # Expected: Layer 2 success ≥90% (was 62%)
   ```

2. **Compare Results:**
   ```python
   # Load before/after results
   before = load_json(".coordination/testing/results/SCRAPE-007-test-results.json")
   after = load_json(".coordination/testing/results/SCRAPE-007-RERUN-test-results.json")
   
   # Calculate improvement
   before_success = before['summary']['layer2_success_rate']  # 62%
   after_success = after['summary']['layer2_success_rate']    # Target: ≥90%
   
   improvement = after_success - before_success
   print(f"Improvement: +{improvement}% Layer 2 success rate")
   ```

3. **Generate Comparison Report:**
   - Before/after metrics
   - Fallback usage statistics
   - Data quality comparison
   - Performance impact

---

### **Step 5: Documentation** (0.5 hours)

1. **Update README:**
   - Document fallback feature
   - Add usage examples
   - Note limitations

2. **Create Design Doc:**
   - Architecture explanation
   - Data format comparison
   - API endpoint documentation

3. **Update CHANGELOG:**
   ```markdown
   ## [1.1.0] - 2025-10-11
   ### Added
   - Layer 2 fallback extractor using /api/workflows/by-id endpoint
   - Automatic fallback when primary API returns 404
   - Data transformation from by-id to template format
   - Statistics tracking for fallback usage
   
   ### Improved
   - Layer 2 success rate: 62% → 90%
   - Workflow coverage: +28% (+14 workflows)
   ```

---

### **Step 6: Deployment Readiness** (0.5 hours)

1. **Final Validation:**
   - [ ] All tests passing
   - [ ] Coverage ≥85%
   - [ ] E2E Layer 2 success ≥90%
   - [ ] Documentation complete
   - [ ] No regressions

2. **Create Evidence Package:**
   ```
   .coordination/testing/results/SCRAPE-006C-evidence/
   ├── test-results.json
   ├── coverage-report.txt
   ├── before-after-comparison.md
   ├── fallback-statistics.json
   └── performance-metrics.txt
   ```

3. **Completion Report:**
   - Create `rnd-to-pm-SCRAPE-006C-COMPLETION.md`
   - Include all metrics
   - Document limitations
   - Provide recommendations

---

## 📋 **ACCEPTANCE CRITERIA**

### **Must Have (Blocking):**

- [ ] **Primary Success Criterion:** ≥75% of previously failed workflows now succeed
- [ ] **Integration:** Works in E2E pipeline without breaking existing functionality
- [ ] **Performance:** Fallback completes in <5s per workflow
- [ ] **Test Coverage:** ≥85% code coverage
- [ ] **Documentation:** Complete usage guide and limitations documented

### **Should Have (Important):**

- [ ] **Data Quality:** ≥80% data completeness vs primary API
- [ ] **E2E Improvement:** Layer 2 success rate ≥90% in E2E test
- [ ] **Error Handling:** Graceful degradation on all edge cases
- [ ] **Logging:** Comprehensive logging of fallback attempts
- [ ] **Statistics:** Fallback usage tracking implemented

### **Nice to Have (Optional):**

- [ ] **Performance:** Fallback <3s (vs <5s target)
- [ ] **Success Rate:** ≥80% fallback success (vs ≥75% target)
- [ ] **E2E Success:** ≥95% Layer 2 success (vs ≥90% target)
- [ ] **Documentation:** Video walkthrough of fallback mechanism
- [ ] **Monitoring:** Dashboard showing fallback usage over time

---

## 🚨 **RISKS & MITIGATION**

### **Risk 1: Fallback API May Be Unstable**
- **Likelihood:** Medium
- **Impact:** High (fallback fails)
- **Mitigation:**
  - Document endpoint thoroughly
  - Add retry logic with exponential backoff
  - Log all failures for analysis
  - Monitor in production

### **Risk 2: Data Transformation May Lose Information**
- **Likelihood:** Certain (by design)
- **Impact:** Medium (partial data)
- **Mitigation:**
  - Clearly mark as "partial" extraction
  - Document all limitations in metadata
  - Preserve all available data
  - Provide comparison with full data

### **Risk 3: May Not Achieve 75% Fallback Success**
- **Likelihood:** Low
- **Impact:** Medium (miss target)
- **Mitigation:**
  - Test on real failed workflows early
  - Adjust target if needed (≥60% still valuable)
  - Document actual success rate honestly
  - Communicate to PM if below target

### **Risk 4: Performance Degradation**
- **Likelihood:** Low
- **Impact:** Low (still within budget)
- **Mitigation:**
  - Fallback only on 404 (not every request)
  - Timeout fallback at 10s
  - Use async for parallel processing
  - Monitor extraction times

---

## 📊 **SUCCESS METRICS SUMMARY**

### **Primary Metrics:**

| Metric | Current | Target | Measurement Method |
|--------|---------|--------|-------------------|
| **Fallback Success Rate** | N/A | **≥75%** | Test on 19 failed workflows |
| **E2E Layer 2 Success** | 62% | **≥90%** | Rerun 50-workflow E2E test |
| **Data Coverage** | 31 workflows | **≥45** | Count successful extractions |
| **Performance** | 0.35s | **<5s** | Measure fallback extraction time |
| **Test Coverage** | 0% | **≥85%** | Run coverage report |

### **Validation Checklist:**

- [ ] 14+ of 19 failed workflows now succeed with fallback
- [ ] E2E test shows ≥90% Layer 2 success
- [ ] Fallback extractions complete in <5s
- [ ] Code coverage ≥85%
- [ ] All tests passing (unit + integration)
- [ ] Documentation complete
- [ ] No regressions in existing functionality
- [ ] Evidence package created
- [ ] Completion report submitted

---

## ✅ **DELIVERABLES CHECKLIST**

### **Code Files:**
- [ ] `src/scrapers/layer2_json.py` (enhanced)
- [ ] `tests/unit/test_layer2_json.py` (15+ tests)
- [ ] `tests/integration/test_layer2_json_real.py` (10+ tests)

### **Documentation:**
- [ ] `docs/LAYER2_FALLBACK_DESIGN.md`
- [ ] Updated README.md with fallback feature
- [ ] Updated CHANGELOG.md

### **Evidence:**
- [ ] `.coordination/testing/results/SCRAPE-006C-test-results.json`
- [ ] `.coordination/testing/results/SCRAPE-006C-coverage-report.txt`
- [ ] `.coordination/testing/results/SCRAPE-006C-before-after.md`

### **Reports:**
- [ ] `.coordination/handoffs/dev1-to-rnd-SCRAPE-006C-COMPLETION.md`
- [ ] `.coordination/handoffs/rnd-to-pm-SCRAPE-006C-VALIDATION.md`

---

## 🎯 **READY FOR IMPLEMENTATION**

**This technical design is complete and ready for:**
1. ✅ PM approval
2. ✅ Task brief creation
3. ✅ Developer assignment
4. ✅ Implementation start

**Estimated Timeline:**
- Research & Design: 1 hour
- Implementation: 2 hours
- Testing: 1.5 hours
- Integration: 0.5 hours
- **Total: 5 hours**

---

**Technical Design Complete**  
**Status:** Awaiting PM Approval  
**Author:** RND Manager  
**Date:** October 11, 2025

🚀 **Ready to build upon approval!**
