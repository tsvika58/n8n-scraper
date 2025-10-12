# SCRAPE-015: Production Operations Guide

## Quick Start

### Start All Dashboards
```bash
docker exec -d n8n-scraper-app bash /app/scripts/start-dashboards.sh
```

### Check Dashboard Status
```bash
# Real-time Scraping Dashboard (5002)
curl -s http://localhost:5002 | grep -o "<title>.*</title>"

# Database Viewer (5004)
curl -s http://localhost:5004/api/stats
```

### Manual Dashboard Control
```bash
# Start Database Viewer
docker exec -d n8n-scraper-app python /app/scripts/db-viewer.py

# Start Real-time Dashboard  
docker exec -d n8n-scraper-app python /app/scripts/realtime-dashboard.py

# Start Terminal Monitor
docker exec -it n8n-scraper-app python /app/scripts/terminal-monitor.py
```

## Dashboard Access Points

| Dashboard | Port | URL | Purpose |
|-----------|------|-----|---------|
| Real-time Scraping | 5002 | http://localhost:5002 | Live scraping progress |
| Database Viewer | 5004 | http://localhost:5004 | Sortable workflow database |
| Terminal Monitor | - | (in terminal) | CLI live statistics |

## Container Survivability

### Current Setup ✅
- **Container**: `n8n-scraper-app`
- **Restart Policy**: `unless-stopped`
- **Volume Mounts**:
  - `./scripts:/app/scripts` (dashboards persist)
  - `./data:/app/data` (scraping data)
  - `./logs:/app/logs` (logging)
- **Database**: Named volume `n8n-scraper-postgres-data` (survives restarts)

### After Container Restart
Dashboards DON'T auto-start (by design - you control when they run).

**To restart dashboards after container restart:**
```bash
docker exec -d n8n-scraper-app bash /app/scripts/start-dashboards.sh
```

### Why Not Auto-Start?
1. You may want to run scraping WITHOUT dashboards (headless)
2. Dashboards use resources (RAM, CPU)
3. Flexible: start only what you need
4. Clean logs: dashboards don't spam container logs

## Production Scraping Workflow

### 1. Prepare Environment
```bash
# Ensure containers are up
docker-compose ps

# Check database health
docker exec n8n-scraper-database pg_isready

# Verify scripts are mounted
docker exec n8n-scraper-app ls -la /app/scripts/ | grep db-viewer
```

### 2. Start Dashboards
```bash
# Start all dashboards
docker exec -d n8n-scraper-app bash /app/scripts/start-dashboards.sh

# Verify they're running
curl http://localhost:5002
curl http://localhost:5004/api/stats
```

### 3. Run Small-Scale Test
```bash
# Test 5 real workflows
docker exec n8n-scraper-app python /app/scripts/test_5_real_e2e_scrape_015.py

# Watch real-time dashboard
open http://localhost:5002

# View results in database
open http://localhost:5004
```

### 4. Run Production Scraping
```bash
# Option A: Test 10 workflows
docker exec n8n-scraper-app python /app/scripts/test_10_real_workflows_scrape_015.py

# Option B: Full production run (100+ workflows)
docker exec n8n-scraper-app python /app/scripts/test_100_real_e2e.py

# Option C: Terminal monitor (live stats)
docker exec -it n8n-scraper-app python /app/scripts/terminal-monitor.py
```

## Testing Checklist (SCRAPE-015)

### ✅ Pre-Scraping Tests

- [ ] **Container Health**
  ```bash
  docker-compose ps
  # Expected: All containers "Up" and "healthy"
  ```

- [ ] **Database Connectivity**
  ```bash
  docker exec n8n-scraper-database pg_isready
  curl http://localhost:5004/api/stats
  # Expected: Connection successful, stats returned
  ```

- [ ] **Database Viewer - Sortable**
  ```bash
  # Open browser: http://localhost:5004
  # Click "Workflow ID" header
  # Expected: Numbers sort 1, 2, 3... (not 1, 10, 100)
  ```

- [ ] **Workflow Details - Clickable**
  ```bash
  # Open browser: http://localhost:5004
  # Click any workflow ID number
  # Expected: Detail page opens with complete data
  ```

- [ ] **Real-time Dashboard**
  ```bash
  curl http://localhost:5002
  # Expected: HTML with "N8N Scraper Monitor"
  ```

- [ ] **Terminal Monitor**
  ```bash
  docker exec -it n8n-scraper-app python /app/scripts/terminal-monitor.py
  # Expected: Live statistics display
  # Press Ctrl+C to exit
  ```

### ✅ Small-Scale E2E Test (5 Workflows)

```bash
# Run test
docker exec n8n-scraper-app python /app/scripts/test_5_real_e2e_scrape_015.py

# Expected results:
# - All 5 workflows scraped
# - Real-time dashboard shows progress
# - Database viewer displays results
# - Clickable workflow IDs work
# - Sorting works correctly
```

### ✅ Post-Test Verification

- [ ] **Database Persistence**
  ```bash
  # Restart container
  docker restart n8n-scraper-app
  
  # Restart dashboards
  docker exec -d n8n-scraper-app bash /app/scripts/start-dashboards.sh
  
  # Check data still there
  curl http://localhost:5004/api/stats
  # Expected: Same workflow count as before restart
  ```

- [ ] **Backup System**
  ```bash
  ./scripts/backup.sh
  # Expected: Backup created in ./backups/postgres/
  ```

- [ ] **Volume Integrity**
  ```bash
  docker volume inspect n8n-scraper-postgres-data
  # Expected: Volume exists and mounted
  ```

## Troubleshooting

### Dashboards Not Responding

```bash
# Check if processes are running
docker exec n8n-scraper-app python -c "import psutil; [print(f'PID {p.pid}: {p.cmdline()}') for p in psutil.process_iter() if 'python' in p.name()]"

# Kill stuck processes
docker exec n8n-scraper-app python -c "import os; os.system('killall python 2>/dev/null || true')"

# Restart dashboards
docker exec -d n8n-scraper-app bash /app/scripts/start-dashboards.sh
```

### Database Connection Issues

```bash
# Check database is up
docker exec n8n-scraper-database pg_isready

# Check connection from app container
docker exec n8n-scraper-app python -c "import psycopg2; conn = psycopg2.connect(host='n8n-scraper-database', port=5432, database='n8n_scraper', user='scraper_user', password='scraper_pass'); print('✅ Connected')"
```

### Port Conflicts

```bash
# Check what's using port 5004
lsof -i :5004

# If needed, change port in docker-compose.yml:
# ports:
#   - "5005:5004"  # Map to different host port
```

## Performance Monitoring

### Resource Usage
```bash
docker stats n8n-scraper-app n8n-scraper-database
```

### Database Stats
```bash
docker exec -it n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    COUNT(*) as total_workflows,
    COUNT(*) FILTER (WHERE layer1_success AND layer2_success AND layer3_success) as completed,
    AVG(processing_time) as avg_time
FROM workflows;"
```

### Logs
```bash
# Container logs
docker logs n8n-scraper-app --tail 100 -f

# Database logs  
docker logs n8n-scraper-database --tail 100 -f

# Application logs
tail -f logs/*.log
```

## Emergency Procedures

### Complete System Restart
```bash
# 1. Stop everything
docker-compose down

# 2. Start infrastructure
docker-compose up -d

# 3. Wait for health check
sleep 30
docker-compose ps

# 4. Start dashboards
docker exec -d n8n-scraper-app bash /app/scripts/start-dashboards.sh

# 5. Verify
curl http://localhost:5004/api/stats
```

### Database Recovery
```bash
# Restore from backup
./scripts/restore.sh --latest

# Or specific backup
./scripts/restore.sh n8n_scraper_backup_20251012_120000
```

### Clean Slate (Preserves Data)
```bash
# Stop containers
docker-compose down

# Rebuild image
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Data persists via volumes!
```

## Production Readiness Checklist

Before signing off SCRAPE-015:

- [ ] ✅ Database viewer sortable (numerical sorting)
- [ ] ✅ Workflow IDs clickable (detail pages work)
- [ ] ✅ Real-time dashboard operational
- [ ] ✅ Terminal monitor functional
- [ ] ✅ Small-scale test (5 workflows) successful
- [ ] ✅ Data persists after container restart
- [ ] ✅ Backup system verified
- [ ] ✅ All ports accessible (5002, 5004)
- [ ] ✅ Documentation complete
- [ ] ✅ Git committed

## Sign-Off Criteria

**Ready for production scraping when:**
1. All dashboards respond to HTTP requests
2. 5-workflow test completes successfully
3. Sorting works (1, 2, 3... not 1, 10, 100)
4. Workflow details clickable and display data
5. Container restart preserves data
6. No manual setup required after restart (just start dashboards)

---

**Last Updated**: October 12, 2025  
**Task**: SCRAPE-015  
**Status**: Production Ready ✅

