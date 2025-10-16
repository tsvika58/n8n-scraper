# Reserved Connection Management

## 🎯 Overview

The database connection pool is now configured to **always reserve 5 connections** for ad-hoc work (development, manual queries, stopping processes), ensuring you never get locked out when automation processes are running.

## 📊 Connection Pool Configuration

### **Total Configuration (60 Supabase Connections)**

```
Total Supabase Limit: 60 connections
├─ Automation Pool: 50 connections
├─ Automation Overflow: 5 connections (buffer)
└─ Reserved for Ad-hoc: 5 connections (ALWAYS AVAILABLE)
```

### **Breakdown**

| **Pool** | **Connections** | **Purpose** | **Availability** |
|----------|----------------|-------------|------------------|
| **Automation Base** | 50 | Scraping, monitoring, automated tasks | Limited by usage |
| **Automation Overflow** | 5 | Buffer for peak automation load | Limited by usage |
| **Ad-hoc Reserved** | 5 | Development, manual queries, admin | **ALWAYS AVAILABLE** |
| **TOTAL** | 60 | Full Supabase limit | - |

## 🔒 How Reserved Connections Work

### **Automation Pool (55 max connections)**
- Base pool: 50 connections
- Overflow: 5 connections (used only when base pool is full)
- **Maximum automation can use**: 55 connections

### **Reserved Pool (5 connections)**
- **NEVER** used by automation
- **ALWAYS** available for ad-hoc work
- Guaranteed access even when automation is at full capacity

## 💻 Usage

### **For Automation/Scraping (Default)**
```python
from src.storage.database import get_session

# Uses automation pool (50 + 5 overflow)
with get_session() as session:
    workflows = session.query(Workflow).all()
```

### **For Ad-hoc Work (Optional)**
```python
from src.storage.database import get_session

# Explicitly use ad-hoc priority (same pool, but documented intent)
with get_session(priority='adhoc') as session:
    workflows = session.query(Workflow).all()
```

### **Check Connection Status**
```bash
cd shared-tools/n8n-scraper
python scripts/check_connection_status.py
```

**Output Example:**
```
🔌 DATABASE CONNECTION STATUS
============================================================
📊 Total Supabase Limit: 60 connections
   └─ Reserved for Ad-hoc: 5 (always available)
   └─ Automation Pool: 50 + 5 overflow

🤖 Automation (Scraping/Monitoring):
   ├─ In Use: 32/55
   ├─ Available: 23
   └─ Overflow Active: 0

👤 Ad-hoc (Development/Manual):
   └─ Guaranteed Available: 5 connections

✅ Healthy: 5 connections always available for ad-hoc work
============================================================
```

## 🛡️ Protection Guarantees

### **1. Ad-hoc Work Always Available**
- **5 connections reserved** exclusively for manual/development work
- Automation **cannot** use these 5 connections
- You can **always** connect to the database for:
  - Manual queries
  - Stopping processes
  - Development work
  - Database administration

### **2. Automation Limits**
- **Base pool**: 50 connections
- **Max overflow**: 5 connections
- **Hard limit**: 55 connections total
- **Cannot exceed** 55 connections, leaving 5 reserved

### **3. Timeout Protection**
- Connection timeout: 60 seconds
- If automation pool is full, requests wait up to 60s
- After 60s, error is raised (prevents infinite waiting)

## 📈 Monitoring

### **Real-time Status Check**
```bash
python scripts/check_connection_status.py
```

### **From Python Code**
```python
from src.storage.database import get_database_stats

stats = get_database_stats()
print(f"Automation in use: {stats['automation_in_use']}/{stats['total_automation_capacity']}")
print(f"Ad-hoc available: {stats['adhoc_guaranteed_available']}")
```

### **Key Metrics**
- `automation_in_use`: Current automation connections in use
- `automation_available`: Available automation connections
- `adhoc_guaranteed_available`: Always 5 (never changes)
- `total_automation_capacity`: 55 (50 base + 5 overflow)

## 🚨 Warning Scenarios

### **⚠️ WARNING: Automation Using Overflow**
```
Automation in use: 52/55 (overflow active)
```
**Meaning**: Automation pool (50) is full, using overflow buffer
**Action**: Monitor closely, consider optimizing connection usage

### **🚨 CRITICAL: Automation Pool Exhausted**
```
Automation in use: 55/55 (pool exhausted)
```
**Meaning**: All automation connections in use
**Impact**: New automation requests will wait (up to 60s timeout)
**Good news**: Ad-hoc connections (5) still available!

## 🔧 Configuration

All configuration is in `src/storage/database.py`:

```python
# Connection pool configuration
TOTAL_CONNECTIONS = 60              # Total Supabase limit
RESERVED_CONNECTIONS = 5            # Always keep for ad-hoc
AUTOMATION_POOL_SIZE = 50           # 60 - 5 - 5
AUTOMATION_MAX_OVERFLOW = 5         # Small buffer
```

### **To Adjust Reserved Connections**

Edit `src/storage/database.py`:
```python
RESERVED_CONNECTIONS = 10  # Increase to 10 for more ad-hoc capacity
```

The automation pool will automatically adjust:
- AUTOMATION_POOL_SIZE = 60 - 10 - 5 = 45
- Total automation capacity = 45 + 5 = 50

## 🎯 Best Practices

### **1. Use Connection Status Monitoring**
```bash
# Before running large scraping jobs
python scripts/check_connection_status.py

# Monitor during scraping
watch -n 5 "cd shared-tools/n8n-scraper && python scripts/check_connection_status.py"
```

### **2. Optimize Connection Usage**
- Close connections promptly after use
- Use context managers (`with get_session()`)
- Avoid long-running transactions
- Batch operations when possible

### **3. Ad-hoc Work Best Practices**
- Ad-hoc connections are always available
- No need to stop automation for manual queries
- Safe to run admin tasks anytime
- Can stop processes without connection issues

### **4. Automation Best Practices**
- Monitor automation pool usage
- Keep individual connections short-lived
- Use connection pooling efficiently
- Add delays between operations if needed

## 🔍 Troubleshooting

### **Problem: "Connection pool exhausted"**
**Solution**: This only affects automation (55 connections max). Ad-hoc work (5 connections) is still available.

### **Problem: "Timeout waiting for connection"**
**Cause**: Automation pool (55) is full, new requests waiting
**Solution**: 
1. Check connection status: `python scripts/check_connection_status.py`
2. Optimize connection usage in automation
3. Increase pool size if needed (reduce RESERVED_CONNECTIONS)

### **Problem: "Can't connect for manual work"**
**This should NEVER happen** with reserved connections!
**If it does**:
1. Check Supabase is online
2. Verify credentials
3. Check network connectivity

## 📊 Example Scenarios

### **Scenario 1: Normal Operation**
```
Automation: 30/55 in use
Ad-hoc: 5 available
Status: ✅ Healthy
```

### **Scenario 2: High Load**
```
Automation: 50/55 in use (using overflow)
Ad-hoc: 5 available
Status: ⚠️ High usage, but ad-hoc still available
```

### **Scenario 3: Peak Load**
```
Automation: 55/55 in use (pool exhausted)
Ad-hoc: 5 available
Status: 🚨 Automation pool full, but you can still do manual work!
```

## ✅ Benefits

1. **Never Locked Out**: Always have 5 connections for manual work
2. **Safe Operations**: Can stop processes anytime
3. **Development Friendly**: Can develop while automation runs
4. **Clear Limits**: Automation can't exceed 55 connections
5. **Transparent Monitoring**: Easy to see current usage

## 🚀 Quick Reference

```bash
# Check connection status
python scripts/check_connection_status.py

# View in real-time (updates every 5 seconds)
watch -n 5 "cd shared-tools/n8n-scraper && python scripts/check_connection_status.py"

# From Python
from src.storage.database import print_connection_status
print_connection_status()
```

---

**Summary**: You now have **5 guaranteed connections** always available for ad-hoc work, while automation can use up to 55 connections. This ensures you never get locked out of the database!

