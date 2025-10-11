#!/usr/bin/env python3
"""
Pytest Dashboard - REAL Live Version
Uses a simpler approach that actually shows live updates
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
        
    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        return f"{elapsed // 60:02d}:{elapsed % 60:02d}"
    
    def get_spinner(self):
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        elapsed = int(time.time() - self.start_time)
        return spinners[elapsed % len(spinners)]
    
    def clear_screen(self):
        """Clear screen and move cursor to top"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_dashboard(self):
        """Print the current dashboard state"""
        # Clear screen
        self.clear_screen()
        
        # Print header
        print("╔" + "="*78 + "╗")
        print("║" + " " * 20 + "🧪 PYTEST LIVE DASHBOARD" + " " * 20 + "║")
        print("╚" + "="*78 + "╝")
        print()
        
        # Print test output (last 10 lines)
        if self.test_output:
            print("📋 Recent Test Output:")
            print("-" * 80)
            for line in self.test_output[-10:]:
                print(f"  {line}")
            print("-" * 80)
            print()
        
        # Print live stats
        status = "🔄 RUNNING" if self.running else "✅ COMPLETED"
        spinner = self.get_spinner() if self.running else "●"
        
        print("╔" + "="*78 + "╗")
        print("║" + " " * 20 + "📊 LIVE STATISTICS" + " " * 20 + "║")
        print("╚" + "="*78 + "╝")
        print()
        print(f"  {spinner} Status: {status}")
        print(f"  ⏱️  Duration: {self.get_elapsed_time()}")
        print(f"  📊 Tests: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped} | Total: {self.total}")
        print(f"  🎯 Coverage: {self.coverage}")
        print(f"  🧪 Current: {self.current_test[:60]}{'...' if len(self.current_test) > 60 else ''}")
        print()
        print("  Press Ctrl+C to stop tests")
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
            self.test_output.append(f"✅ {line}")
        elif "FAILED" in line:
            self.failed += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+FAILED', line)
            if match:
                self.current_test = match.group(1)
            self.test_output.append(f"❌ {line}")
        elif "SKIPPED" in line:
            self.skipped += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+SKIPPED', line)
            if match:
                self.current_test = match.group(1)
            self.test_output.append(f"⏭️  {line}")
        
        # Coverage
        if "TOTAL" in line and "%" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                self.coverage = f"{match.group(1)}%"
        
        # Test completion
        if "passed" in line and "failed" in line and "warnings" in line:
            self.running = False
        
        # Add important lines to output
        if any(keyword in line for keyword in ["PASSED", "FAILED", "SKIPPED", "ERROR", "warnings summary", "TOTAL"]):
            if line not in [t.replace("✅ ", "").replace("❌ ", "").replace("⏭️  ", "") for t in self.test_output]:
                self.test_output.append(line)
    
    def run_tests(self, args):
        """Run pytest and show live dashboard"""
        # Build pytest command
        cmd = ["pytest"] + args
        
        print("🚀 Starting REAL LIVE Pytest Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("🎯 You'll see REAL-TIME updates with live refresh!")
        print()
        time.sleep(2)
        
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
                
                # Update the display
                self.print_dashboard()
                
                # Small delay to make updates visible
                time.sleep(0.2)
            
            # Wait for process to complete
            process.wait()
            
            # Final update
            self.running = False
            self.print_dashboard()
            
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
            process.terminate()
            return
        
        # Show final results
        print("\n" + "="*80)
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
        print("Usage: python pytest-dashboard-real.py [pytest-args...]")
        print("Example: python pytest-dashboard-real.py -v tests/test_logging.py")
        sys.exit(1)
    
    dashboard = PytestDashboard()
    dashboard.run_tests(sys.argv[1:])

if __name__ == "__main__":
    main()




