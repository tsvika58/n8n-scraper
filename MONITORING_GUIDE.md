# 🔍 N8N Scraper Monitoring & Data Viewing Guide

**Last Updated:** October 12, 2025  
**Purpose:** Complete guide to monitoring scraping progress and viewing database contents

---

## 📊 Quick Start - View Your Data NOW!

### Option 1: Web Dashboard (RECOMMENDED ✅)

**Easiest and most visual way to see your data!**

```bash
# Start the web viewer
./view-data.sh

# Your browser should open automatically to:
# http://localhost:5000
```

**Features:**
- ✅ Real-time statistics dashboard
- ✅ Searchable workflow table
- ✅ Quality score visualization
- ✅ Pagination for large datasets  
- ✅ Auto-refresh every 30 seconds
- ✅ Beautiful, professional UI

**Screenshot Preview:**
```
┌─────────────────────────────────────────────────────────┐
│  🗄️ N8N Scraper Database                                │
│  Real-time workflow monitoring and data exploration     │
├─────────────────────────────────────────────────────────┤
│  Total: 1000  │  Successful: 702  │  Avg Quality: 69.69│
├─────────────────────────────────────────────────────────┤
│  Search: [_________________________] [Search] [Clear]   │
├─────────────────────────────────────────────────────────┤
│  Workflow ID    │ URL          │ Quality │ Status      │
│  SYNTH-EDGE-099 │ n8n.io/...   │ 27.5%  │ ✅ Complete │
│  SYNTH-EDGE-098 │ n8n.io/...   │ 42.3%  │ ✅ Complete │
└─────────────────────────────────────────────────────────┘
```

---

### Option 2: pgAdmin (Database GUI)

**Professional database management interface**

```bash
# Start pgAdmin
docker-compose --profile dev up -d

# Open in browser
open http://localhost:8080
```

**Login Credentials:**
- Email: `admin@example.com`
- Password: `admin123`

**Database Connection Settings:**
- **Host:** `n8n-scraper-database` (NOT localhost or IP!)
- **Port:** `5432`
- **Database:** `n8n_scraper`
- **Username:** `scraper_user`
- **Password:** `scraper_pass`
- ⚠️ **IMPORTANT:** Check "Save password" checkbox!

**Common Issues:**
- ❌ "Could not connect" → Make sure Host is `n8n-scraper-database`
- ❌ "Authentication failed" → Enable "Save password" checkbox
- ❌ "Port already in use" → Stop other services on port 8080

---

### Option 3: Terminal Commands (Quick & Dirty)

**For quick checks without opening a browser**

#### Get Statistics
```bash
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE layer1_success AND layer2_success AND layer3_success) as successful,
    ROUND(AVG(quality_score)::numeric, 2) as avg_quality
FROM workflows;
"
```

#### View Recent Workflows
```bash
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    workflow_id,
    LEFT(url, 50) as url,
    quality_score,
    layer1_success as L1,
    layer2_success as L2,
    layer3_success as L3,
    extracted_at
FROM workflows
ORDER BY extracted_at DESC
LIMIT 10;
"
```

#### Search by Workflow ID
```bash
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT * FROM workflows 
WHERE workflow_id = 'SYNTH-EDGE-0099';
"
```

#### Count by Success Status
```bash
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    CASE 
        WHEN layer1_success AND layer2_success AND layer3_success THEN 'Full Success'
        WHEN error_message IS NOT NULL THEN 'Error'
        ELSE 'Partial Success'
    END as status,
    COUNT(*) as count
FROM workflows
GROUP BY status;
"
```

#### Watch Progress in Real-Time
```bash
# Update every 2 seconds
watch -n 2 'docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "SELECT COUNT(*) FROM workflows;"'
```

---

## 🎯 Monitoring Scraping Progress

### Real-Time Progress Tracking

#### Method 1: Web Dashboard (Auto-refresh)
```bash
./view-data.sh
# Refreshes automatically every 30 seconds
```

#### Method 2: Terminal Watch
```bash
# Watch workflow count
watch -n 2 'docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE extracted_at > NOW() - INTERVAL '\''1 hour'\'') as last_hour
FROM workflows;
"'
```

#### Method 3: Logs
```bash
# Watch scraper logs
docker-compose logs -f n8n-scraper-app

# Just show errors
docker-compose logs -f n8n-scraper-app | grep ERROR

# Show progress messages
docker-compose logs -f n8n-scraper-app | grep -i "workflow\|progress\|complete"
```

---

## 📈 Database Schema Overview

### Tables in Database

1. **workflows** (Main table)
   - `workflow_id` - Unique workflow identifier
   - `url` - Full URL to workflow
   - `quality_score` - Calculated quality (0-100)
   - `layer1_success` - Basic extraction success
   - `layer2_success` - Content parsing success  
   - `layer3_success` - Advanced features success
   - `processing_time` - Seconds to process
   - `extracted_at` - Timestamp
   - `error_message` - Error details if failed
   - `retry_count` - Number of retry attempts

2. **workflow_metadata** (Linked)
   - Author, tags, categories, etc.

3. **workflow_structure** (Linked)
   - Nodes, connections, complexity metrics

4. **workflow_content** (Linked)
   - Descriptions, configurations, JSON

5. **video_transcripts** (Linked)
   - Video transcriptions if available

### Explore Schema
```bash
# Show all tables
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "\dt"

# Show workflows table structure
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "\d workflows"

# Show all columns with types
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "\d+ workflows"
```

---

## 🔧 Useful SQL Queries

### Quality Analysis
```sql
-- Quality distribution
SELECT 
    CASE 
        WHEN quality_score >= 80 THEN 'High (80+)'
        WHEN quality_score >= 60 THEN 'Medium (60-79)'
        WHEN quality_score >= 40 THEN 'Low (40-59)'
        ELSE 'Very Low (<40)'
    END as quality_tier,
    COUNT(*) as count,
    ROUND(AVG(processing_time)::numeric, 2) as avg_time
FROM workflows
GROUP BY quality_tier
ORDER BY quality_tier DESC;
```

### Processing Performance
```sql
-- Slowest workflows
SELECT 
    workflow_id,
    processing_time,
    quality_score
FROM workflows
ORDER BY processing_time DESC
LIMIT 10;
```

### Error Analysis
```sql
-- Workflows with errors
SELECT 
    workflow_id,
    error_message,
    retry_count
FROM workflows
WHERE error_message IS NOT NULL
ORDER BY retry_count DESC;
```

### Time-based Analysis
```sql
-- Workflows per hour
SELECT 
    DATE_TRUNC('hour', extracted_at) as hour,
    COUNT(*) as workflows_scraped
FROM workflows
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;
```

---

## 🚀 Production Dashboard (Coming in SCRAPE-015)

### Features Being Built

The current web viewer is basic. In SCRAPE-015, we'll build a **production-grade dashboard** with:

1. **Real-Time Progress**
   - Live scraping progress bar
   - Current workflow being processed
   - Estimated completion time
   - Success/failure rate graphs

2. **Advanced Analytics**
   - Quality score distribution charts
   - Processing time trends
   - Error rate analysis
   - Success rate by extraction layer

3. **Interactive Features**
   - Filter by date range
   - Sort by any column
   - Export to CSV/JSON
   - Detailed workflow inspection
   - Retry failed workflows

4. **System Monitoring**
   - Database size and growth
   - Scraper resource usage (CPU, memory)
   - Rate limiting status
   - Queue depth and backlog

5. **WebSocket Updates**
   - Real-time updates without page refresh
   - Live notifications for events
   - Progress bars that update in real-time

---

## 📱 Quick Reference Commands

### Start Services
```bash
# Start database + scraper
docker-compose up -d

# Start with pgAdmin
docker-compose --profile dev up -d

# Start web viewer
./view-data.sh
```

### View Data
```bash
# Open web viewer
open http://localhost:5000

# Open pgAdmin
open http://localhost:8080

# Terminal quick view
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT COUNT(*) FROM workflows;"
```

### Stop Services
```bash
# Stop web viewer (Ctrl+C in terminal)

# Stop pgAdmin
docker-compose stop n8n-scraper-db-admin

# Stop all services
docker-compose down
```

---

## 🎯 Recommendations

### For Development (Current Phase):
✅ **Use Web Viewer (`./view-data.sh`)**
- Easiest to use
- Beautiful interface
- Auto-refresh
- Perfect for monitoring progress

### For Database Exploration:
✅ **Use pgAdmin**
- Full SQL query capabilities
- View all tables and relationships
- Export data
- Professional database management

### For Quick Checks:
✅ **Use Terminal Commands**
- Fastest for simple queries
- No browser required
- Great for automation/scripts
- Perfect for SSH sessions

### For Production Monitoring:
⏳ **Wait for SCRAPE-015 Dashboard**
- We'll build a comprehensive live dashboard
- Real-time progress tracking
- Advanced analytics
- WebSocket updates

---

## 🆘 Troubleshooting

### Web Viewer Won't Start
```bash
# Check if psycopg2 is installed
pip3 install psycopg2-binary

# Check if port 5000 is available
lsof -i :5000

# Check database is running
docker-compose ps n8n-scraper-database
```

### pgAdmin Connection Failed
```bash
# Verify database is running
docker exec n8n-scraper-database pg_isready

# Test connection from host
psql -h localhost -p 5432 -U scraper_user -d n8n_scraper

# Check logs
docker-compose logs n8n-scraper-database
docker-compose logs n8n-scraper-db-admin
```

### No Data Showing
```bash
# Check if data exists
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "SELECT COUNT(*) FROM workflows;"

# Check if scraper is running
docker-compose ps n8n-scraper-app

# View scraper logs
docker-compose logs n8n-scraper-app
```

---

## 📚 Next Steps

1. ✅ **Try the web viewer** - Run `./view-data.sh`
2. ✅ **Explore your data** - Use search and pagination
3. ✅ **Learn SQL queries** - Try the examples above
4. ⏳ **Wait for production dashboard** (SCRAPE-015)

---

## 💡 Pro Tips

- **Keep web viewer running** during scraping to see live progress
- **Use search feature** to find specific workflows quickly
- **Sort by quality score** to find best/worst quality workflows
- **Check layer success columns** to diagnose extraction issues
- **Monitor processing time** to identify performance bottlenecks
- **Export to CSV** from pgAdmin for analysis in Excel/Google Sheets

---

**Your database currently has: 1,000 workflows with 702 fully successful! 🎉**

Enjoy exploring your data! 🚀

