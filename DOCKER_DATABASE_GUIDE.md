# N8N Scraper - Docker & Database Quick Reference

**Production-Grade Setup for Maximum Reliability**

---

## 🚀 **QUICK START**

```bash
# Start everything
./scripts/start.sh

# Initialize database (first time only)
./scripts/db-init.sh

# Run a scraping job
docker-compose run --rm n8n-scraper-app python scripts/your_script.py

# Stop gracefully
./scripts/stop.sh
```

---

## 📊 **DATABASE OPERATIONS**

### **Daily Operations**

```bash
# Backup database
./scripts/backup.sh

# Monitor performance
./scripts/db-monitor.sh

# Check health
./scripts/health-check.sh

# Run maintenance (weekly recommended)
./scripts/db-maintain.sh
```

### **Recovery Operations**

```bash
# List available backups
./scripts/restore.sh --list

# Restore latest backup
./scripts/restore.sh --latest

# Restore specific backup
./scripts/restore.sh n8n_scraper_backup_20251011_175016

# Restore complete volume (disaster recovery)
./scripts/restore.sh --latest --volume
```

### **Direct Database Access**

```bash
# Interactive psql
docker exec -it n8n-scraper-database psql -U scraper_user -d n8n_scraper

# Run SQL query
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "SELECT COUNT(*) FROM workflows;"

# Dump specific table
docker exec n8n-scraper-database pg_dump -U scraper_user -d n8n_scraper -t workflows > workflows.sql
```

---

## 🐳 **DOCKER OPERATIONS**

### **Container Management**

```bash
# Start services
docker-compose up -d                              # Production
docker-compose --profile dev up -d                # With pgAdmin
docker-compose --profile analysis up -d           # With Jupyter
docker-compose --profile dev --profile analysis up -d  # Full dev environment

# Stop services
docker-compose stop                               # Graceful stop
docker-compose down                               # Stop and remove containers
docker-compose down -v                            # Stop, remove, and DELETE ALL DATA (⚠️ DANGER)

# Restart services
docker-compose restart n8n-scraper-database
docker-compose restart n8n-scraper-app
```

### **Monitoring**

```bash
# Container status
docker-compose ps

# Resource usage
docker stats n8n-scraper-app n8n-scraper-database

# Logs (live)
docker-compose logs -f n8n-scraper-app
docker-compose logs -f n8n-scraper-database

# Logs (last 100 lines)
docker-compose logs --tail=100 n8n-scraper-app
```

### **Development Tools**

```bash
# pgAdmin (Database GUI)
# URL: http://localhost:8080
# Email: admin@n8n-scraper.local
# Password: admin123
docker-compose --profile dev up -d n8n-scraper-db-admin

# Jupyter (Data Analysis)
# URL: http://localhost:8888
# Token: n8n-scraper-2025
docker-compose --profile analysis up -d n8n-scraper-jupyter

# Execute commands in app container
docker exec -it n8n-scraper-app bash
docker exec -it n8n-scraper-app python scripts/your_script.py
```

---

## 🔧 **TROUBLESHOOTING**

### **Database Won't Start**

```bash
# Check logs
docker-compose logs n8n-scraper-database

# Check if port is in use
lsof -i :5432

# Force restart
docker-compose down
docker-compose up -d n8n-scraper-database

# Nuclear option: rebuild
docker-compose down -v
docker-compose up --build -d
./scripts/db-init.sh
```

### **App Can't Connect to Database**

```bash
# Verify database is healthy
docker exec n8n-scraper-database pg_isready -U scraper_user -d n8n_scraper

# Check network
docker network inspect n8n-scraper_n8n-scraper-network

# Check environment variables
docker exec n8n-scraper-app env | grep DATABASE_URL

# Test connection from app
docker exec n8n-scraper-app python -c "
from src.storage.database import engine
engine.connect()
print('Connection OK')
"
```

### **Performance Issues**

```bash
# Check resource usage
docker stats

# Monitor database
./scripts/db-monitor.sh

# Run maintenance
./scripts/db-maintain.sh

# Check cache hit ratio (should be >90%)
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
FROM pg_statio_user_tables;
"
```

### **Out of Disk Space**

```bash
# Check disk usage
df -h
du -sh backups/
du -sh data/

# Clean old backups (keeps last 30 days)
./scripts/backup.sh  # Automatically cleans old backups

# Clean Docker system
docker system prune -a --volumes  # ⚠️ WARNING: Removes ALL unused Docker data

# Clean specific volumes
docker volume ls
docker volume rm <volume-name>
```

---

## 📈 **PERFORMANCE TUNING**

### **Database Configuration**

The PostgreSQL container is pre-configured with optimal settings in `docker-compose.yml`:

- **shared_buffers**: 256MB (25% of 1GB RAM)
- **effective_cache_size**: 768MB (75% of 1GB RAM)
- **work_mem**: 16MB
- **maintenance_work_mem**: 128MB
- **max_connections**: 100
- **random_page_cost**: 1.1 (SSD optimized)

### **Monitoring Key Metrics**

```bash
# Connection pool stats
./scripts/db-monitor.sh

# Query performance
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Index usage
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
"
```

---

## 🔐 **SECURITY BEST PRACTICES**

### **Production Deployment**

1. **Change Default Passwords**
   ```bash
   # Update in docker-compose.yml:
   POSTGRES_PASSWORD: your-strong-password-here
   
   # Update pgAdmin password:
   PGADMIN_DEFAULT_PASSWORD: your-admin-password-here
   ```

2. **Restrict Port Access**
   ```yaml
   # In docker-compose.yml, remove port exposure or use:
   ports:
     - "127.0.0.1:5432:5432"  # Only localhost access
   ```

3. **Enable SSL/TLS** (for production)
   ```bash
   # Add to PostgreSQL environment:
   POSTGRES_SSL_CERT_FILE: /path/to/server.crt
   POSTGRES_SSL_KEY_FILE: /path/to/server.key
   ```

4. **Encrypt Backups**
   ```bash
   # Encrypt backup
   gpg --symmetric --cipher-algo AES256 backups/backup.tar.gz
   
   # Decrypt backup
   gpg --decrypt backups/backup.tar.gz.gpg > backups/backup.tar.gz
   ```

5. **Off-site Backups**
   ```bash
   # Rsync to remote server
   rsync -avz backups/ user@remote:/backups/n8n-scraper/
   
   # AWS S3
   aws s3 sync backups/ s3://your-bucket/n8n-scraper-backups/
   ```

---

## 🔄 **AUTOMATED MAINTENANCE**

### **Setup Cron Jobs**

```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/n8n-scraper/scripts/backup.sh >> /path/to/n8n-scraper/logs/cron-backup.log 2>&1

# Weekly maintenance on Sunday at 3 AM
0 3 * * 0 /path/to/n8n-scraper/scripts/db-maintain.sh >> /path/to/n8n-scraper/logs/cron-maintain.log 2>&1

# Health check every hour
0 * * * * /path/to/n8n-scraper/scripts/health-check.sh >> /path/to/n8n-scraper/logs/cron-health.log 2>&1
```

### **Monitor Cron Jobs**

```bash
# View cron logs
tail -f logs/cron-backup.log
tail -f logs/cron-maintain.log
tail -f logs/cron-health.log

# List active cron jobs
crontab -l

# Test cron script manually
./scripts/backup.sh
```

---

## 📚 **ADDITIONAL RESOURCES**

- **Full Backup Guide**: `BACKUP_GUIDE.md`
- **Project Documentation**: `docs/`
- **Docker Compose Reference**: `docker-compose.yml` (see comments at bottom)
- **Database Schema**: `src/storage/models.py`

---

## 🆘 **EMERGENCY CONTACTS**

**Database Issues:**
- Health Check: `./scripts/health-check.sh`
- Monitor: `./scripts/db-monitor.sh`
- Logs: `docker-compose logs n8n-scraper-database`

**Data Loss:**
- Restore: `./scripts/restore.sh --latest`
- List Backups: `./scripts/restore.sh --list`

**Performance Issues:**
- Monitor: `./scripts/db-monitor.sh`
- Maintenance: `./scripts/db-maintain.sh`
- Stats: `docker stats`

---

**Remember: Your data is precious. Backup often, test restores regularly!** 🛡️

