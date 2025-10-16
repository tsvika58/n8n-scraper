# SUPABASE MIGRATION GUIDE
## Migrating N8N Scraper Database to Cloud

**Date**: October 12, 2025  
**Status**: Ready to migrate (export completed)  
**Export File**: `migration_to_supabase_20251012_213742.sql` (2.2 MB)

---

## ✅ **WHAT I'VE PREPARED:**

1. ✅ **Database exported**: 2.2 MB SQL file ready
2. ✅ **Backup created**: Safe rollback available
3. ✅ **Migration script**: Ready to import

---

## 📋 **YOUR NEXT STEPS:**

### **1. Create Supabase Project (2 minutes)**

Visit: https://supabase.com/dashboard

**Click "New Project" and fill in:**
- **Organization**: [Your existing org, or create new]
- **Name**: `n8n-workflow-scraper`
- **Database Password**: [Create a STRONG password - SAVE IT!]
- **Region**: Choose closest to you:
  - 🇺🇸 US East (Virginia) - fastest for US East Coast
  - 🇺🇸 US West (Oregon) - fastest for US West Coast
  - 🇪🇺 EU West (Ireland) - fastest for Europe
  - 🇦🇺 Southeast Asia (Singapore) - fastest for Asia
- **Pricing Plan**: Free

**Click "Create new project"** - Wait ~2 minutes

---

### **2. Get Connection String (1 minute)**

Once project is created:

1. Click **Settings** (gear icon in sidebar)
2. Click **Database**
3. Scroll to **Connection string** section
4. Select **URI** tab
5. Copy the full connection string (looks like):
   ```
   postgresql://postgres.xxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```
6. **IMPORTANT**: Replace `[YOUR-PASSWORD]` with the actual password you created

---

### **3. Give Me Connection Details**

**I need from you:**
```
Host: db.xxxxxxxxxxxxx.supabase.co
Password: [your password]
```

**OR just paste the full connection string:**
```
postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

---

## 🔧 **WHAT I'LL DO NEXT (Automated):**

Once you provide the connection string, I'll:

1. ✅ **Test connection** (verify Supabase is reachable)
2. ✅ **Import database** (upload 2.2 MB SQL file)
3. ✅ **Update docker-compose.yml** (point to Supabase)
4. ✅ **Restart containers** (connect to cloud)
5. ✅ **Verify migration** (test all dashboards)
6. ✅ **Remove local PostgreSQL** (free up space)

**Estimated time**: 10 minutes

---

## 🔒 **SECURITY NOTE:**

Your connection string contains your password. After migration, I'll:
- ✅ Store it in `.env` file (not committed to Git)
- ✅ Add `.env` to `.gitignore`
- ✅ Keep it secure

**Never share your Supabase password publicly!**

---

## 💾 **ROLLBACK PLAN:**

If anything goes wrong:
```bash
# Restore local database from backup
docker exec -i n8n-scraper-database psql -U scraper_user -d n8n_scraper < backups/pre_production_comprehensive_20251012_205410.sql

# Revert docker-compose.yml to local database
git checkout docker-compose.yml

# Restart
docker-compose restart
```

---

## 📊 **BEFORE & AFTER COMPARISON:**

### Before (Local):
- Database: On your Mac (uses 137 MB disk)
- Backups: On your Mac (uses 2-10 GB)
- Accessible: Only from your Mac
- Risk: If Mac crashes, data could be lost

### After (Supabase):
- Database: In cloud (uses 0 local disk!)
- Backups: Automatic (Supabase handles it)
- Accessible: From anywhere (bonus!)
- Risk: Supabase handles redundancy & backups

---

## ⚡ **READY TO PROCEED?**

**Just tell me:**
1. Your Supabase project is created? (Yes/No)
2. Your connection string (paste here)

Then I'll handle the entire migration automatically!

**Or, if you prefer:**
- I can wait while you create the project
- I can give you the exact commands to run manually
- I can explain any step in more detail

What would you like to do?






