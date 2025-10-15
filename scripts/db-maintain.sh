#!/bin/bash

# ============================================================
# DATABASE MAINTENANCE SCRIPT
# ============================================================
# Optimize database performance with VACUUM, ANALYZE, and REINDEX
#
# Run this:
# - After bulk imports
# - Weekly for production
# - When queries slow down
#
# Author: Dev1
# Date: October 11, 2025

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

DB_CONTAINER="n8n-scraper-database"
DB_USER="scraper_user"
DB_NAME="n8n_scraper"

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; }

echo "============================================================"
log "DATABASE MAINTENANCE"
echo "============================================================"
echo

# 1. Vacuum Analyze (reclaim space, update statistics)
log "Running VACUUM ANALYZE on all tables..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "VACUUM ANALYZE;"
log "VACUUM ANALYZE completed ✓"
echo

# 2. Reindex (rebuild indexes for performance)
log "Reindexing database..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "REINDEX DATABASE $DB_NAME;"
log "Reindex completed ✓"
echo

# 3. Update table statistics
log "Updating table statistics..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE;"
log "Statistics updated ✓"
echo

# 4. Show bloat reduction
log "Checking table sizes after maintenance..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
echo

# 5. Cache hit ratio check
log "Verifying cache performance..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    sum(heap_blks_read) as disk_reads,
    sum(heap_blks_hit) as cache_hits,
    CASE 
        WHEN sum(heap_blks_hit) + sum(heap_blks_read) = 0 THEN 0
        ELSE round(sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100, 2)
    END as cache_hit_ratio_percent
FROM pg_statio_user_tables;
" 2>/dev/null || info "Not enough query history for cache stats"
echo

echo "============================================================"
log "Maintenance completed successfully! ✓"
info "Database is optimized for maximum performance"
info "Recommended: Run this weekly or after large imports"
echo "============================================================"







