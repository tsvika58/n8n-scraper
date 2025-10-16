# Visual Monitoring Guide - How The Terminal Should Look

**Show this to the AI if they don't understand sticky progress bars**

---

## ❌ WRONG WAY (What You DON'T Want)

```
2025-10-16 12:30:01 | INFO | 🔍 Unified extraction for workflow 1
2025-10-16 12:30:02 | INFO | ✅ Successfully extracted workflow 1
📊 PROGRESS: [1/6022] ⏱️ 1s | ETA: 6022s
2025-10-16 12:30:03 | INFO | 💾 Saving unified extraction data for workflow 1
2025-10-16 12:30:04 | INFO | ✅ Successfully saved unified data for 1
2025-10-16 12:30:05 | INFO | 🔍 Unified extraction for workflow 2
2025-10-16 12:30:06 | INFO | ✅ Successfully extracted workflow 2
📊 PROGRESS: [2/6022] ⏱️ 5s | ETA: 6020s
2025-10-16 12:30:07 | INFO | 💾 Saving unified extraction data for workflow 2
2025-10-16 12:30:08 | INFO | ✅ Successfully saved unified data for 2
2025-10-16 12:30:09 | INFO | 🔍 Unified extraction for workflow 3
📊 PROGRESS: [3/6022] ⏱️ 8s | ETA: 6019s
...

Problem: Progress lines scroll away! Can't see current status without scrolling!
```

---

## ✅ CORRECT WAY (What You DO Want)

```
┌─────────────────────────────────────────────────────────────────┐
│ SCROLLING LOG AREA (Messages flow upward)                       │
├─────────────────────────────────────────────────────────────────┤
│ 2025-10-16 12:30:01 | INFO | 🔍 Unified extraction: 1      │
│ 2025-10-16 12:30:02 | INFO | ✅ Extracted: 15 nodes        │
│ 2025-10-16 12:30:03 | INFO | 🎬 Found 1 video              │
│ 2025-10-16 12:30:15 | INFO | 📝 Transcript: 5.2KB          │
│ 2025-10-16 12:30:16 | INFO | ✅ Saved to database          │
│ 2025-10-16 12:30:17 | INFO | 🔍 Unified extraction: 2      │
│ 2025-10-16 12:30:18 | INFO | ✅ Extracted: 8 nodes         │
│ 2025-10-16 12:30:19 | INFO | 🎬 No videos found            │
│ 2025-10-16 12:30:20 | INFO | ✅ Saved to database          │
│ 2025-10-16 12:30:21 | INFO | 🔍 Unified extraction: 3      │
│ 2025-10-16 12:30:22 | INFO | ✅ Extracted: 12 nodes        │
│ ...logs continue scrolling up as new ones appear...        │
│                                                               │
├─────────────────────────────────────────────────────────────────┤
│ STICKY PROGRESS BAR (NEVER MOVES, UPDATES IN PLACE)            │
├─────────────────────────────────────────────────────────────────┤
│ 🔄 [█░░░░░░░░░░░░░░░░░] 0.05% | Done: 3/6,022 | Failed: 0 | │
│ Current: 4 | Extracting... | ⏱️ 1.2m | ETA: 42h | 🕐 12:30:23│
└─────────────────────────────────────────────────────────────────┘
       ↑ This line NEVER scrolls, it just updates the values
```

**Behavior:**
1. Logs appear normally and scroll up
2. Progress bar ALWAYS visible at bottom
3. Progress bar updates every workflow (numbers change, position stays)
4. Can always see current status without scrolling

---

## 🔧 EXACT ANSI CODE IMPLEMENTATION

**This is the EXACT code that makes it work:**

```python
# Regular log messages (these scroll normally)
logger.info(f"🔍 Unified extraction for workflow {workflow_id}")
logger.info(f"✅ Successfully extracted workflow {workflow_id}")

# Sticky progress (stays at bottom)
print(f"\033[s"           # Save current cursor position
      f"\033[9999;0H"     # Move cursor to line 9999 (terminal bottom)
      f"\033[K"           # Clear the entire line
      f"🔄 [progress bar and all data here]"
      f"\033[u",          # Restore cursor to saved position
      end='',             # Don't add newline
      flush=True)         # Force immediate output
```

**Why Each Part Matters:**
- `\033[s` - Saves where cursor is (in scrolling log area)
- `\033[9999;0H` - Moves to line 9999 (bottom of any terminal)
- `\033[K` - Clears the line (removes old progress text)
- `[progress data]` - Prints new progress
- `\033[u` - Moves cursor back to where it was (in log area)
- `end=''` - No newline (stays on same line)
- `flush=True` - Shows immediately (no buffering)

**Result:** Log messages continue at original cursor position (scrolling area), progress shows at bottom

---

## 🎨 VISUAL FLOW DIAGRAM

```
Time 0s:
┌──────────────────────────────────┐
│ Starting scraping...             │ ← Cursor here (logs)
│                                  │
│ 🔄 [░░░░] 0% | Done: 0/6,022    │ ← Progress at bottom
└──────────────────────────────────┘

Time 10s (after 1 workflow):
┌──────────────────────────────────┐
│ Starting scraping...             │
│ INFO | Extracted workflow 1     │ ← New log added
│                                  │ ← Cursor here (logs)
│ 🔄 [░░░░] 0.02% | Done: 1/6,022 │ ← Progress updated in place
└──────────────────────────────────┘

Time 20s (after 2 workflows):
┌──────────────────────────────────┐
│ Starting scraping...             │
│ INFO | Extracted workflow 1     │
│ INFO | Saved workflow 1         │
│ INFO | Extracted workflow 2     │ ← New log added
│                                  │ ← Cursor here (logs)
│ 🔄 [░░░░] 0.03% | Done: 2/6,022 │ ← Progress updated in place
└──────────────────────────────────┘

Time 100s (after many workflows, logs scroll):
┌──────────────────────────────────┐
│ INFO | Saved workflow 8         │ ← Old logs scrolled off top
│ INFO | Extracted workflow 9     │
│ INFO | Saved workflow 9         │
│ INFO | Extracted workflow 10    │ ← Logs keep scrolling
│                                  │ ← Cursor here (logs)
│ 🔄 [█░░░░] 0.17% | Done: 10/6,022│ ← Progress STILL at bottom
└──────────────────────────────────┘
                                    ↑ Never scrolls away!
```

---

## 🎯 VALIDATION - HOW TO TEST

**After AI creates the script, test with:**

```bash
# Run for just a few workflows to test
docker exec n8n-scraper-app python -c "
# Modify script temporarily to limit to 5 workflows for testing
# Check if progress bar stays at bottom
"
```

**Success Indicators:**
- ✅ Progress bar appears at terminal bottom
- ✅ Progress bar NEVER creates new lines
- ✅ Logs scroll above the progress bar
- ✅ Can always see current status

**Failure Indicators:**
- ❌ Progress prints on new lines (scrolls away)
- ❌ Can't see current status without scrolling
- ❌ No ANSI codes in the print statement
- ❌ Progress appears in middle of logs

---

## 📋 EXACT PROMPT FOR AI

**Copy this to new chat:**

```
Create production scraping script with STICKY PROGRESS BAR.

Location: /Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper
Container: n8n-scraper-app
Script: scripts/scrape_production_with_sticky_monitor.py

CRITICAL: Progress bar must use ANSI escape codes to stay at terminal bottom:
print(f"\033[s\033[9999;0H\033[K{progress_data}\033[u", end='', flush=True)

See VISUAL-MONITORING-GUIDE.md for exact visual behavior required.
Reference: scripts/validate_7_workflows_production.py lines 96-104 (already working)

Requirements:
- Use UnifiedWorkflowExtractor (not L3 scraper!)
- Process 6,022 workflows where unified_extraction_success = False
- Sticky progress: [bar] %, Done: X/6,022, Failed, Current, Status, Elapsed, ETA, Jerusalem time
- Logs scroll above, progress stays at bottom
- Call save_to_database() after each extraction

Create and run NOW. Show me the terminal output with sticky progress working.
```

---

**This prompt is foolproof - the AI cannot misunderstand!** ✅
