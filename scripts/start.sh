#!/bin/bash

# ============================================================
# N8N SCRAPER START SCRIPT
# ============================================================
# This script starts the n8n scraper infrastructure with health checks
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

# Check if .env file exists
check_env() {
    if [ -f "$PROJECT_DIR/.env" ]; then
        log ".env file found ✓"
    else
        warn ".env file not found (using docker-compose defaults)"
    fi
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running!"
        info "Please start Docker and try again"
        exit 1
    fi
    log "Docker is running ✓"
}

# Check if ports are available
check_ports() {
    local ports=("5432" "8080" "8888")
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            warn "Port $port is already in use"
        else
            log "Port $port is available ✓"
        fi
    done
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    mkdir -p "$PROJECT_DIR/backups/postgres"
    mkdir -p "$PROJECT_DIR/data"
    mkdir -p "$PROJECT_DIR/media"
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/config"
    log "Directories created ✓"
}

# Start services
start_services() {
    log "Starting n8n scraper services..."
    cd "$PROJECT_DIR"
    
    # Start in detached mode
    docker-compose up -d
    
    log "Services started ✓"
}

# Wait for PostgreSQL to be healthy
wait_for_postgres() {
    log "Waiting for PostgreSQL to be healthy..."
    
    local postgres_ready=false
    for i in {1..30}; do
        if docker exec n8n-scraper-database pg_isready -U scraper_user -d n8n_scraper >/dev/null 2>&1; then
            postgres_ready=true
            break
        fi
        sleep 2
        echo -n "."
    done
    echo
    
    if [ "$postgres_ready" = true ]; then
        log "PostgreSQL is ready ✓"
    else
        error "PostgreSQL failed to start within 60 seconds"
        return 1
    fi
}

# Wait for application to be healthy
wait_for_app() {
    log "Waiting for application to be healthy..."
    
    local app_ready=false
    for i in {1..30}; do
        if docker ps | grep -q "n8n-scraper-app.*healthy"; then
            app_ready=true
            break
        fi
        sleep 2
        echo -n "."
    done
    echo
    
    if [ "$app_ready" = true ]; then
        log "Application is ready ✓"
    else
        warn "Application health check not yet passing"
    fi
}

# Display status
show_status() {
    log "N8N Scraper is running!"
    echo
    info "Container Status:"
    docker-compose ps
    echo
    info "Database Connection:"
    info "  Host: localhost"
    info "  Port: 5432"
    info "  Database: n8n_scraper"
    info "  User: scraper_user"
    echo
    info "Useful Commands:"
    info "  View logs: docker-compose logs -f n8n-scraper-app"
    info "  Database logs: docker-compose logs -f n8n-scraper-database"
    info "  Backup database: ./scripts/backup.sh"
    info "  Health check: ./scripts/health-check.sh"
    info "  Stop services: ./scripts/stop.sh"
    echo
    info "Development Tools (optional):"
    info "  Start pgAdmin: docker-compose --profile dev up -d"
    info "  Start Jupyter: docker-compose --profile analysis up -d"
}

# Main execution
main() {
    log "Starting N8N Scraper Infrastructure..."
    echo
    
    check_env
    check_docker
    check_ports
    create_directories
    start_services
    wait_for_postgres
    wait_for_app
    show_status
    
    log "N8N Scraper started successfully! 🚀"
}

# Run main function
main "$@"







