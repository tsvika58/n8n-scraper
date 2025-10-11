#!/usr/bin/env python3
"""
Simple Sticky Pytest Dashboard - Shows pytest output + sticky bottom bar
NEVER hangs - always returns control to terminal
"""

import subprocess
import sys
import time
import re
import os
import signal
from datetime import datetime

class SimpleStickyDashboard:
    """Simple dashboard that shows pytest output + sticky bottom bar"""
    
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
        
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if not self.start_time:
            return "00:00"
        elapsed = int((datetime.now() - self.start_time).total_seconds())
        return f"{elapsed//60:02d}:{elapsed%60:02d}"
    
    def print_status_bar(self):
        """Print the sticky status bar"""
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
        if len(current) > 30:
            current = current[:27] + "..."
        
        # Print status bar
        print("\n" + "═" * 80)
        print(f"{status_emoji} Running: {elapsed}   🔁 LIVE   📊 Tests: ✅ {passed} ❌ {failed} ⏭️  {skipped} | Total: {total}")
        print(f"🎯 Coverage: {coverage_str}   🧪 Current: {current}")
        print("═" * 80)
    
    def parse_pytest_line(self, line: str):
        """Parse pytest output line for statistics"""
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
        """Run pytest with live dashboard"""
        if pytest_args is None:
            pytest_args = ['-v']
        
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.start_time = datetime.now()
        self.stats['status'] = 'running'
        
        cmd = ['pytest'] + pytest_args
        
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
            
            # Read output and show dashboard
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                # Print the pytest output
                print(line, end='', flush=True)
                
                # Parse for stats
                self.parse_pytest_line(line)
                
                # Show status bar every 5 lines
                line_count += 1
                if line_count % 5 == 0:
                    self.print_status_bar()
            
            # Wait for completion
            return_code = process.wait()
            
            # Update final status
            self.stats['status'] = 'completed' if return_code == 0 else 'failed'
            
            # Final status bar
            self.print_status_bar()
            
            # Show final results
            print(f"\n✅ Tests completed!")
            print(f"⏱️  Duration: {self.get_elapsed_time()}")
            print(f"📊 Results: ✅ {self.stats['passed']} ❌ {self.stats['failed']} ⏭️  {self.stats['skipped']}")
            
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
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Sticky Pytest Dashboard')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--no-cov', action='store_true', help='Disable coverage')
    parser.add_argument('-k', '--keyword', help='Filter tests by keyword')
    parser.add_argument('-m', '--marker', help='Filter tests by marker')
    parser.add_argument('--fast', action='store_true', help='Fast mode')
    parser.add_argument('path', nargs='?', help='Test path')
    
    args = parser.parse_args()
    
    # Build pytest args
    pytest_args = ['-v']
    
    if not args.no_cov and not args.fast:
        pytest_args.extend(['--cov=src', '--cov-report=term-missing'])
    
    if args.keyword:
        pytest_args.extend(['-k', args.keyword])
    
    if args.marker:
        pytest_args.extend(['-m', args.marker])
    
    if args.fast:
        pytest_args.extend(['-x', '--tb=short'])
    
    if args.path:
        pytest_args.append(args.path)
    
    # Add any additional arguments passed directly
    remaining_args = sys.argv[1:]
    # Remove our known arguments
    known_args = ['-v', '--verbose', '--no-cov', '-k', '-m', '--fast', '--help', '-h']
    for i, arg in enumerate(remaining_args):
        if arg in known_args:
            if arg in ['-k', '-m'] and i + 1 < len(remaining_args):
                # Skip the value too
                continue
        elif arg.startswith('-') and arg not in ['--cov=src', '--cov-report=term-missing']:
            # This is an unknown argument, add it to pytest_args
            pytest_args.append(arg)
        elif not arg.startswith('-') and not any(remaining_args[j] in ['-k', '-m'] for j in range(max(0, i-1), i+1)):
            # This looks like a path or test name
            pytest_args.append(arg)
    
    # Run dashboard
    dashboard = SimpleStickyDashboard()
    return_code = dashboard.run_tests(pytest_args)
    
    sys.exit(return_code)


if __name__ == '__main__':
    main()

