#!/usr/bin/env python3
"""
Fixed Pytest Dashboard - Shows pytest output + sticky bottom dashboard
This gives you the REAL jest-dashboard experience with a persistent bottom bar
"""

import subprocess
import sys
import time
import re
import threading
from datetime import datetime
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout

class PytestDashboardFixed:
    """Fixed dashboard that shows pytest output + sticky bottom stats"""
    
    def __init__(self):
        self.console = Console()
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
        self.output_lines = []
        self.max_lines = 20  # Show last 20 lines of pytest output
        
    def create_layout(self) -> Layout:
        """Create the layout with pytest output + sticky bottom bar"""
        layout = Layout()
        
        # Main pytest output area (top)
        pytest_output = self.get_pytest_output()
        
        # Bottom status bar (sticky)
        status_bar = self.create_status_bar()
        
        layout.split_column(
            Layout(pytest_output, name="pytest_output"),
            Layout(status_bar, size=3, name="status_bar")
        )
        
        return layout
    
    def get_pytest_output(self) -> str:
        """Get the last N lines of pytest output"""
        if not self.output_lines:
            return "🚀 Starting tests..."
        
        # Show last max_lines
        recent_lines = self.output_lines[-self.max_lines:]
        return "\n".join(recent_lines)
    
    def create_status_bar(self) -> Panel:
        """Create the sticky bottom status bar"""
        elapsed = self.get_elapsed_time()
        
        # Status emoji
        status_emoji = {
            'idle': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }.get(self.stats['status'], '⏳')
        
        # Heartbeat animation
        heartbeat = "●" if self.stats['status'] == 'running' else "○"
        
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
        
        # Create status text
        status_text = Text()
        status_text.append(f"{status_emoji} ", style="bold")
        status_text.append(f"Running: {elapsed} ", style="bold white")
        status_text.append(f"● ", style="bold green blink" if self.stats['status'] == 'running' else "bold green")
        status_text.append(f"LIVE ", style="bold green" if self.stats['status'] == 'running' else "dim")
        
        status_text.append("\n")
        status_text.append(f"✅ {passed} ", style="bold green")
        status_text.append(f"❌ {failed} ", style="bold red")
        status_text.append(f"⏭️  {skipped} ", style="bold yellow")
        status_text.append(f"📊 {total} tests ", style="dim")
        status_text.append(f"│ 🎯 {coverage_str} ", style="bold cyan")
        
        if current:
            status_text.append(f"│ 🧪 {current}", style="dim")
        
        return Panel(
            status_text,
            box="double",
            style="bold cyan",
            border_style="cyan"
        )
    
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if not self.start_time:
            return "00:00"
        elapsed = int((datetime.now() - self.start_time).total_seconds())
        return f"{elapsed//60:02d}:{elapsed%60:02d}"
    
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
    
    def run_tests(self, pytest_args: list = None):
        """Run pytest with live dashboard"""
        if pytest_args is None:
            pytest_args = ['-v']
        
        self.start_time = datetime.now()
        self.stats['status'] = 'running'
        
        cmd = ['pytest'] + pytest_args
        
        try:
            with Live(self.create_layout(), refresh_per_second=4, console=self.console) as live:
                # Start pytest process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env={'PYTHONUNBUFFERED': '1', **subprocess.os.environ}
                )
                
                # Read output and update dashboard
                for line in iter(process.stdout.readline, ''):
                    if not line:
                        break
                    
                    # Parse the line
                    self.parse_pytest_line(line)
                    
                    # Update dashboard
                    live.update(self.create_layout())
                
                # Wait for completion
                return_code = process.wait()
                
                # Update final status
                self.stats['status'] = 'completed' if return_code == 0 else 'failed'
                live.update(self.create_layout())
                
                # Keep dashboard open for a moment
                time.sleep(2)
                
                return return_code
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Tests interrupted by user[/yellow]")
            return 1
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fixed Pytest Dashboard')
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
    
    # Run dashboard
    dashboard = PytestDashboardFixed()
    return_code = dashboard.run_tests(pytest_args)
    
    sys.exit(return_code)


if __name__ == '__main__':
    main()

