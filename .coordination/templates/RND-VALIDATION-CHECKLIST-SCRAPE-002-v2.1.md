# ✅ **RND VALIDATION CHECKLIST: SCRAPE-002 v2.1**

**Task:** SCRAPE-002 v2.1 (10 Sales Workflows)  
**Developer:** Dev1  
**RND Manager:** [My name]  
**Validation Date:** [When I validate]  
**Method:** Zero-trust independent verification

---

## 🎯 **VALIDATION PROTOCOL**

**Time Required:** 10-15 minutes  
**Approach:** Run every command myself, trust nothing  
**Scope:** 10 specific sales/lead gen workflows

---

## ✅ **STEP 1: Evidence Files Exist (2 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Check all evidence files
ls -la .coordination/testing/results/SCRAPE-002*

# Check sample folder
ls .coordination/testing/results/SCRAPE-002-sample-extractions/
```

**Expected:**
- [ ] `SCRAPE-002-test-output.txt` exists
- [ ] `SCRAPE-002-coverage-report.txt` exists
- [ ] `SCRAPE-002-10-workflow-summary.json` exists
- [ ] `SCRAPE-002-sample-extractions/` folder exists
- [ ] `SCRAPE-002-database-query.txt` exists
- [ ] `SCRAPE-002-evidence-summary.json` exists
- **Total:** 6 files/folders must exist

**Check sample folder:**
```bash
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l
# Must show exactly 10
```
- [ ] Sample folder has EXACTLY 10 workflow files

**Decision:**
- ✅ **All 6 files exist AND folder has 10 files** → Continue to Step 2
- ❌ **ANY file missing OR folder ≠10 files** → **INSTANT REJECT**

**My Verification:**
- Files found: ___/6
- Sample files: ___/10
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
- Tests: ___ (from evidence summary)

**My Verification:**
- Tests I counted: ___
- All passing: ✅ YES / ❌ NO
- Match: ✅ YES / ❌ NO

**Decision:**
- ✅ **35+ tests, all pass, matches claim** → Continue to Step 3
- ❌ **<35 OR any fail OR doesn't match** → **INSTANT REJECT**

**My Result:**
- Tests: ___
- Passing: ✅/❌
- Matches: ✅/❌
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
- Line: `src/scrapers/layer1_metadata.py  XXX  XXX  XX.XX%`

**Expected:**
- [ ] Coverage ≥ 80.00%

**Dev1's Claim:**
- Coverage: ___% (from evidence summary)

**My Verification:**
- Coverage I measured: ___%
- Match: ✅ YES / ❌ NO

**Decision:**
- ✅ **≥80% AND matches claim** → Continue to Step 4
- ❌ **<80% OR doesn't match** → **INSTANT REJECT**

**My Result:**
- Coverage: ___%
- Meets 80%: ✅/❌
- Matches: ✅/❌
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 4: Verify Database Has All 10 Target Workflows (2 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Query for the 10 specific workflow IDs
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');"
```

**Expected:**
- [ ] Result shows exactly 10

**Dev1's Claim:**
- Workflows: ___ (from summary JSON)

**My Verification:**
- Database count: ___
- Specific IDs check: ✅ YES / ❌ NO

**Also verify specific IDs exist:**
```bash
# List all 10 to ensure they're the right ones
sqlite3 data/workflows.db "SELECT workflow_id FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145') ORDER BY workflow_id;"
```
- [ ] All 10 IDs present: 1756, 1832, 1923, 1954, 2087, 2103, 2145, 2156, 2234, 2462

**Decision:**
- ✅ **Database has all 10 specific IDs AND matches claim** → Continue to Step 5
- ❌ **<10 OR wrong IDs OR doesn't match** → **INSTANT REJECT**

**My Result:**
- Workflows in DB: ___
- Correct IDs: ✅/❌
- Matches: ✅/❌
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
- [ ] extract_10_workflows: "PASS"
- [ ] success_rate_90_percent: "PASS"
- [ ] zero_failures: "PASS"
- [ ] coverage_80_percent: "PASS"
- [ ] tests_35_minimum: "PASS"
- [ ] tests_100_percent_pass: "PASS"
- [ ] all_required_fields: "PASS"
- [ ] rate_limiting_2sec: "PASS"
- [ ] database_storage: "PASS"

**Check metrics match my verification:**
- [ ] total_tests matches Step 2
- [ ] coverage_percent matches Step 3
- [ ] total_workflows = 10 and matches Step 4

**Decision:**
- ✅ **All PASS AND metrics match** → Continue to Step 6
- ❌ **Any FAIL OR discrepancies** → **INSTANT REJECT**

**My Result:**
- Requirements PASS: ✅/❌
- Metrics match: ✅/❌
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 6: Verify All 10 Workflow Files (3 min)**

**Action:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Count sample files (must be exactly 10)
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l

# Check specific files exist for all 10 IDs
ls .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_2462.json
ls .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_1954.json
ls .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_2103.json
# ... etc for all 10

# Review 3-4 random samples
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_2462.json
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_2087.json
```

**Expected:**
- [ ] Exactly 10 files (not 9, not 11)
- [ ] Files named: workflow_2462.json, workflow_1954.json, etc. (matching target IDs)
- [ ] Each contains valid JSON
- [ ] Real n8n.io URLs present
- [ ] All 6 required fields in each: workflow_id, title, url, author, created_date, category
- [ ] Data looks reasonable (not gibberish)

**Decision:**
- ✅ **10 files, all target IDs, valid data** → Continue to Step 7
- ❌ **≠10 files OR wrong IDs OR incomplete data** → **INSTANT REJECT**

**My Result:**
- Sample files: ___/10
- Correct IDs: ✅/❌
- Required fields: ✅/❌
- Status: ✅ PASS / ❌ FAIL

---

## ✅ **STEP 7: Compare Claimed vs Actual (2 min)**

**Action:**
Create comparison table:

| Metric | Dev1 Claimed | I Verified | Match? |
|--------|--------------|------------|--------|
| Tests | ___ | ___ | ✅/❌ |
| Coverage | ___% | ___% | ✅/❌ |
| Workflows | 10 | ___ | ✅/❌ |
| Success Rate | ___% | ___% | ✅/❌ |
| Evidence Files | 6 | ___ | ✅/❌ |
| Sample Files | 10 | ___ | ✅/❌ |

**Decision:**
- ✅ **All match (within ±0.5%)** → APPROVE
- ❌ **Any don't match** → **INSTANT REJECT**

**My Result:**
- All metrics match: ✅ YES / ❌ NO
- Discrepancies: [List any]
- Status: ✅ PASS / ❌ FAIL

---

## 📊 **FINAL DECISION**

### **All 7 Steps Results:**

- Step 1 (Evidence exists + 10 files): ✅ PASS / ❌ FAIL
- Step 2 (Tests ≥35, all pass): ✅ PASS / ❌ FAIL
- Step 3 (Coverage ≥80%): ✅ PASS / ❌ FAIL
- Step 4 (Database has 10 specific IDs): ✅ PASS / ❌ FAIL
- Step 5 (Evidence summary accurate): ✅ PASS / ❌ FAIL
- Step 6 (All 10 workflow files valid): ✅ PASS / ❌ FAIL
- Step 7 (Numbers match): ✅ PASS / ❌ FAIL

**Total:** ___/7 PASS

---

### **RND MANAGER DECISION:**

**If 7/7 PASS:**
- ✅ **APPROVE**
- Create: `RND-TO-PM-SCRAPE-002-APPROVED.md`
- Include: All verification results, all metrics, confidence level
- Forward to PM for final approval
- Note: Validated on 10 sales workflows, ready for SCRAPE-002B scale

**If ANY step FAILS:**
- ❌ **REJECT**
- Create: `RND-TO-DEV1-SCRAPE-002-REJECTION-v2.1.md`
- Include: Specific failures, evidence, exact fixes needed
- Deadline: 12-24 hours
- Warning: Third submission - task may be reassigned

---

## 📋 **VERIFICATION COMMANDS (Quick Reference)**

```bash
# Setup
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
source venv/bin/activate

# 1. Check evidence files
ls -la .coordination/testing/results/SCRAPE-002*
ls .coordination/testing/results/SCRAPE-002-sample-extractions/ | wc -l

# 2. Run tests
pytest tests/unit/test_layer1_metadata.py tests/integration/test_layer1_integration.py -v

# 3. Check coverage
pytest tests/unit/test_layer1_metadata.py --cov=src.scrapers.layer1_metadata --cov-report=term-missing

# 4. Check database
sqlite3 data/workflows.db "SELECT COUNT(*) FROM workflows WHERE workflow_id IN ('2462','1954','2103','2234','1756','1832','2156','1923','2087','2145');"

# 5. Read evidence summary
cat .coordination/testing/results/SCRAPE-002-evidence-summary.json

# 6. Spot-check samples
cat .coordination/testing/results/SCRAPE-002-sample-extractions/workflow_2462.json

# 7. Compare all numbers
```

---

## ⏱️ **VALIDATION TIMELINE**

**When Dev1 submits:** Notification received  
**My validation:** 10-15 minutes (run all 7 steps)  
**Decision:** Within 30 minutes of submission  
**If approved:** Forward to PM immediately  
**If rejected:** Detailed feedback to Dev1 within 30 minutes  

---

## ✅ **SCOPE NOTE**

**This validation is for 10 workflows only** (not 50).

**Key differences from original:**
- Workflows: 10 specific IDs (not 50 random)
- Sample files: Must have all 10 (not subset)
- Database: Must have these 10 specific IDs
- Success: 10/10 = 100% or 9/10 = 90%

**Future:** SCRAPE-002B will scale to full production

---

**RND Manager**  
**Checklist Version:** 2.1 (Updated for 10 workflows)  
**For Task:** SCRAPE-002 v2.1  
**Status:** Ready to use when Dev1 submits

