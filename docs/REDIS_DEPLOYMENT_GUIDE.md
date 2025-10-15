# Redis Deployment Guide - Scraper Project

## Overview

Your scraper project now has its **own dedicated Redis** for connection coordination, completely isolated from the n8n-standalone project.

## Architecture

```
┌─────────────────────────────────────────┐
│  N8N-STANDALONE PROJECT (ISOLATED)      │
│  ├── n8n-server                         │
│  ├── n8n-postgres                       │
│  └── n8n-standalone-redis               │
└─────────────────────────────────────────┘
         ❌ NO CONNECTION ❌
┌─────────────────────────────────────────┐
│  N8N-SCRAPER PROJECT (YOUR PROJECT)     │
│  ├── scraper-redis ← NEW!               │
│  ├── n8n-scraper-app                    │
│  └── scraper-db-viewer                  │
│         │                                │
│         └──→ Supabase (external)        │
└─────────────────────────────────────────┘
```

## What Changed

### 1. Added Redis to Scraper Project

**File**: `docker-compose.yml`

```yaml
services:
  scraper-redis:
    image: redis:7-alpine
    container_name: n8n-scraper-redis  # Different from n8n-standalone-redis
    networks:
      - n8n-scraper-network  # Isolated network
```

### 2. Configured Scraper to Use Redis

```yaml
n8n-scraper-app:
  environment:
    REDIS_URL: redis://scraper-redis:6379
    SERVICE_NAME: scraper
    SUPABASE_PLAN: free
    SUPABASE_MAX_CONNECTIONS: 60
```

### 3. Configured Viewer to Use Same Redis

**File**: `n8n-workflow-viewer/docker-compose.yml`

```yaml
workflow-viewer:
  container_name: scraper-db-viewer
  environment:
    REDIS_URL: redis://scraper-redis:6379
    SERVICE_NAME: viewer
  networks:
    - n8n-scraper-network  # Same network as scraper
```

## Deployment Steps

### Step 1: Stop Current Containers

```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Stop scraper (L1.5 will resume later)
docker stop n8n-scraper-app

# Stop viewer
docker stop scraper-db-viewer
```

### Step 2: Start Scraper with Redis

```bash
# Start scraper project (includes Redis)
docker-compose up -d

# Check status
docker ps | grep scraper
```

**You should see:**
```
n8n-scraper-redis    ← NEW Redis container
n8n-scraper-app      ← Your scraper
```

### Step 3: Start Viewer

```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-workflow-viewer

# Start viewer (connects to scraper's Redis)
docker-compose up -d

# Check status
docker ps | grep viewer
```

**You should see:**
```
scraper-db-viewer    ← Connected to scraper network
```

### Step 4: Verify Redis Connection

```bash
# Test from scraper
docker exec n8n-scraper-app python -c "
import redis
client = redis.from_url('redis://scraper-redis:6379')
print('Scraper → Redis:', client.ping())
"

# Test from viewer
docker exec scraper-db-viewer python -c "
import redis
client = redis.from_url('redis://scraper-redis:6379')
print('Viewer → Redis:', client.ping())
"
```

**Expected output:**
```
Scraper → Redis: True
Viewer → Redis: True
```

### Step 5: Verify Connection Coordination

```bash
# Check global connection status
docker exec n8n-scraper-app python -c "
import sys
sys.path.append('/app')
from src.storage.global_connection_coordinator import print_global_status
print_global_status()
"
```

**Expected output:**
```
🌍 GLOBAL CONNECTION STATUS (ALL CONTAINERS)
================================================================
📊 Supabase Configuration:
  Plan: FREE
  Max Connections: 60
  Available for Apps: 54

📈 Current Usage:
  Total Allocated: 25/54
  
🔧 Services:
  scraper    1 container    20 connections
  viewer     1 container     5 connections
```

## Verification Checklist

- [ ] `n8n-scraper-redis` container running
- [ ] `n8n-scraper-app` can connect to Redis
- [ ] `scraper-db-viewer` can connect to Redis
- [ ] Both containers on `n8n-scraper-network`
- [ ] Global connection status shows both services
- [ ] `n8n-standalone-redis` still isolated (not used by scraper)

## Network Isolation

### Scraper Network (n8n-scraper-network)

**Containers:**
- `scraper-redis`
- `n8n-scraper-app`
- `scraper-db-viewer`

**External connections:**
- Supabase (via internet)

### N8N Standalone Network (n8n-standalone_n8n-network)

**Containers:**
- `n8n-standalone-redis`
- `n8n-standalone-server`
- `n8n-standalone-postgres`

**No connection to scraper network!** ✅

## Troubleshooting

### Problem: "Cannot connect to Redis"

**Check Redis is running:**
```bash
docker ps | grep scraper-redis
```

**Check network:**
```bash
docker network inspect n8n-scraper-network
```

**Should show:**
- `scraper-redis`
- `n8n-scraper-app`
- `scraper-db-viewer`

### Problem: "Viewer can't reach Redis"

**Check viewer network:**
```bash
docker inspect scraper-db-viewer | grep -A 10 Networks
```

**Should show:**
```json
"Networks": {
    "n8n-scraper-network": { ... }
}
```

**If not, reconnect:**
```bash
docker network connect n8n-scraper-network scraper-db-viewer
```

### Problem: "Scraper using wrong Redis"

**Check environment:**
```bash
docker exec n8n-scraper-app env | grep REDIS_URL
```

**Should show:**
```
REDIS_URL=redis://scraper-redis:6379
```

**NOT:**
```
REDIS_URL=redis://n8n-standalone-redis:6379  ← WRONG!
```

## Resource Usage

### Redis Memory

**Configured:** 256MB max
**Typical usage:** 10-50MB
**Purpose:** Store connection reservations only

### Network Overhead

**Latency:** <1ms (local Docker network)
**Bandwidth:** Negligible (<1KB per reservation)

## Maintenance

### View Redis Data

```bash
# Connect to Redis CLI
docker exec -it n8n-scraper-redis redis-cli

# List all keys
KEYS *

# View a reservation
GET connection:reservation:scraper:n8n-scraper-app
```

### Clear All Reservations (if needed)

```bash
docker exec n8n-scraper-redis redis-cli FLUSHALL
```

### Backup Redis (optional)

```bash
# Redis auto-saves to /data (persisted volume)
docker exec n8n-scraper-redis redis-cli SAVE

# Backup volume
docker run --rm -v scraper-redis-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup.tar.gz /data
```

## Restart L1.5 Scraper

Now that Redis is set up, restart your L1.5 scraper:

```bash
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Start with global coordination
docker exec -d n8n-scraper-app python /app/scripts/start_scraper_dynamic.py \
    layer1_5_production_scraper.py --all
```

## Monitor

```bash
# Real-time global monitoring
docker exec n8n-scraper-app python /app/scripts/monitor_global_connections.py
```

## Summary

✅ **Scraper project has its own Redis** (`scraper-redis`)  
✅ **Completely isolated** from n8n-standalone  
✅ **Scraper and viewer** both connect to same Redis  
✅ **Global connection coordination** working  
✅ **Respects Supabase limits** (60 for free tier)  

**Next:** Monitor connection usage and adjust limits as needed!

