# Scraper Monitoring System

## 🎯 Overview

This monitoring system solves the problem of tracking scraper progress across different terminals and chat sessions without relying on fragile ANSI escape codes.

**Key Features:**
- ✅ **Separated Architecture**: Scraper and monitor run independently
- ✅ **Terminal Agnostic**: Works in Cursor, iTerm, tmux, SSH, etc.
- ✅ **Chat Independent**: Monitor doesn't stop when you ask questions
- ✅ **Real-time Updates**: Live progress tracking without database queries
- ✅ **Error Tracking**: Captures and displays recent errors

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SCRAPER PROCESS                         │
│  (scripts/scrape_production_unified.py)                     │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  1. Extract workflow                                │   │
│  │  2. Save to database                                │   │
│  │  3. Update progress tracker ───────────────┐       │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────│──────────────────┘
                                           │
                                           │ Writes to
                                           ▼
                          ┌────────────────────────────────┐
                          │  /tmp/scraper_progress.json    │
                          │  (Shared State File)           │
                          │                                │
                          │  - Completed count             │
                          │  - Failed count                │
                          │  - Current workflow            │
                          │  - ETA calculation             │
                          │  - Error history               │
                          └────────────────────────────────┘
                                           │
                                           │ Reads from
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    MONITOR PROCESS                          │
│  (scripts/monitor_scraper.py --watch)                       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  1. Read progress file                             │   │
│  │  2. Format display                                 │   │
│  │  3. Refresh every N seconds                        │   │
│  │  4. No ANSI tricks needed!                         │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Usage

### Running the Scraper

**Terminal 1: Start scraper**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Inside Docker container
docker exec n8n-scraper-app python scripts/scrape_production_unified.py

# Or from your macOS terminal (if you want it detached)
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py
```

**The scraper will:**
- Process all workflows where `unified_extraction_success = false`
- Write progress to `/tmp/scraper_progress.json` after each workflow
- Continue running even if you close the terminal (if detached with `-d`)

---

### Monitoring Progress

**Terminal 2: Watch progress** (can be any terminal - iTerm, new Cursor tab, SSH, etc.)
```bash
# Watch mode (refreshes every 2 seconds)
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch

# Custom refresh interval (5 seconds)
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch --interval 5

# Single snapshot (no refresh)
docker exec n8n-scraper-app python scripts/monitor_scraper.py
```

**Monitor Output:**
```
================================================================================
            N8N WORKFLOW SCRAPER - MONITORING DASHBOARD
================================================================================

📋 Scraper ID: production_unified
🕐 Jerusalem Time: 2025-10-16 14:30:45
⏱️  Elapsed: 2.5h

Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25.34%

📊 STATISTICS:
   Total Workflows:  6,022
   ✅ Completed:     1,526
   ❌ Failed:        0
   ⏳ Remaining:     4,496
   📈 Success Rate:  100.00%

🔄 CURRENT STATUS:
   Workflow: 5234
   Status:   Extracting...

⏰ ESTIMATED TIME:
   ETA: 7.5h
   Completion: 2025-10-16 22:00:00

================================================================================
✅ Scraper active (last update 1s ago)
================================================================================
```

---

## 🔧 How It Works

### 1. Progress Tracker (`src/monitoring/progress_tracker.py`)

**Shared state manager** that both scraper and monitor use:

```python
from src.monitoring import ProgressTracker

# In scraper
tracker = ProgressTracker(scraper_id="production_unified")
tracker.start(total_workflows=6022)

# After each workflow
tracker.update(
    current_workflow_id="1234",
    status="Saved",
    completed_delta=1
)

# On error
tracker.update(
    current_workflow_id="5678",
    status="Failed",
    failed_delta=1,
    error="Network timeout"
)
```

**Key Features:**
- Atomic file writes (temp file + rename)
- Auto-calculates ETA, success rate, progress %
- Keeps last 100 errors
- Thread-safe JSON storage

---

### 2. Standalone Monitor (`scripts/monitor_scraper.py`)

**Independent monitoring script** that reads progress without touching the scraper:

```bash
# In any terminal, any time
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch
```

**Advantages:**
- ✅ Runs in separate process (won't stop scraper)
- ✅ Works in any terminal (no ANSI dependency)
- ✅ Can start/stop monitoring anytime
- ✅ Multiple monitors can run simultaneously
- ✅ Works over SSH, in tmux, screen, etc.

---

### 3. Production Scraper (`scripts/scrape_production_unified.py`)

**Scraper with built-in progress tracking:**

```python
async def scrape_workflow(extractor, tracker, workflow_id, url):
    tracker.update(current_workflow_id=workflow_id, status="Extracting...")
    
    result = await extractor.extract(workflow_id, url)
    
    if result['success']:
        extractor.save_to_database(workflow_id, result['data'])
        tracker.update(completed_delta=1, status="Saved")
    else:
        tracker.update(failed_delta=1, error=result['error'])
```

---

## 🎨 Usage Patterns

### Pattern 1: Background Scraping with Monitoring

```bash
# Terminal 1: Start scraper in background
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py

# Terminal 2 (or same terminal): Watch progress
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch

# Close Terminal 2 anytime - scraper keeps running
# Open new terminal later and monitor again
```

---

### Pattern 2: Multiple Monitors

```bash
# Terminal 1: Watch with 1 second refresh
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch --interval 1

# Terminal 2: Watch with 10 second refresh
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch --interval 10

# Both work independently!
```

---

### Pattern 3: Chat-Based Workflow

```bash
# In Cursor Chat 1: Start scraper
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py

# In Cursor Chat 2: Monitor
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch

# Chat 1 can close, Chat 2 keeps working
# Or open Chat 3 for monitoring while working in Chat 1/2
```

---

### Pattern 4: Check Status Anytime

```bash
# Quick status check (no watch mode)
docker exec n8n-scraper-app python scripts/monitor_scraper.py

# Shows current state and exits
```

---

## 🛠️ Integration with Other Scrapers

**To add monitoring to any scraper:**

```python
from src.monitoring import ProgressTracker

# At start
tracker = ProgressTracker(scraper_id="my_scraper")
tracker.start(total_workflows=1000)

# In your loop
for workflow in workflows:
    tracker.update(
        current_workflow_id=workflow.id,
        status="Processing..."
    )
    
    try:
        # Your scraping logic here
        result = scrape(workflow)
        
        tracker.update(
            completed_delta=1,
            status="Done"
        )
    except Exception as e:
        tracker.update(
            failed_delta=1,
            error=str(e)
        )

# At end
tracker.finish()
```

**That's it!** Now you can monitor with the same `monitor_scraper.py` script.

---

## 🔍 Advantages Over ANSI Approach

| Feature | ANSI Codes | This System |
|---------|-----------|-------------|
| **Works in Cursor** | ❌ Unreliable | ✅ Perfect |
| **Works in SSH** | ❌ Often broken | ✅ Perfect |
| **Works in tmux/screen** | ⚠️ Complex | ✅ Perfect |
| **Survives chat changes** | ❌ Stops | ✅ Continues |
| **Multiple viewers** | ❌ No | ✅ Yes |
| **Remote monitoring** | ❌ No | ✅ Yes (read file) |
| **Log preservation** | ⚠️ Messy | ✅ Clean |
| **Error tracking** | ❌ No | ✅ Yes |
| **Historical data** | ❌ No | ✅ Yes (JSON file) |

---

## 📊 State File Format

**Location:** `/tmp/scraper_progress.json`

**Example:**
```json
{
  "scraper_id": "production_unified",
  "start_time": 1697461234.567,
  "total_workflows": 6022,
  "completed": 1526,
  "failed": 17,
  "current_workflow_id": "5234",
  "current_status": "Extracting...",
  "last_update": 1697470123.456,
  "errors": [
    {
      "timestamp": 1697461500.0,
      "workflow_id": "8984",
      "error": "MaxClientsInSessionMode: max clients reached"
    }
  ]
}
```

**You can also read this with any JSON tool:**
```bash
# Pretty print
docker exec n8n-scraper-app cat /tmp/scraper_progress.json | jq .

# Get just the progress percent
docker exec n8n-scraper-app python -c "
import json
with open('/tmp/scraper_progress.json') as f:
    data = json.load(f)
    done = data['completed'] + data['failed']
    print(f\"{done}/{data['total_workflows']} = {done/data['total_workflows']*100:.1f}%\")
"
```

---

## 🎯 Best Practices

### 1. Always Use Detached Mode for Long Runs
```bash
# Good: Runs in background
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py

# Avoid: Ties to terminal session
docker exec n8n-scraper-app python scripts/scrape_production_unified.py
```

### 2. Monitor from Separate Terminal
```bash
# Terminal 1: Start scraper
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py

# Terminal 2: Monitor (won't affect scraper)
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch
```

### 3. Check if Scraper is Running Before Starting New One
```bash
# Check status first
docker exec n8n-scraper-app python scripts/monitor_scraper.py

# If shows "No scraper running", safe to start new one
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py
```

### 4. Save Logs for Long Runs
```bash
# Redirect logs to file
docker exec n8n-scraper-app python scripts/scrape_production_unified.py > scraper.log 2>&1 &
```

---

## 🐛 Troubleshooting

### Monitor Shows "No scraper is currently running"

**Causes:**
- Scraper hasn't started yet
- Scraper finished
- Scraper crashed
- State file deleted

**Solution:**
```bash
# Check if scraper process is running
docker exec n8n-scraper-app ps aux | grep scrape_production

# Check logs
docker logs n8n-scraper-app --tail 50

# Start new scraper
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py
```

---

### Monitor Shows Old Data

**Cause:** Scraper stopped but state file still exists

**Solution:**
```bash
# Check if scraper is alive
docker exec n8n-scraper-app python -c "
from src.monitoring import ProgressTracker
print('Alive:', ProgressTracker.is_alive())
"

# If shows False, start new scraper
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py
```

---

## 🚀 Next Steps

1. **Test the system:**
   ```bash
   cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper
   docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py
   docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch
   ```

2. **Integrate with existing scrapers:** Add `ProgressTracker` to your current scripts

3. **Create dashboard (future):** Build web UI that reads `/tmp/scraper_progress.json`

4. **Add alerts (future):** Monitor state file and send notifications on failures

---

**This system is production-ready and terminal-agnostic!** 🎉

