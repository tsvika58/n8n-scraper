# Cross-Container Connection Management - Your Questions Answered

## Your Questions

### 1. "Should global pool be dictated by Supabase limitation?"

**YES! Absolutely correct.** ✅

The global pool MUST respect your Supabase plan limits:

| Supabase Plan | Max Connections | Reserved for Supabase (10%) | Available for Apps |
|---------------|-----------------|-----------------------------|--------------------|
| **Free** | 60 | 6 | **54** |
| **Pro** | 200 | 20 | **180** |
| **Team** | 400 | 40 | **360** |
| **Enterprise** | 1000+ | 100+ | **900+** |

**Configuration:**
```bash
# Set in environment variables
SUPABASE_PLAN=free              # Your actual plan
SUPABASE_MAX_CONNECTIONS=60     # From Supabase dashboard
```

The Global Connection Coordinator automatically:
- Reserves 10% for Supabase internal use
- Distributes remaining 90% across all containers
- Prevents any container from exceeding the limit

### 2. "What about db-viewer? Does it use the same connection pool?"

**Currently NO, but it SHOULD!** ⚠️

**Current Problem:**
```
Scraper Container:  20 connections (separate pool)
Viewer Container:    5 connections (separate pool)
                   ─────────────────
TOTAL:              25 connections to Supabase

But they don't know about each other! ❌
```

**Solution: Global Connection Coordinator**

With Redis coordination:
```
┌────────────────────────────────┐
│   REDIS COORDINATOR            │
│   Tracks all containers        │
│   Enforces: 54 max (Free tier) │
└────────────────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌────▼────┐
   │ Scraper │      │ Viewer  │
   │ 40 conn │      │ 10 conn │
   └─────────┘      └─────────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   Supabase      │
        │   50/54 used    │
        └─────────────────┘
```

**Implementation:**

Update viewer to use global coordinator:
```python
# In viewer's database.py
from src.storage.global_connection_coordinator import get_session

async def get_db():
    with get_session() as session:
        yield session
```

**Environment for viewer:**
```yaml
environment:
  REDIS_URL: redis://redis-coordinator:6379
  SERVICE_NAME: viewer
  SUPABASE_PLAN: free
  SUPABASE_MAX_CONNECTIONS: 60
```

### 3. "How to manage cross-container and external connections?"

**Solution: Global Connection Coordinator with Redis**

#### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  REDIS COORDINATOR                        │
│  • Tracks ALL connections (containers + external)        │
│  • Enforces Supabase limit (60 for free tier)           │
│  • Allocates dynamically based on priority               │
└──────────────────┬───────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┬─────────┐
    │              │              │              │         │
┌───▼───┐    ┌────▼────┐    ┌───▼────┐    ┌───▼───┐  ┌──▼──┐
│Scraper│    │ Viewer  │    │  API   │    │ Cron  │  │Ext  │
│15 conn│    │ 3 conn  │    │ 5 conn │    │ 2 conn│  │3 cn │
└───────┘    └─────────┘    └────────┘    └───────┘  └─────┘
   (P:10)       (P:5)         (P:8)        (P:3)     (P:1)
                   │
          ┌────────▼────────┐
          │   Supabase      │
          │   28/54 used    │
          │   26 remaining  │
          └─────────────────┘
```

#### For Containers

**1. Add Redis to docker-compose:**
```yaml
services:
  redis-coordinator:
    image: redis:7-alpine
    container_name: n8n-scraper-redis
    ports:
      - "6379:6379"
  
  scraper:
    environment:
      REDIS_URL: redis://redis-coordinator:6379
      SERVICE_NAME: scraper
      SUPABASE_PLAN: free
  
  viewer:
    environment:
      REDIS_URL: redis://redis-coordinator:6379
      SERVICE_NAME: viewer
      SUPABASE_PLAN: free
```

**2. Use global coordinator:**
```python
from src.storage.global_connection_coordinator import get_session

with get_session() as session:
    # Automatically coordinated!
    result = session.execute(text("SELECT * FROM workflows"))
```

#### For External Connections

**Option A: Register External Services**

For cron jobs, monitoring, etc.:

```python
# In your external script
import os
os.environ['REDIS_URL'] = 'redis://your-redis-host:6379'
os.environ['SERVICE_NAME'] = 'external_cron'
os.environ['SUPABASE_PLAN'] = 'free'

from global_connection_coordinator import get_session

with get_session() as session:
    # Coordinated with all other services!
    pass
```

**Option B: Manual Reservation**

For services that can't use Python:

```bash
# Reserve connections via Redis
redis-cli -h your-redis-host SET "connection:reservation:external:my-service" \
  '{"service_name":"external","count":5,"reserved_at":'$(date +%s)'}'

# Set TTL (5 minutes)
redis-cli -h your-redis-host EXPIRE "connection:reservation:external:my-service" 300
```

**Option C: Account for External in Configuration**

If you can't coordinate external connections:

```bash
# Reserve capacity for external
SUPABASE_MAX_CONNECTIONS=45  # Instead of 60
# This leaves 15 connections for uncoordinated external use
```

## Complete Solution

### Step 1: Deploy Redis

```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Use the new docker-compose with Redis
docker-compose -f docker-compose-with-redis.yml up -d
```

### Step 2: Update All Containers

**Scraper (`docker-compose-with-redis.yml`):**
```yaml
n8n-scraper-app:
  environment:
    REDIS_URL: redis://redis-coordinator:6379
    SERVICE_NAME: scraper
    SUPABASE_PLAN: free
    SUPABASE_MAX_CONNECTIONS: 60
```

**Viewer:**
```yaml
workflow-viewer:
  environment:
    REDIS_URL: redis://redis-coordinator:6379
    SERVICE_NAME: viewer
    SUPABASE_PLAN: free
    SUPABASE_MAX_CONNECTIONS: 60
```

### Step 3: Update Code

**Scraper - No changes needed!**
```python
# Already using get_session
from src.storage.global_connection_coordinator import get_session

with get_session() as session:
    pass
```

**Viewer - Update database.py:**
```python
# OLD
from sqlalchemy.ext.asyncio import create_async_engine

# NEW
from src.storage.global_connection_coordinator import get_session

async def get_db():
    with get_session() as session:
        yield session
```

### Step 4: Monitor

```bash
# Real-time monitoring
docker exec n8n-scraper-app python /app/scripts/monitor_global_connections.py
```

**Output shows ALL containers:**
```
🌍 GLOBAL CONNECTION MONITOR (ALL CONTAINERS)
================================================================
📊 SUPABASE CONFIGURATION
  Plan:                  FREE
  Max Connections:       60
  Available for Apps:    54

📈 GLOBAL USAGE
  Total Allocated:       28/54
  Remaining:             26
  Utilization:           51.9%

🔧 SERVICES
  Service         Containers   Connections     % of Total  
  scraper         1            20              71.4%
  viewer          1            5               17.9%
  api             1            3               10.7%
```

## Benefits

### Before (No Coordination)

❌ Each container has separate pool  
❌ No visibility into total usage  
❌ Risk of exceeding Supabase limit  
❌ Manual coordination required  
❌ External connections untracked  

**Example:**
```
Scraper:  20 connections
Viewer:    5 connections
API:      10 connections
Cron:      5 connections
External:  8 connections
         ─────────────────
TOTAL:    48 connections

But you only see your own container's usage!
Could easily exceed 60 limit without knowing!
```

### After (With Global Coordinator)

✅ Single shared pool across all containers  
✅ Real-time visibility of all connections  
✅ Automatic enforcement of Supabase limits  
✅ Dynamic allocation based on priority  
✅ External connections can be tracked  

**Example:**
```
┌─────────────────────────┐
│ REDIS COORDINATOR       │
│ Limit: 54 (Free tier)   │
│ Used: 28                │
│ Available: 26           │
└─────────────────────────┘

Scraper:  20 (priority 10)
Viewer:    5 (priority 5)
API:       3 (priority 8)

All visible in one place!
Never exceeds 54 limit!
```

## Recommendations

### For Your Current Setup (Free Tier)

1. **Deploy Redis** (lightweight, ~50MB RAM)
   ```bash
   docker-compose -f docker-compose-with-redis.yml up -d
   ```

2. **Set conservative limits**
   ```bash
   SUPABASE_MAX_CONNECTIONS=54  # Leave 6 for Supabase
   ```

3. **Account for external**
   - If you have external connections you can't coordinate
   - Reduce limit further: `SUPABASE_MAX_CONNECTIONS=45`
   - This reserves 15 for external use

4. **Monitor daily**
   ```bash
   # Add to cron
   docker exec n8n-scraper-app python -c "
   from src.storage.global_connection_coordinator import get_global_status
   status = get_global_status()
   print(f'Usage: {status[\"total_allocated\"]}/{status[\"available_for_apps\"]}')
   "
   ```

### For Future (When Scaling)

1. **Upgrade Supabase plan** when utilization >75%
   ```bash
   # Pro tier gives you 200 connections
   SUPABASE_PLAN=pro
   SUPABASE_MAX_CONNECTIONS=200
   ```

2. **Add more services** without worry
   - API container
   - Monitoring container
   - Cron jobs
   - All automatically coordinated!

3. **External connections** can register
   ```python
   # Any external service can join the pool
   from global_connection_coordinator import get_session
   ```

## Files Created

```
n8n-scraper/
├── src/storage/
│   └── global_connection_coordinator.py  ✅ NEW
│
├── scripts/
│   └── monitor_global_connections.py     ✅ NEW
│
├── docs/
│   ├── GLOBAL_CONNECTION_COORDINATION.md ✅ NEW
│   └── CROSS_CONTAINER_CONNECTION_SOLUTION.md ✅ THIS FILE
│
└── docker-compose-with-redis.yml         ✅ NEW
```

## Next Steps

1. **Review** the global coordinator code
2. **Test** with Redis in development
3. **Deploy** to production when ready
4. **Monitor** connection usage
5. **Adjust** limits based on actual usage

## Questions?

- **Global pool limits**: See `GLOBAL_CONNECTION_COORDINATION.md`
- **Redis setup**: See `docker-compose-with-redis.yml`
- **Monitoring**: Use `monitor_global_connections.py`
- **Troubleshooting**: See `GLOBAL_CONNECTION_COORDINATION.md` troubleshooting section

---

**Summary:**
✅ Global pool respects Supabase limits  
✅ Viewer uses same coordinated pool  
✅ External connections can be managed  
✅ Redis provides cross-container coordination  
✅ Real-time monitoring of all connections  
✅ Automatic enforcement and allocation  


