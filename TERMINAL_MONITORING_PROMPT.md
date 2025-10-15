# 🚀 L3 FULL SCRAPING TERMINAL MONITORING PROMPT

## **CURRENT STATUS:**
- **L3 Scraper**: ✅ RUNNING FRESH on ALL 6,022 workflows
- **Process**: Background Python process with Layer 3 Enhanced Scraper
- **Features**: Video discovery, transcript extraction, L1.5 content, quality scoring
- **Database**: Supabase with real-time updates
- **Mode**: FRESH START - All existing L3 data will be overwritten

---

## **🎯 QUICK START - LIVE MONITORING:**

### **Start Live Monitor (Updates Every 5 Seconds):**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper && python scripts/live_l3_monitor.py
```

**This will show:**
- ✅ Real-time progress bar
- 📊 Live statistics (videos, transcripts, completion rate)
- ⚡ Processing speed (workflows/hour)
- 🕒 Recent completions
- ⏰ Estimated completion time
- 🔄 Updates every 5 seconds

---

## **📊 MANUAL PROGRESS CHECKS:**

### **Quick Progress Check:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper && python scripts/monitor_l3_progress.py
```

### **Check Process Status:**
```bash
ps aux | grep "layer3_enhanced_v2" | grep -v grep
```

### **Check Database Viewer:**
```bash
open http://localhost:8080/workflows
```

---

## **🔍 DETAILED MONITORING COMMANDS:**

### **1. Full Progress Report:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper && python -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib.parse

load_dotenv()
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
encoded_password = urllib.parse.quote_plus(db_password)
database_url = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(database_url)
with engine.connect() as connection:
    total = connection.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
    l3_complete = connection.execute(text('SELECT COUNT(*) FROM workflows WHERE layer3_success = true')).scalar()
    l3_incomplete = total - l3_complete
    progress_pct = (l3_complete / total) * 100
    
    print(f'📊 L3 SCRAPING PROGRESS:')
    print(f'   Total Workflows: {total:,}')
    print(f'   L3 Complete: {l3_complete:,}')
    print(f'   L3 Incomplete: {l3_incomplete:,}')
    print(f'   Progress: {progress_pct:.1f}%')
"
```

### **2. Content Statistics:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper && python -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib.parse

load_dotenv()
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
encoded_password = urllib.parse.quote_plus(db_password)
database_url = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(database_url)
with engine.connect() as connection:
    result = connection.execute(text('''
        SELECT 
            COUNT(CASE WHEN transcripts IS NOT NULL AND transcripts != '{}' THEN 1 END) as with_transcripts,
            COUNT(CASE WHEN video_urls IS NOT NULL AND video_urls != '{}' THEN 1 END) as with_videos,
            AVG(CASE WHEN transcripts IS NOT NULL AND transcripts != '{}' 
                THEN LENGTH(transcripts::text) END) as avg_transcript_length
        FROM workflow_content 
        WHERE layer3_success = true
    ''')).fetchone()
    
    print(f'🎬 L3 CONTENT STATISTICS:')
    print(f'   With Videos: {result[1]:,}')
    print(f'   With Transcripts: {result[0]:,}')
    if result[2]:
        print(f'   Avg Transcript Length: {result[2]:.0f} chars')
"
```

---

## **📈 EXPECTED OUTPUT PATTERNS:**

### **Live Monitor Output:**
```
🚀 L3 SCRAPING LIVE MONITOR - 2025-10-15 19:35:00
================================================================================
✅ L3 Scraping Process: RUNNING

📊 PROGRESS: 0.8%
[██████████████████████████████████████████████████] 49/6,022

📈 STATISTICS:
   Total Workflows: 6,022
   L3 Complete: 49
   L3 Incomplete: 5,973
   With Videos: 323
   With Transcripts: 12
   Avg Transcript Length: 18521 chars

⚡ PERFORMANCE:
   Elapsed Time: 0:05:30
   Processing Rate: 534.5 workflows/hour
   Estimated Completion: 2025-10-16 20:45:00

🕒 RECENT COMPLETIONS:
   6270: 2025-10-15 16:19:01.551915
   2462: 2025-10-15 14:35:12.106084
   5170: 2025-10-15 14:33:27.812578
```

### **Scraper Log Output:**
```
📦 BATCH 1/603 (10 workflows)
--------------------------------------------------
[1/6022] Processing 1...
   ✅ SUCCESS: 0 videos, 0 transcripts, 20260 chars, Q:40
[2/6022] Processing 100...
   ✅ SUCCESS: 0 videos, 0 transcripts, 20357 chars, Q:40

📈 Progress: 10/6022 (0.2%)
✅ Successful: 10
❌ Failed: 0
📊 Success Rate: 100.0%
⏳ Waiting 30 seconds before next batch...
```

---

## **🎯 KEY METRICS TO WATCH:**

- **Success Rate**: Should be >90%
- **Processing Speed**: ~500-600 workflows/hour
- **Video Discovery**: Look for workflows with videos found
- **Transcript Extraction**: Check for transcript character counts
- **Quality Scores**: Monitor Q: scores (40-100)

---

## **⚠️ TROUBLESHOOTING:**

### **If Process Stops:**
```bash
# Check if process is running
ps aux | grep "layer3_enhanced_v2" | grep -v grep

# If not running, restart:
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper && python -c "
import asyncio
from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor

async def restart_scraping():
    async with EnhancedLayer3Extractor(headless=True, extract_transcripts=True) as extractor:
        # Restart from where it left off
        print('Restarting L3 scraping...')

asyncio.run(restart_scraping())
"
```

### **If Success Rate Drops:**
- May indicate rate limiting or network issues
- Check for Python errors in logs
- Monitor memory usage

### **If No Videos Found:**
- Normal for many workflows (not all have videos)
- Focus on transcript extraction success

---

## **🏁 COMPLETION INDICATORS:**

- Progress reaches 100% (6,022/6,022)
- All workflows show `layer3_success = true`
- Final success rate reported
- Process exits cleanly
- Estimated completion time reached

---

## **📋 NEXT STEPS AFTER COMPLETION:**

1. **Verify Results**: Check all workflows have L3 data
2. **Content Analysis**: Analyze video/transcript statistics
3. **Quality Review**: Check quality score distribution
4. **Database Update**: Ensure viewer shows all data
5. **Generate Report**: Create completion summary

---

**💡 TIP**: Use the live monitor for real-time updates, and the manual commands for detailed analysis. The process will run for approximately 25 hours total.
