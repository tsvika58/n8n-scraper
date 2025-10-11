#!/usr/bin/env python3
"""
Pytest Dashboard - Real-time test monitoring with beautiful terminal UI
Inspired by jest-dashboard, adapted for Python/pytest

Features:
- Live test progress tracking
- Real-time coverage updates
- Beautiful terminal UI with Rich library
- Test counters and timing
- Sticky bottom status bar
"""

import subprocess
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.layout import Layout
from rich import box
from rich.text import Text


class PytestDashboard:
    """Real-time dashboard for pytest test execution"""
    
    def __init__(self):
        self.console = Console()
        self.start_time = None
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'current_test': '',
            'status': 'idle',
            'coverage': 0.0,
            'duration': 0.0
        }
        self.failed_tests = []
        self.slow_tests = []
        
    def create_dashboard_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        # Create header
        header = self.create_header()
        
        # Create stats panel
        stats = self.create_stats_panel()
        
        # Create progress panel
        progress = self.create_progress_panel()
        
        # Combine into layout
        layout.split_column(
            Layout(header, size=3),
            Layout(stats, size=8),
            Layout(progress, size=5)
        )
        
        return layout
    
    def create_header(self) -> Panel:
        """Create the header panel"""
        elapsed = self.get_elapsed_time()
        
        # Status emoji and color
        status_map = {
            'idle': ('⏳', 'yellow'),
            'running': ('🔄', 'cyan'),
            'completed': ('✅', 'green'),
            'failed': ('❌', 'red')
        }
        emoji, color = status_map.get(self.test_results['status'], ('⏳', 'yellow'))
        
        header_text = Text()
        header_text.append(f"{emoji} Pytest Dashboard ", style=f"bold {color}")
        header_text.append(f"| Duration: {elapsed} ", style="bold white")
        
        if self.test_results['status'] == 'running':
            header_text.append("● ", style="bold green blink")
            header_text.append("LIVE", style="bold green")
        
        return Panel(
            header_text,
            box=box.DOUBLE,
            style=f"bold {color}",
            border_style=color
        )
    
    def create_stats_panel(self) -> Panel:
        """Create the statistics panel"""
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="bold white")
        
        # Test counts
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        skipped = self.test_results['skipped']
        total = self.test_results['total']
        
        stats_table.add_row("✅ Passed", f"{passed}")
        stats_table.add_row("❌ Failed", f"{failed}")
        stats_table.add_row("⏭️  Skipped", f"{skipped}")
        stats_table.add_row("📊 Total", f"{total}")
        
        # Coverage
        coverage = self.test_results['coverage']
        coverage_style = "green" if coverage >= 80 else "yellow" if coverage >= 60 else "red"
        stats_table.add_row(
            "🎯 Coverage",
            Text(f"{coverage:.1f}%", style=f"bold {coverage_style}")
        )
        
        # Current test
        if self.test_results['current_test']:
            current = self.test_results['current_test']
            if len(current) > 50:
                current = current[:47] + "..."
            stats_table.add_row("🧪 Current", current)
        
        return Panel(
            stats_table,
            title="[bold cyan]Test Statistics[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        )
    
    def create_progress_panel(self) -> Panel:
        """Create the progress panel"""
        total = self.test_results['total']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        
        if total > 0:
            progress_pct = ((passed + failed) / total) * 100
            bar_length = 40
            filled = int(bar_length * progress_pct / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            progress_text = Text()
            progress_text.append(f"{bar} ", style="green" if failed == 0 else "yellow")
            progress_text.append(f"{progress_pct:.1f}%", style="bold white")
        else:
            progress_text = Text("No tests running yet...", style="dim")
        
        # Show failed tests if any
        if self.failed_tests:
            progress_text.append("\n\n")
            progress_text.append("Failed Tests:\n", style="bold red")
            for test in self.failed_tests[-5:]:  # Show last 5
                progress_text.append(f"  ❌ {test}\n", style="red")
        
        return Panel(
            progress_text,
            title="[bold green]Progress[/bold green]",
            box=box.ROUNDED,
            border_style="green"
        )
    
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if not self.start_time:
            return "00:00"
        
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def parse_pytest_output(self, line: str):
        """Parse pytest output line and update statistics"""
        # Parse test results
        if " PASSED" in line:
            self.test_results['passed'] += 1
            self.test_results['total'] = self.test_results['passed'] + self.test_results['failed'] + self.test_results['skipped']
        elif " FAILED" in line:
            self.test_results['failed'] += 1
            self.test_results['total'] = self.test_results['passed'] + self.test_results['failed'] + self.test_results['skipped']
            # Extract test name
            test_match = re.search(r'tests/[^\s]+::[^\s]+', line)
            if test_match:
                self.failed_tests.append(test_match.group())
        elif " SKIPPED" in line:
            self.test_results['skipped'] += 1
            self.test_results['total'] = self.test_results['passed'] + self.test_results['failed'] + self.test_results['skipped']
        
        # Parse current test
        test_match = re.search(r'(tests/[^\s]+::[^\s]+)', line)
        if test_match:
            self.test_results['current_test'] = test_match.group(1)
        
        # Parse coverage (from coverage report)
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', line)
        if coverage_match:
            self.test_results['coverage'] = float(coverage_match.group(1))
    
    def run_tests(self, pytest_args: list = None):
        """Run pytest with real-time output monitoring"""
        if pytest_args is None:
            pytest_args = ['-v', '--cov=src', '--cov-report=term-missing']
        
        self.start_time = datetime.now()
        self.test_results['status'] = 'running'
        
        # Start pytest process with unbuffered output
        cmd = ['pytest'] + pytest_args
        
        # Use environment variable to force unbuffered output
        import os
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        try:
            with Live(self.create_dashboard_layout(), refresh_per_second=4, console=self.console) as live:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env,
                    universal_newlines=True
                )
                
                # Read output line by line with timeout
                import select
                from io import TextIOWrapper
                
                while True:
                    # Check if process is still running
                    if process.poll() is not None:
                        # Process ended, read any remaining output
                        remaining = process.stdout.read()
                        if remaining:
                            for line in remaining.split('\n'):
                                if line:
                                    self.parse_pytest_output(line)
                        break
                    
                    # Try to read a line with a short timeout
                    try:
                        line = process.stdout.readline()
                        if line:
                            # Parse the line
                            self.parse_pytest_output(line)
                            
                            # Update dashboard
                            live.update(self.create_dashboard_layout())
                        else:
                            # No output, wait a bit
                            time.sleep(0.1)
                    except Exception as e:
                        # If we can't read, just update the dashboard
                        live.update(self.create_dashboard_layout())
                        time.sleep(0.1)
                
                # Wait for process to complete
                return_code = process.wait()
                
                # Update final status
                self.test_results['status'] = 'completed' if return_code == 0 else 'failed'
                live.update(self.create_dashboard_layout())
                
                return return_code
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Tests interrupted by user[/yellow]")
            return 1
        except Exception as e:
            self.console.print(f"\n[red]Error running tests: {e}[/red]")
            return 1
    
    def print_summary(self):
        """Print final test summary"""
        self.console.print("\n" + "="*60)
        
        if self.test_results['status'] == 'completed':
            self.console.print("✅ [bold green]All tests completed![/bold green]")
        else:
            self.console.print("❌ [bold red]Tests failed![/bold red]")
        
        self.console.print(f"\n📊 Results:")
        self.console.print(f"  ✅ Passed:  {self.test_results['passed']}")
        self.console.print(f"  ❌ Failed:  {self.test_results['failed']}")
        self.console.print(f"  ⏭️  Skipped: {self.test_results['skipped']}")
        self.console.print(f"  📈 Total:   {self.test_results['total']}")
        self.console.print(f"  🎯 Coverage: {self.test_results['coverage']:.1f}%")
        self.console.print(f"  ⏱️  Duration: {self.get_elapsed_time()}")
        
        if self.failed_tests:
            self.console.print(f"\n❌ [bold red]Failed Tests:[/bold red]")
            for test in self.failed_tests:
                self.console.print(f"  • {test}", style="red")
        
        self.console.print("="*60 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pytest Dashboard - Real-time test monitoring')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--no-cov', action='store_true', help='Disable coverage')
    parser.add_argument('-k', '--keyword', help='Run tests matching keyword expression')
    parser.add_argument('-m', '--marker', help='Run tests matching marker expression')
    parser.add_argument('--fast', action='store_true', help='Run tests without coverage (fast mode)')
    parser.add_argument('path', nargs='?', help='Test path to run')
    
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
        pytest_args.append('-x')  # Stop on first failure
    
    if args.path:
        pytest_args.append(args.path)
    
    # Create and run dashboard
    dashboard = PytestDashboard()
    
    dashboard.console.print("\n[bold cyan]🚀 Starting Pytest Dashboard...[/bold cyan]\n")
    
    return_code = dashboard.run_tests(pytest_args)
    
    # Print summary
    dashboard.print_summary()
    
    sys.exit(return_code)


if __name__ == '__main__':
    main()

