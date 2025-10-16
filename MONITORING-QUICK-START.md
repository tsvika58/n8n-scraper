# Monitoring System - Quick Start

## 🎯 Problem Solved

**Before:** ANSI codes don't work in Cursor terminal, progress disappears, monitoring stops when you change chats.

**After:** Scraper and monitor run independently. Works in ANY terminal. Survives chat changes. No ANSI tricks needed!

---

## 🚀 How to Use

### Step 1: Start Scraper (Terminal 1 or Chat 1)

```bash
cd "/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"

# Start in background (recommended)
docker exec -d n8n-scraper-app python scripts/scrape_production_unified.py

# Or foreground (see logs but tied to terminal)
docker exec n8n-scraper-app python scripts/scrape_production_unified.py
```

---

### Step 2: Monitor Progress (Terminal 2 or Chat 2 or iTerm or SSH)

```bash
# Watch mode (refreshes every 2 seconds)
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch

# Slow refresh (every 5 seconds)
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch --interval 5

# Single snapshot (no refresh)
docker exec n8n-scraper-app python scripts/monitor_scraper.py
```

---

### Step 3: Close Monitor Anytime

**Just Ctrl+C!** Scraper keeps running.

Open monitor again anytime from ANY terminal/chat:
```bash
docker exec n8n-scraper-app python scripts/monitor_scraper.py --watch
```

---

## 📺 What You'll See

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
   ❌ Failed:        17
   ⏳ Remaining:     4,479
   📈 Success Rate:  98.90%

🔄 CURRENT STATUS:
   Workflow: 5234
   Status:   Saved

⏰ ESTIMATED TIME:
   ETA: 7.5h
   Completion: 2025-10-16 22:00:00

⚠️  RECENT ERRORS (17 total):
   • WF 8984: MaxClientsInSessionMode: max clients reached
   • WF 8985: MaxClientsInSessionMode: max clients reached
   • WF 4891: 'NoneType' object has no attribute 'get'

================================================================================
✅ Scraper active (last update 1s ago)
================================================================================
```

---

## ✅ Key Benefits

| Benefit | Description |
|---------|-------------|
| **🔄 Independent** | Monitor doesn't affect scraper |
| **📱 Multi-terminal** | Works in Cursor, iTerm, SSH, tmux, etc. |
| **💬 Chat-proof** | Scraper survives chat changes |
| **👥 Multi-viewer** | Multiple monitors can run simultaneously |
| **📊 Real-time** | Updates every N seconds |
| **🐛 Error tracking** | Shows recent errors |
| **⏱️ ETA** | Smart time estimates |
| **🎨 Clean** | No ANSI code mess |

---

## 🔍 Check Status Anytime

```bash
# Quick check (doesn't keep running)
docker exec n8n-scraper-app python scripts/monitor_scraper.py

# Or read the JSON directly
docker exec n8n-scraper-app cat /tmp/scraper_progress.json | jq .
```

---

## 🛑 Stop Scraper

```bash
# Find process
docker exec n8n-scraper-app ps aux | grep scrape_production

# Kill it
docker exec n8n-scraper-app pkill -f scrape_production_unified
```

---

## 📖 Full Documentation

See: `docs/MONITORING-SYSTEM.md`

---

**Ready to use! Works everywhere!** 🎉

