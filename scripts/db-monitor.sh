#!/bin/bash

# ============================================================
# DATABASE PERFORMANCE MONITOR
# ============================================================
# Monitor database performance, connections, and query stats
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
log "DATABASE PERFORMANCE MONITOR"
echo "============================================================"
echo

# 1. Connection Stats
log "CONNECTION STATISTICS:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity
WHERE datname = '$DB_NAME';
" 2>/dev/null || warn "Could not fetch connection stats"

echo

# 2. Database Size & Growth
log "DATABASE SIZE:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    pg_size_pretty(pg_database_size('$DB_NAME')) as database_size,
    pg_size_pretty(pg_total_relation_size('workflows')) as workflows_size,
    pg_size_pretty(pg_total_relation_size('workflow_structure')) as structure_size;
" 2>/dev/null || warn "Could not fetch size stats"

echo

# 3. Table Statistics
log "TABLE RECORD COUNTS:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    'workflows' as table_name, 
    COUNT(*) as records,
    pg_size_pretty(pg_total_relation_size('workflows')) as size
FROM workflows
UNION ALL
SELECT 'workflow_metadata', COUNT(*), pg_size_pretty(pg_total_relation_size('workflow_metadata')) FROM workflow_metadata
UNION ALL
SELECT 'workflow_structure', COUNT(*), pg_size_pretty(pg_total_relation_size('workflow_structure')) FROM workflow_structure
UNION ALL
SELECT 'workflow_content', COUNT(*), pg_size_pretty(pg_total_relation_size('workflow_content')) FROM workflow_content
UNION ALL
SELECT 'video_transcripts', COUNT(*), pg_size_pretty(pg_total_relation_size('video_transcripts')) FROM video_transcripts;
" 2>/dev/null || warn "Tables may not exist yet"

echo

# 4. Index Usage
log "INDEX USAGE:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC
LIMIT 10;
" 2>/dev/null || info "No index stats available yet"

echo

# 5. Slow Queries (if pg_stat_statements enabled)
log "TOP SLOW QUERIES (if available):"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 5;
" 2>/dev/null || info "pg_stat_statements not enabled (optional)"

echo

# 6. Cache Hit Ratio
log "CACHE HIT RATIO (should be >90%):"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
FROM pg_statio_user_tables;
" 2>/dev/null || info "Not enough data for cache stats yet"

echo

# 7. Vacuum & Analyze Status
log "MAINTENANCE STATUS:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public';
" 2>/dev/null || info "No maintenance stats available yet"

echo

# 8. Lock Status
log "CURRENT LOCKS:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    locktype,
    count(*) as count
FROM pg_locks
WHERE database = (SELECT oid FROM pg_database WHERE datname = '$DB_NAME')
GROUP BY locktype;
" 2>/dev/null || info "No lock information available"

echo
echo "============================================================"
log "Monitoring complete!"
info "For continuous monitoring, run: watch -n 5 ./scripts/db-monitor.sh"
echo "============================================================"







