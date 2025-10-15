#!/bin/bash

# ============================================================
# N8N SCRAPER STOP SCRIPT
# ============================================================
# This script gracefully stops the n8n scraper infrastructure
# Based on n8n-standalone architecture for maximum reliability
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

# Check if services are running
check_services() {
    if ! docker-compose ps | grep -q "Up"; then
        warn "No services are currently running"
        return 1
    fi
    return 0
}

# Create backup before stopping
create_backup() {
    if [ "${1:-}" = "--backup" ] || [ "${1:-}" = "-b" ]; then
        log "Creating backup before stopping..."
        "$SCRIPT_DIR/backup.sh"
        log "Backup completed ✓"
    fi
}

# Graceful shutdown
graceful_shutdown() {
    log "Stopping services gracefully..."
    
    # Stop application first to allow operations to finish
    info "Stopping application..."
    docker-compose stop n8n-scraper-app
    
    # Wait a moment for graceful shutdown
    sleep 5
    
    # Stop database
    info "Stopping database..."
    docker-compose stop n8n-scraper-database
    
    # Stop optional services if running
    docker-compose stop n8n-scraper-db-admin 2>/dev/null || true
    docker-compose stop n8n-scraper-jupyter 2>/dev/null || true
    
    log "Services stopped ✓"
}

# Force shutdown
force_shutdown() {
    warn "Force stopping all services..."
    docker-compose down --remove-orphans
    log "Services force stopped ✓"
}

# Cleanup (optional)
cleanup() {
    if [ "${1:-}" = "--cleanup" ] || [ "${1:-}" = "-c" ]; then
        warn "Cleaning up containers and networks (data volumes will be preserved)..."
        docker-compose down --remove-orphans
        log "Cleanup completed ✓"
        info "Note: Data volumes are preserved. To remove volumes, use: docker volume rm n8n-scraper-postgres-data"
    fi
}

# Show final status
show_status() {
    echo
    info "Final Status:"
    docker-compose ps
    echo
    log "N8N Scraper stopped successfully!"
    info "To start again: ./scripts/start.sh"
    info "To restore backup: ./scripts/restore.sh --list"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --force, -f      Force stop all services"
    echo "  --cleanup, -c    Remove containers and networks (preserves data)"
    echo "  --backup, -b     Create backup before stopping"
    echo "  --help, -h       Show this help"
    echo
    echo "Examples:"
    echo "  $0                # Graceful shutdown"
    echo "  $0 --backup       # Backup then shutdown"
    echo "  $0 --force        # Force shutdown"
}

# Main execution
main() {
    local force=false
    local cleanup_flag=false
    local backup_flag=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force|-f)
                force=true
                shift
                ;;
            --cleanup|-c)
                cleanup_flag=true
                shift
                ;;
            --backup|-b)
                backup_flag=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log "Stopping N8N Scraper Infrastructure..."
    echo
    
    cd "$PROJECT_DIR"
    
    if ! check_services; then
        log "No services to stop"
        exit 0
    fi
    
    if [ "$backup_flag" = true ]; then
        create_backup
    fi
    
    if [ "$force" = true ]; then
        force_shutdown
    else
        graceful_shutdown
    fi
    
    if [ "$cleanup_flag" = true ]; then
        cleanup
    fi
    
    show_status
}

# Run main function
main "$@"







