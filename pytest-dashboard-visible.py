#!/usr/bin/env python3
"""
Visible Pytest Dashboard - Shows live updates without clearing screen too fast
You can actually SEE the sticky bottom bar and spinner working
"""

import subprocess
import sys
import time
import re
import os
import signal
from datetime import datetime

class VisiblePytestDashboard:
    """Dashboard that shows live updates you can actually see"""
    
    def __init__(self):
        self.start_time = None
        self.stats = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'total': 0,
            'coverage': 0.0,
            'current_test': '',
            'status': 'idle'
        }
        self.running = True
        self.output_lines = []
        self.max_display_lines = 8  # Fewer lines so you can see the sticky bar
        self.spinner_state = 0
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.update_count = 0
        
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if not self.start_time:
            return "00:00"
        elapsed = int((datetime.now() - self.start_time).total_seconds())
        return f"{elapsed//60:02d}:{elapsed%60:02d}"
    
    def get_spinner(self) -> str:
        """Get current spinner character"""
        char = self.spinner_chars[self.spinner_state]
        self.spinner_state = (self.spinner_state + 1) % len(self.spinner_chars)
        return char
    
    def clear_and_redraw(self):
        """Clear screen and redraw with sticky status bar"""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Show header
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "🧪 PYTEST LIVE DASHBOARD" + " " * 20 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        
        # Show pytest output (last N lines)
        recent_lines = self.output_lines[-self.max_display_lines:]
        for line in recent_lines:
            print(line)
        
        # Show sticky status bar
        self.print_status_bar()
    
    def print_status_bar(self):
        """Print the sticky status bar at bottom with spinner"""
        elapsed = self.get_elapsed_time()
        
        # Status emoji
        status_emoji = {
            'idle': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }.get(self.stats['status'], '⏳')
        
        # Test counts
        passed = self.stats['passed']
        failed = self.stats['failed']
        skipped = self.stats['skipped']
        total = self.stats['total']
        
        # Coverage
        coverage = self.stats['coverage']
        coverage_str = f"{coverage:.1f}%" if coverage > 0 else "--"
        
        # Current test (truncated)
        current = self.stats['current_test']
        if len(current) > 35:
            current = current[:32] + "..."
        
        # Get spinner
        spinner = self.get_spinner() if self.stats['status'] == 'running' else "●"
        
        # Print status bar
        print("\n" + "═" * 80)
        print(f"{status_emoji} Running: {elapsed}   {spinner} LIVE   📊 Tests: ✅ {passed} ❌ {failed} ⏭️  {skipped} | Total: {total}")
        print(f"🎯 Coverage: {coverage_str}   🧪 Current: {current}")
        print("═" * 80)
        print("Press Ctrl+C to stop tests")
    
    def parse_pytest_line(self, line: str):
        """Parse pytest output line for statistics"""
        # Add to output lines
        self.output_lines.append(line.rstrip())
        
        # Parse test results
        if " PASSED" in line:
            self.stats['passed'] += 1
            self.stats['total'] += 1
        elif " FAILED" in line:
            self.stats['failed'] += 1
            self.stats['total'] += 1
        elif " SKIPPED" in line:
            self.stats['skipped'] += 1
            self.stats['total'] += 1
        
        # Parse current test
        test_match = re.search(r'(tests/[^\s]+::[^\s]+)', line)
        if test_match:
            self.stats['current_test'] = test_match.group(1)
        
        # Parse coverage
        coverage_match = re.search(r'TOTAL.*?(\d+)%', line)
        if coverage_match:
            self.stats['coverage'] = float(coverage_match.group(1))
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n\n⚠️  Tests interrupted by user (Ctrl+C)")
        self.running = False
        sys.exit(1)
    
    def run_tests(self, pytest_args: list = None):
        """Run pytest with visible sticky dashboard"""
        if pytest_args is None:
            pytest_args = ['-v', '--cov=src', '--cov-report=term-missing']
        
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.start_time = datetime.now()
        self.stats['status'] = 'running'
        
        cmd = ['pytest'] + pytest_args
        
        print("🚀 Starting VISIBLE Pytest Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("🎯 You'll see the sticky bottom bar with live spinner!")
        time.sleep(2)
        
        try:
            # Start pytest process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={'PYTHONUNBUFFERED': '1', **os.environ}
            )
            
            line_count = 0
            
            # Read output and update sticky dashboard
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                # Parse for stats
                self.parse_pytest_line(line)
                
                # Update sticky dashboard every 3 lines for visibility
                line_count += 1
                self.update_count += 1
                if line_count % 3 == 0:  # Update every 3 lines so you can see it
                    self.clear_and_redraw()
                    time.sleep(0.5)  # Pause so you can see the updates
            
            # Wait for completion
            return_code = process.wait()
            
            # Update final status
            self.stats['status'] = 'completed' if return_code == 0 else 'failed'
            
            # Final sticky dashboard
            self.clear_and_redraw()
            
            # Show final results with celebration
            print(f"\n🎉" + "=" * 78 + "🎉")
            if return_code == 0:
                print(f"🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
            else:
                print(f"❌ TESTS COMPLETED WITH FAILURES ❌")
            print(f"⏱️  Total Duration: {self.get_elapsed_time()}")
            print(f"📊 Final Results: ✅ {self.stats['passed']} ❌ {self.stats['failed']} ⏭️  {self.stats['skipped']}")
            if self.stats['coverage'] > 0:
                print(f"🎯 Final Coverage: {self.stats['coverage']:.1f}%")
            print("🎉" + "=" * 78 + "🎉")
            
            # Wait a moment to show results
            time.sleep(3)
            
            return return_code
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Tests interrupted by user (Ctrl+C)")
            return 1
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1
        finally:
            print("\n🏁 Returning to terminal...")
            self.running = False


def main():
    """Main entry point - passes all arguments to pytest"""
    # Get all command line arguments except the script name
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else ['-v', '--cov=src', '--cov-report=term-missing']
    
    # Run dashboard
    dashboard = VisiblePytestDashboard()
    return_code = dashboard.run_tests(pytest_args)
    
    sys.exit(return_code)


if __name__ == '__main__':
    main()





