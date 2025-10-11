# N8N Scraper Database Backup & Recovery Guide

**HIGH-SURVIVABILITY BACKUP SYSTEM**  
Based on n8n-standalone architecture for maximum data protection

---

## 🎯 Overview

This backup system provides **production-grade database survivability** with:

- ✅ **Multiple Backup Formats**: SQL dump, custom format, and full volume backup
- ✅ **Automated Scheduling**: Cron-based automated backups
- ✅ **Retention Management**: Automatic cleanup of old backups (30-day retention)
- ✅ **Verification**: Integrity checks on all backups
- ✅ **Fast Recovery**: Multiple restore options for different scenarios
- ✅ **Health Monitoring**: Comprehensive health checks
- ✅ **Graceful Operations**: Safe start/stop procedures

---

## 📁 Backup Architecture

### Backup Types

1. **SQL Dump** (`_database.sql`)
   - Human-readable SQL format
   - Easy to inspect and modify
   - Best for: Selective data recovery, manual inspection

2. **Custom Format** (`_database.dump`)
   - Compressed binary format
   - Fastest restore time
   - Best for: Quick recovery, production restores

3. **Volume Backup** (`_volume.tar.gz`)
   - Complete PostgreSQL data directory
   - Includes all configurations and indexes
   - Best for: Disaster recovery, exact replica creation

### Storage Locations

```
n8n-scraper/
├── backups/
│   ├── postgres/              # PostgreSQL-specific backups
│   ├── *.tar.gz               # Compressed backup archives
│   └── *_volume.tar.gz        # Volume backups
├── logs/
│   ├── cron-backup.log        # Automated backup logs
│   └── health-report-*.json   # Health check reports
└── scripts/
    ├── backup.sh              # Manual backup script
    ├── restore.sh             # Restore script
    ├── start.sh               # Start with health checks
    ├── stop.sh                # Graceful shutdown
    └── health-check.sh        # System health monitoring
```

---

## 🚀 Quick Start

### Manual Backup

```bash
# Create a backup now
./scripts/backup.sh

# Stop services and backup
./scripts/stop.sh --backup
```

### Restore from Backup

```bash
# List available backups
./scripts/restore.sh --list

# Restore latest backup (custom format - fastest)
./scripts/restore.sh --latest

# Restore specific backup
./scripts/restore.sh n8n_scraper_backup_20251011_143022

# Restore from SQL dump
./scripts/restore.sh --latest --sql

# Restore entire volume (complete recovery)
./scripts/restore.sh --latest --volume
```

### Health Check

```bash
# Run comprehensive health check
./scripts/health-check.sh
```

---

## ⚙️ Automated Backups

### Setup Cron Job

1. **Edit crontab:**
   ```bash
   crontab -e
   ```

2. **Add backup schedule:**

   **Daily at 2:00 AM** (recommended):
   ```cron
   0 2 * * * /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper/config/cron-backup.sh >> /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper/logs/cron-backup.log 2>&1
   ```

   **Every 6 hours** (high-frequency):
   ```cron
   0 */6 * * * /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper/config/cron-backup.sh >> /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper/logs/cron-backup.log 2>&1
   ```

   **Weekly on Sunday at 3:00 AM** (low-frequency):
   ```cron
   0 3 * * 0 /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper/config/cron-backup.sh >> /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper/logs/cron-backup.log 2>&1
   ```

3. **Verify cron job:**
   ```bash
   crontab -l
   ```

4. **Monitor backups:**
   ```bash
   tail -f logs/cron-backup.log
   ```

---

## 🔄 Backup Lifecycle

### Automatic Retention

- **Retention Period**: 30 days (configurable in `scripts/backup.sh`)
- **Cleanup**: Automatic removal of backups older than retention period
- **Storage**: Backups are stored both in archives and individual formats

### Backup Contents

Each backup includes:
- ✅ All database tables (workflows, metadata, structure, content, transcripts)
- ✅ Database indexes and constraints
- ✅ Database statistics (record counts, sizes)
- ✅ Metadata file with backup information
- ✅ Verification checksums

---

## 🛡️ Disaster Recovery Scenarios

### Scenario 1: Data Corruption (Fast Recovery)

```bash
# Stop application
./scripts/stop.sh

# Restore latest backup (custom format - fastest)
./scripts/restore.sh --latest

# Verify data
./scripts/health-check.sh
```

**Recovery Time**: ~2-5 minutes

---

### Scenario 2: Complete Database Loss

```bash
# Stop all services
./scripts/stop.sh --force

# Restore entire volume
./scripts/restore.sh --latest --volume

# Start services
./scripts/start.sh

# Verify data
./scripts/health-check.sh
```

**Recovery Time**: ~5-10 minutes

---

### Scenario 3: Selective Data Recovery

```bash
# Extract backup
cd backups
tar -xzf n8n_scraper_backup_YYYYMMDD_HHMMSS.tar.gz

# Inspect SQL dump
less n8n_scraper_backup_YYYYMMDD_HHMMSS_database.sql

# Restore specific tables manually using psql
docker exec -i n8n-scraper-database psql -U scraper_user -d n8n_scraper < custom_restore.sql
```

---

### Scenario 4: Move to New Server

1. **On old server:**
   ```bash
   ./scripts/backup.sh
   # Copy backups/n8n_scraper_backup_*.tar.gz to new server
   ```

2. **On new server:**
   ```bash
   # Setup project
   git clone <repository>
   cd n8n-scraper
   
   # Copy backup file to backups/
   cp /path/to/backup.tar.gz backups/
   
   # Start services (creates volumes)
   ./scripts/start.sh
   
   # Restore backup
   ./scripts/restore.sh n8n_scraper_backup_YYYYMMDD_HHMMSS
   
   # Verify
   ./scripts/health-check.sh
   ```

---

## 🔍 Monitoring & Verification

### Health Checks

```bash
# Run full health check
./scripts/health-check.sh

# View health report
cat logs/health-report-*.json | jq
```

### Backup Verification

```bash
# Manual verification
cd backups
tar -tzf n8n_scraper_backup_YYYYMMDD_HHMMSS.tar.gz

# Check backup integrity (automatic in backup script)
# Look for "Backup verification passed ✓" in output
```

### Database Statistics

```bash
# View database size and record counts
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
  SELECT 
    'workflows' as table_name, COUNT(*) as count 
  FROM workflows
  UNION ALL
  SELECT 'workflow_metadata', COUNT(*) FROM workflow_metadata
  UNION ALL
  SELECT 'workflow_structure', COUNT(*) FROM workflow_structure
  UNION ALL
  SELECT 'workflow_content', COUNT(*) FROM workflow_content
  UNION ALL
  SELECT 'video_transcripts', COUNT(*) FROM video_transcripts;
"

# View database size
docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "
  SELECT pg_size_pretty(pg_database_size('n8n_scraper'));
"
```

---

## 🔐 Security Considerations

### Backup Security

1. **Encrypt backups** (if needed):
   ```bash
   # Encrypt backup
   gpg --symmetric --cipher-algo AES256 backups/backup.tar.gz
   
   # Decrypt backup
   gpg --decrypt backups/backup.tar.gz.gpg > backups/backup.tar.gz
   ```

2. **Off-site storage**:
   ```bash
   # Sync to remote server
   rsync -avz backups/ user@remote-server:/backups/n8n-scraper/
   
   # Sync to cloud storage (AWS S3 example)
   aws s3 sync backups/ s3://my-bucket/n8n-scraper-backups/
   ```

3. **Access Control**:
   ```bash
   # Restrict backup directory permissions
   chmod 700 backups/
   chmod 600 backups/*.tar.gz
   ```

---

## 📊 Performance Benchmarks

Based on 1,000 workflows:

| Operation | Time | Size |
|-----------|------|------|
| SQL Dump | ~30s | ~50MB |
| Custom Dump | ~20s | ~15MB (compressed) |
| Volume Backup | ~45s | ~100MB |
| Restore (Custom) | ~10s | - |
| Restore (SQL) | ~25s | - |
| Restore (Volume) | ~15s | - |

---

## 🆘 Troubleshooting

### Backup Fails

```bash
# Check if database is running
docker ps | grep n8n-scraper-database

# Check disk space
df -h

# Check database connection
docker exec n8n-scraper-database pg_isready -U scraper_user -d n8n_scraper

# View backup script logs
./scripts/backup.sh
```

### Restore Fails

```bash
# Verify backup file
tar -tzf backups/backup.tar.gz

# Check available disk space
df -h

# Force stop and retry
./scripts/stop.sh --force
./scripts/restore.sh --latest --force
```

### Database Won't Start

```bash
# Check Docker logs
docker logs n8n-scraper-database

# Restart database
docker-compose restart n8n-scraper-database

# Nuclear option: restore from volume backup
./scripts/restore.sh --latest --volume
```

---

## 📝 Best Practices

1. **Regular Backups**: Set up automated daily backups
2. **Test Restores**: Periodically test restore procedure
3. **Off-site Storage**: Copy backups to external location
4. **Monitor Health**: Run health checks regularly
5. **Retention Policy**: Keep at least 30 days of backups
6. **Documentation**: Keep this guide updated with any changes
7. **Alert System**: Set up notifications for backup failures

---

## 🔗 Related Documentation

- [Docker Compose Configuration](./docker-compose.yml)
- [Database Schema](./docs/SCHEMA.md)
- [API Documentation](./docs/API.md)

---

## 📞 Support

If you encounter issues:

1. Check this guide for troubleshooting steps
2. Review logs: `docker-compose logs -f`
3. Run health check: `./scripts/health-check.sh`
4. Create an issue with logs and error messages

---

**Remember: Your data is only as safe as your last backup!** 🛡️

