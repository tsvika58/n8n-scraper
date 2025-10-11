#!/bin/bash

# ============================================================
# N8N SCRAPER DATABASE BACKUP SCRIPT
# ============================================================
# This script creates automated backups of the PostgreSQL database
# Based on n8n-standalone architecture for maximum survivability
#
# Author: Dev1
# Task: SCRAPE-008 Storage Layer
# Date: October 11, 2025

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
BACKUP_DIR="$PROJECT_DIR/backups"
POSTGRES_BACKUP_DIR="$BACKUP_DIR/postgres"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="n8n_scraper_backup_$TIMESTAMP"

# Database configuration
DB_CONTAINER="n8n-scraper-database"
DB_USER="scraper_user"
DB_NAME="n8n_scraper"

# Logging
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

# Check if database service is running
check_services() {
    if ! docker ps --format "{{.Names}}" | grep -q "^${DB_CONTAINER}$"; then
        error "Database container is not running. Please start it first: ./scripts/start.sh"
        exit 1
    fi
    log "Database container is running ✓"
}

# Create backup directories
create_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$POSTGRES_BACKUP_DIR"
    log "Backup directories ready ✓"
}

# Backup PostgreSQL database (SQL dump)
backup_database_sql() {
    log "Backing up PostgreSQL database (SQL format)..."
    
    local db_backup_file="$POSTGRES_BACKUP_DIR/${BACKUP_NAME}_database.sql"
    
    if docker exec -t "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$db_backup_file"; then
        log "Database SQL backup completed ✓"
        info "SQL backup: $db_backup_file"
        info "SQL backup size: $(du -h "$db_backup_file" | cut -f1)"
    else
        error "Database SQL backup failed"
        return 1
    fi
}

# Backup PostgreSQL database (custom format - compressed, fast restore)
backup_database_custom() {
    log "Backing up PostgreSQL database (custom format)..."
    
    local db_backup_file="$POSTGRES_BACKUP_DIR/${BACKUP_NAME}_database.dump"
    
    if docker exec -t "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc -f "/backups/postgres/$(basename "$db_backup_file")"; then
        log "Database custom backup completed ✓"
        info "Custom backup: $db_backup_file"
        info "Custom backup size: $(du -h "$db_backup_file" | cut -f1)"
    else
        error "Database custom backup failed"
        return 1
    fi
}

# Backup Docker volume (complete data directory)
backup_volume() {
    log "Backing up PostgreSQL data volume..."
    
    local volume_backup_file="$BACKUP_DIR/${BACKUP_NAME}_volume.tar.gz"
    
    if docker run --rm \
        -v n8n-scraper-postgres-data:/data \
        -v "$BACKUP_DIR":/backup \
        alpine tar -czf "/backup/$(basename "$volume_backup_file")" -C /data .; then
        log "Volume backup completed ✓"
        info "Volume backup: $volume_backup_file"
        info "Volume backup size: $(du -h "$volume_backup_file" | cut -f1)"
    else
        error "Volume backup failed"
        return 1
    fi
}

# Get database statistics
get_database_stats() {
    set +u  # Temporarily disable unbound variable check for this function
    log "Collecting database statistics..."
    
    local stats_file="$BACKUP_DIR/${BACKUP_NAME}_stats.json"
    
    # Get table counts (handle case where tables don't exist yet)
    local workflow_count=$(docker exec -t "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM workflows;" 2>&1 | grep -E '^[0-9]+$' || echo "0")
    local metadata_count=$(docker exec -t "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM workflow_metadata;" 2>&1 | grep -E '^[0-9]+$' || echo "0")
    local structure_count=$(docker exec -t "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM workflow_structure;" 2>&1 | grep -E '^[0-9]+$' || echo "0")
    local content_count=$(docker exec -t "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM workflow_content;" 2>&1 | grep -E '^[0-9]+$' || echo "0")
    local transcript_count=$(docker exec -t "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM video_transcripts;" 2>&1 | grep -E '^[0-9]+$' || echo "0")
    
    # Get database size
    local db_size=$(docker exec -t "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | tr -d ' \r\n' || echo "unknown")
    
    cat > "$stats_file" << EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "database": {
    "name": "$DB_NAME",
    "size": "$db_size",
    "tables": {
      "workflows": ${workflow_count:-0},
      "workflow_metadata": ${metadata_count:-0},
      "workflow_structure": ${structure_count:-0},
      "workflow_content": ${content_count:-0},
      "video_transcripts": ${transcript_count:-0}
    },
    "total_records": $((${workflow_count:-0} + ${metadata_count:-0} + ${structure_count:-0} + ${content_count:-0} + ${transcript_count:-0}))
  },
  "system_info": {
    "docker_version": "$(docker --version)",
    "hostname": "$(hostname)",
    "user": "$(whoami)"
  },
  "backup_files": {
    "sql_dump": "${BACKUP_NAME}_database.sql",
    "custom_dump": "${BACKUP_NAME}_database.dump",
    "volume_backup": "${BACKUP_NAME}_volume.tar.gz"
  }
}
EOF
    
    set -u  # Re-enable unbound variable check
    log "Database statistics collected ✓"
    info "Statistics: $stats_file"
}

# Create compressed archive
create_archive() {
    log "Creating compressed backup archive..."
    
    local archive_file="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    cd "$BACKUP_DIR"
    if tar -czf "$archive_file" --exclude="*.tar.gz" "${BACKUP_NAME}_"*; then
        log "Backup archive created ✓"
        info "Backup archive: $archive_file"
        info "Archive size: $(du -h "$archive_file" | cut -f1)"
        
        # Remove individual files to save space (keep only the archive)
        rm -f "${BACKUP_NAME}_"*.sql
        rm -f "${BACKUP_NAME}_"*.dump
        rm -f "${BACKUP_NAME}_"*.json
        # Note: Keep volume backup separate as it's already compressed
        
        log "Individual backup files cleaned up ✓"
    else
        error "Failed to create backup archive"
        return 1
    fi
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    local cleaned_count=0
    
    # Clean old archives
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((cleaned_count++))
    done < <(find "$BACKUP_DIR" -name "n8n_scraper_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -print0)
    
    # Clean old volume backups
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((cleaned_count++))
    done < <(find "$BACKUP_DIR" -name "n8n_scraper_backup_*_volume.tar.gz" -type f -mtime +$RETENTION_DAYS -print0)
    
    if [ $cleaned_count -gt 0 ]; then
        log "Cleaned up $cleaned_count old backup(s) ✓"
    else
        log "No old backups to clean up ✓"
    fi
}

# Verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    local archive_file="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    local volume_backup="$BACKUP_DIR/${BACKUP_NAME}_volume.tar.gz"
    
    local verified=true
    
    # Verify main archive
    if [ -f "$archive_file" ]; then
        if tar -tzf "$archive_file" >/dev/null 2>&1; then
            log "Main archive verification passed ✓"
        else
            error "Main archive is corrupted"
            verified=false
        fi
    else
        error "Main archive not found"
        verified=false
    fi
    
    # Verify volume backup
    if [ -f "$volume_backup" ]; then
        if tar -tzf "$volume_backup" >/dev/null 2>&1; then
            log "Volume backup verification passed ✓"
        else
            error "Volume backup is corrupted"
            verified=false
        fi
    else
        error "Volume backup not found"
        verified=false
    fi
    
    if [ "$verified" = false ]; then
        return 1
    fi
    
    log "All backups verified ✓"
}

# Show backup summary
show_summary() {
    echo
    log "==================== BACKUP SUMMARY ===================="
    info "Backup Name: $BACKUP_NAME"
    info "Backup Directory: $BACKUP_DIR"
    echo
    info "Backup Files:"
    info "  Main Archive: $BACKUP_DIR/${BACKUP_NAME}.tar.gz ($(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1))"
    info "  Volume Backup: $BACKUP_DIR/${BACKUP_NAME}_volume.tar.gz ($(du -h "$BACKUP_DIR/${BACKUP_NAME}_volume.tar.gz" | cut -f1))"
    echo
    info "Recent Backups:"
    ls -lhtr "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -5 || info "No backups found"
    echo
    info "Disk Usage:"
    du -sh "$BACKUP_DIR"
    echo
    info "To restore: ./scripts/restore.sh $BACKUP_NAME"
    log "========================================================"
}

# Main execution
main() {
    log "Starting N8N Scraper Database Backup..."
    echo
    
    cd "$PROJECT_DIR"
    
    check_services
    create_backup_dir
    get_database_stats
    backup_database_sql
    backup_database_custom
    backup_volume
    create_archive
    cleanup_old_backups
    verify_backup
    show_summary
    
    log "Backup completed successfully! 🎉"
}

# Run main function
main "$@"

