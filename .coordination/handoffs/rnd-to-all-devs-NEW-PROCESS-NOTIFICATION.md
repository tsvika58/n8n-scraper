# 📢 **IMPORTANT: NEW TASK PROCESS & TEMPLATES**

**FROM:** RND Manager  
**TO:** Developer-1 (Dev1) & Developer-2 (Dev2)  
**DATE:** October 10, 2025, 12:05 AM  
**SUBJECT:** New Task Assignment Process - Effective Immediately  
**PRIORITY:** CRITICAL - READ BEFORE STARTING ANY NEW WORK

---

## 🚨 **IMPORTANT CHANGES**

We are implementing a new, clearer task assignment and validation process to prevent the issues we've experienced with SCRAPE-001, 002, and 005.

**This affects how you receive tasks, execute them, and submit work.**

---

## 🎯 **WHAT'S CHANGING**

### **Old Process (Problems):**
- ❌ Vague requirements
- ❌ Unclear acceptance criteria
- ❌ No standard evidence format
- ❌ Inconsistent validation
- ❌ Confusion about "done"
- ❌ False/incomplete reports reaching PM

### **New Process (Solutions):**
- ✅ Crystal-clear requirements
- ✅ Exact acceptance criteria with verification commands
- ✅ Standardized evidence files
- ✅ Three-layer validation (Dev → RND → PM)
- ✅ No ambiguity about completion
- ✅ Only verified work reaches PM

---

## 📋 **NEW TEMPLATES IN USE**

### **1. PM Task Brief Template**
**Location:** `/Users/tsvikavagman/Desktop/path58-coordination/n8n-scraper-project/templates/TASK-BRIEF-TEMPLATE-v1.md`

**Purpose:** PM creates task briefs with complete requirements

**What it contains:**
- Exact acceptance criteria
- Verification commands
- Required evidence files
- Quality targets
- Pass/fail criteria

**You should:** Read this when I reference it in my task assignments

---

### **2. RND Task Assignment Template** ⭐ **YOU WILL RECEIVE THIS**
**Location:** `/Users/tsvikavagman/Desktop/path58-coordination/n8n-scraper-project/templates/RND-TASK-ASSIGNMENT-TEMPLATE-v1.md`

**Purpose:** I (RND Manager) break down PM's brief into actionable tasks for you

**What it contains:**
- Your specific mission
- Reference to PM's original brief
- Complete deliverables checklist
- Evidence files you MUST create
- Self-validation protocol (before submitting to me)
- What causes instant rejection
- What causes approval

**You should:** This is YOUR primary work document for each task

---

## 🔄 **NEW WORKFLOW**

### **How Tasks Flow Now:**

```
PM writes task brief (using PM template)
         ↓
Master Orchestrator forwards to RND
         ↓
RND Manager (ME) breaks it down (using RND template)
         ↓
YOU receive RND task assignment
         ↓
YOU execute task following RND instructions
         ↓
YOU complete self-validation checklist
         ↓
YOU submit to RND with evidence files
         ↓
RND Manager validates independently (brutal, zero-trust)
         ↓
RND APPROVES → forwards to PM
   OR
RND REJECTS → returns to you with specific issues
         ↓
PM final validation
         ↓
Task complete (or rejected back to RND/Dev)
```

---

## ✅ **WHAT YOU MUST DO**

### **1. Read the RND Task Assignment Template**
**Action:** Open and read:
```
/Users/tsvikavagman/Desktop/path58-coordination/n8n-scraper-project/templates/RND-TASK-ASSIGNMENT-TEMPLATE-v1.md
```

**Why:** This shows you the format of every task you'll receive

**Time:** 15-20 minutes

---

### **2. Understand the Self-Validation Protocol**
**Key Section:** Lines 218-294 in the RND template

**This is CRITICAL:** Before submitting work to me, you MUST:
- [ ] Run all tests and WATCH them execute
- [ ] Verify coverage meets target
- [ ] Create ALL required evidence files
- [ ] Verify numbers match between files
- [ ] Complete full checklist

**Why:** I will independently verify everything. If your self-validation is incomplete, instant rejection.

---

### **3. Know What Causes Instant Rejection**
**Key Section:** Lines 405-428 in the RND template

**I will REJECT immediately if:**
- ❌ Missing evidence files
- ❌ Numbers don't match
- ❌ Tests failing
- ❌ Coverage below target
- ❌ Can't reproduce results
- ❌ Incomplete requirements
- ❌ "Almost done" (95% ≠ 100%)

**Why:** Protects project quality. Fix issues and resubmit.

---

### **4. Know What Causes Approval**
**Key Section:** Lines 430-445 in the RND template

**I will APPROVE if:**
- ✅ All evidence exists
- ✅ Numbers match exactly
- ✅ Tests 100% pass
- ✅ Coverage meets target
- ✅ All requirements met
- ✅ Reproducible results

**Why:** This is the quality standard we're aiming for.

---

## 📊 **REQUIRED EVIDENCE FILES**

### **For EVERY task, you MUST create:**

1. **`[TASK-ID]-test-output.txt`**
   - Complete pytest output showing all tests passing
   - Created by: `pytest tests/[module] -v > [file]`

2. **`[TASK-ID]-coverage-report.txt`**
   - Complete coverage report showing target met
   - Created by: `pytest --cov=... > [file]`

3. **`[TASK-ID]-sample-output.json`**
   - Sample of your code's output
   - Task-specific format

4. **`[TASK-ID]-evidence-summary.json`**
   - JSON with all metrics and checklist
   - Standardized format (template provided)

**Location:** `.coordination/testing/results/`

**CRITICAL:** All files must exist before you submit to me.

---

## 🔍 **CRITICAL: WATCH TESTS RUN**

### **ALWAYS Do This:**
```bash
# Run tests and WATCH them execute
pytest tests/[module] -v

# ONLY AFTER seeing them pass:
pytest tests/[module] -v > evidence-file.txt
```

### **NEVER Do This:**
```bash
# Bad: Piping without seeing
pytest tests/[module] -v > file.txt  # Can't see if stuck!
```

**Why:** You need to see tests running to know they're not stuck. This is a hard requirement now.

---

## 📝 **COMMUNICATION PROTOCOL**

### **Before Starting Task:**
- [ ] Read PM's original brief (I'll provide link)
- [ ] Read my RND task assignment
- [ ] Ask me questions if ANYTHING unclear
- [ ] Don't assume - ASK

### **During Work:**
- [ ] Update progress daily
- [ ] Report blockers immediately
- [ ] Ask questions early

### **Before Submitting:**
- [ ] Complete self-validation checklist
- [ ] Verify all evidence files exist
- [ ] Double-check numbers match
- [ ] Ready for brutal validation

---

## 🎯 **EXAMPLES OF GOOD vs BAD QUESTIONS**

### **Good Questions (Ask These):**
✅ "Requirement #2 says X. Does that mean Y or Z specifically?"  
✅ "Coverage target is 80%. Should I aim for 85% for safety?"  
✅ "Should sample output include ALL 19 fields or just the core ones?"  
✅ "The test is taking 5 minutes. Is that expected or is something wrong?"  

### **Bad Questions (Don't Ask These):**
❌ "What should I do?" → Read the task brief  
❌ "Is this good enough?" → Check the requirements  
❌ "Can I skip requirement #3?" → No, all required  
❌ "Do I really need all evidence files?" → Yes, all required  

---

## 🚨 **WHAT HAPPENS WITH CURRENT WORK**

### **SCRAPE-001 (Dev1):** ✅ Already approved - no changes needed

### **SCRAPE-002 (Dev1):** 
- Current status: Awaiting clarification from PM
- When clarification comes: I'll issue NEW task assignment using new template
- You'll follow new process for rework

### **SCRAPE-005 (Dev2):** ✅ Already approved - no changes needed

### **Future Tasks:**
- ALL will use new template format
- ALL will require new evidence format
- ALL will have self-validation checklist

---

## 📚 **RESOURCES FOR YOU**

### **Templates to Review:**
1. **PM Task Brief Template:**
   `/Users/tsvikavagman/Desktop/path58-coordination/n8n-scraper-project/templates/TASK-BRIEF-TEMPLATE-v1.md`
   
2. **RND Task Assignment Template:** ⭐ **READ THIS**
   `/Users/tsvikavagman/Desktop/path58-coordination/n8n-scraper-project/templates/RND-TASK-ASSIGNMENT-TEMPLATE-v1.md`

### **Key Sections to Study:**
- Self-Validation Protocol (RND template, lines 218-294)
- Evidence Files Required (RND template, lines 67-137)
- Instant Rejection Criteria (RND template, lines 405-428)
- Testing Protocol (RND template, lines 244-286)

---

## ✅ **ACTION ITEMS FOR YOU**

### **Dev1 - Action Items:**
- [ ] Read RND Task Assignment Template (15-20 min)
- [ ] Understand self-validation checklist
- [ ] Know what causes rejection/approval
- [ ] Wait for my task assignment for SCRAPE-002 rework (using new format)
- [ ] Acknowledge this notification

### **Dev2 - Action Items:**
- [ ] Read RND Task Assignment Template (15-20 min)
- [ ] Understand self-validation checklist
- [ ] Know what causes rejection/approval
- [ ] Wait for my task assignment for SCRAPE-006 (using new format)
- [ ] Acknowledge this notification

---

## 📞 **QUESTIONS?**

### **If you have questions about:**
- **The new process:** Ask me (RND Manager)
- **Specific requirements:** Wait for task assignment, then ask
- **Templates:** Read them first, then ask if unclear
- **Evidence format:** Examples in template, ask if need more

### **How to acknowledge:**
Create file: `.coordination/handoffs/dev[X]-to-rnd-NEW-PROCESS-ACKNOWLEDGED.md`

```markdown
# Acknowledgment: New Process

**Developer:** [Your name]
**Date:** [YYYY-MM-DD]

I acknowledge:
- [ ] Read RND Task Assignment Template
- [ ] Understand self-validation requirements
- [ ] Know evidence files I must create
- [ ] Know what causes rejection/approval
- [ ] Ready to follow new process
- [ ] Will ask questions if unclear

**Questions (if any):**
[List any questions]

**Signature:** [Your name]
```

---

## 🎯 **WHY THIS CHANGE**

### **Problems We Had:**
1. Dev1 SCRAPE-002: Unclear requirements led to incomplete work
2. Dev2 SCRAPE-005: Initial submission needed rework
3. RND (me): Failed to verify independently
4. PM: Received unverified work

### **How New Process Fixes:**
1. ✅ Crystal-clear requirements (PM template)
2. ✅ Actionable breakdown (RND template)
3. ✅ Self-validation before submission (checklist)
4. ✅ Independent RND verification (protocol)
5. ✅ Standard evidence format (templates)
6. ✅ No ambiguity about "done" (exact criteria)

---

## ⏱️ **TIMELINE**

**Effective:** Immediately for all new tasks  
**Current tasks:** Will transition to new format as needed  
**Your action:** Read template by end of today  

---

## 💡 **BENEFITS FOR YOU**

### **This Makes Your Job Easier:**
✅ **No more confusion** - Exact requirements, no guessing  
✅ **Clear success criteria** - Know exactly what "done" means  
✅ **Self-validation** - Catch issues before RND review  
✅ **Faster approval** - If checklist complete, quick approval  
✅ **Less rework** - Clear requirements = less back-and-forth  
✅ **Better communication** - Standard format everyone understands  

---

## 🚀 **NEXT STEPS**

### **Today:**
1. Read this notification ✅
2. Read RND Task Assignment Template (20 min)
3. Ask me any questions
4. Acknowledge (create acknowledgment file)

### **Tomorrow:**
5. Wait for next task assignment in new format
6. Follow new process exactly
7. Complete self-validation before submitting
8. Submit high-quality work

---

## ✅ **FINAL NOTES**

**This is a positive change.** It protects all of us:
- **Protects you:** Clear requirements, no surprises
- **Protects me:** Clear validation criteria
- **Protects PM:** Only verified work reaches them
- **Protects project:** Higher quality, fewer errors

**I'm here to help you succeed with this new process.**

**Questions? Ask me anytime.**

---

**RND Manager**  
**Date:** October 10, 2025, 12:05 AM  
**Status:** Notification sent - awaiting acknowledgment  
**Next:** Issue task assignments using new template

---

# 📋 **TL;DR (Too Long; Didn't Read)**

**What changed:** New templates for tasks and evidence  
**Why:** Prevent confusion and improve quality  
**What you do:** Read RND Task Assignment Template, follow it exactly  
**What you get:** Clear requirements, faster approvals, less rework  
**When:** Effective immediately  
**Action:** Read template + acknowledge this notification  

**Template location:** `/Users/tsvikavagman/Desktop/path58-coordination/n8n-scraper-project/templates/RND-TASK-ASSIGNMENT-TEMPLATE-v1.md`

