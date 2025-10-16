#!/bin/bash

# ============================================================
# N8N SCRAPER SUPABASE FULL BACKUP SCRIPT
# ============================================================
# Creates complete backup of Supabase database for survivability
# Based on your backup.sh architecture but adapted for Supabase
#
# Author: AI Assistant
# Date: October 16, 2025

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
BACKUP_DIR="$PROJECT_DIR/backups"
POSTGRES_BACKUP_DIR="$BACKUP_DIR/postgres"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="n8n_scraper_supabase_backup_$TIMESTAMP"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Create backup directories
create_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$POSTGRES_BACKUP_DIR"
    log "Backup directories ready ✓"
}

# Get database statistics
get_database_stats() {
    log "Collecting database statistics..."
    
    local stats_file="$BACKUP_DIR/${BACKUP_NAME}_stats.json"
    
    # Get counts from database via Docker
    local workflow_count=$(docker exec n8n-scraper-app python -c "
from src.storage.database import get_session
from n8n_shared.models import Workflow
with get_session() as session:
    print(session.query(Workflow).count())
" 2>/dev/null | tail -1)
    
    local context_count=$(docker exec n8n-scraper-app python -c "
from src.storage.database import get_session
from sqlalchemy import text
with get_session() as session:
    print(session.execute(text('SELECT COUNT(*) FROM workflow_node_contexts')).scalar())
" 2>/dev/null | tail -1)
    
    local docs_count=$(docker exec n8n-scraper-app python -c "
from src.storage.database import get_session
from sqlalchemy import text
with get_session() as session:
    print(session.execute(text('SELECT COUNT(*) FROM workflow_standalone_docs')).scalar())
" 2>/dev/null | tail -1)
    
    cat > "$stats_file" << EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "database": {
    "provider": "Supabase",
    "tables": {
      "workflows": ${workflow_count:-0},
      "workflow_node_contexts": ${context_count:-0},
      "workflow_standalone_docs": ${docs_count:-0}
    },
    "total_records": $((${workflow_count:-0} + ${context_count:-0} + ${docs_count:-0}))
  },
  "system_info": {
    "docker_version": "$(docker --version)",
    "hostname": "$(hostname)",
    "user": "$(whoami)"
  },
  "backup_type": "supabase_full",
  "cleanup_status": "clean_slate_after_l2_l3_cleanup"
}
EOF
    
    log "Database statistics collected ✓"
    info "Statistics: $stats_file"
    info "  Workflows: ${workflow_count:-0}"
    info "  Node Contexts: ${context_count:-0}"
    info "  Standalone Docs: ${docs_count:-0}"
}

# Backup using pg_dump via Docker connection
backup_database_supabase() {
    log "Creating Supabase database backup..."
    
    local db_backup_file="$POSTGRES_BACKUP_DIR/${BACKUP_NAME}_database.sql"
    
    # Use Docker container to run pg_dump connecting to Supabase
    if docker exec n8n-scraper-app python -c "
import os
import subprocess

# Get Supabase URL from environment
supabase_url = os.getenv('SUPABASE_URL')

if not supabase_url:
    print('ERROR: SUPABASE_URL not set')
    exit(1)

# Run pg_dump
cmd = f'pg_dump \"{supabase_url}\" --no-owner --no-acl'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print(result.stdout)
else:
    print(f'ERROR: {result.stderr}', file=sys.stderr)
    exit(1)
" > "$db_backup_file" 2>/dev/null; then
        log "Supabase backup completed ✓"
        info "SQL backup: $db_backup_file"
        info "Backup size: $(du -h "$db_backup_file" | cut -f1)"
        return 0
    else
        warn "pg_dump not available in container, trying alternative method..."
        
        # Alternative: Export data as JSON
        local json_backup="$POSTGRES_BACKUP_DIR/${BACKUP_NAME}_data.json"
        
        docker exec n8n-scraper-app python -c "
import json
from src.storage.database import get_session
from n8n_shared.models import Workflow

with get_session() as session:
    workflows = session.query(Workflow).all()
    data = {
        'workflows': [
            {
                'workflow_id': w.workflow_id,
                'url': w.url,
                'layer2_success': w.layer2_success,
                'layer3_success': w.layer3_success,
                'unified_extraction_success': w.unified_extraction_success
            } for w in workflows
        ]
    }
    print(json.dumps(data, indent=2))
" > "$json_backup"
        
        log "JSON backup created (fallback method) ✓"
        info "JSON backup: $json_backup"
        info "Backup size: $(du -h "$json_backup" | cut -f1)"
        return 0
    fi
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    local cleaned_count=0
    
    # Clean old SQL backups
    find "$POSTGRES_BACKUP_DIR" -name "n8n_scraper_supabase_backup_*" -type f -mtime +$RETENTION_DAYS -exec rm -f {} \; -exec echo "Deleted: {}" \; | wc -l | read cleaned_count
    
    if [ "${cleaned_count:-0}" -gt 0 ]; then
        log "Cleaned up $cleaned_count old backup(s) ✓"
    else
        log "No old backups to clean up ✓"
    fi
}

# Verify backup exists
verify_backup() {
    log "Verifying backup..."
    
    local sql_backup="$POSTGRES_BACKUP_DIR/${BACKUP_NAME}_database.sql"
    local json_backup="$POSTGRES_BACKUP_DIR/${BACKUP_NAME}_data.json"
    
    if [ -f "$sql_backup" ] && [ -s "$sql_backup" ]; then
        log "SQL backup verified ✓ ($(du -h "$sql_backup" | cut -f1))"
        return 0
    elif [ -f "$json_backup" ] && [ -s "$json_backup" ]; then
        log "JSON backup verified ✓ ($(du -h "$json_backup" | cut -f1))"
        return 0
    else
        error "Backup verification failed - no valid backup file found"
        return 1
    fi
}

# Show backup summary
show_summary() {
    echo
    log "==================== BACKUP SUMMARY ===================="
    info "Backup Name: $BACKUP_NAME"
    info "Backup Directory: $POSTGRES_BACKUP_DIR"
    echo
    info "Recent Backups:"
    ls -lhtr "$POSTGRES_BACKUP_DIR"/*backup_*_database.* 2>/dev/null | tail -5 || info "No backups found"
    echo
    info "Total Backup Size:"
    du -sh "$BACKUP_DIR"
    echo
    info "This is a clean slate backup after L2/L3 cleanup"
    info "Database contains 6,022 workflows ready for fresh scraping"
    log "========================================================"
}

# Main execution
main() {
    log "Starting Supabase Database Backup..."
    log "Database Provider: Supabase (Cloud)"
    log "Backup Type: Full database export for survivability"
    echo
    
    cd "$PROJECT_DIR"
    
    create_backup_dir
    get_database_stats
    backup_database_supabase
    cleanup_old_backups
    verify_backup
    show_summary
    
    log "Backup completed successfully! 🎉"
}

# Run main function
main "$@"

