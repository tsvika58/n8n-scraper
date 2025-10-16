#!/usr/bin/env python3
"""
Enhanced Scrapers Watchdog
Monitors and restarts Layer 2 V2 and Layer 3 V3 scrapers if they fail.

Author: Dev1
Task: Enhanced L2 L3 Node Context Extraction
Date: October 15, 2025
"""

import os
import sys
import time
import signal
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project paths
sys.path.append('.')
sys.path.append('../n8n-shared')


class EnhancedScrapersWatchdog:
    """Watchdog for enhanced scrapers."""
    
    def __init__(self, restart_delay: int = 60, check_interval: int = 30):
        self.restart_delay = restart_delay
        self.check_interval = check_interval
        self.running = True
        self.processes = {
            'layer2_v2': None,
            'layer3_v3': None,
            'runner': None
        }
        self.stats = {
            'start_time': datetime.now(),
            'restarts': 0,
            'last_check': datetime.now(),
            'layer2_v2_restarts': 0,
            'layer3_v3_restarts': 0,
            'runner_restarts': 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n🛑 Watchdog received signal {signum}, shutting down...")
        self.running = False
        self._cleanup_processes()
    
    def _cleanup_processes(self):
        """Clean up all managed processes."""
        print("🧹 Cleaning up processes...")
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"   Terminating {name} process...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print(f"   Force killing {name} process...")
                    process.kill()
    
    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running by name."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if process_name in cmdline:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False
    
    def _start_process(self, process_name: str, command: List[str]) -> Optional[subprocess.Popen]:
        """Start a process."""
        try:
            print(f"🚀 Starting {process_name} process...")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            print(f"   ✅ {process_name} started with PID {process.pid}")
            return process
        except Exception as e:
            print(f"   ❌ Failed to start {process_name}: {e}")
            return None
    
    def _restart_process(self, process_name: str, command: List[str]):
        """Restart a process."""
        print(f"🔄 Restarting {process_name} process...")
        
        # Stop existing process
        if self.processes[process_name] and self.processes[process_name].poll() is None:
            print(f"   Stopping existing {process_name} process...")
            self.processes[process_name].terminate()
            try:
                self.processes[process_name].wait(timeout=10)
            except subprocess.TimeoutExpired:
                print(f"   Force killing {process_name} process...")
                self.processes[process_name].kill()
        
        # Wait before restart
        print(f"   ⏳ Waiting {self.restart_delay}s before restart...")
        time.sleep(self.restart_delay)
        
        # Start new process
        self.processes[process_name] = self._start_process(process_name, command)
        
        # Update stats
        self.stats['restarts'] += 1
        if process_name == 'layer2_v2':
            self.stats['layer2_v2_restarts'] += 1
        elif process_name == 'layer3_v3':
            self.stats['layer3_v3_restarts'] += 1
        elif process_name == 'runner':
            self.stats['runner_restarts'] += 1
    
    def _check_process_health(self, process_name: str) -> bool:
        """Check if a process is healthy."""
        process = self.processes[process_name]
        if not process:
            return False
        
        # Check if process is still running
        if process.poll() is not None:
            print(f"   ❌ {process_name} process has terminated (exit code: {process.returncode})")
            return False
        
        # Check if process is responsive (basic check)
        try:
            # Try to get process info
            proc = psutil.Process(process.pid)
            if not proc.is_running():
                print(f"   ❌ {process_name} process is not running")
                return False
            
            # Check CPU usage (if it's been running for a while)
            create_time = datetime.fromtimestamp(proc.create_time())
            if datetime.now() - create_time > timedelta(minutes=5):
                cpu_percent = proc.cpu_percent()
                if cpu_percent > 90:  # High CPU usage might indicate a problem
                    print(f"   ⚠️ {process_name} process has high CPU usage: {cpu_percent:.1f}%")
                    # Don't restart for high CPU, just warn
            
            return True
            
        except psutil.NoSuchProcess:
            print(f"   ❌ {process_name} process not found")
            return False
        except Exception as e:
            print(f"   ⚠️ Error checking {process_name} process health: {e}")
            return True  # Assume healthy if we can't check
    
    def display_status(self):
        """Display watchdog status."""
        current_time = datetime.now()
        uptime = current_time - self.stats['start_time']
        
        print(f"\n🔧 ENHANCED SCRAPERS WATCHDOG STATUS")
        print(f"📅 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Uptime: {uptime}")
        print(f"🔄 Last Check: {self.stats['last_check'].strftime('%H:%M:%S')}")
        print()
        
        # Process status
        for name, process in self.processes.items():
            if process and process.poll() is None:
                status = "🟢 RUNNING"
                pid = process.pid
            else:
                status = "🔴 STOPPED"
                pid = "N/A"
            print(f"   {name}: {status} (PID: {pid})")
        
        print()
        print(f"📊 Statistics:")
        print(f"   Total Restarts: {self.stats['restarts']}")
        print(f"   Layer 2 V2 Restarts: {self.stats['layer2_v2_restarts']}")
        print(f"   Layer 3 V3 Restarts: {self.stats['layer3_v3_restarts']}")
        print(f"   Runner Restarts: {self.stats['runner_restarts']}")
    
    def run_watchdog(self, start_processes: bool = True):
        """Run the watchdog."""
        print("🐕 Enhanced Scrapers Watchdog Starting...")
        print(f"⏳ Check interval: {self.check_interval}s")
        print(f"🔄 Restart delay: {self.restart_delay}s")
        print(f"🕒 Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define process commands
        commands = {
            'layer2_v2': ['python', 'scripts/run_enhanced_scrapers.py', '--layer', 'layer2_v2'],
            'layer3_v3': ['python', 'scripts/run_enhanced_scrapers.py', '--layer', 'layer3_v3'],
            'runner': ['python', 'scripts/run_enhanced_scrapers.py', '--layer', 'both']
        }
        
        # Start processes if requested
        if start_processes:
            print("\n🚀 Starting managed processes...")
            for name, command in commands.items():
                if name == 'runner':  # Only start the runner by default
                    self.processes[name] = self._start_process(name, command)
                else:
                    # Don't start individual scrapers, let the runner handle them
                    pass
        
        try:
            while self.running:
                self.stats['last_check'] = datetime.now()
                
                # Check each process
                for name, process in self.processes.items():
                    if process and not self._check_process_health(name):
                        print(f"🔄 {name} process needs restart")
                        self._restart_process(name, commands[name])
                
                # Display status every 10 checks
                if self.stats['restarts'] % 10 == 0:
                    self.display_status()
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Watchdog stopped by user")
        except Exception as e:
            print(f"\n❌ Watchdog error: {e}")
        finally:
            self._cleanup_processes()
            print("👋 Enhanced Scrapers Watchdog stopped")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Scrapers Watchdog')
    parser.add_argument('--check-interval', '-i', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--restart-delay', '-d', type=int, default=60,
                       help='Restart delay in seconds (default: 60)')
    parser.add_argument('--no-start', action='store_true',
                       help='Don\'t start processes, just monitor existing ones')
    
    args = parser.parse_args()
    
    watchdog = EnhancedScrapersWatchdog(
        restart_delay=args.restart_delay,
        check_interval=args.check_interval
    )
    
    watchdog.run_watchdog(start_processes=not args.no_start)


if __name__ == "__main__":
    main()

