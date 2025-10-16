# L3 Full Scraping Monitoring Prompt

## 🚀 COMPLETE L3 SCRAPING ON ALL 6,022 WORKFLOWS

### **Current Status:**
- **Total Workflows**: 6,022 (ALL workflows in database)
- **Processing**: 10 workflows per batch with 30-second delays
- **Estimated Time**: ~25 hours total
- **Features**: Full video discovery, transcript extraction, L1.5 content, quality scoring
- **Overwriting**: The 49 already scraped workflows will be re-scraped

### **What's Running:**
The Layer 3 Enhanced Scraper is currently processing ALL workflows in the database, including:
- ✅ Video discovery (main page + iframes)
- ✅ Transcript extraction with timestamps
- ✅ L1.5 structured content (How it works, Setup instructions)
- ✅ Video classification (primary_explainer, related_workflow, tutorial)
- ✅ Quality scoring (0-100)
- ✅ Database storage (Supabase)

### **Monitoring Commands:**

#### 1. **Check Current Progress:**
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
    # Get L3 completion status
    total = connection.execute(text('SELECT COUNT(*) FROM workflows')).scalar()
    l3_complete = connection.execute(text('SELECT COUNT(*) FROM workflows WHERE layer3_success = true')).scalar()
    l3_incomplete = total - l3_complete
    
    print(f'📊 L3 SCRAPING PROGRESS:')
    print(f'   Total Workflows: {total}')
    print(f'   L3 Complete: {l3_complete}')
    print(f'   L3 Incomplete: {l3_incomplete}')
    print(f'   Progress: {(l3_complete / total) * 100:.1f}%')
    
    # Get recent completions
    recent = connection.execute(text('''
        SELECT workflow_id, layer3_extracted_at 
        FROM workflow_content 
        WHERE layer3_success = true 
        ORDER BY layer3_extracted_at DESC 
        LIMIT 5
    ''')).fetchall()
    
    print(f'\\n🕒 Recent Completions:')
    for row in recent:
        print(f'   {row[0]}: {row[1]}')
"
```

#### 2. **Check Video/Transcript Statistics:**
```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper && python -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib.parse
import json

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
    # Get video/transcript statistics
    result = connection.execute(text('''
        SELECT 
            COUNT(*) as total_workflows,
            COUNT(CASE WHEN transcripts IS NOT NULL AND transcripts != '{}' THEN 1 END) as workflows_with_transcripts,
            COUNT(CASE WHEN video_urls IS NOT NULL AND video_urls != '{}' THEN 1 END) as workflows_with_videos
        FROM workflow_content 
        WHERE layer3_success = true
    ''')).fetchone()
    
    print(f'🎬 L3 CONTENT STATISTICS:')
    print(f'   Total L3 Complete: {result[0]}')
    print(f'   With Videos: {result[2]}')
    print(f'   With Transcripts: {result[1]}')
    
    # Get transcript character counts
    transcript_stats = connection.execute(text('''
        SELECT 
            AVG(LENGTH(transcripts::text)) as avg_transcript_length,
            MAX(LENGTH(transcripts::text)) as max_transcript_length,
            MIN(LENGTH(transcripts::text)) as min_transcript_length
        FROM workflow_content 
        WHERE layer3_success = true AND transcripts IS NOT NULL AND transcripts != '{}'
    ''')).fetchone()
    
    if transcript_stats[0]:
        print(f'\\n📝 TRANSCRIPT STATISTICS:')
        print(f'   Average Length: {transcript_stats[0]:.0f} characters')
        print(f'   Max Length: {transcript_stats[1]:.0f} characters')
        print(f'   Min Length: {transcript_stats[2]:.0f} characters')
"
```

#### 3. **Check Process Status:**
```bash
ps aux | grep "layer3_enhanced_v2" | grep -v grep
```

#### 4. **Monitor Live Logs:**
```bash
# If running in background, check for log files
find /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper -name "*.log" -mmin -5
```

#### 5. **Check Database Viewer:**
```bash
# Open browser to check progress
open http://localhost:8080/workflows
```

### **Expected Output Pattern:**
```
📦 BATCH 1/603 (10 workflows)
--------------------------------------------------
[1/6022] Processing 1...
   ✅ SUCCESS: 0 videos, 0 transcripts, 20260 chars, Q:40
[2/6022] Processing 100...
   ✅ SUCCESS: 0 videos, 0 transcripts, 20357 chars, Q:40
[3/6022] Processing 1001...
   ✅ SUCCESS: 0 videos, 0 transcripts, 20588 chars, Q:40

📈 Progress: 10/6022 (0.2%)
✅ Successful: 10
❌ Failed: 0
📊 Success Rate: 100.0%
⏳ Waiting 30 seconds before next batch...
```

### **Key Metrics to Monitor:**
- **Success Rate**: Should be >90%
- **Video Discovery**: Look for workflows with videos found
- **Transcript Extraction**: Check for transcript character counts
- **Quality Scores**: Monitor Q: scores (40-100)
- **Processing Speed**: ~15 seconds per workflow

### **Troubleshooting:**
- **If process stops**: Check for Python errors or memory issues
- **If success rate drops**: May indicate rate limiting or network issues
- **If no videos found**: Normal for many workflows (not all have videos)
- **If transcripts fail**: YouTube may be blocking automated access

### **Completion Indicators:**
- Progress reaches 100% (6022/6022)
- All workflows show `layer3_success = true`
- Final success rate reported
- Process exits cleanly

### **Next Steps After Completion:**
1. Verify all workflows have L3 data
2. Check video/transcript statistics
3. Update database viewer
4. Run quality analysis
5. Generate completion report

---

**Note**: This process will run for approximately 25 hours. Monitor periodically and check for any errors or issues.

