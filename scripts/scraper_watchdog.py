#!/usr/bin/env python3
"""
Scraper Watchdog - Keepalive Mechanism

Monitors all scraping processes and restarts them if they:
1. Stop running (process died)
2. Stop making progress (stuck/frozen)
3. Cleans up zombie processes automatically
4. Monitors database connection health
"""

import sys
sys.path.append('/app')

from src.storage.database import get_session
from src.storage.connection_manager import (
    connection_manager,
    cleanup_zombie_processes,
    get_database_connection_count
)
from sqlalchemy import text
import time
from datetime import datetime, timedelta
import subprocess
import signal
import psutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SCRAPERS = {
    'layer1_5': {
        'script': '/app/scripts/layer1_5_production_scraper.py',
        'args': ['--all'],
        'check_interval': 300,  # Check progress every 5 minutes
        'max_stall_time': 600,  # Restart if no progress for 10 minutes
        'table': 'workflow_metadata',
        'progress_field': 'layer1_5_extracted_at'
    },
    'layer2': {
        'script': '/app/scripts/run_layer2_production.py',
        'args': [],
        'check_interval': 300,
        'max_stall_time': 600,
        'table': 'workflows',
        'progress_field': 'updated_at',
        'progress_filter': 'layer2_success = true'
    },
    'layer3': {
        'script': '/app/scripts/layer3_production_scraper.py',
        'args': [],  # No arguments needed - will process all by default
        'check_interval': 300,
        'max_stall_time': 600,
        'table': 'workflow_content',
        'progress_field': 'layer3_extracted_at'
    }
}

class ScraperWatchdog:
    def __init__(self):
        self.last_progress = {}
        self.process_pids = {}
        self.restart_count = {}
        self.last_zombie_cleanup = time.time()
        self.last_connection_check = time.time()
        
        # Initialize tracking
        for scraper_name in SCRAPERS:
            self.last_progress[scraper_name] = self.get_current_progress(scraper_name)
            self.restart_count[scraper_name] = 0
    
    def get_current_progress(self, scraper_name):
        """Get current progress count for a scraper"""
        config = SCRAPERS[scraper_name]
        try:
            with get_session() as session:
                if 'progress_filter' in config:
                    query = f"""
                        SELECT COUNT(*) 
                        FROM {config['table']} 
                        WHERE {config['progress_filter']}
                    """
                else:
                    query = f"""
                        SELECT COUNT(*) 
                        FROM {config['table']} 
                        WHERE {config['progress_field']} IS NOT NULL
                    """
                
                result = session.execute(text(query)).fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting progress for {scraper_name}: {e}")
            return 0
    
    def get_last_update_time(self, scraper_name):
        """Get timestamp of last update for a scraper"""
        config = SCRAPERS[scraper_name]
        try:
            with get_session() as session:
                if 'progress_filter' in config:
                    query = f"""
                        SELECT MAX({config['progress_field']}) 
                        FROM {config['table']} 
                        WHERE {config['progress_filter']}
                    """
                else:
                    query = f"""
                        SELECT MAX({config['progress_field']}) 
                        FROM {config['table']}
                    """
                
                result = session.execute(text(query)).fetchone()
                return result[0] if result and result[0] else None
        except Exception as e:
            logger.error(f"Error getting last update for {scraper_name}: {e}")
            return None
    
    def is_process_running(self, scraper_name):
        """Check if scraper process is running"""
        config = SCRAPERS[scraper_name]
        script_name = config['script'].split('/')[-1]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(script_name in str(cmd) for cmd in cmdline):
                        self.process_pids[scraper_name] = proc.info['pid']
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            logger.error(f"Error checking process for {scraper_name}: {e}")
            return False
    
    def start_scraper(self, scraper_name):
        """Start a scraper process"""
        config = SCRAPERS[scraper_name]
        
        try:
            cmd = ['python', config['script']] + config['args']
            logger.info(f"Starting {scraper_name}: {' '.join(cmd)}")
            
            # Start process in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            self.process_pids[scraper_name] = process.pid
            self.restart_count[scraper_name] += 1
            
            logger.info(f"✅ Started {scraper_name} (PID: {process.pid}, Restart #{self.restart_count[scraper_name]})")
            
            # Update last progress to current state
            self.last_progress[scraper_name] = self.get_current_progress(scraper_name)
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start {scraper_name}: {e}")
            return False
    
    def stop_scraper(self, scraper_name):
        """Stop a scraper process"""
        if scraper_name in self.process_pids:
            try:
                pid = self.process_pids[scraper_name]
                process = psutil.Process(pid)
                process.terminate()
                logger.info(f"Stopped {scraper_name} (PID: {pid})")
                return True
            except Exception as e:
                logger.error(f"Error stopping {scraper_name}: {e}")
                return False
        return False
    
    def check_scraper_health(self, scraper_name):
        """Check if scraper is healthy (running and making progress)"""
        config = SCRAPERS[scraper_name]
        
        # Check if process is running
        is_running = self.is_process_running(scraper_name)
        
        if not is_running:
            logger.warning(f"⚠️  {scraper_name} process is NOT running")
            return False, "process_not_running"
        
        # Check if making progress
        current_progress = self.get_current_progress(scraper_name)
        last_update = self.get_last_update_time(scraper_name)
        
        if last_update:
            time_since_update = datetime.utcnow() - last_update
            if time_since_update.total_seconds() > config['max_stall_time']:
                logger.warning(f"⚠️  {scraper_name} has been stalled for {time_since_update.total_seconds():.0f}s")
                return False, "stalled"
        
        # Check if progress count increased
        if current_progress > self.last_progress[scraper_name]:
            logger.info(f"✅ {scraper_name} is healthy (progress: {self.last_progress[scraper_name]} → {current_progress})")
            self.last_progress[scraper_name] = current_progress
            return True, "healthy"
        
        return True, "no_new_progress"
    
    def restart_scraper(self, scraper_name, reason):
        """Restart a scraper"""
        logger.warning(f"🔄 Restarting {scraper_name} (Reason: {reason})")
        
        # Stop if running
        self.stop_scraper(scraper_name)
        
        # Wait a bit
        time.sleep(5)
        
        # Start
        return self.start_scraper(scraper_name)
    
    def cleanup_zombies_if_needed(self):
        """Clean up zombie processes every 2 minutes"""
        current_time = time.time()
        if current_time - self.last_zombie_cleanup > 120:  # 2 minutes
            zombie_count = cleanup_zombie_processes()
            if zombie_count > 0:
                logger.info(f"🧹 Cleaned up {zombie_count} zombie processes")
            self.last_zombie_cleanup = current_time
    
    def check_database_connections(self):
        """Check database connection health every 5 minutes"""
        current_time = time.time()
        if current_time - self.last_connection_check > 300:  # 5 minutes
            # Health check
            if connection_manager.health_check():
                logger.info("✅ Database connection healthy")
            else:
                logger.error("❌ Database connection unhealthy!")
            
            # Connection count
            conn_count = get_database_connection_count()
            if conn_count > 0:
                logger.info(f"📊 Active DB connections: {conn_count}")
            
            # Pool status
            pool_status = connection_manager.get_pool_status()
            if pool_status['status'] == 'active':
                checked_out = pool_status['checked_out']
                max_conn = pool_status['max_connections']
                if checked_out > max_conn * 0.8:  # 80% threshold
                    logger.warning(f"⚠️  High connection usage: {checked_out}/{max_conn}")
            
            self.last_connection_check = current_time
    
    def run(self):
        """Main watchdog loop"""
        logger.info("=" * 80)
        logger.info("🐕 SCRAPER WATCHDOG STARTED")
        logger.info("=" * 80)
        logger.info("Monitoring scrapers: " + ", ".join(SCRAPERS.keys()))
        logger.info("Check interval: 5 minutes")
        logger.info("Max stall time: 10 minutes")
        logger.info("Zombie cleanup: Every 2 minutes")
        logger.info("Connection check: Every 5 minutes")
        logger.info("=" * 80)
        
        # Initial cleanup
        logger.info("🧹 Running initial cleanup...")
        cleanup_zombie_processes()
        
        # Initial start of all scrapers
        for scraper_name in SCRAPERS:
            if not self.is_process_running(scraper_name):
                logger.info(f"Starting {scraper_name} (initial start)")
                self.start_scraper(scraper_name)
        
        try:
            while True:
                logger.info("\n" + "─" * 80)
                logger.info(f"🔍 Health Check - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
                logger.info("─" * 80)
                
                # Clean up zombies
                self.cleanup_zombies_if_needed()
                
                # Check database connections
                self.check_database_connections()
                
                # Check scraper health
                for scraper_name in SCRAPERS:
                    is_healthy, status = self.check_scraper_health(scraper_name)
                    
                    if not is_healthy:
                        self.restart_scraper(scraper_name, status)
                
                logger.info("─" * 80)
                logger.info("✅ Health check complete. Next check in 5 minutes...")
                logger.info("─" * 80)
                
                # Wait for next check
                time.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Watchdog stopped by user")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup on exit"""
        logger.info("Cleaning up watchdog...")
        # Note: We don't stop scrapers on exit - they should continue running

def main():
    watchdog = ScraperWatchdog()
    watchdog.run()

if __name__ == "__main__":
    main()

