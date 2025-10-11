#!/usr/bin/env python3
"""
Pytest Dashboard - REAL-TIME VERSION
Actually shows live updates as tests run
"""

import subprocess
import sys
import time
import re
import threading
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
        self.lock = threading.Lock()
        
    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        return f"{elapsed // 60:02d}:{elapsed % 60:02d}"
    
    def get_spinner(self):
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        elapsed = int(time.time() - self.start_time)
        return spinners[elapsed % len(spinners)]
    
    def print_status(self):
        """Print current status"""
        with self.lock:
            status = "🔄 RUNNING" if self.running else "✅ COMPLETED"
            spinner = self.get_spinner() if self.running else "●"
            
            print(f"\r{spinner} {status} | ⏱️  {self.get_elapsed_time()} | 📊 Tests: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped} | Total: {self.total} | 🎯 Coverage: {self.coverage}", end="", flush=True)
            if self.current_test:
                print(f" | 🧪 Current: {self.current_test[:30]}{'...' if len(self.current_test) > 30 else ''}", end="", flush=True)
    
    def update_status_thread(self):
        """Thread that updates status every second"""
        while self.running:
            self.print_status()
            time.sleep(1)
    
    def parse_pytest_output(self, line):
        """Parse pytest output line and extract information"""
        line = line.strip()
        
        # Test results
        if "PASSED" in line:
            with self.lock:
                self.passed += 1
                self.total += 1
                # Extract test name
                match = re.search(r'tests/.*?::(.*?)\s+PASSED', line)
                if match:
                    self.current_test = match.group(1)
            # Clear the status line, print result, no newline so status continues on same line
            print(f"\r{' ' * 200}\r✅ {line}")
        elif "FAILED" in line:
            with self.lock:
                self.failed += 1
                self.total += 1
                match = re.search(r'tests/.*?::(.*?)\s+FAILED', line)
                if match:
                    self.current_test = match.group(1)
            print(f"\r{' ' * 200}\r❌ {line}")
        elif "SKIPPED" in line:
            with self.lock:
                self.skipped += 1
                self.total += 1
                match = re.search(r'tests/.*?::(.*?)\s+SKIPPED', line)
                if match:
                    self.current_test = match.group(1)
            print(f"\r{' ' * 200}\r⏭️  {line}")
        
        # Coverage
        if "TOTAL" in line and "%" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                with self.lock:
                    self.coverage = f"{match.group(1)}%"
        
        # Test completion detection
        if "passed" in line and "failed" in line and "warnings" in line and "in" in line and "s" in line:
            with self.lock:
                self.running = False
    
    def run_tests(self, args):
        """Run pytest and show live dashboard"""
        # Build pytest command
        cmd = ["pytest"] + args
        
        print("🚀 Starting REAL-TIME Pytest Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("🎯 You'll see LIVE updates as tests run!")
        print()
        time.sleep(1)
        
        # Start status update thread
        status_thread = threading.Thread(target=self.update_status_thread, daemon=True)
        status_thread.start()
        
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
                
                # Small delay to make updates visible
                time.sleep(0.1)
            
            # Wait for process to complete
            process.wait()
            
            # Final update
            with self.lock:
                self.running = False
            self.print_status()
            
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
        print("Usage: python pytest-dashboard-realtime.py [pytest-args...]")
        print("Example: python pytest-dashboard-realtime.py -v tests/test_logging.py")
        sys.exit(1)
    
    dashboard = PytestDashboard()
    dashboard.run_tests(sys.argv[1:])

if __name__ == "__main__":
    main()
