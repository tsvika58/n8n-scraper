#!/usr/bin/env python3
"""
TRUE Sticky Pytest Dashboard - Status bar stays at bottom, pytest output scrolls above
This gives you the REAL jest-dashboard experience with a persistent bottom bar
"""

import subprocess
import sys
import time
import re
import os
import signal
import threading
from datetime import datetime

class TrueStickyDashboard:
    """Dashboard with TRUE sticky bottom bar like jest-dashboard"""
    
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
        self.max_display_lines = 15  # Lines to show above status bar
        
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if not self.start_time:
            return "00:00"
        elapsed = int((datetime.now() - self.start_time).total_seconds())
        return f"{elapsed//60:02d}:{elapsed%60:02d}"
    
    def clear_and_redraw(self):
        """Clear screen and redraw with sticky status bar"""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Show pytest output (last N lines)
        recent_lines = self.output_lines[-self.max_display_lines:]
        for line in recent_lines:
            print(line)
        
        # Show sticky status bar
        self.print_status_bar()
    
    def print_status_bar(self):
        """Print the sticky status bar at bottom"""
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
        if len(current) > 40:
            current = current[:37] + "..."
        
        # Print status bar
        print("\n" + "═" * 80)
        print(f"{status_emoji} Running: {elapsed}   🔁 LIVE   📊 Tests: ✅ {passed} ❌ {failed} ⏭️  {skipped} | Total: {total}")
        print(f"🎯 Coverage: {coverage_str}   🧪 Current: {current}")
        print("═" * 80)
    
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
        """Run pytest with TRUE sticky dashboard"""
        if pytest_args is None:
            pytest_args = ['-v', '--cov=src', '--cov-report=term-missing']
        
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.start_time = datetime.now()
        self.stats['status'] = 'running'
        
        cmd = ['pytest'] + pytest_args
        
        print("🚀 Starting ALL TESTS with TRUE Sticky Dashboard...")
        print(f"📋 Command: {' '.join(cmd)}")
        print("Press Ctrl+C to stop")
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
                
                # Update sticky dashboard every 2 lines
                line_count += 1
                if line_count % 2 == 0:
                    self.clear_and_redraw()
            
            # Wait for completion
            return_code = process.wait()
            
            # Update final status
            self.stats['status'] = 'completed' if return_code == 0 else 'failed'
            
            # Final sticky dashboard
            self.clear_and_redraw()
            
            # Show final results
            print(f"\n🎉 ALL TESTS COMPLETED!")
            print(f"⏱️  Total Duration: {self.get_elapsed_time()}")
            print(f"📊 Final Results: ✅ {self.stats['passed']} ❌ {self.stats['failed']} ⏭️  {self.stats['skipped']}")
            if self.stats['coverage'] > 0:
                print(f"🎯 Final Coverage: {self.stats['coverage']:.1f}%")
            
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
    dashboard = TrueStickyDashboard()
    return_code = dashboard.run_tests(pytest_args)
    
    sys.exit(return_code)


if __name__ == '__main__':
    main()





