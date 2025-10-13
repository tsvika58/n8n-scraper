#!/bin/bash

# ============================================================
# N8N SCRAPER AUTOMATED BACKUP CRON SCRIPT
# ============================================================
# This script is designed to be run by cron for automated backups
#
# Author: Dev1
# Task: SCRAPE-008 Storage Layer
# Date: October 11, 2025
#
# CRON SETUP:
# -----------
# To install this cron job, run:
#   crontab -e
#
# Then add one of these lines:
#
# Daily backup at 2:00 AM:
#   0 2 * * * /path/to/n8n-scraper/config/cron-backup.sh >> /path/to/n8n-scraper/logs/cron-backup.log 2>&1
#
# Every 6 hours:
#   0 */6 * * * /path/to/n8n-scraper/config/cron-backup.sh >> /path/to/n8n-scraper/logs/cron-backup.log 2>&1
#
# Every 12 hours:
#   0 */12 * * * /path/to/n8n-scraper/config/cron-backup.sh >> /path/to/n8n-scraper/logs/cron-backup.log 2>&1
#
# Weekly on Sunday at 3:00 AM:
#   0 3 * * 0 /path/to/n8n-scraper/config/cron-backup.sh >> /path/to/n8n-scraper/logs/cron-backup.log 2>&1
#
# ============================================================

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Main execution
main() {
    log "================================"
    log "Starting automated backup..."
    log "================================"
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Check if services are running
    if ! docker ps | grep -q "n8n-scraper-database"; then
        error "Database container is not running, skipping backup"
        exit 1
    fi
    
    # Run backup script
    if "$PROJECT_DIR/scripts/backup.sh"; then
        log "Backup completed successfully"
        
        # Optional: Send notification (uncomment to enable)
        # echo "Backup completed: $(hostname)" | mail -s "N8N Scraper Backup Success" admin@example.com
    else
        error "Backup failed"
        
        # Optional: Send error notification (uncomment to enable)
        # echo "Backup failed: $(hostname)" | mail -s "N8N Scraper Backup FAILED" admin@example.com
        
        exit 1
    fi
    
    log "================================"
    log "Automated backup finished"
    log "================================"
}

# Run main function
main "$@"





