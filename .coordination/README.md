# 🎯 N8N Scraper - Coordination Directory

**Purpose:** Lightweight PM ↔ RND coordination for n8n scraping project  
**Project Duration:** 18 days (3 sprints)  
**Updated:** Daily by RND Developer

---

## 📂 Directory Structure

```
.coordination/
├── daily/              # Daily status and standup notes
│   ├── status.json    # Current sprint state (updated EOD)
│   ├── YYYYMMDD-standup.md  # Daily standup notes
│   └── blockers.json  # Active blockers tracking
│
├── handoffs/          # PM ↔ RND communication
│   ├── pm-to-rnd.md  # PM instructions to developer
│   ├── rnd-to-pm.md  # Developer updates to PM
│   └── decisions.md  # Key decisions log
│
├── testing/           # Test coordination
│   ├── test-plan.json        # Test scenarios
│   ├── results/              # Daily test results
│   └── quality-gates.json    # Gate status tracking
│
├── metrics/           # Performance tracking
│   ├── extraction-times.csv  # Actual performance data
│   ├── success-rates.csv     # Success rate tracking
│   └── sprint-progress.json  # Sprint burndown
│
└── deliverables/      # Final outputs staging
    ├── dataset-samples/     # Sample extractions
    ├── quality-reports/     # Quality analysis
    └── final-package/       # Ready for delivery
```

---

## 🔄 Daily Workflow

### Morning (9:00 AM) - PM
1. Read `daily/status.json`
2. Read `handoffs/rnd-to-pm.md`
3. Review yesterday's test results
4. Update `handoffs/pm-to-rnd.md` with priorities
5. Quick Slack check-in with RND

### During Day - RND Developer
1. Read `handoffs/pm-to-rnd.md`
2. Execute tasks per task list
3. Run tests continuously
4. Log metrics automatically
5. Flag blockers via Slack immediately

### Evening (6:00 PM) - RND Developer
1. Update `handoffs/rnd-to-pm.md`
2. Update `daily/status.json`
3. Create daily standup note
4. Save test results to `testing/results/`
5. Push code + coordination files to git

---

## 📊 Key Files

### Must Update Daily (EOD):
- `daily/status.json` - Current state
- `handoffs/rnd-to-pm.md` - Developer updates
- `daily/YYYYMMDD-standup.md` - Standup notes
- `testing/results/YYYYMMDD-test-summary.json` - Test results

### Updated by PM (Morning):
- `handoffs/pm-to-rnd.md` - Next priorities

### Updated Weekly:
- `metrics/sprint-progress.json` - Sprint burndown
- `handoffs/decisions.md` - Key decisions

---

## ✅ Quality Gates

**Gate 1:** Day 2 - Basic Functionality  
**Gate 2:** Day 7 - Core Features Complete  
**Gate 3:** Day 10 - Integration Ready  
**Gate 4:** Day 15 - Production Ready  
**Gate 5:** Day 18 - Delivery Ready

See `testing/quality-gates.json` for criteria.

---

## 🚨 Blocker Protocol

If blocked:
1. Log in `daily/blockers.json`
2. Update `handoffs/rnd-to-pm.md`
3. Slack PM immediately
4. Document workaround attempts

---

## 📝 Notes

- This is a **lightweight** coordination structure for an 18-day RND project
- Focus on **evidence-based** updates (metrics, test results)
- Keep coordination overhead **minimal** (<30 min/day)
- All files should be **git-tracked** for history

---

**Last Updated:** October 9, 2025  
**Version:** 1.0
