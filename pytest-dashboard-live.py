#!/usr/bin/env python3
"""
Pytest Dashboard - TRULY LIVE Version
Shows real-time updates without clearing the screen
"""

import subprocess
import sys
import time
import re
import threading
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout

class PytestDashboard:
    def __init__(self):
        self.console = Console()
        self.start_time = time.time()
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0
        self.current_test = ""
        self.coverage = "--"
        self.running = True
        self.test_output = []
        self.max_output_lines = 20
        
    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        return f"{elapsed // 60:02d}:{elapsed % 60:02d}"
    
    def get_spinner(self):
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        elapsed = int(time.time() - self.start_time)
        return spinners[elapsed % len(spinners)]
    
    def create_dashboard(self):
        """Create the dashboard layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="top", size=15),
            Layout(name="bottom", size=5)
        )
        
        # Top section - Test output (scrollable)
        if self.test_output:
            output_text = "\n".join(self.test_output[-self.max_output_lines:])
            layout["top"].update(Panel(
                output_text,
                title="🧪 Test Output",
                border_style="blue"
            ))
        else:
            layout["top"].update(Panel(
                "Waiting for test output...",
                title="🧪 Test Output", 
                border_style="blue"
            ))
        
        # Bottom section - Live stats (sticky)
        status = "🔄 RUNNING" if self.running else "✅ COMPLETED"
        spinner = self.get_spinner() if self.running else "●"
        
        stats_text = f"""
{spinner} {status} | ⏱️  {self.get_elapsed_time()} | 📊 Tests: ✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped} | Total: {self.total}
🎯 Coverage: {self.coverage} | 🧪 Current: {self.current_test[:50]}{'...' if len(self.current_test) > 50 else ''}
        """.strip()
        
        layout["bottom"].update(Panel(
            stats_text,
            title="📊 Live Dashboard",
            border_style="green" if self.running else "yellow"
        ))
        
        return layout
    
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
        elif "FAILED" in line:
            self.failed += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+FAILED', line)
            if match:
                self.current_test = match.group(1)
        elif "SKIPPED" in line:
            self.skipped += 1
            self.total += 1
            match = re.search(r'tests/.*?::(.*?)\s+SKIPPED', line)
            if match:
                self.current_test = match.group(1)
        
        # Coverage
        if "TOTAL" in line and "%" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                self.coverage = f"{match.group(1)}%"
        
        # Test completion
        if "passed" in line and "failed" in line and "warnings" in line:
            self.running = False
        
        # Add to output (only important lines)
        if any(keyword in line for keyword in ["PASSED", "FAILED", "SKIPPED", "ERROR", "warnings summary", "TOTAL"]):
            self.test_output.append(line)
    
    def run_tests(self, args):
        """Run pytest and show live dashboard"""
        # Build pytest command
        cmd = ["pytest"] + args
        
        print("🚀 Starting LIVE Pytest Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("🎯 You'll see REAL-TIME updates with sticky bottom bar!")
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
        
        # Create live display
        with Live(self.create_dashboard(), refresh_per_second=2, screen=True) as live:
            try:
                # Read output line by line
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse the line
                    self.parse_pytest_output(line)
                    
                    # Update the display
                    live.update(self.create_dashboard())
                    
                    # Small delay to make updates visible
                    time.sleep(0.1)
                
                # Wait for process to complete
                process.wait()
                
                # Final update
                self.running = False
                live.update(self.create_dashboard())
                
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
        print("Usage: python pytest-dashboard-live.py [pytest-args...]")
        print("Example: python pytest-dashboard-live.py -v tests/test_logging.py")
        sys.exit(1)
    
    dashboard = PytestDashboard()
    dashboard.run_tests(sys.argv[1:])

if __name__ == "__main__":
    main()
