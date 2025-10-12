# STORAGE REQUIREMENTS ANALYSIS
## Comprehensive Scraping Expansion - Cloud Storage Planning

**Date**: October 12, 2025  
**Current Status**: 🔴 **CRITICAL - Local disk at 100% capacity**  
**Recommendation**: ✅ **IMMEDIATE cloud migration required**

---

## 🚨 CURRENT STORAGE SITUATION

### Local Disk Status:
- **Total Capacity**: 460 GB
- **Currently Used**: 431 GB (94%)
- **Available**: 1.2 GB
- **Status**: 🔴 **CRITICAL - 100% capacity**

### Current Database Size:
- **Total Database**: 14 MB
- **Workflows Scraped**: 71 workflows (with comprehensive data)
- **Workflows in DB**: 6,047 (mostly placeholders)

---

## 📊 STORAGE BREAKDOWN (Based on 20 Fully Scraped Workflows)

### Per-Workflow Storage (7 Layers):

| Table | Avg Per Workflow | For 6,041 Workflows |
|-------|------------------|---------------------|
| workflows (main) | 359 bytes | 2.17 MB |
| workflow_metadata (L1) | 120 bytes | 725 KB |
| workflow_structure (L2) | 120 bytes | 725 KB |
| workflow_content (L3) | 104 bytes | 628 KB |
| workflow_performance_analytics (L7) | 27 bytes | 163 KB |
| workflow_business_intelligence (L4) | 13 bytes | 79 KB |
| workflow_community_data (L5) | 12 bytes | 73 KB |
| workflow_technical_details (L6) | 10 bytes | 60 KB |
| workflow_enhanced_content | 5 bytes | 30 KB |
| workflow_relationships | 4 bytes | 24 KB |

**Total Per Workflow**: ~774 bytes  
**Projected for 6,041 workflows**: **~4.7 MB** (minimal!)

---

## 🎯 PROJECTED STORAGE REQUIREMENTS

### Scenario 1: Basic Scraping (Current 7 Layers)

**Database Only:**
- Core workflow data: ~4.7 MB
- Indexes and overhead: ~2 MB
- **Total Database**: **~7 MB**

**With Backups & Logs:**
- Database: 7 MB
- Daily backups (7 days): 49 MB
- Logs: 5 MB
- **Total**: **~61 MB**

### Scenario 2: With Media (Videos, Images, Screenshots)

If we decide to store media files (currently not implemented):
- **Per workflow estimate**: 5-10 MB (video thumbnails, screenshots)
- **For 6,041 workflows**: 30-60 GB
- **With backups**: 60-120 GB

### Scenario 3: With Full Video Transcripts

If we store full video content:
- **Per workflow estimate**: 50-100 MB (full videos)
- **For 6,041 workflows**: 300-600 GB
- **Not recommended** - link to YouTube instead

---

## 💰 CLOUD STORAGE RECOMMENDATIONS

### Option 1: **AWS (Recommended)**

**RDS PostgreSQL (Managed Database):**
- **Instance**: db.t3.micro ($15/month)
- **Storage**: 20 GB SSD ($2/month)
- **Backups**: Automated, 7-day retention ($2/month)
- **Monthly Cost**: **~$19/month**
- **Pros**: Managed, auto-backups, scalable, reliable
- **Cons**: Ongoing monthly cost

**S3 for Backups:**
- **Storage**: 1 GB ($0.023/month)
- **Monthly Cost**: **$0.02/month**
- **Pros**: Extremely cheap, unlimited retention
- **Cons**: Need to manage backup scripts

**Total AWS Monthly**: **~$19.02/month**

---

### Option 2: **DigitalOcean (Budget-Friendly)**

**Managed PostgreSQL:**
- **1 GB RAM, 10 GB disk**: $15/month
- **Automated backups**: Included
- **Monthly Cost**: **$15/month**
- **Pros**: Simple, affordable, good performance
- **Cons**: Limited to 10 GB (but we only need ~7 MB!)

**Spaces (S3-compatible):**
- **250 GB**: $5/month
- **Monthly Cost**: **$5/month** (if needed for media)
- **Pros**: Simple, S3-compatible
- **Cons**: 250 GB minimum

**Total DigitalOcean Monthly**: **$15-20/month**

---

### Option 3: **Google Cloud Platform**

**Cloud SQL PostgreSQL:**
- **Shared-core, 0.6 GB RAM**: $8.50/month
- **10 GB SSD**: $1.70/month
- **Backups**: $0.08/month
- **Monthly Cost**: **~$10.28/month**
- **Pros**: Cheapest for small DB, good integration
- **Cons**: Shared CPU (slower)

**Cloud Storage (for backups):**
- **1 GB Standard**: $0.02/month
- **Monthly Cost**: **$0.02/month**

**Total GCP Monthly**: **~$10.30/month**

---

### Option 4: **Supabase (Free Tier)**

**PostgreSQL Database:**
- **500 MB database**: FREE
- **1 GB bandwidth**: FREE
- **Monthly Cost**: **$0/month**
- **Pros**: Free, PostgreSQL-compatible, good UI
- **Cons**: 500 MB limit (we need ~7 MB, so plenty of room!)

**Upgrade if Needed:**
- **Pro Plan**: $25/month (8 GB database, 50 GB bandwidth)

**Total Supabase**: **$0/month** (FREE tier is sufficient!)

---

## 📈 STORAGE PROJECTION FOR 6,041 WORKFLOWS

### Based on Current 20 Workflows:

**Current Stats:**
- 20 workflows with all 7 layers
- Database size: 14 MB (includes 6,041 placeholder rows)
- Average per fully-scraped workflow: ~774 bytes

**Projected Full Dataset:**
- 6,041 workflows × 774 bytes = **4.68 MB** (core data)
- With indexes and overhead: **~7 MB**
- With backups (7 days): **~50 MB**
- With logs (30 days): **~100 MB**

**Total Projected Need: ~150-200 MB**

---

## 💡 IMMEDIATE RECOMMENDATIONS

### 🟢 **RECOMMENDED SOLUTION: Supabase Free Tier**

**Why:**
1. ✅ **FREE** (0 cost)
2. ✅ **500 MB limit** (we only need ~150-200 MB)
3. ✅ **PostgreSQL-compatible** (drop-in replacement)
4. ✅ **Automatic backups** included
5. ✅ **Dashboard included** (database viewer)
6. ✅ **REST API** included (bonus feature)
7. ✅ **No credit card** required for free tier

**Setup Time**: 10 minutes

**Migration Steps:**
```bash
# 1. Export current database
docker exec n8n-scraper-database pg_dump -U scraper_user -d n8n_scraper > migration_to_cloud.sql

# 2. Create Supabase project (free at supabase.com)
# 3. Import data to Supabase
# 4. Update docker-compose.yml with Supabase connection string
# 5. Test connection
# 6. Continue scraping to cloud
```

---

### 🟡 **ALTERNATIVE: AWS RDS (Production-Grade)**

**If you need production features:**
- ✅ Better SLA (99.95% uptime)
- ✅ Multi-AZ deployment option
- ✅ Advanced monitoring
- ✅ Enterprise support

**Cost**: $19/month

---

## 🔍 LOCAL DISK CLEANUP OPTIONS

**Before migrating**, you can free up space:

### Quick Wins:
```bash
# 1. Clean Docker images (can free 1-5 GB)
docker system prune -a --volumes

# 2. Clean old logs
find . -name "*.log" -mtime +7 -delete

# 3. Remove old backups (keep only latest)
ls -t backups/*.sql | tail -n +2 | xargs rm

# 4. Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

**Potential Space Freed**: 2-10 GB

---

## 📊 STORAGE GROWTH PROJECTION

### Month 1 (Initial Scrape):
- Database: 7 MB
- Backups: 50 MB
- Logs: 100 MB
- **Total**: ~150 MB

### Month 6 (with re-scraping):
- Database: 15 MB (some workflows updated)
- Backups: 100 MB
- Logs: 200 MB
- **Total**: ~315 MB

### Year 1:
- Database: 30 MB (with historical data)
- Backups: 200 MB
- Logs: 500 MB
- **Total**: ~730 MB

**Still well within FREE tier limits!**

---

## ⚡ RECOMMENDED ACTION PLAN

### Immediate (Today):
1. **Clean local disk** (free 2-10 GB)
   ```bash
   docker system prune -a
   ```

2. **Sign up for Supabase** (free, 5 minutes)
   - Visit: https://supabase.com
   - Create free project
   - Get connection string

3. **Migrate database** (15 minutes)
   - Export current DB
   - Import to Supabase
   - Update connection string
   - Test connection

### Short-term (This Week):
4. **Continue scraping to cloud**
5. **Monitor Supabase usage** (should stay under 500 MB)
6. **Keep local backups minimal** (latest only)

### Long-term (Optional):
7. **Consider AWS RDS** if you need:
   - Higher performance
   - More control
   - Enterprise SLA
   - Currently: NOT NEEDED

---

## 💵 COST SUMMARY

### FREE Option (Recommended):
- **Supabase Free Tier**: $0/month
- **Local storage**: Only code (~1 GB)
- **Total Monthly Cost**: **$0**

### Paid Options (If Needed Later):
- **Supabase Pro**: $25/month (8 GB database)
- **AWS RDS**: $19/month (20 GB database)
- **DigitalOcean**: $15/month (10 GB database)
- **GCP Cloud SQL**: $10/month (10 GB database)

---

## 🎯 FINAL RECOMMENDATION

**For your use case (6,041 workflows, ~7 MB database):**

✅ **Use Supabase Free Tier**
- Completely free
- More than enough capacity (500 MB vs your 7 MB need)
- Easy migration
- Frees up your local disk entirely
- Can upgrade later if needed

**Steps:**
1. Sign up at supabase.com (free, no credit card)
2. I'll help you migrate the database (15 min)
3. Update docker-compose.yml (2 min)
4. Continue scraping to cloud (same workflow)

Would you like me to help you set up Supabase now?

---

**Summary**: Your database is tiny (~7 MB for 6,041 workflows), so cloud storage is cheap/free. The real issue is your local disk being full (431 GB used). Clean Docker images first, then migrate DB to Supabase (free).
