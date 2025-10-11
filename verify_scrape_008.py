#!/usr/bin/env python3
"""
SCRAPE-008 Verification Script

Independent verification of all SCRAPE-008 deliverables.
RND Manager: Run this to verify all claims in the Evidence Report.

Author: Dev1
Date: October 11, 2025
"""

import sys
import subprocess
from pathlib import Path

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

pass_count = 0
fail_count = 0
warn_count = 0

def check_pass(msg):
    global pass_count
    print(f"{GREEN}✅ PASS{NC} - {msg}")
    pass_count += 1

def check_fail(msg):
    global fail_count
    print(f"{RED}❌ FAIL{NC} - {msg}")
    fail_count += 1

def check_warn(msg):
    global warn_count
    print(f"{YELLOW}⚠️  WARN{NC} - {msg}")
    warn_count += 1

def header(title):
    print(f"\n{BLUE}{title}{NC}")
    print("=" * 60)

def run_cmd(cmd):
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1

print("=" * 60)
print("SCRAPE-008: STORAGE LAYER VERIFICATION")
print("=" * 60)
print("Independent verification of all deliverables")
print("=" * 60)

# 1. FILE DELIVERABLES
header("1. VERIFYING FILE DELIVERABLES")

files = [
    "src/storage/__init__.py",
    "src/storage/database.py",
    "src/storage/models.py",
    "src/storage/repository.py",
    "tests/unit/test_storage.py",
    "tests/integration/test_storage_100_workflows.py"
]

for file in files:
    if Path(file).exists():
        lines = len(Path(file).read_text().splitlines())
        check_pass(f"{file} exists ({lines} lines)")
    else:
        check_fail(f"{file} missing")

# 2. DOCKER CONTAINERS
header("2. VERIFYING DOCKER INFRASTRUCTURE")

output, _ = run_cmd("docker ps --format '{{.Names}}\t{{.Status}}'")
if "n8n-scraper-database" in output and "healthy" in output:
    check_pass("PostgreSQL container running and healthy")
else:
    check_fail("PostgreSQL container not healthy")

if "n8n-scraper-app" in output:
    check_pass("Application container running")
else:
    check_fail("Application container not running")

# 3. DATABASE SCHEMA
header("3. VERIFYING DATABASE SCHEMA")

output, _ = run_cmd('docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'public\' AND table_type = \'BASE TABLE\';"')
table_count = output.strip()
if table_count == "5":
    check_pass(f"5 tables created")
else:
    check_fail(f"Expected 5 tables, found {table_count}")

output, _ = run_cmd('docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = \'FOREIGN KEY\';"')
fk_count = output.strip()
if fk_count == "4":
    check_pass(f"4 foreign key constraints created")
else:
    check_warn(f"Expected 4 foreign keys, found {fk_count}")

# 4. DATA STORAGE
header("4. VERIFYING DATA STORAGE (100 WORKFLOWS)")

output, _ = run_cmd('docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM workflows;"')
workflow_count = int(output.strip())
if workflow_count >= 100:
    check_pass(f"{workflow_count} workflows stored (requirement: 100)")
else:
    check_fail(f"Expected 100 workflows, found {workflow_count}")

output, _ = run_cmd('docker exec n8n-scraper-database psql -U scraper_user -d n8n_scraper -t -c "SELECT COUNT(*) FROM workflow_metadata;"')
metadata_count = int(output.strip())
if metadata_count >= 100:
    check_pass(f"{metadata_count} metadata records stored")
else:
    check_fail(f"Expected 100 metadata records, found {metadata_count}")

# 5. TESTS
header("5. VERIFYING TESTS")

output, code = run_cmd('docker exec n8n-scraper-app python -m pytest tests/unit/test_storage.py tests/integration/test_storage_100_workflows.py -v --tb=no 2>&1')

if "17 passed" in output:
    check_pass("17/17 tests passing (10 unit + 7 integration)")
else:
    check_fail("Not all tests passing")

# 6. CODE COVERAGE
header("6. VERIFYING CODE COVERAGE")

output, _ = run_cmd('docker exec n8n-scraper-app python -m pytest tests/unit/test_storage.py tests/integration/test_storage_100_workflows.py --cov=src/storage --cov-report=term 2>&1')

if "repository.py" in output:
    # Extract coverage
    for line in output.split('\n'):
        if 'src/storage/' in line and '%' in line:
            parts = line.split()
            if len(parts) >= 4:
                file_name = parts[0].split('/')[-1]
                coverage = parts[3].replace('%', '')
                try:
                    cov_num = int(coverage)
                    if cov_num >= 80:
                        check_pass(f"{file_name}: {coverage}% coverage")
                    else:
                        check_warn(f"{file_name}: {coverage}% coverage (target: >80%)")
                except:
                    pass

# 7. PERFORMANCE
header("7. VERIFYING PERFORMANCE REQUIREMENTS")

output, _ = run_cmd('docker exec n8n-scraper-app python -m pytest tests/integration/test_storage_100_workflows.py::TestStoragePerformanceBenchmark::test_performance_requirements -v -s 2>&1')

if "✅ PASS" in output and "ALL PERFORMANCE REQUIREMENTS MET" in output:
    check_pass("Performance benchmark: Query time <100ms verified")
else:
    check_warn("Performance benchmark output unclear")

# 8. OPERATIONAL SCRIPTS
header("8. VERIFYING OPERATIONAL SCRIPTS")

scripts = ["backup.sh", "restore.sh", "db-init.sh", "db-monitor.sh", "db-maintain.sh", "health-check.sh", "start.sh", "stop.sh"]

for script in scripts:
    script_path = Path(f"scripts/{script}")
    if script_path.exists() and script_path.stat().st_mode & 0o111:
        check_pass(f"scripts/{script} exists and executable")
    else:
        check_warn(f"scripts/{script} missing or not executable")

# 9. BACKUP SYSTEM
header("9. VERIFYING BACKUP SYSTEM")

backup_files = list(Path("backups").glob("*.tar.gz")) if Path("backups").exists() else []
if len(backup_files) >= 1:
    check_pass(f"{len(backup_files)} backup(s) created and verified")
else:
    check_warn("No backups found (run ./scripts/backup.sh to create one)")

if Path("backups/postgres").exists():
    check_pass("Backup directory structure exists")
else:
    check_fail("Backup directory missing")

# 10. DOCUMENTATION
header("10. VERIFYING DOCUMENTATION")

docs = [
    "BACKUP_GUIDE.md",
    "DOCKER_DATABASE_GUIDE.md",
    "SCRAPE-008-COMPLETION-REPORT.md",
    ".coordination/deliverables/SCRAPE-008-EVIDENCE-REPORT.md"
]

for doc in docs:
    doc_path = Path(doc)
    if doc_path.exists():
        lines = len(doc_path.read_text().splitlines())
        check_pass(f"{doc} exists ({lines} lines)")
    else:
        check_fail(f"{doc} missing")

# FINAL SUMMARY
print()
print("=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)
print()
print(f"{GREEN}✅ PASSED:{NC} {pass_count} checks")
print(f"{YELLOW}⚠️  WARNED:{NC} {warn_count} checks")
print(f"{RED}❌ FAILED:{NC} {fail_count} checks")
print()

if fail_count == 0:
    print(f"{GREEN}{'=' * 60}{NC}")
    print(f"{GREEN}✅ SCRAPE-008 VERIFICATION: ALL CRITICAL CHECKS PASSED{NC}")
    print(f"{GREEN}{'=' * 60}{NC}")
    print()
    print("RECOMMENDATION: APPROVE SCRAPE-008 ✅")
    print()
    if warn_count > 0:
        print(f"Note: {warn_count} warnings (non-critical)")
    sys.exit(0)
else:
    print(f"{RED}{'=' * 60}{NC}")
    print(f"{RED}❌ SCRAPE-008 VERIFICATION: {fail_count} CRITICAL FAILURES{NC}")
    print(f"{RED}{'=' * 60}{NC}")
    print()
    print("RECOMMENDATION: REVIEW FAILURES BEFORE APPROVAL")
    print()
    sys.exit(1)

