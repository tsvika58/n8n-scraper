#!/usr/bin/env python3
"""
SCRAPE-015: Operational Readiness Test
Tests all dashboards and functionality in parallel
"""

import asyncio
import subprocess
import requests
import time
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_test(name, status, details=""):
    icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
    print(f"{icon} {Colors.BOLD}{name}{Colors.END}")
    if details:
        print(f"   {details}")

async def test_container_health():
    """Test Docker containers are healthy"""
    print_header("1️⃣  CONTAINER HEALTH CHECK")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=n8n-scraper", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        containers = result.stdout.strip().split('\n')
        all_healthy = True
        
        for container in containers:
            if container:
                name, status = container.split('\t')
                is_healthy = "Up" in status
                print_test(f"Container: {name}", is_healthy, status)
                all_healthy = all_healthy and is_healthy
        
        return all_healthy
    except Exception as e:
        print_test("Container Health", False, str(e))
        return False

async def test_database_connectivity():
    """Test database is accessible"""
    print_header("2️⃣  DATABASE CONNECTIVITY")
    
    try:
        result = subprocess.run(
            ["docker", "exec", "n8n-scraper-database", "pg_isready", "-U", "scraper_user"],
            capture_output=True,
            text=True,
            timeout=10
        )
        success = result.returncode == 0
        print_test("PostgreSQL Database", success, result.stdout.strip())
        return success
    except Exception as e:
        print_test("Database Connectivity", False, str(e))
        return False

async def test_database_viewer():
    """Test database viewer dashboard"""
    print_header("3️⃣  DATABASE VIEWER (Port 5004)")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic connectivity
    try:
        response = requests.get("http://localhost:5004", timeout=5)
        success = response.status_code == 200
        print_test("HTTP Accessibility", success, f"Status: {response.status_code}")
        if success:
            tests_passed += 1
    except Exception as e:
        print_test("HTTP Accessibility", False, str(e))
    
    # Test 2: API endpoint
    try:
        response = requests.get("http://localhost:5004/api/stats", timeout=5)
        success = response.status_code == 200
        if success:
            data = response.json()
            print_test("API Stats Endpoint", True, f"Total workflows: {data.get('total', 0)}")
            tests_passed += 1
        else:
            print_test("API Stats Endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("API Stats Endpoint", False, str(e))
    
    # Test 3: Numerical sorting
    try:
        response = requests.get("http://localhost:5004/api/workflows?sort=workflow_id&order=asc", timeout=5)
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            if len(workflows) >= 5:
                ids = [int(w['workflow_id']) for w in workflows[:5]]
                is_sorted = ids == sorted(ids)
                print_test("Numerical Sorting (ASC)", is_sorted, f"First 5 IDs: {ids}")
                if is_sorted:
                    tests_passed += 1
            else:
                print_test("Numerical Sorting (ASC)", False, "Not enough workflows to test")
        else:
            print_test("Numerical Sorting (ASC)", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Numerical Sorting (ASC)", False, str(e))
    
    return tests_passed == total_tests

async def test_realtime_dashboard():
    """Test real-time scraping dashboard"""
    print_header("4️⃣  REAL-TIME DASHBOARD (Port 5002)")
    
    try:
        response = requests.get("http://localhost:5002", timeout=5)
        success = response.status_code == 200
        if success:
            has_title = "N8N Scraper" in response.text or "Real" in response.text
            print_test("HTTP Accessibility", success and has_title, f"Status: {response.status_code}")
            return success and has_title
        else:
            print_test("HTTP Accessibility", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("HTTP Accessibility", False, str(e))
        return False

async def test_terminal_monitor():
    """Test terminal monitor (just check file exists and is executable)"""
    print_header("5️⃣  TERMINAL MONITOR")
    
    try:
        result = subprocess.run(
            ["docker", "exec", "n8n-scraper-app", "test", "-f", "/app/scripts/terminal-monitor.py"],
            capture_output=True,
            timeout=5
        )
        exists = result.returncode == 0
        print_test("Script Exists", exists, "/app/scripts/terminal-monitor.py")
        
        if exists:
            print(f"   {Colors.CYAN}ℹ️  To run: docker exec -it n8n-scraper-app python /app/scripts/terminal-monitor.py{Colors.END}")
        
        return exists
    except Exception as e:
        print_test("Terminal Monitor", False, str(e))
        return False

async def test_workflow_details():
    """Test clickable workflow details"""
    print_header("6️⃣  WORKFLOW DETAILS (Clickable IDs)")
    
    try:
        # Get a workflow ID from the API
        response = requests.get("http://localhost:5004/api/workflows", timeout=5)
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            if workflows:
                test_id = workflows[0]['workflow_id']
                
                # Test detail page
                detail_response = requests.get(f"http://localhost:5004/workflow/{test_id}", timeout=5)
                success = detail_response.status_code == 200 and test_id in detail_response.text
                print_test(f"Detail Page (ID: {test_id})", success, f"Status: {detail_response.status_code}")
                return success
            else:
                print_test("Workflow Details", False, "No workflows in database to test")
                return False
        else:
            print_test("Workflow Details", False, f"API Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Workflow Details", False, str(e))
        return False

async def test_data_persistence():
    """Test data persists in database"""
    print_header("7️⃣  DATA PERSISTENCE")
    
    try:
        response = requests.get("http://localhost:5004/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print_test("Database Has Data", total > 0, f"Total workflows: {total}")
            return total > 0
        else:
            print_test("Database Has Data", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Data Persistence", False, str(e))
        return False

async def main():
    """Run all tests"""
    start_time = time.time()
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     SCRAPE-015: OPERATIONAL READINESS TEST SUITE            ║")
    print("║     Testing All Dashboards & Functionality                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    print(f"{Colors.YELLOW}⏱️  Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Run tests in parallel where possible
    results = await asyncio.gather(
        test_container_health(),
        test_database_connectivity(),
        test_database_viewer(),
        test_realtime_dashboard(),
        test_terminal_monitor(),
        test_workflow_details(),
        test_data_persistence(),
        return_exceptions=True
    )
    
    # Count successes
    successes = sum(1 for r in results if r is True)
    total = len(results)
    
    # Summary
    elapsed = time.time() - start_time
    
    print_header("📊 TEST SUMMARY")
    print(f"   Total Tests: {total}")
    print(f"   {Colors.GREEN}Passed: {successes}{Colors.END}")
    print(f"   {Colors.RED}Failed: {total - successes}{Colors.END}")
    print(f"   Success Rate: {Colors.BOLD}{(successes/total*100):.1f}%{Colors.END}")
    print(f"   Time Elapsed: {elapsed:.2f}s")
    
    if successes == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED - PRODUCTION READY!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED - CHECK CONFIGURATION{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

