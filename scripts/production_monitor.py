#!/usr/bin/env python3
"""
Production Monitor with Connection Management

Real-time monitoring with:
- Database connection health
- Process monitoring
- Connection pool management
- Zero tolerance error detection
"""

import os
import sys
import time
import psutil
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'n8n-shared'))

class ProductionMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.error_count = 0
        self.last_error = None
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def check_database_connection(self):
        """Check database connection health."""
        try:
            from src.storage.database import get_session
            from n8n_shared.models import Workflow
            
            with get_session() as session:
                count = session.query(Workflow).count()
                return True, f"Connected - {count} workflows"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def check_process_health(self):
        """Check if validation process is running."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'validate_7_workflows_production' in ' '.join(proc.info['cmdline'] or []):
                    return True, f"PID {proc.info['pid']}"
            return False, "Not running"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_db_viewer(self):
        """Check if DB viewer is accessible."""
        try:
            result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8080/workflows'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout == '200':
                return True, "Accessible"
            else:
                return False, f"HTTP {result.stdout}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_redis(self):
        """Check Redis connection."""
        try:
            result = subprocess.run(['docker', 'exec', 'n8n-scraper-redis', 'redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'PONG' in result.stdout:
                return True, "Connected"
            else:
                return False, "Not responding"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def display_status(self):
        """Display comprehensive status."""
        self.clear_screen()
        
        elapsed = datetime.now() - self.start_time
        
        print("🚀 PRODUCTION MONITOR - ZERO TOLERANCE VALIDATION")
        print("=" * 70)
        print(f"⏰ Runtime: {str(elapsed).split('.')[0]} | Errors: {self.error_count}")
        print()
        
        # Database Connection
        db_ok, db_msg = self.check_database_connection()
        print(f"💾 Database: {'✅' if db_ok else '❌'} {db_msg}")
        
        # Process Health
        proc_ok, proc_msg = self.check_process_health()
        print(f"🔄 Validation Process: {'✅' if proc_ok else '❌'} {proc_msg}")
        
        # DB Viewer
        viewer_ok, viewer_msg = self.check_db_viewer()
        print(f"🌐 DB Viewer: {'✅' if viewer_ok else '❌'} {viewer_msg}")
        
        # Redis
        redis_ok, redis_msg = self.check_redis()
        print(f"🔴 Redis: {'✅' if redis_ok else '❌'} {redis_msg}")
        
        print()
        
        # Error tracking
        if self.error_count > 0:
            print(f"⚠️  ERRORS DETECTED: {self.error_count}")
            if self.last_error:
                print(f"   Last Error: {self.last_error}")
            print()
        
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        print(f"💻 System: CPU {cpu_percent}% | RAM {memory.percent}%")
        print()
        
        print("=" * 70)
        print("🔍 Monitoring every 3 seconds | Press Ctrl+C to stop")
        print("=" * 70)
    
    def run(self):
        """Run the production monitor."""
        self.log("Starting Production Monitor with Zero Tolerance")
        
        try:
            while True:
                self.display_status()
                
                # Check for errors
                db_ok, _ = self.check_database_connection()
                proc_ok, _ = self.check_process_health()
                viewer_ok, _ = self.check_db_viewer()
                redis_ok, _ = self.check_redis()
                
                # Count errors
                current_errors = sum([not db_ok, not proc_ok, not viewer_ok, not redis_ok])
                
                if current_errors > self.error_count:
                    self.error_count = current_errors
                    self.last_error = f"New error detected at {datetime.now().strftime('%H:%M:%S')}"
                    self.log(f"❌ ERROR DETECTED: {current_errors} systems failing", "ERROR")
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Production Monitor stopped by user")
        except Exception as e:
            print(f"\n💥 CRITICAL ERROR: {e}")
            sys.exit(1)

def main():
    """Main function."""
    monitor = ProductionMonitor()
    monitor.run()

if __name__ == "__main__":
    main()