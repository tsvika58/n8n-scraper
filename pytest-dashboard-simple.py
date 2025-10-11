#!/usr/bin/env python3
"""
Pytest Dashboard - SIMPLE WORKING VERSION
Just shows progress without trying to be fancy
"""

import subprocess
import sys
import time
import re
from datetime import datetime

class PytestDashboard:
    def __init__(self):
        self.start_time = time.time()
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0
        self.current_test = ""
        self.coverage = "--"
        
    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        return f"{elapsed // 60:02d}:{elapsed % 60:02d}"
    
    def print_progress(self):
        """Print progress update"""
        print(f"\n📊 Progress: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped} | Total: {self.total} | ⏱️  {self.get_elapsed_time()} | Coverage: {self.coverage}")
        if self.current_test:
            print(f"🧪 Current: {self.current_test}")
        print()
    
    def parse_pytest_output(self, line):
        """Parse pytest output line and extract information"""
        line = line.strip()
        
        # Test results
        if "PASSED" in line:
            self.passed += 1
            self.total += 1
            # Extract test name
            match = re.search(r'tests/.*?::(.*?)\s+PASSED', line)
            if match:
                self.current_test = match.group(1)
            print(f"✅ {line}")
        elif "FAILED" in line:
            self.failed += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+FAILED', line)
            if match:
                self.current_test = match.group(1)
            print(f"❌ {line}")
        elif "SKIPPED" in line:
            self.skipped += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+SKIPPED', line)
            if match:
                self.current_test = match.group(1)
            print(f"⏭️  {line}")
        
        # Coverage
        if "TOTAL" in line and "%" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                self.coverage = f"{match.group(1)}%"
    
    def run_tests(self, args):
        """Run pytest and show progress"""
        # Build pytest command
        cmd = ["pytest"] + args
        
        print("🚀 Starting Simple Pytest Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("🎯 You'll see test results and progress updates!")
        print()
        
        # Start pytest process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**subprocess.os.environ, 'PYTHONUNBUFFERED': '1'}
        )
        
        try:
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Parse the line
                self.parse_pytest_output(line)
                
                # Show progress every 3 tests
                if self.total > 0 and self.total % 3 == 0:
                    self.print_progress()
                
                # Small delay to make updates visible
                time.sleep(0.1)
            
            # Wait for process to complete
            process.wait()
            
            # Final progress
            self.print_progress()
            
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
            process.terminate()
            return
        
        # Show final results
        print("\n" + "="*60)
        if self.failed == 0:
            print("🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
        else:
            print(f"❌ TESTS COMPLETED WITH {self.failed} FAILURES")
        print(f"⏱️  Total Duration: {self.get_elapsed_time()}")
        print(f"📊 Final Results: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped}")
        print(f"🎯 Final Coverage: {self.coverage}")
        print("="*60)
        print("\n🏁 Returning to terminal...")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pytest-dashboard-simple.py [pytest-args...]")
        print("Example: python pytest-dashboard-simple.py -v tests/test_logging.py")
        sys.exit(1)
    
    dashboard = PytestDashboard()
    dashboard.run_tests(sys.argv[1:])

if __name__ == "__main__":
    main()