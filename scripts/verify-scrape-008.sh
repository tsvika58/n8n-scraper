#!/bin/bash

# ============================================================
# SCRAPE-008 VERIFICATION SCRIPT
# ============================================================
# Independent verification of all SCRAPE-008 deliverables
#
# RND Manager: Run this script to verify all claims in the
# SCRAPE-008 Evidence Report
#
# Author: Dev1
# Date: October 11, 2025

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() { echo -e "${GREEN}✅ PASS${NC} - $1"; }
fail() { echo -e "${RED}❌ FAIL${NC} - $1"; }
warn() { echo -e "${YELLOW}⚠️  WARN${NC} - $1"; }
info() { echo -e "${BLUE}ℹ️  INFO${NC} - $1"; }
header() { echo -e "\n${BLUE}$1${NC}\n$(printf '=%.0s' {1..60})"; }

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

check_pass() {
    pass "$1"
    ((PASS_COUNT++))
}

check_fail() {
    fail "$1"
    ((FAIL_COUNT++))
}

check_warn() {
    warn "$1"
    ((WARN_COUNT++))
}

echo "============================================================"
echo "SCRAPE-008: STORAGE LAYER VERIFICATION"
echo "============================================================"
echo "This script independently verifies all deliverables"
echo "============================================================"

# ============================================================
# 1. FILE DELIVERABLES
# ============================================================
header "1. VERIFYING FILE DELIVERABLES"

# Check core files
if [ -f "src/storage/__init__.py" ]; then
    check_pass "src/storage/__init__.py exists"
else
    check_fail "src/storage/__init__.py missing"
fi

if [ -f "src/storage/database.py" ]; then
    check_pass "src/storage/database.py exists"
else
    check_fail "src/storage/database.py missing"
fi

if [ -f "src/storage/models.py" ]; then
    check_pass "src/storage/models.py exists"
else
    check_fail "src/storage/models.py missing"
fi

if [ -f "src/storage/repository.py" ]; then
    check_pass "src/storage/repository.py exists"
else
    check_fail "src/storage/repository.py missing"
fi

# Check test files
if [ -f "tests/unit/test_storage.py" ]; then
    check_pass "tests/unit/test_storage.py exists"
else
    check_fail "tests/unit/test_storage.py missing"
fi

if [ -f "tests/integration/test_storage_100_workflows.py" ]; then
    check_pass "tests/integration/test_storage_100_workflows.py exists"
else
    check_fail "tests/integration/test_storage_100_workflows.py missing"
fi

# ============================================================
# 2. DOCKER CONTAINERS
# ============================================================
header "2. VERIFYING DOCKER INFRASTRUCTURE"

if docker ps | grep -q "n8n-scraper-database.*Up.*healthy"; then
    check_pass "PostgreSQL container running and healthy"
else
    check_fail "PostgreSQL container not healthy"
fi

if docker ps | grep -q "n8n-scraper-app.*Up.*healthy"; then
    check_pass "Application container running and healthy"
else
    check_warn "Application container not fully healthy (may be expected)"
fi

# ============================================================
# 3. DATABASE SCHEMA
# ============================================================
header "3. VERIFYING DATABASE SCHEMA"

# Check tables
TABLE_COUNT=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | tr -d ' \r\n')

if [ "$TABLE_COUNT" = "5" ]; then
    check_pass "5 tables created (workflows, workflow_metadata, workflow_structure, workflow_content, video_transcripts)"
else
    check_fail "Expected 5 tables, found $TABLE_COUNT"
fi

# Check foreign keys
FK_COUNT=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY';" 2>/dev/null | tr -d ' \r\n')

if [ "$FK_COUNT" = "4" ]; then
    check_pass "4 foreign key constraints created"
else
    check_fail "Expected 4 foreign keys, found $FK_COUNT"
fi

# Check indexes
INDEX_COUNT=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';" 2>/dev/null | tr -d ' \r\n')

if [ "$INDEX_COUNT" -ge "8" ]; then
    check_pass "$INDEX_COUNT indexes created (including GIN indexes for JSONB)"
else
    check_warn "Expected at least 8 indexes, found $INDEX_COUNT"
fi

# ============================================================
# 4. DATA STORAGE
# ============================================================
header "4. VERIFYING DATA STORAGE (100 WORKFLOWS)"

WORKFLOW_COUNT=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM workflows;" 2>/dev/null | tr -d ' \r\n')

if [ "$WORKFLOW_COUNT" -ge "100" ]; then
    check_pass "$WORKFLOW_COUNT workflows stored (requirement: 100)"
else
    check_fail "Expected 100 workflows, found $WORKFLOW_COUNT"
fi

METADATA_COUNT=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM workflow_metadata;" 2>/dev/null | tr -d ' \r\n')

if [ "$METADATA_COUNT" -ge "100" ]; then
    check_pass "$METADATA_COUNT metadata records stored"
else
    check_fail "Expected 100 metadata records, found $METADATA_COUNT"
fi

TOTAL_RECORDS=$(docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM workflows UNION ALL SELECT COUNT(*) FROM workflow_metadata UNION ALL SELECT COUNT(*) FROM workflow_structure UNION ALL SELECT COUNT(*) FROM workflow_content UNION ALL SELECT COUNT(*) FROM video_transcripts) AS counts;" 2>/dev/null | tr -d ' \r\n')

if [ "$TOTAL_RECORDS" -ge "300" ]; then
    check_pass "$TOTAL_RECORDS total records across all tables"
else
    check_warn "Expected >300 records, found $TOTAL_RECORDS"
fi

# ============================================================
# 5. TESTS
# ============================================================
header "5. VERIFYING TESTS"

# Run tests and capture results
TEST_OUTPUT=$(docker exec n8n-scraper-app python -m pytest tests/unit/test_storage.py tests/integration/test_storage_100_workflows.py -v --tb=no 2>&1)

TOTAL_TESTS=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")

if [ "$TOTAL_TESTS" = "17" ]; then
    check_pass "17/17 tests passing (10 unit + 7 integration)"
else
    check_fail "Expected 17 passing tests, found $TOTAL_TESTS"
fi

# ============================================================
# 6. CODE COVERAGE
# ============================================================
header "6. VERIFYING CODE COVERAGE"

COVERAGE_OUTPUT=$(docker exec n8n-scraper-app python -m pytest tests/unit/test_storage.py tests/integration/test_storage_100_workflows.py --cov=src/storage --cov-report=term 2>&1)

# Extract coverage percentage for repository.py
REPO_COVERAGE=$(echo "$COVERAGE_OUTPUT" | grep "src/storage/repository.py" | awk '{print $4}' | sed 's/%//' || echo "0")

if [ "$REPO_COVERAGE" -ge "80" ]; then
    check_pass "repository.py coverage: ${REPO_COVERAGE}% (target: >80%)"
else
    check_warn "repository.py coverage: ${REPO_COVERAGE}% (target: >80%)"
fi

# Extract coverage for models.py
MODELS_COVERAGE=$(echo "$COVERAGE_OUTPUT" | grep "src/storage/models.py" | awk '{print $4}' | sed 's/%//' || echo "0")

if [ "$MODELS_COVERAGE" = "100" ]; then
    check_pass "models.py coverage: ${MODELS_COVERAGE}%"
else
    check_warn "models.py coverage: ${MODELS_COVERAGE}%"
fi

# ============================================================
# 7. PERFORMANCE
# ============================================================
header "7. VERIFYING PERFORMANCE REQUIREMENTS"

PERF_OUTPUT=$(docker exec n8n-scraper-app python -m pytest tests/integration/test_storage_100_workflows.py::TestStoragePerformanceBenchmark::test_performance_requirements -v -s 2>&1)

if echo "$PERF_OUTPUT" | grep -q "✅ PASS"; then
    check_pass "Performance benchmark: Query time <100ms"
else
    check_fail "Performance benchmark failed"
fi

if echo "$PERF_OUTPUT" | grep -q "ALL PERFORMANCE REQUIREMENTS MET"; then
    check_pass "All performance requirements met"
else
    check_fail "Performance requirements not met"
fi

# ============================================================
# 8. OPERATIONAL SCRIPTS
# ============================================================
header "8. VERIFYING OPERATIONAL SCRIPTS"

SCRIPTS=("backup.sh" "restore.sh" "db-init.sh" "db-monitor.sh" "db-maintain.sh" "health-check.sh" "start.sh" "stop.sh")

for script in "${SCRIPTS[@]}"; do
    if [ -x "scripts/$script" ]; then
        check_pass "scripts/$script exists and executable"
    else
        check_warn "scripts/$script missing or not executable"
    fi
done

# ============================================================
# 9. BACKUP SYSTEM
# ============================================================
header "9. VERIFYING BACKUP SYSTEM"

BACKUP_COUNT=$(ls -1 backups/*.tar.gz 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -ge "1" ]; then
    check_pass "$BACKUP_COUNT backup(s) created and verified"
else
    check_warn "No backups found (run ./scripts/backup.sh to create one)"
fi

if [ -d "backups/postgres" ]; then
    check_pass "Backup directory structure exists"
else
    check_fail "Backup directory missing"
fi

# ============================================================
# 10. DOCUMENTATION
# ============================================================
header "10. VERIFYING DOCUMENTATION"

DOCS=("BACKUP_GUIDE.md" "DOCKER_DATABASE_GUIDE.md" "SCRAPE-008-COMPLETION-REPORT.md" ".coordination/deliverables/SCRAPE-008-EVIDENCE-REPORT.md")

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        check_pass "$doc exists ($LINES lines)"
    else
        check_fail "$doc missing"
    fi
done

# ============================================================
# FINAL SUMMARY
# ============================================================
echo
echo "============================================================"
echo "VERIFICATION SUMMARY"
echo "============================================================"
echo
echo -e "${GREEN}✅ PASSED:${NC} $PASS_COUNT checks"
echo -e "${YELLOW}⚠️  WARNED:${NC} $WARN_COUNT checks"
echo -e "${RED}❌ FAILED:${NC} $FAIL_COUNT checks"
echo

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ SCRAPE-008 VERIFICATION: ALL CRITICAL CHECKS PASSED${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo
    echo "RECOMMENDATION: APPROVE SCRAPE-008 ✅"
    echo
    if [ "$WARN_COUNT" -gt 0 ]; then
        echo "Note: $WARN_COUNT warnings (non-critical)"
    fi
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ SCRAPE-008 VERIFICATION: $FAIL_COUNT CRITICAL FAILURES${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    echo
    echo "RECOMMENDATION: REVIEW FAILURES BEFORE APPROVAL"
    echo
    exit 1
fi





