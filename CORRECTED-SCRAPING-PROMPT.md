# CORRECTED Production Scraping Prompt - Sticky Progress Bar Required

**🚨 CRITICAL: The AI must understand the sticky progress bar requirement!**

---

## ❌ **WHAT'S WRONG WITH CURRENT IMPLEMENTATION**

The current `scrape_all_production.py` script is probably using **regular print statements** that scroll away with the logs. This is NOT what you want!

**Current (Wrong):**
```
2025-10-16 12:30:01 | INFO | Extracted workflow 1
📊 PROGRESS: [1/6022] ⏱️ 10s | ETA: 1,493m
2025-10-16 12:30:10 | INFO | Extracted workflow 2
📊 PROGRESS: [2/6022] ⏱️ 20s | ETA: 1,490m
2025-10-16 12:30:20 | INFO | Extracted workflow 3
📊 PROGRESS: [3/6022] ⏱️ 30s | ETA: 1,487m
...progress lines scroll away with logs (can't see current status!)
```

---

## ✅ **WHAT YOU WANT (CORRECT)**

**Sticky progress bar stays at bottom:**
```
2025-10-16 12:30:01 | INFO | Extracted workflow 1
2025-10-16 12:30:10 | INFO | Extracted workflow 2  
2025-10-16 12:30:20 | INFO | Extracted workflow 3
2025-10-16 12:30:30 | INFO | Extracted workflow 4
2025-10-16 12:30:40 | INFO | Extracted workflow 5
...logs continue scrolling up...

────────────────────────────────────────────────────────────────────
🔄 [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.08% | Done: 5/6,022 | Failed: 0 | Current: 6 | ✅ Saved | ⏱️ 50s | ETA: 25h | 🕐 12:30:45
↑ THIS LINE STAYS AT BOTTOM AND UPDATES IN PLACE - NEVER SCROLLS AWAY
```

---

## 📝 **COPY THIS EXACT PROMPT TO NEW CHAT:**

```
CRITICAL REQUIREMENT: I need scraping with STICKY PROGRESS BAR at terminal bottom.

## What I Need

The current scrape_all_production.py script needs to be STOPPED and REPLACED with a version that has a STICKY progress bar that stays at the bottom of the terminal.

**STOP current scraping:**
```bash
docker exec n8n-scraper-app pkill -f scrape_all_production.py
```

**CREATE NEW SCRIPT:** scripts/scrape_production_with_sticky_monitor.py

**CRITICAL IMPLEMENTATION:**

The progress line MUST use ANSI escape codes to stay at the terminal bottom:

```python
def print_sticky_progress(self, workflow_id, status):
    """Print sticky progress that stays at terminal bottom."""
    elapsed = time.time() - self.start_time
    progress_pct = (self.completed / self.total * 100) if self.total > 0 else 0
    
    # Progress bar
    bar_length = 30
    filled = int(bar_length * self.completed / self.total) if self.total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # ETA
    if self.completed > 0:
        avg_time = elapsed / self.completed
        eta = avg_time * (self.total - self.completed)
        eta_str = f"{eta/3600:.1f}h" if eta > 3600 else f"{eta/60:.1f}m"
    else:
        eta_str = "calculating..."
    
    elapsed_str = f"{elapsed/3600:.1f}h" if elapsed > 3600 else f"{elapsed/60:.1f}m"
    jerusalem_time = datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%H:%M:%S')
    
    # CRITICAL: Use ANSI codes to keep at bottom
    print(f"\033[s\033[9999;0H\033[K"  # Save cursor, move to line 9999 (bottom), clear line
          f"🔄 [{bar}] {progress_pct:.2f}% | "
          f"Done: {self.completed}/{self.total} | "
          f"Failed: {self.failed} | "
          f"Current: {workflow_id} | "
          f"{status} | "
          f"⏱️ {elapsed_str} | "
          f"ETA: {eta_str} | "
          f"🕐 {jerusalem_time}"
          f"\033[u",  # Restore cursor position
          end='', flush=True)
```

**VISUAL BEHAVIOR:**
- Logs from scraper print normally (logger.info, logger.warning, etc.)
- They scroll up as new logs appear
- Progress line ALWAYS stays at the bottom
- Progress line updates IN PLACE (overwrites itself)
- Never creates new lines for progress

**EXACTLY LIKE:** scripts/validate_7_workflows_production.py (lines 96-104)

## Script Structure

```python
#!/usr/bin/env python3
import asyncio
import sys
import time
from datetime import datetime
import pytz
sys.path.append('.')

from src.scrapers.unified_workflow_extractor import UnifiedWorkflowExtractor
from src.storage.database import get_session
from n8n_shared.models import Workflow

JERUSALEM_TZ = pytz.timezone('Asia/Jerusalem')

class ProductionScraper:
    def __init__(self):
        self.start_time = time.time()
        self.completed = 0
        self.failed = 0
        self.total = 0
    
    def print_sticky_progress(self, workflow_id, status):
        # [IMPLEMENT AS SHOWN ABOVE WITH ANSI CODES]
    
    async def scrape_workflow(self, workflow_id, url):
        """Scrape single workflow."""
        self.print_sticky_progress(workflow_id, "Extracting...")
        
        extractor = UnifiedWorkflowExtractor()
        result = await extractor.extract(workflow_id, url)
        
        if result['success'] and result['data']:
            saved = extractor.save_to_database(workflow_id, result['data'])
            if saved:
                self.completed += 1
                self.print_sticky_progress(workflow_id, "✅ Saved")
            else:
                self.failed += 1
                self.print_sticky_progress(workflow_id, "❌ Save Failed")
        else:
            self.failed += 1
            self.print_sticky_progress(workflow_id, "❌ Failed")
    
    async def run(self):
        """Main scraping loop."""
        # Get all unprocessed workflows
        with get_session() as session:
            workflows = session.query(Workflow).filter(
                Workflow.unified_extraction_success == False
            ).all()
            self.total = len(workflows)
        
        print(f"🚀 Starting: {self.total:,} workflows")
        print()
        
        # Process each
        for wf in workflows:
            await self.scrape_workflow(wf.workflow_id, wf.url)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Final summary
        print("\n\n✅ COMPLETE!")
        print(f"Successful: {self.completed:,}")
        print(f"Failed: {self.failed:,}")

if __name__ == '__main__':
    scraper = ProductionScraper()
    asyncio.run(scraper.run())
```

## Run Command

```bash
cd /Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper
docker exec n8n-scraper-app python scripts/scrape_production_with_sticky_monitor.py
```

## What You Should See

Terminal output with:
- Top section: Logs scrolling up normally
- Bottom section: ONE LINE that updates in place with current progress

Example:
```
[Scrolling logs area]
2025-10-16 12:45:23 | INFO | 🔍 Unified extraction for workflow 1523
2025-10-16 12:45:24 | INFO | ✅ Successfully extracted workflow 1523
2025-10-16 12:45:25 | INFO | 💾 Saving unified extraction data for workflow 1523
2025-10-16 12:45:26 | INFO | ✅ Successfully saved unified data for 1523
2025-10-16 12:45:27 | INFO | 🔍 Unified extraction for workflow 1524
...

────────────────────────────────────────────────────────────────────
🔄 [███░░░░░░░░░░░░░░░░░░░░░░░░░░] 12.5% | Done: 754/6,022 | Failed: 8 | Current: 1524 | Extracting... | ⏱️ 3.2h | ETA: 22.3h | 🕐 12:45:27
```

The bottom line NEVER moves, it just updates the numbers/status in place.

CRITICAL: If you don't see the sticky behavior (bottom line staying put), the ANSI codes are not implemented correctly!

Create the script with proper ANSI codes and run it NOW.
```

---

## 🎯 **KEY POINTS FOR THE AI:**

1. ✅ **Use UnifiedWorkflowExtractor** (not L3 scraper)
2. ✅ **ANSI escape codes required** (\033[s\033[9999;0H\033[K...\033[u)
3. ✅ **Reference working script** (validate_7_workflows_production.py)
4. ✅ **Process all 6,022 workflows** (not 20, not testing)
5. ✅ **Query: unified_extraction_success = False** (not L3 flags)

**Copy the corrected prompt above to your new chat!** 🎯
