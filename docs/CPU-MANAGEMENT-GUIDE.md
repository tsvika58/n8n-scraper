# CPU Management Guide - N8N Scraper

## 🚨 CURRENT STATUS (2025-10-12)

**Container:** n8n-scraper-app  
**CPU Usage:** 0.05% (IDLE)  
**Memory:** 69 MB / 4 GB (1.69%)  
**Status:** ✅ NORMAL

---

## 📊 EXPECTED CPU USAGE PATTERNS

### **Idle State (Dashboards Only)**
- **CPU:** 0.05% - 0.5%
- **Memory:** 50-100 MB
- **Scenario:** Dashboards running, no active scraping

### **Light Scraping (1-5 workflows)**
- **CPU:** 50% - 150%
- **Memory:** 200-500 MB
- **Scenario:** Sequential processing, few concurrent browsers

### **Production Scraping (20+ workflows, 3 concurrent)**
- **CPU:** 150% - 300% ⚠️ **EXPECTED**
- **Memory:** 500 MB - 1.5 GB
- **Scenario:** Full pipeline with Playwright browsers, multimodal processing

### **Heavy Load (100+ workflows, batch mode)**
- **CPU:** 200% - 400% ⚠️ **EXPECTED**
- **Memory:** 1-2 GB
- **Scenario:** Large batch processing, maximum concurrency

---

## 🎛️ CPU CONTROL MECHANISMS

### **1. Concurrency Control (MOST IMPORTANT)**

**Current Setting:** `MAX_CONCURRENT=3`

```bash
# In docker-compose.yml or .env
MAX_CONCURRENT=3  # Default (200-300% CPU)
MAX_CONCURRENT=2  # Moderate (100-200% CPU)
MAX_CONCURRENT=1  # Low CPU (50-100% CPU)
```

**To Change Immediately:**
```bash
# Stop scraping
docker exec n8n-scraper-app pkill -f "python.*orchestrator"

# Update environment
docker exec n8n-scraper-app sh -c 'export MAX_CONCURRENT=2'

# Restart with new limit (if using orchestrator)
```

**Permanent Change:**
```yaml
# docker-compose.yml
environment:
  - MAX_CONCURRENT=2  # Change from 3 to 2
```

Then:
```bash
docker-compose up -d --force-recreate n8n-scraper-app
```

---

### **2. Rate Limiting**

**Current Setting:** `RATE_LIMIT=2.0` (2 requests/second per worker)

```bash
# In docker-compose.yml or .env
RATE_LIMIT=2.0  # Default (fast)
RATE_LIMIT=1.0  # Slower (reduces CPU)
RATE_LIMIT=0.5  # Very slow (minimal CPU)
```

---

### **3. Batch Size Control**

**Current Setting:** `batch_size=5` (in WorkflowOrchestrator)

**Location:** `src/orchestrator/workflow_orchestrator.py`

```python
# Current
orchestrator = WorkflowOrchestrator(
    repository=repository,
    batch_size=5,  # Process 5 workflows per batch
    max_retries=2
)

# For lower CPU
orchestrator = WorkflowOrchestrator(
    repository=repository,
    batch_size=2,  # Process 2 workflows per batch
    max_retries=2
)
```

---

### **4. Headless Browser Optimization**

**Current Setting:** `HEADLESS=true` ✅ (already optimized)

```bash
# In docker-compose.yml
HEADLESS=true  # 30-40% less CPU than headful mode
```

---

### **5. Docker CPU Limits**

**Add CPU Constraints to Container:**

```yaml
# docker-compose.yml
services:
  n8n-scraper-app:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Limit to 2 CPU cores (200%)
          memory: 2G       # Limit memory to 2GB
        reservations:
          cpus: '0.5'      # Reserve 0.5 cores
          memory: 512M
```

**Apply:**
```bash
docker-compose up -d --force-recreate n8n-scraper-app
```

---

### **6. Process Priority (Nice Level)**

**Run scraping with lower priority:**

```bash
# Inside container
docker exec n8n-scraper-app nice -n 10 python /app/scripts/production_test_20_workflows.py
```

`nice` values:
- `-20` = Highest priority (more CPU)
- `0` = Normal priority (default)
- `19` = Lowest priority (less CPU)

---

## 🔧 RECOMMENDED CONFIGURATIONS

### **Development/Testing (Low CPU)**
```yaml
environment:
  - MAX_CONCURRENT=1
  - RATE_LIMIT=1.0
  - HEADLESS=true
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
```

**Expected CPU:** 50-100%

---

### **Production (Balanced)**
```yaml
environment:
  - MAX_CONCURRENT=2
  - RATE_LIMIT=1.5
  - HEADLESS=true
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

**Expected CPU:** 100-200%

---

### **Aggressive Scraping (High Performance)**
```yaml
environment:
  - MAX_CONCURRENT=3
  - RATE_LIMIT=2.0
  - HEADLESS=true
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 3G
```

**Expected CPU:** 200-400%

---

## 🛠️ TROUBLESHOOTING

### **CPU Stays High After Scraping Stops**

**Check for zombie processes:**
```bash
docker exec n8n-scraper-app ps aux | grep -E "chromium|python"
```

**Kill zombie browsers:**
```bash
docker exec n8n-scraper-app pkill -f chromium
docker exec n8n-scraper-app pkill -f playwright
```

---

### **CPU Spikes During Idle**

**Check if dashboards are polling too frequently:**
```bash
# View dashboard processes
docker exec n8n-scraper-app ps aux | grep -E "dashboard|db-viewer"
```

**Dashboard refresh rates:**
- Real-time Dashboard: 5-second refresh (0.1-0.5% CPU)
- Database Viewer: On-demand (0.01% CPU when idle)

If dashboards are causing issues, restart them:
```bash
docker exec n8n-scraper-app python /app/scripts/clean-start-dashboards.py
```

---

### **Memory Leaks Causing CPU Issues**

**Check memory usage:**
```bash
docker stats n8n-scraper-app --no-stream
```

If memory is approaching limit:
```bash
# Restart container to clear memory
docker-compose restart n8n-scraper-app
```

---

## 📈 MONITORING RECOMMENDATIONS

### **Real-Time Monitoring**
```bash
# Continuous stats
docker stats n8n-scraper-app

# Every 5 seconds
watch -n 5 "docker stats n8n-scraper-app --no-stream"
```

### **CPU Alert Thresholds**
- **< 50%**: Idle/minimal activity ✅
- **50-150%**: Normal scraping ✅
- **150-300%**: Heavy scraping (expected during bursts) ⚠️
- **> 300%**: Investigate (possible runaway process) 🚨

---

## 🎯 IMMEDIATE ACTION PLAN FOR HIGH CPU

### **Step 1: Identify the Cause**
```bash
# Check what's running
docker exec n8n-scraper-app ps aux --sort=-%cpu | head -20

# Check for active scraping
docker exec n8n-scraper-app pgrep -af "workflow_orchestrator|production_test"
```

### **Step 2: Graceful Stop (if needed)**
```bash
# Stop active scraping gracefully
docker exec n8n-scraper-app pkill -SIGTERM -f "production_test"

# Wait 10 seconds, then check
sleep 10
docker stats n8n-scraper-app --no-stream
```

### **Step 3: Force Stop (if step 2 fails)**
```bash
# Kill all browsers
docker exec n8n-scraper-app pkill -9 -f chromium

# Kill all Python scrapers
docker exec n8n-scraper-app pkill -9 -f "layer.*extract"
```

### **Step 4: Verify & Restart Dashboards**
```bash
# Ensure dashboards are running
docker exec n8n-scraper-app python /app/scripts/clean-start-dashboards.py

# Verify CPU is back to normal
docker stats n8n-scraper-app --no-stream
```

---

## 💡 OPTIMIZATION TIPS

1. **Scrape During Off-Hours**: Schedule heavy scraping when system resources are available
2. **Use Batch Processing**: Process workflows in smaller batches with pauses
3. **Monitor & Adjust**: Start with conservative settings, increase as needed
4. **Database Optimization**: Ensure PostgreSQL has adequate resources (separate container)
5. **Network Caching**: Consider caching static content to reduce repeated downloads

---

## 📊 CPU BENCHMARKS (Reference)

| Task | Workflows | Concurrent | Time | Avg CPU | Peak CPU |
|------|-----------|------------|------|---------|----------|
| Idle (dashboards only) | 0 | 0 | - | 0.1% | 0.5% |
| Sequential scraping | 5 | 1 | 2.5 min | 60% | 90% |
| Parallel scraping | 20 | 3 | 2.8 min | 180% | 280% |
| Batch (100 workflows) | 100 | 3 | 15 min | 200% | 320% |

---

## ✅ SIGN-OFF CHECKLIST

- [x] CPU usage documented with expected ranges
- [x] Control mechanisms explained (concurrency, rate limiting, Docker limits)
- [x] Troubleshooting procedures provided
- [x] Monitoring recommendations included
- [x] Immediate action plan for high CPU
- [x] Configuration examples for different scenarios

---

**Last Updated:** 2025-10-12  
**Status:** ✅ PRODUCTION READY

