# ✅ **RND VALIDATION CHECKLIST: SCRAPE-002**

**Task:** SCRAPE-002 Rework  
**Developer:** Dev1  
**RND Manager:** [My name]  
**Validation Date:** [When I validate]  
**Method:** Zero-trust independent verification

---

## 🎯 **VALIDATION PROTOCOL**

**Time Required:** 10-15 minutes  
**Approach:** Run every command myself, trust nothing

---

## ✅ **STEP 1: Evidence Files Exist (2 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Check all evidence files
ls -la .coordination/testing/results/SCRAPE-002*
```

**Expected:**
- [ ] `SCRAPE-002-test-output.txt` exists
- [ ] `SCRAPE-002-coverage-report.txt` exists
- [ ] `SCRAPE-002-50-workflow-summary.json` exists
- [ ] `SCRAPE-002-sample-extractions/` folder exists
- [ ] `SCRAPE-002-database-query.txt` exists
- [ ] `SCRAPE-002-evidence-summary.json` exists
- **Total:** 6+ files must exist

**Decision:**
- ✅ **All files exist** → Continue to Step 2
- ❌ **ANY file missing** → **INSTANT REJECT** (return to Dev1 immediately)

**My Verification:**
- Files found: ___/6+
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 2: Run Tests Independently (3-5 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate

# Run tests and WATCH them execute
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v
```

**Watch for:**
- Each test name and PASSED status
- Final summary line

**Expected:**
- [ ] At least 35 tests run
- [ ] All tests PASSED
- [ ] No failures, no errors, no skips
- [ ] Final line: `XX passed, 0 failed` where XX ≥ 35

**Dev1's Claim:**
- Tests: ___ (from their evidence summary)

**My Verification:**
- Tests I counted: ___
- Match: ✅ YES / ❌ NO

**Decision:**
- ✅ **35+ tests, all pass, matches claim** → Continue to Step 3
- ❌ **<35 tests OR any fail OR doesn't match** → **INSTANT REJECT**

**My Result:**
- Tests found: ___
- All passing: ✅ YES / ❌ NO
- Matches claim: ✅ YES / ❌ NO
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 3: Verify Coverage Independently (1-2 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate

# Run coverage and WATCH output
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing
```

**Watch for:**
- Line showing: `src/scrapers/layer1_metadata.py  XXX  XXX  XX.XX%`

**Expected:**
- [ ] Coverage percentage ≥ 80.00%

**Dev1's Claim:**
- Coverage: ___% (from their evidence summary)

**My Verification:**
- Coverage I measured: ___%
- Match: ✅ YES / ❌ NO

**Decision:**
- ✅ **≥80% AND matches claim** → Continue to Step 4
- ❌ **<80% OR doesn't match** → **INSTANT REJECT**

**My Result:**
- Coverage found: ___%
- Meets 80%: ✅ YES / ❌ NO
- Matches claim: ✅ YES / ❌ NO
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 4: Verify Database Records (2 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Query database for workflow count
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows;"
```

**Expected:**
- [ ] Result shows 50 or higher

**Dev1's Claim:**
- Workflows: ___ (from their summary JSON)

**My Verification:**
- Database count: ___
- Match: ✅ YES / ❌ NO

**Decision:**
- ✅ **≥50 AND matches claim** → Continue to Step 5
- ❌ **<50 OR doesn't match** → **INSTANT REJECT**

**Additional Check:**
```bash
# Check database query file matches
cat .coordination/testing/results/SCRAPE-002-database-query.txt | wc -l
# Should show 50+ rows
```

**My Result:**
- Workflows in DB: ___
- Meets 50+: ✅ YES / ❌ NO
- Matches claim: ✅ YES / ❌ NO
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 5: Check Evidence Summary (2 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Read evidence summary
cat .coordination/testing/results/SCRAPE-002-evidence-summary.json
```

**Verify all requirements show "PASS":**
- [ ] extract_50_plus_workflows: "PASS"
- [ ] success_rate_90_percent: "PASS"
- [ ] zero_complete_failures: "PASS"
- [ ] coverage_80_percent: "PASS"
- [ ] tests_35_minimum: "PASS"
- [ ] tests_100_percent_pass: "PASS"
- [ ] all_fields_extracted: "PASS"
- [ ] pagination_working: "PASS"
- [ ] rate_limiting_2sec: "PASS"
- [ ] database_storage: "PASS"
- [ ] notion_updated: "PASS"

**Check metrics match my verification:**
- [ ] total_tests matches Step 2
- [ ] coverage_percent matches Step 3
- [ ] workflows count matches Step 4

**Decision:**
- ✅ **All PASS AND metrics match** → Continue to Step 6
- ❌ **Any FAIL OR discrepancies** → **INSTANT REJECT**

**My Result:**
- All requirements PASS: ✅ YES / ❌ NO
- Metrics match verification: ✅ YES / ❌ NO
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 6: Spot-Check Sample Extractions (3 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Count sample files
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l

# Review 3 random samples
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_*.json
```

**Expected:**
- [ ] At least 5 sample files exist
- [ ] Each contains valid JSON
- [ ] Real n8n.io URLs (https://n8n.io/workflows/XXXX)
- [ ] All 6 required fields present (workflow_id, title, url, author, created_date, category)
- [ ] Data looks reasonable (not gibberish)

**Decision:**
- ✅ **5+ samples, real data, all fields** → Continue to Step 7
- ❌ **<5 samples OR fake/incomplete data** → **INSTANT REJECT**

**My Result:**
- Sample files found: ___
- Real n8n.io data: ✅ YES / ❌ NO
- Required fields present: ✅ YES / ❌ NO
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 7: Compare Claimed vs Actual (2 min)**

**Action:**
Create comparison table:

| Metric | Dev1 Claimed | I Verified | Match? |
|--------|--------------|------------|--------|
| Tests | ___ | ___ | ✅/❌ |
| Coverage | ___% | ___% | ✅/❌ |
| Workflows | ___ | ___ | ✅/❌ |
| Success Rate | ___% | ___% | ✅/❌ |
| Evidence Files | ___ | ___ | ✅/❌ |

**Decision:**
- ✅ **All match (within ±1%)** → APPROVE
- ❌ **Any don't match** → **INSTANT REJECT**

**My Result:**
- All metrics match: ✅ YES / ❌ NO
- Discrepancies: [List any]
- Status: ✅ PASS / ❌ FAIL

---

## 📊 **FINAL DECISION**

### **All 7 Steps Results:**

- Step 1 (Evidence exists): ✅ PASS / ❌ FAIL
- Step 2 (Tests pass): ✅ PASS / ❌ FAIL
- Step 3 (Coverage): ✅ PASS / ❌ FAIL
- Step 4 (Database): ✅ PASS / ❌ FAIL
- Step 5 (Evidence summary): ✅ PASS / ❌ FAIL
- Step 6 (Sample quality): ✅ PASS / ❌ FAIL
- Step 7 (Numbers match): ✅ PASS / ❌ FAIL

**Total:** ___/7 PASS

---

### **RND MANAGER DECISION:**

**If 7/7 PASS:**
- ✅ **APPROVE**
- Create: `RND-TO-PM-SCRAPE-002-APPROVED.md`
- Include: All verification results, metrics, confidence level
- Forward to PM for final approval

**If ANY step FAILS:**
- ❌ **REJECT**
- Create: `RND-TO-DEV1-SCRAPE-002-REJECTION-v2.md`
- Include: Specific failures, evidence of discrepancies, exact rework needed
- Return to Dev1 with 12-24 hour deadline

---

## 📋 **APPROVAL DOCUMENT TEMPLATE**

**If I approve, I'll create:**

```markdown
# RND TO PM: SCRAPE-002 APPROVED

Task: SCRAPE-002 Rework
Developer: Dev1
RND Decision: ✅ APPROVED

## Independent Verification Results:

Tests: Verified 38/38 passing (claimed 38) ✅
Coverage: Verified 84.2% (claimed 84.2%) ✅
Workflows: Verified 52 in database (claimed 52) ✅
Success Rate: Verified 100.0% (claimed 100.0%) ✅
Evidence Files: Verified all 6 exist ✅
Notion: Verified completely updated ✅

All 8 validation steps PASSED.
All claims verified accurate.
Ready for PM final approval.

Confidence: 95% production-ready
```

---

## 📋 **REJECTION DOCUMENT TEMPLATE**

**If I reject, I'll create:**

```markdown
# RND TO DEV1: SCRAPE-002 REJECTION v2

Task: SCRAPE-002 Rework
RND Decision: ❌ REJECTED

## Issues Found:

Issue #1: [Specific problem]
- Claimed: [X]
- Actual: [Y]
- Gap: [X-Y]

Issue #2: [Specific problem]
- Evidence: [What I found]
- Requirement: [What was needed]

## Rework Required:
1. Fix [specific issue]
2. Fix [specific issue]
3. Resubmit by [deadline]

This is second rejection. Task may be reassigned if not fixed.
```

---

## ⏱️ **VALIDATION TIMELINE**

**When Dev1 submits:** Notification received  
**My validation:** 10-15 minutes (run all 8 steps)  
**Decision:** APPROVE or REJECT  
**Communication:** Within 30 minutes of submission  
**If approved:** Forward to PM immediately  
**If rejected:** Detailed feedback to Dev1 immediately  

---

## ✅ **READY TO VALIDATE**

This checklist will be used when Dev1 submits SCRAPE-002 rework.

**I commit to:**
- Run all 8 steps independently
- Watch all tests execute myself
- Verify every claim
- Compare all numbers
- No shortcuts
- Only approve if 8/8 PASS
- Instant reject if any fail

**This protects project quality and ensures only verified work reaches PM.**

---

**RND Manager**  
**Checklist Version:** 1.0  
**For Task:** SCRAPE-002 Rework  
**Status:** Ready to use when Dev1 submits

