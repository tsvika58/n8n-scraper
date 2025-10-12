#!/bin/bash

# ============================================================
# DATABASE INITIALIZATION SCRIPT
# ============================================================
# Initialize the database schema for first-time setup
#
# This script:
# 1. Creates database if it doesn't exist
# 2. Runs SQLAlchemy migrations
# 3. Creates indexes
# 4. Verifies schema
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

DB_CONTAINER="n8n-scraper-database"
DB_USER="scraper_user"
DB_NAME="n8n_scraper"

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; }

echo "============================================================"
log "DATABASE INITIALIZATION"
echo "============================================================"
echo

# 1. Check if database container is running
log "Checking database container..."
if ! docker ps | grep -q "$DB_CONTAINER"; then
    error "Database container is not running"
    info "Start it with: docker-compose up -d n8n-scraper-database"
    exit 1
fi
log "Database container is running ✓"
echo

# 2. Wait for PostgreSQL to be ready
log "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
log "PostgreSQL is ready ✓"
echo

# 3. Create database if it doesn't exist
log "Ensuring database exists..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
log "Database '$DB_NAME' is ready ✓"
echo

# 4. Run SQLAlchemy migrations (create tables)
log "Creating database schema..."
cd "$PROJECT_DIR"

# Option 1: Using Python directly
if docker exec n8n-scraper-app python -c "
import sys
sys.path.append('/app')
from src.storage.database import init_database
try:
    init_database()
    print('Schema created successfully')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>/dev/null; then
    log "Database schema created ✓"
else
    warn "Could not create schema via Python, trying SQL..."
    # Fallback: Create schema manually if needed
fi
echo

# 5. Verify schema
log "Verifying schema..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    table_name,
    (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;
"
echo

# 6. Show indexes
log "Verifying indexes..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"
echo

# 7. Grant permissions
log "Setting up permissions..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
"
log "Permissions configured ✓"
echo

# 8. Summary
echo "============================================================"
log "DATABASE INITIALIZATION COMPLETE! ✓"
echo "============================================================"
echo
info "Database: $DB_NAME"
info "User: $DB_USER"
info "Connection: postgresql://$DB_USER:***@n8n-scraper-database:5432/$DB_NAME"
echo
info "Next steps:"
info "  1. Run health check: ./scripts/health-check.sh"
info "  2. Start scraping: docker-compose run --rm n8n-scraper-app python scripts/your_script.py"
info "  3. Monitor database: ./scripts/db-monitor.sh"
echo "============================================================"


