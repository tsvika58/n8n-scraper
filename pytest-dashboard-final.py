#!/usr/bin/env python3
"""
Pytest Dashboard - FINAL WORKING VERSION
Simple, reliable dashboard that actually works
"""

import subprocess
import sys
import time
import re
import os
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
        self.running = True
        self.test_output = []
        self.last_update = 0
        
    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        return f"{elapsed // 60:02d}:{elapsed % 60:02d}"
    
    def get_spinner(self):
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        elapsed = int(time.time() - self.start_time)
        return spinners[elapsed % len(spinners)]
    
    def print_status_line(self):
        """Print a single status line that updates in place"""
        status = "🔄 RUNNING" if self.running else "✅ COMPLETED"
        spinner = self.get_spinner() if self.running else "●"
        
        # Clear the line and print status
        print(f"\r{spinner} {status} | ⏱️  {self.get_elapsed_time()} | 📊 Tests: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped} | Total: {self.total} | 🎯 Coverage: {self.coverage} | 🧪 Current: {self.current_test[:40]}{'...' if len(self.current_test) > 40 else ''}", end="", flush=True)
    
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
            print(f"\n✅ {line}")
        elif "FAILED" in line:
            self.failed += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+FAILED', line)
            if match:
                self.current_test = match.group(1)
            print(f"\n❌ {line}")
        elif "SKIPPED" in line:
            self.skipped += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+SKIPPED', line)
            if match:
                self.current_test = match.group(1)
            print(f"\n⏭️  {line}")
        
        # Coverage
        if "TOTAL" in line and "%" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                self.coverage = f"{match.group(1)}%"
        
        # Test completion
        if "passed" in line and "failed" in line and "warnings" in line:
            self.running = False
    
    def run_tests(self, args):
        """Run pytest and show live dashboard"""
        # Build pytest command
        cmd = ["pytest"] + args
        
        print("🚀 Starting FINAL Pytest Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("🎯 You'll see live updates with a sticky status line!")
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
            # Print initial status
            self.print_status_line()
            
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Parse the line
                self.parse_pytest_output(line)
                
                # Update status line every 0.5 seconds
                current_time = time.time()
                if current_time - self.last_update >= 0.5:
                    self.print_status_line()
                    self.last_update = current_time
                
                # Small delay to make updates visible
                time.sleep(0.1)
            
            # Wait for process to complete
            process.wait()
            
            # Final update
            self.running = False
            self.print_status_line()
            
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
            process.terminate()
            return
        
        # Show final results
        print("\n\n" + "="*80)
        if self.failed == 0:
            print("🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
        else:
            print(f"❌ TESTS COMPLETED WITH {self.failed} FAILURES")
        
        print(f"⏱️  Total Duration: {self.get_elapsed_time()}")
        print(f"📊 Final Results: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped}")
        print(f"🎯 Final Coverage: {self.coverage}")
        print("="*80)
        print("\n🏁 Returning to terminal...")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pytest-dashboard-final.py [pytest-args...]")
        print("Example: python pytest-dashboard-final.py -v tests/test_logging.py")
        sys.exit(1)
    
    dashboard = PytestDashboard()
    dashboard.run_tests(sys.argv[1:])

if __name__ == "__main__":
    main()




