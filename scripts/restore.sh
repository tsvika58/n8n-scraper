#!/bin/bash

# ============================================================
# N8N SCRAPER DATABASE RESTORE SCRIPT
# ============================================================
# This script restores the PostgreSQL database from a backup
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

# Show usage
show_usage() {
    echo "Usage: $0 [BACKUP_NAME] [OPTIONS]"
    echo
    echo "Arguments:"
    echo "  BACKUP_NAME    Name of the backup to restore (without .tar.gz extension)"
    echo
    echo "Options:"
    echo "  --list, -l     List available backups"
    echo "  --latest       Restore the latest backup"
    echo "  --force, -f    Force restore without confirmation"
    echo "  --sql          Use SQL dump (default: custom format)"
    echo "  --volume       Restore entire volume (complete data directory)"
    echo "  --help, -h     Show this help"
    echo
    echo "Examples:"
    echo "  $0 --list"
    echo "  $0 n8n_scraper_backup_20251011_143022"
    echo "  $0 --latest"
    echo "  $0 --latest --volume"
}

# List available backups
list_backups() {
    log "Available backups:"
    echo
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/*.tar.gz 2>/dev/null)" ]; then
        warn "No backups found in $BACKUP_DIR"
        return 1
    fi
    
    for backup in "$BACKUP_DIR"/n8n_scraper_backup_*.tar.gz; do
        if [[ $backup == *"_volume.tar.gz" ]]; then
            continue  # Skip volume backups in main list
        fi
        local backup_name=$(basename "$backup" .tar.gz)
        local backup_size=$(du -h "$backup" | cut -f1)
        local backup_date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup" 2>/dev/null || stat -c "%y" "$backup" 2>/dev/null | cut -d' ' -f1-2)
        info "$backup_name ($backup_size) - $backup_date"
    done
}

# Get latest backup
get_latest_backup() {
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/n8n_scraper_backup_*.tar.gz 2>/dev/null)" ]; then
        error "No backups found"
        return 1
    fi
    
    local latest_backup=$(ls -t "$BACKUP_DIR"/n8n_scraper_backup_*.tar.gz | grep -v "_volume.tar.gz" | head -1)
    basename "$latest_backup" .tar.gz
}

# Validate backup
validate_backup() {
    local backup_name="$1"
    local backup_file="$BACKUP_DIR/${backup_name}.tar.gz"
    
    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    if ! tar -tzf "$backup_file" >/dev/null 2>&1; then
        error "Backup file is corrupted: $backup_file"
        return 1
    fi
    
    log "Backup validation passed ✓"
}

# Confirm restore
confirm_restore() {
    local backup_name="$1"
    
    if [ "${FORCE:-false}" = "true" ]; then
        return 0
    fi
    
    warn "This will replace the current database with backup: $backup_name"
    warn "Current data will be lost!"
    echo
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        info "Restore cancelled"
        exit 0
    fi
}

# Stop services
stop_services() {
    log "Stopping application services..."
    docker-compose stop n8n-scraper-app 2>/dev/null || true
    log "Application stopped ✓"
}

# Extract backup
extract_backup() {
    local backup_name="$1"
    local backup_file="$BACKUP_DIR/${backup_name}.tar.gz"
    local temp_dir="$BACKUP_DIR/temp_restore"
    
    log "Extracting backup..."
    
    # Create temp directory
    mkdir -p "$temp_dir"
    
    # Extract backup
    if tar -xzf "$backup_file" -C "$temp_dir"; then
        log "Backup extracted ✓"
    else
        error "Failed to extract backup"
        return 1
    fi
}

# Restore database from SQL dump
restore_database_sql() {
    local backup_name="$1"
    local temp_dir="$BACKUP_DIR/temp_restore"
    local db_file="$temp_dir/${backup_name}_database.sql"
    
    if [ ! -f "$db_file" ]; then
        error "Database SQL dump not found: $db_file"
        return 1
    fi
    
    log "Restoring database from SQL dump..."
    
    # Ensure PostgreSQL is running
    if ! docker ps | grep -q "$DB_CONTAINER"; then
        log "Starting PostgreSQL..."
        docker-compose up -d n8n-scraper-database
        
        # Wait for PostgreSQL to be ready
        info "Waiting for PostgreSQL to be ready..."
        local postgres_ready=false
        for i in {1..30}; do
            if docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
                postgres_ready=true
                break
            fi
            sleep 2
        done
        
        if [ "$postgres_ready" = true ]; then
            log "PostgreSQL is ready ✓"
        else
            error "PostgreSQL failed to start"
            return 1
        fi
    fi
    
    # Drop and recreate database
    info "Dropping existing database..."
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
    
    # Restore database
    if docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$db_file"; then
        log "Database restored from SQL dump ✓"
    else
        error "Database restore failed"
        return 1
    fi
}

# Restore database from custom dump
restore_database_custom() {
    local backup_name="$1"
    local temp_dir="$BACKUP_DIR/temp_restore"
    local db_file="$temp_dir/${backup_name}_database.dump"
    
    if [ ! -f "$db_file" ]; then
        error "Database custom dump not found: $db_file"
        return 1
    fi
    
    log "Restoring database from custom dump..."
    
    # Copy dump file into container
    docker cp "$db_file" "$DB_CONTAINER:/tmp/restore.dump"
    
    # Drop and recreate database
    info "Dropping existing database..."
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
    
    # Restore using pg_restore
    if docker exec "$DB_CONTAINER" pg_restore -U "$DB_USER" -d "$DB_NAME" -c /tmp/restore.dump; then
        log "Database restored from custom dump ✓"
        docker exec "$DB_CONTAINER" rm /tmp/restore.dump
    else
        error "Database restore failed"
        docker exec "$DB_CONTAINER" rm /tmp/restore.dump || true
        return 1
    fi
}

# Restore entire volume
restore_volume() {
    local backup_name="$1"
    local volume_backup="$BACKUP_DIR/${backup_name}_volume.tar.gz"
    
    if [ ! -f "$volume_backup" ]; then
        error "Volume backup not found: $volume_backup"
        return 1
    fi
    
    log "Restoring entire PostgreSQL volume..."
    
    # Stop database
    docker-compose stop n8n-scraper-database
    
    # Remove existing volume
    warn "Removing existing volume..."
    docker volume rm n8n-scraper-postgres-data 2>/dev/null || true
    
    # Create new volume and restore data
    if docker run --rm \
        -v n8n-scraper-postgres-data:/data \
        -v "$volume_backup":/backup.tar.gz \
        alpine sh -c "tar -xzf /backup.tar.gz -C /data"; then
        log "Volume restored ✓"
    else
        error "Volume restore failed"
        return 1
    fi
}

# Start services
start_services() {
    log "Starting services..."
    "$SCRIPT_DIR/start.sh"
    log "Services started ✓"
}

# Cleanup temp files
cleanup() {
    local temp_dir="$BACKUP_DIR/temp_restore"
    if [ -d "$temp_dir" ]; then
        rm -rf "$temp_dir"
        log "Temporary files cleaned up ✓"
    fi
}

# Verify restore
verify_restore() {
    log "Verifying restore..."
    
    # Wait for database to be ready
    info "Waiting for database to be ready..."
    local db_ready=false
    for i in {1..30}; do
        if docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
            db_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$db_ready" = true ]; then
        log "Database is ready ✓"
        
        # Get table counts
        local workflow_count=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM workflows;" | tr -d ' \r\n')
        info "Verified $workflow_count workflows restored"
        
        log "Restore verification passed ✓"
    else
        error "Database failed to start after restore"
        return 1
    fi
}

# Main execution
main() {
    local backup_name=""
    local list_only=false
    local use_latest=false
    local use_sql=false
    local use_volume=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --list|-l)
                list_only=true
                shift
                ;;
            --latest)
                use_latest=true
                shift
                ;;
            --force|-f)
                export FORCE=true
                shift
                ;;
            --sql)
                use_sql=true
                shift
                ;;
            --volume)
                use_volume=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [ -z "$backup_name" ]; then
                    backup_name="$1"
                else
                    error "Multiple backup names specified"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Handle list option
    if [ "$list_only" = true ]; then
        list_backups
        exit 0
    fi
    
    # Handle latest option
    if [ "$use_latest" = true ]; then
        backup_name=$(get_latest_backup)
        if [ -z "$backup_name" ]; then
            exit 1
        fi
        log "Using latest backup: $backup_name"
    fi
    
    # Validate backup name
    if [ -z "$backup_name" ]; then
        error "No backup name specified"
        show_usage
        exit 1
    fi
    
    log "Starting N8N Scraper Database Restore..."
    echo
    
    cd "$PROJECT_DIR"
    
    validate_backup "$backup_name"
    confirm_restore "$backup_name"
    stop_services
    
    if [ "$use_volume" = true ]; then
        restore_volume "$backup_name"
        start_services
    else
        extract_backup "$backup_name"
        if [ "$use_sql" = true ]; then
            restore_database_sql "$backup_name"
        else
            restore_database_custom "$backup_name"
        fi
    fi
    
    cleanup
    verify_restore
    
    log "Restore completed successfully! 🎉"
    info "Database is available at: postgresql://scraper_user@localhost:5432/n8n_scraper"
}

# Run main function
main "$@"







