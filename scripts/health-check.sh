#!/bin/bash

# ============================================================
# N8N SCRAPER HEALTH CHECK SCRIPT
# ============================================================
# This script performs comprehensive health checks on the infrastructure
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

# Configuration
TIMEOUT=10
RETRIES=3

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

# Check Docker
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
        return 1
    fi
    log "Docker is running ✓"
    return 0
}

# Check containers
check_containers() {
    log "Checking container status..."
    
    local containers=("n8n-scraper-database" "n8n-scraper-app")
    local all_healthy=true
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container.*Up"; then
            log "Container $container is running ✓"
        else
            error "Container $container is not running"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = false ]; then
        return 1
    fi
    return 0
}

# Check PostgreSQL
check_postgres() {
    log "Checking PostgreSQL..."
    
    if docker exec n8n-scraper-database pg_isready -U scraper_user -d n8n_scraper >/dev/null 2>&1; then
        log "PostgreSQL is ready ✓"
        
        # Check database connectivity
        if docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -c "SELECT 1;" >/dev/null 2>&1; then
            log "PostgreSQL database connection ✓"
            
            # Get database stats
            local db_size=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT pg_size_pretty(pg_database_size('n8n_scraper'));" | tr -d ' \r\n')
            local workflow_count=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM workflows;" 2>/dev/null | tr -d ' \r\n' || echo "0")
            
            info "Database size: $db_size"
            info "Workflow count: $workflow_count"
        else
            error "PostgreSQL database connection failed"
            return 1
        fi
    else
        error "PostgreSQL is not ready"
        return 1
    fi
    return 0
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."
    
    local usage
    usage=$(df -h "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        log "Disk space OK ✓ ($usage% used)"
    elif [ "$usage" -lt 90 ]; then
        warn "Disk space getting low ($usage% used)"
    else
        error "Disk space critically low ($usage% used)"
        return 1
    fi
    return 0
}

# Check memory usage
check_memory() {
    log "Checking memory usage..."
    
    # Get container memory stats
    local db_mem=$(docker stats --no-stream --format "{{.MemUsage}}" n8n-scraper-database | awk '{print $1}')
    local app_mem=$(docker stats --no-stream --format "{{.MemUsage}}" n8n-scraper-app | awk '{print $1}')
    
    info "Database memory: $db_mem"
    info "Application memory: $app_mem"
    
    log "Memory usage OK ✓"
    return 0
}

# Check logs for errors
check_logs() {
    log "Checking recent logs for errors..."
    
    local error_count=0
    
    # Check database logs
    local db_errors=$(docker logs n8n-scraper-database --tail 50 2>&1 | grep -i "error\|fatal\|exception" | wc -l)
    if [ "$db_errors" -eq 0 ]; then
        log "PostgreSQL logs clean ✓"
    else
        error "Found $db_errors errors in PostgreSQL logs"
        error_count=$((error_count + db_errors))
    fi
    
    # Check application logs
    local app_errors=$(docker logs n8n-scraper-app --tail 50 2>&1 | grep -i "error\|fatal\|exception" | wc -l)
    if [ "$app_errors" -eq 0 ]; then
        log "Application logs clean ✓"
    else
        warn "Found $app_errors warnings in application logs"
    fi
    
    if [ $error_count -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Check backups
check_backups() {
    log "Checking backup status..."
    
    local backup_dir="$PROJECT_DIR/backups"
    
    if [ ! -d "$backup_dir" ]; then
        warn "Backup directory does not exist"
        return 1
    fi
    
    local backup_count=$(ls -1 "$backup_dir"/*.tar.gz 2>/dev/null | wc -l)
    
    if [ "$backup_count" -gt 0 ]; then
        log "Found $backup_count backup(s) ✓"
        
        # Check latest backup age
        local latest_backup=$(ls -t "$backup_dir"/*.tar.gz 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            local backup_age_seconds=$(( $(date +%s) - $(stat -f %m "$latest_backup" 2>/dev/null || stat -c %Y "$latest_backup") ))
            local backup_age_hours=$((backup_age_seconds / 3600))
            
            info "Latest backup: $(basename "$latest_backup")"
            info "Backup age: $backup_age_hours hours"
            
            if [ "$backup_age_hours" -gt 24 ]; then
                warn "Latest backup is more than 24 hours old"
            fi
        fi
    else
        warn "No backups found - consider running: ./scripts/backup.sh"
    fi
    
    return 0
}

# Check volume health
check_volumes() {
    log "Checking Docker volumes..."
    
    if docker volume inspect n8n-scraper-postgres-data >/dev/null 2>&1; then
        log "PostgreSQL volume exists ✓"
        
        # Get volume size
        local volume_size=$(docker system df -v | grep "n8n-scraper-postgres-data" | awk '{print $3}' || echo "unknown")
        info "Volume size: $volume_size"
    else
        error "PostgreSQL volume not found"
        return 1
    fi
    
    return 0
}

# Generate health report
generate_report() {
    local overall_status="$1"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    log "Generating health report..."
    
    mkdir -p "$PROJECT_DIR/logs"
    
    cat > "$PROJECT_DIR/logs/health-report-$(date +%Y%m%d_%H%M%S).json" << EOF
{
  "timestamp": "$timestamp",
  "overall_status": "$overall_status",
  "checks": {
    "docker": "$(check_docker >/dev/null 2>&1 && echo "pass" || echo "fail")",
    "containers": "$(check_containers >/dev/null 2>&1 && echo "pass" || echo "fail")",
    "postgres": "$(check_postgres >/dev/null 2>&1 && echo "pass" || echo "fail")",
    "disk_space": "$(check_disk_space >/dev/null 2>&1 && echo "pass" || echo "fail")",
    "memory": "$(check_memory >/dev/null 2>&1 && echo "pass" || echo "fail")",
    "logs": "$(check_logs >/dev/null 2>&1 && echo "pass" || echo "fail")",
    "backups": "$(check_backups >/dev/null 2>&1 && echo "pass" || echo "warn")",
    "volumes": "$(check_volumes >/dev/null 2>&1 && echo "pass" || echo "fail")"
  },
  "system_info": {
    "hostname": "$(hostname)",
    "uptime": "$(uptime | awk '{print $3,$4}' | sed 's/,//')",
    "docker_version": "$(docker --version)",
    "docker_compose_version": "$(docker-compose --version)"
  }
}
EOF
    
    log "Health report saved to logs/health-report-$(date +%Y%m%d_%H%M%S).json ✓"
}

# Main execution
main() {
    local overall_status="healthy"
    local failed_checks=0
    
    log "Starting N8N Scraper Health Check..."
    echo
    
    cd "$PROJECT_DIR"
    
    # Run all checks
    check_docker || { overall_status="unhealthy"; ((failed_checks++)); }
    check_containers || { overall_status="unhealthy"; ((failed_checks++)); }
    check_postgres || { overall_status="unhealthy"; ((failed_checks++)); }
    check_disk_space || { overall_status="unhealthy"; ((failed_checks++)); }
    check_memory || { overall_status="degraded"; }
    check_logs || { overall_status="degraded"; }
    check_backups || { overall_status="degraded"; }
    check_volumes || { overall_status="unhealthy"; ((failed_checks++)); }
    
    # Generate report
    generate_report "$overall_status"
    
    # Display summary
    echo
    if [ "$overall_status" = "healthy" ]; then
        log "Health Check Summary: ALL SYSTEMS HEALTHY ✅"
        log "N8N Scraper is running properly"
    elif [ "$overall_status" = "degraded" ]; then
        warn "Health Check Summary: DEGRADED ⚠️"
        warn "Some non-critical issues detected"
    else
        error "Health Check Summary: UNHEALTHY ❌"
        error "$failed_checks critical issue(s) detected"
        error "Check the logs for more details"
        exit 1
    fi
    
    echo
    info "Useful Commands:"
    info "  View logs: docker-compose logs -f"
    info "  Backup now: ./scripts/backup.sh"
    info "  Restart: ./scripts/stop.sh && ./scripts/start.sh"
}

# Run main function
main "$@"


